import asyncio

import pytest

from security.exceptions import EmptyPasswordError, InvalidPasswordHashError
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


async def test_concurrent_hashing_keeps_serving_other_tasks():
    """Several hashes at once still leave room for the rest of the loop"""
    manager = PasswordManager()

    ticks = await count_ticks_during(
        asyncio.gather(*(manager.hash_password(f"{PASSWORD}{index}") for index in range(4)))
    )

    assert ticks > 0


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


async def test_verification_rejects_empty_arguments():
    """Verification refuses an empty password or an empty hash"""
    manager = PasswordManager()
    hashed = await manager.hash_password(PASSWORD)

    with pytest.raises(EmptyPasswordError):
        await manager.verify_password("", hashed)

    with pytest.raises(EmptyPasswordError):
        await manager.verify_password(PASSWORD, "")


async def test_fresh_hash_needs_no_update():
    """A hash produced by the current settings is not scheduled for rehashing"""
    manager = PasswordManager()

    hashed = await manager.hash_password(PASSWORD)

    assert manager.needs_update(hashed) is False


def test_unreadable_hash_is_treated_as_needing_update():
    """A hash the context cannot read is rehashed rather than trusted"""
    manager = PasswordManager()

    assert manager.needs_update("not-a-hash") is True


def test_needs_update_rejects_an_empty_hash():
    """An empty hash is an error, not an answer"""
    manager = PasswordManager()

    with pytest.raises(EmptyPasswordError):
        manager.needs_update("")


async def test_hash_info_reports_the_scheme():
    """Hash analysis names the scheme that produced it"""
    manager = PasswordManager()

    hashed = await manager.hash_password(PASSWORD)

    assert manager.get_hash_info(hashed) == {"scheme": "argon2"}


def test_hash_info_rejects_an_unidentifiable_hash():
    """A string that identifies as no scheme is reported as invalid"""
    manager = PasswordManager()

    with pytest.raises(InvalidPasswordHashError):
        manager.get_hash_info("not-a-hash")


def test_hash_info_rejects_an_empty_hash():
    """An empty hash is an error, not an answer"""
    manager = PasswordManager()

    with pytest.raises(EmptyPasswordError):
        manager.get_hash_info("")


async def test_support_check_accepts_its_own_hash_and_refuses_junk():
    """Support detection answers without raising for any input"""
    manager = PasswordManager()
    hashed = await manager.hash_password(PASSWORD)

    assert manager.is_hash_supported(hashed) is True
    assert manager.is_hash_supported("not-a-hash") is False
    assert manager.is_hash_supported("") is False
