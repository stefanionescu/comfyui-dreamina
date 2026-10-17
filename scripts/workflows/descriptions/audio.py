"""The audio workflows: voice a script in a chosen voice, and give a drawn host a voice."""

from __future__ import annotations

import json
from scripts.nodes.host import HostNode
from src.config.namespace import NODE_PREFIX
from scripts.workflows.descriptions.texts import SHARED_TEXTS
from scripts.workflows.descriptions.notes import WORKFLOW_TEXTS
from scripts.workflows.page.graph import Node, Group, Subgraph, Workflow
from scripts.workflows.descriptions.nodes import AUDIO_GENERATE, IMAGE_GENERATE
from scripts.workflows.page.config import STAGE_COLOUR, AUDIO_PREVIEW, IMAGE_PREVIEW

SEED_AUDIO = "seed_audio_v1"
VOICE_ARGUMENTS = json.dumps({"voice-name": "Good Guy"}, indent=2)
CAST_ARGUMENTS = json.dumps({"ratio": "3:4", "resolution": "2K"}, indent=2)
SPEAK_ARGUMENTS = json.dumps({}, indent=2)
SCRIPT_PROMPT = (
    "Welcome back to the show. Today we have three new sneakers, and the first pair is already selling fast."
)
CAST_HOST = (
    "A friendly live-shopping host in his thirties with short curly hair and a denim jacket. Waist up, facing the "
    "camera, in a bright studio, photorealistic."
)
LINE_PROMPT = "Hi everyone, it's so good to see you. I've got something special to show you today."
SCRIPT_TEXTS = WORKFLOW_TEXTS["audio-01-voice-a-script"]
HOST_TEXTS = WORKFLOW_TEXTS["audio-02-give-a-host-a-voice"]

VOICE = Subgraph(
    name=SHARED_TEXTS["voice"],
    nodes=(
        Node("speak", AUDIO_GENERATE, {"arguments": VOICE_ARGUMENTS}, is_paid=True),
        Node("save", HostNode.SAVE_AUDIO, {"filename_prefix": "audio/dreamina/script-voice"}),
    ),
    links=(("speak.audio", "save.audio"),),
    columns=(("speak",), ("save",)),
    inputs=(("script", "speak.prompt"),),
    description=SCRIPT_TEXTS["voice_description"],
    previews=(("save", AUDIO_PREVIEW),),
)

VOICE_SCRIPT = Workflow(
    slug="audio-01-voice-a-script",
    nodes=(
        Node("script", HostNode.TEXT_BLOCK, {"value": SCRIPT_PROMPT}, title=SHARED_TEXTS["script"]),
        Node("info", f"{NODE_PREFIX}ModelInfo", {"model": SEED_AUDIO}),
        Node("row", HostNode.PREVIEW, title=SHARED_TEXTS["info"]),
        Node("voice", VOICE.name),
    ),
    links=(("script.STRING", "voice.script"), ("info.info", "row.source")),
    stacks=(
        (
            Group(SHARED_TEXTS["input"], (("script",),), note=SCRIPT_TEXTS["input"]),
            Group(SHARED_TEXTS["voices"], (("info",), ("row",)), note=SCRIPT_TEXTS["voices"]),
        ),
        (Group(SHARED_TEXTS["voice"], (("voice",),), STAGE_COLOUR, SCRIPT_TEXTS["voice"]),),
    ),
    subgraphs=(VOICE,),
)

CAST = Subgraph(
    name=SHARED_TEXTS["cast"],
    nodes=(
        Node("draw", IMAGE_GENERATE, {"arguments": CAST_ARGUMENTS}, is_paid=True),
        Node("look", HostNode.PREVIEW_IMAGE),
    ),
    links=(("draw.images", "look.images"),),
    columns=(("draw",), ("look",)),
    inputs=(("host", "draw.prompt"),),
    outputs=(("references", "draw.references"),),
    description=HOST_TEXTS["cast_description"],
    previews=(("look", IMAGE_PREVIEW),),
)

SPEAK = Subgraph(
    name=SHARED_TEXTS["speak"],
    nodes=(
        Node("speak", AUDIO_GENERATE, {"arguments": SPEAK_ARGUMENTS}, is_paid=True),
        Node("save", HostNode.SAVE_AUDIO, {"filename_prefix": "audio/dreamina/host-voice"}),
    ),
    links=(("speak.audio", "save.audio"),),
    columns=(("speak",), ("save",)),
    inputs=(("references", "speak.references"), ("line", "speak.prompt")),
    description=HOST_TEXTS["speak_description"],
    previews=(("save", AUDIO_PREVIEW),),
)

HOST_VOICE = Workflow(
    slug="audio-02-give-a-host-a-voice",
    nodes=(
        Node("host", HostNode.TEXT_BLOCK, {"value": CAST_HOST}, title=SHARED_TEXTS["host"]),
        Node("line", HostNode.TEXT_BLOCK, {"value": LINE_PROMPT}, title=SHARED_TEXTS["line"]),
        Node("cast", CAST.name),
        Node("speak", SPEAK.name),
    ),
    links=(("host.STRING", "cast.host"), ("cast.references", "speak.references"), ("line.STRING", "speak.line")),
    stacks=(
        (Group(SHARED_TEXTS["input"], (("host", "line"),), note=HOST_TEXTS["input"]),),
        (Group(SHARED_TEXTS["cast"], (("cast",),), STAGE_COLOUR, HOST_TEXTS["cast"]),),
        (Group(SHARED_TEXTS["speak"], (("speak",),), STAGE_COLOUR, HOST_TEXTS["speak"]),),
    ),
    subgraphs=(CAST, SPEAK),
)

AUDIO_WORKFLOWS = (VOICE_SCRIPT, HOST_VOICE)

__all__ = ["AUDIO_WORKFLOWS", "CAST"]
