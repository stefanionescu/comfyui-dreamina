"""How local media is written for upload, how references reach the CLI, and how outputs are sorted."""

# The mediaType the live model list counts each kind of reference as. The lists name no Element type, and an Element
# is expected to count as an image (run C-15).
MEDIA_TYPES = {
    "image": "image",
    "video": "video",
    "audio": "audio",
    "element": "image",
}

__all__ = ["MEDIA_TYPES"]
