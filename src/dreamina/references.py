"""Check a run's references against its mode, order them for --ref, and write its placeholders in the CLI's form."""

from __future__ import annotations

import re
import string
from collections import Counter
from typing import TYPE_CHECKING
from ..config.patterns import PLACEHOLDER_PATTERN
from ..types.errors import ErrorCode, DreaminaError
from ..config.messages.inputs import PLACEHOLDER_UNCONNECTED
from ..config.media import FRAME_MODES, MEDIA_TYPES, PLACEHOLDERS, VOICE_REFERENCE
from ..config.messages.models import (
    VOICE_COUNTED,
    REFERENCES_NONE,
    REFERENCES_TOTAL,
    REFERENCES_ANY_OF,
    REFERENCE_KIND_COUNT,
    REFERENCES_EXCLUSIVE,
    REFERENCE_KIND_REFUSED,
    REFERENCES_ELEMENT_FRAME,
)

if TYPE_CHECKING:
    from ..types import Json
    from ..types.models import ModelMode
    from collections.abc import Mapping, Sequence
    from ..types.references import Reference, LocalMedia

_PLACEHOLDER = re.compile(PLACEHOLDER_PATTERN)


def _find_presence_refusal(mode: ModelMode, items: Sequence[Reference | LocalMedia], total: int) -> str | None:
    """Refuse an Element in a frame, and anything at all for an entry that takes no references."""
    if mode.name in FRAME_MODES and any(item.media == "element" for item in items):
        return REFERENCES_ELEMENT_FRAME.format(mode=mode.label)
    if (mode.references is None or mode.references.maximum == 0) and total:
        return REFERENCES_NONE.format(mode=mode.label, count=total)
    return None


def _find_count_refusal(mode: ModelMode, counts: Counter[str]) -> str | None:
    """Refuse a total, a media type, or a type's count the entry's limits do not allow."""
    references = mode.references
    if references is None:
        return None
    total = counts.total()
    if not references.minimum <= total <= references.maximum:
        return REFERENCES_TOTAL.format(
            mode=mode.label, minimum=references.minimum, maximum=references.maximum, count=total
        )
    limits = {limit.media_type for limit in references.limits}
    refused = next((media for media, count in counts.items() if count and media not in limits), None)
    if refused is not None:
        return REFERENCE_KIND_REFUSED.format(mode=mode.label, media=refused, count=counts[refused])
    wrong = next(
        (limit for limit in references.limits if not limit.minimum <= counts[limit.media_type] <= limit.maximum), None
    )
    return (
        None
        if wrong is None
        else REFERENCE_KIND_COUNT.format(
            mode=mode.label,
            minimum=wrong.minimum,
            maximum=wrong.maximum,
            media=wrong.media_type,
            count=counts[wrong.media_type],
        )
    )


def _find_rule_refusal(mode: ModelMode, counts: Counter[str]) -> str | None:
    """Refuse a run that misses every required type, or holds media types the entry keeps apart."""
    references = mode.references
    if references is None:
        return None
    if references.required_types and not any(counts[media] for media in references.required_types):
        return REFERENCES_ANY_OF.format(mode=mode.label, media=", ".join(references.required_types))
    present = [media for media in references.exclusive_types if counts[media]]
    return REFERENCES_EXCLUSIVE.format(mode=mode.label, media=" and ".join(present)) if len(present) > 1 else None


def validate_references(
    mode: ModelMode, items: Sequence[Reference | LocalMedia], arguments: Mapping[str, Json]
) -> None:
    """Refuse references the chosen mode entry would refuse, before anything is uploaded.

    Each item counts under its media type, an Element as an image. In speech, a voice set in arguments fills one audio
    slot, as the CLI counts it.
    """
    counts = Counter(MEDIA_TYPES[item.media] for item in items)
    is_voiced = mode.name == VOICE_REFERENCE["MODE"] and VOICE_REFERENCE["FLAG"] in arguments
    if is_voiced:
        counts["audio"] += 1
    message = (
        _find_presence_refusal(mode, items, counts.total())
        or _find_count_refusal(mode, counts)
        or _find_rule_refusal(mode, counts)
    )
    if message is not None:
        raise DreaminaError(ErrorCode.INVALID_INPUT, f"{message} {VOICE_COUNTED}" if is_voiced else message)


def plan_references(
    references: Sequence[Reference], local: Sequence[LocalMedia], uploaded: Sequence[Reference]
) -> tuple[tuple[Reference, ...], dict[str, Reference]]:
    """Put every reference in --ref order, and name each one for its placeholder.

    References come first, in socket order, then the uploads by kind and position, whatever order they were listed
    in. Two items with the same bytes share one resource and keep their own places.
    """
    order = {word: index for index, word in enumerate(PLACEHOLDERS)}
    pairs = sorted(zip(local, uploaded, strict=True), key=lambda pair: (order[pair[0].media], pair[0].position))
    # The first placeholder word names the references input.
    word = next(iter(PLACEHOLDERS))
    placed = {f"{word}{index}": reference for index, reference in enumerate(references, 1)}
    placed.update({f"{item.media}{item.position}": reference for item, reference in pairs})
    return (*references, *(reference for _, reference in pairs)), placed


def format_prompt(prompt: str, placed: Mapping[str, Reference]) -> str:
    """Write each placeholder of this pack in the CLI's form, and leave every other part of the prompt as typed."""
    counts = Counter(name.rstrip(string.digits) for name in placed)

    def format_placeholder(match: re.Match[str]) -> str:
        """Write one placeholder as {{node:...}} or {{res:...}}, refusing one whose item is not connected."""
        word = match.group(1)
        reference = placed.get(word + match.group(2))
        if reference is None:
            message = PLACEHOLDER_UNCONNECTED.format(
                placeholder=match.group(0), input=PLACEHOLDERS[word], count=counts[word]
            )
            raise DreaminaError(ErrorCode.INVALID_INPUT, message)
        return "{{" + reference.typed_value + "}}"

    return _PLACEHOLDER.sub(format_placeholder, prompt)


__all__ = ["format_prompt", "plan_references", "validate_references"]
