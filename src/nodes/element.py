"""Element: Add: make a Dreamina Element from a main image, more angles, and a voice, for later runs."""

from __future__ import annotations

import time
import asyncio
from comfy_api.latest import io
from dataclasses import dataclass
from ..comfy.runtime import get_runtime
from ..dreamina.uploads import send_media
from ..comfy.execution import wait_for_run
from ..dreamina.contract import validate_cli
from ..config.dreamina import TITLE_MAX_UNITS
from ..types.references import ElementRequest
from ..config.messages.run import FREE_TIMEOUT
from ..dreamina.elements import create_element
from typing import TYPE_CHECKING, cast, override
from ..types.errors import ErrorCode, DreaminaError
from ..dreamina.canvas import find_canvas, create_canvas
from ..comfy.media import encode_local_file, list_local_media
from ..config.namespace import MENUS, NODE_PREFIX, SOCKET_TYPES
from ..config.messages.inputs import (
    SINGLE_VALUE,
    ELEMENT_MAIN_COUNT,
    ELEMENT_MAIN_MEDIA,
    ELEMENT_TITLE_EMPTY,
    ELEMENT_VOICE_COUNT,
    ELEMENT_VOICE_MEDIA,
    ELEMENT_TITLE_LENGTH,
    ELEMENT_AUXILIARY_MEDIA,
)

if TYPE_CHECKING:
    import torch
    from comfy_api.latest import Input
    from collections.abc import Sequence
    from ..types.references import Reference, LocalMedia

_REFERENCES = io.Custom(SOCKET_TYPES["REFERENCES"])
# The node's name in menus, as its timeout message says it.
_DISPLAY_NAME = "Element: Add"


@dataclass(frozen=True, slots=True)
class _Sources:
    """The connected sources, checked: the media to upload and the references kept as they are.

    Attributes:
        local: The ComfyUI images, main's first, then the voice clips, one item per frame and clip.
        main_frames: How many of the images are main's.
        main: main's references.
        auxiliary: auxiliary's references.
        voice: voice's references.

    """

    local: tuple[LocalMedia, ...]
    main_frames: int
    main: tuple[Reference, ...]
    auxiliary: tuple[Reference, ...]
    voice: tuple[Reference, ...]


def _read_text(name: str, values: Sequence[str]) -> str:
    """Take the one stripped value a text input holds; several different values are refused."""
    texts = {value.strip() for value in values}
    if len(texts) > 1:
        raise DreaminaError(ErrorCode.INVALID_INPUT, SINGLE_VALUE.format(name=name))
    return next(iter(texts), "")


def _parse_sources(values: Sequence[object] | None) -> tuple[list[object], tuple[Reference, ...]]:
    """Split connected values into ComfyUI media and references; a references value is a tuple."""
    media = [value for value in values or () if not isinstance(value, tuple)]
    references = tuple(
        item for value in values or () if isinstance(value, tuple) for item in cast("tuple[Reference, ...]", value)
    )
    return media, references


def _read_sources(
    main: Sequence[object], auxiliary: Sequence[object] | None, voice: Sequence[object] | None
) -> _Sources:
    """Check what is connected before anything is uploaded: one main image, images in auxiliary, one voice at most."""
    main_media, main_references = _parse_sources(main)
    auxiliary_media, auxiliary_references = _parse_sources(auxiliary)
    voice_media, voice_references = _parse_sources(voice)
    main_images: list[torch.Tensor] = cast("list[torch.Tensor]", main_media)
    images: list[torch.Tensor] = [*main_images, *cast("list[torch.Tensor]", auxiliary_media)]
    clips: list[Input.Audio] = cast("list[Input.Audio]", voice_media)
    local = list_local_media(images, (), clips)
    main_frames = sum(int(batch.shape[0]) for batch in main_images)
    if main_frames + len(main_references) != 1:
        raise DreaminaError(ErrorCode.INVALID_INPUT, ELEMENT_MAIN_COUNT)
    if any(reference.media != "image" for reference in main_references):
        raise DreaminaError(ErrorCode.INVALID_INPUT, ELEMENT_MAIN_MEDIA)
    if any(reference.media != "image" for reference in auxiliary_references):
        raise DreaminaError(ErrorCode.INVALID_INPUT, ELEMENT_AUXILIARY_MEDIA)
    voices = sum(1 for item in local if item.media == "audio")
    if voices + len(voice_references) > 1:
        raise DreaminaError(ErrorCode.INVALID_INPUT, ELEMENT_VOICE_COUNT)
    if any(reference.media != "audio" for reference in voice_references):
        raise DreaminaError(ErrorCode.INVALID_INPUT, ELEMENT_VOICE_MEDIA)
    return _Sources(local, main_frames, main_references, auxiliary_references, voice_references)


