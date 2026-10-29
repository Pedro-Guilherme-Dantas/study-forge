import asyncio
import time
from collections.abc import Awaitable, Callable
from app.errors import AppError


class Budget:
    def __init__(self, seconds, steps=8, attempts=20, clock=time.monotonic):
        self.clock = clock
        self.deadline = clock() + seconds
        self.steps, self.attempts = steps, attempts

    def check(self):
        if self.clock() >= self.deadline:
            raise AppError(
                "EXECUTION_LIMIT", "O prazo da operação foi atingido.", 429, "execution"
            )

    def step(self):
        self.check()
        if self.steps <= 0:
            raise AppError(
                "EXECUTION_LIMIT", "Limite de etapas atingido.", 429, "execution"
            )
        self.steps -= 1

    def attempt(self):
        self.check()
        if self.attempts <= 0:
            raise AppError(
                "EXECUTION_LIMIT", "Limite de chamadas atingido.", 429, "execution"
            )
        self.attempts -= 1

    async def call(self, callback):
        self.attempt()
        try:
            async with asyncio.timeout(self.deadline - self.clock()):
                return await callback()
        except TimeoutError:
            raise AppError(
                "EXECUTION_LIMIT",
                "A operação foi interrompida pelo prazo.",
                429,
                "execution",
            ) from None


class Executor:
    """Bounded in-process tasks. The database owns durable ingestion states."""

    def __init__(self, workers=1, capacity=6):
        self.semaphore = asyncio.Semaphore(workers)
        self.capacity = capacity
        self.pending = 0
        self.tasks: set[asyncio.Task] = set()

    def ensure_capacity(self):
        if self.pending >= self.capacity:
            raise AppError(
                "EXECUTION_LIMIT",
                "Há operações demais. Aguarde e tente novamente.",
                429,
            )

    def reserve(self):
        self.ensure_capacity()
        self.pending += 1
        return Reservation(self)

    def submit(self, callback: Callable[[], Awaitable], reservation=None):
        ticket = reservation or self.reserve()
        if ticket.executor is not self or ticket.used:
            raise RuntimeError("Invalid executor reservation")

        async def run():
            try:
                async with self.semaphore:
                    await callback()
            except asyncio.CancelledError:
                raise
            except Exception:
                # Services persist sanitized status; never log exceptions with payloads.
                pass

        coroutine = run()
        try:
            task = asyncio.create_task(coroutine)
        except BaseException:
            coroutine.close()
            ticket.release()
            raise
        ticket.used = True
        self.tasks.add(task)

        def finished(completed):
            # A task cancelled before its first await never enters run's finally block.
            self.tasks.discard(completed)
            self.pending -= 1

        task.add_done_callback(finished)
        return task

    async def drain(self):
        if self.tasks:
            await asyncio.gather(*list(self.tasks), return_exceptions=True)

    async def shutdown(self):
        for task in list(self.tasks):
            task.cancel()
        await self.drain()


class Reservation:
    def __init__(self, executor):
        self.executor, self.used = executor, False

    def release(self):
        if not self.used:
            self.used = True
            self.executor.pending -= 1
