"""Wait for one recorded generation, read its node, and download its outputs.

Generation: Download and the nodes that send a generation both collect through this module. None of its calls bills.
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING
import asyncio
from datetime import UTC, datetime, timedelta

from ..cli import parse_reply, send_command
from .waiting import wait_for_operation
from ..failures import build_failure, build_generation_failure
from ..downloads import download_resources
from ...state.runs import NodeView, NodeShowReply
from ...state.errors import ErrorCode, DreaminaError, SubmissionAbsentError
from ...config.dreamina import DREAMINA_URLS
from ...config.execution import PROGRESS_STEPS
from ...state.generations import GenerationRecord, GenerationResult
from ...config.generations import OPERATION_STATES, RECORD_RETENTION_SECONDS
from ...config.messages.run import CLI_FAILED
from ...config.messages.generations import (
    WAIT_LIMIT,
    GENERATION_GONE,
    GENERATION_EXPIRED,
    GENERATION_UNCOLLECTED,
    GENERATION_KEEPS_RUNNING,
)

if TYPE_CHECKING:
    from ...state import Json
    from .records import GenerationStore
    from ..operation import Progress
    from ...state.settings import Settings, Configuration
    from ...storage.canvas import CanvasStore


class CollectOperation:
    """Wait for one recorded generation, read its node, and download its outputs; none of it bills."""

    def __init__(
        self,
        record: GenerationRecord,
        generations: GenerationStore,
        canvas: CanvasStore,
        deadline: float | None = None,
        request_id: str | None = None,
    ) -> None:
        """Keep the record, the stores, the sending run's deadline, and its request ID for result.

        Args:
            record: The generation to collect.
            generations: The store that holds the generation records.
            canvas: The store that holds the saved canvas.
            deadline: The monotonic deadline of the run that sent the generation, or None to count from now.
            request_id: The request ID of the run call, or None when there is none.

        """
        self.record = record
        self.generations = generations
        self.canvas = canvas
        self.deadline = deadline
        self.request_id = request_id

    async def _wait_for_success(self, deadline: float, progress: Progress | None, settings: Settings) -> None:
        """Wait until the generation ends with at least one output; its own failure deletes the record.

        A failed wait keeps the record, so the person can still collect the generation after a sign-out or an update
        during the wait.

        Args:
            deadline: The monotonic time at which the wait gives up.
            progress: The callback that reports the running step, or None.
            settings: The settings, whose timeout the wait limit message shows.

        Raises:
            DreaminaError: When the wait fails or passes its deadline.
            SubmissionAbsentError: When Dreamina keeps no record of the submission.
            build_generation_failure: When the generation ended with no successful output.

        """
        record = self.record
        try:
            reply = await wait_for_operation(record.submit_id, record.project_id, deadline, progress)
        except SubmissionAbsentError:
            await asyncio.to_thread(self.generations.delete, record.submit_id)
            raise
        except DreaminaError as error:
            raise DreaminaError(error.code, GENERATION_UNCOLLECTED.format(reason=str(error))) from None
        if reply is None:
            raise DreaminaError(ErrorCode.TIMEOUT, WAIT_LIMIT.format(seconds=settings.request_timeout_seconds))
        if not any(resource.state == OPERATION_STATES['SUCCEEDED'] for resource in reply.resources):
            await asyncio.to_thread(self.generations.delete, record.submit_id)
            raise build_generation_failure(reply)

    async def _read_node(self, deadline: float) -> dict[str, Json]:
        """Read the generation's canvas node as Dreamina returns it; a missing node deletes the record.

        Args:
            deadline: The monotonic time by which the show call must end.

        Returns:
            The node as the JSON object Dreamina returns.

        Raises:
            DreaminaError: When the node cannot be read, or Dreamina does not have it.
            build_failure: When the CLI refuses the show call.

        """
        record = self.record
        arguments = ('node', 'show', '--project-id', record.project_id, '--node-id', record.node_id)
        try:
            result = await send_command(arguments, max(deadline - time.monotonic(), 1.0))
            if not result.reply.ok:
                raise build_failure(result, CLI_FAILED)
            nodes = parse_reply(result.reply.payload, NodeShowReply).nodes
        except DreaminaError as error:
            raise DreaminaError(error.code, GENERATION_UNCOLLECTED.format(reason=str(error))) from None
        node = nodes[0].node if nodes else None
        if node is None:
            await asyncio.to_thread(self.generations.delete, record.submit_id)
            raise DreaminaError(ErrorCode.UNAVAILABLE, GENERATION_GONE)
        return node

    async def _read_canvas_url(self) -> str | None:
        """Return the saved canvas's page when the record's canvas is the saved one.

        Returns:
            The web address of the saved canvas, or None when no canvas is saved or the record belongs to another one.

        """
        saved = await asyncio.to_thread(self.canvas.read)
        if saved is None or saved.project_id != self.record.project_id:
            return None
        return saved.web_url

    async def send(self, configuration: Configuration, progress: Progress | None) -> GenerationResult:
        """Wait for the generation, read its node, and download its outputs, then delete the record.

        The record goes only after every download, so the person can collect a failed download again. A cancel leaves
        the record for Generation: Download.

        Args:
            configuration: The configuration, whose settings give the timeout and the download limit.
            progress: The callback that reports each step, or None.

        Returns:
            The record, its node, the node's title, the files, the canvas page, and the request ID.

        Raises:
            DreaminaError: When the record is past its retention, or a cancel stops the collection.

        """
        record = self.record
        settings = configuration.settings
        deadline = self.deadline if self.deadline is not None else time.monotonic() + settings.request_timeout_seconds
        expiry = datetime.fromisoformat(record.submitted_at) + timedelta(seconds=RECORD_RETENTION_SECONDS)
        if datetime.now(UTC) >= expiry:
            await asyncio.to_thread(self.generations.delete, record.submit_id)
            raise DreaminaError(ErrorCode.UNAVAILABLE, GENERATION_EXPIRED.format(**DREAMINA_URLS))
        try:
            await self._wait_for_success(deadline, progress, settings)
            node = await self._read_node(deadline)
            view = parse_reply(node, NodeView)
            files = await download_resources(record.project_id, view, record.submit_id, settings, deadline)
        except asyncio.CancelledError as error:
            raise DreaminaError(ErrorCode.INTERRUPTED, GENERATION_KEEPS_RUNNING) from error
        if progress is not None:
            await progress(PROGRESS_STEPS['DOWNLOADED'])
        await asyncio.to_thread(self.generations.delete, record.submit_id)
        return GenerationResult(record, node, view.title, files, await self._read_canvas_url(), self.request_id)


__all__ = ['CollectOperation']
