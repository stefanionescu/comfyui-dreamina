"""Run one generation with one call, record it as soon as Dreamina accepts it, then wait, read its node, and download.

Dreamina has no cancel for a generation it accepted. A cancel stops the wait, and the record stays for Generation:
Download.
"""

from __future__ import annotations

import time
import uuid
from typing import TYPE_CHECKING
import asyncio
from datetime import UTC, datetime

from ..cli import parse_reply, send_command
from ..modes import choose_mode
from ..canvas import find_canvas, create_canvas
from ..models import find_model
from .collect import CollectOperation
from .waiting import validate_lost_run
from ..uploads import send_media
from ..contract import validate_cli
from ..failures import build_failure
from ..arguments import add_flags, build_flags, choose_prompt, parse_arguments, validate_argument_names
from ..operation import wait_until_settled
from ..references import format_prompt, plan_references, validate_references
from ...state.runs import RunReply
from ...state.errors import ErrorCode, DreaminaError
from ...config.dreamina import EXIT_CODES, CALL_SECONDS, DREAMINA_URLS, ACCEPTED_PHASE
from ...config.execution import PROGRESS_STEPS
from ...state.generations import RunCall, GenerationRecord, GenerationResult
from ...config.generations import RECORD_VERSION
from ...config.messages.run import RUN_REFUSED
from ...config.messages.generations import (
    RUN_UNRECORDED,
    GENERATION_KEEPS_RUNNING,
)

if TYPE_CHECKING:
    from pathlib import Path
    from collections.abc import Callable

    from .records import GenerationStore
    from ..operation import Progress
    from ...state.cli import CliResult
    from ...state.models import ModelMode, ListedModel
    from ...state.settings import Configuration
    from ...storage.canvas import CanvasStore
    from ...state.references import LocalMedia
    from ...state.generations import GenerationPlan


async def _read_node_id(result: CliResult, call: RunCall) -> str:
    """Read the node of a run Dreamina accepted, or stop: it raises a refusal, and checks a lost reply read-only.

    Exit 0 and exit 20 follow acceptance, and so does a failure of the CLI's own records after the submit; every
    other failure means the run did not start.

    Args:
        result: The result of the run call.
        call: The run call, with its submit ID and credit ceiling.

    Returns:
        The ID of the canvas node the run created.

    Raises:
        DreaminaError: When Dreamina accepted the run and the reply names no node for it.
        build_failure: When the run did not start.

    """
    reply = result.reply
    if result.exit_code == EXIT_CODES['OK']:
        try:
            return parse_reply(reply.payload, RunReply).node.node_id
        except DreaminaError:
            await validate_lost_run(call.submit_id, call.project_id)
    storage = reply.error.local_storage if reply.error is not None else None
    phase = storage.submission_phase if storage is not None else None
    if result.exit_code != EXIT_CODES['INCOMPLETE'] and phase != ACCEPTED_PHASE:
        raise build_failure(result, RUN_REFUSED, credit_ceiling=call.credit_ceiling)
    items = reply.partial.items if reply.partial is not None else ()
    node_id = next((item.node_id for item in items if item.submit_id == call.submit_id and item.node_id), None)
    if node_id is None:
        raise DreaminaError(ErrorCode.UNCERTAIN, RUN_UNRECORDED.format(**DREAMINA_URLS))
    return node_id


