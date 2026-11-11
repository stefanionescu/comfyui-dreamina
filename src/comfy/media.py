"""Check ComfyUI media and use ComfyUI's own helpers to convert it to files for upload and back from downloaded files.

Encoding and decoding block, so callers run these functions in a worker thread.
"""

from __future__ import annotations

import io
from typing import TYPE_CHECKING, cast

import torch
from comfy_api.latest import Types, InputImpl
from comfy_api_nodes.util.conversions import (
    tensor_to_bytesio,
    bytesio_to_image_tensor,
    audio_ndarray_to_bytesio,
    audio_bytes_to_audio_input,  # pyright: ignore[reportUnknownVariableType] # reason: ComfyUI types its result as a bare dict.
    audio_tensor_to_contiguous_ndarray,
)

from ..config.media import WAV, IMAGE_TENSOR, UPLOAD_FORMATS
from ..state.errors import ErrorCode, DreaminaError
from ..state.references import LocalMedia
from ..config.messages.media import (
    AUDIO_EMPTY,
    IMAGE_PIXELS,
    IMAGE_CHANNELS,
    AUDIO_UNREADABLE,
    AUDIO_UNWRITABLE,
    IMAGE_UNREADABLE,
    VIDEO_UNREADABLE,
    VIDEO_UNWRITABLE,
)

if TYPE_CHECKING:
    from pathlib import Path
    from collections.abc import Sequence

    from comfy_api.latest import Input


def _encode_image(image: torch.Tensor) -> bytes:
    """Encode one image frame [1, H, W, C] as a PNG at its own size, keeping a fourth channel; never shrink it.

    Args:
        image: One image frame with three or four channels.

    Returns:
        The content of the PNG file.

    Raises:
        DreaminaError: When the frame has another shape, holds a pixel that is not finite, or cannot be encoded.

    """
    if image.ndim != IMAGE_TENSOR['DIMENSIONS'] or image.shape[-1] not in {
        IMAGE_TENSOR['RGB_CHANNELS'],
        IMAGE_TENSOR['RGBA_CHANNELS'],
    }:
        raise DreaminaError(ErrorCode.INVALID_INPUT, IMAGE_CHANNELS)
    if not bool(torch.isfinite(image).all()):
        raise DreaminaError(ErrorCode.INVALID_INPUT, IMAGE_PIXELS)
    try:
        return tensor_to_bytesio(image.clamp(0, 1), total_pixels=None, mime_type='image/png').getvalue()
    except Exception:  # noqa: BLE001 # reason: ComfyUI's helper raises unrelated exception types; one reviewed message replaces them.
        raise DreaminaError(ErrorCode.MEDIA, IMAGE_CHANNELS) from None


def _encode_audio(audio: Input.Audio) -> bytes:
    """Encode one audio clip, whose waveform is [1, C, T], as a 16-bit WAV, which keeps every sample.

    Args:
        audio: One clip: its waveform and its sample rate.

    Returns:
        The content of the WAV file.

    Raises:
        DreaminaError: When the clip holds no sample or cannot be encoded.

    """
    waveform = audio['waveform']
    if waveform.shape[-1] == 0:
        raise DreaminaError(ErrorCode.INVALID_INPUT, AUDIO_EMPTY)
    try:
        return audio_ndarray_to_bytesio(
            audio_tensor_to_contiguous_ndarray(waveform),
            audio['sample_rate'],
            container_format=WAV['FORMAT'],
            codec_name=WAV['CODEC'],
        ).getvalue()
    except Exception:  # noqa: BLE001 # reason: ComfyUI's helper raises unrelated exception types; one reviewed message replaces them.
        raise DreaminaError(ErrorCode.MEDIA, AUDIO_UNWRITABLE) from None


def _encode_video(video: Input.Video, path: Path) -> None:
    """Write a ComfyUI video to an MP4 file, keeping an MP4 source's streams as they are.

    Args:
        video: The ComfyUI video to write.
        path: The MP4 file that receives the video.

    Raises:
        DreaminaError: When ComfyUI cannot write the video.

    """
    try:
        video.save_to(str(path), format=Types.VideoContainer.MP4, codec=Types.VideoCodec.AUTO)  # pyright: ignore[reportUnknownMemberType] # reason: ComfyUI types its metadata parameter as a bare dict.
    except Exception:  # noqa: BLE001 # reason: ComfyUI's helper raises unrelated exception types; one reviewed message replaces them.
        raise DreaminaError(ErrorCode.MEDIA, VIDEO_UNWRITABLE) from None


