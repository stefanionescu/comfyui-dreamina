"""Refusals of a node's prompt, arguments, placeholders, and connected values, made before anything is paid."""

ARGUMENTS_INVALID = 'The arguments input is not valid JSON. Write a JSON object, such as {{"ratio": "16:9"}}.'

ARGUMENTS_SHAPE = (
    'The arguments input holds {shape}. Write a JSON object of flag names and values, such as {{"ratio": "16:9"}}.'
)

PROMPT_TWICE = "The prompt input and arguments both set prompt. Remove it from one of them."

PROMPT_REQUIRED = "Write a prompt. Mode {mode} of this model needs one."

# How a refusal names a JSON value that is not text or a number, or not an object.
JSON_SHAPES = {
    "array": "a JSON list",
    "string": "text in double quotes",
    "number": "a number",
    "boolean": "true or false",
    "null": "null",
    "object": "a JSON object",
}

__all__ = ["ARGUMENTS_INVALID", "ARGUMENTS_SHAPE", "JSON_SHAPES", "PROMPT_REQUIRED", "PROMPT_TWICE"]
