"""Check once per process that the Dreamina CLI is recent enough and offers every command and flag sent to it.

On first use it runs version and schema, two local calls. A check is kept per binary path and modification time, so a
CLI found elsewhere after a move, or written again by an install, is checked again.
"""

from __future__ import annotations

import re
import asyncio
import weakref
from typing import TYPE_CHECKING
from pydantic import ValidationError
from .cli import find_binary, send_command
from ..config.patterns import VERSION_PATTERN
from ..types.errors import ErrorCode, DreaminaError
from ..types.replies import SchemaReply, VersionReply
from ..config.messages.cli import CLI_CHANGED, CLI_MISSING, CLI_OUTDATED, CLI_VERSION_UNREADABLE
from ..config.dreamina import CALL_SECONDS, MINIMUM_VERSION, REQUIRED_COMMANDS, REPLY_SCHEMA_VERSION

if TYPE_CHECKING:
    from ..types import Reply
    from collections.abc import Iterator
    from ..types.replies import SchemaFlag, SchemaCommand

_VERSION = re.compile(VERSION_PATTERN)
# The oldest release accepted, as three numbers.
_MINIMUM = tuple(int(part) for part in MINIMUM_VERSION.split("."))
# Each command this extension sends, with its flags by name, by command path.
type CommandFlags = dict[str, dict[str, SchemaFlag]]

# The binaries whose contract passed in this process, by path and modification time, with their command flags.
_VALIDATED: dict[str, CommandFlags] = {}
# The validations in flight on each event loop, keyed like _VALIDATED, which callers asking at the same time share.
_VALIDATIONS: weakref.WeakKeyDictionary[asyncio.AbstractEventLoop, dict[str, asyncio.Task[CommandFlags]]] = (
    weakref.WeakKeyDictionary()
)


async def _read_document[R: Reply](command: str, record: type[R]) -> R:
    """Run one local call of the check and read its reply, refusing one in a form this extension does not read.

    A missing CLI and one that cannot start keep their own messages.
    """
    try:
        result = await send_command((command,), CALL_SECONDS["LOCAL"])
    except DreaminaError as error:
        if error.code is ErrorCode.TRANSPORT:
            raise DreaminaError(ErrorCode.CONFIGURATION, CLI_VERSION_UNREADABLE) from None
        raise
    if not result.reply.ok or result.reply.schema_version != REPLY_SCHEMA_VERSION:
        raise DreaminaError(ErrorCode.CONFIGURATION, CLI_VERSION_UNREADABLE)
    try:
        return record.model_validate(result.reply.payload)
    except ValidationError:
        raise DreaminaError(ErrorCode.CONFIGURATION, CLI_VERSION_UNREADABLE) from None


def _list_commands(
    commands: tuple[SchemaCommand, ...], parents: tuple[str, ...] = ()
) -> Iterator[tuple[str, dict[str, SchemaFlag]]]:
    """Yield each command's path, its parents' names and its own joined by spaces, with its flags by name."""
    for command in commands:
        path = (*parents, command.name)
        yield " ".join(path), {flag.name: flag for flag in command.flags}
        yield from _list_commands(command.subcommands, path)


async def _read_contract() -> CommandFlags:
    """Refuse a CLI that is too old, or that lacks a command or a flag this extension sends; return their flags."""
    version = (await _read_document("version", VersionReply)).version
    if not is_current_version(version):
        raise DreaminaError(ErrorCode.CONFIGURATION, CLI_OUTDATED.format(version=version, minimum=MINIMUM_VERSION))
    schema = await _read_document("schema", SchemaReply)
    if schema.schema_version != REPLY_SCHEMA_VERSION:
        raise DreaminaError(ErrorCode.CONFIGURATION, CLI_VERSION_UNREADABLE)
    commands = dict(_list_commands(schema.subcommands))
    for path, flags in REQUIRED_COMMANDS.items():
        names = commands.get(path)
        missing = path if names is None else next((f"{path} --{flag}" for flag in flags if flag not in names), None)
        if missing is not None:
            raise DreaminaError(ErrorCode.CONFIGURATION, CLI_CHANGED.format(command=missing))
    return {path: commands[path] for path in REQUIRED_COMMANDS}


def _delete_validation(
    validations: dict[str, asyncio.Task[CommandFlags]], key: str, task: asyncio.Task[CommandFlags]
) -> None:
    """Drop a finished validation, so a later caller checks again when this one failed.

    Its failure already reached every caller still waiting; taking it here keeps a validation whose callers all
    cancelled from failing unseen.
    """
    del validations[key]
    if not task.cancelled():
        task.exception()


def is_current_version(version: str | None) -> bool:
    """Whether a release is MINIMUM_VERSION or later; no version, or text that is not a release, is not current."""
    if version is None:
        return False
    match = _VERSION.match(version)
    return match is not None and tuple(int(part) for part in match.groups()) >= _MINIMUM


async def validate_cli() -> CommandFlags:
    """Check the installed CLI once per process, sharing the check with every caller that asks at the same time.

    It returns the schema's flags of every command this extension sends, so a caller that needs a flag's rule reads it
    from the same check. A task belongs to its event loop, and ComfyUI runs each prompt on a new one, so the checks in
    flight are kept per loop. A caller's cancel leaves the check running for the others.
    """
    binary = find_binary()
    try:
        key = f"{binary}:{binary.stat().st_mtime_ns}" if binary is not None else None
    except OSError:
        key = None
    if key is None:
        raise DreaminaError(ErrorCode.CONFIGURATION, CLI_MISSING)
    flags = _VALIDATED.get(key)
    if flags is not None:
        return flags
    validations = _VALIDATIONS.setdefault(asyncio.get_running_loop(), {})
    task = validations.get(key)
    if task is None:
        task = validations[key] = asyncio.create_task(_read_contract())
        task.add_done_callback(lambda done: _delete_validation(validations, key, done))
    flags = _VALIDATED[key] = await asyncio.shield(task)
    return flags


__all__ = ["is_current_version", "validate_cli"]
