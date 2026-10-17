"""Collect a recorded Dreamina generation that kept running after a cancel, a restart, or a timeout."""

from __future__ import annotations

import asyncio
from typing import override
from functools import partial
from comfy_api.latest import io
from ..comfy.runtime import get_runtime
from .outputs import build_node_outputs
from ..types.errors import ErrorCode, DreaminaError
from ..comfy.execution import send_run, wait_for_run
from ..config.messages.generations import GENERATIONS_EMPTY
from ..dreamina.generations.operation import CollectOperation
from ..config.namespace import MENUS, NODE_PREFIX, SOCKET_TYPES

_REFERENCES = io.Custom(SOCKET_TYPES["REFERENCES"])
# Every output of every paid node, in the order the nodes list them; Generation: Download fills whichever the run made.
_OUTPUTS = (
    io.Image.Output("images", display_name="images", is_output_list=True),
    io.Video.Output("video", display_name="video", is_output_list=True),
    io.Audio.Output("audio", display_name="audio", is_output_list=True),
    _REFERENCES.Output("references", display_name="references"),
    io.String.Output("result", display_name="result"),
)


async def _download_generation(label: str, node_id: str | None) -> io.NodeOutput:
    """Find the record by its label, then wait for it, read its node, and download what it made, for free."""
    runtime = get_runtime()
    if not label and not await asyncio.to_thread(runtime.generations.list_records):
        raise DreaminaError(ErrorCode.INVALID_INPUT, GENERATIONS_EMPTY)
    record = await asyncio.to_thread(runtime.generations.find_record, label)
    operation = CollectOperation(record, runtime.generations, runtime.canvas)
    output_ids = tuple(output.id for output in _OUTPUTS)
    return await send_run(operation, partial(build_node_outputs, output_ids=output_ids), node_id)


class GenerationDownload(io.ComfyNode):
    """Collect a recorded generation; it bills nothing, and one record always gives the same outputs."""

    @classmethod
    @override
    def define_schema(cls) -> io.Schema:
        """Describe the node: the recorded generations to choose from, and every output a paid node has."""
        return io.Schema(
            node_id=f"{NODE_PREFIX}{cls.__name__}",
            display_name="Generation: Download",
            category=MENUS["SHARED"],
            description=(
                "Collect a Dreamina generation that kept running after a cancel, a restart, or a timeout. It bills "
                "nothing."
            ),
            inputs=[
                io.Combo.Input(
                    "generation",
                    options=[record.label for record in get_runtime().generations.list_records()],
                    tooltip="A generation recorded on this server. Press R to list generations recorded later.",
                )
            ],
            outputs=list(_OUTPUTS),
            hidden=[io.Hidden.unique_id],
        )

    @classmethod
    @override
    def validate_inputs(cls, **inputs: object) -> bool | str:  # pyright: ignore[reportIncompatibleMethodOverride] -- reason: ComfyUI calls by schema.
        """Take a generation recorded after the node definitions were built; the node finds the record when it runs.

        ComfyUI skips its own list check only for inputs the validator takes as extra keywords.
        """
        return True

    @classmethod
    @override
    async def execute(cls, *, generation: str = "") -> io.NodeOutput:  # pyright: ignore[reportIncompatibleMethodOverride] -- reason: ComfyUI calls by schema.
        """Collect in an owned task, so ComfyUI's cancel stops the wait and keeps the record."""
        return await wait_for_run(asyncio.create_task(_download_generation(generation, cls.hidden.unique_id)))


__all__ = ["GenerationDownload"]
