const names: Record<string, string> = {
  processing: "Processando",
  ready: "Disponível",
  queued: "Aguardando",
  running: "Em andamento",
  succeeded: "Concluído",
  failed: "Falhou",
  interrupted: "Interrompido",
  partial: "Resultado parcial",
  empty: "Sem fontes utilizáveis",
};
export default function StatusBadge({ state }: { state: string }) {
  return (
    <span className={"status status-" + state}>{names[state] ?? state}</span>
  );
}
