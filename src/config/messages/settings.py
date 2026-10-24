"""Messages for private settings, state storage, and the sign-in routes."""

PRIVATE_STATE_LOCATION = (
    "Keep the Dreamina extension's private state outside ComfyUI, its package, and its media folders."
)

RUNTIME_NOT_READY = 'The Dreamina nodes are still loading. Wait for ComfyUI to finish starting, then run again.'

SETTINGS_CHANGED = (
    'The settings changed in another window. Select Reload settings in Dreamina Settings, then save again.'
)

SETTINGS_RANGE = 'Choose each Dreamina setting within its range in Dreamina Settings.'

SETTINGS_UNREADABLE = (
    "The Dreamina extension's private settings could not be read. Check the state folder's permissions."
)

SETTINGS_WHOLE_NUMBERS = 'Enter whole numbers in Dreamina Settings.'

SETTING_READ_ONLY = 'Change only the request limits that Dreamina Settings shows.'

SETTING_UNKNOWN = 'The Dreamina settings file has an unknown setting. Remove it or reset the settings.'

SIGN_IN_CODE_MISSING = 'Dreamina did not return a sign-in code. In Dreamina Settings, select Sign in again.'

STATE_DIRECTORY_ABSOLUTE = 'Set DREAMINA_COMFY_STATE_DIRECTORY to an absolute folder path.'

STATE_FILE_SIZE = 'A Dreamina state file is larger than expected. Check the state folder.'

STATE_UNREADABLE = (
    "The Dreamina extension's private state could not be read or written. Check the state folder's permissions."
)

__all__ = [
    'PRIVATE_STATE_LOCATION',
    'RUNTIME_NOT_READY',
    'SETTINGS_CHANGED',
    'SETTINGS_RANGE',
    'SETTINGS_UNREADABLE',
    'SETTINGS_WHOLE_NUMBERS',
    'SETTING_READ_ONLY',
    'SETTING_UNKNOWN',
    'SIGN_IN_CODE_MISSING',
    'STATE_DIRECTORY_ABSOLUTE',
    'STATE_FILE_SIZE',
    'STATE_UNREADABLE',
]
