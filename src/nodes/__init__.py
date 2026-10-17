"""Register the extension's nodes in menu order."""

from comfy_api.latest import io
from .image import ImageGenerate
from .upscale import ImageUpscale

NODE_TYPES: tuple[type[io.ComfyNode], ...] = (ImageGenerate, ImageUpscale)

__all__ = ["NODE_TYPES"]
