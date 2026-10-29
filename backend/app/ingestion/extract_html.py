import hashlib
from importlib.metadata import version
import trafilatura
from app.errors import AppError


EXTRACTION_CONFIG = {
    "output_format": "markdown",
    "include_comments": False,
    "include_tables": True,
    "include_images": False,
    "include_links": False,
    "include_formatting": True,
    "deduplicate": False,
    "fast": True,
}


def extract_html(body):
    if (
        b"<!entity" in body.lower()
        or b"<!doctype" in body.lower()
        and b"system " in body.lower()
    ):
        raise AppError(
            "UNSUPPORTED_SOURCE",
            "A página contém declarações não permitidas.",
            422,
            "extract",
        )
    text = trafilatura.extract(body, **EXTRACTION_CONFIG)
    if not text or not text.strip():
        raise AppError(
            "EMPTY_SOURCE",
            "Não foi possível extrair conteúdo útil desta página.",
            422,
            "extract",
        )
    fingerprint = hashlib.sha256(
        (version("trafilatura") + repr(sorted(EXTRACTION_CONFIG.items()))).encode()
    ).hexdigest()
    return text, fingerprint
