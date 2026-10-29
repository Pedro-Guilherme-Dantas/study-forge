import secrets
from uuid import uuid4
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.errors import AppError
from app.diagnostics import event

_ALLOWED_HOSTS = {
    "127.0.0.1:8000",
    "localhost:8000",
    "127.0.0.1:5173",
    "localhost:5173",
    "127.0.0.1",
    "localhost",
    "[::1]:8000",
}
_ALLOWED_ORIGINS = {
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "http://127.0.0.1:5173",
    "http://localhost:5173",
    "http://[::1]:8000",
}
_SECURITY_HEADERS = {
    "cache-control": "no-store",
    "x-content-type-options": "nosniff",
    "referrer-policy": "no-referrer",
    "content-security-policy": "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'",
}


class LocalSecurity:
    def __init__(self, app, store, settings):
        self.app, self.store, self.settings = app, store, settings

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        request = Request(scope)
        request_id = str(uuid4())
        started = False

        async def secure_send(message):
            nonlocal started
            if message["type"] == "http.response.start":
                started = True
                headers = [
                    (k, v)
                    for k, v in message.get("headers", [])
                    if k.lower() not in {x.encode() for x in _SECURITY_HEADERS}
                ]
                headers.extend(
                    (k.encode(), v.encode()) for k, v in _SECURITY_HEADERS.items()
                )
                message["headers"] = headers
            await send(message)

        try:
            if request.headers.get("host", "").lower() not in _ALLOWED_HOSTS:
                raise AppError(
                    "ACCESS_DENIED", "Acesso permitido apenas por localhost.", 403
                )
            mutation = request.method not in ("GET", "HEAD", "OPTIONS")
            if mutation and request.headers.get("origin") not in _ALLOWED_ORIGINS:
                raise AppError("ACCESS_DENIED", "Origem não autorizada.", 403)
            path = scope["path"]
            if path.startswith("/api/") and path not in (
                "/api/runtime",
                "/api/sessions",
            ):
                session = self.store.get_session(request.cookies.get("sf_session"))
                scope.setdefault("state", {})["session"] = session
                if mutation and not secrets.compare_digest(
                    request.headers.get("x-csrf-token", ""), session.csrf
                ):
                    raise AppError("ACCESS_DENIED", "Token da sessão inválido.", 403)
            cap = (
                self.settings.max_upload_bytes
                if path == "/api/materials"
                else self.settings.max_message_bytes
            ) + 65536
            length = request.headers.get("content-length")
            if length and (not length.isdecimal() or int(length) > cap):
                raise AppError(
                    "PAYLOAD_TOO_LARGE", "O conteúdo excede o limite permitido.", 413
                )
            total = 0

            async def limited_receive():
                nonlocal total
                message = await receive()
                total += len(message.get("body", b""))
                if total > cap:
                    raise AppError(
                        "PAYLOAD_TOO_LARGE",
                        "O conteúdo excede o limite permitido.",
                        413,
                    )
                return message

            await self.app(scope, limited_receive, secure_send)
        except Exception as error:
            if started:
                return
            safe = (
                error
                if isinstance(error, AppError)
                else AppError(
                    "INTERNAL_ERROR",
                    "Não foi possível concluir a operação.",
                    500,
                    "request",
                )
            )
            event(
                request_id=request_id,
                stage=safe.stage,
                error_code=safe.code,
                status=safe.status,
            )
            await JSONResponse(safe.envelope(request_id), status_code=safe.status)(
                scope, receive, secure_send
            )
