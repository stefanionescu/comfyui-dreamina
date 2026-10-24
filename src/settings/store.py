"""Own the private settings and the account cache token outside ComfyUI's public storage."""

import hmac
import json
import hashlib
from pathlib import Path
import secrets
import threading
from dataclasses import asdict, fields

from ..state import Json
from .schema import DEFAULT_SETTINGS, parse_settings
from ..state.errors import ErrorCode, DreaminaError
from ..state.parsing import parse_json, validate_fields
from ..storage.files import read_file, save_file
from ..config.storage import FILE_NAMES, MAX_FILE_BYTES
from ..state.settings import Settings, Configuration
from ..config.security import ACCOUNT_TOKEN_BYTES
from ..config.settings import SETTING_RANGES
from ..config.messages.settings import SETTINGS_CHANGED, SETTING_READ_ONLY, SETTINGS_UNREADABLE

EDITABLE_SETTINGS = frozenset(item.name for item in fields(Settings))


class ConfigurationStore:
    """Serialize local changes across server and executor threads."""

    def __init__(self, directory: Path) -> None:
        """Select private storage and own the lock for settings changes and the account token."""
        self.directory = directory
        self.lock = threading.Lock()
        # The signed-in account's cache token; None until read in this process, and after a sign-in or sign-out.
        self._account: str | None = None
        # A sign-in or sign-out counts here, so an account read that started before it never keeps the earlier
        # account's token.
        self._account_changes = 0
        self._account_key = secrets.token_bytes(ACCOUNT_TOKEN_BYTES)

    def _read_revised_settings(self) -> tuple[Settings, str]:
        """Read the settings and their revision, which identifies these non-secret settings.

        A window saves against the revision it read, so a stale window cannot overwrite newer changes.
        """
        settings = self.read_settings()
        encoded = json.dumps(asdict(settings), sort_keys=True, separators=(',', ':')).encode()
        return settings, hashlib.sha256(encoded).hexdigest()

    def read_settings(self) -> Settings:
        """Read settings without creating files or directories.

        A save replaces the file whole, so a read needs no lock.
        """
        path = self.directory / FILE_NAMES['SETTINGS']
        if not path.exists():
            return DEFAULT_SETTINGS
        content = read_file(path, max_bytes=MAX_FILE_BYTES['SETTINGS']).decode()
        return parse_settings(validate_fields(parse_json(content)))

    def read_configuration(self) -> Configuration:
        """Read the settings and the account token together, refusing unreadable settings."""
        with self.lock:
            try:
                settings = self.read_settings()
            except (OSError, UnicodeError):
                raise DreaminaError(ErrorCode.CONFIGURATION, SETTINGS_UNREADABLE) from None
            return Configuration(settings, self._account, self._account_changes)

    def read_status(self) -> dict[str, Json]:
        """Describe the effective settings, their ranges, and their revision."""
        with self.lock:
            settings, revision = self._read_revised_settings()
        return {
            'settings': asdict(settings),
            'setting_ranges': {
                name: {'minimum': definition['minimum'], 'maximum': definition['maximum']}
                for name, definition in SETTING_RANGES.items()
            },
            'revision': revision,
        }

    def save_settings(self, changes: dict[str, Json], revision: str) -> None:
        """Apply a validated patch only to the version the editor actually read."""
        if changes.keys() - EDITABLE_SETTINGS:
            raise DreaminaError(ErrorCode.CONFIGURATION, SETTING_READ_ONLY)
        with self.lock:
            current, current_revision = self._read_revised_settings()
            if revision != current_revision:
                raise DreaminaError(ErrorCode.CONFLICT, SETTINGS_CHANGED)
            updated = parse_settings(asdict(current) | changes)
            save_file(self.directory / FILE_NAMES['SETTINGS'], (json.dumps(asdict(updated), indent=2) + '\n').encode())

    def create_account_token(self, user_id: int, account_changes: int) -> str:
        """Build the account's cache token and keep it unless the account changed while the caller read it.

        The random key makes the token useless outside this process; the account ID itself is never stored.
        """
        token = hmac.new(self._account_key, str(user_id).encode(), hashlib.sha256).hexdigest()
        with self.lock:
            if account_changes == self._account_changes:
                self._account = token
        return token

    def reset_account_token(self) -> None:
        """Forget the account token after a sign-in or sign-out, so the next run reads the account again."""
        with self.lock:
            self._account = None
            self._account_changes += 1


__all__ = ['ConfigurationStore']
