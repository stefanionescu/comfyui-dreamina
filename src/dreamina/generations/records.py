"""Keep a private record of every generation Dreamina accepted.

A generation keeps running after a cancel, a timeout, or a ComfyUI restart, and its record lets Generation: Download
collect it.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
import threading
from dataclasses import field, dataclass

from pydantic import ValidationError

from ...state.errors import ErrorCode, DreaminaError
from ...storage.files import read_file, save_file
from ...config.storage import MAX_FILE_BYTES, GENERATION_SUFFIX
from ...state.generations import GenerationRecord
from ...config.generations import LABEL_SEPARATOR, LABEL_CHARACTERS
from ...config.messages.generations import GENERATION_UNKNOWN

if TYPE_CHECKING:
    from pathlib import Path


@dataclass(eq=False)
class GenerationStore:
    """Own the generation records folder; every method blocks, so callers run it off the event loop.

    Attributes:
        directory: The private generations folder.

    """

    directory: Path
    # The lock that the record files share across threads.
    _lock: threading.Lock = field(default_factory=threading.Lock, init=False, repr=False)

    def _read_all(self) -> list[GenerationRecord]:
        """Read every record, skipping a damaged, oversized, or other-version file so it never blocks the rest."""
        if not self.directory.is_dir():
            return []
        records: list[GenerationRecord] = []
        for path in sorted(self.directory.glob(f'*{GENERATION_SUFFIX}')):
            try:
                content = read_file(path, max_bytes=MAX_FILE_BYTES['GENERATION'])
                records.append(GenerationRecord.model_validate_json(content))
            except (OSError, ValidationError, DreaminaError):
                continue
        return records

    def save(self, record: GenerationRecord) -> None:
        """Write one record atomically, named by its submit ID."""
        path = self.directory / f'{record.submit_id}{GENERATION_SUFFIX}'
        with self._lock:
            save_file(path, (record.model_dump_json(indent=2) + '\n').encode())

    def delete(self, submit_id: str) -> None:
        """Delete one record; a record already gone needs no removal."""
        path = self.directory / f'{submit_id}{GENERATION_SUFFIX}'
        with self._lock:
            path.unlink(missing_ok=True)

    def list_records(self) -> list[GenerationRecord]:
        """List every recorded generation, of every kind, newest first: one node collects them all."""
        with self._lock:
            records = self._read_all()
        return sorted(records, key=lambda record: record.submitted_at, reverse=True)

    def list_labeled_records(self) -> list[tuple[str, GenerationRecord]]:
        """List every record, newest first, with its label in Generation: Download.

        A label holds the start of the submit ID, the model, and the minute of the submission in UTC.
        """
        labeled: list[tuple[str, GenerationRecord]] = []
        for record in self.list_records():
            submitted = record.submitted_at[: LABEL_CHARACTERS['TIME']].replace('T', ' ')
            label = LABEL_SEPARATOR.join((record.submit_id[: LABEL_CHARACTERS['SUBMIT_ID']], record.model, submitted))
            labeled.append((label, record))
        return labeled

    def find_record(self, label: str) -> GenerationRecord:
        """Return the newest record with this label; it compares whole labels, so two alike IDs stay apart."""
        record = next((record for name, record in self.list_labeled_records() if name == label), None)
        if record is None:
            raise DreaminaError(ErrorCode.INVALID_INPUT, GENERATION_UNKNOWN)
        return record


__all__ = ['GenerationStore']
