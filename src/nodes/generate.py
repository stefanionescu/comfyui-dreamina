"""The paid node every generation node is: any Dreamina model of its kind, named by its canonical name, and one run."""

from __future__ import annotations

from typing import TYPE_CHECKING, Unpack, ClassVar, TypedDict, override
from functools import partial

from comfy_api.latest import io

from .base import PaidNode
from .outputs import build_node_outputs
from ..comfy.media import list_local_media, encode_local_file
from ..state.errors import DreaminaError
from ..comfy.runtime import get_runtime
from ..config.inputs import TOOLTIPS, INPUT_NAMES, DEFAULT_CEILINGS, ARGUMENTS_TOOLTIPS, CREDIT_CEILING_RANGE
from ..config.models import DEFAULT_MODELS, DEFAULT_ARGUMENTS
from ..comfy.execution import send_run
from ..dreamina.models import find_model
from ..config.namespace import MENUS, NODE_PREFIX, SOCKET_TYPES
from ..dreamina.contract import validate_cli
from ..state.generations import GenerationPlan
from ..dreamina.arguments import choose_prompt, parse_arguments, validate_argument_names
from ..dreamina.generations.operation import GenerationOperation

if TYPE_CHECKING:
    import torch
    from comfy_api.latest import Input

    from ..state import Kind
    from ..state.references import Reference


def _read_queued(value: object) -> str | None:
    """Read a queued text input: a one-item list holding text, or text itself from a direct call; None when linked."""
    if isinstance(value, str):
        return value
    if isinstance(value, (list, tuple)) and len(value) == 1 and isinstance(value[0], str):  # pyright: ignore[reportUnknownArgumentType] # reason: ComfyUI passes queued values untyped.
        return value[0]
    return None


class GenerateSources(TypedDict, total=False):
    """The media sockets and the references a kind node sends; ComfyUI leaves out a socket with nothing connected.

    Attributes:
        references: The connected canvas nodes and resources, in socket order.
        images: The connected ComfyUI images.
        videos: The connected ComfyUI videos.
        audio: The connected ComfyUI audio clips.

    """

    references: tuple[Reference, ...] | None
    images: list[torch.Tensor] | None
    videos: list[Input.Video] | None
    audio: list[Input.Audio] | None


