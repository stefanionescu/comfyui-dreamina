"""The Element workflows: keep one host the same across two shots, and cast a saved host from files."""

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
TAKE_SCENE = (
    "The host from {{reference1}} walks into the kitchen from {{image1}}, stops behind the counter, smiles, and waves "
    "at the camera. Medium shot, soft daylight."
)
KEEP_TEXTS = WORKFLOW_TEXTS["video-03-keep-a-host-across-shots"]
TAKE_TEXTS = WORKFLOW_TEXTS["video-06-cast-a-saved-host"]

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

TAKE = Subgraph(
    name=SHARED_TEXTS["take"],
    nodes=(
        Node("video", VIDEO_GENERATE, {"arguments": SHOT_ARGUMENTS}, is_paid=True),
        Node("save", HostNode.SAVE_VIDEO, {"filename_prefix": "video/dreamina/host-walks-in"}),
    ),
    links=(("video.video", "save.video"),),
    columns=(("video",), ("save",)),
    inputs=(("element", "video.references"), ("place", "video.images"), ("scene", "video.prompt")),
    description=TAKE_TEXTS["take_description"],
)

CAST_SAVED_HOST = Workflow(
    slug="video-06-cast-a-saved-host",
    nodes=(
        Node("host", HostNode.IMAGE, {"image": ""}, title=SHARED_TEXTS["host"]),
        Node("full_body", HostNode.IMAGE, {"image": ""}, title=SHARED_TEXTS["full_body"]),
        Node("place", HostNode.IMAGE, {"image": ""}, title=SHARED_TEXTS["place"]),
        Node("scene", HostNode.TEXT_BLOCK, {"value": TAKE_SCENE}, title=SHARED_TEXTS["scene"]),
        Node("keep", f"{NODE_PREFIX}ElementAdd", {"title": "Host"}),
        Node("take", TAKE.name),
    ),
    links=(
        ("host.IMAGE", "keep.main"),
        ("full_body.IMAGE", "keep.auxiliary"),
        ("keep.references", "take.element"),
        ("place.IMAGE", "take.place"),
        ("scene.STRING", "take.scene"),
    ),
    stacks=(
        (Group(SHARED_TEXTS["input"], (("host", "full_body"), ("place", "scene")), note=TAKE_TEXTS["input"]),),
        (Group(SHARED_TEXTS["keep"], (("keep",),), STAGE_COLOUR, TAKE_TEXTS["keep"]),),
        (Group(SHARED_TEXTS["take"], (("take",),), STAGE_COLOUR, TAKE_TEXTS["take"]),),
    ),
    subgraphs=(TAKE,),
)

ELEMENT_WORKFLOWS = (KEEP_HOST_ACROSS_SHOTS, CAST_SAVED_HOST)

__all__ = ["ELEMENT_WORKFLOWS"]
