import { useState } from "react";
import type { Citation as Reference } from "../types";
import { api } from "../api";
import MarkdownView from "./MarkdownView";
import ErrorNotice from "./ErrorNotice";

export default function Citation({
  citation,
  conversation,
}: {
  citation: Reference;
  conversation: string;
}) {
  const [open, setOpen] = useState(false);
  const [value, setValue] = useState<Reference | null>(null);
  const [error, setError] = useState("");
  async function inspect() {
    if (open) {
      setOpen(false);
      return;
    }
    try {
      setValue(await api.citation(conversation, citation.citation_id));
      setOpen(true);
    } catch (error) {
      setError(
        error instanceof Error ? error.message : "Referência indisponível.",
      );
    }
  }
  return (
    <div className="citation">
      <button
        className="secondary-button"
        aria-expanded={open}
        onClick={() => void inspect()}
      >
        ↗ {citation.title} ·{" "}
        {citation.scope === "library" ? "Biblioteca" : "Temporária"}
      </button>
      {error && <ErrorNotice message={error} />}{" "}
      {open && value && (
        <blockquote>
          <p className="chunk-label">
            LINHAS {value.locator.start_line}–{value.locator.end_line} ·{" "}
            {value.locator.section_path.join(" / ")}
          </p>
          <MarkdownView text={value.quote} />
        </blockquote>
      )}
    </div>
  );
}
