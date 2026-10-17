"""How the extension records a generation Dreamina accepted, waits for it, and labels it."""

# The canvas and generation record format; a reader refuses any other.
RECORD_VERSION = 1

# Dreamina does not document how long it keeps a submission readable, so an older record is deleted instead of read.
RECORD_RETENTION_SECONDS = 2_592_000

# A recorded generation's label in Generation: Download: the start of its submit ID, its model, and when it was sent,
# to the minute in UTC.
LABEL_SEPARATOR = " · "
LABEL_CHARACTERS = {
    "SUBMIT_ID": 8,
    "TIME": 16,
}

# Dreamina's state words, as the contract runs recorded them. SUCCEEDED is a resource's state in an operation reply
# once its output exists.
OPERATION_STATES = {
    "SUCCEEDED": "succeeded",
}

# The code of operation status and operation wait, with exit 20, for a submit ID Dreamina keeps no record of (run
# C-16). It never means the run is still going.
SUBMISSION_ABSENT = "cli.operation_submission_absent"

# The arguments keys Image: Upscale takes: node upscale image's own flags. Their allowed values, ranges, and defaults
# are read from the CLI's schema each process.
UPSCALE_FLAGS = ("mode", "resolution", "detail")

# What each upscale mode needs and takes besides mode, as the schema's constraints state it: pro needs resolution and
# takes detail; normal takes neither.
UPSCALE_MODES = {
    "pro": {"REQUIRED": ("resolution",), "TAKEN": ("resolution", "detail")},
    "normal": {"REQUIRED": (), "TAKEN": ()},
}

# The model name an upscale's record carries, so Generation: Download labels it.
UPSCALE_MODEL = "upscale"

# How node create image registers an uploaded resource as an image node's output.
UPSCALE_IMPORT_KIND = "local_upload"

# The command that upscales image nodes, as the CLI check lists its flags.
UPSCALE_COMMAND = "node upscale image"

# Image: Upscale's starting credit_ceiling: Part 0's quote for one 2K pro upscale, rounded up to the next 10.
UPSCALE_CEILING = 10

# Image: Upscale's starting arguments: the pro mode, the CLI's default, needs a resolution, and 2K is the smallest.
UPSCALE_ARGUMENTS = '{"resolution": "2K"}'

# How the schema writes a flag's rule: the text before the first ";" of constraints lists the allowed values split by
# "|", or gives a whole-number range such as "1..100".
SCHEMA_CONSTRAINTS = {"PART": ";", "CHOICE": "|"}

# A wait call that gave no readable answer is made again after this pause, so a broken CLI does not spin.
WAIT_REREAD_SECONDS = 2

__all__ = [
    "LABEL_CHARACTERS",
    "LABEL_SEPARATOR",
    "OPERATION_STATES",
    "RECORD_RETENTION_SECONDS",
    "RECORD_VERSION",
    "SCHEMA_CONSTRAINTS",
    "SUBMISSION_ABSENT",
    "UPSCALE_ARGUMENTS",
    "UPSCALE_CEILING",
    "UPSCALE_COMMAND",
    "UPSCALE_FLAGS",
    "UPSCALE_IMPORT_KIND",
    "UPSCALE_MODEL",
    "UPSCALE_MODES",
    "WAIT_REREAD_SECONDS",
]
