"""Messages for media that cannot be encoded, uploaded, downloaded, or read.

{reason} is the CLI's cleaned reason, ending as a sentence.
"""

AUDIO_EMPTY = "The connected audio has no samples."

AUDIO_UNREADABLE = (
    "An audio file Dreamina returned could not be decoded. It is still on the ComfyUI canvas at dreamina.capcut.com."
)

AUDIO_UNWRITABLE = "The connected audio could not be written as WAV. Use mono or stereo audio."

DOWNLOAD_EMPTY = (
    "Dreamina returned an empty file for an output. The run stays recorded, so Generation: Download can collect it "
    "again later."
)

DOWNLOAD_FAILED = (
    "An output could not be downloaded from Dreamina: {reason} The run stays recorded, so Generation: Download can "
    "collect it again."
)

DOWNLOAD_LIMIT = (
    "An output from Dreamina is {size} MB, above the maximum download size of {maximum} MB in Dreamina Settings. "
    "Raise it, then collect the run with Generation: Download."
)

DOWNLOAD_MISMATCH = (
    "A downloaded output did not match the size and checksum Dreamina reported, so it was not used. The run stays "
    "recorded, so Generation: Download can collect it again."
)

IMAGE_CHANNELS = "Connect a ComfyUI image with three or four color channels."

IMAGE_PIXELS = "The connected image holds values that are not numbers. Check the node that made it."

IMAGE_UNREADABLE = (
    "An image Dreamina returned could not be decoded. It is still on the ComfyUI canvas at dreamina.capcut.com."
)

OUTPUTS_MISSING = (
    "Dreamina reports the run finished, but its canvas node holds no finished output from it yet. The run stays "
    "recorded, so Generation: Download can collect it later."
)

RESOURCE_TYPE = (
    "Dreamina returned an output of a type this extension cannot read: {type}. Update the extension, then collect the "
    "run with Generation: Download."
)

UPLOAD_INVALID = (
    "The Dreamina CLI refused a connected file before sending it: {reason} An image may be at most 30 MB "
    "(31,457,280 bytes). Connect a smaller or valid file, then run again."
)

UPLOAD_LIMIT = (
    "A connected {kind} is {size} MB, above the maximum upload size of {maximum} MB in Dreamina Settings. Connect a "
    "smaller {kind}, or raise the limit there."
)

UPLOAD_REFUSED = (
    "Dreamina refused a connected file: {reason} Nothing was billed. Check that the media opens in ComfyUI, then run "
    "again."
)

UPLOAD_UNREADABLE = "Dreamina's answer to an upload could not be read. Nothing was billed. Run again."

VIDEO_UNREADABLE = (
    "A video Dreamina returned could not be read. It is still on the ComfyUI canvas at dreamina.capcut.com."
)

VIDEO_UNWRITABLE = "The connected video could not be written as MP4."

__all__ = [
    "AUDIO_EMPTY",
    "AUDIO_UNREADABLE",
    "AUDIO_UNWRITABLE",
    "DOWNLOAD_EMPTY",
    "DOWNLOAD_FAILED",
    "DOWNLOAD_LIMIT",
    "DOWNLOAD_MISMATCH",
    "IMAGE_CHANNELS",
    "IMAGE_PIXELS",
    "IMAGE_UNREADABLE",
    "OUTPUTS_MISSING",
    "RESOURCE_TYPE",
    "UPLOAD_INVALID",
    "UPLOAD_LIMIT",
    "UPLOAD_REFUSED",
    "UPLOAD_UNREADABLE",
    "VIDEO_UNREADABLE",
    "VIDEO_UNWRITABLE",
]
