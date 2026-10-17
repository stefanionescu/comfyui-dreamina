"""The paid node every generation node is: any Dreamina model of its kind, named by its canonical name, and one run."""

from __future__ import annotations

from .base import PaidNode
from functools import partial
from comfy_api.latest import io
from ..comfy.execution import send_run
from ..comfy.runtime import get_runtime
from .outputs import build_node_outputs
from ..dreamina.models import find_model
from ..types.errors import DreaminaError
from ..dreamina.contract import validate_cli
from ..types.generations import GenerationPlan
from typing import TYPE_CHECKING, ClassVar, override
from ..config.namespace import NODE_PREFIX, SOCKET_TYPES
from ..comfy.media import encode_local_file, list_local_media
from ..config.models import DEFAULT_MODELS, DEFAULT_ARGUMENTS
from ..dreamina.generations.operation import GenerationOperation
from ..dreamina.arguments import choose_prompt, parse_arguments, validate_argument_names
from ..config.inputs import TOOLTIPS, RUN_NUMBER, INPUT_NAMES, ARGUMENTS_TOOLTIPS, CREDIT_CEILING_RANGE

if TYPE_CHECKING:
    import torch
    from ..types import Kind
    from comfy_api.latest import Input
    from ..types.references import Reference


def _read_queued(value: object) -> str | None:
    """Read a queued text input: a one-item list holding text, or text itself from a direct call; None when linked."""
    if isinstance(value, str):
        return value
    if isinstance(value, (list, tuple)) and len(value) == 1 and isinstance(value[0], str):  # pyright: ignore[reportUnknownArgumentType] -- reason: ComfyUI passes queued values untyped.
        return value[0]
    return None


class GenerateNode(PaidNode):
    """Run one generation with any Dreamina model of the node's kind and fill the node's outputs.

    Attributes:
        kind: What the node's models make; a model of another kind is refused before paying.
        display_name: The node's name in menus, also sent as the canvas node's title when the prompt is empty.
        default_ceiling: The starting credit_ceiling: the default model's quote at its starting arguments.
        outputs: The node's output sockets in order; build_node_outputs fills them by ID.

    """

    kind: ClassVar[Kind]
    display_name: ClassVar[str]
    default_ceiling: ClassVar[int]
    outputs: ClassVar[tuple[io.Output, ...]]

    @classmethod
    def build_schema(cls, *, category: str, description: str) -> io.Schema:
        """Describe a kind node: its media sockets, references, model, ceiling, run number, prompt, and arguments."""
        media = (
            io.Image.Input(INPUT_NAMES["IMAGES"], optional=True, tooltip=TOOLTIPS["IMAGES"]),
            io.Video.Input(INPUT_NAMES["VIDEOS"], optional=True, tooltip=TOOLTIPS["VIDEOS"]),
            io.Audio.Input(INPUT_NAMES["AUDIO"], optional=True, tooltip=TOOLTIPS["AUDIO"]),
        )
        inputs: list[io.Input] = [
            *(item for item in media if item.id in cls.list_inputs),
            io.Custom(SOCKET_TYPES["REFERENCES"]).Input(
                INPUT_NAMES["REFERENCES"], optional=True, tooltip=TOOLTIPS["REFERENCES"]
            ),
            io.String.Input(INPUT_NAMES["MODEL"], default=DEFAULT_MODELS[cls.kind], tooltip=TOOLTIPS["MODEL"]),
            io.Int.Input(
                INPUT_NAMES["CREDIT_CEILING"],
                default=cls.default_ceiling,
                min=CREDIT_CEILING_RANGE["MIN"],
                max=CREDIT_CEILING_RANGE["MAX"],
                tooltip=TOOLTIPS["CREDIT_CEILING"],
            ),
            io.Int.Input(
                INPUT_NAMES["RUN_NUMBER"],
                default=RUN_NUMBER["DEFAULT"],
                min=RUN_NUMBER["MIN"],
                max=RUN_NUMBER["MAX"],
                tooltip=TOOLTIPS["RUN_NUMBER"],
            ),
            io.String.Input(INPUT_NAMES["PROMPT"], default="", multiline=True, tooltip=TOOLTIPS["PROMPT"]),
            io.String.Input(
                INPUT_NAMES["ARGUMENTS"],
                default=DEFAULT_ARGUMENTS[cls.kind],
                multiline=True,
                tooltip=ARGUMENTS_TOOLTIPS[cls.kind],
            ),
        ]
        return io.Schema(
            node_id=f"{NODE_PREFIX}{cls.__name__}",
            display_name=cls.display_name,
            category=category,
            description=description,
            inputs=inputs,
            outputs=list(cls.outputs),
            is_input_list=True,
            hidden=[io.Hidden.unique_id],
        )

    @classmethod
    @override
    async def validate_inputs(  # pyright: ignore[reportIncompatibleMethodOverride] -- reason: ComfyUI calls by schema.
        cls, model: object = None, prompt: object = None, arguments: object = None
    ) -> bool | str:
        """Make the free checks a typed model allows when the workflow is queued, before any node runs or bills.

        A linked value is unknown until the workflow runs, and send makes its checks then. ComfyUI skips its own checks
        only for the inputs named here, so credit_ceiling and run_number keep their range checks.
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
    async def send(  # noqa: PLR0913 -- reason: ComfyUI requires one named argument for each saved node input.
        cls,
        *,
        model: str,
        credit_ceiling: int,
        prompt: str = "",
        arguments: str = "",
        references: tuple[Reference, ...] | None = None,
        images: list[torch.Tensor] | None = None,
        videos: list[Input.Video] | None = None,
        audio: list[Input.Audio] | None = None,
    ) -> io.NodeOutput:
        """Run one generation and fill the outputs; the operation makes every check again, since a link skips them.

        ComfyUI sets hidden on the class it runs; a direct call from another pack has no node ID and no progress bar.
        """
        node_id = cls.hidden.unique_id if cls.hidden is not None else None  # pyright: ignore[reportUnnecessaryComparison] -- reason: ComfyUI types hidden as always set, but a direct call runs the class itself, whose hidden is None.
        plan = GenerationPlan(
            kind=cls.kind,
            title=cls.display_name,
            model=model.strip(),
            prompt=prompt,
            arguments=arguments,
            credit_ceiling=credit_ceiling,
            references=references or (),
            local=list_local_media(images or (), videos or (), audio or ()),
        )
        runtime = get_runtime()
        operation = GenerationOperation(plan, runtime.generations, runtime.canvas, encode_local_file)
        output_ids = tuple(output.id for output in cls.outputs)
        return await send_run(operation, partial(build_node_outputs, output_ids=output_ids), node_id)


__all__ = ["GenerateNode"]
