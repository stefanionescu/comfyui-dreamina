"""Register the extension's nodes in menu order."""

from .model import ModelInfo
from .element import ElementAdd
from comfy_api.latest import io
from .audio import AudioGenerate
from .image import ImageGenerate
from .video import VideoGenerate
from .upscale import ImageUpscale
from .download import GenerationDownload

NODE_TYPES: tuple[type[io.ComfyNode], ...] = (
    ImageGenerate,
    ImageUpscale,
    VideoGenerate,
    AudioGenerate,
    ElementAdd,
    GenerationDownload,
    ModelInfo,
)

__all__ = ["NODE_TYPES"]
