import unicodedata
from app.errors import AppError
from app.settings import Settings


def validate_markdown(
    filename: str, body: bytes, settings: Settings
) -> tuple[str, str]:
    if len(body) > settings.max_upload_bytes:
        raise AppError(
            "PAYLOAD_TOO_LARGE",
            "O arquivo ultrapassa o limite de envio.",
            413,
            "validate",
        )
    name = unicodedata.normalize(
        "NFC", filename.replace("\\", "/").rsplit("/", 1)[-1]
    ).strip()
    if not name.lower().endswith(".md") or len(name) <= 3 or len(name) > 200:
        raise AppError(
            "INVALID_MARKDOWN", "Envie um arquivo com extensão .md.", 422, "validate"
        )
    try:
        value = body.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        raise AppError(
            "INVALID_MARKDOWN",
            "O arquivo deve ser texto UTF-8 legível.",
            422,
            "validate",
        ) from None
    if not value.strip("\ufeff \t\r\n") or any(
        ord(c) < 32 and c not in "\r\n\t" for c in value
    ):
        raise AppError(
            "INVALID_MARKDOWN",
            "O arquivo está vazio ou contém dados binários.",
            422,
            "validate",
        )
    return name, value
