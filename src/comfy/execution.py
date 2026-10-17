"""Run Dreamina operations with ComfyUI's progress bar and its cancel."""

from __future__ import annotations

import asyncio
from functools import partial
from .runtime import get_runtime
from typing import TYPE_CHECKING
from comfy_api.latest import ComfyAPI
from ..types.errors import ErrorCode, DreaminaError
from ..config.execution import PROGRESS_STEPS, CANCELLATION_POLL_SECONDS
from comfy.model_management import throw_exception_if_processing_interrupted

if TYPE_CHECKING:
    from comfy_api.latest import io
    from collections.abc import Callable
    from ..dreamina.operation import Progress, Operation


async def _wait_shielded[T](task: asyncio.Task[T]) -> bool:
    """Wait until the task settles despite cancellation, and report whether cancellation arrived."""
    cancelled = False
    while not task.done():
        try:
            await asyncio.shield(task)
        except asyncio.CancelledError:
            cancelled = True
        except Exception:  # noqa: BLE001 -- reason: The caller reads the settled task's failure after resolving cancellation.
            break
    return cancelled


async def _wait_for_thread[T](work: Callable[[], T]) -> T:
    """Run blocking work in a thread, and finish it before letting a cancel through."""
    task = asyncio.create_task(asyncio.to_thread(work))
    if await _wait_shielded(task):
        task.exception()
        raise asyncio.CancelledError
    return task.result()


async def wait_for_run[T](task: asyncio.Task[T]) -> T:
    """Forward ComfyUI's cancel to the owned asyncio task that runs an operation.

    A cancel after Dreamina accepted the run ends the task with the message that the generation keeps running, which
    replaces ComfyUI's own interrupt, since ComfyUI shows no text for an interrupt.
    """
    try:
        while not task.done():
            throw_exception_if_processing_interrupted()
            await asyncio.wait({task}, timeout=CANCELLATION_POLL_SECONDS)
        return await task
    finally:
        if not task.done():
            task.cancel()
            outcomes = await asyncio.gather(task, return_exceptions=True)
            interrupted = [
                outcome
                for outcome in outcomes
                if isinstance(outcome, DreaminaError) and outcome.code is ErrorCode.INTERRUPTED
            ]
            if interrupted:
                raise interrupted[0]


async def send_run[Result](
    operation: Operation[Result], build_outputs: Callable[[Result], io.NodeOutput], node_id: str | None
) -> io.NodeOutput:
    """Validate, send, and build the node's outputs, showing only ComfyUI's progress bar.

    The bar is the node's own: a node that another node or pack calls has no ID, so it leaves the calling node's bar
    alone. The operation reports each step it reaches. Building the outputs decodes media, which blocks, so it runs in a
    worker thread.
    """
    progress: Progress | None = None
    if node_id is not None:
        progress = partial(ComfyAPI().execution.set_progress, max_value=PROGRESS_STEPS["TOTAL"], node_id=node_id)
        await progress(0)
    configuration = await asyncio.to_thread(get_runtime().configuration.read_snapshot)
    operation.validate(configuration.settings)
    result = await wait_for_run(asyncio.create_task(operation.send(configuration, progress)))
    outputs = await _wait_for_thread(lambda: build_outputs(result))
    if progress is not None:
        await progress(PROGRESS_STEPS["TOTAL"])
    return outputs


__all__ = ["send_run", "wait_for_run"]
