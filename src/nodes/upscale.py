"""Image: Upscale, the paid node for Dreamina's upscale of image nodes and ComfyUI images."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, ClassVar, override

from comfy_api.latest import io
from comfy_execution.graph import ExecutionBlocker

from .base import PaidNode
from .outputs import build_result_document
from ..comfy.media import decode_images, list_local_media, encode_local_file
from ..comfy.runtime import get_runtime
from ..config.inputs import INPUT_NAMES, CREDIT_CEILING_RANGE
from ..comfy.execution import send_run
from ..config.namespace import MENUS, NODE_PREFIX, SOCKET_TYPES
from ..dreamina.upscale import UpscaleOperation
from ..state.references import Reference
from ..state.generations import UpscaleRequest
from ..config.generations import UPSCALE_MODES, UPSCALE_DETAIL, UPSCALE_CEILING, UPSCALE_SETTINGS, UPSCALE_RESOLUTIONS

if TYPE_CHECKING:
    from collections.abc import Sequence

    import torch

    from ..state import Json
    from ..state.generations import GenerationResult

_REFERENCES = io.Custom(SOCKET_TYPES['REFERENCES'])
# The outputs of the node in order; each label equals its ID.
_OUTPUTS = (
    io.Image.Output('images', display_name='images', is_output_list=True),
    _REFERENCES.Output('references', display_name='references'),
    io.String.Output('result', display_name='result'),
)
# The name of the node in menus, also the title of each image node it imports.
_DISPLAY_NAME = 'Image: Upscale'
# The mode dropdown: pro shows its resolution and detail, and normal takes neither.
_MODE = io.DynamicCombo.Input(
    UPSCALE_SETTINGS['MODE'],
    options=[
        io.DynamicCombo.Option(
            UPSCALE_MODES[0],
            [
                io.Combo.Input(
                    UPSCALE_SETTINGS['RESOLUTION'],
                    options=list(UPSCALE_RESOLUTIONS),
                    default=UPSCALE_RESOLUTIONS[0],
                    tooltip='The size of the result. Larger costs more.',
                ),
                io.Int.Input(
                    UPSCALE_SETTINGS['DETAIL'],
                    default=UPSCALE_DETAIL['DEFAULT'],
                    min=UPSCALE_DETAIL['MIN'],
                    max=UPSCALE_DETAIL['MAX'],
                    tooltip='How much fine detail the upscale adds, from 1 to 100.',
                ),
            ],
        ),
        io.DynamicCombo.Option(UPSCALE_MODES[1], []),
    ],
    tooltip='pro redraws each image larger with fine detail; normal enlarges it to twice its size.',
)


def _build_upscale_outputs(results: Sequence[GenerationResult]) -> io.NodeOutput:
    """Fill the outputs in source order: one image, one canvas node, and one result document per source."""
    contents = [file.content for result in results for file in result.files if file.kind == 'image']
    references = tuple(
        Reference(origin='node', value=result.record.node_id, media='image', title=result.title) for result in results
    )
    document = json.dumps([build_result_document(result) for result in results], indent=2, ensure_ascii=False)
    return io.NodeOutput(
        list(decode_images(contents)) if contents else ExecutionBlocker(None),
        references or ExecutionBlocker(None),
        document,
    )


class ImageUpscale(PaidNode):
    """Make images larger and sharper with Dreamina's upscale."""

    list_inputs: ClassVar[frozenset[str]] = frozenset({INPUT_NAMES['IMAGES'], INPUT_NAMES['REFERENCES']})

    @classmethod
    @override
    def define_schema(cls) -> io.Schema:
        """Describe the node: images and references in, the ceiling and the mode, one image out per source."""
        inputs: list[io.Input] = [
            io.Image.Input(
                INPUT_NAMES['IMAGES'],
                optional=True,
                tooltip='ComfyUI images to upscale. Each is uploaded to your Dreamina canvas first.',
            ),
            _REFERENCES.Input(
                INPUT_NAMES['REFERENCES'],
                optional=True,
                tooltip=(
                    'Images from Image: Generate or Image: Upscale, upscaled where they are, with no upload. They '
                    'go before images.'
                ),
            ),
            io.Int.Input(
                INPUT_NAMES['CREDIT_CEILING'],
                default=UPSCALE_CEILING,
                min=CREDIT_CEILING_RANGE['MIN'],
                max=CREDIT_CEILING_RANGE['MAX'],
                tooltip=(
                    'The most credits this upscale may cost, for all its images together. Above it, Dreamina runs '
                    'nothing and bills nothing.'
                ),
            ),
            _MODE,
            cls.run_number_input,
        ]
        return io.Schema(
            node_id=f'{NODE_PREFIX}{cls.__name__}',
            display_name=_DISPLAY_NAME,
            category=MENUS['IMAGE'],
            description="Make images larger and sharper with Dreamina's upscale.",
            inputs=inputs,
            outputs=list(_OUTPUTS),
            is_input_list=True,
            hidden=[io.Hidden.unique_id],
        )

    @classmethod
    @override
    async def send(
        cls,
        *,
        credit_ceiling: int,
        mode: dict[str, Json],
        images: list[torch.Tensor] | None = None,
        references: list[tuple[Reference, ...]] | None = None,
    ) -> io.NodeOutput:
        """Upscale every source and fill the outputs; the operation checks everything again, because a link skips it.

        ComfyUI sets hidden on the class it runs; a direct call from another pack has no node ID and no progress bar.
        """
        node_id = cls.hidden.unique_id if cls.hidden is not None else None  # pyright: ignore[reportUnnecessaryComparison] # reason: ComfyUI types hidden as always set, but a direct call runs the class itself, whose hidden is None.
        request = UpscaleRequest(
            images=list_local_media(images or (), (), ()),
            references=tuple(reference for group in references or () for reference in group),
            credit_ceiling=credit_ceiling,
            settings=mode,
            title=_DISPLAY_NAME,
        )
        runtime = get_runtime()
        operation = UpscaleOperation(request, runtime.generations, runtime.canvas, encode_local_file)
        return await send_run(operation.send, _build_upscale_outputs, node_id)


__all__ = ['ImageUpscale']
