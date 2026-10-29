"""Called only by the protected selection endpoint, never made available to a model."""

from uuid import uuid4
from sqlalchemy import select, func
from sqlalchemy.dialects.postgresql import insert
from app.db.models import (
    Material,
    MaterialVersion,
    EmbeddingProfile,
    IngestionOperation,
    SelectionGrant,
    now,
)
from app.errors import AppError
from app.schemas import PromotionReceipt
from app.ingestion.chunk import digest, pipeline_fingerprint, pipeline_config


class PromotionService:
    def __init__(self, ingestion):
        self.ingestion = ingestion

    async def select(
        self, conversation, source_id, expected_hash, idempotency_key=None
    ):
        service = self.ingestion
        key = digest(idempotency_key) if idempotency_key else None
        if idempotency_key and (len(idempotency_key) > 128 or len(idempotency_key) < 8):
            raise AppError("INVALID_REQUEST", "A chave da seleção é inválida.", 422)
        async with conversation.lock:
            if conversation.closed:
                raise AppError("SOURCE_EXPIRED", "A conversa foi encerrada.", 410)
            snapshot = conversation.sources.get(str(source_id))
            if not snapshot:
                raise AppError("SOURCE_EXPIRED", "A fonte temporária expirou.", 410)
            if (
                snapshot.summary.snapshot_hash != expected_hash
                or digest(snapshot.text) != expected_hash
            ):
                raise AppError(
                    "SOURCE_CHANGED",
                    "A identidade da fonte mudou. Consulte-a novamente.",
                    409,
                )
            if (
                snapshot.fingerprint != pipeline_fingerprint(service.settings)
                or snapshot.embedding_profile != service.settings.embedding_profile
            ):
                raise AppError(
                    "PIPELINE_MISMATCH",
                    "O perfil da fonte mudou. Faça outra pesquisa.",
                    409,
                )
            ticket = None
            try:
                async with service.database() as db, db.begin():
                    # Local personal actor; serializes idempotency across selected sources.
                    await db.execute(select(func.pg_advisory_xact_lock(72198341)))
                    existing_key = (
                        await db.scalar(
                            select(SelectionGrant).where(
                                SelectionGrant.idempotency_hash == key
                            )
                        )
                        if key
                        else None
                    )
                    if existing_key and (
                        existing_key.input_sha256 != expected_hash
                        or existing_key.source_origin_key != snapshot.effective_url
                    ):
                        raise AppError(
                            "SELECTION_CONFLICT",
                            "Esta chave já identifica outra seleção.",
                            409,
                        )
                    profile = service.settings.embedding_profile
                    await db.execute(
                        insert(EmbeddingProfile)
                        .values(
                            id=profile,
                            provider="fixture"
                            if service.settings.app_mode == "fixture"
                            else service.settings.gemini_backend,
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
                            source_kind="selected_web",
                            origin_key=snapshot.effective_url,
                            display_name=snapshot.summary.title,
                            original_url=snapshot.summary.origin_url,
                            effective_url=snapshot.effective_url,
                            status="processing",
                        )
                        .on_conflict_do_nothing(
                            index_elements=["source_kind", "origin_key"]
                        )
                    )
                    material = await db.scalar(
                        select(Material)
                        .where(
                            Material.source_kind == "selected_web",
                            Material.origin_key == snapshot.effective_url,
                        )
                        .with_for_update()
                    )
                    version = await db.scalar(
                        select(MaterialVersion).where(
                            MaterialVersion.material_id == material.id,
                            MaterialVersion.input_sha256 == expected_hash,
                            MaterialVersion.pipeline_fingerprint
                            == snapshot.fingerprint,
                            MaterialVersion.embedding_profile_id == profile,
                        )
                    )
                    if version:
                        grant = await db.scalar(
                            select(SelectionGrant).where(
                                SelectionGrant.material_version_id == version.id
                            )
                        )
                        if not grant:
                            raise AppError(
                                "SELECTION_REQUIRED",
                                "A autorização dessa versão não está disponível.",
                                409,
                            )
                        operation = await db.scalar(
                            select(IngestionOperation).where(
                                IngestionOperation.material_version_id == version.id
                            )
                        )
                        result = PromotionReceipt(
                            material_id=material.id,
                            version_id=version.id,
                            operation_id=operation.id,
                            selection_status="already_accepted",
                        )
                        return result
                    # Repeated selection only reads an existing receipt. It must not
                    # require worker capacity or start another ingestion.
                    ticket = service.executor.reserve()
                    number = (
                        await db.scalar(
                            select(func.max(MaterialVersion.version_number)).where(
                                MaterialVersion.material_id == material.id
                            )
                        )
                        or 0
                    ) + 1
                    version = MaterialVersion(
                        id=uuid4(),
                        material_id=material.id,
                        version_number=number,
                        input_snapshot_text=snapshot.text,
                        input_sha256=expected_hash,
                        raw_capture_sha256=snapshot.raw_hash,
                        pipeline_fingerprint=snapshot.fingerprint,
                        pipeline_config=pipeline_config(service.settings),
                        embedding_profile_id=profile,
                        state="processing",
                        obtained_at=snapshot.summary.obtained_at,
                        selected_at=now(),
                        extractor_metadata={
                            "name": "trafilatura",
                            "fingerprint": snapshot.extraction_fingerprint,
                            "capture_persisted": False,
                        },
                    )
                    db.add(version)
                    await db.flush()
                    db.add(
                        SelectionGrant(
                            material_version_id=version.id,
                            input_sha256=expected_hash,
                            source_origin_key=snapshot.effective_url,
                            raw_capture_sha256=snapshot.raw_hash,
                            obtained_at=snapshot.summary.obtained_at,
                            selected_at=version.selected_at,
                            idempotency_hash=key,
                        )
                    )
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
                    result = PromotionReceipt(
                        material_id=material.id,
                        version_id=version.id,
                        operation_id=operation.id,
                        selection_status="accepted",
                    )
                try:
                    service.executor.submit(
                        lambda: service.process(result.operation_id), ticket
                    )
                except Exception:
                    await service._fail(
                        result.operation_id, "EXECUTION_INTERRUPTED", interrupted=True
                    )
                    raise AppError(
                        "EXECUTION_INTERRUPTED",
                        "A seleção foi guardada, mas o processamento foi interrompido. Consulte a operação.",
                        503,
                    ) from None
                return result
            except BaseException:
                if ticket is not None:
                    ticket.release()
                raise
