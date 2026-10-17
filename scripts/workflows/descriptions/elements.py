"""The Element workflow: keep one host the same across two shots."""

from __future__ import annotations

import json
from scripts.nodes.host import HostNode
from src.config.namespace import NODE_PREFIX
from scripts.workflows.descriptions.audio import CAST
from scripts.workflows.page.config import STAGE_COLOUR
from scripts.workflows.descriptions.texts import SHARED_TEXTS
from scripts.workflows.descriptions.nodes import VIDEO_GENERATE
from scripts.workflows.descriptions.notes import WORKFLOW_TEXTS
from scripts.workflows.page.graph import Node, Group, Subgraph, Workflow

SHOT_ARGUMENTS = json.dumps({"ratio": "9:16", "resolution": "720p", "duration": 4}, indent=2)
KEEP_HOST = (
    "A friendly man in his thirties with short curly hair and a denim jacket. Waist up, facing the camera, plain light "
    "gray background, photorealistic."
)
OPENING_SCENE = (
    "The host from {{reference1}} stands behind a counter of sneakers, waves at the camera, and picks up a white "
    "sneaker. Bright studio, medium shot."
)
CLOSING_SCENE = (
    "The host from {{reference1}} holds the white sneaker next to his face and points at it, smiling. Close-up, warm "
    "light."
)
KEEP_TEXTS = WORKFLOW_TEXTS["video-03-keep-a-host-across-shots"]

SHOT_1 = Subgraph(
    name=SHARED_TEXTS["shot_1"],
    nodes=(
        Node("video", VIDEO_GENERATE, {"arguments": SHOT_ARGUMENTS}, is_paid=True),
        Node("save", HostNode.SAVE_VIDEO, {"filename_prefix": "video/dreamina/host-shot-1"}),
    ),
    links=(("video.video", "save.video"),),
    columns=(("video",), ("save",)),
    inputs=(("element", "video.references"), ("scene", "video.prompt")),
    description=KEEP_TEXTS["shot_1_description"],
)

SHOT_2 = Subgraph(
    name=SHARED_TEXTS["shot_2"],
    nodes=(
        Node("video", VIDEO_GENERATE, {"arguments": SHOT_ARGUMENTS}, is_paid=True),
        Node("save", HostNode.SAVE_VIDEO, {"filename_prefix": "video/dreamina/host-shot-2"}),
    ),
    links=(("video.video", "save.video"),),
    columns=(("video",), ("save",)),
    inputs=(("element", "video.references"), ("scene", "video.prompt")),
    description=KEEP_TEXTS["shot_2_description"],
)

KEEP_HOST_ACROSS_SHOTS = Workflow(
    slug="video-03-keep-a-host-across-shots",
    nodes=(
        Node("host", HostNode.TEXT_BLOCK, {"value": KEEP_HOST}, title=SHARED_TEXTS["host"]),
        Node("opening", HostNode.TEXT_BLOCK, {"value": OPENING_SCENE}, title=SHARED_TEXTS["opening"]),
        Node("closing", HostNode.TEXT_BLOCK, {"value": CLOSING_SCENE}, title=SHARED_TEXTS["closing"]),
        Node("cast", CAST.name),
        Node("keep", f"{NODE_PREFIX}ElementAdd", {"title": "Host"}),
        Node("shot_1", SHOT_1.name),
        Node("shot_2", SHOT_2.name),
    ),
    links=(
        ("host.STRING", "cast.host"),
        ("cast.references", "keep.main"),
        ("keep.references", "shot_1.element"),
        ("keep.references", "shot_2.element"),
        ("opening.STRING", "shot_1.scene"),
        ("closing.STRING", "shot_2.scene"),
    ),
    stacks=(
        (Group(SHARED_TEXTS["input"], (("host", "opening", "closing"),), note=KEEP_TEXTS["input"]),),
        (Group(SHARED_TEXTS["cast"], (("cast",),), STAGE_COLOUR, KEEP_TEXTS["cast"]),),
        (Group(SHARED_TEXTS["keep"], (("keep",),), STAGE_COLOUR, KEEP_TEXTS["keep"]),),
        (Group(SHARED_TEXTS["shot_1"], (("shot_1",),), STAGE_COLOUR, KEEP_TEXTS["shot_1"]),),
        (Group(SHARED_TEXTS["shot_2"], (("shot_2",),), STAGE_COLOUR, KEEP_TEXTS["shot_2"]),),
    ),
    subgraphs=(CAST, SHOT_1, SHOT_2),
)

ELEMENT_WORKFLOWS = (KEEP_HOST_ACROSS_SHOTS,)

__all__ = ["ELEMENT_WORKFLOWS"]
