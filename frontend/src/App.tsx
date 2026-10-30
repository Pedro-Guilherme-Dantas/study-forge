import { useCallback, useEffect, useState } from "react";
import { getRuntime } from "./api";
import type { Runtime } from "./types";
import Library from "./pages/Library";
import Chat from "./pages/Chat";
import Sources from "./pages/Sources";
import Progress from "./pages/Progress";
import ErrorNotice from "./components/ErrorNotice";

type Page = "chat" | "library" | "progress" | "sources";
const pages: { id: Page; title: string; icon: string }[] = [
  { id: "chat", title: "Chat de estudos", icon: "◌" },
  { id: "library", title: "Biblioteca", icon: "▤" },
  { id: "progress", title: "Progresso", icon: "◷" },
  { id: "sources", title: "Fontes da pesquisa", icon: "⌕" },
];

export default function App() {
  const [page, setPage] = useState<Page>("library");
  const [runtime, setRuntime] = useState<Runtime | null>(null);
  const [error, setError] = useState("");
  const refresh = useCallback(() => {
    getRuntime()
      .then((value) => {
        setRuntime(value);
        setError("");
      })
      .catch(() =>
        setError(
          "O serviço local não respondeu. Verifique se a aplicação está em execução.",
        ),
      );
  }, []);
  useEffect(() => {
    refresh();
    const interval = window.setInterval(refresh, 10000);
    return () => window.clearInterval(interval);
  }, [refresh]);
  return (
    <div className="app-layout">
      <aside className="sidebar">
        <a
          className="brand"
          href="#"
          onClick={(event) => {
            event.preventDefault();
            setPage("library");
          }}
        >
          <span className="brand-mark">
            S<span>✦</span>
          </span>
          <span>
            StudyForge<small>SEU ESPAÇO DE ESTUDO</small>
          </span>
        </a>
        <div className="sidebar-label">SEU ESPAÇO</div>
        <nav aria-label="Navegação principal">
          {pages.map((item) => (
            <button
              key={item.id}
              className={page === item.id ? "active" : ""}
              aria-current={page === item.id ? "page" : undefined}
              onClick={() => setPage(item.id)}
            >
              <span>{item.icon}</span>
              {item.title}
              {page === item.id && <i />}
            </button>
          ))}
        </nav>
        <div className="sidebar-note">
          <span>✧</span>
          <h3>Aprender é construir.</h3>
          <p>
            Uma pergunta, uma fonte,
            <br />
            um entendimento de cada vez.
          </p>
        </div>
        <footer className="sidebar-footer">
          <span className="avatar">P</span>
          <span>
            Espaço pessoal<small>Somente neste computador</small>
          </span>
          <span className="local-dot" />
        </footer>
      </aside>
      <div className="workspace">
        <header className="topbar">
          <span>
            Meu espaço <span>/</span>{" "}
            <strong>{pages.find((item) => item.id === page)?.title}</strong>
          </span>
          <span className="local-label">● Ambiente local</span>
        </header>
        <main className="main-content">
          {error && <ErrorNotice message={error} />}
          <div className="environment-notice" role="status">
            <span>◈</span>
            <p>
              {runtime?.provider.disclosure ??
                "Verificando o ambiente local..."}
            </p>
            <span className="environment-tag">MVP EM CONSTRUÇÃO</span>
          </div>
          <div hidden={page !== "chat"}>
            <Chat />
          </div>
          {page === "chat" ? null : page === "sources" ? (
            <Sources fixture={runtime?.provider.backend === "fixture"} />
          ) : page === "progress" ? (
            <Progress />
          ) : (
            <Library maxBytes={runtime?.limits.max_upload_bytes} />
          )}
        </main>
        <footer className="workspace-footer">
          StudyForge <span>Aprendizado com origem, contexto e controle.</span>
        </footer>
      </div>
    </div>
  );
}
