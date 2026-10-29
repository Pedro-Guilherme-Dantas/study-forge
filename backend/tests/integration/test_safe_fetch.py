import httpcore
import pytest
from app.web_fetch import SafeFetcher
from app.operations import Budget
from app.settings import Settings
from app.errors import AppError


async def test_mixed_dns_is_blocked_before_transport_creation():
    async def resolver(*args):
        return ["93.184.215.14", "::1"]

    def forbidden(**kwargs):
        pytest.fail("Blocked DNS must never reach pool")

    with pytest.raises(AppError) as failure:
        await SafeFetcher(Settings(), resolver, forbidden).fetch(
            "https://example.org", Budget(2)
        )
    assert failure.value.code == "DESTINATION_BLOCKED"


async def test_actual_httpcore_bytes_preserve_host_and_validate_redirect():
    backend = httpcore.AsyncMockBackend(
        [
            b"HTTP/1.1 302 Found\r\nLocation: http://127.0.0.1/\r\nContent-Length: 0\r\n\r\n"
        ]
    )
    hosts = []

    async def resolver(host, port):
        hosts.append(host)
        return ["93.184.215.14"] if host == "example.org" else ["127.0.0.1"]

    def pool(**kwargs):
        assert kwargs["network_backend"].host == "example.org"
        return httpcore.AsyncConnectionPool(network_backend=backend)

    with pytest.raises(AppError) as failure:
        await SafeFetcher(Settings(), resolver, pool).fetch(
            "http://example.org", Budget(2)
        )
    assert failure.value.code == "DESTINATION_BLOCKED"
    assert hosts == ["example.org", "127.0.0.1"]


async def test_html_stream_byte_limit_and_format():
    async def resolver(*args):
        return ["93.184.215.14"]

    def pool(**kwargs):
        return httpcore.AsyncConnectionPool(
            network_backend=httpcore.AsyncMockBackend(
                [
                    b"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: 20\r\n\r\n"
                    + b"x" * 20
                ]
            )
        )

    with pytest.raises(AppError) as failure:
        await SafeFetcher(Settings(max_html_bytes=10), resolver, pool).fetch(
            "http://example.org", Budget(2)
        )
    assert failure.value.status == 413


async def test_pinned_connection_preserves_sni_host_and_certificate_verification():
    import ssl
    from app.web_fetch import PinnedBackend

    seen = {}

    class Stream(httpcore.AsyncNetworkStream):
        def __init__(self):
            self.read_once = False

        async def read(self, max_bytes, timeout=None):
            if self.read_once:
                return b""
            self.read_once = True
            return b"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: 13\r\n\r\n<html></html>"

        async def write(self, buffer, timeout=None):
            seen.setdefault("request", b"")
            seen["request"] += buffer

        async def aclose(self):
            pass

        async def start_tls(self, ssl_context, server_hostname=None, timeout=None):
            seen["sni"] = server_hostname
            assert (
                ssl_context.verify_mode == ssl.CERT_REQUIRED
                and ssl_context.check_hostname
            )
            return self

        def get_extra_info(self, info):
            return None

    class Network:
        async def connect_tcp(self, host, port, *args):
            seen["ip"] = host
            return Stream()

    async def resolver(*args):
        return ["93.184.215.14"]

    def pool(**kwargs):
        pin = kwargs["network_backend"]
        return httpcore.AsyncConnectionPool(
            network_backend=PinnedBackend(pin.host, pin.address, Network())
        )

    page = await SafeFetcher(Settings(), resolver, pool).fetch(
        "https://example.org", Budget(2)
    )
    assert page.body == b"<html></html>"
    assert seen["ip"] == "93.184.215.14" and seen["sni"] == "example.org"
    assert b"Host: example.org\r\n" in seen["request"]
