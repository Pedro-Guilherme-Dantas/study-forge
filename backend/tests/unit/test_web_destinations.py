import pytest
from app.web_fetch import parse_destination, public_ip, PinnedBackend
from app.errors import AppError


@pytest.mark.parametrize(
    "url",
    [
        "file:///etc/passwd",
        "http://localhost/",
        "http://db/",
        "http://host.local/",
        "https://user:password@example.org/",
        "http://example.org:8000",
        "http://[::1%25eth0]/",
        "http://examp\nle.org",
    ],
)
def test_forbidden_url(url):
    with pytest.raises(AppError):
        parse_destination(url)


@pytest.mark.parametrize(
    "ip",
    [
        "127.0.0.1",
        "10.0.0.1",
        "169.254.169.254",
        "::1",
        "::ffff:127.0.0.1",
        "ff02::1",
        "192.0.2.1",
    ],
)
def test_private_or_reserved_ip(ip):
    assert not public_ip(ip)


async def test_pin_connects_to_approved_ip_and_never_resolves_original_host():
    class Delegate:
        async def connect_tcp(self, host, *args):
            assert host == "93.184.215.14"
            return "connected"

    backend = PinnedBackend("example.org", "93.184.215.14", Delegate())
    assert await backend.connect_tcp("example.org", 443) == "connected"
    with pytest.raises(AppError):
        await backend.connect_tcp("attacker.example", 443)
