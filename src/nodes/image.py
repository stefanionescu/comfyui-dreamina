"""Image: Generate, the paid node for every Dreamina model that makes images."""

from typing import override
from comfy_api.latest import io
from .generate import GenerateNode
from ..config.namespace import MENUS, SOCKET_TYPES
from ..config.inputs import INPUT_NAMES, DEFAULT_CEILINGS


class ImageGenerate(GenerateNode):
    """Generate or edit images with any Dreamina image model."""

    kind = "image"
    display_name = "Image: Generate"
    default_ceiling = DEFAULT_CEILINGS["image"]
    list_inputs = frozenset({INPUT_NAMES["IMAGES"]})
    outputs = (
        io.Image.Output("images", display_name="images", is_output_list=True),
        io.Custom(SOCKET_TYPES["REFERENCES"]).Output("references", display_name="references"),
        io.String.Output("result", display_name="result"),
    )

    @classmethod
    @override
    def define_schema(cls) -> io.Schema:
        """Describe the node: its name, its menu, and its inputs."""
        return cls.build_schema(
            category=MENUS["IMAGE"],
            description="Generate or edit images with any Dreamina image model.",
        )


__all__ = ["ImageGenerate"]
