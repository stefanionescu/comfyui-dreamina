"""Fill a Dreamina node's outputs from what its generation made."""

from __future__ import annotations

import json
from comfy_api.latest import io
from typing import TYPE_CHECKING
from ..types.references import Reference
from comfy_execution.graph import ExecutionBlocker
from ..comfy.media import decode_audio, decode_video, decode_images

if TYPE_CHECKING:
    from ..types import Json
    from collections.abc import Callable, Sequence
    from ..types.generations import GenerationResult


def _build_references(result: GenerationResult) -> tuple[Reference, ...]:
    """Pass one output on as its canvas node, which keeps the canvas edge, and several as one resource each."""
    files = result.files
    if len(files) == 1:
        return (Reference(origin="node", value=result.record.node_id, media=files[0].kind, title=result.title),)
    return tuple(
        Reference(origin="resource", value=file.resource_id, media=file.kind, title=result.title) for file in files
    )


def build_result_document(result: GenerationResult) -> dict[str, Json]:
    """Describe the run: the canvas link, the run call's request ID for support, and the node as node show returned it.

    A key without a value is left out: Generation: Download has no request ID, and a replaced canvas has no link.
    """
    document: dict[str, Json] = {}
    if result.canvas_url is not None:
        document["canvas"] = result.canvas_url
    if result.request_id is not None:
        document["requestId"] = result.request_id
    document["node"] = dict(result.node)
    return document


def build_node_outputs(result: GenerationResult, output_ids: Sequence[str]) -> io.NodeOutput:
    """Fill the node's outputs by ID, decoding only those it shows; an empty output blocks the nodes after it."""
    contents = {
        kind: [file.content for file in result.files if file.kind == kind] for kind in ("image", "video", "audio")
    }
    builders: dict[str, Callable[[], object]] = {
        "images": lambda: list(decode_images(contents["image"])),
        "video": lambda: [decode_video(content) for content in contents["video"]],
        "audio": lambda: [decode_audio(content) for content in contents["audio"]],
        "references": lambda: _build_references(result),
        "result": lambda: json.dumps(build_result_document(result), indent=2, ensure_ascii=False),
    }
    values = [builders[output_id]() for output_id in output_ids]
    return io.NodeOutput(*(ExecutionBlocker(None) if value in ([], ()) else value for value in values))


__all__ = ["build_node_outputs", "build_result_document"]
