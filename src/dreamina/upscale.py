"""Upscale image nodes with Dreamina's own command: import ComfyUI images, send one paid call, and collect each image.

Every source gets its own submit ID and record, saved before the first wait, so Generation: Download can collect an
upscale that keeps running.
"""

from __future__ import annotations

import time
import uuid
from typing import TYPE_CHECKING
import asyncio
from datetime import UTC, datetime

from .cli import parse_reply, send_command
from .canvas import find_canvas, create_canvas
from .uploads import send_media
from .contract import read_rule, validate_cli
from .failures import build_failure, sanitize_reason
from .operation import wait_until_settled
from ..state.runs import ElementReply, UpscaleReply
from ..state.errors import ErrorCode, DreaminaError
from ..config.models import FLAG_PREFIX
from ..config.dreamina import EXIT_CODES, CALL_SECONDS, DREAMINA_URLS, ACCEPTED_PHASE
from ..config.execution import PROGRESS_STEPS
from ..state.generations import UpscaleCall, GenerationRecord
from ..config.generations import (
    UPSCALE_MODEL,
    RECORD_VERSION,
    UPSCALE_COMMAND,
    UPSCALE_SETTINGS,
    UPSCALE_IMPORT_KIND,
)
from .generations.collect import CollectOperation
from ..config.messages.run import CLI_FAILED, RUN_REFUSED, UPSCALE_REFUSED, UPSCALE_PARTLY_REFUSED
from ..config.messages.inputs import (
    UPSCALE_RANGE,
    UPSCALE_CHOICE,
    UPSCALE_SOURCE_EMPTY,
    UPSCALE_SOURCE_LIMIT,
    UPSCALE_REFERENCE_MEDIA,
    UPSCALE_REFERENCE_RESOURCE,
)
from ..config.messages.generations import RUN_UNCERTAIN, RUN_UNRECORDED, STATUS_CODE_REASON, GENERATION_KEEPS_RUNNING

if TYPE_CHECKING:
    from pathlib import Path
    from collections.abc import Callable

    from ..state import Json
    from .operation import Progress
    from ..state.cli import CliResult
    from ..state.replies import SchemaFlag
    from ..state.settings import Settings, Configuration
    from ..storage.canvas import CanvasStore
    from ..state.references import LocalMedia
    from ..state.generations import UpscaleRequest, GenerationResult
    from .generations.records import GenerationStore


def _validate_value(key: str, value: Json, flag: SchemaFlag) -> str:
    """Check one value against its flag's schema rule, exactly as the schema writes it, and return it as sent.

    Args:
        key: The setting's flag name, named in the refusal.
        value: The value the node gives the setting.
        flag: The schema's entry for the flag.

    Returns:
        The value as text for the command line.

    Raises:
        DreaminaError: When the value is outside the range or not among the allowed values.

    """
    rule = read_rule(flag)
    if isinstance(rule, range):
        if isinstance(value, bool) or not isinstance(value, int) or value not in rule:
            message = UPSCALE_RANGE.format(key=key, minimum=rule.start, maximum=rule.stop - 1)
            raise DreaminaError(ErrorCode.INVALID_INPUT, message)
    elif rule is not None and value not in rule:
        raise DreaminaError(ErrorCode.INVALID_INPUT, UPSCALE_CHOICE.format(key=key, values=', '.join(rule)))
    return str(value)


def _read_outcomes(result: CliResult, call: UpscaleCall) -> dict[str, tuple[str | None, str]]:
    """Map each source to its new node ID, or to None and Dreamina's reason for refusing it.

    Exit 0 and exit 20 follow acceptance, and so does a failure of the CLI's own records after the submit; every
    other failure means Dreamina accepted nothing.

    Args:
        result: The CLI's answer to the upscale call.
        call: The call that was sent, whose credit ceiling a failure names.

    Returns:
        The node ID or None, and the reason, by source node ID.

    Raises:
        DreaminaError: When the CLI exits with 0 and its reply cannot be read.
        build_failure: When Dreamina accepted nothing.

    """
    reply = result.reply
    storage = reply.error.local_storage if reply.error is not None else None
    if result.exit_code == EXIT_CODES['INCOMPLETE'] or (
        storage is not None and storage.submission_phase == ACCEPTED_PHASE
    ):
        items = reply.partial.items if reply.partial is not None else ()
        return {item.source_node_id: (item.node_id, '') for item in items if item.source_node_id and item.node_id}
    if result.exit_code != EXIT_CODES['OK']:
        raise build_failure(result, RUN_REFUSED, credit_ceiling=call.credit_ceiling)
    try:
        upscale = parse_reply(reply.payload, UpscaleReply)
    except DreaminaError:
        raise DreaminaError(ErrorCode.UNCERTAIN, RUN_UNCERTAIN.format(**DREAMINA_URLS)) from None
    return {
        item.source_node_id: (
            item.node_id if item.error is None else None,
            sanitize_reason(item.error.message or STATUS_CODE_REASON.format(code=item.error.status_code))
            if item.error is not None
            else '',
        )
        for item in upscale.items
    }


