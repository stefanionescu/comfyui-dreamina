"""Download a finished node's outputs through the CLI, checking each file's size and SHA-256 before reading it."""

from __future__ import annotations

import math
import time
import asyncio
import hashlib
import tempfile
from pathlib import Path
from .cli import send_command
from .failures import build_failure
from pydantic import ValidationError
from typing import TYPE_CHECKING, cast
from ..types.replies import DownloadReply
from ..types.generations import OutputFile
from ..config.storage import TEMPORARY_PREFIX
from ..config.units import BYTES_PER_MEGABYTE
from ..types.errors import ErrorCode, DreaminaError
from ..config.media import FREE_ATTEMPTS, RESOURCE_KINDS, RESOURCE_SUCCESS
from ..config.messages.media import (
    RESOURCE_TYPE,
    DOWNLOAD_EMPTY,
    DOWNLOAD_LIMIT,
    DOWNLOAD_FAILED,
    OUTPUTS_MISSING,
    DOWNLOAD_MISMATCH,
)

if TYPE_CHECKING:
    from ..types import Kind
    from ..types.cli import CliResult
    from ..types.replies import NodeView
    from ..types.settings import Settings


def _read_download(path: Path, size: int, sha256: str) -> bytes | None:
    """Read the pack's own copy of a download and delete it; None when it is missing or does not match the reply."""
    try:
        with path.open("rb") as file:
            content = file.read(size + 1)
    except OSError:
        return None
    finally:
        path.unlink(missing_ok=True)
    return content if len(content) == size and hashlib.sha256(content).hexdigest() == sha256.lower() else None


async def _read_checked(result: CliResult, resource_id: str, path: Path, settings: Settings) -> bytes | None:
    """Read one successful download's reply and file; None when the outcome is unknown and the file is sent again."""
    try:
        reply = DownloadReply.model_validate(result.reply.payload)
    except ValidationError:
        return None
    if reply.resource_id != resource_id:
        return None
    if reply.size == 0:
        raise DreaminaError(ErrorCode.MEDIA, DOWNLOAD_EMPTY)
    maximum = settings.max_download_megabytes
    if reply.size > maximum * BYTES_PER_MEGABYTE:
        shown = math.ceil(reply.size * 10 / BYTES_PER_MEGABYTE) / 10
        raise DreaminaError(ErrorCode.MEDIA, DOWNLOAD_LIMIT.format(size=shown, maximum=maximum))
    return await asyncio.to_thread(_read_download, path, reply.size, reply.sha256)


async def _download_file(project_id: str, resource_id: str, path: Path, settings: Settings, deadline: float) -> bytes:
    """Download one resource, a second time only when the first outcome is unknown, and return its checked bytes."""
    arguments = ("resource", "download", resource_id, "--project-id", project_id, "--output", str(path))
    for attempt in range(1, FREE_ATTEMPTS + 1):
        try:
            result = await send_command(arguments, max(deadline - time.monotonic(), 1.0))
        except DreaminaError as error:
            if error.code is not ErrorCode.TRANSPORT or attempt == FREE_ATTEMPTS:
                raise
            continue
        if result.reply.ok:
            content = await _read_checked(result, resource_id, path, settings)
            if content is not None:
                return content
        elif result.reply.error is None or not result.reply.error.retryable or attempt == FREE_ATTEMPTS:
            raise build_failure(result, DOWNLOAD_FAILED)
    raise DreaminaError(ErrorCode.MEDIA, DOWNLOAD_MISMATCH)


async def download_resources(
    project_id: str, node: NodeView, submit_id: str, settings: Settings, deadline: float
) -> tuple[OutputFile, ...]:
    """Download the finished resources of one submit ID, in the node's order, and return their bytes.

    At most one output file is on disk at a time, in a private temporary folder, under a name the pack makes.
    """
    resources = [
        resource
        for resource in node.resources
        if resource.submit_id == submit_id and resource.status == RESOURCE_SUCCESS
    ]
    if not resources:
        raise DreaminaError(ErrorCode.MEDIA, OUTPUTS_MISSING)
    unknown = next((resource.type for resource in resources if resource.type not in RESOURCE_KINDS), None)
    if unknown is not None:
        raise DreaminaError(ErrorCode.MEDIA, RESOURCE_TYPE.format(type=unknown))
    files: list[OutputFile] = []
    with tempfile.TemporaryDirectory(prefix=TEMPORARY_PREFIX, ignore_cleanup_errors=True) as folder:
        for index, resource in enumerate(resources, 1):
            path = Path(folder) / f"output-{index}"
            content = await _download_file(project_id, resource.resource_id, path, settings, deadline)
            files.append(OutputFile(resource.resource_id, cast("Kind", RESOURCE_KINDS[resource.type]), content))
    return tuple(files)


__all__ = ["download_resources"]
