"""Errors safe to show without exposing provider data."""

from enum import StrEnum


class ErrorCode(StrEnum):
    """Stable categories for the messages a person reads."""

    CONFIGURATION = 'configuration'
    AUTHENTICATION = 'authentication'
    CREDITS = 'credits'
    INVALID_INPUT = 'invalid_input'
    REFUSED = 'refused'
    UNAVAILABLE = 'unavailable'
    RATE_LIMITED = 'rate_limited'
    TIMEOUT = 'timeout'
    TRANSPORT = 'transport'
    UNCERTAIN = 'uncertain'
    INTERRUPTED = 'interrupted'
    CONFLICT = 'conflict'
    MEDIA = 'media'


class DreaminaError(RuntimeError):
    """Show reviewed text; the CLI's cleaned reason, when there is one, is already part of it."""

    def __init__(self, code: ErrorCode, message: str) -> None:
        """Store the complete message and its category."""
        super().__init__(message)
        self.code = code


class SubmissionAbsentError(DreaminaError):
    """A submission Dreamina keeps no record of; the extension deletes its record here and sends nothing again."""


__all__ = ['DreaminaError', 'ErrorCode', 'SubmissionAbsentError']