class UpscaleOperation:
    """One upscale of every source, sent with one call and recorded per source as soon as Dreamina accepts it."""

    def __init__(
        self,
        request: UpscaleRequest,
        generations: GenerationStore,
        canvas: CanvasStore,
        encode: Callable[[LocalMedia, Path], Path],
    ) -> None:
        """Keep the request of the node, the stores, and ComfyUI's encoder, which the node passes in.

        Args:
            request: The upscale the node asks for.
            generations: The store that keeps one record per accepted source.
            canvas: The store that keeps the pack's canvas.
            encode: ComfyUI's encoder, which writes one image into a folder.

        """
        self.request = request
        self.generations = generations
        self.canvas = canvas
        self.encode = encode

    async def _plan_upscale(self) -> tuple[dict[str, str], str]:
        """Refuse what the live schema or the sources do not allow, and return the settings to send and the mode.

        Returns:
            The settings as text by flag name, and the upscale mode.

        Raises:
            DreaminaError: When a setting breaks its rule, a reference is not an image node, or the sources are none
                or too many.

        """
        flags = (await validate_cli())[UPSCALE_COMMAND]
        values = {key: _validate_value(key, value, flags[key]) for key, value in self.request.settings.items()}
        references = self.request.references
        if any(reference.media != 'image' for reference in references):
            raise DreaminaError(ErrorCode.INVALID_INPUT, UPSCALE_REFERENCE_MEDIA)
        if any(reference.origin != 'node' for reference in references):
            raise DreaminaError(ErrorCode.INVALID_INPUT, UPSCALE_REFERENCE_RESOURCE)
        count = len(references) + len(self.request.images)
        limit = read_rule(flags['node-id'])
        maximum = limit.stop - 1 if isinstance(limit, range) else count
        if not count:
            raise DreaminaError(ErrorCode.INVALID_INPUT, UPSCALE_SOURCE_EMPTY)
        if count > maximum:
            raise DreaminaError(ErrorCode.INVALID_INPUT, UPSCALE_SOURCE_LIMIT.format(maximum=maximum, count=count))
        return values, values[UPSCALE_SETTINGS['MODE']]

    async def _create_sources(self, project_id: str, settings: Settings, deadline: float) -> tuple[str, ...]:
        """Upload the ComfyUI images and import each as an image node at no cost; return the new node IDs in order.

        Args:
            project_id: The canvas that receives the images.
            settings: The settings that hold the maximum upload size.
            deadline: The monotonic time by which each call must end.

        Returns:
            The IDs of the new image nodes.

        Raises:
            build_failure: When the CLI refuses to create an image node.

        """
        uploaded = await send_media(project_id, self.request.images, self.encode, settings, deadline)
        nodes: list[str] = []
        for reference in uploaded:
            arguments = (
                "node", "create", "image", "--project-id", project_id, "--resource-id", reference.value,
                "--import-kind", UPSCALE_IMPORT_KIND, "--submit-id", str(uuid.uuid4()), "--title", self.request.title,
            )  # fmt: skip
            result = await send_command(arguments, max(deadline - time.monotonic(), 1.0))
            if not result.reply.ok:
                raise build_failure(result, CLI_FAILED)
            nodes.append(parse_reply(result.reply.payload, ElementReply).node.node_id)
        return tuple(nodes)

    async def _build_call(
        self, configuration: Configuration, deadline: float, progress: Progress | None
    ) -> UpscaleCall:
        """Check, find the canvas, import the images, and build the upscale call; nothing here bills.

        Args:
            configuration: The configuration whose settings limit the uploads.
            deadline: The monotonic time by which the free calls must end.
            progress: The report of each finished step, or None.

        Returns:
            The call to send, with one submit ID per source.

        """
        values, mode = await self._plan_upscale()
        if progress is not None:
            await progress(PROGRESS_STEPS['CHECKED'])
        canvas = await find_canvas(self.canvas) or await create_canvas(self.canvas)
        imported = await self._create_sources(canvas.project_id, configuration.settings, deadline)
        if progress is not None:
            await progress(PROGRESS_STEPS['UPLOADED'])
        sources = (*(reference.value for reference in self.request.references), *imported)
        return UpscaleCall(
            project_id=canvas.project_id,
            sources=sources,
            submit_ids=tuple(str(uuid.uuid4()) for _ in sources),
            flags=tuple(item for key, value in values.items() for item in (FLAG_PREFIX + key, value)),
            mode=mode,
            credit_ceiling=self.request.credit_ceiling,
        )

    async def _send_upscale(self, call: UpscaleCall) -> tuple[tuple[GenerationRecord, ...], str | None]:
        """Send the upscale call once and record each accepted source before anything waits for it.

        It returns the records in source order, and the refusal to raise for a source Dreamina refused.

        Args:
            call: The upscale call that _build_call built.

        Returns:
            The saved records, and the refusal message or None.

        Raises:
            DreaminaError: When the call's outcome is unknown, or Dreamina accepted the call and named no source.

        """
        submitted_at = datetime.now(UTC).isoformat()
        # The node sends the upscale call once and never again.
        arguments = (
            'node', 'upscale', 'image', '--project-id', call.project_id,
            *(item for source in call.sources for item in ('--node-id', source)),
            *(item for submit_id in call.submit_ids for item in ('--submit-id', submit_id)),
            *call.flags, '--credit-ceiling', str(call.credit_ceiling),
        )  # fmt: skip
        try:
            result = await send_command(arguments, CALL_SECONDS['RUN'])
        except DreaminaError as error:
            if error.code is ErrorCode.TRANSPORT:
                raise DreaminaError(ErrorCode.UNCERTAIN, RUN_UNCERTAIN.format(**DREAMINA_URLS)) from None
            raise
        outcomes = _read_outcomes(result, call)
        records = tuple(
            GenerationRecord(
                version=RECORD_VERSION,
                submit_id=submit_id,
                project_id=call.project_id,
                node_id=node_id,
                kind='image',
                model=UPSCALE_MODEL,
                mode=call.mode,
                submitted_at=submitted_at,
                source_node_id=source,
            )
            for source, submit_id in zip(call.sources, call.submit_ids, strict=True)
            if (node_id := outcomes.get(source, (None, ''))[0]) is not None
        )
        for record in records:
            await asyncio.to_thread(self.generations.save, record)
        if not records and not outcomes:
            raise DreaminaError(ErrorCode.UNCERTAIN, RUN_UNRECORDED.format(**DREAMINA_URLS))
        refused = next(
            (
                (number, reason)
                for number, source in enumerate(call.sources, 1)
                if (reason := outcomes.get(source, (None, ''))[1])
            ),
            None,
        )
        if refused is None:
            return records, None
        template = UPSCALE_PARTLY_REFUSED if records else UPSCALE_REFUSED
        return records, template.format(number=refused[0], reason=refused[1])

    async def send(self, configuration: Configuration, progress: Progress | None) -> tuple[GenerationResult, ...]:
        """Check, import, send the upscale once, record each accepted source, then collect each in source order.

        A cancel during the upscale call waits for its answer, so an accepted upscale is always recorded.

        Args:
            configuration: The configuration of the pack, with the request timeout.
            progress: The report of each finished step, or None.

        Returns:
            The collected result of each source.

        Raises:
            DreaminaError: When a cancel arrived during the call, or Dreamina refused a source.

        """
        deadline = time.monotonic() + configuration.settings.request_timeout_seconds
        call = await self._build_call(configuration, deadline, progress)
        running = asyncio.create_task(self._send_upscale(call))
        is_cancelled = await wait_until_settled(running)
        records, refusal = running.result()
        if progress is not None:
            await progress(PROGRESS_STEPS['ACCEPTED'])
        if is_cancelled:
            raise DreaminaError(ErrorCode.INTERRUPTED, GENERATION_KEEPS_RUNNING)
        if refusal is not None:
            raise DreaminaError(ErrorCode.INVALID_INPUT, refusal)
        if progress is not None:
            await progress(PROGRESS_STEPS['RUNNING'])
        results = [
            await CollectOperation(record, self.generations, self.canvas, deadline).send(configuration, None)
            for record in records
        ]
        if progress is not None:
            await progress(PROGRESS_STEPS['DOWNLOADED'])
        return tuple(results)


__all__ = ['UpscaleOperation']
