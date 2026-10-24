"""Create a Dreamina Element from sources already on the canvas; it generates nothing and bills nothing."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

from .cli import parse_reply, send_command
from .failures import build_failure
from ..state.runs import ElementReply
from ..state.references import Reference
from ..config.messages.run import ELEMENT_REFUSED

if TYPE_CHECKING:
    from ..state.references import ElementRequest


async def create_element(project_id: str, request: ElementRequest, deadline: float) -> Reference:
    """Make the Element with one free call, each source by its bare ID, and return it as a canvas node reference.

    The node never sends the call again: a second run makes a second Element, at no cost.
    """
    arguments = (
        "node", "create", "element", "--project-id", project_id, "--main", request.main.value,
        *(("--voice", request.voice.value) if request.voice is not None else ()),
        *(item for reference in request.auxiliary for item in ("--auxiliary", reference.value)),
        "--title", request.title, *(("--description", request.description) if request.description else ()),
    )  # fmt: skip
    result = await send_command(arguments, max(deadline - time.monotonic(), 1.0))
    if not result.reply.ok:
        raise build_failure(result, ELEMENT_REFUSED)
    node = parse_reply(result.reply.payload, ElementReply).node
    return Reference(origin='node', value=node.node_id, media='element', title=request.title)


__all__ = ['create_element']
