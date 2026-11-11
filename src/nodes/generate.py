"""The paid node every generation node is: any Dreamina model of its kind, named by its canonical name, and one run."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, cast, override
from functools import partial

from comfy_api.latest import io

from .base import PaidNode
from .outputs import build_node_outputs
from ..comfy.media import list_local_media, encode_local_file
from ..state.errors import DreaminaError
from ..comfy.runtime import get_runtime
from ..config.inputs import FLAGS, LINES, TOOLTIPS, INPUT_NAMES, FLAG_MINIMUMS, DEFAULT_CEILINGS, CREDIT_CEILING_RANGE
from ..config.models import DEFAULT_MODELS
from ..comfy.execution import send_run
from ..dreamina.models import find_model
from ..config.namespace import MENUS, NODE_PREFIX, SOCKET_TYPES
from ..dreamina.contract import validate_cli
from ..state.generations import GenerationPlan
from ..dreamina.arguments import add_flags, choose_prompt, parse_arguments, validate_argument_names
from ..dreamina.generations.operation import GenerationOperation

if TYPE_CHECKING:
    from collections.abc import Mapping

    import torch
    from comfy_api.latest import Input

    from ..state import Json, Kind
    from ..state.references import Reference


def _read_queued(value: object) -> object:
    """Read a queued input: the item of a one-item list, or a plain value from a direct call; None when linked.

    Args:
        value: What ComfyUI passed for the input when the person queued the workflow.

    Returns:
        The value, or None when the input is linked.

    """
    if isinstance(value, (list, tuple)):
        items = cast('list[object]', value)
        return items[0] if len(items) == 1 else None
    return value


def _build_flag(name: str, *, start: str | int) -> io.Input:
    """Build one flag input: a whole number from the flag's least value, or a line of text.

    Args:
        name: The name of the flag input.
        start: The default of the input; a whole number makes a number input, and text makes a text input.

    Returns:
        The input.

    """
    if isinstance(start, int):
        return io.Int.Input(name, default=start, min=FLAG_MINIMUMS[name], tooltip=TOOLTIPS[name])
    return io.String.Input(name, default=start, tooltip=TOOLTIPS[name])


def _read_flags(kind: Kind, inputs: Mapping[str, object]) -> dict[str, Json]:
    """Read the flag inputs of a node by CLI flag name; a linked value, or a line left empty, sends nothing.

    An input names its flag with underscores for dashes, so voice_name sends --voice-name.

    Args:
        kind: The kind of the node, which decides its flag inputs.
        inputs: The inputs of the node by name.

    Returns:
        The values to send, by flag name without the leading dashes.

    """
    flags: dict[str, Json] = {}
    for name in (*FLAGS[kind], *LINES[kind]):
        value = _read_queued(inputs.get(name))
        if value is not None and value != '':
            flags[name.replace('_', '-')] = cast('Json', value)
    return flags


class GenerateNode(PaidNode):
    """Run one generation with any Dreamina model of the node kind and fill the outputs of the node.

    Attributes:
        kind: What the models of the node make; the node refuses a model of another kind before paying.
        display_name: The name of the node in menus, also sent as the title of the canvas node when the prompt is empty.
        menu: The menu that lists the node.
        description: What the node does, as ComfyUI shows it.
        default_ceiling: The starting credit_ceiling: the default model's quote at its starting flags.
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
        """Describe a kind node: media sockets, references, model, ceiling, flags, run number, then the text inputs.

        Returns:
            The schema of the kind node.

        """
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
            *(_build_flag(name, start=start) for name, start in FLAGS[cls.kind].items()),
            cls.run_number_input,
            *(io.String.Input(name, default=start, tooltip=TOOLTIPS[name]) for name, start in LINES[cls.kind].items()),
            io.String.Input(INPUT_NAMES['PROMPT'], default='', multiline=True, tooltip=TOOLTIPS['PROMPT']),
            io.String.Input(INPUT_NAMES['ARGUMENTS'], default='', multiline=True, tooltip=TOOLTIPS['ARGUMENTS']),
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
    async def validate_inputs(cls, **inputs: object) -> bool | str:  # pyright: ignore[reportIncompatibleMethodOverride] # reason: ComfyUI passes every input by name, the flags with dashes included.
        """Make the free checks a typed model allows when the person queues the workflow, before anything bills.

        A linked value is unknown until the workflow runs, and send makes its checks then. The flag inputs differ by
        kind, so this validator takes every input by name. ComfyUI then skips its own range checks, and the operation
        checks each value against the model before paying.

        Args:
            **inputs: Every input of the node by name, as queued.

        Returns:
            True, or the message of the check that failed.

        """
        name, text, typed = (_read_queued(inputs.get(INPUT_NAMES[key])) for key in ('MODEL', 'ARGUMENTS', 'PROMPT'))
        if not isinstance(name, str):
            return True
        try:
            await validate_cli()
            arguments = parse_arguments(text) if isinstance(text, str) else {}
            values = add_flags(_read_flags(cls.kind, inputs), arguments)
            validate_argument_names(await find_model(name, cls.kind), values)
            if isinstance(typed, str):
                choose_prompt(typed, values)
        except DreaminaError as error:
            return str(error)
        return True

    @classmethod
    @override
    async def send(cls, **inputs: object) -> io.NodeOutput:
        """Run one generation and fill the outputs; the operation makes every check again, because a link skips them.

        ComfyUI sets hidden on the class it runs; a direct call from another pack has no node ID and no progress bar.
        ComfyUI leaves out a socket with nothing connected.

        Args:
            **inputs: Every saved input of the node by name, without the run number.

        Returns:
            The outputs of the node.

        """
        node_id = cls.hidden.unique_id if cls.hidden is not None else None  # pyright: ignore[reportUnnecessaryComparison] # reason: ComfyUI types hidden as always set, but a direct call runs the class itself, whose hidden is None.
        plan = GenerationPlan(
            kind=cls.kind,
            title=cls.display_name,
            model=str(inputs.get(INPUT_NAMES['MODEL'], DEFAULT_MODELS[cls.kind])).strip(),
            prompt=str(inputs.get(INPUT_NAMES['PROMPT']) or ''),
            flags=_read_flags(cls.kind, inputs),
            arguments=str(inputs.get(INPUT_NAMES['ARGUMENTS']) or ''),
            credit_ceiling=cast('int', inputs.get(INPUT_NAMES['CREDIT_CEILING'], cls.default_ceiling)),
            references=cast('tuple[Reference, ...] | None', inputs.get(INPUT_NAMES['REFERENCES'])) or (),
            local=list_local_media(
                cast('list[torch.Tensor] | None', inputs.get(INPUT_NAMES['IMAGES'])) or (),
                cast('list[Input.Video] | None', inputs.get(INPUT_NAMES['VIDEOS'])) or (),
                cast('list[Input.Audio] | None', inputs.get(INPUT_NAMES['AUDIO'])) or (),
            ),
        )
        runtime = get_runtime()
        operation = GenerationOperation(plan, runtime.generations, runtime.canvas, encode_local_file)
        output_ids = tuple(output.id for output in cls.outputs if output.id is not None)
        return await send_run(operation.send, partial(build_node_outputs, output_ids=output_ids), node_id)


class ImageGenerate(GenerateNode):
    """Generate or edit images with any Dreamina image model.

    Attributes:
        kind: The node takes image models.
        display_name: The name of the image node in menus.
        list_inputs: Only the images socket takes a list.
        menu: The image menu.
        description: What the image node does, as ComfyUI shows it.
        default_ceiling: The starting credit ceiling of an image run.
        outputs: The images, their references, and the result document.

    """

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
    """Generate a video from a prompt, frames, or references with any Dreamina video model.

    Attributes:
        kind: The node takes video models.
        display_name: The name of the video node in menus.
        list_inputs: The images, videos, and audio sockets each take a list.
        menu: The video menu.
        description: What the video node does, as ComfyUI shows it.
        default_ceiling: The starting credit ceiling of a video run.
        outputs: The video, its references, and the result document.

    """

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
    """Make speech, dubbing, or music with any Dreamina audio model.

    Attributes:
        kind: The node takes audio models.
        display_name: The name of the audio node in menus.
        list_inputs: The images and audio sockets each take a list.
        menu: The audio menu.
        description: What the audio node does, as ComfyUI shows it.
        default_ceiling: The starting credit ceiling of an audio run.
        outputs: The audio, its references, and the result document.

    """

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
