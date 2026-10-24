"""Generations: the canvas they live on, the record kept while one runs, the run a node asks for, and what it made."""

from typing import Literal
from dataclasses import dataclass
from collections.abc import Mapping

from . import Json, Kind, Value
from .references import Reference, LocalMedia


class CanvasRecord(Value):
    """The pack's Dreamina canvas, kept in canvas.json.

    Attributes:
        version: File format version; the reader refuses any other.
        project_id: The canvas ID every call names.
        web_url: The canvas's page on Dreamina.

    """

    version: Literal[1]
    project_id: str
    web_url: str


class GenerationRecord(Value):
    """One run Dreamina accepted, recorded before the first wait so the pack can collect a run that keeps going.

    Attributes:
        version: File format version; the reader refuses any other.
        submit_id: The run's submit ID, which also names the record's file.
        project_id: The canvas that received the run.
        node_id: The canvas node that holds the run's outputs.
        kind: The kind of node that sent it.
        model: The canonical model name, or what the upscale node records in its place.
        mode: The mode that ran.
        submitted_at: When the extension sent the run call, as an ISO 8601 time in UTC.
        source_node_id: The image node an upscale started from; None for a generation.

    """

    version: Literal[1]
    submit_id: str
    project_id: str
    node_id: str
    kind: Kind
    model: str
    mode: str
    submitted_at: str
    source_node_id: str | None = None


@dataclass(frozen=True, slots=True)
class GenerationPlan:
    """The inputs of a generation node as they came, before any check.

    Attributes:
        kind: What the models of the node make.
        title: The display name of the node, sent as the title of the canvas node when the prompt is empty.
        model: The model name as typed, stripped.
        prompt: The prompt box.

        flags: The flag inputs of the node by flag name, without an empty line input.
        arguments: The arguments box, as JSON text.
        credit_ceiling: The most credits the run may cost.

        references: The connected references, in socket order.
        local: The connected media, split into one item per frame, video, and clip.

    """

    kind: Kind
    title: str
    model: str
    prompt: str
    flags: Mapping[str, Json]
    arguments: str
    credit_ceiling: int
    references: tuple[Reference, ...]
    local: tuple[LocalMedia, ...]


@dataclass(frozen=True, slots=True)
class RunCall:
    """One run call, which the extension builds after every check and upload.

    Attributes:
        kind: What the models of the node make.
        project_id: The canvas that receives the run.
        model: The canonical model name.
        mode: The mode entry's name.
        flags: The mode and flag part of the call.
        sources: The --prompt or --title pair, then one --ref pair per reference, in order.
        credit_ceiling: The most credits the run may cost.
        submit_id: The run's one submit ID, made here.

    """

    kind: Kind
    project_id: str
    model: str
    mode: str
    flags: tuple[str, ...]
    sources: tuple[str, ...]
    credit_ceiling: int
    submit_id: str


@dataclass(frozen=True, slots=True)
class UpscaleRequest:
    """One upscale a node asks for, as its inputs came; send checks it against the CLI's schema.

    Attributes:
        images: The ComfyUI images to upload and import, one per frame, in order.
        references: The connected references, in socket order.
        credit_ceiling: The most credits the whole batch may cost.
        settings: The mode and the settings it takes, by flag name.
        title: The display name of the node, the title of each imported image node.

    """

    images: tuple[LocalMedia, ...]
    references: tuple[Reference, ...]
    credit_ceiling: int
    settings: Mapping[str, Json]
    title: str


@dataclass(frozen=True, slots=True)
class UpscaleCall:
    """One upscale call, built after every check and import: one submit ID per source, one ceiling for all.

    Attributes:
        project_id: The canvas the sources are on.
        sources: The image node IDs, references first.
        submit_ids: One new submit ID per source, in the same order.
        flags: The --mode, --resolution, and --detail pairs arguments sets.
        mode: The upscale mode that runs, recorded with each source.
        credit_ceiling: The most credits the whole batch may cost.

    """

    project_id: str
    sources: tuple[str, ...]
    submit_ids: tuple[str, ...]
    flags: tuple[str, ...]
    mode: str
    credit_ceiling: int


@dataclass(frozen=True, slots=True)
class OutputFile:
    """One downloaded output, checked against Dreamina's size and SHA-256.

    Attributes:
        resource_id: The output's resource ID.
        kind: image, video, or audio.
        content: The file's bytes.

    """

    resource_id: str
    kind: Kind
    content: bytes


@dataclass(frozen=True, slots=True)
class GenerationResult:
    """What a finished generation made.

    Attributes:
        record: The generation's record, which the extension deletes once it has downloaded every output.
        node: The canvas node as node show returned it.
        title: The title of the canvas node.
        files: The downloaded outputs, in the resource order of the node.
        canvas_url: The canvas's page, when the record's canvas is the saved one.
        request_id: The run call's request ID, kept for support.

    """

    record: GenerationRecord
    node: Mapping[str, Json]
    title: str | None
    files: tuple[OutputFile, ...]
    canvas_url: str | None
    request_id: str | None


__all__ = [
    'CanvasRecord',
    'GenerationPlan',
    'GenerationRecord',
    'GenerationResult',
    'OutputFile',
    'RunCall',
    'UpscaleCall',
    'UpscaleRequest',
]
