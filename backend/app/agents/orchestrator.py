"""Owns turn lifecycle; the model has no persistence or search authority."""

import asyncio
import re
from uuid import UUID, uuid4
from app.operations import Budget
from app.errors import AppError
from app.schemas import (
    TurnResult,
    ResearchOffer,
    ErrorEnvelope,
    ResearchResult,
    OfferDecision,
    TurnRequest,
)


class Orchestrator:
    def __init__(self, settings, graph, executor, researcher=None):
        self.settings, self.graph, self.executor = settings, graph, executor
        self.researcher = researcher

    @staticmethod
    def explicit_research(message):
        return bool(
            re.search(
                r"^\s*(?:(?:por favor|pode|poderia|quero que você|gostaria que você)\s*[,.:]?\s*)?"
                r"(?:pesquis[ea]|pesquisar|busque|buscar|procure|procurar|search|look up)\b"
                r"(?![^.!?]*\b(?:não|nunca|not|never)\b)[^.!?]{0,200}\b(web|internet|online|fontes|páginas)\b",
                message,
                re.I,
            )
        )

    async def start(self, conversation, request):
        if len(request.message.encode()) > self.settings.max_message_bytes:
            raise AppError(
                "PAYLOAD_TOO_LARGE", "A pergunta excede o limite permitido.", 413
            )
        if not request.message.strip():
            raise AppError("INVALID_REQUEST", "Escreva uma pergunta.", 422)
        async with conversation.lock:
            if conversation.closed:
                raise AppError(
                    "CONVERSATION_CLOSED", "Esta conversa foi encerrada.", 410
                )
            if any(
                result.status == "running" for result in conversation.turns.values()
            ):
                raise AppError(
                    "OPERATION_BUSY",
                    "Aguarde a resposta atual antes de enviar outra pergunta.",
                    409,
                )
            if len(conversation.turns) >= 32:
                raise AppError(
                    "EXECUTION_LIMIT",
                    "Esta conversa atingiu o limite local. Encerre para iniciar outra.",
                    429,
                )
            turn_id, epoch = str(uuid4()), conversation.epoch
            ticket = self.executor.reserve()
            conversation.turns[turn_id] = TurnResult(turn_id=turn_id, status="running")
            if request.intent == "research" or self.explicit_research(request.message):
                research_id = str(uuid4())
                conversation.turns[turn_id].research_id = UUID(research_id)
                conversation.research[research_id] = ResearchResult(
                    research_id=research_id, status="running"
                )
            conversation.messages.append({"role": "user", "text": request.message})
            try:
                task = self.executor.submit(
                    lambda: self.run(conversation, epoch, turn_id, request), ticket
                )
            except BaseException:
                conversation.turns.pop(turn_id, None)
                conversation.messages.pop()
                ticket.release()
                raise
            conversation.tasks.add(task)
            task.add_done_callback(conversation.tasks.discard)
        return turn_id

    async def run(
        self, conversation, epoch, turn_id, request, authorized_research=False
    ):
        try:
            async with asyncio.timeout(self.settings.turn_timeout):
                budget = Budget(
                    self.settings.turn_timeout,
                    self.settings.max_graph_steps,
                    self.settings.max_external_attempts,
                )
                researched = (
                    authorized_research
                    or request.intent == "research"
                    or self.explicit_research(request.message)
                )

                async def perform_research():
                    research_id = await self.research(
                        conversation,
                        epoch,
                        request.message,
                        budget,
                        str(conversation.turns[turn_id].research_id),
                    )
                    return {
                        "research_id": research_id,
                        "temporary": list(conversation.sources.values()),
                    }

                result = await self.graph.ainvoke(
                    {
                        "question": request.message,
                        "budget": budget,
                        "temporary": list(conversation.sources.values()),
                        "authorized_research": researched,
                        "research_callback": perform_research if researched else None,
                    },
                    config={
                        "recursion_limit": self.settings.max_graph_steps,
                        "callbacks": [],
                    },
                )
                budget.check()
                research_id = result.get("research_id")
                output, evidence = result["output"], result["evidence"]
                citations = evidence.resolve(output.citation_ids, turn_id)
                status = {
                    "supported": "complete",
                    "partial": "partial",
                    "insufficient": "insufficient",
                    "conflicting": "partial",
                }[output.evidence_status]
                offer = None
                if not researched and output.evidence_status in (
                    "partial",
                    "insufficient",
                ):
                    offer = ResearchOffer(
                        offer_id=uuid4(), turn_id=turn_id, topic=request.message
                    )
                    status = "awaiting_research_consent"
                final = TurnResult(
                    turn_id=turn_id,
                    status=status,
                    answer_markdown=output.answer_markdown,
                    evidence_status=output.evidence_status,
                    citations=citations,
                    research_offer=offer,
                    research_id=research_id,
                )
                async with conversation.lock:
                    if conversation.closed or conversation.epoch != epoch:
                        return
                    conversation.turns[turn_id] = final
                    conversation.messages.append(
                        {"role": "assistant", "text": output.answer_markdown}
                    )
                    conversation.citations.update({c.citation_id: c for c in citations})
                    if offer:
                        conversation.offers[str(offer.offer_id)] = offer
        except asyncio.CancelledError:
            raise
        except Exception as error:
            safe = (
                error
                if isinstance(error, AppError)
                else AppError(
                    "EXECUTION_LIMIT"
                    if isinstance(error, TimeoutError)
                    else "TURN_FAILED",
                    "Não foi possível concluir esta resposta. Tente novamente.",
                    503,
                    "tutor",
                )
            )
            previous = conversation.turns.get(turn_id)
            final = TurnResult(
                turn_id=turn_id,
                status="failed",
                research_id=previous.research_id if previous else None,
                error=ErrorEnvelope.model_validate(safe.envelope()),
            )
            async with conversation.lock:
                if (
                    conversation.apply(
                        epoch, lambda: conversation.turns.__setitem__(turn_id, final)
                    )
                    and final.research_id
                ):
                    research = conversation.research.get(str(final.research_id))
                    if research and research.status == "running":
                        conversation.research[str(final.research_id)] = ResearchResult(
                            research_id=final.research_id,
                            status="failed",
                            error_codes=[safe.code],
                        )

    async def research(self, conversation, epoch, topic, budget, research_id):
        async with conversation.lock:
            if conversation.closed or conversation.epoch != epoch:
                raise AppError(
                    "CONVERSATION_CLOSED", "Esta conversa foi encerrada.", 410
                )
            if (
                len(conversation.research) >= 32
                or len(conversation.sources) + self.settings.max_pages_per_research
                > self.settings.max_temporary_sources
            ):
                raise AppError(
                    "EXECUTION_LIMIT",
                    "A conversa atingiu o limite de pesquisas ou fontes temporárias.",
                    429,
                )
            conversation.research[research_id] = ResearchResult(
                research_id=research_id, status="running"
            )
        try:
            turn_deadline = budget.deadline
            # Budget.call expires before the outer cancellation, allowing the collector
            # to return already-completed sources with explicit partial failures.
            budget.deadline = min(turn_deadline, budget.clock() + 43)
            try:
                async with asyncio.timeout(min(45, turn_deadline - budget.clock())):
                    snapshots, unavailable, errors = await self.researcher.collect(
                        topic, budget
                    )
            finally:
                budget.deadline = turn_deadline
            async with conversation.lock:
                if conversation.closed or conversation.epoch != epoch:
                    raise AppError(
                        "CONVERSATION_CLOSED", "Esta conversa foi encerrada.", 410
                    )
                byte_count = sum(
                    len(s.text.encode())
                    for s in [*conversation.sources.values(), *snapshots]
                )
                if byte_count > self.settings.max_temporary_bytes:
                    raise AppError(
                        "EXECUTION_LIMIT",
                        "A conversa atingiu o limite de conteúdo temporário.",
                        429,
                    )
                conversation.sources.update(
                    {str(s.summary.source_id): s for s in snapshots}
                )
                status = (
                    "partial"
                    if snapshots and errors
                    else "succeeded"
                    if snapshots
                    else "failed"
                    if errors
                    else "empty"
                )
                conversation.research[research_id] = ResearchResult(
                    research_id=research_id,
                    status=status,
                    sources=[s.summary for s in snapshots] + unavailable,
                    error_codes=errors,
                )
            return research_id
        except BaseException as error:
            code = (
                error.code
                if isinstance(error, AppError)
                else "EXECUTION_INTERRUPTED"
                if isinstance(error, asyncio.CancelledError)
                else "RESEARCH_FAILED"
            )
            async with conversation.lock:
                conversation.apply(
                    epoch,
                    lambda: conversation.research.__setitem__(
                        research_id,
                        ResearchResult(
                            research_id=research_id, status="failed", error_codes=[code]
                        ),
                    ),
                )
            raise

    async def decide(self, conversation, offer_id, accept):
        async with conversation.lock:
            offer = conversation.offers.get(str(offer_id))
            if not offer:
                raise AppError(
                    "NOT_FOUND", "Oferta não encontrada nesta conversa.", 404
                )
            if offer.state != "awaiting":
                turn = conversation.turns[str(offer.turn_id)]
                if (offer.state == "accepted") != accept:
                    raise AppError(
                        "OPERATION_BUSY", "Esta oferta já recebeu outra decisão.", 409
                    )
                return OfferDecision(
                    offer_id=offer_id, state=offer.state, research_id=turn.research_id
                )
            turn = conversation.turns[str(offer.turn_id)]
            if not accept:
                offer.state = "declined"
                turn.status = "partial" if turn.citations else "insufficient"
                turn.research_offer = None
                return OfferDecision(offer_id=offer_id, state="declined")
            if any(value.status == "running" for value in conversation.turns.values()):
                raise AppError("OPERATION_BUSY", "Aguarde a operação atual.", 409)
            ticket = self.executor.reserve()
            epoch = conversation.epoch
            task = self.executor.submit(
                lambda: self.run(
                    conversation,
                    epoch,
                    str(offer.turn_id),
                    TurnRequest(message=offer.topic),
                    True,
                ),
                ticket,
            )
            offer.state = "accepted"
            turn.status = "running"
            turn.research_id = uuid4()
            conversation.research[str(turn.research_id)] = ResearchResult(
                research_id=turn.research_id, status="running"
            )
            turn.research_offer = None
            conversation.tasks.add(task)
            task.add_done_callback(conversation.tasks.discard)
            return OfferDecision(
                offer_id=offer_id, state="accepted", research_id=turn.research_id
            )
