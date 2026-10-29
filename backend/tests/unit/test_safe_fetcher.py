import gzip
import httpcore
import pytest
from app.web_fetch import SafeFetcher, PinnedBackend
from app.settings import Settings
from app.operations import Budget
from app.errors import AppError


async def test_compression_bomb_is_rejected_before_decompression(monkeypatch):
    bomb = gzip.compress(b"x" * 5_000_000)
    backend = httpcore.AsyncMockBackend(
        [
            b"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Encoding: gzip\r\nContent-Length: "
            + str(len(bomb)).encode()
            + b"\r\n\r\n"
            + bomb
        ]
    )

    async def resolver(*args):
        return ["93.184.215.14"]

    def pool(**kwargs):
        assert kwargs.get("proxy") is None
        return httpcore.AsyncConnectionPool(network_backend=backend)

    def forbidden(*args):
        pytest.fail("Collector must not decompress encoded bodies")

    monkeypatch.setattr(gzip, "decompress", forbidden)
    monkeypatch.setenv("HTTPS_PROXY", "http://127.0.0.1:9999")
    with pytest.raises(AppError) as failure:
        await SafeFetcher(Settings(), resolver, pool).fetch(
            "https://example.org", Budget(2)
        )
    assert failure.value.code == "UNSUPPORTED_ENCODING"


async def test_rebinding_cannot_change_the_destination_after_validation(monkeypatch):
    calls = []

    class Delegate:
        async def connect_tcp(self, host, *args):
            calls.append(host)
            return object()

    pin = PinnedBackend("example.org", "93.184.215.14", Delegate())

    async def forbidden(*args, **kwargs):
        pytest.fail("No second DNS lookup is permitted")

    import asyncio

    monkeypatch.setattr(asyncio.get_running_loop(), "getaddrinfo", forbidden)
    await pin.connect_tcp("example.org", 443)
    assert calls == ["93.184.215.14"]
