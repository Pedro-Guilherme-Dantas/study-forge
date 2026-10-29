import asyncio
import secrets
from dataclasses import dataclass, field
from uuid import uuid4
from app.errors import AppError


@dataclass
class Conversation:
    id: str = field(default_factory=lambda: str(uuid4()))
    epoch: int = 0
    closed: bool = False
    messages: list = field(default_factory=list)
    sources: dict = field(default_factory=dict)
    turns: dict = field(default_factory=dict)
    offers: dict = field(default_factory=dict)
    research: dict = field(default_factory=dict)
    citations: dict = field(default_factory=dict)
    tasks: set[asyncio.Task] = field(default_factory=set)
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)

    def apply(self, epoch, callback):
        if self.closed or self.epoch != epoch:
            return False
        callback()
        return True


@dataclass
class Session:
    id: str = field(default_factory=lambda: str(uuid4()))
    csrf: str = field(default_factory=lambda: secrets.token_urlsafe(32))
    conversation: Conversation | None = None


class SessionStore:
    def __init__(self):
        self.instance_id = str(uuid4())
        self._sessions: dict[str, Session] = {}

    def create_session(self):
        if len(self._sessions) >= 128:
            raise AppError("EXECUTION_LIMIT", "Limite de sessões locais atingido.", 429)
        session = Session()
        self._sessions[session.id] = session
        return session

    def get_session(self, session_id):
        session = self._sessions.get(str(session_id))
        if session is None:
            raise AppError(
                "SESSION_EXPIRED", "A sessão expirou. Abra uma nova sessão.", 410
            )
        return session

    def create_conversation(self, session):
        if session.conversation is None or session.conversation.closed:
            session.conversation = Conversation()
        return session.conversation

    def get_conversation(self, session, conversation_id):
        conversation = session.conversation
        if (
            conversation is None
            or conversation.closed
            or conversation.id != str(conversation_id)
        ):
            raise AppError("CONVERSATION_CLOSED", "Esta conversa foi encerrada.", 410)
        return conversation

    async def close(self, session, conversation_id):
        conversation = session.conversation
        if conversation is None or conversation.id != str(conversation_id):
            return
        async with conversation.lock:
            conversation.closed = True
            conversation.epoch += 1
            tasks = list(conversation.tasks)
            for task in tasks:
                task.cancel()
            for name in (
                "messages",
                "sources",
                "turns",
                "offers",
                "research",
                "citations",
            ):
                getattr(conversation, name).clear()
            conversation.tasks.clear()
            session.conversation = None
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def shutdown(self):
        for session in list(self._sessions.values()):
            if session.conversation:
                await self.close(session, session.conversation.id)
        self._sessions.clear()
