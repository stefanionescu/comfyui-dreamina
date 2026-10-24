"""How a paid run shows ComfyUI's progress bar and notices its cancel."""

# The progress bar of a paid node: model checked, media uploaded, run accepted, run finished, outputs downloaded, and
# outputs built.
PROGRESS_STEPS = {
    'CHECKED': 1,
    'UPLOADED': 2,
    'ACCEPTED': 3,
    'RUNNING': 4,
    'DOWNLOADED': 5,
    'TOTAL': 6,
}

# How often a wait checks ComfyUI's cancel, in seconds.
CANCELLATION_POLL_SECONDS = 0.1

__all__ = [
    'CANCELLATION_POLL_SECONDS',
    'PROGRESS_STEPS',
]
