"""The Dreamina CLI: its file names, install folders, call arguments, commands, exit codes, limits, and pages."""

# The CLI's file name on macOS and Linux, and on Windows.
BINARY_NAMES = {
    "POSIX": "dreamina-canvas",
    "WINDOWS": "dreamina-canvas.exe",
}

# The installer's default folder, as parts under the home folder: ~/.local/bin, and %USERPROFILE%\bin on Windows.
INSTALL_FOLDERS = {
    "POSIX": (".local", "bin"),
    "WINDOWS": ("bin",),
}

# Every call starts with these: one JSON object per reply, and a stop instead of any prompt.
GLOBAL_ARGUMENTS = ("--format", "json", "--non-interactive")

# The release the extension's contract was read from; an older one is refused.
MINIMUM_VERSION = "1.0.3"

# The reply format the extension reads, in the envelope and in the schema reply.
REPLY_SCHEMA_VERSION = "1"

# Every command this extension runs and every flag it writes itself, by command path. Flags a person writes in
# arguments are checked against model list instead.
REQUIRED_COMMANDS = {
    "auth status": (),
    "auth login": (),
    "auth wait": ("device-code", "timeout"),
    "auth account": (),
    "auth logout": (),
    "model list": ("type",),
    "model": ("type",),
    "voice list": ("model", "offset", "count"),
    "canvas create": ("project-id",),
    "canvas ls": ("limit", "cursor"),
    "resource upload": ("project-id", "file", "type", "resource-id"),
    "resource download": ("project-id", "output"),
    "node create image": (
        "project-id",
        "mode",
        "model",
        "prompt",
        "ref",
        "count",
        "title",
        "run",
        "submit-id",
        "credit-ceiling",
        "resource-id",
        "import-kind",
    ),
    "node create video": (
        "project-id",
        "mode",
        "model",
        "prompt",
        "ref",
        "count",
        "title",
        "run",
        "submit-id",
        "credit-ceiling",
    ),
    "node create audio": (
        "project-id",
        "mode",
        "scenario",
        "model",
        "prompt",
        "ref",
        "title",
        "run",
        "submit-id",
        "credit-ceiling",
    ),
    "node create element": ("project-id", "main", "auxiliary", "voice", "title", "description"),
    "node upscale image": ("project-id", "node-id", "submit-id", "mode", "resolution", "detail", "credit-ceiling"),
    "node show": ("project-id", "node-id"),
    "operation status": ("project-id",),
    "operation wait": ("project-id", "timeout"),
}

# The exit codes the extension reads by number: success, a local refusal, a stop at the quote, sign-in, and an
# operation that did not finish in this call.
EXIT_CODES = {
    "OK": 0,
    "INVALID": 2,
    "CONFIRM": 10,
    "SIGN_IN": 11,
    "INCOMPLETE": 20,
}

# The phase a failure of the CLI's own records reports when Dreamina had already accepted the run.
ACCEPTED_PHASE = "after_submit"

# How long one call may take when no run's deadline bounds it, in seconds. LOCAL bounds version and schema, which read
# only this computer. READ bounds a canvas call and the read-only check of a lost run reply. RUN bounds the run call,
# which saves, quotes, approves, and submits, and returns once Dreamina accepts the run. WAIT bounds one operation wait
# of WAIT_SLICE, with room for the CLI to start and to finish its last read.
CALL_SECONDS = {
    "LOCAL": 10,
    "READ": 60,
    "RUN": 120,
    "WAIT": 45,
}

# A reply is read in chunks. stdout holds a success reply, the largest being the 272,322-byte schema reply; stderr
# holds one failure reply.
REPLY_BYTES = {
    "CHUNK": 65_536,
    "STDOUT": 4_000_000,
    "STDERR": 65_536,
}

# A reply may nest this deep; the schema reply nests 23 levels.
MAX_REPLY_DEPTH = 64

# A CLI reason is cut to this length.
MAX_REASON_CHARACTERS = 300

# A reason that ends otherwise gets a full stop.
REASON_ENDINGS = (".", "!", "?", "…")

# Dreamina's pages messages send the person to, keyed by the placeholder each message uses.
DREAMINA_URLS = {
    "home_page": "dreamina.capcut.com/ai-tool/home",
    "cli_page": "dreamina.capcut.com/canvas-cli",
}

# One short operation wait; the loop calls it again until the run ends or the request timeout passes. A Go duration.
WAIT_SLICE = "15s"

# The canvas every node of this extension lives on.
CANVAS_NAME = "ComfyUI"

# The canvases listed per canvas ls page, the CLI's maximum.
CANVAS_PAGE_SIZE = 100

# The schema's limit for a node or Element title: at most 512 UTF-16 code units.
TITLE_MAX_UNITS = 512

# How long each call of Dreamina Settings and the account read may take, in seconds. LOCAL bounds version, auth
# status, and auth logout, which read or clear state on this computer. NETWORK bounds auth login and auth account,
# which call Dreamina. WAIT_MARGIN is the time auth wait gets beyond its own --timeout, so the CLI ends the wait first.
ACCOUNT_TIMEOUTS = {
    "LOCAL": 10,
    "NETWORK": 15,
    "WAIT_MARGIN": 15,
}

# The failure codes of an auth wait that ends without approval. WAIT_TIMEOUT: its --timeout ran out first, and the same
# device code can be waited on again. EXPIRED: the challenge's expiresAt passed, and a new auth login is needed.
SIGN_IN_FAILURES = {
    "WAIT_TIMEOUT": "cli.login_wait_timeout",
    "EXPIRED": "cli.login_expired",
}

# How long a challenge lasts when auth login returns no expiresAt, in seconds: auth wait's own default, 10m.
SIGN_IN_SECONDS = 600

__all__ = [
    "ACCEPTED_PHASE",
    "ACCOUNT_TIMEOUTS",
    "BINARY_NAMES",
    "CALL_SECONDS",
    "CANVAS_NAME",
    "CANVAS_PAGE_SIZE",
    "DREAMINA_URLS",
    "EXIT_CODES",
    "GLOBAL_ARGUMENTS",
    "INSTALL_FOLDERS",
    "MAX_REASON_CHARACTERS",
    "MAX_REPLY_DEPTH",
    "MINIMUM_VERSION",
    "REASON_ENDINGS",
    "REPLY_BYTES",
    "REPLY_SCHEMA_VERSION",
    "REQUIRED_COMMANDS",
    "SIGN_IN_FAILURES",
    "SIGN_IN_SECONDS",
    "TITLE_MAX_UNITS",
    "WAIT_SLICE",
]
