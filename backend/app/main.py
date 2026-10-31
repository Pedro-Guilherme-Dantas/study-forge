from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from app.settings import Settings, get_settings
from app.sessions import SessionStore
from app.operations import Executor
from app.security import LocalSecurity
from app.db.session import make_database
from app.errors import AppError
from app.diagnostics import configure
from app.observability import Observability
from app.api import (
    sessions,
    runtime,
    materials,
    operations,
    chat,
    citations,
    research,
    sources,
    progress,
)
from app.agents.researcher import Researcher
from app.providers.search import SearchProvider
from app.web_fetch import SafeFetcher
from app.retrieval import Retriever
from app.agents.tutor import Tutor
from app.agents.graph import build_tutor_graph
from app.agents.orchestrator import Orchestrator
from app.ingestion.service import IngestionService
from app.ingestion.promotion import PromotionService
from app.api.openapi import install_openapi
from app.providers.gemini import GeminiProvider
from sqlalchemy.exc import SQLAlchemyError


def create_app(settings: Settings | None = None):
    settings = settings or get_settings()
    configure()
    store = SessionStore()
    observability = Observability(settings)
    engine, database = make_database(settings)
    executor = Executor(
        settings.max_ingestions,
        settings.max_ingestions + settings.max_queued_ingestions,
    )

    @asynccontextmanager
    async def lifespan(app):
        await observability.start()
        try:
            await app.state.ingestion.recover()
        except SQLAlchemyError:
            # The health endpoint reports an unmigrated database without exposing details.
            pass
        yield
        await store.shutdown()
        await executor.shutdown()
        await observability.close()
        await engine.dispose()

    app = FastAPI(
        title="StudyForge",
        version="0.1.0",
        lifespan=lifespan,
        docs_url=None,
        redoc_url=None,
    )
    app.state.settings, app.state.store = settings, store
    app.state.observability = observability
    app.state.engine, app.state.database = engine, database
    app.state.executor = executor
    app.state.ingestion = IngestionService(
        settings, database, executor, GeminiProvider(settings), store.instance_id
    )
    app.state.promotion = PromotionService(app.state.ingestion)
    provider = GeminiProvider(settings)
    app.state.orchestrator = Orchestrator(
        settings,
        build_tutor_graph(
            Retriever(settings, database, provider), Tutor(settings, provider)
        ),
        executor,
        Researcher(settings, SearchProvider(settings), SafeFetcher(settings), provider),
        observability=observability,
        provider=provider,
    )
    app.add_middleware(LocalSecurity, store=store, settings=settings)

    @app.exception_handler(AppError)
    async def app_error(request: Request, error: AppError):
        return JSONResponse(error.envelope(), status_code=error.status)

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, error: RequestValidationError):
        safe = AppError("INVALID_REQUEST", "Verifique os campos enviados.", 422)
        return JSONResponse(safe.envelope(), status_code=422)

    app.include_router(sessions.router)
    app.include_router(runtime.router)
    app.include_router(materials.router)
    app.include_router(operations.router)
    app.include_router(chat.router)
    app.include_router(citations.router)
    app.include_router(research.router)
    app.include_router(sources.router)
    app.include_router(progress.router)
    install_openapi(app)
    dist = Path("/workspace/frontend/dist")
    if dist.exists():
        app.mount("/", StaticFiles(directory=dist, html=True), name="web")
    return app


app = create_app()