class GenerationOperation:
    """One generation, sent with one run call and recorded as soon as Dreamina accepts it."""

    def __init__(
        self,
        plan: GenerationPlan,
        generations: GenerationStore,
        canvas: CanvasStore,
        encode: Callable[[LocalMedia, Path], Path],
    ) -> None:
        """Keep the plan of the node, the stores, and ComfyUI's encoder, which the node passes in.

        The encoder is ComfyUI's, because this package may not import ComfyUI.

        Args:
            plan: What the node asks for: the model, prompt, flags, references, and local media.
            generations: The store that records the accepted run.
            canvas: The store that holds the saved canvas.
            encode: ComfyUI's encoder, which the upload calls for local media.

        """
        self.plan = plan
        self.generations = generations
        self.canvas = canvas
        self.encode = encode

    async def _plan_run(self) -> tuple[ListedModel, ModelMode, str, tuple[str, ...]]:
        """Refuse locally everything that the live model list says Dreamina refuses, and build the flags.

        Returns:
            The listed model, the chosen entry, the prompt, and the flags of the run call.

        """
        plan = self.plan
        await validate_cli()
        values = add_flags(plan.flags, parse_arguments(plan.arguments))
        listed = await find_model(plan.model, plan.kind)
        validate_argument_names(listed, values)
        items = (*plan.references, *plan.local)
        mode, label = choose_mode(listed, plan.kind, tuple(item.media for item in items), values)
        prompt = choose_prompt(plan.prompt, values)
        flags = build_flags(listed.name, mode, label, prompt, values)
        validate_references(mode, label, items, values)
        return listed, mode, prompt, flags

    async def _send_media(
        self, configuration: Configuration, deadline: float, prompt: str
    ) -> tuple[str, tuple[str, ...]]:
        """Find or create the canvas, upload the local media, and write the prompt or title and each --ref.

        Args:
            configuration: The configuration, whose settings the upload reads.
            deadline: The monotonic time by which the uploads must end.
            prompt: The prompt to send, empty when the run sends the title instead.

        Returns:
            The project ID of the canvas, and the prompt or title arguments followed by each reference.

        """
        plan = self.plan
        canvas = await find_canvas(self.canvas) or await create_canvas(self.canvas)
        uploaded = await send_media(canvas.project_id, plan.local, self.encode, configuration.settings, deadline)
        ordered, placed = plan_references(plan.references, plan.local, uploaded)
        text = ('--prompt', format_prompt(prompt, placed)) if prompt else ('--title', plan.title)
        return canvas.project_id, (*text, *(item for reference in ordered for item in ('--ref', reference)))

    async def _build_call(self, configuration: Configuration, deadline: float, progress: Progress | None) -> RunCall:
        """Check, upload, and build the run call; a cancel here stops the run with nothing sent to the model.

        Args:
            configuration: The configuration that the upload step receives.
            deadline: The monotonic time by which the run must end.
            progress: The callback that reports the checked and uploaded steps, or None.

        Returns:
            The run call, with a new submit ID.

        """
        listed, mode, prompt, flags = await self._plan_run()
        if progress is not None:
            await progress(PROGRESS_STEPS['CHECKED'])
        project_id, sources = await self._send_media(configuration, deadline, prompt)
        if progress is not None:
            await progress(PROGRESS_STEPS['UPLOADED'])
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
        """Send the run call once, with its own time limit, and record an accepted run before anything waits for it.

        Args:
            call: The run call to send.

        Returns:
            The record of the accepted run, and the request ID of the reply when it has one.

        Raises:
            DreaminaError: When the call fails before the CLI gives a reply.

        """
        submitted_at = datetime.now(UTC).isoformat()
        # The node sends the run call once and never again.
        arguments = (
            'node', 'create', call.kind, '--project-id', call.project_id, '--model', call.model, *call.flags,
            *call.sources, '--run', '--submit-id', call.submit_id, '--credit-ceiling', str(call.credit_ceiling),
        )  # fmt: skip
        try:
            result = await send_command(arguments, CALL_SECONDS['RUN'])
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

    async def send(self, configuration: Configuration, progress: Progress | None) -> GenerationResult:
        """Check, upload, send the run once, record it, then wait for it and collect what it made.

        Every refusal comes before anything leaves the computer, and the run call is the last step that can bill. A
        cancel during the run call waits for its answer, so an accepted run is always recorded.

        Args:
            configuration: The configuration, whose settings give the time limit of the whole run.
            progress: The callback that reports each step of the run, or None.

        Returns:
            The result of the collection: the record, its node, and the downloaded files.

        Raises:
            DreaminaError: When a cancel arrives during the run call.

        """
        deadline = time.monotonic() + configuration.settings.request_timeout_seconds
        call = await self._build_call(configuration, deadline, progress)
        running = asyncio.create_task(self._send_run(call))
        is_cancelled = await wait_until_settled(running)
        record, request_id = running.result()
        if is_cancelled:
            raise DreaminaError(ErrorCode.INTERRUPTED, GENERATION_KEEPS_RUNNING)
        if progress is not None:
            await progress(PROGRESS_STEPS['ACCEPTED'])
        collect = CollectOperation(record, self.generations, self.canvas, deadline, request_id)
        return await collect.send(configuration, progress)


__all__ = ['GenerationOperation']
