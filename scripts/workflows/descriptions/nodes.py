"""The node IDs of the paid nodes the shipped workflows place."""

from src.config.namespace import NODE_PREFIX

IMAGE_GENERATE = f"{NODE_PREFIX}ImageGenerate"
IMAGE_UPSCALE = f"{NODE_PREFIX}ImageUpscale"
AUDIO_GENERATE = f"{NODE_PREFIX}AudioGenerate"

__all__ = ["AUDIO_GENERATE", "IMAGE_GENERATE", "IMAGE_UPSCALE"]
