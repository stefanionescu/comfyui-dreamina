"""Read and keep each kind's models from the person's live Dreamina model list, sharing reads.

This module keeps each list for the life of the process. The read is free, and a name it misses reads the list again
once.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
import asyncio
import difflib
import weakref

from pydantic import ValidationError

from .cli import send_command
from .failures import build_failure
from ..state.errors import ErrorCode, DreaminaError
from ..state.models import ModelListReply
from ..config.models import KINDS, KIND_NODES, LIST_COMMAND, DEFAULT_MODELS, SUGGESTION_COUNT, LIST_TIMEOUT_SECONDS
from ..config.messages.run import CLI_FAILED
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
    from ..state import Kind
    from ..state.models import ListedModel

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

    Args:
        reads: The reads in flight on the event loop of the read, keyed by kind.
        kind: The kind whose read ended.
        read: The finished task.

    """
    del reads[kind]
    if not read.cancelled():
        read.exception()


async def _send_model_list(kind: str) -> tuple[ListedModel, ...]:
    """Read one kind's models from the CLI and keep them; a failed read keeps nothing.

    Args:
        kind: The kind of models to list: image, video, or audio.

    Returns:
        The models the CLI lists for the kind.

    Raises:
        DreaminaError: When this extension cannot read the list the CLI sent.
        build_failure: When the CLI refuses the list command.

    """
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

    A task belongs to its event loop. ComfyUI runs each prompt on a new loop and validates queued prompts on the
    server's loop, so this module keeps the reads in flight per loop. A caller's cancel leaves the read running for the
    others.

    Args:
        kind: The kind whose list to return.

    Returns:
        The kept or newly read models of the kind.

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
    """Match a name to a canonical name, then to an alias, ignoring case; never by substring or ranking.

    Args:
        models: The listed models to search.
        name: The model name as the person typed it.

    Returns:
        The matching model, or None when no model has the name or alias.

    Raises:
        DreaminaError: When the name is an alias of more than one model.

    """
    typed = name.casefold()
    exact = next((model for model in models if model.name.casefold() == typed), None)
    if exact is not None:
        return exact
    aliased = [model for model in models if any(alias.casefold() == typed for alias in model.aliases)]
    if len(aliased) > 1:
        names = ', '.join(model.name for model in aliased)
        raise DreaminaError(ErrorCode.INVALID_INPUT, MODEL_AMBIGUOUS.format(model=name, names=names))
    return aliased[0] if aliased else None


async def _find_in_kind(name: str, kind: str) -> tuple[ListedModel | None, tuple[ListedModel, ...]]:
    """Match a name in one kind's list, reading the list again once when a list kept from earlier misses it.

    Args:
        name: The model name as the person typed it.
        kind: The kind whose list to search.

    Returns:
        The match, or None, and the list that was searched last.

    """
    was_kept = kind in _LISTS
    models = await _read_model_list(kind)
    match = _find_match(models, name)
    if match is None and was_kept:
        _LISTS.pop(kind, None)
        models = await _read_model_list(kind)
        match = _find_match(models, name)
    return match, models


def _build_unknown(name: str, models: tuple[ListedModel, ...], made: str) -> DreaminaError:
    """Refuse a name no list holds, suggesting the closest canonical names; equal scores keep list order.

    Args:
        name: The model name that no list holds.
        models: Every model that was searched.
        made: What the searched kinds make, as the message for an empty list names it.

    Returns:
        The error for the caller to raise.

    """
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
    names = ', '.join(model.name for model in ranked[:SUGGESTION_COUNT])
    return DreaminaError(ErrorCode.UNAVAILABLE, MODEL_UNKNOWN.format(model=name, names=names))


async def _find_any(name: str) -> ListedModel:
    """Find a model of any kind, for Model: Info, searching each kind in menu order.

    Args:
        name: The stripped model name to find.

    Returns:
        The first model that matches.

    Raises:
        _build_unknown: When no kind's list holds the name.

    """
    searched: list[ListedModel] = []
    for kind in KINDS:
        match, models = await _find_in_kind(name, kind)
        if match is not None:
            return match
        searched.extend(models)
    raise _build_unknown(name, tuple(searched), ANY_KIND)


async def find_model(name: str, kind: Kind | None) -> ListedModel:
    """Find a typed model name in the person's live list of one kind, or of every kind when the caller gives no kind.

    A paid node passes its kind, and this function refuses a model of another kind, naming the node that runs it.
    Model: Info passes no kind.

    Args:
        name: The model name as typed; spaces around it are ignored.
        kind: The kind of the calling node, or None to search every kind.

    Returns:
        The listed model with that name or alias.

    Raises:
        DreaminaError: When the name is empty, or the model belongs to another kind.
        _build_unknown: When no searched list holds the name.

    """
    name = name.strip()
    if not name:
        raise DreaminaError(ErrorCode.INVALID_INPUT, MODEL_EMPTY.format(example=DEFAULT_MODELS[kind or 'image']))
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


__all__ = ['find_model']
