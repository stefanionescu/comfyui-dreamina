"""Upscale image nodes with Dreamina's own command: import ComfyUI images, send one paid call, and collect each image.

Every source gets its own submit ID and record, saved before the first wait, so an upscale that keeps running can be
collected with Generation: Download.
"""

from __future__ import annotations

import re
import time
import uuid
import asyncio
from .uploads import send_media
from typing import TYPE_CHECKING
from .contract import validate_cli
from datetime import UTC, datetime
from .arguments import parse_arguments
from ..config.models import FLAG_PREFIX
from .operation import wait_until_settled
from .cli import parse_reply, send_command
from ..config.execution import PROGRESS_STEPS
from .canvas import find_canvas, create_canvas
from ..config.patterns import SCHEMA_RANGE_PATTERN
from ..types.errors import ErrorCode, DreaminaError
from .generations.operation import CollectOperation
from .failures import build_failure, sanitize_reason
from ..types.replies import ElementReply, UpscaleReply
from ..types.generations import UpscaleCall, GenerationRecord
from ..config.dreamina import EXIT_CODES, CALL_SECONDS, DREAMINA_URLS, ACCEPTED_PHASE
from ..config.messages.run import CLI_FAILED, RUN_REFUSED, UPSCALE_REFUSED, UPSCALE_PARTLY_REFUSED
from ..config.messages.generations import RUN_UNCERTAIN, RUN_UNRECORDED, STATUS_CODE_REASON, GENERATION_KEEPS_RUNNING
from ..config.generations import (
    UPSCALE_FLAGS,
    UPSCALE_MODEL,
    UPSCALE_MODES,
    RECORD_VERSION,
    UPSCALE_COMMAND,
    SCHEMA_CONSTRAINTS,
    UPSCALE_IMPORT_KIND,
)
from ..config.messages.inputs import (
    UPSCALE_MODE_FLAG,
    UPSCALE_FLAG_NEEDED,
    UPSCALE_ARGUMENT_KEY,
    UPSCALE_SOURCE_EMPTY,
    UPSCALE_SOURCE_LIMIT,
    UPSCALE_ARGUMENT_RANGE,
    UPSCALE_ARGUMENT_CHOICE,
    UPSCALE_REFERENCE_MEDIA,
    UPSCALE_REFERENCE_RESOURCE,
)

if TYPE_CHECKING:
    from ..types import Json
    from pathlib import Path
    from .operation import Progress
    from ..types.cli import CliResult
    from ..types.replies import SchemaFlag
    from ..storage.canvas import CanvasStore
    from ..types.references import LocalMedia
    from collections.abc import Mapping, Callable
    from .generations.records import GenerationStore
    from ..types.settings import Settings, Configuration
    from ..types.generations import UpscaleRequest, GenerationResult

_RANGE = re.compile(SCHEMA_RANGE_PATTERN)


def _read_rule(flag: SchemaFlag) -> range | tuple[str, ...] | None:
    """Read a flag's rule from the schema: a whole-number range, the allowed values, or None when it gives neither."""
    head = flag.constraints.split(SCHEMA_CONSTRAINTS["PART"], 1)[0].strip()
    match = _RANGE.match(head)
    if match is not None:
        return range(int(match.group(1)), int(match.group(2)) + 1)
    if SCHEMA_CONSTRAINTS["CHOICE"] in head:
        return tuple(part.strip() for part in head.split(SCHEMA_CONSTRAINTS["CHOICE"]))
    return None


def _validate_value(key: str, value: Json, flag: SchemaFlag) -> str:
    """Check one value against its flag's schema rule, exactly as the schema writes it, and return it as sent."""
    rule = _read_rule(flag)
    if isinstance(rule, range):
        if isinstance(value, bool) or not isinstance(value, int) or value not in rule:
            message = UPSCALE_ARGUMENT_RANGE.format(key=key, minimum=rule.start, maximum=rule.stop - 1)
            raise DreaminaError(ErrorCode.INVALID_INPUT, message)
    elif rule is not None and value not in rule:
        raise DreaminaError(ErrorCode.INVALID_INPUT, UPSCALE_ARGUMENT_CHOICE.format(key=key, values=", ".join(rule)))
    return str(value)


