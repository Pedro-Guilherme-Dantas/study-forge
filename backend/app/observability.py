"""Explicit traces with opt-in bounded content capture; never serialize graph state."""

import asyncio
from contextlib import contextmanager, suppress
from contextvars import ContextVar
from datetime import datetime, timezone
from functools import wraps
from uuid import uuid4

from langsmith import AsyncClient, tracing_context
from langsmith.utils import LangSmithAuthError, LangSmithRateLimitError

from app.errors import AppError

_active = ContextVar("studyforge_trace", default=None)
_parent = ContextVar("studyforge_span", default=None)
_content = ContextVar("studyforge_trace_content", default=None)
_SENSITIVE_FIELDS = {
    "api_key",
    "authorization",
    "cookie",
    "csrf_token",
    "database_url",
    "settings",
    "budget",
    "research_callback",
    "headers",
    "password",
    "access_token",
    "refresh_token",
}
_FIELDS = {
    "count",
    "library_count",
    "temporary_count",
    "citation_count",
    "status",
    "evidence_status",
    "research_authorized",
    "research_accepted",
    "error_count",
    "attempt",
    "query",
    "model",
    "dimensions",
    "input_count",
    "error_code",
    "input_tokens",
    "output_tokens",
    "total_tokens",
}


def capture_content(*, inputs=None, outputs=None):
    """Only explicitly supplied JSON-like values enter the trace, never function args/self."""
    state, record = _content.get(), _parent.get()
    if state is None or record is None:
        return

    def clean(value, depth=0):
        if state["remaining"] <= 0 or depth > 6:
            state["truncated"] = True
            return "[TRUNCATED]"
        if isinstance(value, str):
            for secret in state["secrets"]:
                value = value.replace(secret, "[REDACTED]")
            raw = value.encode("utf-8")
            cap = min(32768, state["remaining"])
            state["remaining"] -= min(len(raw), cap)
            if len(raw) > cap:
                state["truncated"] = True
                return raw[:cap].decode("utf-8", errors="ignore") + " [TRUNCATED]"
            return value
        if value is None or isinstance(value, (bool, int, float)):
            return value
        if isinstance(value, dict):
            result = {}
            for key, item in list(value.items())[:40]:
                if not isinstance(key, str):
                    continue
                key = key[:80]
                if key.lower().replace("-", "_") in _SENSITIVE_FIELDS:
                    result[key] = "[REDACTED]"
                else:
                    result[key] = clean(item, depth + 1)
            if len(value) > 40:
                state["truncated"] = True
            return result
        if isinstance(value, (list, tuple)):
            result = [clean(item, depth + 1) for item in value[:20]]
            if len(value) > 20:
                state["truncated"] = True
                result.append("[TRUNCATED]")
            return result
        return "[NOT_CAPTURED]"

    for name, value in (("inputs", inputs), ("outputs", outputs)):
        if isinstance(value, dict):
            captured = clean(value)
            if isinstance(captured, dict):
                record[name].update(captured)
            else:
                record[name]["content"] = captured
    if state["truncated"]:
        record.setdefault("extra", {}).setdefault("metadata", {})[
            "content_truncated"
        ] = True


def evidence_documents(results):
    if _content.get() is None:
        return []
    return [
        {
            "page_content": item.passage.text,
            "metadata": {
                "evidence_id": f"e{index + 1}",
                "title": item.passage.display_name,
                "scope": "temporary"
                if hasattr(item.passage, "source_id")
                else "library",
                "origin_url": item.passage.origin_url,
                "distance": item.distance,
                "locator": item.passage.locator.model_dump(mode="json"),
            },
        }
        for index, item in enumerate(results)
    ]


def annotate(**fields):
    record = _parent.get()
    if record is not None:
        record["outputs"].update(
            {
                key: value
                for key, value in fields.items()
                if key in _FIELDS and isinstance(value, (str, int, float, bool))
            }
        )
        if fields.get("status") == "failed" and fields.get("error_code"):
            record["error"] = fields["error_code"]


