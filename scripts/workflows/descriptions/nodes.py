"""The node IDs of this extension's nodes that the shipped workflows place."""

from src.config.namespace import NODE_PREFIX

IMAGE_GENERATE = f'{NODE_PREFIX}ImageGenerate'
IMAGE_UPSCALE = f'{NODE_PREFIX}ImageUpscale'
AUDIO_GENERATE = f'{NODE_PREFIX}AudioGenerate'
VIDEO_GENERATE = f'{NODE_PREFIX}VideoGenerate'
ELEMENT_ADD = f'{NODE_PREFIX}ElementAdd'
GENERATION_DOWNLOAD = f'{NODE_PREFIX}GenerationDownload'
MODEL_REPORT = f'{NODE_PREFIX}ModelInfo'

__all__ = [
    'AUDIO_GENERATE',
    'ELEMENT_ADD',
    'GENERATION_DOWNLOAD',
    'IMAGE_GENERATE',
    'IMAGE_UPSCALE',
    'MODEL_REPORT',
    'VIDEO_GENERATE',
]
