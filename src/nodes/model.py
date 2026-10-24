"""Report what any Dreamina model takes, from the live model list, its full specification, and its voices."""

from __future__ import annotations

import json
import time
from typing import override
import asyncio

from comfy_api.latest import io

from ..state.errors import ErrorCode, DreaminaError
from ..comfy.runtime import get_runtime
from ..config.inputs import INPUT_NAMES
from ..config.models import DEFAULT_MODELS
from ..comfy.execution import wait_for_run
from ..dreamina.report import read_report
from ..config.namespace import MENUS, NODE_PREFIX
from ..config.messages.run import FREE_TIMEOUT

# The name of the node, as its timeout message says it.
_DISPLAY_NAME = 'Model: Info'


async def _read_report(name: str) -> io.NodeOutput:
    """Read the model's report within the request timeout."""
    configuration = await asyncio.to_thread(get_runtime().configuration.read_configuration)
    seconds = configuration.settings.request_timeout_seconds
    try:
        async with asyncio.timeout(seconds):
            report = await read_report(name, time.monotonic() + seconds)
    except TimeoutError:
        raise DreaminaError(ErrorCode.TIMEOUT, FREE_TIMEOUT.format(node=_DISPLAY_NAME, seconds=seconds)) from None
    return io.NodeOutput(json.dumps(report, ensure_ascii=False))


class ModelInfo(io.ComfyNode):
    """Show what any Dreamina model takes; it bills nothing."""

    @classmethod
    @override
    def define_schema(cls) -> io.Schema:
        """Describe the node: one model name in, one JSON report out."""
        return io.Schema(
            node_id=f'{NODE_PREFIX}{cls.__name__}',
            display_name=_DISPLAY_NAME,
            category=MENUS['SHARED'],
            description=(
                'Show what a Dreamina model takes, as JSON: its modes, settings, allowed values, reference and file '
                'limits, and voices. It bills nothing.'
            ),
            inputs=[
                io.String.Input(
                    INPUT_NAMES['MODEL'],
                    default=DEFAULT_MODELS['image'],
                    tooltip=(
                        'A model name from your Dreamina model list, or one of its other names. Case does not matter.'
                    ),
                )
            ],
            outputs=[io.String.Output('info', display_name='info')],
        )

    @classmethod
    @override
    async def execute(cls, *, model: str) -> io.NodeOutput:  # pyright: ignore[reportIncompatibleMethodOverride] # reason: ComfyUI calls by schema.
        """Read the report in an owned task, so ComfyUI's cancel stops it."""
        return await wait_for_run(asyncio.create_task(_read_report(model.strip())))


__all__ = ['ModelInfo']
