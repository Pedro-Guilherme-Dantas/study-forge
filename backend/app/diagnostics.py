import json
import logging

_ALLOWED = {"request_id", "stage", "error_code", "duration_ms", "status", "count"}
_logger = logging.getLogger("studyforge")


def event(**fields):
    safe = {key: value for key, value in fields.items() if key in _ALLOWED}
    _logger.info(json.dumps(safe, ensure_ascii=True))


def configure():
    for name in (
        "httpx",
        "httpcore",
        "httpx2",
        "google.genai",
        "langsmith",
        "sqlalchemy.engine",
    ):
        logging.getLogger(name).setLevel(logging.CRITICAL)
