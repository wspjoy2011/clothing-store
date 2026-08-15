import asyncio

import pytest

from security.exceptions import EmptyPasswordError
from security.passwords import PasswordManager

PASSWORD = "E2ePassword123!"


async def count_ticks_during(work) -> int:
    """
    Count how many times the event loop ran while the work was in progress

    Args:
        work: Coroutine to run

    Returns:
        Number of loop iterations observed
    """
    ticks = 0

    async def tick() -> None:
        nonlocal ticks
        while True:
            await asyncio.sleep(0.005)
            ticks += 1

    ticker = asyncio.create_task(tick())
    try:
        await work
    finally:
        ticker.cancel()

    return ticks


async def test_hashing_leaves_the_event_loop_free():
    """Hashing runs off the loop, so other tasks keep being served"""
    manager = PasswordManager()

    ticks = await count_ticks_during(manager.hash_password(PASSWORD))

    assert ticks > 0


async def test_verification_leaves_the_event_loop_free():
    """Verification runs off the loop, so other tasks keep being served"""
    manager = PasswordManager()
    hashed = await manager.hash_password(PASSWORD)

    ticks = await count_ticks_during(manager.verify_password(PASSWORD, hashed))

    assert ticks > 0


async def test_concurrent_hashing_overlaps():
    """Several hashes run at once instead of queueing behind one another"""
    manager = PasswordManager()

    started = asyncio.get_running_loop().time()
    await manager.hash_password(PASSWORD)
    single = asyncio.get_running_loop().time() - started

    started = asyncio.get_running_loop().time()
    await asyncio.gather(*(manager.hash_password(f"{PASSWORD}{index}") for index in range(4)))
    batch = asyncio.get_running_loop().time() - started

    assert batch < single * 4


async def test_hash_and_verify_round_trip():
    """A hashed password verifies against its own hash and rejects another"""
    manager = PasswordManager()

    hashed = await manager.hash_password(PASSWORD)

    assert await manager.verify_password(PASSWORD, hashed) is True
    assert await manager.verify_password("WrongPassword1!", hashed) is False


async def test_empty_password_is_rejected():
    """An empty password never reaches the hashing backend"""
    manager = PasswordManager()

    with pytest.raises(EmptyPasswordError):
        await manager.hash_password("")
