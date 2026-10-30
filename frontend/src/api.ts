import type {
  Session,
  Runtime,
  Material,
  MaterialDetail,
  Operation,
  Chunk,
  Conversation,
  Turn,
  Citation,
  Research,
  Source,
  Progress,
} from "./types";

let session: Session | null = null;
let initializing: Promise<Session> | null = null;
let instance: string | null = null;
let temporarySourcesDiscarded = false;
let sessionEpoch = 0;

export function wereTemporarySourcesDiscarded() {
  return temporarySourcesDiscarded;
}

export class ApiError extends Error {
  constructor(
    message: string,
    public code = "NETWORK_ERROR",
    public status = 0,
  ) {
    super(message);
  }
}

async function decode<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    if (response.status === 410 && body.error?.code === "SESSION_EXPIRED")
      reset();
    throw new ApiError(
      body.error?.message ?? "Não foi possível concluir a operação.",
      body.error?.code,
      response.status,
    );
  }
  return response.status === 204
    ? (undefined as T)
    : (response.json() as Promise<T>);
}

export function reset() {
  sessionEpoch++;
  temporarySourcesDiscarded = true;
  session = null;
  initializing = null;
  window.dispatchEvent(new Event("studyforge:reset"));
}

export async function getRuntime(): Promise<Runtime> {
  const runtime = await decode<Runtime>(
    await fetch("/api/runtime", { cache: "no-store" }),
  );
  if (instance && instance !== runtime.server_instance_id) reset();
  instance = runtime.server_instance_id;
  return runtime;
}

async function ensureSession(): Promise<Session> {
  if (session) return session;
  if (!initializing) {
    const epoch = sessionEpoch;
    initializing = fetch("/api/sessions", {
      method: "POST",
      credentials: "same-origin",
      cache: "no-store",
    })
      .then(decode<Session>)
      .then((value) => {
        if (epoch !== sessionEpoch)
          throw new ApiError(
            "A sessão mudou. Envie a pergunta novamente.",
            "SESSION_EXPIRED",
            410,
          );
        session = value;
        return value;
      })
      .finally(() => {
        if (epoch === sessionEpoch) initializing = null;
      });
  }
  return initializing;
}

export async function request<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const epoch = sessionEpoch;
  const current = await ensureSession();
  if (epoch !== sessionEpoch)
    throw new ApiError(
      "A sessão mudou. Repita a ação desejada.",
      "SESSION_EXPIRED",
      410,
    );
  const headers = new Headers(options.headers);
  if (options.method && options.method !== "GET")
    headers.set("X-CSRF-Token", current.csrf_token);
  const value = await decode<T>(
    await fetch(path, {
      ...options,
      headers,
      credentials: "same-origin",
      cache: "no-store",
    }),
  );
  if (epoch !== sessionEpoch)
    throw new ApiError(
      "A sessão mudou. Repita a ação desejada.",
      "SESSION_EXPIRED",
      410,
    );
  return value;
}

export const api = {
  progress: () => request<Progress>("/api/progress"),
  research: (id: string, topic: string) =>
    request<{ research_id: string; status: "running" }>(
      `/api/conversations/${id}/research`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic }),
      },
    ),
  researchResult: (id: string, research: string) =>
    request<Research>(`/api/conversations/${id}/research/${research}`),
  decision: (id: string, offer: string, accept: boolean) =>
    request<{
      offer_id: string;
      state: "accepted" | "declined";
      research_id: string | null;
    }>(`/api/conversations/${id}/research-offers/${offer}/decision`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ accept }),
    }),
  source: (id: string, source: string) =>
    request<{ source: Source; snapshot_text: string }>(
      `/api/conversations/${id}/sources/${source}`,
    ),
  select: (id: string, source: string, hash: string, key: string) =>
    request<{
      material_id: string;
      version_id: string;
      operation_id: string;
      selection_status: "accepted" | "already_accepted";
    }>(`/api/conversations/${id}/sources/${source}/selection`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "Idempotency-Key": key },
      body: JSON.stringify({ snapshot_hash: hash }),
    }),
  conversation: () =>
    request<Conversation>("/api/conversations", { method: "POST" }),
  close: async (id: string) => {
    await request<void>("/api/conversations/" + encodeURIComponent(id), {
      method: "DELETE",
    });
    sessionEpoch++;
    temporarySourcesDiscarded = true;
  },
  turn: (id: string, message: string, intent = "auto") =>
    request<{ turn_id: string; status: "running" }>(
      "/api/conversations/" + encodeURIComponent(id) + "/turns",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message, intent }),
      },
    ),
  turnResult: (id: string, turn: string) =>
    request<Turn>(
      "/api/conversations/" +
        encodeURIComponent(id) +
        "/turns/" +
        encodeURIComponent(turn),
    ),
  citation: (id: string, citation: string) =>
    request<Citation>(
      "/api/conversations/" +
        encodeURIComponent(id) +
        "/citations/" +
        encodeURIComponent(citation),
    ),
  materials: (cursor?: string) =>
    request<{ items: Material[]; next_cursor: string | null }>(
      "/api/materials" +
        (cursor ? "?cursor=" + encodeURIComponent(cursor) : ""),
    ),
  material: (id: string) =>
    request<MaterialDetail>("/api/materials/" + encodeURIComponent(id)),
  chunks: (id: string, version: string) =>
    request<{ items: Chunk[] }>(
      "/api/materials/" +
        encodeURIComponent(id) +
        "/versions/" +
        encodeURIComponent(version) +
        "/chunks",
    ),
  operation: (id: string) =>
    request<Operation>("/api/operations/" + encodeURIComponent(id)),
  retry: (id: string) =>
    request<Operation>("/api/operations/" + encodeURIComponent(id) + "/retry", {
      method: "POST",
    }),
  upload: (file: File) => {
    const body = new FormData();
    body.set("file", file);
    return request<Operation>("/api/materials", { method: "POST", body });
  },
};
