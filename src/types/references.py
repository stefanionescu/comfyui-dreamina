"""Dreamina canvas nodes and resources a run references, and ComfyUI media waiting for its upload."""

from typing import Literal
from . import Kind, MediaKind
from dataclasses import dataclass
from ..config.media import REFERENCE_TYPES

type ReferenceOrigin = Literal["node", "resource"]


@dataclass(frozen=True, slots=True)
class Reference:
    """One Dreamina canvas node or resource a run can use, with no upload.

    Attributes:
        origin: node for a canvas node, which keeps the edge to it; resource for one concrete file.
        value: The node ID (node_...) or the resource ID (a lowercase UUID), as the CLI writes it.
        media: image, video, audio, or element.
        title: The canvas node's title when Dreamina gives one; None otherwise.

    """

    origin: ReferenceOrigin
    value: str
    media: MediaKind
    title: str | None

    @property
    def typed_value(self) -> str:
        """Write the reference as --ref and a prompt placeholder take it: node:<node ID> or res:<resource ID>."""
        return f"{REFERENCE_TYPES[self.origin]}:{self.value}"


@dataclass(frozen=True, slots=True)
class LocalMedia:
    """One connected ComfyUI image frame, video, or audio clip, uploaded when its run starts.

    Attributes:
        media: image, video, or audio.
        value: The ComfyUI value: an IMAGE frame [1, H, W, C], a VIDEO, or an AUDIO clip whose waveform is [1, C, T].
        position: Its place among the connected items of its kind, from 1, which its placeholder names.

    """

    media: Kind
    value: object
    position: int


__all__ = ["LocalMedia", "Reference"]
