"""HTML collector with DNS pinning. No cookies, proxies, credentials or second host lookup."""

import asyncio
import ipaddress
import socket
from urllib.parse import urlsplit, urlunsplit, urljoin
from dataclasses import dataclass
import httpcore
from app.errors import AppError


def parse_destination(url):
    try:
        parts = urlsplit(url)
        if (
            len(url) > 4096
            or parts.scheme not in ("http", "https")
            or not parts.hostname
            or parts.username is not None
            or parts.password is not None
            or "%" in parts.netloc
            or any(ord(char) <= 32 for char in url)
        ):
            raise ValueError()
        port = parts.port or (443 if parts.scheme == "https" else 80)
        if port not in (80, 443):
            raise ValueError()
        host = parts.hostname.encode("idna").decode("ascii").lower().rstrip(".")
        if (
            host == "localhost"
            or host.endswith((".localhost", ".local", ".internal"))
            or "." not in host
            and ":" not in host
        ):
            raise ValueError()
        normalized = urlunsplit(
            (parts.scheme, parts.netloc, parts.path or "/", parts.query, "")
        )
        return normalized, host, port
    except ValueError, UnicodeError:
        raise AppError(
            "DESTINATION_BLOCKED", "O endereço da fonte não é permitido.", 422, "fetch"
        ) from None


def public_ip(address):
    try:
        ip = ipaddress.ip_address(address)
        if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped:
            ip = ip.ipv4_mapped
        return ip.is_global and not ip.is_multicast and not ip.is_reserved
    except ValueError:
        return False


async def resolve_public(host, port):
    try:
        literal = ipaddress.ip_address(host)
        values = [str(literal)]
    except ValueError:
        records = await asyncio.get_running_loop().getaddrinfo(
            host, port, type=socket.SOCK_STREAM
        )
        values = list(dict.fromkeys(record[4][0] for record in records))
    if not values or not all(public_ip(value) for value in values):
        raise AppError(
            "DESTINATION_BLOCKED",
            "A fonte aponta para um destino interno ou reservado.",
            422,
            "fetch",
        )
    return values


class PinnedBackend(httpcore.AsyncNetworkBackend):
    def __init__(self, host, address, delegate=None):
        self.host, self.address = host, address
        self.delegate = delegate or httpcore.AnyIOBackend()

    async def connect_tcp(
        self, host, port, timeout=None, local_address=None, socket_options=None
    ):
        if host.rstrip(".").lower() != self.host or not public_ip(self.address):
            raise AppError(
                "DESTINATION_BLOCKED",
                "Destino de conexão não autorizado.",
                422,
                "fetch",
            )
        return await self.delegate.connect_tcp(
            self.address, port, timeout, local_address, socket_options
        )

    async def sleep(self, seconds):
        await asyncio.sleep(seconds)


@dataclass(frozen=True)
class HtmlPage:
    original_url: str
    effective_url: str
    body: bytes


class SafeFetcher:
    def __init__(
        self,
        settings,
        resolver=resolve_public,
        pool_factory=httpcore.AsyncConnectionPool,
    ):
        self.settings, self.resolver, self.pool_factory = (
            settings,
            resolver,
            pool_factory,
        )

    async def fetch(self, url, budget):
        original = url
        try:
            for hop in range(4):
                url, host, port = parse_destination(url)
                addresses = await budget.call(lambda: self.resolver(host, port))
                if not addresses or not all(public_ip(value) for value in addresses):
                    raise AppError(
                        "DESTINATION_BLOCKED",
                        "A fonte aponta para um destino proibido.",
                        422,
                        "fetch",
                    )
                # No implicit fallback: a failure is reported, never re-resolved by the transport.
                backend = PinnedBackend(host, addresses[0])
                budget.attempt()
                async with asyncio.timeout(min(10, budget.deadline - budget.clock())):
                    async with self.pool_factory(
                        network_backend=backend,
                        retries=0,
                        max_connections=1,
                        max_keepalive_connections=0,
                    ) as pool:
                        async with pool.stream(
                            "GET",
                            url,
                            headers={
                                "Accept": "text/html",
                                "Accept-Encoding": "identity",
                                "User-Agent": "StudyForge/0.1",
                            },
                            extensions={
                                "timeout": dict(connect=5, read=5, write=5, pool=5)
                            },
                        ) as response:
                            headers = {k.lower(): v for k, v in response.headers}
                            if response.status in (301, 302, 303, 307, 308):
                                if hop == 3 or b"location" not in headers:
                                    raise AppError(
                                        "SOURCE_UNAVAILABLE",
                                        "A fonte excedeu o limite de redirecionamentos.",
                                        502,
                                        "fetch",
                                    )
                                url = urljoin(
                                    url, headers[b"location"].decode("latin1")
                                )
                                continue
                            if response.status != 200:
                                raise AppError(
                                    "SOURCE_UNAVAILABLE",
                                    "Não foi possível obter esta página.",
                                    502,
                                    "fetch",
                                )
                            if (
                                headers.get(b"content-type", b"")
                                .split(b";")[0]
                                .strip()
                                .lower()
                                != b"text/html"
                            ):
                                raise AppError(
                                    "UNSUPPORTED_SOURCE",
                                    "A fonte não é uma página HTML.",
                                    422,
                                    "fetch",
                                )
                            if (
                                headers.get(b"content-encoding", b"identity").lower()
                                != b"identity"
                            ):
                                raise AppError(
                                    "UNSUPPORTED_ENCODING",
                                    "A fonte enviou uma compactação não aceita neste coletor.",
                                    422,
                                    "fetch",
                                )
                            body = bytearray()
                            async for piece in response.aiter_stream():
                                if (
                                    len(body) + len(piece)
                                    > self.settings.max_html_bytes
                                ):
                                    raise AppError(
                                        "PAYLOAD_TOO_LARGE",
                                        "A página excede o limite de coleta.",
                                        413,
                                        "fetch",
                                    )
                                body.extend(piece)
                            return HtmlPage(original, url, bytes(body))
        except AppError:
            raise
        except Exception:
            raise AppError(
                "SOURCE_UNAVAILABLE",
                "A fonte não respondeu dentro dos limites.",
                502,
                "fetch",
                True,
            ) from None
