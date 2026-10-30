import { useCallback, useEffect, useRef, useState } from "react";
import { api } from "../api";
import type { Material, Operation } from "../types";
import StatusBadge from "../components/StatusBadge";
import ErrorNotice from "../components/ErrorNotice";
import MaterialDetail from "../components/MaterialDetail";

export default function Library({ maxBytes = 1048576 }: { maxBytes?: number }) {
  const [materials, setMaterials] = useState<Material[]>([]);
  const [cursor, setCursor] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState<string | null>(null);
  const [operation, setOperation] = useState<Operation | null>(null);
  const input = useRef<HTMLInputElement>(null);
  const refresh = useCallback(async () => {
    const page = await api.materials();
    setMaterials(page.items);
    setCursor(page.next_cursor);
    setLoading(false);
  }, []);
  const closeDetail = useCallback(() => setSelected(null), []);
  async function loadMore() {
    if (!cursor) return;
    try {
      const page = await api.materials(cursor);
      setMaterials((values) => [
        ...new Map(
          [...values, ...page.items].map((item) => [item.material_id, item]),
        ).values(),
      ]);
      setCursor(page.next_cursor);
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : "Não foi possível carregar outros materiais.",
      );
    }
  }
  useEffect(() => {
    refresh().catch(() => {
      setError(
        "Não foi possível abrir a biblioteca. Verifique o serviço local.",
      );
      setLoading(false);
    });
  }, [refresh]);
  const pending =
    materials.some((m) => m.status === "processing") ||
    (!!operation && ["queued", "running"].includes(operation.state));
  useEffect(() => {
    if (!pending) return;
    let disposed = false;
    const timer = window.setInterval(async () => {
      try {
        if (operation) {
          const result = await api.operation(operation.operation_id);
          if (!disposed) setOperation(result);
        }
        if (!disposed) await refresh();
      } catch {
        if (!disposed)
          setError(
            "Não foi possível atualizar o processamento. Tente novamente.",
          );
      }
    }, 1500);
    return () => {
      disposed = true;
      window.clearInterval(timer);
    };
  }, [pending, operation, refresh]);
  async function upload(file?: File) {
    if (!file) return;
    if (!file.name.toLowerCase().endsWith(".md")) {
      setError("Envie somente arquivos Markdown (.md).");
      return;
    }
    if (file.size > maxBytes) {
      setError("O arquivo excede o limite de envio deste ambiente.");
      return;
    }
    setUploading(true);
    setError("");
    try {
      setOperation(await api.upload(file));
      await refresh();
    } catch (error) {
      setError(error instanceof Error ? error.message : "O envio falhou.");
    } finally {
      setUploading(false);
      if (input.current) input.current.value = "";
    }
  }
  const ready = materials.filter((m) => m.status === "ready").length;
  const filtered = materials.filter((m) =>
    m.display_name
      .toLocaleLowerCase("pt-BR")
      .includes(search.toLocaleLowerCase("pt-BR")),
  );
  return (
    <>
      <header className="page-heading">
        <div>
          <div className="eyebrow">SEUS MATERIAIS, SUAS FONTES</div>
          <h1>
            Biblioteca<span>.</span>
          </h1>
          <p>Transforme seus materiais em pontos de partida para aprender.</p>
        </div>
        <label className={"primary-button " + (uploading ? "disabled" : "")}>
          ＋ Adicionar material
          <input
            ref={input}
            type="file"
            accept=".md,text/markdown"
            disabled={uploading}
            onChange={(event) => void upload(event.target.files?.[0])}
          />
        </label>
      </header>
      {error && <ErrorNotice message={error} onDismiss={() => setError("")} />}
      <section className="summary-grid" aria-label="Resumo da biblioteca">
        <div>
          <span className="summary-icon">▤</span>
          <strong>{materials.length}</strong>
          <span>materiais carregados</span>
        </div>
        <div>
          <span className="summary-icon green">✓</span>
          <strong>{ready}</strong>
          <span>disponíveis para estudo</span>
        </div>
        <div>
          <span className="summary-icon amber">◷</span>
          <strong>
            {materials.filter((m) => m.status === "processing").length}
          </strong>
          <span>em processamento</span>
        </div>
      </section>
      <section className="library-panel">
        <div className="panel-toolbar">
          <h2>
            Seus materiais <span className="count">{materials.length}</span>
          </h2>
          <label className="search-box">
            <span>⌕</span>
            <input
              aria-label="Encontrar material pelo nome"
              placeholder="Encontrar um material..."
              value={search}
              onChange={(event) => setSearch(event.target.value)}
            />
          </label>
        </div>
        {operation && (
          <div className="operation-notice" role="status">
            <StatusBadge state={operation.state} />
            <span>
              {operation.state === "succeeded"
                ? "Seu material está disponível na biblioteca."
                : operation.state === "failed" ||
                    operation.state === "interrupted"
                  ? "O material não ficou disponível. Abra os detalhes para verificar e tentar novamente."
                  : "Preparando trechos e verificando o material..."}
            </span>
          </div>
        )}
        {loading ? (
          <div className="empty-state" role="status">
            Carregando seus materiais...
          </div>
        ) : filtered.length ? (
          <div className="material-list">
            {filtered.map((material) => (
              <button
                key={material.material_id}
                className="material-row"
                onClick={() => setSelected(material.material_id)}
              >
                <span className="file-icon">M↓</span>
                <span className="material-name">
                  <strong>{material.display_name}</strong>
                  <small>
                    {material.source_kind === "markdown_upload"
                      ? "Markdown · material enviado por você"
                      : "Web · fonte selecionada por você"}
                  </small>
                </span>
                <StatusBadge state={material.status} />
                <span className="row-arrow">↗</span>
              </button>
            ))}
          </div>
        ) : (
          <div className="empty-state">
            <div className="empty-symbol">▤</div>
            <h3>
              {search
                ? "Nenhum material com esse nome"
                : "Uma biblioteca começa com uma ideia."}
            </h3>
            <p>
              {search
                ? "Tente outro nome para encontrar seu material."
                : "Envie seu primeiro arquivo Markdown. Você poderá acompanhar o processamento e consultar cada trecho com sua origem."}
            </p>
            {!search && (
              <button
                className="secondary-button"
                onClick={() => input.current?.click()}
              >
                Escolher um arquivo .md
              </button>
            )}
          </div>
        )}
        {cursor && (
          <button className="secondary-button" onClick={() => void loadMore()}>
            Carregar mais materiais
          </button>
        )}
      </section>
      <div className="library-footnote">
        <span>◇</span>
        <p>
          <strong>O conhecimento permanece sob seu controle.</strong>
          <br />
          Fontes da web só entram na biblioteca quando você decide guardá-las.
        </p>
        <span className="file-type">.md</span>
      </div>
      {selected && (
        <MaterialDetail
          id={selected}
          onClose={closeDetail}
          onChanged={refresh}
        />
      )}
    </>
  );
}
