"""Define the progress report every operation gives, and how to await a paid call through a cancel."""

from __future__ import annotations

from typing import TYPE_CHECKING
import asyncio

if TYPE_CHECKING:
    from collections.abc import Callable, Awaitable

type Progress = Callable[[int], Awaitable[None]]


async def wait_until_settled[T](task: asyncio.Task[T]) -> bool:
    """Wait until the asyncio task ends, however often a cancel arrives, and report whether one arrived.

    A cancel stops only the wait, never the asyncio task it waits for, so a second cancel cannot cut it off either.
    """
    is_cancelled = False
    while not task.done():
        try:
            await asyncio.wait({task})
        except asyncio.CancelledError:
            is_cancelled = True
    return is_cancelled


__all__ = ['wait_until_settled']
