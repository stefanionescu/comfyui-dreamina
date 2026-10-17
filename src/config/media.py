"""How local media is written for upload, how references reach the CLI, and how outputs are sorted."""

# A ComfyUI IMAGE tensor: batch, height, width, and three or four channels. Each connected frame reaches the encoder
# alone, as [1, H, W, C], and a decoded image is [1, H, W, 3].
IMAGE_TENSOR = {
    "DIMENSIONS": 4,
    "RGB_CHANNELS": 3,
    "RGBA_CHANNELS": 4,
}

# What each kind of local media is written as before its upload, and the --type resource upload takes for it: PNG at
# the image's own size, 16-bit WAV, and MP4.
UPLOAD_FORMATS = {
    "image": {"EXTENSION": "png", "TYPE": "image"},
    "video": {"EXTENSION": "mp4", "TYPE": "video"},
    "audio": {"EXTENSION": "wav", "TYPE": "audio"},
}

# The WAV container and codec PyAV writes audio with.
WAV = {
    "FORMAT": "wav",
    "CODEC": "pcm_s16le",
}

# An upload or a download bills nothing, so one whose outcome is unknown is sent a second time, and never a third.
FREE_ATTEMPTS = 2

# The CLI's code for an upload whose outcome it could not learn; the same resource ID makes the second try safe.
UPLOAD_STATE_UNKNOWN = "cli.upload_state_unknown"

# The word the CLI writes before a node ID or a resource ID, in --ref and in a prompt placeholder.
REFERENCE_TYPES = {
    "node": "node",
    "resource": "res",
}

# Each placeholder word a prompt may use, with the input whose items it counts from 1, in --ref order.
PLACEHOLDERS = {
    "reference": "references",
    "image": "images",
    "video": "videos",
    "audio": "audio",
}

# The mediaType the live model list counts each kind of reference as. The lists name no Element type, and an Element
# is expected to count as an image (run C-15).
MEDIA_TYPES = {
    "image": "image",
    "video": "video",
    "audio": "audio",
    "element": "image",
}

# The modes whose frames take images only: an Element counts as an image in the list's limits, but never fills a frame.
FRAME_MODES = ("first_last_frame",)

# In speech, a voice set with this flag fills one audio reference slot, as a connected audio clip does.
VOICE_REFERENCE = {
    "FLAG": "voice-name",
    "MODE": "tts",
}

# The kind of an output resource by the type node show gives it.
RESOURCE_KINDS = {
    "image": "image",
    "video": "video",
    "audio": "audio",
}

# The status node show gives a resource that finished and can be downloaded.
RESOURCE_SUCCESS = "success"

__all__ = [
    "FRAME_MODES",
    "FREE_ATTEMPTS",
    "IMAGE_TENSOR",
    "MEDIA_TYPES",
    "PLACEHOLDERS",
    "REFERENCE_TYPES",
    "RESOURCE_KINDS",
    "RESOURCE_SUCCESS",
    "UPLOAD_FORMATS",
    "UPLOAD_STATE_UNKNOWN",
    "VOICE_REFERENCE",
    "WAV",
]
