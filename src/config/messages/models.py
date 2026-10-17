"""Messages about finding a model in the person's Dreamina model list, choosing its mode, and checking its flags."""

MODEL_EMPTY = "Type a Dreamina model name in model, such as {example}."

MODEL_UNKNOWN = (
    "The model {model} is not in your Dreamina model list. The closest names are {names}. Copy one into model."
)

MODEL_AMBIGUOUS = "The name {model} matches more than one Dreamina model: {names}. Type one of them in model."

MODEL_KIND = "The model {model} makes {made}, so it runs in {node}, not in {this}."

MODEL_LIST_EMPTY = "Your Dreamina model list holds no {made} models. Check that your Dreamina plan includes them."

MODEL_LIST_UNREADABLE = (
    "The Dreamina CLI sent a model list this extension cannot read. Update the extension, or try again later."
)

MODE_UNKNOWN = 'The model {model} has no mode named {mode}. Set "mode" in arguments to one of its modes: {modes}.'

MODE_NOT_OFFERED = (
    'The connected inputs call for the {mode} mode, which the model {model} does not have. Set "mode" in arguments '
    "to one of its modes: {modes}."
)

SCENARIO_UNKNOWN = (
    'The model {model} has no scenario named {scenario}. Set "scenario" in arguments to one of: {scenarios}.'
)

SCENARIO_NOT_OFFERED = (
    'The connected inputs call for the {scenario} scenario, which the model {model} does not have. Set "scenario" '
    "in arguments to one of: {scenarios}."
)

REFERENCES_NO_ENTRY = (
    "No entry of mode {mode} of this model takes what is connected ({connected}). Its entries take {limits}. Change "
    "the inputs, or set another mode in arguments."
)

ARGUMENT_UNKNOWN = "The model {model} has no flag named {flag}. Its flags are {flags}."

ARGUMENT_DASHES = 'Write the flag {flag} without its leading dashes, as "{name}".'

FLAG_NOT_IN_MODE = (
    "Mode {mode} of this model has no flag named {flag}. Its flags are {flags}. Remove it from arguments, or set "
    "another mode."
)

FLAG_REQUIRED = (
    'Set "{flag}" in arguments. Mode {mode} of this model needs it, and Model: Info lists its allowed values.'
)

VALUE_TYPE = "Write {flag} as text or a number, not {shape}."

VALUE_CHOICES = "The flag {flag} does not take {value}. Write one of: {values}."

VALUE_NUMBER = "The flag {flag} takes a number, and it has {value}."

VALUE_TOO_LOW = "The flag {flag} takes {minimum} or more, and it has {value}."

VALUE_TOO_HIGH = "The flag {flag} takes at most {maximum}, and it has {value}."

VALUE_STEP = "The flag {flag} takes steps of {step}, so {value} cannot be sent. Write {lower} or {upper}."

VALUE_TOO_SHORT = "The flag {flag} takes at least {minimum} characters, and it has {count}."

VALUE_TOO_LONG = "The flag {flag} takes at most {maximum} characters, and it has {count}."

REFERENCES_ANY_OF = "Mode {mode} of this model needs at least one reference of these kinds: {media}. Connect one."

REFERENCES_ELEMENT_FRAME = (
    "Mode {mode} takes only images as frames, and an Element cannot be one. Disconnect the Element, or set another "
    "mode in arguments."
)

REFERENCES_EXCLUSIVE = (
    "Mode {mode} of this model cannot take {media} references together. Keep one kind and disconnect the others."
)

REFERENCES_NONE = (
    "Mode {mode} of this model takes no images, videos, audio, or references, but the run has {count}. Disconnect "
    "them, or set another mode in arguments."
)

REFERENCES_TOTAL = (
    "Mode {mode} of this model takes at least {minimum} and at most {maximum} references in all, but the run has "
    "{count}."
)

REFERENCE_KIND_COUNT = (
    "Mode {mode} of this model takes at least {minimum} and at most {maximum} {media} references, but the run has "
    "{count}."
)

REFERENCE_KIND_REFUSED = (
    "Mode {mode} of this model takes no {media} references, but the run has {count}. Disconnect them, or set another "
    "mode in arguments."
)

VOICE_COUNTED = "The voice-name in arguments counts as one audio reference."

# What each kind of model makes, as the refusals name it, and every kind together, for Model: Info.
KIND_NAMES = {"image": "images", "video": "videos", "audio": "audio"}
ANY_KIND = "images, videos, or audio"

# A mode with a scenario, as the refusals name it, such as "tts (text-reading)".
MODE_LABEL = "{name} ({scenario})"

# One mode entry's reference limits, as REFERENCES_NO_ENTRY lists them, such as "1 to 1 references (image 1 to 1)".
REFERENCE_LIMITS = "{minimum} to {maximum} references ({types})"

# One media type's limits inside REFERENCE_LIMITS, and the text for an entry that enables none.
TYPE_LIMITS = "{media} {minimum} to {maximum}"
NO_MEDIA = "no media"

# What is connected, as REFERENCES_NO_ENTRY says it: one count per media type, or nothing.
CONNECTED_COUNT = "{media} {count}"
NOTHING_CONNECTED = "nothing"

__all__ = [
    "ANY_KIND",
    "ARGUMENT_DASHES",
    "ARGUMENT_UNKNOWN",
    "CONNECTED_COUNT",
    "FLAG_NOT_IN_MODE",
    "FLAG_REQUIRED",
    "KIND_NAMES",
    "MODEL_AMBIGUOUS",
    "MODEL_EMPTY",
    "MODEL_KIND",
    "MODEL_LIST_EMPTY",
    "MODEL_LIST_UNREADABLE",
    "MODEL_UNKNOWN",
    "MODE_LABEL",
    "MODE_NOT_OFFERED",
    "MODE_UNKNOWN",
    "NOTHING_CONNECTED",
    "NO_MEDIA",
    "REFERENCES_ANY_OF",
    "REFERENCES_ELEMENT_FRAME",
    "REFERENCES_EXCLUSIVE",
    "REFERENCES_NONE",
    "REFERENCES_NO_ENTRY",
    "REFERENCES_TOTAL",
    "REFERENCE_KIND_COUNT",
    "REFERENCE_KIND_REFUSED",
    "REFERENCE_LIMITS",
    "SCENARIO_NOT_OFFERED",
    "SCENARIO_UNKNOWN",
    "TYPE_LIMITS",
    "VALUE_CHOICES",
    "VALUE_NUMBER",
    "VALUE_STEP",
    "VALUE_TOO_HIGH",
    "VALUE_TOO_LONG",
    "VALUE_TOO_LOW",
    "VALUE_TOO_SHORT",
    "VALUE_TYPE",
    "VOICE_COUNTED",
]
