"""Register the extension's nodes in menu order."""

from comfy_api.latest import io
from .image import ImageGenerate

NODE_TYPES: tuple[type[io.ComfyNode], ...] = (ImageGenerate,)

__all__ = ["NODE_TYPES"]
