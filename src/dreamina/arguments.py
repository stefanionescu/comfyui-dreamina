"""Check the arguments and prompt of a generation node against the model's flags, and build the run call's flags.

Every refusal comes before any upload or payment. Each check reads a field of the live model list.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

from ..state.errors import ErrorCode, DreaminaError
from ..config.models import COUNT_FLAG, COUNT_VALUE, FLAG_PREFIX, PROMPT_FLAG, SELECTION_KEYS
from ..state.parsing import parse_json
from ..config.messages.inputs import (
    JSON_SHAPES,
    PROMPT_TWICE,
    ARGUMENTS_SHAPE,
    PROMPT_REQUIRED,
    PROMPT_TOO_LONG,
    PROMPT_TOO_SHORT,
    ARGUMENTS_INVALID,
)
from ..config.messages.models import (
    VALUE_STEP,
    VALUE_TYPE,
    VALUE_NUMBER,
    FLAG_REQUIRED,
    VALUE_CHOICES,
    VALUE_TOO_LOW,
    VALUE_TOO_HIGH,
    VALUE_TOO_LONG,
    ARGUMENT_DASHES,
    VALUE_TOO_SHORT,
    ARGUMENT_UNKNOWN,
    FLAG_NOT_IN_MODE,
)
from ..config.messages.requests import JSON_SYNTAX

if TYPE_CHECKING:
    from collections.abc import Mapping

    from ..state import Json
    from ..state.models import ModelFlag, ModelMode, ListedModel

# How a refusal names a JSON value, by its exact Python type as parse_json makes it.
_SHAPES: dict[type, str] = {
    bool: 'boolean',
    int: 'number',
    float: 'number',
    str: 'string',
    list: 'array',
    dict: 'object',
    type(None): 'null',
}


def _format_number(number: float) -> str:
    """Write a number as the CLI receives it: a whole number without a decimal part."""
    whole = int(number)
    if whole == number:
        return str(whole)
    return str(number)


def _format_value(name: str, value: Json) -> str:
    """Write one value as the text the CLI receives; the node sends only text and numbers."""
    if isinstance(value, bool) or not isinstance(value, (str, int, float)):
        raise DreaminaError(
            ErrorCode.INVALID_INPUT, VALUE_TYPE.format(flag=name, shape=JSON_SHAPES[_SHAPES[type(value)]])
        )
    return value if isinstance(value, str) else _format_number(value)


def _validate_number(name: str, flag: ModelFlag, text: str) -> None:
    """Check a value against its flag's minimum, maximum, and step; the step counts from the minimum or from 0."""
    try:
        number = float(text)
    except ValueError:
        number = math.nan
    if not math.isfinite(number):
        raise DreaminaError(ErrorCode.INVALID_INPUT, VALUE_NUMBER.format(flag=name, value=text))
    if flag.minimum is not None and number < flag.minimum:
        message = VALUE_TOO_LOW.format(flag=name, minimum=_format_number(flag.minimum), value=text)
        raise DreaminaError(ErrorCode.INVALID_INPUT, message)
    if flag.maximum is not None and number > flag.maximum:
        message = VALUE_TOO_HIGH.format(flag=name, maximum=_format_number(flag.maximum), value=text)
        raise DreaminaError(ErrorCode.INVALID_INPUT, message)
    base = flag.minimum or 0
    steps = (number - base) / flag.step if flag.step else 0
    if not math.isclose(steps, round(steps), abs_tol=1e-9):
        lower = base + math.floor(steps) * (flag.step or 0)
        upper = lower + (flag.step or 0)
        step = _format_number(flag.step or 0)
        message = VALUE_STEP.format(
            flag=name, step=step, value=text, lower=_format_number(lower), upper=_format_number(upper)
        )
        raise DreaminaError(ErrorCode.INVALID_INPUT, message)


def _validate_value(name: str, flag: ModelFlag, value: Json) -> str:
    """Check one value against its flag's listed values, length, and numeric bounds, and return it as sent."""
    text = _format_value(name, value)
    if flag.values is not None and text not in flag.values:
        message = VALUE_CHOICES.format(flag=name, value=text, values=', '.join(flag.values))
        raise DreaminaError(ErrorCode.INVALID_INPUT, message)
    if flag.min_length is not None and len(text) < flag.min_length:
        message = VALUE_TOO_SHORT.format(flag=name, minimum=flag.min_length, count=len(text))
        raise DreaminaError(ErrorCode.INVALID_INPUT, message)
    if flag.max_length is not None and len(text) > flag.max_length:
        message = VALUE_TOO_LONG.format(flag=name, maximum=flag.max_length, count=len(text))
        raise DreaminaError(ErrorCode.INVALID_INPUT, message)
    if (flag.minimum, flag.maximum, flag.step) != (None, None, None):
        _validate_number(name, flag, text)
    return text


def _validate_prompt(model: str, flag: ModelFlag, prompt: str) -> None:
    """Check the prompt's length against the entry's prompt flag, naming the model and how much is over."""
    count = len(prompt)
    if flag.min_length is not None and count < flag.min_length:
        message = PROMPT_TOO_SHORT.format(count=count, model=model, minimum=flag.min_length)
        raise DreaminaError(ErrorCode.INVALID_INPUT, message)
    if flag.max_length is not None and count > flag.max_length:
        excess = count - flag.max_length
        message = PROMPT_TOO_LONG.format(count=count, model=model, maximum=flag.max_length, excess=excess)
        raise DreaminaError(ErrorCode.INVALID_INPUT, message)


