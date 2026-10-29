import asyncio
from uuid import UUID, uuid4
from sqlalchemy import select, func
from sqlalchemy.dialects.postgresql import insert
from app.db.models import (
    Material,
    MaterialVersion,
    Chunk,
    EmbeddingProfile,
    IngestionOperation,
    SelectionGrant,
    now,
)
from app.errors import AppError
from app.schemas import (
    IngestionReceipt,
    MaterialSummary,
    MaterialPage,
    MaterialDetail,
    VersionSummary,
    LibraryChunk,
    Locator,
)
from app.ingestion.validate import validate_markdown
from app.ingestion.normalize import normalize
from app.ingestion.chunk import (
    chunk_text,
    pipeline_config,
    pipeline_fingerprint,
    digest,
)
from app.providers.gemini import GeminiProvider


def receipt(operation):
    return IngestionReceipt(
        operation_id=operation.id,
        material_id=operation.material_id,
        version_id=operation.material_version_id,
        state=operation.state,
        stage=operation.stage,
        attempt=operation.attempt,
        error_code=operation.error_code,
    )


def summary(material):
    return MaterialSummary(
        material_id=material.id,
        source_kind=material.source_kind,
        display_name=material.display_name,
        status=material.status,
        active_version_id=material.active_version_id,
    )


