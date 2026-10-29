from fastapi import APIRouter, Request
from sqlalchemy import text
from starlette.responses import JSONResponse
from app.schemas import RuntimeInfo, ProviderInfo, ExperimentLimits, HealthInfo

router = APIRouter()


@router.get("/api/runtime", response_model=RuntimeInfo, operation_id="getRuntime")
async def get_runtime(request: Request):
    settings = request.app.state.settings
    fixture = settings.app_mode == "fixture"
    return RuntimeInfo(
        server_instance_id=request.app.state.store.instance_id,
        provider=ProviderInfo(
            backend="fixture" if fixture else settings.gemini_backend,
            generation_model="fixture" if fixture else settings.gemini_generation_model,
            embedding_model=settings.embedding_profile,
            retention_status="fixture_only" if fixture else "provider_managed",
            disclosure="Ensaio local com respostas/vetores de teste, sem envio externo."
            if fixture
            else "Perguntas e trechos necessários são enviados à API Gemini; pesquisas enviam consultas ao provedor de busca. Conversas e fontes não selecionadas não são persistidas localmente. A retenção nos provedores segue suas políticas.",
        ),
        limits=ExperimentLimits(**settings.public_limits()),
    )


@router.get("/health/live", response_model=HealthInfo, operation_id="liveness")
async def live():
    return HealthInfo(status="ok", database_ready=False)


@router.get("/health/ready", response_model=HealthInfo, operation_id="readiness")
async def ready(request: Request):
    try:
        async with request.app.state.engine.connect() as connection:
            revision = await connection.scalar(
                text("SELECT version_num FROM alembic_version")
            )
            if revision != "0002_selection_grants":
                return JSONResponse(
                    {"status": "not_ready", "database_ready": False}, status_code=503
                )
        return HealthInfo(status="ok", database_ready=True)
    except Exception:
        return JSONResponse(
            {"status": "not_ready", "database_ready": False}, status_code=503
        )
