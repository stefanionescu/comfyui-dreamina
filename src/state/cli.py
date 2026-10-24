"""The envelope every Dreamina CLI reply has, and the result of one call; the records ignore unknown fields."""

from dataclasses import dataclass

from pydantic import Field

from . import Json, Reply


class Validation(Reply):
    """Which value the CLI refused, and why.

    Attributes:
        reason_code: The CLI's machine name for the refusal.
        field_path: The refused field, when the refusal names one.
        detail: The CLI's text for a person, which the extension shows and never matches.

    """

    reason_code: str = Field(default='', alias='reasonCode')
    field_path: str | None = Field(default=None, alias='fieldPath')
    detail: str = ''


class LocalStorage(Reply):
    """A failure of the CLI's own records on this computer.

    Attributes:
        submission_phase: When it failed; after_submit means Dreamina already accepted the run.

    """

    submission_phase: str | None = Field(default=None, alias='submissionPhase')


class CliFailure(Reply):
    """The error object of a failure reply.

    Attributes:
        code: The CLI's stable error code, such as cli.invalid_flag.
        failure_class: The error's class, such as invalid_input.
        message: The CLI's English text, shown cleaned where no field names the cause.
        reason: A finer cause, such as network_timeout.
        retryable: Whether the CLI says the extension may send the same call again.
        required_action: What the CLI says must happen next, such as `login` or `upgrade`.
        validation: The refused value, for an invalid input.
        local_storage: The CLI's own record failure, when it is one.

    """

    code: str = ''
    failure_class: str = Field(default='', alias='class')
    message: str = ''
    reason: str | None = None
    retryable: bool = False
    required_action: str | None = Field(default=None, alias='requiredAction')
    validation: Validation | None = None
    local_storage: LocalStorage | None = Field(default=None, alias='localStorage')


class CreditConfirmation(Reply):
    """Dreamina's quote when a run stops at its credit ceiling.

    Attributes:
        reason: Why the run stopped, such as ceiling_too_low.
        minimum_credit_ceiling: The smallest credit ceiling that runs it; None when the price is unknown.

    """

    reason: str = ''
    minimum_credit_ceiling: int | None = Field(default=None, alias='minimumCreditCeiling')


class PartialItem(Reply):
    """One item the CLI made before it stopped.

    Attributes:
        node_id: The canvas node it saved.
        submit_id: The run's submit ID.
        source_node_id: The node an upscale started from.

    """

    node_id: str | None = Field(default=None, alias='nodeId')
    submit_id: str | None = Field(default=None, alias='submitId')
    source_node_id: str | None = Field(default=None, alias='sourceNodeId')


class PartialRun(Reply):
    """What a failed call had already made.

    Attributes:
        items: Each node and run it made.

    """

    items: tuple[PartialItem, ...] = ()


class CliMeta(Reply):
    """What every reply says about the call itself.

    Attributes:
        request_id: Dreamina's ID for the call, kept for support.

    """

    request_id: str | None = Field(default=None, alias='requestId')


class CliReply(Reply):
    """One reply: a success or a failure.

    Attributes:
        schema_version: The reply format.
        ok: Whether the call succeeded.
        payload: The success reply's content, read by each caller into its own record.
        error: The failure, when ok is false.

        credit_confirmation: The quote of a run that stopped at its ceiling.
        partial: What a failed call had already made.
        meta: What the reply says about the call.

    """

    schema_version: str = Field(alias='schemaVersion')
    ok: bool
    payload: Json = Field(default=None, alias='data')
    error: CliFailure | None = None
    credit_confirmation: CreditConfirmation | None = Field(default=None, alias='creditConfirmation')
    partial: PartialRun | None = Field(default=None, alias='partialData')
    meta: CliMeta | None = None


@dataclass(frozen=True, slots=True)
class CliResult:
    """One finished call.

    Attributes:
        exit_code: The process's exit code.
        reply: Its one reply; the success JSON is reply.payload.

    """

    exit_code: int
    reply: CliReply


__all__ = [
    'CliFailure',
    'CliMeta',
    'CliReply',
    'CliResult',
    'CreditConfirmation',
    'LocalStorage',
    'PartialItem',
    'PartialRun',
    'Validation',
]
