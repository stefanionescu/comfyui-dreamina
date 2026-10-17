"""Turn the Dreamina CLI's failure replies into reviewed messages, reading structured fields only.

The CLI's message text is never matched; it is shown, cleaned, only where no field names the cause.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING
from ..types.cli import CliFailure
from ..config.patterns import REASON_PATTERNS
from ..config.generations import OPERATION_STATES
from ..types.errors import ErrorCode, DreaminaError
from ..config.dreamina import EXIT_CODES, DREAMINA_URLS, REASON_ENDINGS, MAX_REASON_CHARACTERS
from ..config.messages.generations import GENERATION_EMPTY, GENERATION_FAILED, STATUS_CODE_REASON
from ..config.messages.run import (
    NO_REASON,
    DNS_FAILED,
    FLAG_REFUSED,
    MODE_REQUIRED,
    PRICE_UNKNOWN,
    NETWORK_DENIED,
    TITLE_REQUIRED,
    CEILING_TOO_LOW,
    NETWORK_TIMEOUT,
    SIGN_IN_LIMITED,
    SIGN_IN_REQUIRED,
    UPGRADE_REQUIRED,
    REFERENCE_REFUSED,
    CREDENTIALS_DENIED,
    LOCAL_STATE_FAILED,
    REGION_UNAVAILABLE,
    OPERATION_INCOMPLETE,
    REFERENCE_UNAVAILABLE,
    CREDENTIALS_UNREADABLE,
)

if TYPE_CHECKING:
    from ..types.replies import OperationReply
    from ..types.cli import CliResult, Validation

_URL = re.compile(REASON_PATTERNS["URL"])
_PATH = re.compile(REASON_PATTERNS["PATH"])
_IDENTIFIER = re.compile(REASON_PATTERNS["IDENTIFIER"])

# The causes the CLI names in error.reason, each a finer cause than the class it comes with.
_REASON_FAILURES: dict[str, tuple[ErrorCode, str]] = {
    "dns_resolution_failed": (ErrorCode.TRANSPORT, DNS_FAILED),
    "network_permission_denied": (ErrorCode.TRANSPORT, NETWORK_DENIED),
    "network_timeout": (ErrorCode.TRANSPORT, NETWORK_TIMEOUT),
    "credential_store_permission_denied": (ErrorCode.AUTHENTICATION, CREDENTIALS_DENIED),
    "credential_store_unavailable": (ErrorCode.AUTHENTICATION, CREDENTIALS_UNREADABLE),
    "credential_store_corrupt": (ErrorCode.AUTHENTICATION, CREDENTIALS_UNREADABLE),
}

# The error codes with a fix of their own, each a finer cause than its exit code.
_CODE_FAILURES: dict[str, tuple[ErrorCode, str]] = {
    "cli.generation_mode_required": (ErrorCode.INVALID_INPUT, MODE_REQUIRED),
    "cli.generation_title_required": (ErrorCode.INVALID_INPUT, TITLE_REQUIRED),
    "cli.invalid_flag": (ErrorCode.INVALID_INPUT, FLAG_REFUSED),
    "cli.invalid_resource_reference": (ErrorCode.INVALID_INPUT, REFERENCE_REFUSED),
    "cli.resource_unavailable": (ErrorCode.UNAVAILABLE, REFERENCE_UNAVAILABLE),
    "cli.region_not_available": (ErrorCode.UNAVAILABLE, REGION_UNAVAILABLE),
    "cli.passport_rate_limited": (ErrorCode.RATE_LIMITED, SIGN_IN_LIMITED),
}


def _choose_reason(validation: Validation | None, message: str) -> str:
    """Name the refused field with the CLI's detail for it, or give the CLI's message when no value was refused."""
    if validation is None:
        return message
    return f"{validation.field_path}: {validation.detail}" if validation.field_path else validation.detail


def _choose_failure(exit_code: int, failure: CliFailure, context: str) -> tuple[ErrorCode, str]:
    """Pick the code and message after the quote's row; the first row that matches decides, and context is the last.

    An upgrade comes before sign-in, because neither is retried and the upgrade is what the person can fix. The CLI's
    own records and the credential store come before sign-in too, since signing in again would not help.
    """
    action, failure_class = failure.required_action, failure.failure_class
    is_sign_in = exit_code == EXIT_CODES["SIGN_IN"] or action == "login" or failure_class == "auth_required"
    is_incomplete = (
        exit_code == EXIT_CODES["INCOMPLETE"] or action == "resume" or failure_class == "operation_incomplete"
    )
    is_invalid = exit_code == EXIT_CODES["INVALID"] or failure_class == "invalid_input"
    rows = (
        (ErrorCode.CONFIGURATION, UPGRADE_REQUIRED) if action == "upgrade" else None,
        (ErrorCode.CONFIGURATION, LOCAL_STATE_FAILED) if failure.local_storage is not None else None,
        _REASON_FAILURES.get(failure.reason or ""),
        (ErrorCode.AUTHENTICATION, SIGN_IN_REQUIRED) if is_sign_in else None,
        _CODE_FAILURES.get(failure.code),
        (ErrorCode.TRANSPORT, OPERATION_INCOMPLETE) if is_incomplete else None,
        (ErrorCode.INVALID_INPUT, context) if is_invalid else None,
    )
    return next((row for row in rows if row is not None), (ErrorCode.TRANSPORT, context))


def sanitize_reason(text: str) -> str:
    """Remove links, file paths, and identifier-shaped text, then shorten the rest.

    Links go first, so the path pattern never meets one. The reason ends as a sentence, because a message adds its
    next step after it.
    """
    text = _PATH.sub("", _URL.sub("", text))
    text = " ".join(_IDENTIFIER.sub("", text).split())
    if len(text) > MAX_REASON_CHARACTERS:
        text = text[: MAX_REASON_CHARACTERS - 1].rstrip() + "…"
    if text and not text.endswith(REASON_ENDINGS):
        text += "."
    return text or NO_REASON


def build_failure(result: CliResult, context: str, *, credit_ceiling: int | None = None) -> DreaminaError:
    """Build the reviewed error for one failure reply, with the CLI's cleaned reason where no field names the cause.

    context is the caller's message for an invalid input or a failure no field names. A stop at the quote names the
    run's credit ceiling. A template without a placeholder drops that value. A failure reply without an error object
    reads as one whose fields are all empty.
    """
    failure = result.reply.error or CliFailure()
    if result.exit_code == EXIT_CODES["CONFIRM"] or failure.required_action == "confirm":
        confirmation = result.reply.credit_confirmation
        minimum = confirmation.minimum_credit_ceiling if confirmation is not None else None
        template = PRICE_UNKNOWN if minimum is None else CEILING_TOO_LOW
        return DreaminaError(ErrorCode.CREDITS, template.format(minimum=minimum, ceiling=credit_ceiling))
    code, template = _choose_failure(result.exit_code, failure, context)
    reason = sanitize_reason(_choose_reason(failure.validation, failure.message))
    return DreaminaError(code, template.format(reason=reason, **DREAMINA_URLS))


def build_generation_failure(reply: OperationReply) -> DreaminaError:
    """Build the error of a generation that ended with no successful output, from Dreamina's fields only.

    An empty resource set is not a success, so a run that made nothing says so.
    """
    error = reply.submission_error
    if error is not None:
        text = _choose_reason(error.validation, error.message).strip()
        if not text and error.status_code is not None:
            text = STATUS_CODE_REASON.format(code=error.status_code)
        return DreaminaError(ErrorCode.INVALID_INPUT, GENERATION_FAILED.format(reason=sanitize_reason(text)))
    code = next(
        (
            resource.status_code
            for resource in reply.resources
            if resource.state != OPERATION_STATES["SUCCEEDED"] and resource.status_code is not None
        ),
        None,
    )
    if code is not None:
        return DreaminaError(
            ErrorCode.INVALID_INPUT, GENERATION_FAILED.format(reason=STATUS_CODE_REASON.format(code=code))
        )
    return DreaminaError(ErrorCode.INVALID_INPUT, GENERATION_EMPTY)


__all__ = ["build_failure", "build_generation_failure", "sanitize_reason"]
