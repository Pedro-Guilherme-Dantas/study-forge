import httpx
import pytest
from app.providers.gemini import call_provider
from app.operations import Budget


@pytest.mark.parametrize("kind", ["read_timeout", "remote_disconnect"])
async def test_transient_transport_errors_retry_at_most_once(kind, monkeypatch):
    calls = []
    failure = (
        httpx.ReadTimeout("synthetic")
        if kind == "read_timeout"
        else httpx.RemoteProtocolError("synthetic")
    )

    async def action():
        calls.append(1)
        raise failure

    async def wait(*args):
        pass

    monkeypatch.setattr("app.providers.gemini.asyncio.sleep", wait)
    with pytest.raises(type(failure)):
        await call_provider(Budget(5), action)
    assert len(calls) == 2
