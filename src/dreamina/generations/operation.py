"""Run one generation with one call, record it as soon as Dreamina accepts it, then wait, read its node, and download.

Dreamina has no cancel for a generation it accepted. A cancel stops the wait, and the record stays for Generation:
Download.
"""

from __future__ import annotations

import time
import uuid
import asyncio
from ..models import find_model
from ..modes import choose_mode
from ..uploads import send_media
from typing import TYPE_CHECKING
from ..contract import validate_cli
from ..failures import build_failure
from ..downloads import download_resources
from ..operation import wait_until_settled
from ..cli import parse_reply, send_command
from datetime import UTC, datetime, timedelta
from ...config.execution import PROGRESS_STEPS
from ..canvas import find_canvas, create_canvas
from ..failures import build_generation_failure
from ...types.errors import ErrorCode, DreaminaError
from ...config.messages.run import CLI_FAILED, RUN_REFUSED
from .waiting import validate_lost_run, wait_for_operation
from ...types.replies import RunReply, NodeView, NodeShowReply
from ...types.generations import RunCall, GenerationRecord, GenerationResult
from ..references import format_prompt, plan_references, validate_references
from ...config.dreamina import EXIT_CODES, CALL_SECONDS, DREAMINA_URLS, ACCEPTED_PHASE
from ...config.generations import RECORD_VERSION, OPERATION_STATES, RECORD_RETENTION_SECONDS
from ..arguments import build_flags, choose_prompt, parse_arguments, validate_argument_names
from ...config.messages.generations import (
    WAIT_LIMIT,
    RUN_UNRECORDED,
    GENERATION_GONE,
    GENERATION_ABSENT,
    GENERATION_EXPIRED,
    GENERATION_UNCOLLECTED,
    GENERATION_KEEPS_RUNNING,
)

if TYPE_CHECKING:
    from pathlib import Path
    from ...types import Json
    from ..operation import Progress
    from ...types.cli import CliResult
    from .records import GenerationStore
    from collections.abc import Callable
    from ...storage.canvas import CanvasStore
    from ...types.references import LocalMedia
    from ...types.generations import GenerationPlan
    from ...types.models import ModelMode, ListedModel
    from ...types.settings import Settings, Configuration


