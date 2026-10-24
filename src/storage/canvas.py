"""Keep the pack's Dreamina canvas: its ID and its link."""

from __future__ import annotations

from typing import TYPE_CHECKING
import threading
from dataclasses import field, dataclass

from pydantic import ValidationError

from .files import read_file, save_file
from ..state.errors import ErrorCode, DreaminaError
from ..config.storage import MAX_FILE_BYTES
from ..state.generations import CanvasRecord
from ..config.messages.settings import STATE_UNREADABLE

if TYPE_CHECKING:
    from pathlib import Path


@dataclass(eq=False)
class CanvasStore:
    """Own canvas.json; the server loop reads it and the executor loop writes it, so a lock guards it.

    Attributes:
        path: The canvas file.

    """

    path: Path
    # The lock that reads and writes of the canvas file share across threads.
    _lock: threading.Lock = field(default_factory=threading.Lock, init=False, repr=False)

    def read(self) -> CanvasRecord | None:
        """Read the saved canvas; None when there is none or the file is not a canvas record, so a save replaces it."""
        with self._lock:
            if not self.path.exists():
                return None
            try:
                content = read_file(self.path, max_bytes=MAX_FILE_BYTES['CANVAS'])
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
        content = (record.model_dump_json(indent=2) + '\n').encode()
        with self._lock:
            save_file(self.path, content)


__all__ = ['CanvasStore']
