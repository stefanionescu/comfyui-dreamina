"""The image workflows: design a host, edit a product photo, and upscale a poster."""

from __future__ import annotations

import json
from scripts.nodes.host import HostNode
from scripts.workflows.descriptions.texts import SHARED_TEXTS
from scripts.workflows.descriptions.notes import WORKFLOW_TEXTS
from scripts.workflows.page.config import STAGE_COLOUR, IMAGE_PREVIEW
from scripts.workflows.page.graph import Node, Group, Subgraph, Workflow
from scripts.workflows.descriptions.nodes import IMAGE_UPSCALE, IMAGE_GENERATE

SUNBURST = "dreamina_gpt_image_2_5_sunburst"
DESIGN_ARGUMENTS = json.dumps({"ratio": "3:4", "resolution": "2K"}, indent=2)
EDIT_ARGUMENTS = json.dumps({"ratio": "1:1", "resolution": "1K"}, indent=2)
HOST_PROMPT = (
    "Studio portrait of a live-shopping host: a cheerful woman in her late twenties with shoulder-length auburn hair, "
    "a mustard knit sweater, and small gold hoop earrings. Waist up, facing the camera, plain light gray background, "
    "soft light."
)
CHANGE_PROMPT = (
    "Place the product from {{image1}} on a light oak table beside a sunny window, with a soft shadow under it. Keep "
    "its shape, colors, and label exactly as they are."
)
POSTER_ARGUMENTS = json.dumps({"ratio": "3:4", "resolution": "2K"}, indent=2)
POSTER_PROMPT = (
    'A poster for a summer night market: the title "Night Market" in bold hand-lettered type at the top, paper '
    'lanterns and food stalls in silhouette, and the date "August 14" at the bottom. Flat illustration in deep blue '
    "and orange."
)
HOST_TEXTS = WORKFLOW_TEXTS["image-01-design-a-host"]
EDIT_TEXTS = WORKFLOW_TEXTS["image-02-edit-a-product-photo"]
POSTER_TEXTS = WORKFLOW_TEXTS["image-03-upscale-a-poster"]

DESIGN = Subgraph(
    name=SHARED_TEXTS["design"],
    nodes=(
        Node("draw", IMAGE_GENERATE, {"arguments": DESIGN_ARGUMENTS}, is_paid=True),
        Node("save", HostNode.SAVE_IMAGE, {"filename_prefix": "image/dreamina/host"}),
    ),
    links=(("draw.images", "save.images"),),
    columns=(("draw",), ("save",)),
    inputs=(("host", "draw.prompt"),),
    description=HOST_TEXTS["design_description"],
    previews=(("save", IMAGE_PREVIEW),),
)

DESIGN_HOST = Workflow(
    slug="image-01-design-a-host",
    nodes=(
        Node("host", HostNode.TEXT_BLOCK, {"value": HOST_PROMPT}, title=SHARED_TEXTS["host"]),
        Node("design", DESIGN.name),
    ),
    links=(("host.STRING", "design.host"),),
    stacks=(
        (Group(SHARED_TEXTS["input"], (("host",),), note=HOST_TEXTS["input"]),),
        (Group(SHARED_TEXTS["design"], (("design",),), STAGE_COLOUR, HOST_TEXTS["design"]),),
    ),
    subgraphs=(DESIGN,),
)

EDIT = Subgraph(
    name=SHARED_TEXTS["edit"],
    nodes=(
        Node("draw", IMAGE_GENERATE, {"model": SUNBURST, "arguments": EDIT_ARGUMENTS}, is_paid=True),
        Node("save", HostNode.SAVE_IMAGE, {"filename_prefix": "image/dreamina/product-edit"}),
    ),
    links=(("draw.images", "save.images"),),
    columns=(("draw",), ("save",)),
    inputs=(("photo", "draw.images"), ("change", "draw.prompt")),
    description=EDIT_TEXTS["edit_description"],
    previews=(("save", IMAGE_PREVIEW),),
)

EDIT_PHOTO = Workflow(
    slug="image-02-edit-a-product-photo",
    nodes=(
        Node("photo", HostNode.IMAGE, {"image": ""}, title=SHARED_TEXTS["photo"]),
        Node("change", HostNode.TEXT_BLOCK, {"value": CHANGE_PROMPT}, title=SHARED_TEXTS["change"]),
        Node("edit", EDIT.name),
    ),
    links=(("photo.IMAGE", "edit.photo"), ("change.STRING", "edit.change")),
    stacks=(
        (Group(SHARED_TEXTS["input"], (("photo", "change"),), note=EDIT_TEXTS["input"]),),
        (Group(SHARED_TEXTS["edit"], (("edit",),), STAGE_COLOUR, EDIT_TEXTS["edit"]),),
    ),
    subgraphs=(EDIT,),
)

POSTER = Subgraph(
    name=SHARED_TEXTS["poster"],
    nodes=(
        Node("draw", IMAGE_GENERATE, {"arguments": POSTER_ARGUMENTS}, is_paid=True),
        Node("save", HostNode.SAVE_IMAGE, {"filename_prefix": "image/dreamina/poster"}),
    ),
    links=(("draw.images", "save.images"),),
    columns=(("draw",), ("save",)),
    inputs=(("brief", "draw.prompt"),),
    outputs=(("references", "draw.references"),),
    description=POSTER_TEXTS["poster_description"],
    previews=(("save", IMAGE_PREVIEW),),
)

ENLARGE = Subgraph(
    name=SHARED_TEXTS["enlarge"],
    nodes=(
        Node("up", IMAGE_UPSCALE, is_paid=True),
        Node("save", HostNode.SAVE_IMAGE, {"filename_prefix": "image/dreamina/poster-upscaled"}),
    ),
    links=(("up.images", "save.images"),),
    columns=(("up",), ("save",)),
    inputs=(("references", "up.references"),),
    description=POSTER_TEXTS["enlarge_description"],
    previews=(("save", IMAGE_PREVIEW),),
)

UPSCALE_POSTER = Workflow(
    slug="image-03-upscale-a-poster",
    nodes=(
        Node("brief", HostNode.TEXT_BLOCK, {"value": POSTER_PROMPT}, title=SHARED_TEXTS["brief"]),
        Node("poster", POSTER.name),
        Node("enlarge", ENLARGE.name),
    ),
    links=(("brief.STRING", "poster.brief"), ("poster.references", "enlarge.references")),
    stacks=(
        (Group(SHARED_TEXTS["input"], (("brief",),), note=POSTER_TEXTS["input"]),),
        (Group(SHARED_TEXTS["poster"], (("poster",),), STAGE_COLOUR, POSTER_TEXTS["poster"]),),
        (Group(SHARED_TEXTS["enlarge"], (("enlarge",),), STAGE_COLOUR, POSTER_TEXTS["enlarge"]),),
    ),
    subgraphs=(POSTER, ENLARGE),
)

IMAGE_WORKFLOWS = (DESIGN_HOST, EDIT_PHOTO, UPSCALE_POSTER)

__all__ = ["IMAGE_WORKFLOWS"]
