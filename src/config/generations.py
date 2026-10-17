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
# once its output exists; ABSENT is a submission's state when Dreamina keeps no record of the submit ID.
OPERATION_STATES = {
    "SUCCEEDED": "succeeded",
    "ABSENT": "absent",
}

# A wait call that gave no readable answer is made again after this pause, so a broken CLI does not spin.
WAIT_REREAD_SECONDS = 2

__all__ = [
    "LABEL_CHARACTERS",
    "LABEL_SEPARATOR",
    "OPERATION_STATES",
    "RECORD_RETENTION_SECONDS",
    "RECORD_VERSION",
    "WAIT_REREAD_SECONDS",
]
