"""The image workflows: design a host, edit a product photo, upscale a poster, and reuse a saved host."""

from scripts.nodes.host import HostNode
from scripts.workflows.page.graph import Node, Group, Subgraph, Workflow
from scripts.workflows.page.config import STAGE_COLOUR, IMAGE_PREVIEW
from scripts.workflows.descriptions.nodes import IMAGE_UPSCALE, IMAGE_GENERATE
from scripts.workflows.descriptions.notes import WORKFLOW_TEXTS
from scripts.workflows.descriptions.texts import SHARED_TEXTS

DESIGN_FLAGS = {'ratio': '3:4'}
HOST_PROMPT = (
    'Studio portrait of a live-shopping host: a cheerful woman in her late twenties with shoulder-length auburn hair, '
    'a mustard knit sweater, and small gold hoop earrings. Waist up, facing the camera, plain light gray background, '
    'soft light.'
)
CHANGE_PROMPT = (
    'Place the product from {{image1}} on a light oak table beside a sunny window, with a soft shadow under it. Keep '
    'its shape, colors, and label exactly as they are.'
)
SAVED_FLAGS = {'ratio': '9:16'}
POSE_PROMPT = (
    'The woman from {{image1}}, full body, standing and facing the camera on a plain light gray background. Keep her '
    'face, auburn hair, mustard knit sweater, and gold hoop earrings exactly as they are, with dark jeans and white '
    'sneakers.'
)
PLACE_PROMPT = (
    'The woman from {{image1}} stands behind the counter of the kitchen from {{image2}} and holds the burger from '
    '{{image3}} on its plate in both hands, at its real size, smiling at the camera. Keep her face, hair, and clothes, '
    'the kitchen, and the burger as they are. Photorealistic, soft daylight.'
)
POSTER_FLAGS = {'ratio': '3:4'}
POSTER_PROMPT = (
    'A poster for a summer night market: the title "Night Market" in bold hand-lettered type at the top, paper '
    'lanterns and food stalls in silhouette, and the date "August 14" at the bottom. Flat illustration in deep blue '
    'and orange.'
)
HOST_TEXTS = WORKFLOW_TEXTS['image-01-design-a-host']
EDIT_TEXTS = WORKFLOW_TEXTS['image-02-edit-a-product-photo']
POSTER_TEXTS = WORKFLOW_TEXTS['image-03-upscale-a-poster']
REDRAW_TEXTS = WORKFLOW_TEXTS['image-04-redraw-a-saved-host']
COMBINE_TEXTS = WORKFLOW_TEXTS['image-05-place-a-host-in-a-scene']

DESIGN = Subgraph(
    name=SHARED_TEXTS['design'],
    nodes=(
        Node('draw', IMAGE_GENERATE, DESIGN_FLAGS, is_paid=True),
        Node('save', HostNode.SAVE_IMAGE, {'filename_prefix': 'image/dreamina/host'}),
    ),
    links=(('draw.images', 'save.images'),),
    columns=(('draw',), ('save',)),
    inputs=(('host', 'draw.prompt'),),
    description=HOST_TEXTS['design_description'],
    previews=(('save', IMAGE_PREVIEW),),
)

DESIGN_HOST = Workflow(
    slug='image-01-design-a-host',
    nodes=(
        Node('host', HostNode.TEXT_BLOCK, {'value': HOST_PROMPT}, title=SHARED_TEXTS['host']),
        Node('design', DESIGN.name),
    ),
    links=(('host.STRING', 'design.host'),),
    stacks=(
        (Group(SHARED_TEXTS['input'], (('host',),), note=HOST_TEXTS['input']),),
        (Group(SHARED_TEXTS['design'], (('design',),), STAGE_COLOUR, HOST_TEXTS['design']),),
    ),
    subgraphs=(DESIGN,),
)

EDIT = Subgraph(
    name=SHARED_TEXTS['edit'],
    nodes=(
        Node('draw', IMAGE_GENERATE, is_paid=True),
        Node('save', HostNode.SAVE_IMAGE, {'filename_prefix': 'image/dreamina/product-edit'}),
    ),
    links=(('draw.images', 'save.images'),),
    columns=(('draw',), ('save',)),
    inputs=(('photo', 'draw.images'), ('change', 'draw.prompt')),
    description=EDIT_TEXTS['edit_description'],
    previews=(('save', IMAGE_PREVIEW),),
)

EDIT_PHOTO = Workflow(
    slug='image-02-edit-a-product-photo',
    nodes=(
        Node('photo', HostNode.IMAGE, {'image': ''}, title=SHARED_TEXTS['photo']),
        Node('change', HostNode.TEXT_BLOCK, {'value': CHANGE_PROMPT}, title=SHARED_TEXTS['change']),
        Node('edit', EDIT.name),
    ),
    links=(('photo.IMAGE', 'edit.photo'), ('change.STRING', 'edit.change')),
    stacks=(
        (Group(SHARED_TEXTS['input'], (('photo', 'change'),), note=EDIT_TEXTS['input']),),
        (Group(SHARED_TEXTS['edit'], (('edit',),), STAGE_COLOUR, EDIT_TEXTS['edit']),),
    ),
    subgraphs=(EDIT,),
)

POSTER = Subgraph(
    name=SHARED_TEXTS['poster'],
    nodes=(
        Node('draw', IMAGE_GENERATE, POSTER_FLAGS, is_paid=True),
        Node('save', HostNode.SAVE_IMAGE, {'filename_prefix': 'image/dreamina/poster'}),
    ),
    links=(('draw.images', 'save.images'),),
    columns=(('draw',), ('save',)),
    inputs=(('brief', 'draw.prompt'),),
    outputs=(('references', 'draw.references'),),
    description=POSTER_TEXTS['poster_description'],
    previews=(('save', IMAGE_PREVIEW),),
)

