"""Run Dreamina operations with ComfyUI's progress bar and its cancel."""

from __future__ import annotations

from typing import TYPE_CHECKING
import asyncio
from functools import partial

from comfy_api.latest import ComfyAPI
from comfy.model_management import throw_exception_if_processing_interrupted

from .runtime import get_runtime
from ..config.execution import PROGRESS_STEPS, CANCELLATION_POLL_SECONDS

if TYPE_CHECKING:
    from collections.abc import Callable, Coroutine

    from comfy_api.latest import io

    from ..state.settings import Configuration
    from ..dreamina.operation import Progress


async def _wait_shielded[T](task: asyncio.Task[T]) -> bool:
    """Wait until the task settles despite cancellation, and report whether cancellation arrived."""
    cancelled = False
    while not task.done():
        try:
            await asyncio.shield(task)
        except asyncio.CancelledError:
            cancelled = True
        except Exception:  # noqa: BLE001 # reason: The caller reads the settled task's failure after resolving cancellation.
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
    """Pass ComfyUI's cancel to the owned asyncio task that runs an operation, wait for it, then let the cancel through.

    ComfyUI's interrupt reaches ComfyUI, which then stops the prompt before its next node. A run that Dreamina accepted
    keeps running and Dreamina bills it; Generation: Download collects it.
    """
    try:
        while not task.done():
            throw_exception_if_processing_interrupted()
            await asyncio.wait({task}, timeout=CANCELLATION_POLL_SECONDS)
        return await task
    finally:
        if not task.done():
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)


async def send_run[Result](
    operation: Callable[[Configuration, Progress | None], Coroutine[object, object, Result]],
    build_outputs: Callable[[Result], io.NodeOutput],
    node_id: str | None,
) -> io.NodeOutput:
    """Send the operation and build the outputs of the node, showing only ComfyUI's progress bar.

    The operation sends one Dreamina operation, reports each step it reaches, and returns its result.

    The bar belongs to the node itself: a node that another node or pack calls has no ID, so it leaves the bar of the
    calling node alone. The operation reports each step it reaches. Building the outputs decodes media, which blocks, so
    it runs in a worker thread.
    """
    progress: Progress | None = None
    if node_id is not None:
        progress = partial(ComfyAPI().execution.set_progress, max_value=PROGRESS_STEPS['TOTAL'], node_id=node_id)
        await progress(0)
    configuration = await asyncio.to_thread(get_runtime().configuration.read_configuration)
    result = await wait_for_run(asyncio.create_task(operation(configuration, progress)))
    outputs = await _wait_for_thread(lambda: build_outputs(result))
    if progress is not None:
        await progress(PROGRESS_STEPS['TOTAL'])
    return outputs


__all__ = ['send_run', 'wait_for_run']
