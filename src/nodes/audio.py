"""Audio: Generate, the paid node for every Dreamina model that makes audio."""

from typing import override
from comfy_api.latest import io
from .generate import GenerateNode
from ..config.namespace import MENUS, SOCKET_TYPES
from ..config.inputs import INPUT_NAMES, DEFAULT_CEILINGS


class AudioGenerate(GenerateNode):
    """Make speech, dubbing, or music with any Dreamina audio model."""

    kind = "audio"
    display_name = "Audio: Generate"
    default_ceiling = DEFAULT_CEILINGS["audio"]
    list_inputs = frozenset({INPUT_NAMES["IMAGES"], INPUT_NAMES["AUDIO"]})
    outputs = (
        io.Audio.Output("audio", display_name="audio", is_output_list=True),
        io.Custom(SOCKET_TYPES["REFERENCES"]).Output("references", display_name="references"),
        io.String.Output("result", display_name="result"),
    )

    @classmethod
    @override
    def define_schema(cls) -> io.Schema:
        """Describe the node: its name, its menu, and its inputs."""
        return cls.build_schema(
            category=MENUS["AUDIO"],
            description="Make speech, dubbing, or music with any Dreamina audio model.",
        )


__all__ = ["AudioGenerate"]
