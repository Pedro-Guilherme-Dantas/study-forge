export default function ErrorNotice({
  message,
  onDismiss,
}: {
  message: string;
  onDismiss?: () => void;
}) {
  return (
    <div className="error-notice" role="alert">
      <span>{message}</span>
      {onDismiss && (
        <button type="button" aria-label="Fechar aviso" onClick={onDismiss}>
          ×
        </button>
      )}
    </div>
  );
}
