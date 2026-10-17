"""Messages for a generation's outcomes after the run call."""

GENERATION_ABSENT = (
    "Dreamina no longer has a record of this generation, so its record here was deleted. If it finished, its output "
    "is on its canvas in your Dreamina projects at {home_page}."
)

GENERATION_EMPTY = (
    "Dreamina finished this run without any output. Change the prompt or the connected inputs, then run again."
)

GENERATION_EXPIRED = (
    "This generation was recorded too long ago for Dreamina to report it, so its record was deleted. If it finished, "
    "its output is on its canvas in your Dreamina projects at {home_page}."
)

GENERATION_FAILED = (
    "The generation failed on Dreamina: {reason} Change the prompt or the connected inputs, then run again."
)

GENERATION_GONE = (
    "This generation's node is no longer on its Dreamina canvas, so its outputs cannot be collected, and its record "
    "was deleted. Run the node that made it again."
)

GENERATION_KEEPS_RUNNING = (
    "Dreamina cannot stop a generation it accepted, so this one keeps running and is billed. It stays recorded. "
    "Collect its outputs with Generation: Download."
)

GENERATION_UNKNOWN = (
    "This generation is not recorded on this server, or it was already collected. Press R to list the generations "
    "recorded here, then choose one."
)

GENERATIONS_EMPTY = (
    "No generation is recorded on this server. A paid Dreamina node records each run Dreamina accepts, and it stays "
    "listed here until its outputs are collected."
)

GENERATION_UNCOLLECTED = (
    "Dreamina accepted this run and bills it, but ComfyUI could not collect it. {reason} It stays recorded, so "
    "collect it with Generation: Download instead of running the paid node again."
)

RUN_UNCERTAIN = (
    "The Dreamina CLI stopped before it said whether Dreamina accepted this run, and Dreamina shows no run for it "
    "yet. It may still start and be billed. Look for it on the ComfyUI canvas in your Dreamina projects at "
    "{home_page} before you run again."
)

RUN_UNRECORDED = (
    "Dreamina accepted this run, but its reply could not be read, so ComfyUI cannot collect it. It keeps running and "
    "is billed. Find its output on the ComfyUI canvas in your Dreamina projects at {home_page}."
)

STATUS_CODE_REASON = "Dreamina gave error code {code}."

WAIT_LIMIT = (
    "Dreamina accepted this run, so it is billed, but its outputs did not arrive within the request timeout of "
    "{seconds} seconds in Dreamina Settings. It stays recorded. Collect it later with Generation: Download."
)

__all__ = [
    "GENERATIONS_EMPTY",
    "GENERATION_ABSENT",
    "GENERATION_EMPTY",
    "GENERATION_EXPIRED",
    "GENERATION_FAILED",
    "GENERATION_GONE",
    "GENERATION_KEEPS_RUNNING",
    "GENERATION_UNCOLLECTED",
    "GENERATION_UNKNOWN",
    "RUN_UNCERTAIN",
    "RUN_UNRECORDED",
    "STATUS_CODE_REASON",
    "WAIT_LIMIT",
]
