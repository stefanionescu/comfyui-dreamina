"""Refusals of the prompt, arguments, placeholders, and connected values of a node, made before any payment."""

ARGUMENTS_INVALID = 'The arguments input is not valid JSON. Write a JSON object, such as {{"ratio": "16:9"}}.'

ARGUMENTS_SHAPE = (
    'The arguments input holds {shape}. Write a JSON object of flag names and values, such as {{"ratio": "16:9"}}.'
)

PROMPT_TWICE = 'The prompt input and arguments both set prompt. Remove it from one of them.'

PROMPT_REQUIRED = 'Write a prompt. Mode {mode} of this model needs one.'

PROMPT_TOO_LONG = (
    'The prompt has {count:,} characters, and {model} takes at most {maximum:,}. Shorten it by {excess:,} characters, '
    'or choose another model.'
)

PROMPT_TOO_SHORT = 'The prompt has {count:,} characters, and {model} needs at least {minimum:,}. Write a longer one.'

PLACEHOLDER_UNCONNECTED = (
    'The prompt uses {placeholder}, but {input} has {count} connected. Placeholders count from 1 within each input.'
)

SINGLE_VALUE = 'Connect one value to {name}, not a list.'

UPSCALE_SOURCE_EMPTY = (
    'Connect what to upscale: ComfyUI images to images, or the references output of Image: Generate to references.'
)

UPSCALE_SOURCE_LIMIT = 'Connect at most {maximum} images to Image: Upscale. It has {count}.'

UPSCALE_REFERENCE_MEDIA = (
    'Image: Upscale takes only images. Connect the references output of Image: Generate or Image: Upscale. An '
    'Element, a video, or audio cannot be upscaled.'
)

UPSCALE_REFERENCE_RESOURCE = (
    'One of the references is a single image of a run that made several, and Image: Upscale takes whole canvas nodes '
    "only. Connect that node's images output to images instead."
)

UPSCALE_ARGUMENT_KEY = 'Image: Upscale takes only {keys} in arguments, not {key}.'

UPSCALE_ARGUMENT_CHOICE = 'Set {key} in arguments to one of {values}.'

UPSCALE_ARGUMENT_RANGE = 'Set {key} in arguments to a whole number from {minimum} to {maximum}.'

UPSCALE_FLAG_NEEDED = 'Add {key} to arguments: the {mode} mode needs it. Choose one of {values}.'

UPSCALE_MODE_FLAG = 'Leave {key} out of arguments when mode is {mode}: that mode does not take it.'

ELEMENT_MAIN_COUNT = 'Connect one image to main: the clearest image of the subject. Connect other angles to auxiliary.'

ELEMENT_MAIN_MEDIA = "Connect an image to main. An Element, a video, or audio cannot be an Element's main image."

ELEMENT_AUXILIARY_MEDIA = 'Connect only images to auxiliary, such as the side and the back of the subject.'

ELEMENT_VOICE_COUNT = 'Connect one voice clip to voice.'

ELEMENT_VOICE_MEDIA = 'Connect audio to voice, such as the references output of Audio: Generate.'

ELEMENT_TITLE_EMPTY = (
    "Type the Element's name into title, such as Host. Your Dreamina canvas shows the Element under this name."
)

ELEMENT_TITLE_LENGTH = 'Shorten title to at most {maximum} characters. An emoji counts as two.'

# How a refusal names a JSON value that is not text or a number, or not an object.
JSON_SHAPES = {
    'array': 'a JSON list',
    'string': 'text in double quotes',
    'number': 'a number',
    'boolean': 'true or false',
    'null': 'null',
    'object': 'a JSON object',
}

__all__ = [
    'ARGUMENTS_INVALID',
    'ARGUMENTS_SHAPE',
    'ELEMENT_AUXILIARY_MEDIA',
    'ELEMENT_MAIN_COUNT',
    'ELEMENT_MAIN_MEDIA',
    'ELEMENT_TITLE_EMPTY',
    'ELEMENT_TITLE_LENGTH',
    'ELEMENT_VOICE_COUNT',
    'ELEMENT_VOICE_MEDIA',
    'JSON_SHAPES',
    'PLACEHOLDER_UNCONNECTED',
    'PROMPT_REQUIRED',
    'PROMPT_TOO_LONG',
    'PROMPT_TOO_SHORT',
    'PROMPT_TWICE',
    'SINGLE_VALUE',
    'UPSCALE_ARGUMENT_CHOICE',
    'UPSCALE_ARGUMENT_KEY',
    'UPSCALE_ARGUMENT_RANGE',
    'UPSCALE_FLAG_NEEDED',
    'UPSCALE_MODE_FLAG',
    'UPSCALE_REFERENCE_MEDIA',
    'UPSCALE_REFERENCE_RESOURCE',
    'UPSCALE_SOURCE_EMPTY',
    'UPSCALE_SOURCE_LIMIT',
]
