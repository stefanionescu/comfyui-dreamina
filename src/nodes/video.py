"""Video: Generate, the paid node for every Dreamina model that makes a video."""

from typing import override
from comfy_api.latest import io
from .generate import GenerateNode
from ..config.namespace import MENUS, SOCKET_TYPES
from ..config.inputs import INPUT_NAMES, DEFAULT_CEILINGS


class VideoGenerate(GenerateNode):
    """Generate a video from a prompt, frames, or references with any Dreamina video model."""

    kind = "video"
    display_name = "Video: Generate"
    default_ceiling = DEFAULT_CEILINGS["video"]
    list_inputs = frozenset({INPUT_NAMES["IMAGES"], INPUT_NAMES["VIDEOS"], INPUT_NAMES["AUDIO"]})
    outputs = (
        io.Video.Output("video", display_name="video", is_output_list=True),
        io.Custom(SOCKET_TYPES["REFERENCES"]).Output("references", display_name="references"),
        io.String.Output("result", display_name="result"),
    )

    @classmethod
    @override
    def define_schema(cls) -> io.Schema:
        """Describe the node: its name, its menu, and its inputs."""
        return cls.build_schema(
            category=MENUS["VIDEO"],
            description="Generate a video from a prompt, frames, or references with any Dreamina video model.",
        )


__all__ = ["VideoGenerate"]
