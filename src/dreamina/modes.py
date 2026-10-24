"""Choose the mode entry for a run from arguments or from the connected inputs."""

from __future__ import annotations

from typing import TYPE_CHECKING
from collections import Counter

from ..config.media import MEDIA_TYPES
from ..state.errors import ErrorCode, DreaminaError
from ..config.models import MODES, SCENARIOS, FRAME_IMAGES, SELECTION_KEYS
from ..config.messages.models import (
    NO_MEDIA,
    MODE_LABEL,
    TYPE_LIMITS,
    MODE_UNKNOWN,
    CONNECTED_COUNT,
    MODE_NOT_OFFERED,
    REFERENCE_LIMITS,
    SCENARIO_UNKNOWN,
    NOTHING_CONNECTED,
    REFERENCES_NO_ENTRY,
    SCENARIO_NOT_OFFERED,
)

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from ..state import Json, Kind, MediaKind
    from ..state.models import ModelMode, ListedModel


def _choose_video(connected: Sequence[MediaKind]) -> str:
    """Choose a video mode: text alone, one or two images as frames, and anything else as references."""
    if not connected:
        return MODES['video']['TEXT']
    if len(connected) <= FRAME_IMAGES and all(media == 'image' for media in connected):
        return MODES['video']['FRAMES']
    return MODES['video']['MULTIMODAL']


def _choose_by_inputs(kind: Kind, connected: Sequence[MediaKind]) -> str:
    """Choose the mode name from the connected inputs; for an image node an Element counts as an image."""
    if kind == 'video':
        return _choose_video(connected)
    if kind == 'image':
        return MODES['image']['IMAGES' if any(media in {'image', 'element'} for media in connected) else 'TEXT']
    return MODES['audio']['SPEECH']


def _choose_name(model: ListedModel, kind: Kind, connected: Sequence[MediaKind], arguments: Mapping[str, Json]) -> str:
    """Choose the mode name from arguments, from the model's only mode, or from the connected inputs."""
    names = list(dict.fromkeys(mode.name for mode in model.modes))
    modes = ', '.join(names)
    selected = arguments.get(SELECTION_KEYS['MODE'])
    if selected is not None:
        name = str(selected)
        if name not in names:
            raise DreaminaError(ErrorCode.INVALID_INPUT, MODE_UNKNOWN.format(model=model.name, mode=name, modes=modes))
        return name
    if len({(mode.name, mode.scenario) for mode in model.modes}) == 1:
        return model.modes[0].name
    name = _choose_by_inputs(kind, connected)
    if name not in names:
        raise DreaminaError(ErrorCode.INVALID_INPUT, MODE_NOT_OFFERED.format(model=model.name, mode=name, modes=modes))
    return name


def _choose_scenario(
    model: ListedModel, name: str, connected: Sequence[MediaKind], arguments: Mapping[str, Json]
) -> str | None:
    """Choose the speech scenario of the chosen mode, from arguments or from the connected inputs; None without one."""
    scenarios = list(dict.fromkeys(mode.scenario for mode in model.modes if mode.name == name and mode.scenario))
    if not scenarios:
        return None
    listed = ', '.join(scenarios)
    selected = arguments.get(SELECTION_KEYS['SCENARIO'])
    scenario = str(selected) if selected is not None else SCENARIOS['DUBBING' if connected else 'READING']
    if scenario in scenarios:
        return scenario
    template = SCENARIO_UNKNOWN if selected is not None else SCENARIO_NOT_OFFERED
    raise DreaminaError(ErrorCode.INVALID_INPUT, template.format(model=model.name, scenario=scenario, scenarios=listed))


def _is_fitting(mode: ModelMode, counts: Counter[str]) -> bool:
    """Whether an entry takes the connected inputs: the total, and each connected type within its listed limits."""
    references = mode.references
    if references is None:
        return not counts.total()
    limits = {limit.media_type: limit for limit in references.limits}
    return references.minimum <= counts.total() <= references.maximum and all(
        media in limits and limits[media].minimum <= count <= limits[media].maximum for media, count in counts.items()
    )


def _describe_limits(mode: ModelMode) -> str:
    """Write one entry's reference limits as REFERENCES_NO_ENTRY lists them."""
    references = mode.references
    if references is None:
        return REFERENCE_LIMITS.format(minimum=0, maximum=0, types=NO_MEDIA)
    types = ', '.join(
        TYPE_LIMITS.format(media=limit.media_type, minimum=limit.minimum, maximum=limit.maximum)
        for limit in references.limits
    )
    return REFERENCE_LIMITS.format(minimum=references.minimum, maximum=references.maximum, types=types or NO_MEDIA)


def choose_mode(
    model: ListedModel, kind: Kind, connected: Sequence[MediaKind], arguments: Mapping[str, Json]
) -> tuple[ModelMode, str]:
    """Choose the one mode entry a run uses; of several entries of one mode, the first that takes the connected inputs.

    It returns the entry and the label that refusals name it by: its name, with its scenario when it has one. Every
    entry it chooses from has the chosen name and scenario, so the label fits each of them.

    connected is the kind of every item the run sends, references first. 07 checks every reference rule against the
    entry chosen here.
    """
    name = _choose_name(model, kind, connected, arguments)
    scenario = _choose_scenario(model, name, connected, arguments)
    label = MODE_LABEL.format(name=name, scenario=scenario) if scenario else name
    candidates = [mode for mode in model.modes if mode.name == name and (scenario is None or mode.scenario == scenario)]
    if len(candidates) == 1:
        return candidates[0], label
    counts = Counter(MEDIA_TYPES[media] for media in connected)
    fitting = next((mode for mode in candidates if _is_fitting(mode, counts)), None)
    if fitting is not None:
        return fitting, label
    present = ', '.join(CONNECTED_COUNT.format(media=media, count=count) for media, count in counts.items())
    limits = ' or '.join(_describe_limits(mode) for mode in candidates)
    message = REFERENCES_NO_ENTRY.format(mode=label, connected=present or NOTHING_CONNECTED, limits=limits)
    raise DreaminaError(ErrorCode.INVALID_INPUT, message)


__all__ = ['choose_mode']
