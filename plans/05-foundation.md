# Foundation

This plan builds the runtime pieces every node needs before its first run:

- the constants and the foundation messages;
- the records, the error type, and JSON parsing;
- private files and the settings;
- the local route guard and the settings route;
- sign-in, sign-out, and the account cache token;
- the CLI installer;
- the status route that **Dreamina Settings** reads;
- the runtime object, route registration, and extension loading.

Every module ports from the fal pack's current code
(`F=/Users/dr_stone/Documents/work/comfyui-fal`, commit `cef8b6e`), not from
`F/plans/05-foundation.md`. The porting rules below apply to every F module
this plan and later plans bring in. The sign-in, install, and status modules
have no F source. They follow the CLI facts in
[research/cli.md](research/cli.md) and
[02-dreamina-contract.md](02-dreamina-contract.md).

Readers: the engineer or agent who builds the Foundation milestone, and the
owner, who approves the sign-in and install checks.

Nothing here runs a paid generation. At the end of this plan:

- ComfyUI loads the extension with no nodes;
- the private state folder is chosen but not created;
- five routes answer: the status, the settings, sign-in, sign-out, and
  install;
- a person can install the CLI, sign in, and sign out through them.

The canvas, the generation records, and the paid nodes arrive in later
milestones. [Step 19](#step-19-runtime) and
[Step 20](#step-20-account-routes-and-the-status-document) say how each joins
without breaking this one.

## Contents

- [Decisions this plan makes](#decisions-this-plan-makes)
- [When each part is built](#when-each-part-is-built)
- [Porting rules](#porting-rules)
- [Step 1: Namespace constants](#step-1-namespace-constants)
- [Step 2: Security constants](#step-2-security-constants)
- [Step 3: Settings constants](#step-3-settings-constants)
- [Step 4: Storage constants](#step-4-storage-constants)
- [Step 5: Patterns](#step-5-patterns)
- [Step 6: Execution constants](#step-6-execution-constants)
- [Step 7: Foundation messages](#step-7-foundation-messages)
- [Step 8: Base records](#step-8-base-records)
- [Step 9: Errors](#step-9-errors)
- [Step 10: JSON parsing](#step-10-json-parsing)
- [Step 11: Settings records](#step-11-settings-records)
- [Step 12: Private files](#step-12-private-files)
- [Step 13: Settings schema and store](#step-13-settings-schema-and-store)
- [Step 14: Local route guard, request body, and settings route](#step-14-local-route-guard-request-body-and-settings-route)
- [Step 15: Installer constants, account limits, and units](#step-15-installer-constants-account-limits-and-units)
- [Step 16: Installer and sign-in messages](#step-16-installer-and-sign-in-messages)
- [Step 17: Sign-in and the account](#step-17-sign-in-and-the-account)
- [Step 18: The installer](#step-18-the-installer)
- [Step 19: Runtime](#step-19-runtime)
- [Step 20: Account routes and the status document](#step-20-account-routes-and-the-status-document)
- [Step 21: Route registration](#step-21-route-registration)
- [Step 22: Extension loading and package docstrings](#step-22-extension-loading-and-package-docstrings)
- [Names this plan uses from other plans](#names-this-plan-uses-from-other-plans)

## Decisions this plan makes

| Question | Decision | Why |
| -------- | -------- | --- |
| Where do credentials live? | Nowhere in the pack. F's `src/storage/credentials.py`, `src/types/credentials.py`, the credential route, its constants, and its messages are not ported. | The CLI keeps the sign-in in the OS credential store ([01-decisions.md](01-decisions.md#sign-in-and-privacy), [research/cli.md](research/cli.md#sign-in)). |
| Which routes exist? | `GET /dreamina/v1/status`, `PATCH /dreamina/v1/settings`, `POST` and `DELETE /dreamina/v1/session`, `POST /dreamina/v1/cli`. Every one passes F's local route guard. Every change needs `X-Dreamina-Comfy: 1` and multi-user mode off. | [04-architecture.md](04-architecture.md#srcconfig) fixes `ROUTES`. F's guard is the owner's rule for every private route. |
| Who owns which route? | `src/settings/routes.py` registers only `PATCH` settings. `src/comfy/account.py` registers the other four and reuses `build_local_route`. | `src.settings` and `src.dreamina` are siblings and may not import each other ([04-architecture.md](04-architecture.md#import-layers)). |
| What does a settings save return? | The whole status document, as F's routes do. `ConfigurationRoutes` takes the status reader as a constructor argument from `register_routes`. | The dialog reads one reply shape for every route. Passing the reader in keeps `src.settings` free of `src.dreamina`. |
| What does the status read? | `version`, then `auth status`, then `auth account` when signed in: three CLI calls at most, each with a short timeout. A failed call never fails the route. It shows as "not found" or "signed out". | The dialog must open even when the CLI is missing or the network is down. `auth status` reads only local state ([02-dreamina-contract.md](02-dreamina-contract.md#sign-in)). |
| How does a sign-in wait? | `SignInState` keeps the challenge in memory and owns one task on the server loop. The task runs `auth wait` until the challenge's `expiresAt`. `cli.login_wait_timeout` means wait again with the same code. `cli.login_expired` marks the sign-in expired. Any other failure marks it failed, with its reviewed message. | The two failure codes are captured ([research/cli.md](research/cli.md#sign-in)). A new code is needed only after `cli.login_expired`. |
| What does the status say about a pending sign-in? | `sign_in` holds `state` (`waiting`, `expired`, or `failed`), `user_code`, `verification_url`, `expires_at`, and `message`. | The dialog shows "The sign-in link expired" only when the server says so. A failed wait shows the CLI's reviewed reason. |
| What is the cache token? | An HMAC-SHA256 of `auth account`'s `userId`, keyed by 16 random bytes made once per process. It is read lazily and forgotten after a sign-in or sign-out. | [01-decisions.md](01-decisions.md#sign-in-and-privacy): a new account runs paid nodes again. The random key keeps the small integer `userId` from being recovered from the token. |
| How does the installer reach the network? | `aiohttp` with `trust_env=False`, no redirects, and a byte cap. The two addresses are built from `INSTALLER_HOST`, so the host check holds by construction. | [04-architecture.md](04-architecture.md#how-the-cli-is-installed). A check of a host that a constant fixes would guard a state that cannot occur (`rules/GENERAL.md`). |
| What does the installer run? | `bash <file>`, or `powershell.exe -NoProfile -ExecutionPolicy Bypass -File <file>` on Windows, with the server's environment, for at most 300 seconds. | ByteDance's installer is the only supported install ([research/cli.md](research/cli.md#release-and-install)). Nothing is bundled. |
| What are the sign-in and install functions called? | `create_sign_in` (`auth login`), `wait_for_sign_in`, `delete_sign_in` (`auth logout`), `read_account`, `download_installer` (fetch the script), and `save_cli` (run it, which saves the CLI to disk). 08's are `send_command` and `validate_cli`. | Every function starts with a verb from `rules/NAMING.md`, which the function check enforces (`python.function-verb`). The table has no `start`, `sign`, `install`, `run`, or `check`. |
| Which helpers in `account.py` are private? | `_create_sign_in` and `_wait_for_sign_in`. Only `SignInState` calls them. | The function check `python.module-only-public` refuses a public function no other module names. |
| How is a pending sign-in stopped? | A new sign-in or a sign-out cancels and awaits the wait task. No shutdown hook is added. | ComfyUI 0.37.2 never runs aiohttp's shutdown signals: `main.py:581-584` stops the loop without `runner.cleanup()`. The `auth wait` child ends by itself at the challenge's expiry, because its `--timeout` is the time left. |
| When is the CLI runner built? | Inside the Foundation milestone, between this plan's Part A and Part B. | Sign-in, install, and the status call `send_command`, which [08-runs.md](08-runs.md) owns. |

## When each part is built

The Foundation milestone of [README.md](README.md#build-order) builds three
parts, in this order, and commits once at the end:

| Part | Steps | Why then |
| ---- | ----- | -------- |
| A | [Step 1](#step-1-namespace-constants) to [Step 14](#step-14-local-route-guard-request-body-and-settings-route) | Constants, records, errors, files, settings, and the settings route call no CLI |
| 08 Part A | [08-runs.md](08-runs.md) Part A: the CLI constants, `src/types/cli.py`, the replies this plan reads, `send_command`, `find_binary`, the failure map, and `validate_cli` | It reads Part A's `ErrorCode`, `DreaminaError`, `Reply`, `parse_json`, and patterns |
| B | [Step 15](#step-15-installer-constants-account-limits-and-units) to [Step 22](#step-22-extension-loading-and-package-docstrings) | Sign-in, install, and the status call the CLI through 08's runner |

The Frontend milestone ([16-frontend.md](16-frontend.md)) and the owner's
sign-in in [22-owner-setup.md](22-owner-setup.md) need working sign-in and
install routes. So 08 Part A cannot wait for the Model check milestone,
which holds [06-model-check.md](06-model-check.md) only.

## Porting rules

When a step says "port", copy the named file from `F` at commit `cef8b6e`
and apply every rule below in addition to the step's own edits.

1. Rename with this table, then reread every docstring, comment, and message
   for the old name.

   | fal                                           | Dreamina                                              |
   | --------------------------------------------- | ----------------------------------------------------- |
   | `FalError`                                    | `DreaminaError`                                       |
   | `src/fal/`, `..fal.` imports                  | `src/dreamina/`, `..dreamina.`                        |
   | `FAL_COMFY_STATE_DIRECTORY`                   | `DREAMINA_COMFY_STATE_DIRECTORY`                      |
   | `FalComfyUI`, `fal-comfy`                     | `DreaminaComfyUI`, `dreamina-comfy`                   |
   | `.fal-`                                       | `.dreamina-`                                          |
   | `/fal/v1/`                                    | `/dreamina/v1/`                                       |
   | `X-Fal-Comfy`                                 | `X-Dreamina-Comfy`                                    |
   | "fal Settings"                                | "Dreamina Settings"                                   |
   | "fal" in any other text                       | "Dreamina", or "the Dreamina extension" where the text means this pack |
   | `FAL_KEY`, "fal API key", and every key text  | Removed with the code that used them                  |

1. Dreamina writes its name with a capital letter, so F's lowercase rule
   (F's porting rule 2) does not apply. A message, docstring, or comment may
   start with "Dreamina".
1. Keep `__all__` as the module's last statement, in Ruff `RUF022` order.
   Type aliases stay out of it, as in F.
1. Keep the import block flat and sorted by statement length, as F does.
1. A function of one or two statements, counting nested statements, is
   inlined into its callers (`max_trivial_statements` is 2). ComfyUI hooks,
   properties, dunders, and protocol stubs are exempt.
1. A public module-level function that no other module names is private
   (`python.module-only-public`, `quality/repository/functions/names.py:64-89`).
1. No `logging`, `print`, or warnings anywhere.
1. Every new name starts with a verb from `rules/NAMING.md` and avoids the
   banned words in `quality/config/naming/terms.json`
   ([01-decisions.md](01-decisions.md#banned-words-that-shape-names)).
   String keys are names too: no `SERVICE`, `DATA`, or `INFO` key.
1. Keep each docstring and "why" comment while it is still true. Rewrite it
   when the behavior differs from F. Comments describe the present code only.
1. Messages are second person and imperative, one or two sentences, and say
   where to act: "in Dreamina Settings" for the dialog. They never hold a
   user ID, a device code, a file path, or a stack trace.

## Step 1: Namespace constants

Create `src/config/namespace.py`, ported from `F/src/config/namespace.py`.
`NODE_PREFIX` and `MENUS` keep their names because `scripts/nodes/check.py`,
`scripts/nodes/schema.py`, and the workflow descriptions import them
([17-scripts-and-workflows.md](17-scripts-and-workflows.md)).

```python
"""The names this extension uses in spaces shared with other packs."""

# Every node identifier is this prefix and the class name.
NODE_PREFIX = "Dreamina"

# The menu headings the nodes are grouped under.
MENUS = {
    "SHARED": "Dreamina",
    "IMAGE": "Dreamina/Image",
    "VIDEO": "Dreamina/Video",
    "AUDIO": "Dreamina/Audio",
}

# The socket types more than one node shares, prefixed so no other pack's socket of the same name connects.
SOCKET_TYPES = {
    "REFERENCES": "DREAMINA_REFERENCES",
}

__all__ = [
    "MENUS",
    "NODE_PREFIX",
    "SOCKET_TYPES",
]
```

F's `TEXT` and `MESH` menus and its `FILES` and `OPTIONS` sockets have no
Dreamina node ([01-decisions.md](01-decisions.md#the-nodes)). What
`DREAMINA_REFERENCES` carries is owned by [07-media.md](07-media.md).

## Step 2: Security constants

Port `F/src/config/security.py` to `src/config/security.py` with the module
docstring "The local routes of Dreamina Settings: their paths, the requests
they accept, and the replies they send." Keep `LOCAL_HOSTS`,
`DEFAULT_PORTS`, `PROXY_HEADERS`, `PROXY_HEADER_PREFIX`,
`CROSS_SITE_FETCHES`, `JSON_MEDIA_TYPE`, `PRIVATE_HEADERS`, and
`JSON_LIMITS` with their values and comments (`F/src/config/security.py:10-41`).
Delete `MAX_CREDENTIAL_CHARACTERS` (`F/src/config/security.py:43-44`).
Change these:

| Constant              | Value | Comment |
| --------------------- | ----- | ------- |
| `ROUTES`              | `{"STATUS": "/dreamina/v1/status", "SETTINGS": "/dreamina/v1/settings", "SESSION": "/dreamina/v1/session", "CLI": "/dreamina/v1/cli"}` | `# The local routes of Dreamina Settings: its status, the request limits, sign-in and sign-out, and the CLI install.` |
| `CHANGE_HEADER`       | `"X-Dreamina-Comfy"` | `# Dreamina Settings sends this header with every change; a plain form or link cannot.` |
| `ACCOUNT_TOKEN_BYTES` | `16` (replaces `GENERATION_TOKEN_BYTES`) | `# The bytes of the random key, made once per process, that turns the account ID into ComfyUI's cache token.` |

The `__all__` list follows the new names. `X-Dreamina-Comfy` holds no banned
word, so it needs no naming exception
([01-decisions.md](01-decisions.md#names-and-identifiers)). The header goes
only to the local ComfyUI server. The frontend sends the same spelling
([16-frontend.md](16-frontend.md#step-4-local-replies-and-requests)).

These four paths are all the routes the pack has. No later plan adds one:
the nodes read the model list themselves
([06-model-check.md](06-model-check.md)), and Generation: Download lists its
records through its own dropdown ([14-node-download.md](14-node-download.md)).

## Step 3: Settings constants

Port `F/src/config/settings.py` to `src/config/settings.py` with these
values:

```python
"""The editable settings with their defaults and ranges, and the size and time a settings request may take."""

# Each setting's default and range, in seconds or in megabytes of 1,000,000 bytes. The largest file any listed model
# takes is a seedance_2.5 reference video of 209,715,200 bytes, so the maximum upload size stops at 210 decimal megabytes.
SETTING_RANGES: dict[str, dict[str, int]] = {
    "request_timeout_seconds": {"default": 1800, "minimum": 10, "maximum": 3600},
    "max_upload_megabytes": {"default": 210, "minimum": 1, "maximum": 210},
    "max_download_megabytes": {"default": 512, "minimum": 16, "maximum": 4096},
}

# The settings route reads a request body of at most max_bytes, in chunks, within timeout_seconds.
SETTINGS_BODY = {
    "MAX_BYTES": 4096,
    "CHUNK_BYTES": 1024,
    "TIMEOUT_SECONDS": 5,
}

__all__ = [
    "SETTINGS_BODY",
    "SETTING_RANGES",
]
```

Why each value:

| Setting                   | Default | Range      | Why |
| ------------------------- | ------- | ---------- | --- |
| `request_timeout_seconds` | 1800    | 10 to 3600 | It bounds one run, from the first upload to the last download ([01-decisions.md](01-decisions.md#paid-runs)). A video run waits in Dreamina's queue and then renders for minutes. Cutting a wait short saves nothing: the generation keeps running and is billed, and its record stays for **Generation: Download**. Past an hour, Generation: Download collects it, so 3600 stays the maximum, as in F, B, and O. |
| `max_upload_megabytes`    | 210     | 1 to 210   | It bounds each encoded file before `resource upload` sends it ([07-media.md](07-media.md)). `model <canonical>` gives each model's file limits ([research/catalog.md](research/catalog.md#file-limits)): images 50 MB, `seedance_2.0` videos 52,428,800 bytes, and `seedance_2.5` videos 209,715,200 bytes, the largest. 210 decimal megabytes (210,000,000 bytes) is the first whole number above it. A larger file is refused before any upload. The limit applies to each file, because each file is its own upload. |
| `max_download_megabytes`  | 512     | 16 to 4096 | It bounds each output file `resource download` writes, which the node then reads into memory ([07-media.md](07-media.md)). A 30-second 4K video fits with room. 16 MB still covers a 4K PNG. 4096 is F's maximum. |

209,715,200 bytes is 200 binary megabytes (200 × 1,048,576), and the setting
counts decimal megabytes. So a `seedance_2.5` video between 200,000,000 and
209,715,200 bytes is refused locally although Dreamina takes it. Contract
checks C-2 to C-4 of [21-test-runs.md](21-test-runs.md) measure the real
upload limits ([02-dreamina-contract.md](02-dreamina-contract.md#uploads)).
If they differ, the maximum changes here and in the changes table.

What each setting controls (the dialog labels belong to
[16-frontend.md](16-frontend.md#step-3-browser-text)):

| Setting                   | Label in the dialog          | Used by |
| ------------------------- | ---------------------------- | ------- |
| `request_timeout_seconds` | Request timeout (seconds)    | One run, from the first upload to the last download ([08](08-runs.md)) |
| `max_upload_megabytes`    | Maximum upload size (MB)     | Each encoded file sent with `resource upload` ([07](07-media.md)) |
| `max_download_megabytes`  | Maximum download size (MB)   | Each output file `resource download` writes ([07](07-media.md)) |

The megabytes are decimal (1,000,000 bytes), as F's are. The CLI calls of
Dreamina Settings have their own short timeouts
([Step 15](#step-15-installer-constants-account-limits-and-units)), so no
setting bounds them.

## Step 4: Storage constants

Port `F/src/config/storage.py` to `src/config/storage.py`.
`ENVIRONMENT_VARIABLES["STATE_DIRECTORY"]` keeps its key because the build
scripts read it.

```python
"""The private state folder, its files and their size limits, and the environment variables that move them."""

# An absolute folder that replaces the platform's own state folder.
ENVIRONMENT_VARIABLES = {
    "STATE_DIRECTORY": "DREAMINA_COMFY_STATE_DIRECTORY",
}

# The state folder's name on macOS and Windows, and under XDG_STATE_HOME elsewhere.
STATE_FOLDER_NAMES = {
    "DEFAULT": "DreaminaComfyUI",
    "XDG": "dreamina-comfy",
}

# Only the folder's owner may open it.
PRIVATE_FOLDER_MODE = 0o700

# A file is written under this prefix, then moved into place; the downloaded installer uses it too.
TEMPORARY_PREFIX = ".dreamina-"

# The settings.
FILE_NAMES = {
    "SETTINGS": "settings.json",
}

# The largest settings file the extension reads.
MAX_FILE_BYTES = {
    "SETTINGS": 65_536,
}

__all__ = [
    "ENVIRONMENT_VARIABLES",
    "FILE_NAMES",
    "MAX_FILE_BYTES",
    "PRIVATE_FOLDER_MODE",
    "STATE_FOLDER_NAMES",
    "TEMPORARY_PREFIX",
]
```

The resulting folders are the ones in
[01-decisions.md](01-decisions.md#names-and-identifiers):

| System  | State folder                                              |
| ------- | --------------------------------------------------------- |
| macOS   | `~/Library/Application Support/DreaminaComfyUI`           |
| Windows | `%LOCALAPPDATA%\DreaminaComfyUI`                          |
| Linux   | `${XDG_STATE_HOME:-~/.local/state}/dreamina-comfy`        |

Later plans add their entries to this module, each with its first reader.
This plan fixes the values, so the plans agree:

| Plan                                       | Adds | Comment |
| ------------------------------------------ | ---- | ------- |
| [08-runs.md](08-runs.md) Part A            | `ENVIRONMENT_VARIABLES["INSTALL_DIRECTORY"] = "DREAMINA_CANVAS_INSTALL_DIR"` | The installer's own variable for the CLI's folder, which `find_binary` checks first |
| [08-runs.md](08-runs.md) Part B            | `FILE_NAMES["CANVAS"] = "canvas.json"`, `MAX_FILE_BYTES["CANVAS"] = 4_096` | The pack's canvas: its ID and link |
| [08-runs.md](08-runs.md) Part B            | `GENERATION_FOLDER = "generations"`, `MAX_FILE_BYTES["GENERATION"] = 16_384` | The generation records, one file per submit ID, in this folder of the state folder |

Each plan updates the comments of `ENVIRONMENT_VARIABLES`, `FILE_NAMES`, and
`MAX_FILE_BYTES`, and `__all__`, when it adds an entry.

## Step 5: Patterns

Create `src/config/patterns.py` with the docstring "Regular expression text
that its owners compile once." Every value is regular expression text that
its owner compiles once at module level. Each constant arrives in the change
that first compiles it. This plan fixes every value, so the plans that add
them agree. At the end of this plan the module holds `REVISION_PATTERN`, and
the two that 08 Part A adds inside this milestone.

| Constant              | Pattern text | Added by | Matches |
| --------------------- | ------------ | -------- | ------- |
| `REVISION_PATTERN`    | `^[a-f0-9]{64}$` | This plan, [Step 14](#step-14-local-route-guard-request-body-and-settings-route) | The settings revision, a SHA-256 digest |
| `VERSION_PATTERN`     | `^(\d+)\.(\d+)\.(\d+)(?:[-+][0-9A-Za-z.-]+)?$` | [08-runs.md](08-runs.md) Part A (`validate_cli`, `is_current_version`) | A CLI release such as `1.0.3`; groups 1 to 3 are compared as numbers with `MINIMUM_VERSION` |
| `REASON_PATTERNS`     | below | [08-runs.md](08-runs.md) Part A (the failure map's reason cleaning) | What is removed from a CLI reason or the installer's output before a person sees it |
| `PLACEHOLDER_PATTERN` | `(?<!\\)\{\{(image\|video\|audio\|reference)([1-9][0-9]*)\}\}` | [07-media.md](07-media.md) | The pack's placeholders, such as `{{image1}}`; a `\{{` the person escaped is left alone ([01-decisions.md](01-decisions.md#placeholders)) |

The backslash before `|` exists only in this table. The Python strings use a
plain `|`. Each constant gets a one-line comment that says what it matches.

Why these shapes:

- **Versions.** `version` returned `1.0.3` (capture `version.json`). The
  optional suffix keeps a pre-release name readable. A version the pattern
  does not match is not current.
- **No ID patterns.** The pack makes submit, canvas, and resource IDs with
  `uuid4`, which prints the CLI's one accepted spelling, a canonical lowercase
  UUID ([research/cli.md](research/cli.md#references-and-placeholders)). Node
  IDs come from the CLI's own replies. No plan checks either against a
  pattern, so none is defined: the owner's rules delete constants nothing
  reads.

`REASON_PATTERNS`, with this comment above it: "A CLI reason or the
installer's output is cleaned before a person sees it. Links, file paths, and
identifier-shaped text are removed. Identifier-shaped text is a UUID, a
canvas node ID, or a run of 32 or more letters, digits, and base64 signs that
holds both a letter and a digit."

```python
REASON_PATTERNS = {
    "URL": r"https?://\S+",
    "PATH": r"(?<![\w.~])(?:~|[A-Za-z]:)?(?:[\\/][\w.@+-]+){2,}[\\/]?",
    "TOKEN": (
        r"\b[0-9A-Fa-f]{8}(?:-[0-9A-Fa-f]{4}){3}-[0-9A-Fa-f]{12}\b"
        r"|\bnode_[A-Za-z0-9_-]+"
        r"|(?<![\w+/=-])(?=[\w+/=]*\d)(?=[\w+/=]*[A-Za-z])[\w+/=]{32,}"
    ),
}
```

F's `FAL_URL` and `LOCKED` patterns and its `DESCRIPTION_PATTERNS` are fal's
and are not ported. 01 removes every link, so no Dreamina link is kept
([01-decisions.md](01-decisions.md#errors)). `PATH` removes absolute paths of
two or more parts, home paths, and Windows drive paths: the installer prints
its install folder, and `rules/GENERAL.md` "Error messages" forbids file
paths in messages. Its look-behind leaves `and/or` and `1/2` alone. URLs are
removed first, so `PATH` never meets a link.

## Step 6: Execution constants

Fix the values of `src/config/execution.py`. Its only reader is
`src/comfy/execution.py` ([08-runs.md](08-runs.md) Part B), so the file
arrives with that reader, as the owner's rule for constants says
([research/owner-rules.md](research/owner-rules.md)):

```python
"""How a paid run shows ComfyUI's progress bar and notices its cancel."""

# A paid node's progress bar: model checked, media uploaded, run accepted, run finished, outputs downloaded, and
# outputs built.
PROGRESS_STEPS = {
    "CHECKED": 1,
    "UPLOADED": 2,
    "ACCEPTED": 3,
    "RUNNING": 4,
    "DOWNLOADED": 5,
    "TOTAL": 6,
}

# How often a wait checks ComfyUI's cancel, in seconds.
CANCELLATION_POLL_SECONDS = 0.1

__all__ = [
    "CANCELLATION_POLL_SECONDS",
    "PROGRESS_STEPS",
]
```

The steps follow [04-architecture.md](04-architecture.md#how-a-paid-run-flows).
`CANCELLATION_POLL_SECONDS` is F's.

## Step 7: Foundation messages

Create these two modules. Each is a flat list of constants in ASCII order,
one message per condition, with `{name}` placeholders filled by `.format` at
the raise site. The sign-in and installer messages arrive in Part B with
their first readers ([Step 16](#step-16-installer-and-sign-in-messages)).

`src/config/messages/settings.py`, with the docstring
`"""Messages for private settings, state storage, and the sign-in routes."""`:

| Constant                   | Text |
| -------------------------- | ---- |
| `PRIVATE_STATE_LOCATION`   | `Keep the Dreamina extension's private state outside ComfyUI, its package, and its media folders.` |
| `RUNTIME_NOT_READY`        | `The Dreamina nodes are still loading. Wait for ComfyUI to finish starting, then run again.` |
| `SETTINGS_CHANGED`         | `The settings changed in another window. Select Reload settings in Dreamina Settings, then save again.` |
| `SETTINGS_RANGE`           | `Choose each Dreamina setting within its range in Dreamina Settings.` |
| `SETTINGS_UNREADABLE`      | `The Dreamina extension's private settings could not be read. Check the state folder's permissions.` |
| `SETTINGS_WHOLE_NUMBERS`   | `Enter whole numbers in Dreamina Settings.` |
| `SETTING_READ_ONLY`        | `Change only the request limits that Dreamina Settings shows.` |
| `SETTING_UNKNOWN`          | `The Dreamina settings file has an unknown setting. Remove it or reset the settings.` |
| `STATE_DIRECTORY_ABSOLUTE` | `Set DREAMINA_COMFY_STATE_DIRECTORY to an absolute folder path.` |
| `STATE_FILE_SIZE`          | `A Dreamina state file is larger than expected. Check the state folder.` |
| `STATE_UNREADABLE`         | `The Dreamina extension's private state could not be read or written. Check the state folder's permissions.` |

F's `KEY_EMPTY`, `KEY_REQUIRED`, `KEY_UNREADABLE`, and `KEY_WHITESPACE`
(`F/src/config/messages/settings.py:3-9`) are not ported.

`src/config/messages/requests.py`, with the docstring
`"""Messages for rejected local HTTP requests."""`, ports F's file. F's
`CLEAR_KEY_BODY` and `SINGLE_KEY_REQUIRED` are not ported. Two texts are new:

| Constant                    | Text |
| --------------------------- | ---- |
| `BODY_NOT_ALLOWED`          | `Send no content with a sign-in, sign-out, or install request.` |
| `LOCAL_CONNECTION_REQUIRED` | `Open Dreamina Settings from a browser on the ComfyUI computer, at a localhost address.` |

The other eight keep F's text: `JSON_DEPTH`, `JSON_DUPLICATE_KEY`,
`JSON_MAPPING`, `JSON_SIZE`, `JSON_SYNTAX`, `JSON_TYPE`, `JSON_VALUES`,
`REQUEST_TIMEOUT`, and `SETTINGS_REVISION_REQUIRED`.

The other message modules of
[04-architecture.md](04-architecture.md#srcconfig) (`inputs`, `models`,
`media`, `cli`, `run`, `generations`) arrive with the plans that own them.
08 Part A creates `messages/cli.py`, and
[Step 16](#step-16-installer-and-sign-in-messages) adds the installer's
messages to it.

## Step 8: Base records

Create `src/types/__init__.py`, ported from `F/src/types/__init__.py`:

```python
"""Records shared by the runtime: dataclasses for in-process values, pydantic models for JSON."""

from typing import Literal
from pydantic import BaseModel, ConfigDict


type Json = bool | int | float | str | list[Json] | dict[str, Json] | None
# What a paid generation node's models make: one node per kind, as model list groups models by type.
type Kind = Literal["image", "video", "audio"]
# What a reference carries: a kind's media, or a Dreamina Element.
type MediaKind = Literal["image", "video", "audio", "element"]


class Value(BaseModel):
    """A frozen record that refuses unknown fields, for files this extension writes."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class Reply(BaseModel):
    """A frozen record that ignores unknown fields, for the JSON the Dreamina CLI prints."""

    # The CLI adds fields over time; a new field must not break a paid run that already succeeded.
    model_config = ConfigDict(extra="ignore", frozen=True)


# Type aliases are imported by name; __all__ lists runtime names.
__all__ = ["Reply", "Value"]
```

`Kind` holds one value per generation node:

| Kind    | Node            |
| ------- | --------------- |
| `image` | Image: Generate |
| `video` | Video: Generate |
| `audio` | Audio: Generate |

[06-model-check.md](06-model-check.md) reads a model's `type` from the live
list and refuses a model of another kind. `MediaKind` is the `media` of a
`Reference` ([07-media.md](07-media.md)).

## Step 9: Errors

Create `src/types/errors.py`, ported from `F/src/types/errors.py`, with the
class renamed `DreaminaError`. F's `RetryLaterError`
(`F/src/types/errors.py:33-44`) is not ported: it carries fal's HTTP
`Retry-After`, and the pack sends no HTTP request to Dreamina. `ErrorCode`
keeps F's thirteen members. [08-runs.md](08-runs.md) maps every CLI failure
to them.

| Member           | Value              | Meaning for Dreamina |
| ---------------- | ------------------ | -------------------- |
| `CONFIGURATION`  | `"configuration"`  | Settings, the state folder, a CLI that is missing, too old, or changed, and an installer that fails |
| `AUTHENTICATION` | `"authentication"` | Signed out (exit 11, `requiredAction` `login`), a sign-in that returns no code, and an account whose plan cannot use the CLI or the model |
| `CREDITS`        | `"credits"`        | A run stopped at its `credit_ceiling` (exit 10), and an account without enough credits |
| `INVALID_INPUT`  | `"invalid_input"`  | Node inputs, the checks before paying, and a CLI refusal of an input (exit 2, class `invalid_input`) |
| `REFUSED`        | `"refused"`        | Dreamina's safety check |
| `UNAVAILABLE`    | `"unavailable"`    | A model not in the person's list, a region Dreamina does not serve, and a generation that failed |
| `RATE_LIMITED`   | `"rate_limited"`   | A sign-in or call Dreamina throttles, such as `cli.passport_rate_limited` |
| `TIMEOUT`        | `"timeout"`        | The request timeout of a run, and the installer's time limit |
| `TRANSPORT`      | `"transport"`      | A CLI that fails to start, an unreadable reply to any call but the run call, network failures, failed uploads or downloads, and an installer that cannot be downloaded |
| `UNCERTAIN`      | `"uncertain"`      | A run call whose reply was lost, which Dreamina may have accepted |
| `INTERRUPTED`    | `"interrupted"`    | ComfyUI's cancel |
| `CONFLICT`       | `"conflict"`       | A stale settings revision |
| `MEDIA`          | `"media"`          | Media that cannot be encoded or decoded, and a file over the upload or download limit |

```python
class DreaminaError(RuntimeError):
    """Show reviewed text; the CLI's cleaned reason, when there is one, is already part of it."""

    def __init__(self, code: ErrorCode, message: str) -> None:
        """Store the complete message and its category."""
        super().__init__(message)
        self.code = code
```

`str(error)` is the complete message. Callers branch on `code`, never on the
text. The module docstring stays "Errors that can be shown without exposing
provider data." It ends with `__all__ = ["DreaminaError", "ErrorCode"]`.

## Step 10: JSON parsing

Port `F/src/types/parsing.py` to `src/types/parsing.py` unchanged apart from
the porting rules. `parse_json(text, *, max_bytes, max_depth)` refuses
oversized, too deeply nested, duplicate-key, and non-finite JSON, and
`validate_fields(value)` requires an object (`F/src/types/parsing.py:41-58`).
Each raises `DreaminaError` with `ErrorCode.INVALID_INPUT` and the `JSON_*`
messages of [Step 7](#step-7-foundation-messages).
[06-model-check.md](06-model-check.md) uses the same functions for each paid
node's `arguments`.

## Step 11: Settings records

Port `F/src/types/settings.py` to `src/types/settings.py` with the module
docstring "Execution settings and the snapshot each run reads." `Settings`
keeps its three integer fields and its `revision` property. Rewrite its
attribute docstrings:

| Attribute                          | Docstring line |
| ---------------------------------- | -------------- |
| `Settings.request_timeout_seconds` | How long one run may take, from the first upload to the last download. |
| `Settings.max_upload_megabytes`    | Largest single file uploaded to Dreamina. |
| `Settings.max_download_megabytes`  | Largest single output file accepted. |

`Configuration` loses `credential` and `generation` and the import of
`Credential`:

```python
@dataclass(frozen=True, slots=True)
class Configuration:
    """One settings and account snapshot for one run.

    Attributes:
        settings: Effective execution limits.
        account: Token identifying the signed-in account in ComfyUI's cache; None until read in this process.
        account_changes: How many sign-ins and sign-outs this process had when the snapshot was read.

    """

    settings: Settings
    account: str | None
    account_changes: int
```

Decisions:

- **A new account token only when the account changes.** The token is the
  part of a paid node's cache key that makes ComfyUI run the node again when
  the same inputs could now give a different result, as with another
  account. Settings only bound a run, and ComfyUI never caches a failed run.
- **The account is read lazily.** No snapshot runs a CLI call.
  [08-runs.md](08-runs.md)'s `PaidNode.fingerprint_inputs` reads the account
  when `account` is `None`, as [Step 13](#step-13-settings-schema-and-store)
  describes.

## Step 12: Private files

Port `F/src/storage/files.py` to `src/storage/files.py` unchanged apart from
the porting rules:

| Function                                 | Does |
| ---------------------------------------- | ---- |
| `choose_state_directory() -> Path`       | `DREAMINA_COMFY_STATE_DIRECTORY` when set (absolute after `expanduser`, else `STATE_DIRECTORY_ABSOLUTE`), else the platform folder; never creates it (`F/src/storage/files.py:12-24`) |
| `save_file(path, content) -> None`       | Creates the parent with mode `0o700`, writes a `.dreamina-` temporary file from `tempfile.mkstemp` (mode `0600`), flushes, `fsync`s, and replaces the target atomically; the temporary file is removed in `finally` |
| `read_file(path, *, max_bytes) -> bytes` | Reads at most `max_bytes + 1` bytes and refuses more with `STATE_FILE_SIZE` |

Keep F's `bearer:disable python_lang_path_traversal` comment and its reason
on `save_file` (`F/src/storage/files.py:37-38`). The same `save_file` writes
the canvas and the generation records ([08-runs.md](08-runs.md)), so they are
atomic and private without code of their own.

F's `src/storage/credentials.py` and `src/types/credentials.py` are not
ported, and no `functions.json` entry is added for `Credential.reveal`.

## Step 13: Settings schema and store

Port `F/src/settings/schema.py` to `src/settings/schema.py` unchanged apart
from the porting rules: `DEFAULT_SETTINGS` built from `SETTING_RANGES`, and
`parse_settings(document)` refusing unknown settings (`SETTING_UNKNOWN`),
values that are not `int` (`SETTINGS_WHOLE_NUMBERS`), and values outside
their range (`SETTINGS_RANGE`), all with `CONFIGURATION`.

Port `F/src/settings/store.py` to `src/settings/store.py` with the module
docstring "Own the private settings and the account cache token outside
ComfyUI's public storage." `ConfigurationStore` keeps F's lock and
`EDITABLE_SETTINGS`. The credential code goes: `_build_snapshot`,
`read_listing_access`, `save_credential`, `delete_credential`, and the
imports of `Credential` and `src/storage/credentials.py`
(`F/src/settings/store.py:35-46`, `F/src/settings/store.py:70-86`,
`F/src/settings/store.py:116-137`). `read_listing_access` served fal's free
listing read without a key; the CLI's model list needs a sign-in instead.

| Member | Does |
| ------ | ---- |
| `__init__(directory)` | Sets `directory`, `lock` (`threading.Lock`), `_account = None`, `_account_changes = 0`, and `_account_key = secrets.token_bytes(ACCOUNT_TOKEN_BYTES)` |
| `read_settings() -> Settings` | F's, unchanged (`F/src/settings/store.py:48-54`) |
| `read_snapshot() -> Configuration` | Under the lock, reads the settings (an `OSError` or `UnicodeError` becomes `SETTINGS_UNREADABLE` with `CONFIGURATION`) and returns `Configuration(settings, self._account, self._account_changes)` |
| `read_status() -> dict[str, Json]` | Under the lock, reads the settings and returns `{"settings", "setting_ranges", "revision"}` as F builds them, without `credential_limit` or `credential` |
| `save_settings(changes, revision) -> None` | F's checks and save (`F/src/settings/store.py:104-114`), returning nothing; the route reads the status afterwards |
| `create_account_token(user_id, account_changes) -> str` | Builds `hmac.new(self._account_key, str(user_id).encode(), hashlib.sha256).hexdigest()`; under the lock, keeps it as `_account` only when `account_changes` still equals `_account_changes`; returns the token either way |
| `reset_account_token() -> None` | Under the lock, sets `_account = None` and adds 1 to `_account_changes` |

The comments that go with them:

- On `_account_changes`: "A sign-in or sign-out counts here, so an account
  read that started before it never keeps the earlier account's token."
- On `create_account_token`: "The random key makes the token useless outside
  this process; the account ID itself is never stored."

How the token is used, so [08-runs.md](08-runs.md) writes
`PaidNode.fingerprint_inputs` (F's at `F/src/nodes/base.py:25-29`) the same
way:

1. Read a snapshot with `asyncio.to_thread(store.read_snapshot)`.
1. When `snapshot.account` is set, return it.
1. Otherwise call `read_account()` ([Step 17](#step-17-sign-in-and-the-account)),
   then return `store.create_account_token(account.user_id,
   snapshot.account_changes)`.

A signed-out read raises the sign-in `DreaminaError`, as F's
`fingerprint_inputs` raises when no key is set. `userId` lives only in that
one call's locals: it is never written to disk, logged, or sent to the
browser ([02-dreamina-contract.md](02-dreamina-contract.md#the-account)).

The module ends with `__all__ = ["ConfigurationStore"]`.

## Step 14: Local route guard, request body, and settings route

Port `F/src/settings/access.py` and `F/src/settings/body.py` to
`src/settings/` unchanged apart from the porting rules:

- `build_local_route(callback, *, is_mutation, is_multi_user)` refuses proxy
  headers, a non-loopback peer, a `Host` that is not exactly a loopback host
  on the server socket's port, a different `Origin`, a cross-site or
  same-site `Sec-Fetch-Site`, and, for changes, a missing `X-Dreamina-Comfy:
  1` header or multi-user mode, all with `403 LOCAL_CONNECTION_REQUIRED`
  (`F/src/settings/access.py:61-82`). A `DreaminaError` becomes `400` with
  its message (`409` for `CONFLICT`), a `web.HTTPException` keeps its status
  and text, and `OSError` or `UnicodeError` becomes `500 STATE_UNREADABLE`.
  Every reply is JSON with `PRIVATE_HEADERS`; errors are `{"error":
  message}` (`F/src/settings/access.py:85-110`). The module docstring
  becomes "Serve the private routes of Dreamina Settings only to the local
  ComfyUI page, with safe errors and private headers."
- `read_body(request)` requires `Content-Type: application/json` (`415`), at
  most 4096 bytes (`413`), read in 1024-byte chunks within 5 seconds (`408`),
  then strict `parse_json` and an object (`F/src/settings/body.py:12-30`).

Port `F/src/settings/routes.py` to `src/settings/routes.py` with the module
docstring "Serve the request limits through a guarded local route." Add
`REVISION_PATTERN` to `src/config/patterns.py`
([Step 5](#step-5-patterns)) in the same change.

`ConfigurationRoutes(store, read_status, *, is_multi_user=False)`:

- `read_status` is `Callable[[], Awaitable[dict[str, Json]]]`: the status
  reader of `AccountRoutes`, passed in by `register_routes`
  ([Step 21](#step-21-route-registration)). The settings package never
  imports `src.dreamina` or `src.comfy`.
- `save_settings(request)` keeps F's body check
  (`F/src/settings/routes.py:31-38`): exactly `{"revision": "<64 hex>",
  "settings": {…}}`, else `SETTINGS_REVISION_REQUIRED`. It then runs
  `store.save_settings` in `asyncio.to_thread` and returns `await
  self.read_status()`.
- `register(routes)` registers one route:

| Method  | Path                      | Body                                                | Handler         | Returns |
| ------- | ------------------------- | --------------------------------------------------- | --------------- | ------- |
| `PATCH` | `/dreamina/v1/settings`   | exactly `{"revision": "<64 hex>", "settings": {…}}` | `save_settings` | The status document ([Step 20](#step-20-account-routes-and-the-status-document)) |

F's `read_status`, `save_credential`, and `delete_credential` handlers and
their routes are not ported (`F/src/settings/routes.py:26-29`,
`F/src/settings/routes.py:40-53`). So F's `functions.json` entry for
`ConfigurationRoutes.read_status` is not added: the policy check refuses an
entry whose function does not exist.

## Step 15: Installer constants, account limits, and units

Part B starts here, after [08-runs.md](08-runs.md) Part A.

Create `src/config/installer.py`:

```python
"""ByteDance's official Dreamina CLI installer: where it is, how it runs, and how long it may take."""

# The one host the installer comes from; the download follows no redirect away from it.
INSTALLER_HOST = "dreamina.capcut.com"

# The installer for each system: a shell script on macOS and Linux, a PowerShell script on Windows.
INSTALLER_URLS = {
    "POSIX": f"https://{INSTALLER_HOST}/canvas-cli/install.sh",
    "WINDOWS": f"https://{INSTALLER_HOST}/canvas-cli/install.ps1",
}

# The program and options that run a downloaded installer; the installer file goes last.
INSTALLER_SHELLS = {
    "POSIX": ("bash",),
    "WINDOWS": ("powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File"),
}

# How long the installer script's download may take, in seconds.
INSTALLER_DOWNLOAD_SECONDS = 30

# How long the installer may run, in seconds.
INSTALL_TIMEOUT_SECONDS = 300

# The largest installer script read, and how much of the installer's output is kept for an error message.
INSTALLER_BYTES = {
    "SCRIPT": 1_000_000,
    "OUTPUT": 65_536,
}

# How many of the installer's last output lines an error message quotes.
INSTALLER_REASON_LINES = 3

__all__ = [
    "INSTALLER_BYTES",
    "INSTALLER_DOWNLOAD_SECONDS",
    "INSTALLER_HOST",
    "INSTALLER_REASON_LINES",
    "INSTALLER_SHELLS",
    "INSTALLER_URLS",
    "INSTALL_TIMEOUT_SECONDS",
]
```

Why these values:

- **The addresses** are the CLI page's
  ([research/cli.md](research/cli.md#release-and-install)). The Windows CMD
  form (`install.bat`) is not used: PowerShell runs `install.ps1` directly.
  The CLI page's one-line commands are not constants: no code reads them.
  The README and ADVANCED write them as plain text for a terminal
  ([18-documentation.md](18-documentation.md)), and Dreamina Settings shows
  none ([16-frontend.md](16-frontend.md)).
- **30 seconds** for the script, because it is one small text file. A
  download that takes longer has stalled.
- **300 seconds** for the run, which downloads the binary of about 25 MB and
  the skill archive, on a slow connection too. The installer takes a lock
  folder and keeps a backup, so a run cut short leaves the earlier CLI
  working ([research/cli.md](research/cli.md#release-and-install)).
- **One megabyte** is far above a shell script's size, so it refuses only a
  reply that is not the installer. The output cap keeps the last 64 KB of
  each stream, which holds the installer's last lines.

Add these to `src/config/dreamina.py`, which 08 Part A creates, below 08's
constants, and add them to its `__all__`:

```python
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
```

The codes are the captures `error-login-wait-timeout.json` and
`error-login-expired.json`. `expiresAt` is optional in the schema
(`auth login` `successData`), so `SIGN_IN_SECONDS` uses the schema's own
default for `--timeout` (`10m`). The status reads at most two local calls and
one network call, so its worst case is 35 seconds. The dialog's request
timeout allows for it ([16-frontend.md](16-frontend.md#step-2-shared-modules)).

Create `src/config/units.py`:

```python
"""Units the size and time limits are written in."""

# A minute, for messages that give a limit in minutes.
SECONDS_PER_MINUTE = 60

__all__ = ["SECONDS_PER_MINUTE"]
```

Its first reader is the installer's timeout message
([Step 18](#step-18-the-installer)). `BYTES_PER_MEGABYTE = 1_000_000`, with
the comment "A megabyte is 1,000,000 bytes, as the settings count them.",
arrives with its first reader by build order: the upload and download limits
of [07-media.md](07-media.md).

## Step 16: Installer and sign-in messages

Add to `src/config/messages/settings.py`, in ASCII order:

| Constant               | Text |
| ---------------------- | ---- |
| `SIGN_IN_CODE_MISSING` | `Dreamina did not return a sign-in code. In Dreamina Settings, select Sign in again.` |

Add to `src/config/messages/cli.py`, which 08 Part A creates, in ASCII order
among 08's constants:

| Constant                  | Text |
| ------------------------- | ---- |
| `INSTALL_DOWNLOAD_FAILED` | `The Dreamina installer could not be downloaded from dreamina.capcut.com. Check the internet connection, or run the install command from the extension's README in a terminal.` |
| `INSTALL_FAILED`          | `The Dreamina installer stopped with an error: {reason} Run the install command from the extension's README in a terminal to see all of its output.` |
| `INSTALL_NO_ANSWER`       | `The Dreamina installer finished, but the Dreamina CLI does not answer. Run dreamina-canvas version in a terminal to see why.` |
| `INSTALL_SHELL_MISSING`   | `The Dreamina installer needs {shell}, which the ComfyUI computer does not have. Install {shell}, then select Install in Dreamina Settings again.` |
| `INSTALL_TIMEOUT`         | `The Dreamina installer did not finish within {minutes} minutes. Run the install command from the extension's README in a terminal.` |

`{reason}` is the installer's cleaned output, ending as a sentence
([Step 18](#step-18-the-installer)). `{shell}` is `bash` or `powershell.exe`.
`{minutes}` is `INSTALL_TIMEOUT_SECONDS // SECONDS_PER_MINUTE`. The messages
of a signed-out run, a CLI that is missing or too old, and every other CLI
failure are 08's ([08-runs.md](08-runs.md)).

## Step 17: Sign-in and the account

Create `src/dreamina/account.py` with the docstring "Sign in, sign out, and
read the account through the Dreamina CLI, keeping the device code on the
server." It never reads the credential store. Every call goes through
`send_command` with the timeouts of
[Step 15](#step-15-installer-constants-account-limits-and-units).

Each function runs its call with `send_command`, then:

1. raises `build_failure(result, context)` when `result.reply.ok` is false.
   The context is the failure map's context for a free call that is not the
   run call, so an unreadable reply is `TRANSPORT`
   ([02-dreamina-contract.md](02-dreamina-contract.md#replies));
1. reads `result.reply.payload` with 08's `parse_reply(payload, record)`,
   which returns the record or raises 08's invalid-reply `DreaminaError`
   (`TRANSPORT`).

No helper wraps these two steps: a wrapper would leave `delete_sign_in` with
one statement, which `python.trivial-function` refuses.

| Function | CLI call | Timeout | Returns |
| -------- | -------- | ------- | ------- |
| `is_signed_in() -> bool` | `auth status` | `LOCAL` | `AuthReply.logged_in is True` |
| `read_account() -> AccountReply` | `auth account` | `NETWORK` | `userId`, `isVip`, and `vipLevel` (captured: `isVip` `true`, `vipLevel` `standard`) |
| `delete_sign_in() -> None` | `auth logout` | `LOCAL` | Nothing; the reply's `loggedOut` is not read |
| `_create_sign_in() -> AuthChallenge \| None` | `auth login` | `NETWORK` | The reply's `challenge`; `None` when there is none and `state.loggedIn` is true, which means the CLI is already signed in; otherwise `DreaminaError(AUTHENTICATION, SIGN_IN_CODE_MISSING)` |
| `_wait_for_sign_in(challenge, expires_at) -> bool` | `auth wait` | below | `True` on approval, `False` when the challenge expired |

`_wait_for_sign_in` repeats while time is left before `expires_at`:

1. Let `remaining` be the seconds until `expires_at`. Stop with `False` when
   it is zero or less.
1. Run `auth wait --device-code <challenge.device_code> --timeout
   <ceil(remaining)>s`, with a `send_command` timeout of `ceil(remaining) +
   ACCOUNT_TIMEOUTS["WAIT_MARGIN"]`. The duration is a Go duration such as
   `540s`, because a bare number fails with `cli.invalid_flag`, exit 2
   (capture `error-invalid-flag.json`).
1. A success reply returns `True`. The owner's approval returned `status`
   `logged_in` and `state.loggedIn` `true`.
1. A failure whose `error.code` is `SIGN_IN_FAILURES["EXPIRED"]`
   (`cli.login_expired`, exit 11) returns `False`.
1. A failure whose `error.code` is `SIGN_IN_FAILURES["WAIT_TIMEOUT"]`
   (`cli.login_wait_timeout`, exit 20, `retryable` `true`) loops with the same
   device code.
1. Any other failure raises `build_failure(result, context)`.

Only structured fields decide, never the message text
([01-decisions.md](01-decisions.md#errors)).

`SignInState` owns the one pending sign-in. It lives on the server loop
only, so an `asyncio.Lock` makes `create_challenge` and `reset` take turns
across their awaits. A `threading.Lock` cannot be held across an await, and no other
thread touches the state.

| Member | Does |
| ------ | ---- |
| `__init__(reset_account)` | `reset_account` is `Callable[[], None]`, the store's `reset_account_token`; the runtime passes it, because `src.dreamina` may not import `src.settings`. Sets `_lock`, `_task = None`, `_challenge = None`, `_expires_at = None`, `_state = None`, and `_message = None`. |
| `async create_challenge() -> None` | Under the lock: cancels and awaits any wait task and forgets its challenge; runs `_create_sign_in`; with a challenge, keeps it, sets `_expires_at`, sets `_state` to `waiting`, and starts `_task = asyncio.create_task(self._wait_for_approval(challenge))` on the running loop |
| `build_status() -> dict[str, Json] \| None` | `None` with no challenge; otherwise the `sign_in` object of the status document ([Step 20](#step-20-account-routes-and-the-status-document)). A `waiting` state past `_expires_at` is reported as `expired`. |
| `async reset() -> None` | Under the lock: cancels and awaits the wait task, then clears the challenge, state, and message |
| `async _wait_for_approval(challenge) -> None` | The task: runs `_wait_for_sign_in`. On `True`, clears the challenge and state and calls `reset_account()`. On `False`, sets `_state` to `expired`. On a `DreaminaError`, sets `_state` to `failed` and `_message` to `str(error)`. A cancel propagates. |

`_expires_at` comes from `datetime.fromisoformat(challenge.expires_at)`, as a
UTC time. When `expiresAt` is absent or unreadable, it is now plus
`SIGN_IN_SECONDS`.

Why this shape:

- **The device code never leaves the server.** `AuthChallenge.device_code` is
  read only by `_wait_for_sign_in`. `build_status` returns the user code, the
  link, and the expiry, never the device code
  ([research/owner-rules.md](research/owner-rules.md#rules-added-for-dreamina)).
- **A new sign-in replaces the old one.** The skill says not to start another
  login "merely because authorization is pending"
  ([research/cli.md](research/cli.md#sign-in)). The pack starts one only when
  the person selects **Sign in**.
- **Every task has an owner.** `create_challenge` and `reset` cancel and
  await the old task, and `SignInState` keeps the only reference to it.
  `send_command` kills the `auth wait` child when the task is canceled
  ([04-architecture.md](04-architecture.md#threads-event-loops-and-subprocesses)).
- **A ComfyUI that stops** ends the loop without a cancel. The child `auth
  wait` then ends by itself when its `--timeout`, the time left on the
  challenge, runs out.

The module ends with `__all__ = ["SignInState", "delete_sign_in",
"is_signed_in", "read_account"]`.

## Step 18: The installer

Create `src/dreamina/installer.py` with the docstring "Install the Dreamina
CLI with ByteDance's official installer, and read which release is
installed." It is the one module that downloads and runs the installer
([04-architecture.md](04-architecture.md#import-layers)). It defines
`INSTALLER_SYSTEM = "WINDOWS" if sys.platform == "win32" else "POSIX"` at
module level, with the comment "The installer key for the server's system."

`read_cli_version() -> str | None`:

1. Return `None` when `find_binary()` finds no binary.
1. Run `version` through `send_command` with `ACCOUNT_TIMEOUTS["LOCAL"]`.
1. Return `VersionReply.version` from a success reply. Return `None` for a
   failed reply, an unreadable reply, or any `DreaminaError` from
   `send_command`, such as a binary that cannot start.

`download_installer() -> Path` fetches the official script to a private
temporary file:

1. **Download.** Inside `asyncio.timeout(INSTALLER_DOWNLOAD_SECONDS)`, open
   `aiohttp.ClientSession(trust_env=False)` and send `GET
   INSTALLER_URLS[INSTALLER_SYSTEM]` with `allow_redirects=False`. Any status
   but `200`, a body over `INSTALLER_BYTES["SCRIPT"]` read in chunks, an
   `aiohttp.ClientError`, or a `TimeoutError` raises
   `INSTALL_DOWNLOAD_FAILED` with `TRANSPORT`. TLS is verified, as aiohttp
   does by default.
1. **Save privately.** In `asyncio.to_thread`, write the bytes to
   `tempfile.mkstemp(prefix=TEMPORARY_PREFIX, suffix=<the address's suffix>)`
   in the system temporary folder (mode `0600`), close the file, and return
   its path. The suffix is `.sh` or `.ps1`, read from the address's path;
   PowerShell's `-File` needs `.ps1`. A failed write deletes the file before
   it raises.

`save_cli(installer_path) -> str` runs the script, which saves the CLI to
disk, and returns the new release:

1. **Find the shell.** `shutil.which` on the first item of
   `INSTALLER_SHELLS[INSTALLER_SYSTEM]`. No match raises `INSTALL_SHELL_MISSING`
   with `CONFIGURATION`. The full path replaces the bare name, so no process
   starts from a partial path.
1. **Run.** Inside `asyncio.timeout(INSTALL_TIMEOUT_SECONDS)`, start
   `asyncio.create_subprocess_exec(<shell path>, *<the shell's options>,
   <installer_path>)` with stdin from `DEVNULL`, stdout and stderr piped, and
   the server's environment unchanged. An `OSError` at start raises
   `INSTALL_SHELL_MISSING`. Both streams are read at once, in chunks, keeping
   the last `INSTALLER_BYTES["OUTPUT"]` bytes of each, and the process is
   awaited. On a cancel or the timeout, the process is killed and awaited, so
   no child outlives the route. A `TimeoutError` raises `INSTALL_TIMEOUT`
   with `TIMEOUT`.
1. **Check the exit.** A non-zero exit raises `INSTALL_FAILED` with
   `CONFIGURATION`. `{reason}` is the last `INSTALLER_REASON_LINES` non-empty
   lines of stderr, or of stdout when stderr is empty, decoded as UTF-8 with
   replacement, joined with spaces, and passed through 08's `sanitize_reason`.
   That removes links, paths, and identifiers, collapses whitespace, cuts the
   text to `MAX_REASON_CHARACTERS` (300), and ends it as a sentence.
1. **Clean up.** `installer_path` is deleted in `finally`, in
   `asyncio.to_thread`, whatever the outcome.
1. **Read the new release.** Call 08's `reset_cli_validation()`, so the next
   run validates the new binary with `validate_cli`, then
   `read_cli_version()`. `None` raises `INSTALL_NO_ANSWER` with
   `CONFIGURATION`. Otherwise return the version.

The route calls the two in turn
([Step 20](#step-20-account-routes-and-the-status-document)). The install's
worst case is 30 seconds of download, 300 of installer, and 10 for the
version.

Notes:

- **What runs is ByteDance's.** The pack bundles no installer and no binary
  ([research/owner-rules.md](research/owner-rules.md#rules-added-for-dreamina)).
  The installer honors `DREAMINA_CANVAS_INSTALL_DIR`, keeps the folder of a
  `dreamina-canvas` already on `PATH`, and on Windows installs only on
  `AMD64` ([research/cli.md](research/cli.md#release-and-install)). Its own
  refusal reaches the person through `INSTALL_FAILED`.
- **Two installs at once** meet the installer's own lock folder,
  `.dreamina-canvas.install.lock`. The second one fails with the installer's
  message. The pack adds no lock of its own.
- **A closed dialog does not stop an install.** aiohttp 3.14.3 in ComfyUI
  0.37.2 does not cancel a handler when the browser disconnects:
  `handler_cancellation` defaults to `False` (`aiohttp/web_server.py:21`),
  and ComfyUI's `web.AppRunner(self.app, access_log=None)` keeps it
  (`server.py:1411`).
- **No command from a reply runs.** An upgrade reply's
  `clientUpgrade.installCommands` is never run. **Update** runs this same
  fixed installer ([02-dreamina-contract.md](02-dreamina-contract.md#install-upgrade-and-the-version-gate)).

The module ends with `__all__ = ["INSTALLER_SYSTEM", "download_installer",
"read_cli_version", "save_cli"]`.

## Step 19: Runtime

Port `F/src/comfy/runtime.py` to `src/comfy/runtime.py`. At this milestone
`Runtime` holds the settings store and the sign-in state:

```python
class Runtime:
    """State shared by this extension's nodes and routes across event loops.

    Attributes:
        configuration: Private settings and the account cache token.
        sign_in: The pending Dreamina sign-in, kept in memory.

    """

    __slots__ = ("configuration", "sign_in")

    configuration: ConfigurationStore
    sign_in: SignInState

    def __init__(self) -> None:
        """Create the shared stores and place their state under one private directory."""
        self.configuration = ConfigurationStore(choose_state_directory())
        self.sign_in = SignInState(self.configuration.reset_account_token)
```

`create_runtime()` and `get_runtime()` are F's
(`F/src/comfy/runtime.py:35-49`): one module-level `_runtime`, created once
off the event loop, with F's `# noqa: PLW0603 -- reason: ComfyUI initializes
one shared runtime during loading.`, and `get_runtime()` raising
`RUNTIME_NOT_READY` with `CONFIGURATION` before loading. `scripts/` imports
`create_runtime`, so the name stays. Its docstring ("Initialize once through
the host's extension lifecycle, without network calls.") stays true at every
milestone: `SignInState` starts no task until a sign-in, and every store reads
only files. Creating `SignInState`'s `asyncio.Lock` in a worker thread is
safe on Python 3.12, which binds a lock to a loop at its first use.

The other two stores of [04-architecture.md](04-architecture.md#srccomfy)
join `Runtime` in [08-runs.md](08-runs.md) Part B, which builds them. Read
models are not a runtime store: [06-model-check.md](06-model-check.md) keeps
them in `src/dreamina/models.py`'s module-level cache, as F does. 08 adds, in
one change, the slot (in `__slots__` order), the class annotation, the
`Attributes:` docstring line, the line in `__init__`, and the imports:

| Plan                              | Attribute     | Line in `__init__` | Docstring line |
| --------------------------------- | ------------- | ------------------ | -------------- |
| [08-runs.md](08-runs.md) Part B   | `canvas`      | `self.canvas = CanvasStore(self.configuration.directory / FILE_NAMES["CANVAS"])` | `canvas: The pack's saved Dreamina canvas.` |
| [08-runs.md](08-runs.md) Part B   | `generations` | `self.generations = GenerationStore(self.configuration.directory / GENERATION_FOLDER)` | `generations: Recorded generations, one per submit ID.` |

Neither store creates a file or folder until it saves. Between milestones the
runtime only has the stores built so far, and nothing reads a store before
its plan.

## Step 20: Account routes and the status document

Create `src/comfy/account.py` with the docstring "Serve the status,
sign-in, sign-out, and install routes of Dreamina Settings." It imports
`build_local_route` from `src/settings/access.py`, which the import layers
allow ([04-architecture.md](04-architecture.md#import-layers)).

`AccountRoutes(configuration, sign_in, *, is_multi_user=False)`:

| Handler | Method and path | Body | Does | Returns |
| ------- | --------------- | ---- | ---- | ------- |
| `read_status(_request=None)` | `GET /dreamina/v1/status` | none | Builds the status document below | The status document |
| `create_session(request)` | `POST /dreamina/v1/session` | none, else `400 BODY_NOT_ALLOWED` | `await sign_in.create_challenge()` | The status document |
| `delete_session(request)` | `DELETE /dreamina/v1/session` | none, else `400 BODY_NOT_ALLOWED` | `await sign_in.reset()`, `await delete_sign_in()`, then `configuration.reset_account_token()` | The status document |
| `save_release(request)` | `POST /dreamina/v1/cli` | none, else `400 BODY_NOT_ALLOWED` | `await save_cli(await download_installer())` | The status document |

- A body is refused when `request.can_read_body` is true, as F refused one
  when clearing the key.
- `read_status` takes an optional request, so `ConfigurationRoutes` can call
  it with none.
- `register(routes)` wraps each handler in `build_local_route` with
  `is_multi_user`: `read_status` with `is_mutation=False`, the other three
  with `is_mutation=True`, as F's `register` does
  (`F/src/settings/routes.py:55-61`).

The status document:

```json
{
  "settings": {
    "request_timeout_seconds": 1800,
    "max_upload_megabytes": 210,
    "max_download_megabytes": 512
  },
  "setting_ranges": {
    "request_timeout_seconds": { "minimum": 10, "maximum": 3600 },
    "max_upload_megabytes": { "minimum": 1, "maximum": 210 },
    "max_download_megabytes": { "minimum": 16, "maximum": 4096 }
  },
  "revision": "<sha256 of the settings>",
  "cli": {
    "found": true,
    "version": "1.0.3",
    "minimum_version": "1.0.3",
    "is_current": true
  },
  "account": { "signed_in": true, "is_vip": true, "vip_level": "standard" },
  "sign_in": null,
  "mutation_allowed": true
}
```

A pending sign-in fills `sign_in`:

```json
{
  "state": "waiting",
  "user_code": "XXXX-XXXX",
  "verification_url": "https://dreamina.capcut.com/ai-tool/cli-auth-os?cli_name=canvas_cli&user_code=XXXX-XXXX",
  "expires_at": "2026-10-16T21:53:28+00:00",
  "message": null
}
```

How each key is filled:

| Key | Source | When a call fails |
| --- | ------ | ----------------- |
| `settings`, `setting_ranges`, `revision` | `configuration.read_status()` in `asyncio.to_thread` | F's route errors |
| `cli.found`, `cli.version` | `read_cli_version()`: one `version` call, `LOCAL` timeout | `found` is `false` and `version` is `null`, for a missing binary and for one that does not answer |
| `cli.minimum_version` | `MINIMUM_VERSION` | Never fails |
| `cli.is_current` | `is_current_version(version)`, `false` when not found | Never fails |
| `account.signed_in` | Not found: `false`, with no call. Otherwise `is_signed_in()`: one `auth status` call, `LOCAL` timeout | A failed `auth status` shows `false` |
| `account.is_vip`, `account.vip_level` | Signed in: `read_account()`, one `auth account` call, `NETWORK` timeout; `null` when a field is absent | An `AUTHENTICATION` error, such as expired credentials, sets `signed_in` to `false`. Any other error keeps `signed_in` `true` with both fields `null`. |
| `sign_in` | `sign_in.build_status()` | Never fails |
| `mutation_allowed` | `not is_multi_user` | Never fails |

The `sign_in` values:

- `state` is `waiting`, `expired`, or `failed`.
- `user_code` is the challenge's `userCode`.
- `verification_url` is `verificationUriComplete`, which carries the code,
  or `verificationUri` when it is absent.
- `expires_at` is `_expires_at` in UTC, written with
  `isoformat(timespec="seconds")`.
- `message` is the reviewed failure text when `state` is `failed`, else
  `null`.

What the document never holds: `userId`, the device code, the CLI's profile,
region, credential storage, sign-in expiry, an install command, or the
canvas. The dialog shows neither a command nor a canvas link
([16-frontend.md](16-frontend.md)), so the status reads no `canvas.json`.
The user code is shown to the person who signs in, by design of the device
sign-in.

The account section is filled by one private method,
`_read_account_status(is_found) -> dict[str, Json]`, so `read_status` stays
short. No later plan adds a key or a parameter to `AccountRoutes`.
[16-frontend.md](16-frontend.md#step-4-local-replies-and-requests) parses the
document.

The module ends with `__all__ = ["AccountRoutes"]`.

## Step 21: Route registration

Port `F/src/comfy/routes.py` to `src/comfy/routes.py` with the module
docstring "Register the extension's local routes with ComfyUI."
`register_routes()` keeps F's check (`F/src/comfy/routes.py:16-29`): it
resolves the state folder and refuses it with `PRIVATE_STATE_LOCATION` when
it lies inside `folder_paths.base_path`, the input, output, temp, or user
folder, or the extension (`EXTENSION_ROOT = Path(__file__).resolve().parents[2]`).
Then it registers both route sets on `PromptServer.instance.routes`:

```python
runtime = get_runtime()
account = AccountRoutes(runtime.configuration, runtime.sign_in, is_multi_user=args.multi_user)
account.register(PromptServer.instance.routes)
ConfigurationRoutes(runtime.configuration, account.read_status, is_multi_user=args.multi_user).register(
    PromptServer.instance.routes
)
```

The refusal runs before any route exists, so no setting is written into a
folder ComfyUI serves. Its docstring becomes "Reject public state locations
before enabling changes, then register every local route." No later plan
adds a route or a browser event to this module.

## Step 22: Extension loading and package docstrings

Port `F/__init__.py` to the repository root unchanged except the module
docstring: "Load the Dreamina nodes and their local routes through ComfyUI's
extension entry point." It keeps `WEB_DIRECTORY = "./web"`, the `Extension`
class whose `on_load` imports `create_runtime` and `register_routes` lazily,
runs `create_runtime` in `asyncio.to_thread`, and calls `register_routes()`;
whose `get_node_list` returns `list(NODE_TYPES)`; and `async def
comfy_entrypoint() -> Extension` (`F/__init__.py:8-31`). There is no
`NODE_CLASS_MAPPINGS`. The allowlist entry for `comfy_entrypoint`,
`Extension.on_load`, and `Extension.get_node_list`, and the naming exception
that lets `on_load` hold the banned word `load`, come with
[03-repository-setup.md](03-repository-setup.md)'s copy of `functions.json`
and `policy.json`.

Create `src/nodes/__init__.py`, so loading works before any node exists:

```python
"""Register the extension's nodes in menu order."""

from comfy_api.latest import io


NODE_TYPES: tuple[type[io.ComfyNode], ...] = ()

__all__ = ["NODE_TYPES"]
```

[04-architecture.md](04-architecture.md#srcnodes) fixes the order, and each
node plan adds its class.

Create or overwrite each runtime package's `__init__.py` with exactly this
docstring and nothing else. [03-repository-setup.md](03-repository-setup.md)
creates these packages as stubs at Tooling, because import-linter needs every
package its contracts name to exist. This step gives them their final text.

| File                              | Docstring |
| --------------------------------- | --------- |
| `src/__init__.py`                 | `Node logic for Dreamina, independent of the ComfyUI loader.` |
| `src/comfy/__init__.py`           | `Connect Dreamina runs and the local routes to the ComfyUI host.` |
| `src/dreamina/__init__.py`        | `Calls to the Dreamina CLI and its installer: sign-in, the model check, uploads, runs, and downloads.` |
| `src/settings/__init__.py`        | `The private settings, their local route, and the snapshot each run reads.` |
| `src/storage/__init__.py`         | `Private files outside ComfyUI: the settings, the canvas, and the generation records.` |
| `src/config/__init__.py`          | `Fixed settings shared by the runtime and the build tools.` |
| `src/config/messages/__init__.py` | `The text the nodes, routes, and dialogs show.` |

The one subpackage of `src/dreamina/`, `generations/`, is created by
[08-runs.md](08-runs.md) Part B with its first module.

State of the quality configuration at the end of this plan:

| File | State |
| ---- | ----- |
| `quality/config/repository/functions.json` | `allowlist` holds the `__init__.py` entry from Tooling and any entry 08 Part A adds; this plan adds none. Every handler and store method here has more than two statements, and every public function is named by another module. `verbs` is unchanged: every name here starts with a verb already in it. |
| `quality/config/naming/policy.json` | 03's rules only. No Dreamina naming exception is needed yet. Model: Info's `info` exception arrives with [15-node-model-info.md](15-node-model-info.md). |

At the end of this plan, ComfyUI loads the extension with no nodes, the
private state folder is chosen but not created, and the five routes answer.
The build order commits here with
`feat(nodes): add the settings, sign-in routes and extension loading`
([README.md](README.md#build-order)).

## Names this plan uses from other plans

| Name | Owner | Used for |
| ---- | ----- | -------- |
| `send_command(arguments, timeout_seconds)`, `CliResult` (`reply`), `CliReply` (`ok`, `payload`, `error`), `CliFailure` (`code`) | [08-runs.md](08-runs.md) Part A | Every CLI call of sign-in, sign-out, the account, and the status |
| `find_binary() -> Path \| None` | [08-runs.md](08-runs.md) Part A | "Not found" in the status, before any call |
| `build_failure(result, context)` with the context of a free call | [08-runs.md](08-runs.md) Part A | Failed auth calls |
| `sanitize_reason(text)`, `MAX_REASON_CHARACTERS` | [08-runs.md](08-runs.md) Part A | The installer's error output; 08 makes F's private `_sanitize_reason` (`F/src/fal/failures.py:98-111`) public for this second caller |
| `validate_cli`, `reset_cli_validation()`, `is_current_version(version)`, `MINIMUM_VERSION` | [08-runs.md](08-runs.md) Part A | Forgetting the cached validation after `save_cli`, and `is_current` in the status |
| `VersionReply` (`version`), `AuthReply` (`logged_in` from `auth status`, `status`, `state.logged_in`, `challenge`), `AuthChallenge` (`device_code`, `user_code`, `verification_uri`, `verification_uri_complete`, `poll_seconds`, `expires_at`), `AccountReply` (`user_id`, `is_vip`, `vip_level`) | [08-runs.md](08-runs.md) Part A, `src/types/replies.py` | Reading the auth and version replies; `device_code` with `repr=False` |
| `parse_reply(payload, record)` | [08-runs.md](08-runs.md) Part A | Reading a success payload into a reply record, with 08's invalid-reply `DreaminaError` |
| `src/config/messages/cli.py`, `src/config/dreamina.py` | [08-runs.md](08-runs.md) Part A | The modules Steps 15 and 16 add to |
| `CanvasStore`, `GenerationStore` | [08-runs.md](08-runs.md) Part B | Join `Runtime` later |
| `PaidNode.fingerprint_inputs` | [08-runs.md](08-runs.md) Part B | Reads the account token as Step 13 says |
| The status document's reader | [16-frontend.md](16-frontend.md) | The dialog |
| Contract checks C-2 to C-4 | [21-test-runs.md](21-test-runs.md) | The real upload limits |
| The owner's sign-in | [22-owner-setup.md](22-owner-setup.md) | The first live sign-in through these routes |
| File limits per model | [research/catalog.md](research/catalog.md#file-limits) | `max_upload_megabytes` |
