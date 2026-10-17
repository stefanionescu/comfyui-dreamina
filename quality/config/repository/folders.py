"""Folder ownership policy."""

PYTHON_PREFIX_COLLISION_ALLOWLIST: tuple[str, ...] = ()

# The canvas store joins files.py in the Media and runs milestone, which removes this entry.
SINGLE_FILE_PACKAGE_ALLOWLIST: tuple[str, ...] = ("src/storage",)

DISALLOWED_AMBIGUOUS_FOLDER_NAMES = (
    "bash",
    "common",
    "core",
    "helper",
    "helpers",
    "javascript",
    "python",
    "support",
    "util",
    "utils",
)

# CodeQL has distinct query languages and configurations for Python and JavaScript.
AMBIGUOUS_FOLDER_ALLOWLIST = ("quality/python", "quality/security/codeql/python")

AMBIGUOUS_FOLDER_EXCLUDED_PREFIXES = ("quality/config/",)
