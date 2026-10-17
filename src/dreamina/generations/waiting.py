"""Wait for one accepted generation with short read-only waits, and check a run whose reply was lost.

Each call here is free and safe to repeat; a cancel kills it at once.
"""

from __future__ import annotations

import time
import asyncio
from ..failures import build_failure
from pydantic import ValidationError
from typing import NoReturn, TYPE_CHECKING
from ...types.replies import OperationReply
from ..cli import parse_reply, send_command
from ...config.messages.run import CLI_FAILED
from ...config.execution import PROGRESS_STEPS
from ...types.errors import ErrorCode, DreaminaError
from ...config.generations import OPERATION_STATES, WAIT_REREAD_SECONDS
from ...config.messages.generations import RUN_UNCERTAIN, RUN_UNRECORDED
from ...config.dreamina import EXIT_CODES, WAIT_SLICE, CALL_SECONDS, DREAMINA_URLS

if TYPE_CHECKING:
    from ..operation import Progress


async def wait_for_operation(
    submit_id: str, project_id: str, deadline: float, progress: Progress | None
) -> OperationReply | None:
    """Wait for a generation to end, one short wait after another; None once the deadline passed.

    Exit 20 is the normal answer while the generation runs. A reply that cannot be read is read again after a pause,
    so a broken CLI does not spin.
    """
    arguments = ("operation", "wait", submit_id, "--project-id", project_id, "--timeout", WAIT_SLICE)
    is_running = False
    while (remaining := deadline - time.monotonic()) > 0:
        try:
            result = await send_command(arguments, min(remaining, CALL_SECONDS["WAIT"]))
        except DreaminaError as error:
            if error.code is not ErrorCode.TRANSPORT:
                raise
            await asyncio.sleep(WAIT_REREAD_SECONDS)
            continue
        if result.exit_code == EXIT_CODES["INCOMPLETE"]:
            if progress is not None and not is_running:
                await progress(PROGRESS_STEPS["RUNNING"])
            is_running = True
        elif result.exit_code != EXIT_CODES["OK"]:
            raise build_failure(result, CLI_FAILED)
        else:
            try:
                return OperationReply.model_validate(result.reply.payload)
            except ValidationError:
                await asyncio.sleep(WAIT_REREAD_SECONDS)
    return None


async def validate_lost_run(submit_id: str, project_id: str) -> NoReturn:
    """Ask once, read-only, whether Dreamina knows a run whose reply was lost, and stop with what it says.

    The run call is never sent again. No record is kept either way, because the status names no canvas node.
    """
    arguments = ("operation", "status", submit_id, "--project-id", project_id)
    try:
        result = await send_command(arguments, CALL_SECONDS["READ"])
        reply = parse_reply(result.reply.payload, OperationReply) if result.exit_code == EXIT_CODES["OK"] else None
    except DreaminaError:
        raise DreaminaError(ErrorCode.UNCERTAIN, RUN_UNCERTAIN.format(**DREAMINA_URLS)) from None
    submission = reply.submission if reply is not None else None
    is_known = result.exit_code == EXIT_CODES["INCOMPLETE"] or (
        reply is not None and (submission is None or submission.state != OPERATION_STATES["ABSENT"])
    )
    raise DreaminaError(ErrorCode.UNCERTAIN, (RUN_UNRECORDED if is_known else RUN_UNCERTAIN).format(**DREAMINA_URLS))


__all__ = ["validate_lost_run", "wait_for_operation"]
