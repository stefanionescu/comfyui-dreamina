"""The names the model check reads from Dreamina's model list, and the starting values of each generation node."""

# The generation nodes, by what their models make, in menu order; each is a model list type.
KINDS = ('image', 'video', 'audio')

# The node that runs each kind, as a refusal names it.
KIND_NODES = {
    'image': 'Image: Generate',
    'video': 'Video: Generate',
    'audio': 'Audio: Generate',
}

# The starting value in the model box of each node. The person types any other name; these are the only model names
# here.
DEFAULT_MODELS = {
    'image': 'seedream_5.0_lite',
    'video': 'seedance_2.0_mini',
    'audio': 'seed_audio_v1',
}

# The starting value in the arguments box of each node: the required flags of the default model's first mode.
DEFAULT_ARGUMENTS = {
    'image': '{"ratio": "1:1", "resolution": "2K"}',
    'video': '{"ratio": "16:9", "resolution": "720p", "duration": 4}',
    'audio': '{"voice-name": "Jessie"}',
}

# The modes a node chooses by itself for each kind and role. Any other mode a model lists runs when arguments sets it.
MODES = {
    'image': {'TEXT': 't2i', 'IMAGES': 'i2i'},
    'video': {'TEXT': 't2v', 'FRAMES': 'first_last_frame', 'MULTIMODAL': 'm2v'},
    'audio': {'SPEECH': 'tts'},
}

# The speech scenarios a node chooses by itself: reading text when the node has nothing connected, dubbing when it has
# something connected.
SCENARIOS = {'READING': 'text-reading', 'DUBBING': 'omni-dubbing'}

# The arguments keys that choose the mode entry; they are never sent as flags of their own.
SELECTION_KEYS = {'MODE': 'mode', 'SCENARIO': 'scenario'}

# The flag the prompt box fills.
PROMPT_FLAG = 'prompt'

# The flag that sets how many outputs a run makes, and the value sent when arguments does not set it.
COUNT_FLAG = 'count'
COUNT_VALUE = '1'

# The dashes model list writes before each flag name, and the pack writes back when it builds the call.
FLAG_PREFIX = '--'

# The most images first_last_frame takes: the first frame, then the last.
FRAME_IMAGES = 2

# How many close model names a refusal suggests.
SUGGESTION_COUNT = 3

# The CLI call that lists one kind's models; the kind follows it.
LIST_COMMAND = ('model', 'list', '--type')

# Voices read per voice list call: the CLI's largest page, so a catalog of up to 100 voices takes one call.
VOICE_PAGE_COUNT = 100

# Seconds one model list read may take. A read takes well under a second; this bounds a CLI that stops answering.
LIST_TIMEOUT_SECONDS = 60

__all__ = [
    'COUNT_FLAG',
    'COUNT_VALUE',
    'DEFAULT_ARGUMENTS',
    'DEFAULT_MODELS',
    'FLAG_PREFIX',
    'FRAME_IMAGES',
    'KINDS',
    'KIND_NODES',
    'LIST_COMMAND',
    'LIST_TIMEOUT_SECONDS',
    'MODES',
    'PROMPT_FLAG',
    'SCENARIOS',
    'SELECTION_KEYS',
    'SUGGESTION_COUNT',
    'VOICE_PAGE_COUNT',
]
