"""Messages for rejected local HTTP requests."""

BODY_NOT_ALLOWED = 'Send no content with a sign-in, sign-out, or install request.'

JSON_DEPTH = 'The request is nested too deeply.'

JSON_DUPLICATE_KEY = 'The request repeats a field name.'

JSON_MAPPING = 'Send a JSON object.'

JSON_SIZE = 'The request is too large.'

JSON_SYNTAX = 'The request is not valid JSON.'

JSON_TYPE = 'Send the request as application/json.'

JSON_VALUES = 'The request holds values JSON cannot carry.'

LOCAL_CONNECTION_REQUIRED = 'Open Dreamina Settings from a browser on the ComfyUI computer, at a localhost address.'

REQUEST_TIMEOUT = 'The request took too long to arrive.'

SETTINGS_REVISION_REQUIRED = 'Send the settings revision you read together with the changed settings.'

__all__ = [
    'BODY_NOT_ALLOWED',
    'JSON_DEPTH',
    'JSON_DUPLICATE_KEY',
    'JSON_MAPPING',
    'JSON_SIZE',
    'JSON_SYNTAX',
    'JSON_TYPE',
    'JSON_VALUES',
    'LOCAL_CONNECTION_REQUIRED',
    'REQUEST_TIMEOUT',
    'SETTINGS_REVISION_REQUIRED',
]