def list_local_media(
    images: Sequence[torch.Tensor], videos: Sequence[Input.Video], audio: Sequence[Input.Audio]
) -> tuple[LocalMedia, ...]:
    """Split the connected media into one item per image frame, video, and audio clip, each kind numbered from 1.

    Items keep socket order, then batch order, which is the order their placeholders count in.

    Args:
        images: The connected image batches, in socket order.
        videos: The connected videos, in socket order.
        audio: The connected audio batches, in socket order.

    Returns:
        The image frames, then the videos, then the audio clips.

    """
    frames = [frame.unsqueeze(0) for batch in images for frame in batch]
    clips: list[Input.Audio] = [
        {'waveform': clip['waveform'][index : index + 1], 'sample_rate': clip['sample_rate']}
        for clip in audio
        for index in range(clip['waveform'].shape[0])
    ]
    return (
        *(LocalMedia('image', frame, position) for position, frame in enumerate(frames, 1)),
        *(LocalMedia('video', video, position) for position, video in enumerate(videos, 1)),
        *(LocalMedia('audio', clip, position) for position, clip in enumerate(clips, 1)),
    )


def encode_local_file(media: LocalMedia, folder: Path) -> Path:
    """Write one item into the folder, named by its kind and position, and return the file's path.

    Args:
        media: The item to write.
        folder: The folder that receives the file.

    Returns:
        The path of the written file.

    """
    path = folder / f'{media.media}-{media.position}.{UPLOAD_FORMATS[media.media]["EXTENSION"]}'
    if media.media == 'video':
        _encode_video(cast('Input.Video', media.value), path)
        return path
    if media.media == 'image':
        content = _encode_image(cast('torch.Tensor', media.value))
    else:
        content = _encode_audio(cast('Input.Audio', media.value))
    path.write_bytes(content)
    return path


def decode_images(contents: Sequence[bytes]) -> tuple[torch.Tensor, ...]:
    """Read each image as pixels [1, H, W, 3], in the order given, dropping an alpha channel instead of blending it.

    Args:
        contents: The content of each downloaded image file.

    Returns:
        One image per file.

    Raises:
        DreaminaError: When ComfyUI cannot read a file as an image.

    """
    images: list[torch.Tensor] = []
    for content in contents:
        try:
            images.append(bytesio_to_image_tensor(io.BytesIO(content), mode='RGB'))
        except Exception:  # noqa: BLE001 # reason: ComfyUI's helper raises unrelated exception types; one reviewed message replaces them.
            raise DreaminaError(ErrorCode.MEDIA, IMAGE_UNREADABLE) from None
    return tuple(images)


def decode_video(content: bytes) -> Input.Video:
    """Read a video from memory, and its size once, so an unreadable file fails here and not in Save Video.

    Args:
        content: The content of a downloaded video file.

    Returns:
        The ComfyUI video.

    Raises:
        DreaminaError: When ComfyUI cannot read the file as a video.

    """
    try:
        video = InputImpl.VideoFromFile(io.BytesIO(content))
        video.get_dimensions()
    except Exception:  # noqa: BLE001 # reason: ComfyUI's helper raises unrelated exception types; one reviewed message replaces them.
        raise DreaminaError(ErrorCode.MEDIA, VIDEO_UNREADABLE) from None
    return video


def decode_audio(content: bytes) -> Input.Audio:
    """Read any common audio container as ComfyUI audio: a waveform [1, C, T] and its sample rate.

    Args:
        content: The content of a downloaded audio file.

    Returns:
        The ComfyUI audio.

    Raises:
        DreaminaError: When ComfyUI cannot read the file as audio.

    """
    try:
        audio = cast('Input.Audio', cast('object', audio_bytes_to_audio_input(content)))
    except Exception:  # noqa: BLE001 # reason: ComfyUI's helper raises unrelated exception types; one reviewed message replaces them.
        raise DreaminaError(ErrorCode.MEDIA, AUDIO_UNREADABLE) from None
    return audio


__all__ = ['decode_audio', 'decode_images', 'decode_video', 'encode_local_file', 'list_local_media']
