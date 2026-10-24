"""The audio workflows: voice a script in a chosen voice, and give a drawn host a voice."""

from scripts.nodes.host import HostNode
from scripts.workflows.page.graph import Node, Group, Subgraph, Workflow
from scripts.workflows.page.config import STAGE_COLOUR, IMAGE_PREVIEW
from scripts.workflows.descriptions.nodes import MODEL_REPORT, AUDIO_GENERATE, IMAGE_GENERATE
from scripts.workflows.descriptions.notes import WORKFLOW_TEXTS
from scripts.workflows.descriptions.texts import SHARED_TEXTS

SEED_AUDIO = 'seed_audio_v1'
VOICE_FLAGS = {'voice_name': 'Good Guy'}
CAST_FLAGS = {'ratio': '3:4'}
SPEAK_FLAGS = {'voice_name': ''}
SCRIPT_PROMPT = (
    'Welcome back to the show. Today we have three new sneakers, and the first pair is already selling fast.'
)
CAST_HOST = (
    'A friendly live-shopping host in his thirties with short curly hair and a denim jacket. Waist up, facing the '
    'camera, in a bright studio, photorealistic.'
)
LINE_PROMPT = "Hi everyone, it's so good to see you. I've got something special to show you today."
SCRIPT_TEXTS = WORKFLOW_TEXTS['audio-01-voice-a-script']
HOST_TEXTS = WORKFLOW_TEXTS['audio-02-give-a-host-a-voice']

VOICE = Subgraph(
    name=SHARED_TEXTS['voice'],
    nodes=(
        Node('speak', AUDIO_GENERATE, VOICE_FLAGS, is_paid=True),
        Node('save', HostNode.SAVE_AUDIO, {'filename_prefix': 'audio/dreamina/script-voice'}),
    ),
    links=(('speak.audio', 'save.audio'),),
    columns=(('speak',), ('save',)),
    inputs=(('script', 'speak.prompt'),),
    description=SCRIPT_TEXTS['voice_description'],
)

VOICE_SCRIPT = Workflow(
    slug='audio-01-voice-a-script',
    nodes=(
        Node('script', HostNode.TEXT_BLOCK, {'value': SCRIPT_PROMPT}, title=SHARED_TEXTS['script']),
        Node('info', MODEL_REPORT, {'model': SEED_AUDIO}),
        Node('row', HostNode.PREVIEW, title=SHARED_TEXTS['info']),
        Node('voice', VOICE.name),
    ),
    links=(('script.STRING', 'voice.script'), ('info.info', 'row.source')),
    stacks=(
        (
            Group(SHARED_TEXTS['input'], (('script',),), note=SCRIPT_TEXTS['input']),
            Group(SHARED_TEXTS['voices'], (('info',), ('row',)), note=SCRIPT_TEXTS['voices']),
        ),
        (Group(SHARED_TEXTS['voice'], (('voice',),), STAGE_COLOUR, SCRIPT_TEXTS['voice']),),
    ),
    subgraphs=(VOICE,),
)

CAST = Subgraph(
    name=SHARED_TEXTS['cast'],
    nodes=(
        Node('draw', IMAGE_GENERATE, CAST_FLAGS, is_paid=True),
        Node('look', HostNode.PREVIEW_IMAGE),
    ),
    links=(('draw.images', 'look.images'),),
    columns=(('draw',), ('look',)),
    inputs=(('host', 'draw.prompt'),),
    outputs=(('references', 'draw.references'),),
    description=HOST_TEXTS['cast_description'],
    previews=(('look', IMAGE_PREVIEW),),
)

SPEAK = Subgraph(
    name=SHARED_TEXTS['speak'],
    nodes=(
        Node('speak', AUDIO_GENERATE, SPEAK_FLAGS, is_paid=True),
        Node('save', HostNode.SAVE_AUDIO, {'filename_prefix': 'audio/dreamina/host-voice'}),
    ),
    links=(('speak.audio', 'save.audio'),),
    columns=(('speak',), ('save',)),
    inputs=(('references', 'speak.references'), ('line', 'speak.prompt')),
    description=HOST_TEXTS['speak_description'],
)

HOST_VOICE = Workflow(
    slug='audio-02-give-a-host-a-voice',
    nodes=(
        Node('host', HostNode.TEXT_BLOCK, {'value': CAST_HOST}, title=SHARED_TEXTS['host']),
        Node('line', HostNode.TEXT_BLOCK, {'value': LINE_PROMPT}, title=SHARED_TEXTS['line']),
        Node('cast', CAST.name),
        Node('speak', SPEAK.name),
    ),
    links=(('host.STRING', 'cast.host'), ('cast.references', 'speak.references'), ('line.STRING', 'speak.line')),
    stacks=(
        (Group(SHARED_TEXTS['input'], (('host', 'line'),), note=HOST_TEXTS['input']),),
        (Group(SHARED_TEXTS['cast'], (('cast',),), STAGE_COLOUR, HOST_TEXTS['cast']),),
        (Group(SHARED_TEXTS['speak'], (('speak',),), STAGE_COLOUR, HOST_TEXTS['speak']),),
    ),
    subgraphs=(CAST, SPEAK),
)

AUDIO_WORKFLOWS = (VOICE_SCRIPT, HOST_VOICE)

__all__ = ['AUDIO_WORKFLOWS', 'CAST']