def _validate_mode(mode: str, keys: set[str], flags: Mapping[str, SchemaFlag]) -> None:
    """Refuse a flag the mode needs but arguments leaves out, and one the mode does not take."""
    rules = UPSCALE_MODES.get(mode)
    if rules is None:
        return
    missing = next((key for key in rules["REQUIRED"] if key not in keys), None)
    if missing is not None:
        rule = _read_rule(flags[missing])
        values = ", ".join(rule) if isinstance(rule, tuple) else ""
        raise DreaminaError(ErrorCode.INVALID_INPUT, UPSCALE_FLAG_NEEDED.format(key=missing, mode=mode, values=values))
    extra = next((key for key in sorted(keys) if key != UPSCALE_FLAGS[0] and key not in rules["TAKEN"]), None)
    if extra is not None:
        raise DreaminaError(ErrorCode.INVALID_INPUT, UPSCALE_MODE_FLAG.format(key=extra, mode=mode))


def _read_outcomes(result: CliResult, call: UpscaleCall) -> dict[str, tuple[str | None, str]]:
    """Map each source to its new node ID, or to None and Dreamina's reason for refusing it.

    Exit 0 and exit 20 follow acceptance, and so does a failure of the CLI's own records after the submit; every
    other failure means nothing was accepted.
    """
    reply = result.reply
    storage = reply.error.local_storage if reply.error is not None else None
    if result.exit_code == EXIT_CODES["INCOMPLETE"] or (
        storage is not None and storage.submission_phase == ACCEPTED_PHASE
    ):
        items = reply.partial.items if reply.partial is not None else ()
        return {item.source_node_id: (item.node_id, "") for item in items if item.source_node_id and item.node_id}
    if result.exit_code != EXIT_CODES["OK"]:
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
            else "",
        )
        for item in upscale.items
    }


def parse_upscale_arguments(text: str, flags: Mapping[str, SchemaFlag]) -> dict[str, str]:
    """Check the arguments box against the upscale command's own flags, and return each value to send by flag name.

    A flag left out sends nothing, so the CLI's default applies; the mode is read from its schema default then.
    """
    values = parse_arguments(text)
    unknown = next((key for key in values if key not in UPSCALE_FLAGS), None)
    if unknown is not None:
        message = UPSCALE_ARGUMENT_KEY.format(keys=", ".join(UPSCALE_FLAGS), key=unknown)
        raise DreaminaError(ErrorCode.INVALID_INPUT, message)
    sent = {key: _validate_value(key, values[key], flags[key]) for key in UPSCALE_FLAGS if key in values}
    _validate_mode(sent.get(UPSCALE_FLAGS[0], str(flags[UPSCALE_FLAGS[0]].default)), set(values), flags)
    return sent