@contextmanager
def span(name, run_type="chain"):
    records = _active.get()
    if records is None or len(records) >= 64:
        yield
        return
    parent = _parent.get()
    identifier = uuid4()
    start = datetime.now(timezone.utc)
    order = start.strftime("%Y%m%dT%H%M%S%fZ") + str(identifier)
    record = {
        "id": identifier,
        "name": name,
        "run_type": run_type,
        "start_time": start,
        "inputs": {},
        "outputs": {},
        "parent_run_id": parent["id"] if parent else None,
        "trace_id": records[0]["id"] if records else identifier,
        "dotted_order": parent["dotted_order"] + "." + order if parent else order,
    }
    records.append(record)
    token = _parent.set(record)
    try:
        yield
    except BaseException as error:
        record["error"] = (
            error.code
            if isinstance(error, AppError)
            else "EXECUTION_INTERRUPTED"
            if isinstance(error, asyncio.CancelledError)
            else "EXECUTION_LIMIT"
            if isinstance(error, TimeoutError)
            else "STAGE_FAILED"
        )
        raise
    finally:
        record["end_time"] = datetime.now(timezone.utc)
        _parent.reset(token)


def observed(name, run_type="chain"):
    def decorate(function):
        @wraps(function)
        async def wrapped(*args, **kwargs):
            with span(name, run_type):
                return await function(*args, **kwargs)

        return wrapped

    return decorate


class Observability:
    def __init__(self, settings, client=None):
        self.settings = settings
        self.client = client
        self.queue = asyncio.Queue(maxsize=8)
        self.worker = None
        self.sent = self.failed = self.dropped = 0
        self.last_error_code = None

    async def start(self):
        if not self.settings.studyforge_tracing:
            return
        if self.client is None:
            self.client = AsyncClient(
                api_url=self.settings.langsmith_endpoint,
                api_key=self.settings.langsmith_api_key.get_secret_value(),
                workspace_id=self.settings.langsmith_workspace_id or None,
                timeout_ms=(2000, 2000, 2000, 2000),
                retry_config={"max_retries": 1},
                disable_prompt_cache=True,
            )
        self.worker = asyncio.create_task(self._export())

    @contextmanager
    def turn(self, turn_id, mode):
        # Suppress ambient LangChain instrumentation even if the host has tracing flags.
        with tracing_context(enabled=False):
            if not self.settings.studyforge_tracing:
                yield
                return
            records = []
            token = _active.set(records)
            parent_token = _parent.set(None)
            content_token = _content.set(
                {
                    "remaining": 262144,
                    "truncated": False,
                    "secrets": tuple(
                        secret.get_secret_value()
                        for secret in (
                            self.settings.gemini_api_key,
                            self.settings.search_api_key,
                            self.settings.langsmith_api_key,
                        )
                        if secret.get_secret_value()
                    ),
                }
                if self.settings.studyforge_trace_content
                else None
            )
            try:
                with span("studyforge.turn"):
                    records[0]["extra"] = {
                        "metadata": {
                            "turn_id": turn_id,
                            "app_mode": mode,
                            "capture": self.capture_mode,
                        }
                    }
                    records[0]["tags"] = ["studyforge", mode, self.capture_mode]
                    yield
            finally:
                _parent.reset(parent_token)
                _active.reset(token)
                _content.reset(content_token)
                try:
                    self.queue.put_nowait(records)
                except asyncio.QueueFull:
                    self.dropped += 1

    async def _export(self):
        while True:
            records = await self.queue.get()
            try:
                async with asyncio.timeout(10):
                    for record in records:
                        await self.client.create_run(
                            **record,
                            project_name=self.settings.langsmith_project,
                        )
                self.sent += 1
                self.last_error_code = None
            except Exception as error:
                # Never log the SDK exception: it can include headers or response bodies.
                self.failed += 1
                self.last_error_code = (
                    "EXPORT_TIMEOUT"
                    if isinstance(error, TimeoutError)
                    else "EXPORT_RATE_LIMITED"
                    if isinstance(error, LangSmithRateLimitError)
                    else "EXPORT_AUTH_FAILED"
                    if isinstance(error, LangSmithAuthError)
                    else "EXPORT_FAILED"
                )
            finally:
                self.queue.task_done()

    async def flush(self):
        await self.queue.join()

    async def close(self):
        if self.worker:
            self.worker.cancel()
            with suppress(asyncio.CancelledError):
                await self.worker
        while not self.queue.empty():
            self.queue.get_nowait()
            self.queue.task_done()
            self.dropped += 1
        if self.client:
            with suppress(Exception):
                await self.client.aclose()

    def status(self):
        return {
            "enabled": self.settings.studyforge_tracing,
            "capture": self.capture_mode,
            "sent": self.sent,
            "failed": self.failed,
            "dropped": self.dropped,
            "queued": self.queue.qsize(),
            "last_error_code": self.last_error_code,
        }

    @property
    def capture_mode(self):
        return (
            "content"
            if self.settings.studyforge_trace_content
            else "operational_metadata_only"
        )
