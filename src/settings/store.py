"""Own the private settings and the account cache token outside ComfyUI's public storage."""

import hmac
import json
import hashlib
import secrets
import threading
from ..types import Json
from pathlib import Path
from dataclasses import asdict, fields
from ..config.settings import SETTING_RANGES
from ..storage.files import save_file, read_file
from ..config.security import ACCOUNT_TOKEN_BYTES
from ..types.errors import ErrorCode, DreaminaError
from ..types.settings import Settings, Configuration
from .schema import DEFAULT_SETTINGS, parse_settings
from ..config.storage import FILE_NAMES, MAX_FILE_BYTES
from ..types.parsing import parse_json, validate_fields
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

    def read_settings(self) -> Settings:
        """Read settings without creating files or directories; a save replaces the file whole, so no lock is needed."""
        path = self.directory / FILE_NAMES["SETTINGS"]
        if not path.exists():
            return DEFAULT_SETTINGS
        content = read_file(path, max_bytes=MAX_FILE_BYTES["SETTINGS"]).decode()
        return parse_settings(validate_fields(parse_json(content)))

    def read_snapshot(self) -> Configuration:
        """Read the settings and the account token together, refusing settings that cannot be read."""
        with self.lock:
            try:
                settings = self.read_settings()
            except (OSError, UnicodeError):
                raise DreaminaError(ErrorCode.CONFIGURATION, SETTINGS_UNREADABLE) from None
            return Configuration(settings, self._account, self._account_changes)

    def read_status(self) -> dict[str, Json]:
        """Describe the effective settings, their ranges, and their revision."""
        with self.lock:
            settings = self.read_settings()
        return {
            "settings": asdict(settings),
            "setting_ranges": {
                name: {"minimum": definition["minimum"], "maximum": definition["maximum"]}
                for name, definition in SETTING_RANGES.items()
            },
            "revision": settings.revision,
        }

    def save_settings(self, changes: dict[str, Json], revision: str) -> None:
        """Apply a validated patch only to the version the editor actually read."""
        if changes.keys() - EDITABLE_SETTINGS:
            raise DreaminaError(ErrorCode.CONFIGURATION, SETTING_READ_ONLY)
        with self.lock:
            current = self.read_settings()
            if revision != current.revision:
                raise DreaminaError(ErrorCode.CONFLICT, SETTINGS_CHANGED)
            updated = parse_settings(asdict(current) | changes)
            save_file(self.directory / FILE_NAMES["SETTINGS"], (json.dumps(asdict(updated), indent=2) + "\n").encode())

    def create_account_token(self, user_id: int, account_changes: int) -> str:
        """Build the account's cache token and keep it unless the account changed while it was read.

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


__all__ = ["ConfigurationStore"]
