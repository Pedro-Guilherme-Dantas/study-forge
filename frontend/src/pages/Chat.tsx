import { useEffect, useRef, useState } from "react";
import { api } from "../api";
import type { Turn } from "../types";
import MarkdownView from "../components/MarkdownView";
import Citation from "../components/Citation";
import ErrorNotice from "../components/ErrorNotice";

type Entry = { question: string; result: Turn };
const evidenceLabels = {
  supported: "COM SUPORTE",
  partial: "SUPORTE PARCIAL",
  insufficient: "EVIDÊNCIA INSUFICIENTE",
  conflicting: "FONTES EM CONFLITO",
};
export default function Chat() {
  const [conversation, setConversation] = useState("");
  const [entries, setEntries] = useState<Entry[]>([]);
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const generation = useRef(0);
  const input = useRef<HTMLTextAreaElement>(null);
  useEffect(() => {
    const clear = () => {
      generation.current++;
      setConversation("");
      setEntries([]);
      setMessage("");
      setBusy(false);
      setError("A aplicação reiniciou. A conversa anterior foi descartada.");
    };
    window.addEventListener("studyforge:reset", clear);
    return () => {
      generation.current++;
      window.removeEventListener("studyforge:reset", clear);
    };
  }, []);
  async function send() {
    if (!message.trim() || busy) return;
    const epoch = generation.current;
    setBusy(true);
    setError("");
    const question = message;
    try {
      const id = conversation || (await api.conversation()).conversation_id;
      if (generation.current !== epoch) return;
      setConversation(id);
      const receipt = await api.turn(id, question);
      if (generation.current !== epoch) return;
      setMessage("");
      const result = {
        ...receipt,
        answer_markdown: null,
        evidence_status: null,
        citations: [],
        research_offer: null,
        research_id: null,
        error: null,
      } satisfies Turn;
      setEntries((values) => [...values, { question, result }]);
      for (;;) {
        const value = await api.turnResult(id, receipt.turn_id);
        if (generation.current !== epoch) return;
        setEntries((values) =>
          values.map((entry) =>
            entry.result.turn_id === receipt.turn_id
              ? { ...entry, result: value }
              : entry,
          ),
        );
        if (value.status !== "running") break;
        await new Promise((resolve) => window.setTimeout(resolve, 700));
      }
    } catch (error) {
      if (generation.current === epoch)
        setError(
          error instanceof Error
            ? error.message
            : "Não foi possível responder.",
        );
    } finally {
      if (generation.current === epoch) {
        setBusy(false);
        input.current?.focus();
      }
    }
  }
  async function close() {
    generation.current++;
    setBusy(true);
    setError("");
    try {
      if (conversation) await api.close(conversation);
      window.dispatchEvent(new Event("studyforge:closed"));
      setConversation("");
      setEntries([]);
      setMessage("");
      const next = await api.conversation();
      setConversation(next.conversation_id);
    } catch (error) {
      setError(
        error instanceof Error ? error.message : "Não foi possível encerrar.",
      );
    } finally {
      setBusy(false);
      input.current?.focus();
    }
  }
  async function decide(turn: Turn, accept: boolean) {
    if (!turn.research_offer || busy) return;
    setBusy(true);
    setError("");
    const epoch = generation.current;
    try {
      await api.decision(conversation, turn.research_offer.offer_id, accept);
      for (;;) {
        const result = await api.turnResult(conversation, turn.turn_id);
        if (epoch !== generation.current) return;
        setEntries((values) =>
          values.map((entry) =>
            entry.result.turn_id === turn.turn_id
              ? { ...entry, result }
              : entry,
          ),
        );
        if (result.status !== "running") break;
        await new Promise((resolve) => window.setTimeout(resolve, 700));
      }
    } catch (error) {
      if (epoch === generation.current)
        setError(
          error instanceof Error
            ? error.message
            : "Não foi possível registrar a decisão.",
        );
    } finally {
      if (epoch === generation.current) setBusy(false);
    }
  }
  return (
    <section className="chat-page">
      <div className="page-heading">
        <div>
          <span className="eyebrow">APRENDA A PARTIR DAS SUAS FONTES</span>
          <h1>
            Uma boa pergunta<span>.</span>
          </h1>
          <p>
            Converse com seus materiais e confira de onde vem cada resposta.
          </p>
        </div>
        <button className="secondary-button" onClick={() => void close()}>
          Encerrar conversa
        </button>
      </div>
      <p className="muted">
        Esta conversa fica apenas na memória. Encerrar ou reiniciar descarta
        mensagens e fontes temporárias.
      </p>
      {error && <ErrorNotice message={error} />}
      <div className="chat-history" aria-live="polite">
        {entries.length === 0 && (
          <div className="empty-state">
            <span>✧</span>
            <h3>O que você quer compreender hoje?</h3>
            <p>
              Faça uma pergunta sobre os materiais disponíveis na biblioteca.
            </p>
          </div>
        )}
        {entries.map((entry) => (
          <article className="chat-entry" key={entry.result.turn_id}>
            <div className="user-question">
              <span className="eyebrow">SUA PERGUNTA</span>
              <p>{entry.question}</p>
            </div>
            <div className="tutor-answer">
              <span className="eyebrow">
                TUTOR ·{" "}
                {entry.result.evidence_status
                  ? evidenceLabels[entry.result.evidence_status]
                  : entry.result.status === "failed"
                    ? "FALHA NA RESPOSTA"
                    : "CONSULTANDO MATERIAIS"}
              </span>
              {entry.result.status === "running" && (
                <p role="status">Recuperando fontes e preparando a resposta…</p>
              )}
              {entry.result.answer_markdown && (
                <MarkdownView text={entry.result.answer_markdown} />
              )}{" "}
              {entry.result.error && (
                <ErrorNotice message={entry.result.error.error.message} />
              )}
              <div className="citation-list">
                {entry.result.citations.map((citation) => (
                  <Citation
                    key={citation.citation_id}
                    citation={citation}
                    conversation={conversation}
                  />
                ))}
              </div>
              {entry.result.research_offer && (
                <div className="research-offer">
                  <p>
                    A base disponível não sustenta uma resposta completa. Deseja
                    pesquisar fontes na web?
                  </p>
                  <div>
                    <button
                      className="primary-button"
                      disabled={busy}
                      onClick={() => void decide(entry.result, true)}
                    >
                      Aceitar pesquisa
                    </button>
                    <button
                      className="secondary-button"
                      disabled={busy}
                      onClick={() => void decide(entry.result, false)}
                    >
                      Agora não
                    </button>
                  </div>
                </div>
              )}
            </div>
          </article>
        ))}
      </div>
      <form
        className="chat-composer"
        onSubmit={(event) => {
          event.preventDefault();
          void send();
        }}
      >
        <label htmlFor="question">Sua pergunta</label>
        <textarea
          ref={input}
          id="question"
          value={message}
          onChange={(event) => setMessage(event.target.value)}
          placeholder="Quero entender melhor…"
          rows={3}
          maxLength={32000}
        />
        <div>
          <span>Respostas fundamentadas dependem das fontes disponíveis.</span>
          <button
            className="primary-button"
            disabled={busy || !message.trim()}
            type="submit"
          >
            {busy ? "Preparando…" : "Enviar pergunta ↗"}
          </button>
        </div>
      </form>
    </section>
  );
}
