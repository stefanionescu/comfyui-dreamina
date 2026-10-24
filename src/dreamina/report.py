"""Describe one model for Model: Info: its listed modes, the limits model <canonical> adds, and its voices."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

from .cli import parse_reply, send_command
from .models import find_model
from .voices import read_voices
from .contract import validate_cli
from .failures import build_failure
from ..config.media import VOICE_REFERENCE
from ..config.models import KIND_NODES, FLAG_PREFIX
from ..config.messages.run import CLI_FAILED
from ..state.specifications import SpecificationReply

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ..state import Json
    from ..state.models import ModelMode
    from ..state.specifications import MaterialLimits, ModeSpecification


def _format_bound(value: float | None) -> Json:
    """Show a whole-number bound without a decimal point."""
    if value is None:
        return None
    return int(value) if value.is_integer() else value


def _describe_limits(limits: MaterialLimits | None) -> Json:
    """Describe one media type's file limits, in bytes, pixels, and milliseconds; null when Dreamina gives none."""
    if limits is None:
        return None
    return {
        'max_file_bytes': limits.max_file_bytes,
        'min_width_px': limits.min_width_px,
        'max_width_px': limits.max_width_px,
        'min_height_px': limits.min_height_px,
        'max_height_px': limits.max_height_px,
        'min_duration_ms': limits.min_duration_ms,
        'max_duration_ms': limits.max_duration_ms,
    }


def _find_specification(mode: ModelMode, specifications: Sequence[ModeSpecification]) -> ModeSpecification | None:
    """Return the one specification of a listed mode, told apart by mode, scenario, and total material count."""
    references = mode.references
    fitting = [
        specification
        for specification in specifications
        if specification.mode == mode.name
        and specification.scenario == mode.scenario
        and (
            references is None
            or (
                specification.materials is not None
                and specification.materials.total_count.minimum == references.minimum
                and specification.materials.total_count.maximum == references.maximum
            )
        )
    ]
    return fitting[0] if len(fitting) == 1 else None


def _describe_references(mode: ModelMode, specification: ModeSpecification | None) -> Json:
    """Describe what a mode takes; null when the list omits it, so the mode takes no materials."""
    references = mode.references
    if references is None:
        return None
    materials = specification.materials if specification is not None else None
    limits = {material.media_type: material.limits for material in materials.types} if materials is not None else {}
    return {
        'minimum': references.minimum,
        'maximum': references.maximum,
        'types': [
            {
                'media': limit.media_type,
                'minimum': limit.minimum,
                'maximum': limit.maximum,
                'limits': _describe_limits(limits.get(limit.media_type)),
            }
            for limit in references.limits
        ],
        'require_any_of': list(references.required_types),
        'mutually_exclusive': list(references.exclusive_types),
        'max_total_video_ms': materials.max_total_video_ms if materials is not None else None,
        'max_total_audio_ms': materials.max_total_audio_ms if materials is not None else None,
    }


def _describe_mode(mode: ModelMode, specifications: Sequence[ModeSpecification]) -> dict[str, Json]:
    """Describe one listed mode with the limits and membership its specification adds."""
    specification = _find_specification(mode, specifications)
    configs = specification.vip_configs if specification is not None else None
    return {
        'mode': mode.name,
        'scenario': mode.scenario,
        'flags': [
            {
                'flag': flag.name.removeprefix(FLAG_PREFIX),
                'required': flag.required,
                'values': list(flag.values) if flag.values is not None else None,
                'minimum': _format_bound(flag.minimum),
                'maximum': _format_bound(flag.maximum),
                'step': _format_bound(flag.step),
                'min_length': flag.min_length,
                'max_length': flag.max_length,
            }
            for flag in mode.flags
        ],
        'references': _describe_references(mode, specification),
        'max_outputs': specification.max_batch_count if specification is not None else None,
        'membership': {
            'required': mode.vip_required,
            'sizes': list(mode.vip_sizes) if mode.vip_sizes is not None else None,
            'model_level': specification.is_vip if specification is not None else None,
            'by_size': [{'size': item.size, 'required': item.is_vip} for item in configs]
            if configs is not None
            else None,
        },
    }


async def _read_specifications(model: str, kind: str, deadline: float) -> tuple[ModeSpecification, ...]:
    """Read one model's full specification, one entry per mode, with one free call."""
    result = await send_command(('model', model, '--type', kind), max(deadline - time.monotonic(), 1.0))
    if not result.reply.ok:
        raise build_failure(result, CLI_FAILED)
    reply = parse_reply(result.reply.payload, SpecificationReply)
    return tuple(
        match.generation
        for match in reply.matches
        if match.kind == 'generation' and match.generation is not None and match.generation.model == model
    )


async def read_report(name: str, deadline: float) -> dict[str, Json]:
    """Describe a typed model as Model: Info shows it: every key present, null where Dreamina gives no value.

    This function finds the model in the live lists the paid nodes check against; its full specification adds the file
    limits, and a speech model's voices follow. Every read is free.
    """
    await validate_cli()
    model = await find_model(name, None)
    specifications = await _read_specifications(model.name, model.kind, deadline)
    is_speech = any(mode.name == VOICE_REFERENCE['MODE'] for mode in model.modes)
    voices = await read_voices(model.name, deadline) if is_speech else None
    return {
        'model': model.name,
        'aliases': list(model.aliases),
        'kind': model.kind,
        'node': KIND_NODES[model.kind],
        'modes': [_describe_mode(mode, specifications) for mode in model.modes],
        'voices': list(voices) if voices is not None else None,
    }


__all__ = ['read_report']
