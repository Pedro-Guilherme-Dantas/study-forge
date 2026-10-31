from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, model_validator

Hash = Annotated[str, Field(pattern=r"^[a-f0-9]{64}$")]
MaterialState = Literal["processing", "ready", "failed", "interrupted"]
OperationState = Literal["queued", "running", "succeeded", "failed", "interrupted"]
Stage = Literal["validate", "normalize", "chunk", "embed", "publish"]
ResearchState = Literal[
    "running", "succeeded", "partial", "empty", "failed", "interrupted"
]


class Model(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ErrorBody(Model):
    code: str
    message: str
    stage: str
    retryable: bool
    request_id: str


class ErrorEnvelope(Model):
    error: ErrorBody


class ExperimentLimits(Model):
    max_upload_bytes: int = Field(ge=1)
    max_html_bytes: int = Field(ge=1)
    max_pages_per_research: int = Field(ge=1)
    max_temporary_sources: int = Field(ge=1)
    max_message_bytes: int = Field(ge=1)
    max_graph_steps: int = Field(ge=1)
    max_external_attempts: int = Field(ge=1)
    embedding_dimensions: int = Field(ge=1)
    retrieval_top_k: int = Field(ge=1)


class ProviderInfo(Model):
    backend: Literal["developer", "vertex", "fixture"]
    generation_model: str
    embedding_model: str
    retention_status: Literal["provider_managed", "fixture_only"]
    disclosure: str


class RuntimeInfo(Model):
    server_instance_id: UUID
    access: Literal["localhost_only"] = "localhost_only"
    provider: ProviderInfo
    temporary_lifetime: Literal["conversation_close_or_app_restart"] = (
        "conversation_close_or_app_restart"
    )
    chat_history: Literal["memory_only"] = "memory_only"
    limits: ExperimentLimits


class ObservabilityInfo(Model):
    enabled: bool
    capture: Literal["operational_metadata_only", "content"]
    sent: int = Field(ge=0)
    failed: int = Field(ge=0)
    dropped: int = Field(ge=0)
    queued: int = Field(ge=0)
    last_error_code: (
        Literal[
            "EXPORT_TIMEOUT",
            "EXPORT_RATE_LIMITED",
            "EXPORT_AUTH_FAILED",
            "EXPORT_FAILED",
        ]
        | None
    ) = None


class SessionReceipt(Model):
    session_id: UUID
    server_instance_id: UUID
    csrf_token: str


class ConversationReceipt(Model):
    conversation_id: UUID
    server_instance_id: UUID
    epoch: int = Field(ge=0)
    state: Literal["open"] = "open"


class Locator(Model):
    kind: Literal["markdown_original", "html_extracted_snapshot"]
    section_path: list[str]
    start_char: int = Field(ge=0)
    end_char: int = Field(ge=1)
    start_line: int = Field(ge=1)
    end_line: int = Field(ge=1)
    offset_unit: Literal["unicode_code_point"] = "unicode_code_point"
    block_index: int = Field(default=0, ge=0)

    @model_validator(mode="after")
    def ordered(self):
        if self.end_char <= self.start_char or self.end_line < self.start_line:
            raise ValueError("Invalid source interval")
        return self


class LibraryCitation(Model):
    citation_id: str
    scope: Literal["library"] = "library"
    title: str
    quote: str
    locator: Locator
    material_id: UUID
    version_id: UUID
    chunk_id: str


class TemporaryCitation(Model):
    citation_id: str
    scope: Literal["temporary"] = "temporary"
    title: str
    quote: str
    locator: Locator
    source_id: UUID
    snapshot_hash: Hash
    origin_url: str = Field(json_schema_extra={"format": "uri"})


Citation = Annotated[LibraryCitation | TemporaryCitation, Field(discriminator="scope")]


class TurnRequest(Model):
    message: str = Field(min_length=1)
    intent: Literal["auto", "research"] = "auto"


class TurnReceipt(Model):
    turn_id: UUID
    status: Literal["running"] = "running"


class ResearchOffer(Model):
    offer_id: UUID
    turn_id: UUID
    reason_code: Literal["KB_INSUFFICIENT"] = "KB_INSUFFICIENT"
    topic: str
    state: Literal["awaiting", "accepted", "declined"] = "awaiting"


class TurnResult(Model):
    turn_id: UUID
    status: Literal[
        "running",
        "awaiting_research_consent",
        "complete",
        "partial",
        "insufficient",
        "failed",
    ]
    answer_markdown: str | None = None
    evidence_status: (
        Literal["supported", "partial", "insufficient", "conflicting"] | None
    ) = None
    citations: list[Citation] = Field(default_factory=list)
    research_offer: ResearchOffer | None = None
    research_id: UUID | None = None
    error: ErrorEnvelope | None = None


class ResearchRequest(Model):
    topic: str = Field(min_length=1)


class ResearchReceipt(Model):
    research_id: UUID
    status: Literal["running"] = "running"


class OfferRequest(Model):
    accept: bool


class OfferDecision(Model):
    offer_id: UUID
    state: Literal["accepted", "declined"]
    research_id: UUID | None = None


class SourceSummary(Model):
    source_id: UUID
    title: str
    origin_url: str = Field(json_schema_extra={"format": "uri"})
    state: Literal["available", "unavailable"]
    snapshot_hash: Hash | None = None
    obtained_at: datetime | None = None
    preview: str | None = None
    error_code: str | None = None


class ResearchResult(Model):
    research_id: UUID
    status: ResearchState
    sources: list[SourceSummary] = Field(default_factory=list)
    error_codes: list[str] = Field(default_factory=list)


class TemporarySourceDetail(Model):
    source: SourceSummary
    snapshot_text: str
    locator_kind: Literal["html_extracted_snapshot"] = "html_extracted_snapshot"
    pipeline_fingerprint: Hash
    temporary: Literal[True] = True


class SelectionRequest(Model):
    snapshot_hash: Hash


class PromotionReceipt(Model):
    material_id: UUID
    version_id: UUID
    operation_id: UUID
    selection_status: Literal["accepted", "already_accepted"]


class MaterialSummary(Model):
    material_id: UUID
    source_kind: Literal["markdown_upload", "selected_web"]
    display_name: str
    status: MaterialState
    active_version_id: UUID | None = None


class MaterialPage(Model):
    items: list[MaterialSummary]
    next_cursor: str | None = None


class VersionSummary(Model):
    version_id: UUID
    state: MaterialState
    input_sha256: Hash
    pipeline_fingerprint: Hash
    embedding_profile_id: str
    obtained_at: datetime | None = None
    selected_at: datetime | None = None


class MaterialDetail(Model):
    material: MaterialSummary
    origin_url: str | None = None
    versions: list[VersionSummary]
    operation_id: UUID | None = None


class LibraryChunk(Model):
    material_id: UUID
    version_id: UUID
    chunk_id: str
    text: str
    locator: Locator
    source_kind: Literal["markdown_upload", "selected_web"]
    display_name: str
    origin_url: str | None = None


class IngestionReceipt(Model):
    operation_id: UUID
    material_id: UUID
    version_id: UUID
    state: OperationState
    stage: Stage
    attempt: int = Field(ge=1)
    error_code: str | None = None


class ResearchSummary(Model):
    research_id: UUID
    status: ResearchState


class ProgressSnapshot(Model):
    materials: list[MaterialSummary]
    ingestions: list[IngestionReceipt]
    research: list[ResearchSummary]


class HealthInfo(Model):
    status: Literal["ok", "not_ready"]
    database_ready: bool
