"""Install the Dreamina CLI with ByteDance's official installer, and read the installed release.

What runs is ByteDance's own script, fetched from its one host; the extension bundles no installer and no binary, and
never runs a command a reply names.
"""

from __future__ import annotations

import os
import sys
from http import HTTPStatus
import shutil
import asyncio
from pathlib import Path
import tempfile
import contextlib
from urllib.parse import urlsplit

import aiohttp

from .cli import parse_reply, send_command
from .failures import sanitize_reason
from ..config.units import SECONDS_PER_MINUTE
from ..state.errors import ErrorCode, DreaminaError
from ..state.replies import VersionReply
from ..config.storage import TEMPORARY_PREFIX
from ..config.dreamina import ACCOUNT_TIMEOUTS
from ..config.installer import (
    INSTALLER_URLS,
    INSTALLER_BYTES,
    INSTALLER_DOMAINS,
    INSTALLER_PROGRAMS,
    INSTALLER_REDIRECTS,
    INSTALLER_REASON_LINES,
    INSTALL_TIMEOUT_SECONDS,
    INSTALLER_DOWNLOAD_SECONDS,
)
from ..config.messages.cli import (
    INSTALL_FAILED,
    INSTALL_TIMEOUT,
    INSTALL_NO_ANSWER,
    INSTALL_DOWNLOAD_FAILED,
    INSTALL_PROGRAM_MISSING,
)

# The installer key for the server's system.
_SYSTEM = 'WINDOWS' if sys.platform == 'win32' else 'POSIX'


async def _read_script(url: str) -> bytes:
    """Download the installer script, refusing another status, a body larger than a script, and any other host.

    The download follows the redirects to ByteDance's content delivery network, and keeps the script only when it came
    over HTTPS from a CapCut domain. The session reads no proxy settings from the environment and verifies TLS, as
    aiohttp does by default.

    Args:
        url: The address of the installer script on ByteDance's host.

    Returns:
        The bytes of the script.

    Raises:
        DreaminaError: When the status is not 200, the last host is not a CapCut domain over HTTPS, or the body is too
            large.

    """
    async with (
        aiohttp.ClientSession(trust_env=False) as session,
        session.get(url, max_redirects=INSTALLER_REDIRECTS) as response,
    ):
        host = response.url.host or ''
        if response.status != HTTPStatus.OK or response.url.scheme != 'https' or not host.endswith(INSTALLER_DOMAINS):
            raise DreaminaError(ErrorCode.TRANSPORT, INSTALL_DOWNLOAD_FAILED)
        script = bytearray()
        async for chunk in response.content.iter_any():
            script += chunk
            if len(script) > INSTALLER_BYTES['SCRIPT']:
                raise DreaminaError(ErrorCode.TRANSPORT, INSTALL_DOWNLOAD_FAILED)
    return bytes(script)


def _save_script(script: bytes, suffix: str) -> Path:
    """Write the script to a private temporary file, which only its owner can read, and delete it if the write fails.

    Args:
        script: The bytes of the installer script.
        suffix: The file extension the temporary file takes.

    Returns:
        The path of the temporary file.

    Raises:
        BaseException: Whatever the write raises, after the file is deleted.

    """
    descriptor, name = tempfile.mkstemp(prefix=TEMPORARY_PREFIX, suffix=suffix)
    path = Path(name)
    try:
        with os.fdopen(descriptor, 'wb') as file:
            file.write(script)
    except BaseException:
        path.unlink(missing_ok=True)
        raise
    return path


async def _read_tail(stream: asyncio.StreamReader | None) -> bytes:
    """Read one output stream to its end, keeping only its last `INSTALLER_BYTES["OUTPUT"]` bytes.

    Args:
        stream: The installer's stdout or stderr; None reads nothing.

    Returns:
        The last bytes of the stream.

    """
    tail = b''
    while stream is not None and (chunk := await stream.read(INSTALLER_BYTES['OUTPUT'])):
        tail = (tail + chunk)[-INSTALLER_BYTES['OUTPUT'] :]
    return tail


