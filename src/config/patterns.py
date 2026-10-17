"""Regular expression text that its owners compile once."""

# A settings revision, a SHA-256 digest.
REVISION_PATTERN = r"^[a-f0-9]{64}$"

# A CLI release such as 1.0.3; groups 1 to 3 are compared as numbers with MINIMUM_VERSION.
VERSION_PATTERN = r"^(\d+)\.(\d+)\.(\d+)(?:[-+][0-9A-Za-z.-]+)?$"

# A placeholder of this pack in a prompt, such as {{image1}}: one of its four words and a number from 1, in double
# braces, not after the backslash the CLI uses for a literal {{.
PLACEHOLDER_PATTERN = r"(?<!\\)\{\{(image|video|audio|reference)([1-9][0-9]*)\}\}"

# A whole-number range at the start of a schema constraint, such as "1..100" or "1..20 unique canonical Node IDs".
SCHEMA_RANGE_PATTERN = r"^(\d+)\.\.(\d+)\b"

# A CLI reason or the installer's output is cleaned before a person sees it. Links, file paths, and identifier-shaped
# text are removed. Identifier-shaped text is a UUID, a canvas node ID, or a run of 32 or more letters, digits, and
# base64 signs that holds both a letter and a digit.
REASON_PATTERNS = {
    "URL": r"https?://\S+",
    "PATH": r"(?<![\w.~])(?:~|[A-Za-z]:)?(?:[\\/][\w.@+-]+){2,}[\\/]?",
    "IDENTIFIER": (
        r"\b[0-9A-Fa-f]{8}(?:-[0-9A-Fa-f]{4}){3}-[0-9A-Fa-f]{12}\b"
        r"|\bnode_[A-Za-z0-9_-]+"
        r"|(?<![\w+/=-])(?=[\w+/=]*\d)(?=[\w+/=]*[A-Za-z])[\w+/=]{32,}"
    ),
}

__all__ = [
    "PLACEHOLDER_PATTERN",
    "REASON_PATTERNS",
    "REVISION_PATTERN",
    "SCHEMA_RANGE_PATTERN",
    "VERSION_PATTERN",
]
