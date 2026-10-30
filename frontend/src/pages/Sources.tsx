import { useCallback, useEffect, useState } from "react";
import { api, wereTemporarySourcesDiscarded } from "../api";
import type { Source, Research } from "../types";
import ErrorNotice from "../components/ErrorNotice";
import MarkdownView from "../components/MarkdownView";

const expirationNotice =
  "Fontes temporárias anteriores expiraram após encerramento ou reinício.";

export default function Sources({ fixture }: { fixture: boolean }) {
  const [conversation, setConversation] = useState("");
  const [sources, setSources] = useState<Source[]>([]);
  const [topic, setTopic] = useState("");
  const [error, setError] = useState("");
  const [notice, setNotice] = useState(() =>
    wereTemporarySourcesDiscarded() ? expirationNotice : "",
  );
  const [researchStatus, setResearchStatus] = useState<
    Research["status"] | null
  >(null);
  const [running, setRunning] = useState(false);
  const [busy, setBusy] = useState(false);
  const [inspected, setInspected] = useState<
    Record<string, { text: string; hash: string }>
  >({});
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [accepted, setAccepted] = useState<Set<string>>(new Set());
  const refresh = useCallback(async () => {
    const progress = await api.progress();
    if (!progress.research.length) {
      setSources([]);
      setRunning(false);
      setResearchStatus(null);
      return;
    }
    const id = (await api.conversation()).conversation_id;
    setNotice((current) => (current === expirationNotice ? "" : current));
    setConversation(id);
    const research = await Promise.all(
      progress.research.map((item) => api.researchResult(id, item.research_id)),
    );
    setRunning(research.some((item) => item.status === "running"));
    setResearchStatus(research.at(-1)?.status ?? null);
    setSources([
      ...new Map(
        research
          .flatMap((item) => item.sources)
          .map((source) => [source.source_id, source]),
      ).values(),
    ]);
  }, []);
  useEffect(() => {
    let active = true;
    const update = () => {
      if (active)
        void refresh().catch((error) =>
          setError(
            error instanceof Error
              ? error.message
              : "Não foi possível consultar fontes.",
          ),
        );
    };
    update();
    const interval = window.setInterval(update, 1500);
    const reset = () => {
      setSources([]);
      setInspected({});
      setSelected(new Set());
      setAccepted(new Set());
      setConversation("");
      setRunning(false);
      setResearchStatus(null);
      setNotice(expirationNotice);
    };
    window.addEventListener("studyforge:reset", reset);
    window.addEventListener("studyforge:closed", reset);
    return () => {
      active = false;
      window.clearInterval(interval);
      window.removeEventListener("studyforge:reset", reset);
      window.removeEventListener("studyforge:closed", reset);
    };
  }, [refresh]);
  async function search() {
    setBusy(true);
    setError("");
    setNotice("");
    try {
      const id = (await api.conversation()).conversation_id;
      setConversation(id);
      await api.research(id, topic);
      setTopic("");
      await refresh();
    } catch (error) {
      setError(
        error instanceof Error ? error.message : "Pesquisa indisponível.",
      );
    } finally {
      setBusy(false);
    }
  }
  async function inspect(source: Source) {
    try {
      const detail = await api.source(conversation, source.source_id);
      setInspected((values) => ({
        ...values,
        [source.source_id]: {
          text: detail.snapshot_text,
          hash: detail.source.snapshot_hash!,
        },
      }));
    } catch (error) {
      setError(error instanceof Error ? error.message : "Fonte expirada.");
    }
  }
  async function save() {
    setBusy(true);
    setError("");
    try {
      for (const id of selected) {
        const snapshot = inspected[id];
        if (!snapshot) continue;
        const receipt = await api.select(
          conversation,
          id,
          snapshot.hash,
          "selection-" + id,
        );
        setAccepted((values) => new Set([...values, id]));
        setNotice(
          "Seleção aceita. Acompanhe a ingestão na biblioteca ou em Progresso. Operação: " +
            receipt.operation_id,
        );
      }
      setSelected(new Set());
      await refresh();
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : "Não foi possível guardar a seleção.",
      );
    } finally {
      setBusy(false);
    }
  }
  return (
    <section>
      <div className="page-heading">
        <div>
          <span className="eyebrow">EXPLORE ANTES DE GUARDAR</span>
          <h1>
            Fontes da pesquisa<span>.</span>
          </h1>
          <p>
            Consulte as fontes temporárias e selecione apenas o que quer manter.
          </p>
        </div>
      </div>
      <p className="muted">
        As fontes duram até encerrar a conversa ou reiniciar. Navegar entre
        telas não as descarta.
        {fixture &&
          " No modo fixture, são páginas sintéticas locais, sem pesquisa real."}
      </p>
      <form
        className="research-form"
        onSubmit={(event) => {
          event.preventDefault();
          void search();
        }}
      >
        <label htmlFor="topic">Pesquisar um assunto</label>
        <div>
          <input
            id="topic"
            value={topic}
            onChange={(event) => setTopic(event.target.value)}
            placeholder="Qual assunto você quer explorar?"
            maxLength={2000}
          />
          <button
            className="primary-button"
            disabled={busy || running || !topic.trim()}
          >
            Pesquisar ↗
          </button>
        </div>
      </form>
      {error && <ErrorNotice message={error} />}{" "}
      {notice && <p role="status">{notice}</p>}
      {researchStatus === "empty" && (
        <p role="status">
          A pesquisa terminou sem encontrar fontes utilizáveis. Tente outro
          assunto ou reformule a busca.
        </p>
      )}
      {researchStatus === "failed" && (
        <ErrorNotice message="A pesquisa falhou. Nenhuma fonte desta tentativa ficou disponível. Tente novamente; fontes anteriores continuam disponíveis até encerrar a conversa." />
      )}
      {researchStatus === "partial" && (
        <p role="status">
          A pesquisa terminou com falha parcial. Somente as fontes disponíveis
          podem fundamentar respostas ou ser selecionadas.
        </p>
      )}
      {running && <p role="status">Pesquisa em andamento…</p>}
      {!sources.length && !running && (
        <div className="empty-state">
          <span>⌕</span>
          <h3>Nenhuma fonte disponível.</h3>
          <p>
            {researchStatus === "empty" || researchStatus === "failed"
              ? "Você pode fazer uma nova pesquisa pelo campo acima."
              : "Inicie uma pesquisa ou aceite uma oferta no chat."}
          </p>
        </div>
      )}
      <div className="source-grid">
        {sources.map((source) => (
          <article className="source-card" key={source.source_id}>
            <span className="eyebrow">
              FONTE TEMPORÁRIA ·{" "}
              {source.state === "available" ? "DISPONÍVEL" : "INDISPONÍVEL"}
            </span>
            <h3>{source.title}</h3>
            <a
              href={source.origin_url}
              target="_blank"
              rel="noopener noreferrer"
            >
              Consultar endereço de origem ↗
            </a>
            <p>
              {source.preview ??
                "Esta fonte não pôde ser obtida ou processada. Ela não será usada para fundamentar respostas."}
            </p>
            {source.state === "available" && (
              <button
                className="secondary-button"
                onClick={() => void inspect(source)}
              >
                Inspecionar conteúdo
              </button>
            )}
            {inspected[source.source_id] && (
              <>
                <div className="source-preview">
                  <MarkdownView text={inspected[source.source_id].text} />
                </div>
                <label className="source-selection">
                  <input
                    type="checkbox"
                    checked={selected.has(source.source_id)}
                    disabled={accepted.has(source.source_id) || busy}
                    onChange={(event) =>
                      setSelected((values) => {
                        const next = new Set(values);
                        if (event.target.checked) next.add(source.source_id);
                        else next.delete(source.source_id);
                        return next;
                      })
                    }
                  />
                  {accepted.has(source.source_id)
                    ? "Seleção já aceita"
                    : "Quero guardar esta fonte"}
                </label>
              </>
            )}
          </article>
        ))}
      </div>
      {selected.size > 0 && (
        <div className="selection-toolbar">
          <p>{selected.size} fonte(s) selecionada(s) por você</p>
          <button
            className="primary-button"
            disabled={busy}
            onClick={() => void save()}
          >
            Guardar selecionadas
          </button>
        </div>
      )}
    </section>
  );
}
