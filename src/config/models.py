"""The names the model check reads from Dreamina's model list, and each generation node's starting values."""

# The generation nodes, by what their models make, in menu order; each is a model list type.
KINDS = ("image", "video", "audio")

# The node that runs each kind, as a refusal names it.
KIND_NODES = {
    "image": "Image: Generate",
    "video": "Video: Generate",
    "audio": "Audio: Generate",
}

# The starting value of each node's model box. The person types any other name; these are the only model names here.
DEFAULT_MODELS = {
    "image": "seedream_5.0_lite",
    "video": "seedance_2.0_mini",
    "audio": "seed_audio_v1",
}

# The modes a node chooses by itself, by kind and role. Any other mode a model lists runs when arguments sets it.
MODES = {
    "image": {"TEXT": "t2i", "IMAGES": "i2i"},
    "video": {"TEXT": "t2v", "FRAMES": "first_last_frame", "MULTIMODAL": "m2v"},
    "audio": {"SPEECH": "tts"},
}

# The speech scenarios a node chooses by itself: reading text when nothing is connected, dubbing when something is.
SCENARIOS = {"READING": "text-reading", "DUBBING": "omni-dubbing"}

# The arguments keys that choose the mode entry; they are never sent as flags of their own.
SELECTION_KEYS = {"MODE": "mode", "SCENARIO": "scenario"}

# The flag the prompt box fills.
PROMPT_FLAG = "prompt"

# The flag that sets how many outputs a run makes, and the value sent when arguments does not set it.
COUNT_FLAG = "count"
COUNT_VALUE = "1"

# The dashes model list writes before each flag name, and the pack writes back when it builds the call.
FLAG_PREFIX = "--"

# The most images first_last_frame takes: the first frame, then the last.
FRAME_IMAGES = 2

# How many close model names a refusal suggests.
SUGGESTION_COUNT = 3

# The CLI call that lists one kind's models; the kind follows it.
LIST_COMMAND = ("model", "list", "--type")

# Seconds one model list read may take. A read takes well under a second; this bounds a CLI that stops answering.
LIST_TIMEOUT_SECONDS = 60

__all__ = [
    "COUNT_FLAG",
    "COUNT_VALUE",
    "DEFAULT_MODELS",
    "FLAG_PREFIX",
    "FRAME_IMAGES",
    "KINDS",
    "KIND_NODES",
    "LIST_COMMAND",
    "LIST_TIMEOUT_SECONDS",
    "MODES",
    "PROMPT_FLAG",
    "SCENARIOS",
    "SELECTION_KEYS",
    "SUGGESTION_COUNT",
]
