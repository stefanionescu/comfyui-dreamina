"""Read every voice a speech model's voice list holds, page by page."""

from __future__ import annotations

import time

from .cli import parse_reply, send_command
from .failures import build_failure
from ..config.models import VOICE_PAGE_COUNT
from ..state.replies import VoicePage
from ..config.dreamina import EXIT_CODES
from ..config.messages.run import CLI_FAILED


async def read_voices(model: str, deadline: float) -> tuple[str, ...]:
    """Return a speech model's voice names in Dreamina's order; empty when the model has no voices.

    The CLI refuses an unsupported route as an invalid input, which means no voices.
    """
    names: list[str] = []
    offset = 0
    while True:
        arguments = ('voice', 'list', '--model', model, '--offset', str(offset), '--count', str(VOICE_PAGE_COUNT))
        result = await send_command(arguments, max(deadline - time.monotonic(), 1.0))
        failure = result.reply.error
        if result.exit_code == EXIT_CODES['INVALID'] or (
            failure is not None and failure.failure_class == 'invalid_input'
        ):
            return ()
        if not result.reply.ok:
            raise build_failure(result, CLI_FAILED)
        voice_page = parse_reply(result.reply.payload, VoicePage).models.get(model)
        if voice_page is None:
            return tuple(names)
        names.extend(voice.voice_name for voice in voice_page.items)
        if not voice_page.has_more:
            return tuple(names)
        offset = voice_page.next_offset


__all__ = ['read_voices']
