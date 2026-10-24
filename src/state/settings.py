"""Execution settings and the snapshot each run reads."""

from dataclasses import dataclass


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


@dataclass(frozen=True, slots=True)
class Configuration:
    """One settings and account snapshot for one run.

    Attributes:
        settings: Effective execution limits.
        account: Token identifying the signed-in account in ComfyUI's cache; None until read in this process.
        account_changes: How many sign-ins and sign-outs this process had when it read the snapshot.

    """

    settings: Settings
    account: str | None
    account_changes: int


__all__ = ['Configuration', 'Settings']
