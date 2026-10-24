"""How the extension records a generation Dreamina accepted, waits for it, and labels it."""

# The canvas and generation record format; a reader refuses any other.
RECORD_VERSION = 1

# Dreamina does not document how long it keeps a submission readable, so the extension deletes an older record instead
# of reading it.
RECORD_RETENTION_SECONDS = 2_592_000

# A recorded generation's label in Generation: Download: the start of its submit ID, its model, and when the extension
# sent it, to the minute in UTC.
LABEL_SEPARATOR = ' · '
LABEL_CHARACTERS = {
    'SUBMIT_ID': 8,
    'TIME': 16,
}

# Dreamina's state words, as the contract runs recorded them. SUCCEEDED is a resource's state in an operation reply
# once its output exists.
OPERATION_STATES = {
    'SUCCEEDED': 'succeeded',
}

# The code of operation status and operation wait, with exit 20, for a submit ID Dreamina keeps no record of, as in run
# C-16. It never means the run is still going.
SUBMISSION_ABSENT = 'cli.operation_submission_absent'

# The inputs of Image: Upscale's settings, named as the CLI's flags.
UPSCALE_SETTINGS = {'MODE': 'mode', 'RESOLUTION': 'resolution', 'DETAIL': 'detail'}

# The upscale modes, in node order: pro, the CLI's default, redraws the image larger with fine detail, and normal
# enlarges it to twice its size.
UPSCALE_MODES = ('pro', 'normal')

# The settings the pro mode takes, as the CLI's schema lists them: its resolutions, and its detail range and default.
# Normal takes neither. The operation checks each value against the live schema again before paying.
UPSCALE_RESOLUTIONS = ('2K', '4K', '8K')
UPSCALE_DETAIL = {'DEFAULT': 50, 'MIN': 1, 'MAX': 100}

# The model name an upscale's record carries, so Generation: Download labels it.
UPSCALE_MODEL = 'upscale'

# How node create image registers an uploaded resource as the output of an image node.
UPSCALE_IMPORT_KIND = 'local_upload'

# The command that upscales image nodes, as the CLI check lists its flags.
UPSCALE_COMMAND = 'node upscale image'

# Image: Upscale's starting credit_ceiling: Part 0's quote for one 2K pro upscale, rounded up to the next 10.
UPSCALE_CEILING = 10

# How the schema writes a flag's rule. The text before the first `;` of constraints lists the allowed values split by
# `|`, or gives a whole-number range such as `1..100`.
SCHEMA_CONSTRAINTS = {'PART': ';', 'CHOICE': '|'}

# After this pause, the extension repeats a wait call that gave no readable answer, so a broken CLI does not spin.
WAIT_REREAD_SECONDS = 2

__all__ = [
    'LABEL_CHARACTERS',
    'LABEL_SEPARATOR',
    'OPERATION_STATES',
    'RECORD_RETENTION_SECONDS',
    'RECORD_VERSION',
    'SCHEMA_CONSTRAINTS',
    'SUBMISSION_ABSENT',
    'UPSCALE_CEILING',
    'UPSCALE_COMMAND',
    'UPSCALE_DETAIL',
    'UPSCALE_IMPORT_KIND',
    'UPSCALE_MODEL',
    'UPSCALE_MODES',
    'UPSCALE_RESOLUTIONS',
    'UPSCALE_SETTINGS',
    'WAIT_REREAD_SECONDS',
]
