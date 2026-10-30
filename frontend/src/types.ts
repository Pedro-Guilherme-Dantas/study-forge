export type MaterialState = "processing" | "ready" | "failed" | "interrupted";
export type OperationState =
  "queued" | "running" | "succeeded" | "failed" | "interrupted";
export type Locator = {
  kind: "markdown_original" | "html_extracted_snapshot";
  section_path: string[];
  start_char: number;
  end_char: number;
  start_line: number;
  end_line: number;
  offset_unit: "unicode_code_point";
  block_index?: number;
};
export type Material = {
  material_id: string;
  source_kind: "markdown_upload" | "selected_web";
  display_name: string;
  status: MaterialState;
  active_version_id: string | null;
};
export type Version = {
  version_id: string;
  state: MaterialState;
  input_sha256: string;
  pipeline_fingerprint: string;
  embedding_profile_id: string;
  obtained_at: string | null;
  selected_at: string | null;
};
export type MaterialDetail = {
  material: Material;
  origin_url: string | null;
  versions: Version[];
  operation_id: string | null;
};
export type Chunk = {
  material_id: string;
  version_id: string;
  chunk_id: string;
  text: string;
  locator: Locator;
  source_kind: "markdown_upload" | "selected_web";
  display_name: string;
  origin_url: string | null;
};
export type Operation = {
  operation_id: string;
  material_id: string;
  version_id: string;
  state: OperationState;
  stage: "validate" | "normalize" | "chunk" | "embed" | "publish";
  attempt: number;
  error_code: string | null;
};
export type Runtime = {
  server_instance_id: string;
  access: "localhost_only";
  provider: {
    backend: "developer" | "vertex" | "fixture";
    generation_model: string;
    embedding_model: string;
    retention_status: "provider_managed" | "fixture_only";
    disclosure: string;
  };
  limits: Record<string, number>;
  temporary_lifetime: "conversation_close_or_app_restart";
  chat_history: "memory_only";
};
export type Session = {
  session_id: string;
  server_instance_id: string;
  csrf_token: string;
};
export type Conversation = {
  conversation_id: string;
  server_instance_id: string;
  epoch: number;
  state: "open";
};
type CitationBase = {
  citation_id: string;
  title: string;
  quote: string;
  locator: Locator;
};
export type LibraryCitation = CitationBase & {
  scope: "library";
  material_id: string;
  version_id: string;
  chunk_id: string;
};
export type TemporaryCitation = CitationBase & {
  scope: "temporary";
  source_id: string;
  snapshot_hash: string;
  origin_url: string;
};
export type Citation = LibraryCitation | TemporaryCitation;
export type ResearchOffer = {
  reason_code: "KB_INSUFFICIENT";
  offer_id: string;
  turn_id: string;
  topic: string;
  state: "awaiting" | "accepted" | "declined";
};
export type Turn = {
  turn_id: string;
  status:
    | "running"
    | "awaiting_research_consent"
    | "complete"
    | "partial"
    | "insufficient"
    | "failed";
  answer_markdown: string | null;
  evidence_status:
    "supported" | "partial" | "insufficient" | "conflicting" | null;
  citations: Citation[];
  research_offer: ResearchOffer | null;
  research_id: string | null;
  error: {
    error: {
      code: string;
      message: string;
      stage: string;
      retryable: boolean;
      request_id: string;
    };
  } | null;
};
export type Source = {
  source_id: string;
  title: string;
  origin_url: string;
  state: "available" | "unavailable";
  snapshot_hash: string | null;
  obtained_at: string | null;
  preview: string | null;
  error_code: string | null;
};
export type Research = {
  research_id: string;
  status:
    "running" | "succeeded" | "partial" | "empty" | "failed" | "interrupted";
  sources: Source[];
  error_codes: string[];
};
export type Progress = {
  materials: Material[];
  ingestions: Operation[];
  research: { research_id: string; status: Research["status"] }[];
};
