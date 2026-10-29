import asyncio
import pytest
from app.errors import AppError
from app.operations import Budget, Executor
from tests.fakes import Clock


@pytest.mark.unit
def test_every_attempt_and_step_counts():
    clock = Clock()
    budget = Budget(10, steps=1, attempts=2, clock=clock)
    budget.step()
    budget.attempt()
    budget.attempt()
    with pytest.raises(AppError):
        budget.attempt()
    with pytest.raises(AppError):
        budget.step()
    clock.advance(11)
    with pytest.raises(AppError):
        budget.check()


@pytest.mark.unit
async def test_admission_is_bounded_and_released_after_error():
    executor = Executor(1, 1)
    finish = asyncio.Event()
    started = asyncio.Event()

    async def work():
        started.set()
        await finish.wait()

    executor.submit(work)
    await started.wait()
    with pytest.raises(AppError):
        executor.submit(work)
    finish.set()
    await executor.drain()

    async def fail():
        raise RuntimeError("sensitive")

    executor.submit(fail)
    await executor.drain()
    assert executor.pending == 0


@pytest.mark.unit
async def test_cancelling_before_first_instruction_releases_capacity():
    executor = Executor(1, 1)

    async def never_called():
        pytest.fail("Cancelled task must not start")

    task = executor.submit(never_called)
    task.cancel()
    await executor.drain()
    assert executor.pending == 0
    reservation = executor.reserve()
    reservation.release()
