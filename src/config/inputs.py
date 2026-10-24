"""Names and tooltips of the inputs every generation node shares."""

# The inputs every generation node can show, in node order: sockets first, then the short values, then the text boxes.
# Each node places its own flags after the credit ceiling.
INPUT_NAMES = {
    'IMAGES': 'images',
    'VIDEOS': 'videos',
    'AUDIO': 'audio',
    'REFERENCES': 'references',
    'MODEL': 'model',
    'CREDIT_CEILING': 'credit_ceiling',
    'RUN_NUMBER': 'run_number',
    'PROMPT': 'prompt',
    'ARGUMENTS': 'arguments',
}

# The run number's default and range; changing it sends the same run again.
RUN_NUMBER = {'DEFAULT': 0, 'MIN': 0, 'MAX': 2**31 - 1}

# The credit ceiling's range: the CLI takes any whole number from 0, and ComfyUI's number widget stops at 2**31 - 1.
CREDIT_CEILING_RANGE = {'MIN': 0, 'MAX': 2**31 - 1}

# The starting credit_ceiling of each generation node: its default model's quote at its starting flags, rounded up to
# the next 10, from Part 0's price sweep.
DEFAULT_CEILINGS = {
    'image': 10,
    'video': 20,
    'audio': 20,
}

# The flags each generation node shows as inputs, in node order, by Dreamina's flag name, with the value each starts
# at. Every model of the kind lists them, and the list gives no defaults, so the node always sends them; the starting
# values suit the default model.
FLAGS: dict[str, dict[str, str | int]] = {
    'image': {'ratio': '1:1', 'resolution': '2K', 'count': 1},
    'video': {'ratio': '16:9', 'resolution': '720p', 'duration': 4, 'count': 1},
    'audio': {},
}

# The least value of each flag input that takes a number; the node checks the range of the model free, before
# paying.
FLAG_MINIMUMS = {'duration': 1, 'count': 1}

# The one-line flag inputs of each generation node, by Dreamina's flag name, with the text each starts with. An empty
# one sends nothing.
LINES: dict[str, dict[str, str]] = {
    'image': {},
    'video': {},
    'audio': {'voice-name': 'Jessie'},
}

# Tooltips of the inputs every generation node shares, in plain words.
TOOLTIPS = {
    'IMAGES': 'Images uploaded with the run. Create List joins several. In the prompt, {{image1}} is the first.',
    'VIDEOS': 'Videos uploaded with the run. Create List joins several. In the prompt, {{video1}} is the first.',
    'AUDIO': 'Audio clips uploaded with the run. Create List joins several. In the prompt, {{audio1}} is the first.',
    'REFERENCES': (
        'Outputs of other Dreamina nodes and Elements, sent with no upload, before any image, video, or audio. In '
        'the prompt, {{reference1}} is the first.'
    ),
    'MODEL': (
        'The Dreamina model to run, by its exact name. A name that is not in your Dreamina model list is refused '
        'before paying, with the closest names.'
    ),
    'CREDIT_CEILING': (
        'The most credits this run may cost. Dreamina stops a run that costs more, and nothing is billed.'
    ),
    'RUN_NUMBER': 'Change this number to send the same run again.',
    'PROMPT': (
        'The prompt, sent as written. Point at a connected input with {{image1}}, {{reference1}}, and so on. Leave '
        'it empty to send none.'
    ),
    'ARGUMENTS': (
        'The model\'s other flags as a JSON object, under the names Model: Info lists, such as {"mode": "m2v"}. Set '
        '"mode" to choose the mode. Leave it empty to send none.'
    ),
    'ratio': 'The shape of the result, such as 16:9. Model: Info lists the shapes each model takes.',
    'resolution': 'The size of the result, such as 2K or 720p. Model: Info lists the sizes each model takes.',
    'duration': 'The length in seconds. Model: Info lists the lengths each model takes.',
    'count': 'How many results to make. Each one costs credits.',
    'voice-name': (
        'The voice for text reading, by the name Model: Info lists. Leave it empty for omni dubbing, when something '
        'is connected.'
    ),
}

__all__ = [
    'CREDIT_CEILING_RANGE',
    'DEFAULT_CEILINGS',
    'FLAGS',
    'FLAG_MINIMUMS',
    'INPUT_NAMES',
    'LINES',
    'RUN_NUMBER',
    'TOOLTIPS',
]
