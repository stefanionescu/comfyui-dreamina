"""Define the operation every node hands to the run wrapper, and how a paid call is awaited through a cancel."""

from __future__ import annotations

import asyncio
from typing import Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable, Awaitable
    from ..types.settings import Settings, Configuration

type Progress = Callable[[int], Awaitable[None]]


class Operation[Result](Protocol):
    """One Dreamina operation, validated before anything is sent."""

    def validate(self, settings: Settings) -> None:
        """Refuse inputs the settings do not allow, before anything is sent."""
        raise NotImplementedError(settings)

    async def send(self, configuration: Configuration, progress: Progress | None) -> Result:
        """Send the operation, report each step reached, and return its result."""
        raise NotImplementedError(configuration, progress)


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


__all__ = ["Operation", "wait_until_settled"]
