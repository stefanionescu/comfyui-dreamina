"""The ComfyUI nodes the example workflows place beside this extension's own."""

from enum import StrEnum


class HostNode(StrEnum):
    """One ComfyUI node, by the name ComfyUI registers it under."""

    IMAGE = "LoadImage"
    PREVIEW = "PreviewAny"
    TEXT_BLOCK = "PrimitiveStringMultiline"
    SAVE_IMAGE = "SaveImage"
    PREVIEW_IMAGE = "PreviewImage"
    SAVE_AUDIO = "SaveAudioAdvanced"
    SAVE_VIDEO = "SaveVideo"


__all__ = ["HostNode"]
