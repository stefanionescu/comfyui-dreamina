"""Keep the pack's Dreamina canvas: its ID and its link."""

from __future__ import annotations

import threading
from typing import TYPE_CHECKING
from pydantic import ValidationError
from .files import save_file, read_file
from ..config.storage import MAX_FILE_BYTES
from ..types.generations import CanvasRecord
from ..types.errors import ErrorCode, DreaminaError
from ..config.messages.settings import STATE_UNREADABLE

if TYPE_CHECKING:
    from pathlib import Path


class CanvasStore:
    """Own canvas.json; the server loop reads it and the executor loop writes it, so a lock guards it."""

    def __init__(self, path: Path) -> None:
        """Select the canvas file and the lock its reads and writes share across threads."""
        self.path = path
        self._lock = threading.Lock()

    def read(self) -> CanvasRecord | None:
        """Read the saved canvas; None when there is none or the file is not a canvas record, so a save replaces it."""
        with self._lock:
            if not self.path.exists():
                return None
            try:
                content = read_file(self.path, max_bytes=MAX_FILE_BYTES["CANVAS"])
            except OSError:
                raise DreaminaError(ErrorCode.CONFIGURATION, STATE_UNREADABLE) from None
            except DreaminaError:
                return None
        try:
            return CanvasRecord.model_validate_json(content)
        except ValidationError:
            return None

    def save(self, record: CanvasRecord) -> None:
        """Write the canvas record atomically, replacing any earlier one."""
        content = (record.model_dump_json(indent=2) + "\n").encode()
        with self._lock:
            save_file(self.path, content)


__all__ = ["CanvasStore"]
