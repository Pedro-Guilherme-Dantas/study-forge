import { useEffect, useRef, useState } from "react";
import { api } from "../api";
import type { MaterialDetail as Detail, Chunk } from "../types";
import StatusBadge from "./StatusBadge";
import ErrorNotice from "./ErrorNotice";
import MarkdownView from "./MarkdownView";

export default function MaterialDetail({
  id,
  onClose,
  onChanged,
}: {
  id: string;
  onClose: () => void;
  onChanged: () => Promise<void>;
}) {
  const [detail, setDetail] = useState<Detail | null>(null);
  const [chunks, setChunks] = useState<Chunk[]>([]);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const close = useRef<HTMLButtonElement>(null);
  const panel = useRef<HTMLElement>(null);
  useEffect(() => {
    let disposed = false;
    let timer: number | undefined;
    const previous =
      document.activeElement instanceof HTMLElement
        ? document.activeElement
        : null;
    setDetail(null);
    setChunks([]);
    setError("");
    close.current?.focus();
    async function load() {
      const value = await api.material(id);
      if (disposed) return;
      setDetail(value);
      if (value.material.active_version_id) {
        const result = await api.chunks(id, value.material.active_version_id);
        if (!disposed) setChunks(result.items);
      }
      if (
        !disposed &&
        value.versions.some((version) => version.state === "processing")
      ) {
        timer = window.setTimeout(
          () =>
            void load().catch(() => {
              if (!disposed) setError("Não foi possível atualizar o material.");
            }),
          1500,
        );
      }
    }
    load().catch(() => {
      if (!disposed) setError("Não foi possível consultar o material.");
    });
    const escape = (event: KeyboardEvent) => {
      if (event.key === "Escape") onClose();
      if (event.key === "Tab") {
        const items = panel.current?.querySelectorAll<HTMLElement>(
          'a[href],button:not([disabled]),input:not([disabled]),textarea:not([disabled]),[tabindex="0"]',
        );
        if (!items?.length) return;
        const first = items[0],
          last = items[items.length - 1];
        if (event.shiftKey && document.activeElement === first) {
          event.preventDefault();
          last.focus();
        } else if (!event.shiftKey && document.activeElement === last) {
          event.preventDefault();
          first.focus();
        }
      }
    };
    window.addEventListener("keydown", escape);
    return () => {
      disposed = true;
      window.clearTimeout(timer);
      window.removeEventListener("keydown", escape);
      previous?.focus();
    };
  }, [id, onClose]);
  async function retry() {
    if (!detail?.operation_id) return;
    setBusy(true);
    setError("");
    try {
      await api.retry(detail.operation_id);
      await onChanged();
      onClose();
    } catch (error) {
      setError(
        error instanceof Error ? error.message : "Não foi possível repetir.",
      );
    } finally {
      setBusy(false);
    }
  }
  return (
    <div className="dialog-backdrop">
      <section
        ref={panel}
        className="detail-panel"
        role="dialog"
        aria-modal="true"
        aria-labelledby="material-title"
      >
        <header>
          <div>
            <span className="eyebrow">MATERIAL DA BIBLIOTECA</span>
            <h2 id="material-title">
              {detail?.material.display_name ?? "Carregando material"}
            </h2>
          </div>
          <button
            ref={close}
            className="icon-button"
            aria-label="Fechar material"
            onClick={onClose}
          >
            ×
          </button>
        </header>
        {error && <ErrorNotice message={error} />}
        <div className="detail-content">
          {detail && (
            <>
              <StatusBadge state={detail.material.status} />
              <p className="muted">
                {detail.material.source_kind === "markdown_upload"
                  ? "Origem: arquivo Markdown enviado por você."
                  : "Origem: página web selecionada por você."}
              </p>
              {detail.origin_url && (
                <a
                  href={detail.origin_url}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Consultar endereço de origem ↗
                </a>
              )}
              {!chunks.length && (
                <p>
                  Este material ainda não tem uma versão disponível para
                  consulta.
                </p>
              )}
              {chunks.map((chunk, index) => (
                <article className="source-chunk" key={chunk.chunk_id}>
                  <div className="chunk-label">
                    TRECHO {index + 1} · LINHAS {chunk.locator.start_line}–
                    {chunk.locator.end_line}
                  </div>
                  <MarkdownView text={chunk.text} />
                </article>
              ))}
              {["failed", "interrupted"].includes(
                detail.versions[0]?.state ?? "",
              ) && (
                <div className="retry-panel">
                  <p>
                    A última tentativa não foi concluída. Trechos incompletos
                    não ficam disponíveis para estudo.
                  </p>
                  <button
                    className="primary-button"
                    disabled={busy}
                    onClick={() => void retry()}
                  >
                    Tentar novamente
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      </section>
    </div>
  );
}