ENLARGE = Subgraph(
    name=SHARED_TEXTS['enlarge'],
    nodes=(
        Node('up', IMAGE_UPSCALE, is_paid=True),
        Node('save', HostNode.SAVE_IMAGE, {'filename_prefix': 'image/dreamina/poster-upscaled'}),
    ),
    links=(('up.images', 'save.images'),),
    columns=(('up',), ('save',)),
    inputs=(('references', 'up.references'),),
    description=POSTER_TEXTS['enlarge_description'],
    previews=(('save', IMAGE_PREVIEW),),
)

UPSCALE_POSTER = Workflow(
    slug='image-03-upscale-a-poster',
    nodes=(
        Node('brief', HostNode.TEXT_BLOCK, {'value': POSTER_PROMPT}, title=SHARED_TEXTS['brief']),
        Node('poster', POSTER.name),
        Node('enlarge', ENLARGE.name),
    ),
    links=(('brief.STRING', 'poster.brief'), ('poster.references', 'enlarge.references')),
    stacks=(
        (Group(SHARED_TEXTS['input'], (('brief',),), note=POSTER_TEXTS['input']),),
        (Group(SHARED_TEXTS['poster'], (('poster',),), STAGE_COLOUR, POSTER_TEXTS['poster']),),
        (Group(SHARED_TEXTS['enlarge'], (('enlarge',),), STAGE_COLOUR, POSTER_TEXTS['enlarge']),),
    ),
    subgraphs=(POSTER, ENLARGE),
)

REDRAW = Subgraph(
    name=SHARED_TEXTS['redraw'],
    nodes=(
        Node('draw', IMAGE_GENERATE, SAVED_FLAGS, is_paid=True),
        Node('save', HostNode.SAVE_IMAGE, {'filename_prefix': 'image/dreamina/host-full-body'}),
    ),
    links=(('draw.images', 'save.images'),),
    columns=(('draw',), ('save',)),
    inputs=(('host', 'draw.images'), ('pose', 'draw.prompt')),
    description=REDRAW_TEXTS['redraw_description'],
    previews=(('save', IMAGE_PREVIEW),),
)

REDRAW_HOST = Workflow(
    slug='image-04-redraw-a-saved-host',
    nodes=(
        Node('host', HostNode.IMAGE, {'image': ''}, title=SHARED_TEXTS['host']),
        Node('pose', HostNode.TEXT_BLOCK, {'value': POSE_PROMPT}, title=SHARED_TEXTS['pose']),
        Node('redraw', REDRAW.name),
    ),
    links=(('host.IMAGE', 'redraw.host'), ('pose.STRING', 'redraw.pose')),
    stacks=(
        (Group(SHARED_TEXTS['input'], (('host', 'pose'),), note=REDRAW_TEXTS['input']),),
        (Group(SHARED_TEXTS['redraw'], (('redraw',),), STAGE_COLOUR, REDRAW_TEXTS['redraw']),),
    ),
    subgraphs=(REDRAW,),
)

COMBINE = Subgraph(
    name=SHARED_TEXTS['combine'],
    nodes=(
        Node('draw', IMAGE_GENERATE, SAVED_FLAGS, is_paid=True),
        Node('save', HostNode.SAVE_IMAGE, {'filename_prefix': 'image/dreamina/host-in-kitchen'}),
    ),
    links=(('draw.images', 'save.images'),),
    columns=(('draw',), ('save',)),
    inputs=(('pictures', 'draw.images'), ('change', 'draw.prompt')),
    description=COMBINE_TEXTS['combine_description'],
    previews=(('save', IMAGE_PREVIEW),),
)

PLACE_HOST = Workflow(
    slug='image-05-place-a-host-in-a-scene',
    nodes=(
        Node('host', HostNode.IMAGE, {'image': ''}, title=SHARED_TEXTS['host']),
        Node('place', HostNode.IMAGE, {'image': ''}, title=SHARED_TEXTS['place']),
        Node('product', HostNode.IMAGE, {'image': ''}, title=SHARED_TEXTS['product']),
        Node('pictures', HostNode.LIST, title=SHARED_TEXTS['pictures']),
        Node('change', HostNode.TEXT_BLOCK, {'value': PLACE_PROMPT}, title=SHARED_TEXTS['change']),
        Node('combine', COMBINE.name),
    ),
    links=(
        ('host.IMAGE', 'pictures.inputs.input0'),
        ('place.IMAGE', 'pictures.inputs.input1'),
        ('product.IMAGE', 'pictures.inputs.input2'),
        ('pictures.list', 'combine.pictures'),
        ('change.STRING', 'combine.change'),
    ),
    stacks=(
        (
            Group(
                SHARED_TEXTS['input'],
                (('host', 'place', 'product'), ('pictures', 'change')),
                note=COMBINE_TEXTS['input'],
            ),
        ),
        (Group(SHARED_TEXTS['combine'], (('combine',),), STAGE_COLOUR, COMBINE_TEXTS['combine']),),
    ),
    subgraphs=(COMBINE,),
)

IMAGE_WORKFLOWS = (DESIGN_HOST, EDIT_PHOTO, UPSCALE_POSTER, REDRAW_HOST, PLACE_HOST)

__all__ = ['IMAGE_WORKFLOWS']
