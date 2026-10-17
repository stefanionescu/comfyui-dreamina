"""Names and tooltips of the inputs every generation node shares."""

# The inputs every generation node can show, in node order: sockets first, then the short values, then the text boxes.
INPUT_NAMES = {
    "IMAGES": "images",
    "VIDEOS": "videos",
    "AUDIO": "audio",
    "REFERENCES": "references",
    "MODEL": "model",
    "CREDIT_CEILING": "credit_ceiling",
    "RUN_NUMBER": "run_number",
    "PROMPT": "prompt",
    "ARGUMENTS": "arguments",
}

# The run number's default and range; changing it sends the same run again.
RUN_NUMBER = {"DEFAULT": 0, "MIN": 0, "MAX": 2**31 - 1}

# The credit ceiling's range: the CLI takes any whole number from 0, and ComfyUI's number widget stops at 2**31 - 1.
CREDIT_CEILING_RANGE = {"MIN": 0, "MAX": 2**31 - 1}

# Tooltips of the inputs every generation node shares, in plain words.
TOOLTIPS = {
    "IMAGES": "Images uploaded with the run. Create List joins several. In the prompt, {{image1}} is the first.",
    "VIDEOS": "Videos uploaded with the run. Create List joins several. In the prompt, {{video1}} is the first.",
    "AUDIO": "Audio clips uploaded with the run. Create List joins several. In the prompt, {{audio1}} is the first.",
    "REFERENCES": (
        "Outputs of other Dreamina nodes and Elements, sent with no upload, before any image, video, or audio. In "
        "the prompt, {{reference1}} is the first."
    ),
    "MODEL": (
        "The Dreamina model to run, by its exact name. A name that is not in your Dreamina model list is refused "
        "before paying, with the closest names."
    ),
    "CREDIT_CEILING": (
        "The most credits this run may cost. Dreamina stops a run that costs more, and nothing is billed."
    ),
    "RUN_NUMBER": "Change it to send the same run again.",
    "PROMPT": (
        "The prompt, sent as written. Point at a connected input with {{image1}}, {{reference1}}, and so on. Leave "
        "it empty to send none."
    ),
}

# The arguments box's tooltip, by kind. A speech voice fits only text reading, so the audio tooltip says when to clear
# it.
_ARGUMENTS = (
    "The model's settings as a JSON object, under Dreamina's flag names, such as {\"duration\": 5}. Model: Info lists "
    'them. Set "mode" to choose the mode.'
)
ARGUMENTS_TOOLTIPS = {
    "image": _ARGUMENTS,
    "video": _ARGUMENTS,
    "audio": (
        'The model\'s settings as a JSON object, under Dreamina\'s flag names, such as {"voice-name": "Jessie"}. A '
        "voice applies to text reading, when nothing is connected. For omni dubbing, or a model that lists no "
        "voice-name, leave {}."
    ),
}

__all__ = ["ARGUMENTS_TOOLTIPS", "CREDIT_CEILING_RANGE", "INPUT_NAMES", "RUN_NUMBER", "TOOLTIPS"]
