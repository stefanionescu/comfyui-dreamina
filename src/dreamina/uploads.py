"""Upload a run's local media to the pack's canvas through the CLI, each distinct file once.

This module keeps nothing between runs. The encoded files live in a private temporary folder until their uploads finish.
"""

from __future__ import annotations

import math
import time
import uuid
from typing import TYPE_CHECKING
import asyncio
import hashlib
from pathlib import Path
import tempfile

from .cli import parse_reply, send_command
from .failures import build_failure
from ..config.media import FREE_ATTEMPTS, UPLOAD_FORMATS, UPLOAD_STATE_UNKNOWN
from ..config.units import BYTES_PER_MEGABYTE
from ..state.errors import ErrorCode, DreaminaError
from ..state.replies import UploadReply
from ..config.storage import TEMPORARY_PREFIX
from ..state.references import Reference
from ..config.messages.media import UPLOAD_LIMIT, UPLOAD_REFUSED, UPLOAD_UNREADABLE

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

    from ..state.settings import Settings
    from ..state.references import LocalMedia


def _encode_files(
    items: Sequence[LocalMedia], encode: Callable[[LocalMedia, Path], Path], folder: Path
) -> list[tuple[Path, int, str]]:
    """Encode every item into the folder, and read each file's size and SHA-256; this blocks."""
    encoded: list[tuple[Path, int, str]] = []
    for item in items:
        path = encode(item, folder)
        with path.open('rb') as file:
            digest = hashlib.file_digest(file, 'sha256').hexdigest()
        encoded.append((path, path.stat().st_size, digest))
    return encoded


def _validate_upload_size(items: Sequence[LocalMedia], sizes: Sequence[int], settings: Settings) -> None:
    """Refuse the first file larger than the maximum upload size, before any upload."""
    maximum = settings.max_upload_megabytes
    for item, size in zip(items, sizes, strict=True):
        if size > maximum * BYTES_PER_MEGABYTE:
            shown = math.ceil(size * 10 / BYTES_PER_MEGABYTE) / 10
            raise DreaminaError(
                ErrorCode.INVALID_INPUT, UPLOAD_LIMIT.format(kind=item.media, size=shown, maximum=maximum)
            )


async def _send_upload(project_id: str, path: Path, media_type: str, resource_id: str, deadline: float) -> None:
    """Upload one file, sending it a second time with the same resource ID only when the first outcome is unknown.

    The unknown outcomes are a reply the CLI runner cannot read, a retryable failure, and the CLI's own unknown upload
    state. Every other failure has a definite answer, and this function raises it at once.
    """
    arguments = (
        "resource", "upload", "--project-id", project_id, "--file", str(path), "--type", media_type,
        "--resource-id", resource_id,
    )  # fmt: skip
    for attempt in range(1, FREE_ATTEMPTS + 1):
        try:
            result = await send_command(arguments, max(deadline - time.monotonic(), 1.0))
        except DreaminaError as error:
            if error.code is not ErrorCode.TRANSPORT or attempt == FREE_ATTEMPTS:
                raise
            continue
        failure = result.reply.error
        if result.reply.ok:
            if parse_reply(result.reply.payload, UploadReply).resource_id != resource_id:
                raise DreaminaError(ErrorCode.TRANSPORT, UPLOAD_UNREADABLE)
            return
        if (
            failure is None
            or not (failure.retryable or failure.code == UPLOAD_STATE_UNKNOWN)
            or attempt == FREE_ATTEMPTS
        ):
            raise build_failure(result, UPLOAD_REFUSED)


async def send_media(
    project_id: str,
    items: Sequence[LocalMedia],
    encode: Callable[[LocalMedia, Path], Path],
    settings: Settings,
    deadline: float,
) -> tuple[Reference, ...]:
    """Upload every item to the canvas and return one resource reference per item, in item order.

    This function encodes every item and checks it against the maximum upload size before the first upload. It
    uploads items with the same bytes once, and they share one reference.
    """
    if not items:
        return ()
    uploaded: dict[str, str] = {}
    with tempfile.TemporaryDirectory(prefix=TEMPORARY_PREFIX, ignore_cleanup_errors=True) as folder:
        encoded = await asyncio.to_thread(_encode_files, items, encode, Path(folder))
        _validate_upload_size(items, [size for _, size, _ in encoded], settings)
        for item, (path, _, digest) in zip(items, encoded, strict=True):
            if digest not in uploaded:
                resource_id = str(uuid.uuid4())
                await _send_upload(project_id, path, UPLOAD_FORMATS[item.media]['TYPE'], resource_id, deadline)
                uploaded[digest] = resource_id
    return tuple(
        Reference(origin='resource', value=uploaded[digest], media=item.media, title=None)
        for item, (_, _, digest) in zip(items, encoded, strict=True)
    )


__all__ = ['send_media']
