"""Dreamina canvas nodes and resources a run references, and ComfyUI media waiting for its upload."""

from typing import Literal
from dataclasses import dataclass

from . import Kind, MediaKind

type ReferenceOrigin = Literal['node', 'resource']


@dataclass(frozen=True, slots=True)
class Reference:
    """One Dreamina canvas node or resource a run can use, with no upload.

    Attributes:
        origin: node for a canvas node, which keeps the edge to it; resource for one concrete file.
        value: The node ID or the resource ID, as the CLI writes it. A node ID starts with `node_`; a resource ID is a
            lowercase universally unique identifier.
        media: image, video, audio, or element.
        title: The title of the canvas node when Dreamina gives one; None otherwise.

    """

    origin: ReferenceOrigin
    value: str
    media: MediaKind
    title: str | None


@dataclass(frozen=True, slots=True)
class LocalMedia:
    """One connected ComfyUI image frame, video, or audio clip, uploaded when its run starts.

    Attributes:
        media: image, video, or audio.
        value: The ComfyUI value: an `IMAGE` frame [1, H, W, C], a `VIDEO`, or an `AUDIO` clip whose waveform is
            [1, C, T].
        position: Its place among the connected items of its kind, from 1, which its placeholder names.

    """

    media: Kind
    value: object
    position: int


@dataclass(frozen=True, slots=True)
class ElementRequest:
    """One Element to create, every source already on the canvas.

    Attributes:
        main: The primary image.
        auxiliary: More images of the same subject, node sources first.
        voice: The voice, or None.
        title: The Element's name on the canvas.
        description: A note kept with the Element; empty sends nothing.

    """

    main: Reference
    auxiliary: tuple[Reference, ...]
    voice: Reference | None
    title: str
    description: str


__all__ = ['ElementRequest', 'LocalMedia', 'Reference']
