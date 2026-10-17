"""Read each kind's models from the person's live Dreamina model list, sharing reads and keeping each list.

Each list is kept for the life of the process. The read is free, and a name it misses reads the list again once.
"""

from __future__ import annotations

import asyncio
import difflib
import weakref
from .cli import send_command
from typing import TYPE_CHECKING
from .failures import build_failure
from pydantic import ValidationError
from ..types.models import ModelListReply
from ..config.messages.run import CLI_FAILED
from ..types.errors import ErrorCode, DreaminaError
from ..config.models import KINDS, KIND_NODES, LIST_COMMAND, DEFAULT_MODELS, SUGGESTION_COUNT, LIST_TIMEOUT_SECONDS
from ..config.messages.models import (
    ANY_KIND,
    KIND_NAMES,
    MODEL_KIND,
    MODEL_EMPTY,
    MODEL_UNKNOWN,
    MODEL_AMBIGUOUS,
    MODEL_LIST_EMPTY,
    MODEL_LIST_UNREADABLE,
)

if TYPE_CHECKING:
    from ..types import Kind
    from ..types.models import ListedModel

# Each kind's models, read once per ComfyUI process; a name a list misses reads it again.
_LISTS: dict[str, tuple[ListedModel, ...]] = {}
# The reads in flight on each event loop, keyed by kind, which callers asking at the same time share.
_READS: weakref.WeakKeyDictionary[asyncio.AbstractEventLoop, dict[str, asyncio.Task[tuple[ListedModel, ...]]]] = (
    weakref.WeakKeyDictionary()
)


def _delete_read(
    reads: dict[str, asyncio.Task[tuple[ListedModel, ...]]], kind: str, read: asyncio.Task[tuple[ListedModel, ...]]
) -> None:
    """Drop a finished read, so a later caller reads the list again when this one kept nothing.

    Its failure already reached every caller still waiting; taking it here keeps a read whose callers all cancelled
    from failing unseen.
    """
    del reads[kind]
    if not read.cancelled():
        read.exception()


async def _send_model_list(kind: str) -> tuple[ListedModel, ...]:
    """Read one kind's models from the CLI and keep them; a failed read keeps nothing."""
    result = await send_command((*LIST_COMMAND, kind), LIST_TIMEOUT_SECONDS)
    if not result.reply.ok:
        raise build_failure(result, CLI_FAILED)
    try:
        models = ModelListReply.model_validate(result.reply.payload).items
    except ValidationError:
        raise DreaminaError(ErrorCode.TRANSPORT, MODEL_LIST_UNREADABLE) from None
    _LISTS[kind] = models
    return models


async def _read_model_list(kind: str) -> tuple[ListedModel, ...]:
    """Return one kind's kept models, or read them, sharing the read with every caller that asks at the same time.

    A task belongs to its event loop, and ComfyUI runs each prompt on a new one and validates queued prompts on the
    server's, so the reads in flight are kept per loop. A caller's cancel leaves the read running for the others.
    """
    if kind in _LISTS:
        return _LISTS[kind]
    reads = _READS.setdefault(asyncio.get_running_loop(), {})
    task = reads.get(kind)
    if task is None:
        task = reads[kind] = asyncio.create_task(_send_model_list(kind))
        task.add_done_callback(lambda done: _delete_read(reads, kind, done))
    return await asyncio.shield(task)


def _find_match(models: tuple[ListedModel, ...], name: str) -> ListedModel | None:
    """Match a name to a canonical name, then to an alias, ignoring case; never by substring or ranking."""
    typed = name.casefold()
    exact = next((model for model in models if model.name.casefold() == typed), None)
    if exact is not None:
        return exact
    aliased = [model for model in models if any(alias.casefold() == typed for alias in model.aliases)]
    if len(aliased) > 1:
        names = ", ".join(model.name for model in aliased)
        raise DreaminaError(ErrorCode.INVALID_INPUT, MODEL_AMBIGUOUS.format(model=name, names=names))
    return aliased[0] if aliased else None


async def _find_in_kind(name: str, kind: str) -> tuple[ListedModel | None, tuple[ListedModel, ...]]:
    """Match a name in one kind's list, reading the list again once when a list kept from earlier misses it."""
    was_kept = kind in _LISTS
    models = await _read_model_list(kind)
    match = _find_match(models, name)
    if match is None and was_kept:
        _LISTS.pop(kind, None)
        models = await _read_model_list(kind)
        match = _find_match(models, name)
    return match, models


def _build_unknown(name: str, models: tuple[ListedModel, ...], made: str) -> DreaminaError:
    """Refuse a name no list holds, suggesting the closest canonical names; equal scores keep list order."""
    if not models:
        return DreaminaError(ErrorCode.UNAVAILABLE, MODEL_LIST_EMPTY.format(made=made))
    typed = name.casefold()
    ranked = sorted(
        models,
        key=lambda model: max(
            difflib.SequenceMatcher(None, typed, candidate.casefold()).ratio()
            for candidate in (model.name, *model.aliases)
        ),
        reverse=True,
    )
    names = ", ".join(model.name for model in ranked[:SUGGESTION_COUNT])
    return DreaminaError(ErrorCode.UNAVAILABLE, MODEL_UNKNOWN.format(model=name, names=names))


async def _find_any(name: str) -> ListedModel:
    """Find a model of any kind, for Model: Info, searching each kind in menu order."""
    searched: list[ListedModel] = []
    for kind in KINDS:
        match, models = await _find_in_kind(name, kind)
        if match is not None:
            return match
        searched.extend(models)
    raise _build_unknown(name, tuple(searched), ANY_KIND)


async def find_model(name: str, kind: Kind | None) -> ListedModel:
    """Find a typed model name in the person's live list of one kind, or of every kind when no kind is given.

    A paid node passes its kind, and a model of another kind is refused with the node that runs it. Model: Info
    passes no kind.
    """
    name = name.strip()
    if not name:
        raise DreaminaError(ErrorCode.INVALID_INPUT, MODEL_EMPTY.format(example=DEFAULT_MODELS[kind or "image"]))
    if kind is None:
        return await _find_any(name)
    match, models = await _find_in_kind(name, kind)
    if match is not None:
        return match
    for other in KINDS:
        if other != kind and _find_match(await _read_model_list(other), name) is not None:
            message = MODEL_KIND.format(
                model=name, made=KIND_NAMES[other], node=KIND_NODES[other], this=KIND_NODES[kind]
            )
            raise DreaminaError(ErrorCode.INVALID_INPUT, message)
    raise _build_unknown(name, models, KIND_NAMES[kind])


__all__ = ["find_model"]
