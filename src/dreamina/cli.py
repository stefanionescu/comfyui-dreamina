"""Find the Dreamina CLI and run it, the only place the extension starts it.

Each call is one process with closed input and capped output. A cancel or a timeout kills the process and waits for it
to end, so no child outlives its node.
"""

from __future__ import annotations

import os
import sys
import math
import shutil
from typing import TYPE_CHECKING
import asyncio
from pathlib import Path
import contextlib

from pydantic import ValidationError

from ..state.cli import CliReply, CliResult
from ..state.errors import ErrorCode, DreaminaError
from ..state.parsing import parse_json
from ..config.storage import ENVIRONMENT_VARIABLES
from ..config.dreamina import (
    EXIT_CODES,
    REPLY_BYTES,
    BINARY_NAMES,
    INSTALL_FOLDERS,
    MAX_REPLY_DEPTH,
    GLOBAL_ARGUMENTS,
)
from ..config.messages.cli import CLI_MISSING, CLI_TIMEOUT, CLI_NOT_STARTED, CLI_REPLY_INVALID

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ..state import Json, Reply

# The key of the server's system in BINARY_NAMES and INSTALL_FOLDERS.
_SYSTEM = 'WINDOWS' if sys.platform == 'win32' else 'POSIX'


async def _read_stream(stream: asyncio.StreamReader | None, max_bytes: int) -> bytes:
    """Read one stream to its end in chunks, refusing a reply over its cap."""
    content = bytearray()
    while stream is not None and (chunk := await stream.read(REPLY_BYTES['CHUNK'])):
        content += chunk
        if len(content) > max_bytes:
            raise DreaminaError(ErrorCode.TRANSPORT, CLI_REPLY_INVALID)
    return bytes(content)


def _parse_result(exit_code: int, stdout: bytes, stderr: bytes) -> CliResult:
    """Read the call's one reply: from stdout on success and from stderr otherwise."""
    is_ok = exit_code == EXIT_CODES['OK']
    content = stdout if is_ok else stderr
    try:
        document = parse_json(content.decode(), max_bytes=len(content) + 1, max_depth=MAX_REPLY_DEPTH)
    except (UnicodeError, DreaminaError):
        raise DreaminaError(ErrorCode.TRANSPORT, CLI_REPLY_INVALID) from None
    reply = parse_reply(document, CliReply)
    if reply.ok is not is_ok:
        raise DreaminaError(ErrorCode.TRANSPORT, CLI_REPLY_INVALID)
    return CliResult(exit_code, reply)


def find_binary() -> Path | None:
    """Return the first CLI found in the installer's own folder, on `PATH`, or in the installer's default folder.

    It runs at every call, so it finds an install or a move at once.
    """
    name = BINARY_NAMES[_SYSTEM]
    folder = os.environ.get(ENVIRONMENT_VARIABLES['INSTALL_DIRECTORY'])
    found = shutil.which(name)
    candidates = (
        Path(folder) / name if folder else None,
        Path(found) if found else None,
        Path.home().joinpath(*INSTALL_FOLDERS[_SYSTEM], name),
    )
    return next((path for path in candidates if path and path.is_file() and os.access(path, os.X_OK)), None)


def parse_reply[R: Reply](payload: Json, record: type[R]) -> R:
    """Read one success payload into its record, refusing a reply this extension cannot read."""
    try:
        return record.model_validate(payload)
    except ValidationError:
        raise DreaminaError(ErrorCode.TRANSPORT, CLI_REPLY_INVALID) from None


async def send_command(arguments: Sequence[str], timeout_seconds: float) -> CliResult:
    """Run one call and return its exit code and reply; the caller decides what a failure reply means.

    The call runs without a shell, so each argument reaches the CLI as it is. The server's environment reaches the CLI
    unchanged, so it finds the person's sign-in. The call reads both streams at once, so a full pipe never stops the
    child.
    """
    binary = find_binary()
    if binary is None:
        raise DreaminaError(ErrorCode.CONFIGURATION, CLI_MISSING)
    try:
        process = await asyncio.create_subprocess_exec(
            binary,
            *GLOBAL_ARGUMENTS,
            *arguments,
            stdin=asyncio.subprocess.DEVNULL,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
    except OSError:
        raise DreaminaError(ErrorCode.CONFIGURATION, CLI_NOT_STARTED) from None
    try:
        async with asyncio.timeout(timeout_seconds):
            stdout, stderr, exit_code = await asyncio.gather(
                _read_stream(process.stdout, REPLY_BYTES['STDOUT']),
                _read_stream(process.stderr, REPLY_BYTES['STDERR']),
                process.wait(),
            )
    except TimeoutError:
        raise DreaminaError(ErrorCode.TRANSPORT, CLI_TIMEOUT.format(seconds=math.ceil(timeout_seconds))) from None
    finally:
        if process.returncode is None:
            with contextlib.suppress(ProcessLookupError):
                process.kill()
            await asyncio.shield(process.wait())
    return _parse_result(exit_code, stdout, stderr)


__all__ = ['find_binary', 'parse_reply', 'send_command']
