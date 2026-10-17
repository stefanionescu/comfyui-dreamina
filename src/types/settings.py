"""Execution settings and the snapshot each run reads."""

import json
import hashlib
from dataclasses import asdict, dataclass


@dataclass(frozen=True, slots=True)
class Settings:
    """Limits that a workflow cannot raise.

    Attributes:
        request_timeout_seconds: How long one run may take, from the first upload to the last download.
        max_upload_megabytes: Largest single file uploaded to Dreamina.
        max_download_megabytes: Largest single output file accepted.

    """

    request_timeout_seconds: int
    max_upload_megabytes: int
    max_download_megabytes: int

    @property
    def revision(self) -> str:
        """Identify these non-secret settings so a stale window cannot overwrite newer changes."""
        encoded = json.dumps(asdict(self), sort_keys=True, separators=(",", ":")).encode()
        return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class Configuration:
    """One settings and account snapshot for one run.

    Attributes:
        settings: Effective execution limits.
        account: Token identifying the signed-in account in ComfyUI's cache; None until read in this process.
        account_changes: How many sign-ins and sign-outs this process had when the snapshot was read.

    """

    settings: Settings
    account: str | None
    account_changes: int


__all__ = ["Configuration", "Settings"]
