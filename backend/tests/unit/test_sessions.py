import asyncio
import pytest
from app.errors import AppError
from app.sessions import SessionStore


@pytest.mark.unit
async def test_close_discards_all_and_prevents_late_callback():
    store = SessionStore()
    session = store.create_session()
    conversation = store.create_conversation(session)
    conversation.messages.append({"content": "PRIVATE_MARKER"})
    conversation.sources["source"] = {"text": "PRIVATE_MARKER"}
    epoch = conversation.epoch
    await store.close(session, conversation.id)
    assert conversation.messages == [] and conversation.sources == {}
    assert not conversation.apply(epoch, lambda: conversation.messages.append("late"))
    with pytest.raises(AppError) as error:
        store.get_conversation(session, conversation.id)
    assert error.value.status == 410
    replacement = store.create_conversation(session)
    assert replacement.id != conversation.id and replacement.messages == []


@pytest.mark.unit
async def test_sessions_and_restarts_are_isolated():
    store = SessionStore()
    first, other = store.create_session(), store.create_session()
    conversation = store.create_conversation(first)
    with pytest.raises(AppError):
        store.get_conversation(other, conversation.id)
    with pytest.raises(AppError):
        SessionStore().get_session(first.id)


@pytest.mark.unit
async def test_tasks_cancelled_and_lock_serializes_close():
    store = SessionStore()
    session = store.create_session()
    conversation = store.create_conversation(session)
    task = asyncio.create_task(asyncio.sleep(60))
    conversation.tasks.add(task)
    await store.close(session, conversation.id)
    assert task.cancelled()