def _build_mode_flags(model: str, mode: ModelMode, label: str, prompt: str, flag: ModelFlag | None) -> list[str]:
    """Start the call with the entry's mode and scenario, and check the prompt against the entry's prompt flag."""
    built = [FLAG_PREFIX + SELECTION_KEYS['MODE'], mode.name]
    if mode.scenario:
        built += [FLAG_PREFIX + SELECTION_KEYS['SCENARIO'], mode.scenario]
    if flag is not None and flag.required and not prompt:
        raise DreaminaError(ErrorCode.INVALID_INPUT, PROMPT_REQUIRED.format(mode=label))
    if flag is not None and prompt:
        _validate_prompt(model, flag, prompt)
    return built


def parse_arguments(text: str) -> dict[str, Json]:
    """Read the arguments box as one JSON object, keys in the person's order; empty text is an empty object."""
    if not text.strip():
        return {}
    try:
        value = parse_json(text)
    except DreaminaError as error:
        if str(error) != JSON_SYNTAX:
            raise
        raise DreaminaError(ErrorCode.INVALID_INPUT, ARGUMENTS_INVALID.format()) from None
    if not isinstance(value, dict):
        shape = JSON_SHAPES[_SHAPES[type(value)]]
        raise DreaminaError(ErrorCode.INVALID_INPUT, ARGUMENTS_SHAPE.format(shape=shape))
    return value


def validate_argument_names(model: ListedModel, arguments: Mapping[str, Json]) -> None:
    """Refuse a key no entry of the model lists, or one written with dashes; it needs nothing connected."""
    flags = list(dict.fromkeys(flag.name.removeprefix(FLAG_PREFIX) for mode in model.modes for flag in mode.flags))
    selection = [SELECTION_KEYS['MODE']]
    if any(mode.scenario for mode in model.modes):
        selection.append(SELECTION_KEYS['SCENARIO'])
    allowed = {*flags, PROMPT_FLAG, *selection}
    for key in arguments:
        if key.startswith('-'):
            raise DreaminaError(ErrorCode.INVALID_INPUT, ARGUMENT_DASHES.format(flag=key, name=key.lstrip('-')))
        if key not in allowed:
            listed = ', '.join(name for name in flags if name not in SELECTION_KEYS.values())
            message = ARGUMENT_UNKNOWN.format(model=model.name, flag=key, flags=listed)
            raise DreaminaError(ErrorCode.INVALID_INPUT, message)


def choose_prompt(prompt: str, arguments: Mapping[str, Json]) -> str:
    """Return the one prompt a run sends: from the prompt box or from arguments, never both."""
    has_text = bool(prompt.strip())
    if PROMPT_FLAG not in arguments:
        return prompt if has_text else ''
    if has_text:
        raise DreaminaError(ErrorCode.INVALID_INPUT, PROMPT_TWICE)
    value = arguments[PROMPT_FLAG]
    if not isinstance(value, str):
        shape = JSON_SHAPES[_SHAPES[type(value)]]
        raise DreaminaError(ErrorCode.INVALID_INPUT, VALUE_TYPE.format(flag=PROMPT_FLAG, shape=shape))
    return value


def build_flags(model: str, mode: ModelMode, label: str, prompt: str, arguments: Mapping[str, Json]) -> tuple[str, ...]:
    """Build --mode, --scenario, and each flag of arguments, checked against the chosen entry, with --count 1.

    This function checks the prompt, and its refusals name the model; the run call sends the prompt. The person's keys
    keep their order. The key of each flag is its name without the leading dashes, and label names the entry in
    refusals.
    """
    flags = {flag.name.removeprefix(FLAG_PREFIX): flag for flag in mode.flags}
    built = _build_mode_flags(model, mode, label, prompt, flags.get(PROMPT_FLAG))
    for key, value in arguments.items():
        if key in SELECTION_KEYS.values() or key == PROMPT_FLAG:
            continue
        flag = flags.get(key)
        if flag is None:
            message = FLAG_NOT_IN_MODE.format(mode=label, flag=key, flags=', '.join(flags))
            raise DreaminaError(ErrorCode.INVALID_INPUT, message)
        built += [FLAG_PREFIX + key, _validate_value(key, flag, value)]
    if COUNT_FLAG in flags and COUNT_FLAG not in arguments:
        built += [FLAG_PREFIX + COUNT_FLAG, COUNT_VALUE]
    present = {*arguments, PROMPT_FLAG, COUNT_FLAG, *([SELECTION_KEYS['SCENARIO']] if mode.scenario else [])}
    missing = next((name for name, flag in flags.items() if flag.required and name not in present), None)
    if missing is not None:
        raise DreaminaError(ErrorCode.INVALID_INPUT, FLAG_REQUIRED.format(flag=missing, mode=label))
    return tuple(built)


__all__ = ['build_flags', 'choose_prompt', 'parse_arguments', 'validate_argument_names']