async def _send_element(sources: _Sources, title: str, description: str, deadline: float) -> Reference:
    """Upload the ComfyUI media, bind every source by its bare ID, and make the Element."""
    runtime = get_runtime()
    await validate_cli()
    canvas = await find_canvas(runtime.canvas) or await create_canvas(runtime.canvas)
    settings = (await asyncio.to_thread(runtime.configuration.read_snapshot)).settings
    uploaded = await send_media(canvas.project_id, sources.local, encode_local_file, settings, deadline)
    images = [reference for item, reference in zip(sources.local, uploaded, strict=True) if item.media == "image"]
    clips = [reference for item, reference in zip(sources.local, uploaded, strict=True) if item.media == "audio"]
    auxiliary = (*sources.auxiliary, *images[sources.main_frames :])
    request = ElementRequest(
        main=(*sources.main, *images[: sources.main_frames])[0],
        auxiliary=tuple(sorted(auxiliary, key=lambda reference: reference.origin != "node")),
        voice=next(iter((*sources.voice, *clips)), None),
        title=title,
        description=description,
    )
    return await create_element(canvas.project_id, request, deadline)


async def _create_element(
    main: Sequence[object],
    auxiliary: Sequence[object] | None,
    voice: Sequence[object] | None,
    texts: tuple[Sequence[str], Sequence[str]],
) -> io.NodeOutput:
    """Check every input before anything is uploaded, then make the Element within the request timeout."""
    title, description = _read_text("title", texts[0]), _read_text("description", texts[1])
    if not title:
        raise DreaminaError(ErrorCode.INVALID_INPUT, ELEMENT_TITLE_EMPTY)
    if len(title.encode("utf-16-le")) // 2 > TITLE_MAX_UNITS:
        raise DreaminaError(ErrorCode.INVALID_INPUT, ELEMENT_TITLE_LENGTH.format(maximum=TITLE_MAX_UNITS))
    sources = _read_sources(main, auxiliary, voice)
    seconds = (await asyncio.to_thread(get_runtime().configuration.read_snapshot)).settings.request_timeout_seconds
    try:
        async with asyncio.timeout(seconds):
            element = await _send_element(sources, title, description, time.monotonic() + seconds)
    except TimeoutError:
        raise DreaminaError(ErrorCode.TIMEOUT, FREE_TIMEOUT.format(node=_DISPLAY_NAME, seconds=seconds)) from None
    return io.NodeOutput((element,))


class ElementAdd(io.ComfyNode):
    """Make a Dreamina Element; it bills nothing."""

    @classmethod
    @override
    def define_schema(cls) -> io.Schema:
        """Describe the node: a main image, more angles, a voice, a title, and a note in; one Element out."""
        return io.Schema(
            node_id=f"{NODE_PREFIX}{cls.__name__}",
            display_name=_DISPLAY_NAME,
            category=MENUS["SHARED"],
            description=(
                "Make a Dreamina Element from a main image, more angles, and a voice, so later runs keep the subject "
                "the same. It bills nothing."
            ),
            inputs=[
                io.MultiType.Input(
                    "main",
                    types=[io.Image, _REFERENCES],
                    tooltip=(
                        "The Element's main image: one ComfyUI image, or one image from another Dreamina node's "
                        "references."
                    ),
                ),
                io.MultiType.Input(
                    "auxiliary",
                    types=[io.Image, _REFERENCES],
                    optional=True,
                    tooltip="More images of the same subject, such as its side and back.",
                ),
                io.MultiType.Input(
                    "voice",
                    types=[io.Audio, _REFERENCES],
                    optional=True,
                    tooltip="The Element's voice: one ComfyUI audio clip, or the references of Audio: Generate.",
                ),
                io.String.Input(
                    "title", default="", tooltip="The Element's name on your Dreamina canvas, such as Host."
                ),
                io.String.Input(
                    "description",
                    default="",
                    multiline=True,
                    tooltip="A note kept with the Element on your canvas. Leave it empty to send none.",
                ),
            ],
            outputs=[_REFERENCES.Output("references", display_name="references")],
            is_input_list=True,
        )

    @classmethod
    @override
    async def execute(  # pyright: ignore[reportIncompatibleMethodOverride] -- reason: ComfyUI calls by schema.
        cls,
        *,
        main: list[object],
        title: list[str],
        description: list[str],
        auxiliary: list[object] | None = None,
        voice: list[object] | None = None,
    ) -> io.NodeOutput:
        """Make the Element in an owned task, so ComfyUI's cancel stops the work."""
        return await wait_for_run(asyncio.create_task(_create_element(main, auxiliary, voice, (title, description))))


__all__ = ["ElementAdd"]
