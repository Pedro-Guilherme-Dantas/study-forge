import { useEffect, useState } from "react";
import { api } from "../api";
import type { Progress as Snapshot } from "../types";
import StatusBadge from "../components/StatusBadge";
import ErrorNotice from "../components/ErrorNotice";
const stages = {
  validate: "Validação",
  normalize: "Preparação do texto",
  chunk: "Divisão em trechos",
  embed: "Preparação da recuperação",
  publish: "Publicação",
};

export default function Progress() {
  const [snapshot, setSnapshot] = useState<Snapshot | null>(null);
  const [error, setError] = useState("");
  useEffect(() => {
    let active = true;
    const refresh = () => {
      api
        .progress()
        .then((value) => {
          if (active) {
            setSnapshot(value);
            setError("");
          }
        })
        .catch((error) => {
          if (active)
            setError(
              error instanceof Error
                ? error.message
                : "Progresso indisponível.",
            );
        });
    };
    refresh();
    const interval = window.setInterval(refresh, 1500);
    return () => {
      active = false;
      window.clearInterval(interval);
    };
  }, []);
  return (
    <section>
      <span className="eyebrow">ACOMPANHE O QUE ESTÁ ACONTECENDO</span>
      <h1>
        Progresso<span>.</span>
      </h1>
      <p>
        Estados de processamento dos materiais e das pesquisas. Sem notas ou
        medição de domínio do conteúdo.
      </p>
      {error && <ErrorNotice message={error} />}{" "}
      {!snapshot && !error && <p role="status">Consultando operações…</p>}
      {snapshot && (
        <>
          <h2>
            Ingestões recentes <small>(até 100)</small>
          </h2>
          {!snapshot.ingestions.length && (
            <p className="empty-state">Nenhuma ingestão iniciada.</p>
          )}
          {snapshot.ingestions.map((operation) => (
            <article className="operation-row" key={operation.operation_id}>
              <div>
                <strong>
                  {snapshot.materials.find(
                    (material) =>
                      material.material_id === operation.material_id,
                  )?.display_name ?? "Material da biblioteca"}
                </strong>
                <p className="muted">
                  Etapa: {stages[operation.stage]} · Tentativa{" "}
                  {operation.attempt}
                </p>
                {operation.error_code && (
                  <p>
                    O processamento não foi concluído. Abra o material na
                    biblioteca para consultar e tentar novamente.
                  </p>
                )}
              </div>
              <StatusBadge state={operation.state} />
            </article>
          ))}
          <h2>Pesquisas desta conversa</h2>
          {!snapshot.research.length && (
            <p className="empty-state">Nenhuma pesquisa nesta conversa.</p>
          )}
          {snapshot.research.map((research) => (
            <article className="operation-row" key={research.research_id}>
              <span>Pesquisa · {research.research_id.slice(0, 8)}</span>
              <StatusBadge state={research.status} />
            </article>
          ))}
        </>
      )}
    </section>
  );
}
