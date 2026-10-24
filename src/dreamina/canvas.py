"""Find the canvas every node writes to, and create it when there is none.

Every run lists the account's canvases first, so a new canvas replaces one the person deleted on Dreamina before any
upload or run.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING
import asyncio

from .cli import parse_reply, send_command
from .failures import build_failure
from ..state.errors import ErrorCode, DreaminaError
from ..state.replies import CanvasReply, CanvasListReply
from ..config.dreamina import CANVAS_NAME, CALL_SECONDS, CANVAS_PAGE_SIZE
from ..state.generations import CanvasRecord
from ..config.generations import RECORD_VERSION
from ..config.messages.run import CLI_FAILED

if TYPE_CHECKING:
    from ..storage.canvas import CanvasStore


async def _is_listed(project_id: str) -> bool:
    """Whether the account's canvas list holds this canvas, reading page after page until it finds the canvas."""
    cursor: str | None = None
    while True:
        arguments = ('canvas', 'ls', '--limit', str(CANVAS_PAGE_SIZE), *(('--cursor', cursor) if cursor else ()))
        result = await send_command(arguments, CALL_SECONDS['READ'])
        if not result.reply.ok:
            raise build_failure(result, CLI_FAILED)
        page = parse_reply(result.reply.payload, CanvasListReply)
        if any(item.project_id == project_id for item in page.items):
            return True
        if not page.has_more or not page.next_cursor:
            return False
        cursor = page.next_cursor


async def find_canvas(store: CanvasStore) -> CanvasRecord | None:
    """Return the saved canvas while Dreamina still lists it; None when the store holds none or the person deleted it.

    The next create_canvas replaces the record of a deleted canvas, so this function keeps the record.
    """
    record = await asyncio.to_thread(store.read)
    if record is None or not await _is_listed(record.project_id):
        return None
    return record


async def create_canvas(store: CanvasStore) -> CanvasRecord:
    """Create the pack's canvas with an ID made here, and save it.

    Only a lost or unreadable reply sends the same call again, once, with the same ID, so a lost reply never leaves a
    second canvas. The CLI's current canvas is never changed.
    """
    project_id = str(uuid.uuid4())
    arguments = ('canvas', 'create', CANVAS_NAME, '--project-id', project_id)
    try:
        result = await send_command(arguments, CALL_SECONDS['READ'])
    except DreaminaError as error:
        if error.code is not ErrorCode.TRANSPORT:
            raise
        result = await send_command(arguments, CALL_SECONDS['READ'])
    if not result.reply.ok:
        raise build_failure(result, CLI_FAILED)
    project = parse_reply(result.reply.payload, CanvasReply).project
    record = CanvasRecord(version=RECORD_VERSION, project_id=project.project_id, web_url=project.web_url)
    await asyncio.to_thread(store.save, record)
    return record


__all__ = ['create_canvas', 'find_canvas']