class GenerateNode(PaidNode):
    """Run one generation with any Dreamina model of the node kind and fill the outputs of the node.

    Attributes:
        kind: What the models of the node make; the node refuses a model of another kind before paying.
        display_name: The name of the node in menus, also sent as the title of the canvas node when the prompt is empty.
        menu: The menu that lists the node.
        description: What the node does, as ComfyUI shows it.
        default_ceiling: The starting credit_ceiling: the default model's quote at its starting arguments.
        outputs: The output sockets of the node in order; build_node_outputs fills them by ID.

    """

    kind: ClassVar[Kind]
    display_name: ClassVar[str]
    menu: ClassVar[str]
    description: ClassVar[str]
    default_ceiling: ClassVar[int]
    outputs: ClassVar[tuple[io.Output, ...]]

    @classmethod
    @override
    def define_schema(cls) -> io.Schema:
        """Describe a kind node: its media sockets, references, model, ceiling, run number, prompt, and arguments."""
        media = (
            io.Image.Input(INPUT_NAMES['IMAGES'], optional=True, tooltip=TOOLTIPS['IMAGES']),
            io.Video.Input(INPUT_NAMES['VIDEOS'], optional=True, tooltip=TOOLTIPS['VIDEOS']),
            io.Audio.Input(INPUT_NAMES['AUDIO'], optional=True, tooltip=TOOLTIPS['AUDIO']),
        )
        inputs: list[io.Input] = [
            *(item for item in media if item.id in cls.list_inputs),
            io.Custom(SOCKET_TYPES['REFERENCES']).Input(
                INPUT_NAMES['REFERENCES'], optional=True, tooltip=TOOLTIPS['REFERENCES']
            ),
            io.String.Input(INPUT_NAMES['MODEL'], default=DEFAULT_MODELS[cls.kind], tooltip=TOOLTIPS['MODEL']),
            io.Int.Input(
                INPUT_NAMES['CREDIT_CEILING'],
                default=cls.default_ceiling,
                min=CREDIT_CEILING_RANGE['MIN'],
                max=CREDIT_CEILING_RANGE['MAX'],
                tooltip=TOOLTIPS['CREDIT_CEILING'],
            ),
            cls.run_number_input,
            io.String.Input(INPUT_NAMES['PROMPT'], default='', multiline=True, tooltip=TOOLTIPS['PROMPT']),
            io.String.Input(
                INPUT_NAMES['ARGUMENTS'],
                default=DEFAULT_ARGUMENTS[cls.kind],
                multiline=True,
                tooltip=ARGUMENTS_TOOLTIPS[cls.kind],
            ),
        ]
        return io.Schema(
            node_id=f'{NODE_PREFIX}{cls.__name__}',
            display_name=cls.display_name,
            category=cls.menu,
            description=cls.description,
            inputs=inputs,
            outputs=list(cls.outputs),
            is_input_list=True,
            hidden=[io.Hidden.unique_id],
        )

    @classmethod
    @override
    async def validate_inputs(  # pyright: ignore[reportIncompatibleMethodOverride] # reason: ComfyUI calls by schema.
        cls, model: object = None, prompt: object = None, arguments: object = None
    ) -> bool | str:
        """Make the free checks a typed model allows when the person queues the workflow.

        These checks come before any node runs or bills. A linked value is unknown until the workflow runs, and send
        makes its checks then. ComfyUI skips its own checks only for the inputs named here, so credit_ceiling and
        run_number keep their range checks.
        """
        name, text, typed = _read_queued(model), _read_queued(arguments), _read_queued(prompt)
        if name is None:
            return True
        try:
            await validate_cli()
            values = parse_arguments(text) if text is not None else {}
            validate_argument_names(await find_model(name, cls.kind), values)
            if typed is not None:
                choose_prompt(typed, values)
        except DreaminaError as error:
            return str(error)
        return True

    @classmethod
    @override
    async def send(
        cls,
        *,
        model: str,
        credit_ceiling: int,
        prompt: str = '',
        arguments: str = '',
        **sources: Unpack[GenerateSources],
    ) -> io.NodeOutput:
        """Run one generation and fill the outputs; the operation makes every check again, because a link skips them.

        ComfyUI sets hidden on the class it runs; a direct call from another pack has no node ID and no progress bar.
        """
        node_id = cls.hidden.unique_id if cls.hidden is not None else None  # pyright: ignore[reportUnnecessaryComparison] # reason: ComfyUI types hidden as always set, but a direct call runs the class itself, whose hidden is None.
        plan = GenerationPlan(
            kind=cls.kind,
            title=cls.display_name,
            model=model.strip(),
            prompt=prompt,
            arguments=arguments,
            credit_ceiling=credit_ceiling,
            references=sources.get('references') or (),
            local=list_local_media(
                sources.get('images') or (), sources.get('videos') or (), sources.get('audio') or ()
            ),
        )
        runtime = get_runtime()
        operation = GenerationOperation(plan, runtime.generations, runtime.canvas, encode_local_file)
        output_ids = tuple(output.id for output in cls.outputs if output.id is not None)
        return await send_run(operation.send, partial(build_node_outputs, output_ids=output_ids), node_id)


class ImageGenerate(GenerateNode):
    """Generate or edit images with any Dreamina image model."""

    kind = 'image'
    display_name = 'Image: Generate'
    list_inputs = frozenset({INPUT_NAMES['IMAGES']})
    menu = MENUS['IMAGE']
    description = 'Generate or edit images with any Dreamina image model.'
    default_ceiling = DEFAULT_CEILINGS['image']
    outputs = (
        io.Image.Output('images', display_name='images', is_output_list=True),
        io.Custom(SOCKET_TYPES['REFERENCES']).Output('references', display_name='references'),
        io.String.Output('result', display_name='result'),
    )


class VideoGenerate(GenerateNode):
    """Generate a video from a prompt, frames, or references with any Dreamina video model."""

    kind = 'video'
    display_name = 'Video: Generate'
    list_inputs = frozenset({INPUT_NAMES['IMAGES'], INPUT_NAMES['VIDEOS'], INPUT_NAMES['AUDIO']})
    menu = MENUS['VIDEO']
    description = 'Generate a video from a prompt, frames, or references with any Dreamina video model.'
    default_ceiling = DEFAULT_CEILINGS['video']
    outputs = (
        io.Video.Output('video', display_name='video', is_output_list=True),
        io.Custom(SOCKET_TYPES['REFERENCES']).Output('references', display_name='references'),
        io.String.Output('result', display_name='result'),
    )


class AudioGenerate(GenerateNode):
    """Make speech, dubbing, or music with any Dreamina audio model."""

    kind = 'audio'
    display_name = 'Audio: Generate'
    list_inputs = frozenset({INPUT_NAMES['IMAGES'], INPUT_NAMES['AUDIO']})
    menu = MENUS['AUDIO']
    description = 'Make speech, dubbing, or music with any Dreamina audio model.'
    default_ceiling = DEFAULT_CEILINGS['audio']
    outputs = (
        io.Audio.Output('audio', display_name='audio', is_output_list=True),
        io.Custom(SOCKET_TYPES['REFERENCES']).Output('references', display_name='references'),
        io.String.Output('result', display_name='result'),
    )


__all__ = ['AudioGenerate', 'GenerateNode', 'ImageGenerate', 'VideoGenerate']
