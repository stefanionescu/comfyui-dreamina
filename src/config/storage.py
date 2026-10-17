"""The private state folder, its files and their size limits, and the environment variables that move them."""

# An absolute folder that replaces the platform's own state folder, and the installer's own folder for the CLI, which
# find_binary checks first.
ENVIRONMENT_VARIABLES = {
    "STATE_DIRECTORY": "DREAMINA_COMFY_STATE_DIRECTORY",
    "INSTALL_DIRECTORY": "DREAMINA_CANVAS_INSTALL_DIR",
}

# The state folder's name on macOS and Windows, and under XDG_STATE_HOME elsewhere.
STATE_FOLDER_NAMES = {
    "DEFAULT": "DreaminaComfyUI",
    "XDG": "dreamina-comfy",
}

# Only the folder's owner may open it.
PRIVATE_FOLDER_MODE = 0o700

# A file is written under this prefix, then moved into place; the downloaded installer uses it too.
TEMPORARY_PREFIX = ".dreamina-"

# The settings and the pack's canvas.
FILE_NAMES = {
    "SETTINGS": "settings.json",
    "CANVAS": "canvas.json",
}

# The largest settings, canvas, and generation record files the extension reads.
MAX_FILE_BYTES = {
    "SETTINGS": 65_536,
    "CANVAS": 4_096,
    "GENERATION": 16_384,
}

# The generation records: one file per submit ID, in this folder of the state folder.
GENERATION_FOLDER = "generations"

# A generation record's file name is its submit ID and this suffix.
GENERATION_SUFFIX = ".json"

__all__ = [
    "ENVIRONMENT_VARIABLES",
    "FILE_NAMES",
    "GENERATION_FOLDER",
    "GENERATION_SUFFIX",
    "MAX_FILE_BYTES",
    "PRIVATE_FOLDER_MODE",
    "STATE_FOLDER_NAMES",
    "TEMPORARY_PREFIX",
]