async def _read_node_id(result: CliResult, call: RunCall) -> str:
    """Read the node of a run Dreamina accepted, or stop: a refusal is raised, and a lost reply is checked read-only.

    Exit 0 and exit 20 follow acceptance, and so does a failure of the CLI's own records after the submit; every
    other failure means the run did not start.
    """
    reply = result.reply
    if result.exit_code == EXIT_CODES["OK"]:
        try:
            return parse_reply(reply.payload, RunReply).node.node_id
        except DreaminaError:
            await validate_lost_run(call.submit_id, call.project_id)
    storage = reply.error.local_storage if reply.error is not None else None
    phase = storage.submission_phase if storage is not None else None
    if result.exit_code != EXIT_CODES["INCOMPLETE"] and phase != ACCEPTED_PHASE:
        raise build_failure(result, RUN_REFUSED, credit_ceiling=call.credit_ceiling)
    items = reply.partial.items if reply.partial is not None else ()
    node_id = next((item.node_id for item in items if item.submit_id == call.submit_id and item.node_id), None)
    if node_id is None:
        raise DreaminaError(ErrorCode.UNCERTAIN, RUN_UNRECORDED.format(**DREAMINA_URLS))
    return node_id


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
        """Keep the record, the stores, the sending run's deadline, and its request ID for result."""
        self.record = record
        self.generations = generations
        self.canvas = canvas
        self.deadline = deadline
        self.request_id = request_id

    async def _wait_for_success(self, deadline: float, progress: Progress | None, settings: Settings) -> None:
        """Wait until the generation ends with at least one output; its own failure deletes the record.

        A failed wait keeps the record, so a sign-out or an update during the wait can still be collected.
        """
        record = self.record
        try:
            reply = await wait_for_operation(record.submit_id, record.project_id, deadline, progress)
        except DreaminaError as error:
            raise DreaminaError(error.code, GENERATION_UNCOLLECTED.format(reason=str(error))) from None
        if reply is None:
            raise DreaminaError(ErrorCode.TIMEOUT, WAIT_LIMIT.format(seconds=settings.request_timeout_seconds))
        if reply.submission is not None and reply.submission.state == OPERATION_STATES["ABSENT"]:
            await asyncio.to_thread(self.generations.delete, record.submit_id)
            raise DreaminaError(ErrorCode.UNAVAILABLE, GENERATION_ABSENT.format(**DREAMINA_URLS))
        if not any(resource.state == OPERATION_STATES["SUCCEEDED"] for resource in reply.resources):
            await asyncio.to_thread(self.generations.delete, record.submit_id)
            raise build_generation_failure(reply)

    async def _read_node(self, deadline: float) -> dict[str, Json]:
        """Read the generation's canvas node as Dreamina returns it; a node no longer there deletes the record."""
        record = self.record
        arguments = ("node", "show", "--project-id", record.project_id, "--node-id", record.node_id)
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
        """Return the saved canvas's page when the record's canvas is the saved one."""
        saved = await asyncio.to_thread(self.canvas.read)
        if saved is None or saved.project_id != self.record.project_id:
            return None
        return saved.web_url

    def validate(self, settings: Settings) -> None:
        """Accept every record; there is nothing to refuse before reading its status."""

    async def send(self, configuration: Configuration, progress: Progress | None) -> GenerationResult:
        """Wait for the generation, read its node, and download its outputs, then delete the record.

        The record goes only after every download, so a failed download can be collected again. A cancel leaves the
        record for Generation: Download.
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
            await progress(PROGRESS_STEPS["DOWNLOADED"])
        await asyncio.to_thread(self.generations.delete, record.submit_id)
        return GenerationResult(record, node, view.title, files, await self._read_canvas_url(), self.request_id)


class GenerationOperation:
    """One generation, sent with one run call and recorded as soon as Dreamina accepts it."""

    def __init__(
        self,
        plan: GenerationPlan,
        generations: GenerationStore,
        canvas: CanvasStore,
        encode: Callable[[LocalMedia, Path], Path],
    ) -> None:
        """Keep the node's plan, the stores, and ComfyUI's encoder, which the node passes in.

        The encoder is ComfyUI's, since this package may not import ComfyUI.
        """
        self.plan = plan
        self.generations = generations
        self.canvas = canvas
        self.encode = encode

    async def _plan_run(self) -> tuple[ListedModel, ModelMode, str, tuple[str, ...]]:
        """Refuse locally everything the live model list says Dreamina would refuse, and build the flags."""
        plan = self.plan
        await validate_cli()
        values = parse_arguments(plan.arguments)
        listed = await find_model(plan.model, plan.kind)
        validate_argument_names(listed, values)
        items = (*plan.references, *plan.local)
        mode = choose_mode(listed, plan.kind, tuple(item.media for item in items), values)
        prompt = choose_prompt(plan.prompt, values)
        flags = build_flags(mode, prompt, values)
        validate_references(mode, items, values)
        return listed, mode, prompt, flags

    async def _send_media(
        self, configuration: Configuration, deadline: float, prompt: str
    ) -> tuple[str, tuple[str, ...]]:
        """Find or create the canvas, upload the local media, and write the prompt or title and each --ref."""
        plan = self.plan
        canvas = await find_canvas(self.canvas) or await create_canvas(self.canvas)
        uploaded = await send_media(canvas.project_id, plan.local, self.encode, configuration.settings, deadline)
        ordered, placed = plan_references(plan.references, plan.local, uploaded)
        text = ("--prompt", format_prompt(prompt, placed)) if prompt else ("--title", plan.title)
        return canvas.project_id, (*text, *(item for reference in ordered for item in ("--ref", reference.typed_value)))

    async def _build_call(self, configuration: Configuration, deadline: float, progress: Progress | None) -> RunCall:
        """Check, upload, and build the run call; a cancel here stops the run with nothing sent to the model."""
        listed, mode, prompt, flags = await self._plan_run()
        if progress is not None:
            await progress(PROGRESS_STEPS["CHECKED"])
        project_id, sources = await self._send_media(configuration, deadline, prompt)
        if progress is not None:
            await progress(PROGRESS_STEPS["UPLOADED"])
        return RunCall(
            kind=self.plan.kind,
            project_id=project_id,
            model=listed.name,
            mode=mode.name,
            flags=flags,
            sources=sources,
            credit_ceiling=self.plan.credit_ceiling,
            submit_id=str(uuid.uuid4()),
        )

    async def _send_run(self, call: RunCall) -> tuple[GenerationRecord, str | None]:
        """Send the run call once, with its own time limit, and record an accepted run before anything waits for it."""
        submitted_at = datetime.now(UTC).isoformat()
        try:
            result = await send_command(call.arguments, CALL_SECONDS["RUN"])
        except DreaminaError as error:
            if error.code is ErrorCode.TRANSPORT:
                await validate_lost_run(call.submit_id, call.project_id)
            raise
        record = GenerationRecord(
            version=RECORD_VERSION,
            submit_id=call.submit_id,
            project_id=call.project_id,
            node_id=await _read_node_id(result, call),
            kind=call.kind,
            model=call.model,
            mode=call.mode,
            submitted_at=submitted_at,
        )
        await asyncio.to_thread(self.generations.save, record)
        return record, result.reply.meta.request_id if result.reply.meta is not None else None

    def validate(self, settings: Settings) -> None:
        """Accept every plan: each check needs the model, which send reads after the CLI check."""

    async def send(self, configuration: Configuration, progress: Progress | None) -> GenerationResult:
        """Check, upload, send the run once, record it, then wait for it and collect what it made.

        Every refusal comes before anything leaves the computer, and the run call is the last step that can bill. A
        cancel during the run call waits for its answer, so an accepted run is always recorded.
        """
        deadline = time.monotonic() + configuration.settings.request_timeout_seconds
        call = await self._build_call(configuration, deadline, progress)
        running = asyncio.create_task(self._send_run(call))
        is_cancelled = await wait_until_settled(running)
        record, request_id = running.result()
        if is_cancelled:
            raise DreaminaError(ErrorCode.INTERRUPTED, GENERATION_KEEPS_RUNNING)
        if progress is not None:
            await progress(PROGRESS_STEPS["ACCEPTED"])
        collect = CollectOperation(record, self.generations, self.canvas, deadline, request_id)
        return await collect.send(configuration, progress)


__all__ = ["CollectOperation", "GenerationOperation"]