def _describe_output(stdout: bytes, stderr: bytes) -> str:
    """Quote the installer's last lines without paths and links, from stderr or from stdout when stderr is empty.

    Args:
        stdout: The tail of the installer's standard output.
        stderr: The tail of the installer's standard error.

    Returns:
        The last lines, joined into one sanitized reason.

    """
    text = (stderr if stderr.strip() else stdout).decode(errors='replace')
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return sanitize_reason(' '.join(lines[-INSTALLER_REASON_LINES:]))


async def _wait_for_installer(installer_path: Path) -> None:
    """Run the installer with its shell, by full path, and refuse a failed or stalled run.

    A cancel or the timeout kills the shell and waits for it, so no child outlives the route. The installer takes a
    lock folder and keeps a backup, so a run cut short leaves the earlier CLI working.

    Args:
        installer_path: The downloaded installer script to run.

    Raises:
        DreaminaError: When the shell is missing or does not start, the run passes the timeout, or the installer exits
            with an error.

    """
    program, *options = INSTALLER_PROGRAMS[_SYSTEM]
    program_path = shutil.which(program)
    if program_path is None:
        raise DreaminaError(ErrorCode.CONFIGURATION, INSTALL_PROGRAM_MISSING.format(program=program))
    try:
        process = await asyncio.create_subprocess_exec(
            program_path,
            *options,
            str(installer_path),
            stdin=asyncio.subprocess.DEVNULL,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
    except OSError:
        raise DreaminaError(ErrorCode.CONFIGURATION, INSTALL_PROGRAM_MISSING.format(program=program)) from None
    try:
        async with asyncio.timeout(INSTALL_TIMEOUT_SECONDS):
            stdout, stderr, exit_code = await asyncio.gather(
                _read_tail(process.stdout), _read_tail(process.stderr), process.wait()
            )
    except TimeoutError:
        minutes = INSTALL_TIMEOUT_SECONDS // SECONDS_PER_MINUTE
        raise DreaminaError(ErrorCode.TIMEOUT, INSTALL_TIMEOUT.format(minutes=minutes)) from None
    finally:
        if process.returncode is None:
            with contextlib.suppress(ProcessLookupError):
                process.kill()
            await asyncio.shield(process.wait())
    if exit_code:
        raise DreaminaError(ErrorCode.CONFIGURATION, INSTALL_FAILED.format(reason=_describe_output(stdout, stderr)))


async def read_cli_version() -> str | None:
    """Return the installed release; None when the CLI is missing or does not answer.

    Returns:
        The release the CLI reports, or None.

    """
    try:
        result = await send_command(('version',), ACCOUNT_TIMEOUTS['LOCAL'])
        reply = parse_reply(result.reply.payload, VersionReply) if result.reply.ok else None
    except DreaminaError:
        return None
    return reply.version if reply is not None else None


async def download_installer() -> Path:
    """Fetch the official installer into a private temporary file and return its path.

    The file keeps the address's suffix, because PowerShell runs only a .ps1 file.

    Returns:
        The path of the temporary file that holds the installer.

    Raises:
        DreaminaError: When the download fails or passes its timeout.

    """
    url = INSTALLER_URLS[_SYSTEM]
    try:
        async with asyncio.timeout(INSTALLER_DOWNLOAD_SECONDS):
            script = await _read_script(url)
    except (aiohttp.ClientError, TimeoutError):
        raise DreaminaError(ErrorCode.TRANSPORT, INSTALL_DOWNLOAD_FAILED) from None
    return await asyncio.to_thread(_save_script, script, Path(urlsplit(url).path).suffix)


async def save_cli(installer_path: Path) -> None:
    """Run the downloaded installer, which writes the CLI to disk, and refuse a CLI that does not answer afterwards.

    This function deletes the installer file whatever the outcome. The next run checks the new binary, whose
    modification time changed.

    Args:
        installer_path: The installer file that download_installer wrote.

    Raises:
        DreaminaError: When the installer fails, or the CLI gives no version after the install.

    """
    try:
        await _wait_for_installer(installer_path)
    finally:
        await asyncio.to_thread(installer_path.unlink, missing_ok=True)
    if await read_cli_version() is None:
        raise DreaminaError(ErrorCode.CONFIGURATION, INSTALL_NO_ANSWER)


__all__ = ['download_installer', 'read_cli_version', 'save_cli']
