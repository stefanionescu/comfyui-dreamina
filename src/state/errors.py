"""Errors safe to show without exposing provider data."""

from enum import StrEnum


class ErrorCode(StrEnum):
    """Stable categories for the messages a person reads.

    Attributes:
        CONFIGURATION: The settings, the private state, or the setup of the extension is wrong.
        AUTHENTICATION: The sign-in or the credential store fails.
        CREDITS: The run costs more than the credit ceiling, or its price is unknown.
        INVALID_INPUT: An input of a node or of a request is wrong.
        REFUSED: Dreamina refuses the request.
        UNAVAILABLE: A model, a reference, or the region is not available.
        RATE_LIMITED: Dreamina limits how often the call may run.
        TIMEOUT: A call does not end within its time limit.
        TRANSPORT: The network fails, or a reply cannot be read.
        UNCERTAIN: The extension cannot tell whether Dreamina accepted the run.
        INTERRUPTED: A cancel stopped the wait while the generation keeps running.
        CONFLICT: The settings changed after the editor read them.
        MEDIA: A media file cannot be encoded or decoded.

    """

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
        """Store the complete message and its category.

        Args:
            code: The category of the error.
            message: The complete text a person reads.

        """
        super().__init__(message)
        self.code = code


class SubmissionAbsentError(DreaminaError):
    """A submission Dreamina keeps no record of; the extension deletes its record here and sends nothing again."""


__all__ = ['DreaminaError', 'ErrorCode', 'SubmissionAbsentError']
