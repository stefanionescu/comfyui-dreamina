"""The ComfyUI nodes the example workflows place beside this extension's own."""

from enum import StrEnum


class HostNode(StrEnum):
    """One ComfyUI node, by the name ComfyUI registers it under.

    Attributes:
        IMAGE: The node that loads an image file.
        LIST: The node that makes a list from its inputs.
        PREVIEW: The node that previews a value of any type.
        TEXT_BLOCK: The node that holds a text of several lines.
        SAVE_IMAGE: The node that saves an image.
        PREVIEW_IMAGE: The node that previews an image.
        SAVE_AUDIO: The node that saves audio.
        SAVE_VIDEO: The node that saves a video.

    """

    IMAGE = 'LoadImage'
    LIST = 'CreateList'
    PREVIEW = 'PreviewAny'
    TEXT_BLOCK = 'PrimitiveStringMultiline'
    SAVE_IMAGE = 'SaveImage'
    PREVIEW_IMAGE = 'PreviewImage'
    SAVE_AUDIO = 'SaveAudioAdvanced'
    SAVE_VIDEO = 'SaveVideo'


__all__ = ['HostNode']
