"""One model's full specification, as model <canonical> returns it: materials, file limits, outputs, and membership."""

from . import Reply
from pydantic import Field


class CountRange(Reply):
    """How many of something a mode takes.

    Attributes:
        minimum: The fewest.
        maximum: The most.

    """

    minimum: int = Field(alias="min")
    maximum: int = Field(alias="max")


class MaterialLimits(Reply):
    """The file limits of one media type; a limit Dreamina does not give is None.

    Attributes:
        max_file_bytes: The largest file, in bytes.
        min_width_px: The narrowest picture, in pixels.
        max_width_px: The widest picture, in pixels.
        min_height_px: The lowest picture, in pixels.
        max_height_px: The highest picture, in pixels.
        min_duration_ms: The shortest clip, in milliseconds.
        max_duration_ms: The longest clip, in milliseconds.

    """

    max_file_bytes: int | None = Field(default=None, alias="maxFileSizeBytes")
    min_width_px: int | None = Field(default=None, alias="minWidthPx")
    max_width_px: int | None = Field(default=None, alias="maxWidthPx")
    min_height_px: int | None = Field(default=None, alias="minHeightPx")
    max_height_px: int | None = Field(default=None, alias="maxHeightPx")
    min_duration_ms: int | None = Field(default=None, alias="minDurationMs")
    max_duration_ms: int | None = Field(default=None, alias="maxDurationMs")


class MaterialType(Reply):
    """One media type a mode takes.

    Attributes:
        media_type: image, video, or audio.
        count: How many of it.
        limits: Its file limits.

    """

    media_type: str = Field(alias="mediaType")
    count: CountRange
    limits: MaterialLimits | None = None


class MaterialSet(Reply):
    """Everything a mode takes as materials.

    Attributes:
        total_count: How many materials in all.
        types: Each media type.
        max_total_video_ms: The longest all videos together may be, in milliseconds.
        max_total_audio_ms: The longest all audio together may be, in milliseconds.

    """

    total_count: CountRange = Field(alias="totalCount")
    types: tuple[MaterialType, ...] = ()
    max_total_video_ms: int | None = Field(default=None, alias="maxTotalVideoDurationMs")
    max_total_audio_ms: int | None = Field(default=None, alias="maxTotalAudioDurationMs")


class SizeMembership(Reply):
    """Whether one output size needs a paid plan.

    Attributes:
        size: The output size, such as 2K.
        is_vip: Whether it needs a paid plan.

    """

    size: str = Field(alias="resolution")
    is_vip: bool | None = Field(default=None, alias="isVip")


class ModeSpecification(Reply):
    """One mode's full specification.

    Attributes:
        model: The canonical model name.
        mode: The mode.
        scenario: The speech scenario, or None.
        materials: What the mode takes.
        max_batch_count: The most outputs one run makes.
        is_vip: Whether the model needs a paid plan.
        vip_configs: Which output sizes need a paid plan.

    """

    model: str
    mode: str
    scenario: str | None = None
    materials: MaterialSet | None = None
    max_batch_count: int | None = Field(default=None, alias="maxBatchGenCount")
    is_vip: bool | None = Field(default=None, alias="isVip")
    vip_configs: tuple[SizeMembership, ...] | None = Field(default=None, alias="vipConfigs")


class SpecificationMatch(Reply):
    """One match of model <canonical>.

    Attributes:
        kind: What matched, such as generation.
        generation: The mode's specification, for a generation match.

    """

    kind: str
    generation: ModeSpecification | None = None


class SpecificationReply(Reply):
    """The reply of model <canonical>.

    Attributes:
        matches: Every match, one per mode.

    """

    matches: tuple[SpecificationMatch, ...]


__all__ = [
    "CountRange",
    "MaterialLimits",
    "MaterialSet",
    "MaterialType",
    "ModeSpecification",
    "SizeMembership",
    "SpecificationMatch",
    "SpecificationReply",
]
