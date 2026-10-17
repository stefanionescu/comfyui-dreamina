"""Share the cache key, the run number, and the list inputs of the paid nodes."""

from __future__ import annotations

import asyncio
from comfy_api.latest import io
from ..comfy.runtime import get_runtime
from ..config.inputs import INPUT_NAMES
from ..dreamina.account import read_account
from typing import TYPE_CHECKING, ClassVar, cast
from ..config.messages.inputs import SINGLE_VALUE
from ..types.errors import ErrorCode, DreaminaError

if TYPE_CHECKING:
    from collections.abc import Callable, Awaitable


def _read_single(name: str, value: object) -> object:
    """Take the one value an input list holds; a plain value, from a call in Python, passes as it is."""
    if not isinstance(value, list):
        return value
    values = cast("list[object]", value)
    if len(values) != 1:
        raise DreaminaError(ErrorCode.INVALID_INPUT, SINGLE_VALUE.format(name=name))
    return values[0]


class PaidNode(io.ComfyNode):
    """Own the cache key, the run-number input, and the list inputs every paid node shares.

    Attributes:
        send: Typed entry point that receives every saved input except the run number.
        list_inputs: The media inputs of the node; each reaches send as the whole list, and every other input as its
            one value.

    """

    send: ClassVar[Callable[..., Awaitable[io.NodeOutput]]]
    list_inputs: ClassVar[frozenset[str]] = frozenset()

    @classmethod
    async def fingerprint_inputs(cls, **_inputs: object) -> str:
        """Add the signed-in account's token to the cache key, so another account runs the node again.

        The account is read once per process and after each sign-in or sign-out. A signed-out read raises the sign-in
        error, so the node runs and refuses with it.
        """
        store = get_runtime().configuration
        snapshot = await asyncio.to_thread(store.read_snapshot)
        if snapshot.account is not None:
            return snapshot.account
        account = await read_account()
        return await asyncio.to_thread(store.create_account_token, account.user_id, snapshot.account_changes)

    @classmethod
    async def execute(cls, **inputs: object) -> io.NodeOutput:  # pyright: ignore[reportIncompatibleMethodOverride] -- reason: ComfyUI awaits an async execute.
        """Drop the run number, which ComfyUI uses to invalidate its cache, and send.

        A node that takes input lists receives every input as a list; only its media inputs may hold several items.
        """
        inputs.pop(INPUT_NAMES["RUN_NUMBER"], None)
        values = {
            name: value if name in cls.list_inputs else _read_single(name, value) for name, value in inputs.items()
        }
        return await cls.send(**values)


__all__ = ["PaidNode"]
