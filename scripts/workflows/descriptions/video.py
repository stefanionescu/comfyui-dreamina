"""The video workflows: animate a host, film a product ad, and recover a video left running."""

from __future__ import annotations

import json
from scripts.nodes.host import HostNode
from src.config.namespace import NODE_PREFIX
from scripts.workflows.descriptions.audio import CAST
from scripts.workflows.descriptions.texts import SHARED_TEXTS
from scripts.workflows.descriptions.notes import WORKFLOW_TEXTS
from scripts.workflows.page.graph import Node, Group, Subgraph, Workflow
from scripts.workflows.descriptions.nodes import IMAGE_GENERATE, VIDEO_GENERATE
from scripts.workflows.page.config import STAGE_COLOUR, IMAGE_PREVIEW, VIDEO_PREVIEW

SEEDANCE_2_5 = "seedance_2.5"
PORTRAIT_ARGUMENTS = json.dumps({"ratio": "9:16", "resolution": "2K"}, indent=2)
ANIMATE_ARGUMENTS = json.dumps({"ratio": "9:16", "resolution": "720p", "duration": 4}, indent=2)
FILM_ARGUMENTS = json.dumps({"mode": "m2v", "ratio": "9:16", "resolution": "480p", "duration": 4}, indent=2)
# Part 0's quote of Film's settings, 48 credits, rounded up to the next 10.
FILM_CEILING = 50
PORTRAIT_HOST = (
    "A friendly man in his thirties with short curly hair and a denim jacket, standing in a bright studio with shelves "
    "of sneakers behind him. Waist up, looking at the camera, photorealistic."
)
ANIMATE_SCENE = (
    "He smiles, picks up a sneaker from the shelf, and turns it toward the camera. Slow push-in, warm light."
)
FILM_HOST = (
    "A cheerful woman in her late twenties with shoulder-length auburn hair and a mustard knit sweater. Waist up, "
    "facing the camera, in a bright studio, photorealistic."
)
FILM_PRODUCT = (
    "A pair of white canvas sneakers with red laces, side view, on a plain white background, soft studio light."
)
FILM_SCENE = (
    "The host in {{reference1}} holds up the sneakers from {{image1}}, smiles, and turns them toward the camera to "
    "show the red laces. Bright studio, slow push-in."
)
SHOT_PROMPT = (
    "A white canvas sneaker with red laces turns slowly on a plain white turntable. Soft studio light, slow push-in."
)
ANIMATE_TEXTS = WORKFLOW_TEXTS["video-01-animate-a-host"]
FILM_TEXTS = WORKFLOW_TEXTS["video-02-film-a-product-ad"]
RECOVER_TEXTS = WORKFLOW_TEXTS["video-04-recover-a-video"]

PORTRAIT = Subgraph(
    name=SHARED_TEXTS["portrait"],
    nodes=(
        Node("draw", IMAGE_GENERATE, {"arguments": PORTRAIT_ARGUMENTS}, is_paid=True),
        Node("look", HostNode.PREVIEW_IMAGE),
    ),
    links=(("draw.images", "look.images"),),
    columns=(("draw",), ("look",)),
    inputs=(("host", "draw.prompt"),),
    outputs=(("references", "draw.references"),),
    description=ANIMATE_TEXTS["portrait_description"],
    previews=(("look", IMAGE_PREVIEW),),
)

ANIMATE = Subgraph(
    name=SHARED_TEXTS["animate"],
    nodes=(
        Node("video", VIDEO_GENERATE, {"arguments": ANIMATE_ARGUMENTS}, is_paid=True),
        Node("save", HostNode.SAVE_VIDEO, {"filename_prefix": "video/dreamina/host"}),
    ),
    links=(("video.video", "save.video"),),
    columns=(("video",), ("save",)),
    inputs=(("references", "video.references"), ("scene", "video.prompt")),
    description=ANIMATE_TEXTS["animate_description"],
    previews=(("save", VIDEO_PREVIEW),),
)

ANIMATE_HOST = Workflow(
    slug="video-01-animate-a-host",
    nodes=(
        Node("host", HostNode.TEXT_BLOCK, {"value": PORTRAIT_HOST}, title=SHARED_TEXTS["host"]),
        Node("scene", HostNode.TEXT_BLOCK, {"value": ANIMATE_SCENE}, title=SHARED_TEXTS["scene"]),
        Node("portrait", PORTRAIT.name),
        Node("animate", ANIMATE.name),
    ),
    links=(
        ("host.STRING", "portrait.host"),
        ("portrait.references", "animate.references"),
        ("scene.STRING", "animate.scene"),
    ),
    stacks=(
        (Group(SHARED_TEXTS["input"], (("host", "scene"),), note=ANIMATE_TEXTS["input"]),),
        (Group(SHARED_TEXTS["portrait"], (("portrait",),), STAGE_COLOUR, ANIMATE_TEXTS["portrait"]),),
        (Group(SHARED_TEXTS["animate"], (("animate",),), STAGE_COLOUR, ANIMATE_TEXTS["animate"]),),
    ),
    subgraphs=(PORTRAIT, ANIMATE),
)