class UpscaleOperation:
    """One upscale of every source, sent with one call and recorded per source as soon as Dreamina accepts it."""

    def __init__(
        self,
        request: UpscaleRequest,
        generations: GenerationStore,
        canvas: CanvasStore,
        encode: Callable[[LocalMedia, Path], Path],
    ) -> None:
        """Keep the node's request, the stores, and ComfyUI's encoder, which the node passes in."""
        self.request = request
        self.generations = generations
        self.canvas = canvas
        self.encode = encode

    async def _plan_upscale(self) -> tuple[dict[str, str], str]:
        """Refuse bad arguments, references that are not whole image nodes, and too few or too many sources."""
        flags = (await validate_cli())[UPSCALE_COMMAND]
        values = parse_upscale_arguments(self.request.arguments, flags)
        references = self.request.references
        if any(reference.media != "image" for reference in references):
            raise DreaminaError(ErrorCode.INVALID_INPUT, UPSCALE_REFERENCE_MEDIA)
        if any(reference.origin != "node" for reference in references):
            raise DreaminaError(ErrorCode.INVALID_INPUT, UPSCALE_REFERENCE_RESOURCE)
        count = len(references) + len(self.request.images)
        limit = _read_rule(flags["node-id"])
        maximum = limit.stop - 1 if isinstance(limit, range) else count
        if not count:
            raise DreaminaError(ErrorCode.INVALID_INPUT, UPSCALE_SOURCE_EMPTY)
        if count > maximum:
            raise DreaminaError(ErrorCode.INVALID_INPUT, UPSCALE_SOURCE_LIMIT.format(maximum=maximum, count=count))
        return values, values.get(UPSCALE_FLAGS[0], str(flags[UPSCALE_FLAGS[0]].default))

    async def _create_sources(self, project_id: str, settings: Settings, deadline: float) -> tuple[str, ...]:
        """Upload the ComfyUI images and import each as an image node, for free; return the new node IDs in order."""
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
        """Check, find the canvas, import the images, and build the upscale call; nothing here bills."""
        values, mode = await self._plan_upscale()
        if progress is not None:
            await progress(PROGRESS_STEPS["CHECKED"])
        canvas = await find_canvas(self.canvas) or await create_canvas(self.canvas)
        imported = await self._create_sources(canvas.project_id, configuration.settings, deadline)
        if progress is not None:
            await progress(PROGRESS_STEPS["UPLOADED"])
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
        """
        submitted_at = datetime.now(UTC).isoformat()
        try:
            result = await send_command(call.arguments, CALL_SECONDS["RUN"])
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
                kind="image",
                model=UPSCALE_MODEL,
                mode=call.mode,
                submitted_at=submitted_at,
                source_node_id=source,
            )
            for source, submit_id in zip(call.sources, call.submit_ids, strict=True)
            if (node_id := outcomes.get(source, (None, ""))[0]) is not None
        )
        for record in records:
            await asyncio.to_thread(self.generations.save, record)
        if not records and not outcomes:
            raise DreaminaError(ErrorCode.UNCERTAIN, RUN_UNRECORDED.format(**DREAMINA_URLS))
        refused = next(
            (
                (number, reason)
                for number, source in enumerate(call.sources, 1)
                if (reason := outcomes.get(source, (None, ""))[1])
            ),
            None,
        )
        if refused is None:
            return records, None
        template = UPSCALE_PARTLY_REFUSED if records else UPSCALE_REFUSED
        return records, template.format(number=refused[0], reason=refused[1])

    def validate(self, settings: Settings) -> None:
        """Accept every request; each check needs the CLI's schema, which send reads."""

    async def send(self, configuration: Configuration, progress: Progress | None) -> tuple[GenerationResult, ...]:
        """Check, import, send the upscale once, record each accepted source, then collect each in source order.

        A cancel during the upscale call waits for its answer, so an accepted upscale is always recorded.
        """
        deadline = time.monotonic() + configuration.settings.request_timeout_seconds
        call = await self._build_call(configuration, deadline, progress)
        running = asyncio.create_task(self._send_upscale(call))
        is_cancelled = await wait_until_settled(running)
        records, refusal = running.result()
        if progress is not None:
            await progress(PROGRESS_STEPS["ACCEPTED"])
        if is_cancelled:
            raise DreaminaError(ErrorCode.INTERRUPTED, GENERATION_KEEPS_RUNNING)
        if refusal is not None:
            raise DreaminaError(ErrorCode.INVALID_INPUT, refusal)
        if progress is not None:
            await progress(PROGRESS_STEPS["RUNNING"])
        results = [
            await CollectOperation(record, self.generations, self.canvas, deadline).send(configuration, None)
            for record in records
        ]
        if progress is not None:
            await progress(PROGRESS_STEPS["DOWNLOADED"])
        return tuple(results)


__all__ = ["UpscaleOperation", "parse_upscale_arguments"]
