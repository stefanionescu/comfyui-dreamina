"""Register the extension's nodes in menu order."""

from comfy_api.latest import io

from .model import ModelInfo
from .element import ElementAdd
from .upscale import ImageUpscale
from .download import GenerationDownload
from .generate import AudioGenerate, ImageGenerate, VideoGenerate

NODE_TYPES: tuple[type[io.ComfyNode], ...] = (
    ImageGenerate,
    ImageUpscale,
    VideoGenerate,
    AudioGenerate,
    ElementAdd,
    GenerationDownload,
    ModelInfo,
)

__all__ = ['NODE_TYPES']
