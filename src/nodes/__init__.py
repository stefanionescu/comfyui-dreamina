"""Register the extension's nodes in menu order."""

from .model import ModelInfo
from comfy_api.latest import io
from .audio import AudioGenerate
from .image import ImageGenerate
from .upscale import ImageUpscale

NODE_TYPES: tuple[type[io.ComfyNode], ...] = (ImageGenerate, ImageUpscale, AudioGenerate, ModelInfo)

__all__ = ["NODE_TYPES"]
