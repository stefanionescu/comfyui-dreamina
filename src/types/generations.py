"""Generations: the canvas they live on, the record kept while one runs, the run a node asks for, and what it made."""

from typing import Literal
from . import Json, Kind, Value
from dataclasses import dataclass
from collections.abc import Mapping
from .references import Reference, LocalMedia
from ..config.generations import LABEL_SEPARATOR, LABEL_CHARACTERS


class CanvasRecord(Value):
    """The pack's Dreamina canvas, kept in canvas.json.

    Attributes:
        version: File format version; any other is refused.
        project_id: The canvas ID every call names.
        web_url: The canvas's page on Dreamina.

    """

    version: Literal[1]
    project_id: str
    web_url: str


class GenerationRecord(Value):
    """One run Dreamina accepted, recorded before the first wait so a run that keeps going can be collected.

    Attributes:
        version: File format version; any other is refused.
        submit_id: The run's submit ID, which also names the record's file.
        project_id: The canvas the run was sent to.
        node_id: The canvas node that holds the run's outputs.
        kind: The kind of node that sent it.
        model: The canonical model name, or what the upscale node records in its place.
        mode: The mode that ran.
        submitted_at: When the run call was sent, in ISO 8601 and UTC.
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

    @property
    def label(self) -> str:
        """Name the record as Generation: Download lists it: its submit ID's start, its model, and its minute in UTC."""
        submitted = self.submitted_at[: LABEL_CHARACTERS["TIME"]].replace("T", " ")
        return LABEL_SEPARATOR.join((self.submit_id[: LABEL_CHARACTERS["SUBMIT_ID"]], self.model, submitted))


@dataclass(frozen=True, slots=True)
class GenerationPlan:
    """A generation node's inputs as they came, before any check.

    Attributes:
        kind: What the node's models make.
        title: The node's display name, sent as the canvas node's title when the prompt is empty.
        model: The model name as typed, stripped.
        prompt: The prompt box.
        arguments: The arguments box, as JSON text.
        credit_ceiling: The most credits the run may cost.
        references: The connected references, in socket order.
        local: The connected media, split into one item per frame, video, and clip.

    """

    kind: Kind
    title: str
    model: str
    prompt: str
    arguments: str
    credit_ceiling: int
    references: tuple[Reference, ...]
    local: tuple[LocalMedia, ...]


@dataclass(frozen=True, slots=True)
class RunCall:
    """One run call, built after every check and upload.

    Attributes:
        kind: What the node's models make.
        project_id: The canvas the run is sent to.
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

    @property
    def arguments(self) -> tuple[str, ...]:
        """Write the run call, which is sent once and never again."""
        return (
            "node", "create", self.kind, "--project-id", self.project_id, "--model", self.model, *self.flags,
            *self.sources, "--run", "--submit-id", self.submit_id, "--credit-ceiling", str(self.credit_ceiling),
        )  # fmt: skip


@dataclass(frozen=True, slots=True)
class UpscaleRequest:
    """One upscale a node asks for, as its inputs came; send checks it against the CLI's schema.

    Attributes:
        images: The ComfyUI images to upload and import, one per frame, in order.
        references: The connected references, in socket order.
        credit_ceiling: The most credits the whole batch may cost.
        arguments: The arguments input's JSON text.
        title: The node's display name, the title of each imported image node.

    """

    images: tuple[LocalMedia, ...]
    references: tuple[Reference, ...]
    credit_ceiling: int
    arguments: str
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

    @property
    def arguments(self) -> tuple[str, ...]:
        """Write the upscale call, which is sent once and never again."""
        return (
            "node", "upscale", "image", "--project-id", self.project_id,
            *(item for source in self.sources for item in ("--node-id", source)),
            *(item for submit_id in self.submit_ids for item in ("--submit-id", submit_id)),
            *self.flags, "--credit-ceiling", str(self.credit_ceiling),
        )  # fmt: skip


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
        record: The generation's record, deleted once every output was downloaded.
        node: The canvas node as node show returned it.
        title: The canvas node's title.
        files: The downloaded outputs, in the node's resource order.
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
    "CanvasRecord",
    "GenerationPlan",
    "GenerationRecord",
    "GenerationResult",
    "OutputFile",
    "RunCall",
    "UpscaleCall",
    "UpscaleRequest",
]