class IngestionService:
    def __init__(self, settings, database, executor, provider, instance_id):
        self.settings, self.database, self.executor = settings, database, executor
        self.provider, self.instance_id = provider, instance_id

    async def accept_markdown(self, filename, body):
        name, original = validate_markdown(filename, body, self.settings)
        fingerprint, input_hash = pipeline_fingerprint(self.settings), digest(original)
        profile = self.settings.embedding_profile
        async with self.database() as db:
            existing = await db.scalar(
                select(IngestionOperation)
                .join(
                    MaterialVersion,
                    IngestionOperation.material_version_id == MaterialVersion.id,
                )
                .join(Material, MaterialVersion.material_id == Material.id)
                .where(
                    Material.origin_key == name,
                    Material.source_kind == "markdown_upload",
                    MaterialVersion.input_sha256 == input_hash,
                    MaterialVersion.pipeline_fingerprint == fingerprint,
                    MaterialVersion.embedding_profile_id == profile,
                )
            )
            if existing:
                return receipt(existing)
        ticket = self.executor.reserve()
        try:
            async with self.database() as db, db.begin():
                await db.execute(
                    insert(EmbeddingProfile)
                    .values(
                        id=profile,
                        provider="fixture"
                        if self.settings.app_mode == "fixture"
                        else self.settings.gemini_backend,
                        model=profile,
                        dimensions=768,
                        configuration={
                            "normalization": "L2",
                            "text_template": "section-v1",
                        },
                    )
                    .on_conflict_do_nothing(index_elements=["id"])
                )
                await db.execute(
                    insert(Material)
                    .values(
                        id=uuid4(),
                        source_kind="markdown_upload",
                        origin_key=name,
                        display_name=name,
                        status="processing",
                    )
                    .on_conflict_do_nothing(
                        index_elements=["source_kind", "origin_key"]
                    )
                )
                material = await db.scalar(
                    select(Material)
                    .where(
                        Material.source_kind == "markdown_upload",
                        Material.origin_key == name,
                    )
                    .with_for_update()
                )
                version = await db.scalar(
                    select(MaterialVersion).where(
                        MaterialVersion.material_id == material.id,
                        MaterialVersion.input_sha256 == input_hash,
                        MaterialVersion.pipeline_fingerprint == fingerprint,
                        MaterialVersion.embedding_profile_id == profile,
                    )
                )
                if version:
                    operation = await db.scalar(
                        select(IngestionOperation).where(
                            IngestionOperation.material_version_id == version.id
                        )
                    )
                    result = receipt(operation)
                    ticket.release()
                    return result
                latest = (
                    await db.scalar(
                        select(func.max(MaterialVersion.version_number)).where(
                            MaterialVersion.material_id == material.id
                        )
                    )
                    or 0
                )
                version = MaterialVersion(
                    id=uuid4(),
                    material_id=material.id,
                    version_number=latest + 1,
                    input_snapshot_text=original,
                    input_sha256=input_hash,
                    raw_capture_sha256=input_hash,
                    pipeline_fingerprint=fingerprint,
                    pipeline_config=pipeline_config(self.settings),
                    embedding_profile_id=profile,
                    state="processing",
                )
                db.add(version)
                await db.flush()
                operation = IngestionOperation(
                    id=uuid4(),
                    material_id=material.id,
                    material_version_id=version.id,
                    state="queued",
                    stage="validate",
                    attempt=1,
                )
                db.add(operation)
                await db.flush()
                result = receipt(operation)
            try:
                self.executor.submit(lambda: self.process(result.operation_id), ticket)
            except Exception:
                await self._fail(
                    result.operation_id, "EXECUTION_INTERRUPTED", interrupted=True
                )
                raise AppError(
                    "EXECUTION_INTERRUPTED",
                    "Não foi possível iniciar o processamento. Tente novamente.",
                    503,
                ) from None
            return result
        except BaseException:
            ticket.release()
            raise

    async def _fail(self, operation_id, code, interrupted=False):
        async with self.database() as db, db.begin():
            operation = await db.get(
                IngestionOperation, operation_id, with_for_update=True
            )
            if not operation or operation.state == "succeeded":
                return
            state = "interrupted" if interrupted else "failed"
            operation.state, operation.error_code, operation.finished_at = (
                state,
                code,
                now(),
            )
            version = await db.get(MaterialVersion, operation.material_version_id)
            version.state, version.failure_code = state, code
            material = await db.get(
                Material, operation.material_id, with_for_update=True
            )
            material.status = "ready" if material.active_version_id else state

    async def process(self, operation_id):
        try:
            async with asyncio.timeout(self.settings.ingestion_timeout):
                async with self.database() as db, db.begin():
                    operation = await db.get(
                        IngestionOperation, operation_id, with_for_update=True
                    )
                    if operation.state != "queued":
                        return
                    operation.state, operation.stage = "running", "normalize"
                    operation.runner_instance_id, operation.started_at = (
                        self.instance_id,
                        now(),
                    )
                    version = await db.get(
                        MaterialVersion, operation.material_version_id
                    )
                    text, version_id = version.input_snapshot_text, version.id
                    material = await db.get(Material, version.material_id)
                    source_kind = material.source_kind
                    if source_kind == "selected_web":
                        grant = await db.scalar(
                            select(SelectionGrant).where(
                                SelectionGrant.material_version_id == version.id,
                                SelectionGrant.input_sha256 == version.input_sha256,
                                SelectionGrant.source_origin_key == material.origin_key,
                            )
                        )
                        if not grant:
                            raise AppError(
                                "SELECTION_REQUIRED",
                                "A fonte não tem autorização de seleção.",
                                403,
                                "validate",
                            )
                    if (
                        version.pipeline_fingerprint
                        != pipeline_fingerprint(self.settings)
                        or version.embedding_profile_id
                        != self.settings.embedding_profile
                    ):
                        raise AppError(
                            "PIPELINE_MISMATCH",
                            "A versão exige seu perfil original.",
                            409,
                            "normalize",
                        )
                doc = await asyncio.to_thread(normalize, text)
                drafts = await asyncio.to_thread(chunk_text, doc, self.settings)
                if not drafts:
                    raise AppError(
                        "INVALID_MARKDOWN",
                        "O material não contém texto utilizável.",
                        422,
                        "chunk",
                    )
                async with self.database() as db, db.begin():
                    operation = await db.get(IngestionOperation, operation_id)
                    operation.stage = "embed"
                vectors = await self.provider.embed(
                    [" / ".join(c.locator.section_path) + "\n" + c.text for c in drafts]
                )
                if len(vectors) != len(drafts):
                    raise AppError(
                        "INVALID_EMBEDDING",
                        "Nem todos os trechos receberam vetores.",
                        502,
                        "embed",
                    )
                vectors = [GeminiProvider.validate_vector(vector) for vector in vectors]
                async with self.database() as db, db.begin():
                    operation = await db.get(
                        IngestionOperation, operation_id, with_for_update=True
                    )
                    if operation.state != "running":
                        return
                    version = await db.get(
                        MaterialVersion, version_id, with_for_update=True
                    )
                    material = await db.get(
                        Material, version.material_id, with_for_update=True
                    )
                    for ordinal, (draft, vector) in enumerate(
                        zip(drafts, vectors, strict=True)
                    ):
                        key = digest(
                            f"{version.id}:{version.pipeline_fingerprint}:{ordinal}:{draft.start}:{draft.end}:{draft.sha256}"
                        )
                        db.add(
                            Chunk(
                                id=key,
                                material_version_id=version.id,
                                ordinal=ordinal,
                                text=draft.text,
                                start_char=draft.start,
                                end_char=draft.end,
                                locator=draft.locator.model_copy(
                                    update={
                                        "kind": "html_extracted_snapshot"
                                        if source_kind == "selected_web"
                                        else "markdown_original"
                                    }
                                ).model_dump(mode="json"),
                                chunk_sha256=draft.sha256,
                                pipeline_fingerprint=version.pipeline_fingerprint,
                                embedding_profile_id=version.embedding_profile_id,
                                embedding=vector,
                            )
                        )
                    await db.flush()
                    count = await db.scalar(
                        select(func.count())
                        .select_from(Chunk)
                        .where(Chunk.material_version_id == version.id)
                    )
                    if count != len(drafts):
                        raise AppError(
                            "PUBLICATION_INCOMPLETE",
                            "A publicação ficou incompleta.",
                            500,
                            "publish",
                        )
                    version.normalized_text, version.normalized_sha256 = (
                        doc.text,
                        digest(doc.text),
                    )
                    version.expected_chunk_count = version.published_chunk_count = count
                    version.state, version.ready_at, version.failure_code = (
                        "ready",
                        now(),
                        None,
                    )
                    active = (
                        await db.get(MaterialVersion, material.active_version_id)
                        if material.active_version_id
                        else None
                    )
                    if active is None or active.version_number < version.version_number:
                        material.active_version_id = version.id
                    material.status = "ready"
                    operation.state, operation.stage = "succeeded", "publish"
                    operation.finished_at, operation.error_code = now(), None
        except asyncio.CancelledError:
            await self._fail(operation_id, "EXECUTION_INTERRUPTED", interrupted=True)
            raise
        except TimeoutError:
            await self._fail(operation_id, "EXECUTION_LIMIT", interrupted=True)
        except AppError as error:
            await self._fail(operation_id, error.code)
        except Exception:
            await self._fail(operation_id, "INGESTION_FAILED")

    async def recover(self):
        async with self.database() as db, db.begin():
            operations = (
                await db.scalars(
                    select(IngestionOperation)
                    .where(IngestionOperation.state.in_(["queued", "running"]))
                    .with_for_update()
                )
            ).all()
            for operation in operations:
                operation.state, operation.error_code = (
                    "interrupted",
                    "EXECUTION_INTERRUPTED",
                )
                operation.finished_at = now()
                version = await db.get(MaterialVersion, operation.material_version_id)
                version.state, version.failure_code = (
                    "interrupted",
                    "EXECUTION_INTERRUPTED",
                )
                material = await db.get(Material, operation.material_id)
                material.status = (
                    "ready" if material.active_version_id else "interrupted"
                )

    async def retry(self, operation_id):
        ticket = self.executor.reserve()
        try:
            async with self.database() as db, db.begin():
                operation = await db.get(
                    IngestionOperation, operation_id, with_for_update=True
                )
                if not operation:
                    raise AppError("NOT_FOUND", "Operação não encontrada.", 404)
                if (
                    operation.state not in ("failed", "interrupted")
                    or operation.attempt >= 3
                ):
                    raise AppError(
                        "OPERATION_BUSY",
                        "Esta operação não pode ser repetida agora.",
                        409,
                    )
                version = await db.get(MaterialVersion, operation.material_version_id)
                if (
                    version.pipeline_fingerprint != pipeline_fingerprint(self.settings)
                    or version.embedding_profile_id != self.settings.embedding_profile
                ):
                    raise AppError(
                        "PIPELINE_MISMATCH",
                        "O perfil do material mudou. Reenvie para criar outra versão.",
                        409,
                    )
                operation.state, operation.stage = "queued", "validate"
                operation.attempt += 1
                operation.error_code, operation.finished_at = None, None
                version.state, version.failure_code = "processing", None
                material = await db.get(Material, version.material_id)
                material.status = (
                    "ready" if material.active_version_id else "processing"
                )
                result = receipt(operation)
            try:
                self.executor.submit(lambda: self.process(operation_id), ticket)
            except Exception:
                await self._fail(
                    operation_id, "EXECUTION_INTERRUPTED", interrupted=True
                )
                raise AppError(
                    "EXECUTION_INTERRUPTED",
                    "Não foi possível iniciar o processamento. Tente novamente.",
                    503,
                ) from None
            return result
        except BaseException:
            ticket.release()
            raise

    async def get_operation(self, operation_id):
        async with self.database() as db:
            operation = await db.get(IngestionOperation, operation_id)
            if not operation:
                raise AppError("NOT_FOUND", "Operação não encontrada.", 404)
            return receipt(operation)

    async def list_materials(self, cursor=None):
        async with self.database() as db:
            query = select(Material).order_by(Material.id).limit(51)
            if cursor:
                query = query.where(Material.id > cursor)
            values = list((await db.scalars(query)).all())
            return MaterialPage(
                items=[summary(m) for m in values[:50]],
                next_cursor=str(values[49].id) if len(values) > 50 else None,
            )

    async def material_detail(self, material_id):
        async with self.database() as db:
            material = await db.get(Material, material_id)
            if not material:
                raise AppError("NOT_FOUND", "Material não encontrado.", 404)
            versions = (
                await db.scalars(
                    select(MaterialVersion)
                    .where(MaterialVersion.material_id == material_id)
                    .order_by(MaterialVersion.version_number.desc())
                )
            ).all()
            operation_id = await db.scalar(
                select(IngestionOperation.id)
                .where(IngestionOperation.material_id == material_id)
                .order_by(IngestionOperation.created_at.desc())
                .limit(1)
            )
            return MaterialDetail(
                material=summary(material),
                origin_url=material.effective_url,
                versions=[
                    VersionSummary(
                        version_id=v.id,
                        state=v.state,
                        input_sha256=v.input_sha256,
                        pipeline_fingerprint=v.pipeline_fingerprint,
                        embedding_profile_id=v.embedding_profile_id,
                        obtained_at=v.obtained_at,
                        selected_at=v.selected_at,
                    )
                    for v in versions
                ],
                operation_id=operation_id,
            )

    async def chunks(self, material_id, version_id, chunk_id=None):
        async with self.database() as db:
            version = await db.get(MaterialVersion, version_id)
            material = await db.get(Material, material_id)
            if (
                not material
                or not version
                or version.material_id != material_id
                or version.state != "ready"
            ):
                raise AppError(
                    "NOT_FOUND", "O material ainda não está disponível.", 404
                )
            query = (
                select(Chunk)
                .where(Chunk.material_version_id == version_id)
                .order_by(Chunk.ordinal)
                .limit(2048)
            )
            if chunk_id:
                query = query.where(Chunk.id == chunk_id)
            values = (await db.scalars(query)).all()
            if chunk_id and not values:
                raise AppError("NOT_FOUND", "Trecho não encontrado.", 404)
            return [
                LibraryChunk(
                    material_id=material.id,
                    version_id=version.id,
                    chunk_id=c.id,
                    text=c.text,
                    locator=Locator.model_validate(c.locator),
                    source_kind=material.source_kind,
                    display_name=material.display_name,
                    origin_url=material.effective_url,
                )
                for c in values
            ]
