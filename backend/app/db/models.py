from datetime import datetime, timezone
from uuid import UUID, uuid4
from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from pgvector.sqlalchemy import VECTOR


def now():
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class Material(Base):
    __tablename__ = "materials"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    source_kind: Mapped[str] = mapped_column(String(30))
    origin_key: Mapped[str] = mapped_column(Text)
    display_name: Mapped[str] = mapped_column(String(200))
    original_url: Mapped[str | None] = mapped_column(Text)
    effective_url: Mapped[str | None] = mapped_column(Text)
    active_version_id: Mapped[UUID | None]
    status: Mapped[str] = mapped_column(String(20), default="processing")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=now, onupdate=now
    )
    __table_args__ = (
        UniqueConstraint("source_kind", "origin_key", name="uq_material_origin"),
        CheckConstraint("source_kind IN ('markdown_upload','selected_web')"),
        CheckConstraint("status IN ('processing','ready','failed','interrupted')"),
        ForeignKeyConstraint(
            ["id", "active_version_id"],
            ["material_versions.material_id", "material_versions.id"],
            use_alter=True,
            name="fk_material_active",
        ),
    )


class EmbeddingProfile(Base):
    __tablename__ = "embedding_profiles"
    id: Mapped[str] = mapped_column(String(200), primary_key=True)
    provider: Mapped[str] = mapped_column(String(30))
    model: Mapped[str] = mapped_column(String(120))
    dimensions: Mapped[int] = mapped_column(default=768)
    configuration: Mapped[dict] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    __table_args__ = (CheckConstraint("dimensions = 768"),)


class MaterialVersion(Base):
    __tablename__ = "material_versions"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    material_id: Mapped[UUID] = mapped_column(ForeignKey("materials.id"), index=True)
    version_number: Mapped[int] = mapped_column(Integer)
    input_snapshot_text: Mapped[str] = mapped_column(Text)
    input_sha256: Mapped[str] = mapped_column(String(64))
    raw_capture_sha256: Mapped[str] = mapped_column(String(64))
    normalized_text: Mapped[str] = mapped_column(Text, default="")
    normalized_sha256: Mapped[str | None] = mapped_column(String(64))
    pipeline_fingerprint: Mapped[str] = mapped_column(String(64))
    pipeline_config: Mapped[dict] = mapped_column(JSONB)
    embedding_profile_id: Mapped[str] = mapped_column(
        ForeignKey("embedding_profiles.id")
    )
    expected_chunk_count: Mapped[int] = mapped_column(default=0)
    published_chunk_count: Mapped[int] = mapped_column(default=0)
    state: Mapped[str] = mapped_column(String(20), default="processing", index=True)
    failure_code: Mapped[str | None] = mapped_column(String(60))
    obtained_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    selected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    extractor_metadata: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    ready_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    __table_args__ = (
        UniqueConstraint("material_id", "version_number", name="uq_version_number"),
        UniqueConstraint("material_id", "id", name="uq_version_owner"),
        UniqueConstraint(
            "material_id",
            "input_sha256",
            "pipeline_fingerprint",
            "embedding_profile_id",
            name="uq_version_content",
        ),
        CheckConstraint("state IN ('processing','ready','failed','interrupted')"),
        CheckConstraint(
            "state <> 'ready' OR (published_chunk_count = expected_chunk_count AND expected_chunk_count > 0)"
        ),
    )


class Chunk(Base):
    __tablename__ = "chunks"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    material_version_id: Mapped[UUID] = mapped_column(
        ForeignKey("material_versions.id"), index=True
    )
    ordinal: Mapped[int]
    text: Mapped[str] = mapped_column(Text)
    start_char: Mapped[int]
    end_char: Mapped[int]
    locator: Mapped[dict] = mapped_column(JSONB)
    chunk_sha256: Mapped[str] = mapped_column(String(64))
    pipeline_fingerprint: Mapped[str] = mapped_column(String(64))
    embedding_profile_id: Mapped[str] = mapped_column(
        ForeignKey("embedding_profiles.id")
    )
    embedding: Mapped[list[float]] = mapped_column(VECTOR(768))
    __table_args__ = (
        UniqueConstraint("material_version_id", "ordinal", name="uq_chunk_ordinal"),
        CheckConstraint("end_char > start_char AND start_char >= 0"),
    )


class SelectionGrant(Base):
    __tablename__ = "selection_grants"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    material_version_id: Mapped[UUID] = mapped_column(
        ForeignKey("material_versions.id"), unique=True
    )
    input_sha256: Mapped[str] = mapped_column(String(64))
    source_origin_key: Mapped[str] = mapped_column(Text)
    raw_capture_sha256: Mapped[str] = mapped_column(String(64))
    obtained_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    selected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    action: Mapped[str] = mapped_column(String(40), default="explicit_user_selection")
    actor: Mapped[str] = mapped_column(String(40), default="local_personal_user")
    idempotency_hash: Mapped[str | None] = mapped_column(String(64), unique=True)
    __table_args__ = (
        CheckConstraint(
            "action = 'explicit_user_selection' AND actor = 'local_personal_user'"
        ),
    )


class IngestionOperation(Base):
    __tablename__ = "ingestion_operations"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    material_id: Mapped[UUID] = mapped_column(ForeignKey("materials.id"), index=True)
    material_version_id: Mapped[UUID] = mapped_column(
        ForeignKey("material_versions.id"), unique=True
    )
    state: Mapped[str] = mapped_column(String(20), default="queued", index=True)
    stage: Mapped[str] = mapped_column(String(20), default="validate")
    attempt: Mapped[int] = mapped_column(default=1)
    error_code: Mapped[str | None] = mapped_column(String(60))
    runner_instance_id: Mapped[str | None] = mapped_column(String(36))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    __table_args__ = (
        CheckConstraint(
            "state IN ('queued','running','succeeded','failed','interrupted')"
        ),
        CheckConstraint("stage IN ('validate','normalize','chunk','embed','publish')"),
    )