PACKSHOT = Subgraph(
    name=SHARED_TEXTS["packshot"],
    nodes=(
        Node("draw", IMAGE_GENERATE, is_paid=True),
        Node("look", HostNode.PREVIEW_IMAGE),
    ),
    links=(("draw.images", "look.images"),),
    columns=(("draw",), ("look",)),
    inputs=(("product", "draw.prompt"),),
    outputs=(("images", "draw.images"),),
    description=FILM_TEXTS["packshot_description"],
    previews=(("look", IMAGE_PREVIEW),),
)

FILM = Subgraph(
    name=SHARED_TEXTS["film"],
    nodes=(
        Node(
            "video",
            VIDEO_GENERATE,
            {"model": SEEDANCE_2_5, "arguments": FILM_ARGUMENTS, "credit_ceiling": FILM_CEILING},
            is_paid=True,
        ),
        Node("save", HostNode.SAVE_VIDEO, {"filename_prefix": "video/dreamina/product-ad"}),
    ),
    links=(("video.video", "save.video"),),
    columns=(("video",), ("save",)),
    inputs=(("host", "video.references"), ("product", "video.images"), ("scene", "video.prompt")),
    description=FILM_TEXTS["film_description"],
    previews=(("save", VIDEO_PREVIEW),),
)

FILM_AD = Workflow(
    slug="video-02-film-a-product-ad",
    nodes=(
        Node("host", HostNode.TEXT_BLOCK, {"value": FILM_HOST}, title=SHARED_TEXTS["host"]),
        Node("product", HostNode.TEXT_BLOCK, {"value": FILM_PRODUCT}, title=SHARED_TEXTS["product"]),
        Node("scene", HostNode.TEXT_BLOCK, {"value": FILM_SCENE}, title=SHARED_TEXTS["scene"]),
        Node("cast", CAST.name),
        Node("packshot", PACKSHOT.name),
        Node("film", FILM.name),
    ),
    links=(
        ("host.STRING", "cast.host"),
        ("product.STRING", "packshot.product"),
        ("cast.references", "film.host"),
        ("packshot.images", "film.product"),
        ("scene.STRING", "film.scene"),
    ),
    stacks=(
        (Group(SHARED_TEXTS["input"], (("host", "product", "scene"),), note=FILM_TEXTS["input"]),),
        (Group(SHARED_TEXTS["cast"], (("cast",),), STAGE_COLOUR, FILM_TEXTS["cast"]),),
        (Group(SHARED_TEXTS["packshot"], (("packshot",),), STAGE_COLOUR, FILM_TEXTS["packshot"]),),
        (Group(SHARED_TEXTS["film"], (("film",),), STAGE_COLOUR, FILM_TEXTS["film"]),),
    ),
    subgraphs=(CAST, PACKSHOT, FILM),
)

SHOT = Subgraph(
    name=SHARED_TEXTS["shot"],
    nodes=(
        Node("video", VIDEO_GENERATE, {"prompt": SHOT_PROMPT}, is_paid=True),
        Node("save", HostNode.SAVE_VIDEO, {"filename_prefix": "video/dreamina/shot"}),
    ),
    links=(("video.video", "save.video"),),
    columns=(("video",), ("save",)),
    description=RECOVER_TEXTS["shot_description"],
    previews=(("save", VIDEO_PREVIEW),),
)

RECOVER_VIDEO = Workflow(
    slug="video-04-recover-a-video",
    nodes=(
        Node("download", f"{NODE_PREFIX}GenerationDownload", {"generation": ""}),
        Node("save", HostNode.SAVE_VIDEO, {"filename_prefix": "video/dreamina/recovered"}),
        Node("shot", SHOT.name, is_bypassed=True),
    ),
    links=(("download.video", "save.video"),),
    stacks=(
        (Group(SHARED_TEXTS["collect"], (("download",), ("save",)), STAGE_COLOUR, RECOVER_TEXTS["collect"]),),
        (Group(SHARED_TEXTS["shot"], (("shot",),), STAGE_COLOUR, RECOVER_TEXTS["shot"]),),
    ),
    subgraphs=(SHOT,),
)

VIDEO_WORKFLOWS = (ANIMATE_HOST, FILM_AD, RECOVER_VIDEO)

__all__ = ["VIDEO_WORKFLOWS"]
