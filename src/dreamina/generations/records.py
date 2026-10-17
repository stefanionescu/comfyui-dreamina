"""Keep a private record of every generation Dreamina accepted.

A generation keeps running after a cancel, a timeout, or a ComfyUI restart, and its record lets Generation: Download
collect it.
"""

from __future__ import annotations

import threading
from typing import TYPE_CHECKING
from pydantic import ValidationError
from ...storage.files import save_file, read_file
from ...types.generations import GenerationRecord
from ...types.errors import ErrorCode, DreaminaError
from ...config.messages.generations import GENERATION_UNKNOWN
from ...config.storage import MAX_FILE_BYTES, GENERATION_SUFFIX

if TYPE_CHECKING:
    from pathlib import Path


class GenerationStore:
    """Own the generation records folder; every method blocks, so callers run it off the event loop."""

    def __init__(self, directory: Path) -> None:
        """Select the private generations folder and the lock its files share across threads."""
        self.directory = directory
        self._lock = threading.Lock()

    def _read_all(self) -> list[GenerationRecord]:
        """Read every record; a damaged, oversized, or other-version file is skipped, so it never blocks the rest."""
        if not self.directory.is_dir():
            return []
        records: list[GenerationRecord] = []
        for path in sorted(self.directory.glob(f"*{GENERATION_SUFFIX}")):
            try:
                content = read_file(path, max_bytes=MAX_FILE_BYTES["GENERATION"])
                records.append(GenerationRecord.model_validate_json(content))
            except (OSError, ValidationError, DreaminaError):
                continue
        return records

    def save(self, record: GenerationRecord) -> None:
        """Write one record atomically, named by its submit ID."""
        path = self.directory / f"{record.submit_id}{GENERATION_SUFFIX}"
        with self._lock:
            save_file(path, (record.model_dump_json(indent=2) + "\n").encode())

    def delete(self, submit_id: str) -> None:
        """Delete one record; a record already gone needs no removal."""
        path = self.directory / f"{submit_id}{GENERATION_SUFFIX}"
        with self._lock:
            # reason: Record names are submit IDs this extension made, inside the private generations folder.
            # bearer:disable python_lang_path_traversal
            path.unlink(missing_ok=True)

    def list_records(self) -> list[GenerationRecord]:
        """List every recorded generation, of every kind, newest first: one node collects them all."""
        with self._lock:
            records = self._read_all()
        return sorted(records, key=lambda record: record.submitted_at, reverse=True)

    def find_record(self, label: str) -> GenerationRecord:
        """Return the newest record with this label; whole labels are compared, so two alike IDs stay apart."""
        record = next((record for record in self.list_records() if record.label == label), None)
        if record is None:
            raise DreaminaError(ErrorCode.INVALID_INPUT, GENERATION_UNKNOWN)
        return record


__all__ = ["GenerationStore"]
