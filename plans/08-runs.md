# Runs and Node Base

This plan builds the machinery every node that talks to Dreamina shares:

- the CLI's names, limits, and the commands the pack uses;
- the failure messages and the map from the CLI's failure fields to them;
- the records of the CLI's envelope and of every success reply;
- `send_command`, the one function that starts the CLI, and the version gate;
- the canvas every node writes to;
- the generation records, the run call, the wait, and the collection of a
  finished generation;
- the run wrapper that connects a run to ComfyUI's progress bar and cancel;
- the paid node base, the shared output builder, and `GenerateNode`, the base
  of the three generation nodes.

Node plans 09 to 15 use all of it.

Most modules port from the fal pack's current code
(`F=/Users/dr_stone/Documents/work/comfyui-fal`, commit `cef8b6e`), following
the porting rules of [05-foundation.md](05-foundation.md#porting-rules). The
runner, the failure map, the version gate, the canvas, and the wait are new,
because the pack calls a local CLI instead of an HTTP API. ComfyUI's own code
is cited as `C=/Users/dr_stone/ComfyUI-Installs/ComfyUI/ComfyUI` (commit
`830232b8`, ComfyUI 0.37.2). CLI facts cite the schema, the skill, and the
captures as [research/cli.md](research/cli.md) does.

Readers: the engineer or agent who builds the CLI runner, the paid path, and
the paid node base, and the writers of the other plans, who reuse their
names. Nothing here has been implemented. Written on 2026-10-16.

## Contents

- [Decisions this plan makes](#decisions-this-plan-makes)
- [When each part is built](#when-each-part-is-built)
- [Step 1: CLI constants](#step-1-cli-constants)
- [Step 2: CLI and run messages](#step-2-cli-and-run-messages)
- [Step 3: CLI records and the first reply records](#step-3-cli-records-and-the-first-reply-records)
- [Step 4: Failures](#step-4-failures)
- [Step 5: The CLI runner](#step-5-the-cli-runner)
- [Step 6: The version gate](#step-6-the-version-gate)
- [Step 7: Run constants, messages, and storage names](#step-7-run-constants-messages-and-storage-names)
- [Step 8: Run reply records](#step-8-run-reply-records)
- [Step 9: Generation records](#step-9-generation-records)
- [Step 10: The canvas](#step-10-the-canvas)
- [Step 11: Operation protocol](#step-11-operation-protocol)
- [Step 12: Generation store, the runtime, and the status](#step-12-generation-store-the-runtime-and-the-status)
- [Step 13: The wait, a lost reply, and a failed generation](#step-13-the-wait-a-lost-reply-and-a-failed-generation)
- [Step 14: Generation operation](#step-14-generation-operation)
- [Step 15: Run wrapper](#step-15-run-wrapper)
- [Step 16: Node base](#step-16-node-base)
- [Step 17: Node outputs](#step-17-node-outputs)
- [Step 18: Generate node](#step-18-generate-node)
- [Step 19: Allowlist and commits](#step-19-allowlist-and-commits)
- [Rules every node plan follows](#rules-every-node-plan-follows)
- [What the live runs settle](#what-the-live-runs-settle)
- [Names this plan uses from other plans](#names-this-plan-uses-from-other-plans)

## Decisions this plan makes

| Question | Decision | Why |
| -------- | -------- | --- |
| How does a CLI call run? | `send_command` starts the binary with `asyncio.create_subprocess_exec`, stdin from `DEVNULL`, both streams read at once with byte caps, the server's environment unchanged, and a timeout. It returns the exit code and the one JSON object, from stdout on exit 0 and from stderr otherwise. | [01-decisions.md](01-decisions.md#subprocesses-and-concurrency). No shell, so a prompt with quotes or `$` needs no escaping. |
| What bounds each call? | Calls inside a run take what is left of the run's request timeout (`deadline - time.monotonic()`), as 07's uploads and downloads do, and a wait call stops at `CALL_SECONDS["WAIT"]` too. The version gate, the canvas calls, the run call, and the check of a lost run reply have their own bound in `CALL_SECONDS`. | The request timeout bounds a run "from the first upload to the last download" ([01-decisions.md](01-decisions.md#paid-runs)). The run call is never cut short by a deadline that is nearly over ([Step 14](#step-14-generation-operation)). |
| Which failures of the run call mean Dreamina accepted the run? | Exit 0, exit 20, and a failure whose `error.localStorage.submissionPhase` is `after_submit`. Every other structured failure is a refusal. | "After an accepted media submission, exhausted transient errors, timeout, or interruption return `ok=false`, exit `20`" (`skill: references/recovery-and-idempotency.md`), and `after_submit` "requires read-only `operation status/wait`" (`skill: references/authentication.md#local-business-state-storage`). |
| What happens to a run call whose reply is lost? | One read-only `operation status <submitId> --project-id <canvas>`. If Dreamina knows the run, the node says it was accepted but cannot be collected. Otherwise it says the run may still start. Nothing is recorded, and the run call is never sent again. | "submit response was lost: inspect read-only with the same submit ID; **do not replay the run**" (`skill: references/recovery-and-idempotency.md`). `operation status` returns no node ID, and `node show` needs one. The owner rejected records of uncertain runs (O `6340e4a`). |
| How is a deleted canvas found? | `find_canvas` lists the account's canvases with `canvas ls` on every run. A saved canvas Dreamina no longer lists is cleared, and `create_canvas` makes a new one. | A missing, forbidden, or unlinked ID return "the **same** error" (`skill: references/identity-and-references.md#resolution-rules`), so a failed save cannot tell a deleted canvas from a deleted reference. `canvas ls` is free and lists canvases by ID. |
| What does `build_failure`'s `context` mean? | The message a failure gets when no row of the map names it: an invalid input (row 8) or an unknown failure (row 9). Free calls pass `CLI_FAILED`, the run calls `RUN_REFUSED`, and 07 `UPLOAD_REFUSED` or `DOWNLOAD_FAILED`. | Each caller knows what its failure means for the person; the map keeps every fixed-fix message (sign-in, upgrade, network, the ceiling) the same everywhere. |
| How does a cancel after acceptance show? | As a `DreaminaError` with `INTERRUPTED` and a message that the generation keeps running, is billed, and stays recorded. A cancel before acceptance shows as ComfyUI's `InterruptProcessingException`. | ComfyUI shows no text for an interrupt (`C/execution.py:618-626`, `:692-699`). [01-decisions.md](01-decisions.md#paid-runs) requires that message. |
| What does a failure of the wait say? | A failure of the wait or of `node show` that leaves the record is raised as `GENERATION_UNCOLLECTED`, which quotes it and sends the person to **Generation: Download**. 07's download messages say the same in their own words. | Telling the person to run the node again would bill a second generation. |
| How does `REQUIRED_COMMANDS` grow? | It lists every command and flag the finished pack sends, from Part A on. No later plan adds an entry. | The version gate checks the installed CLI as a whole, so an incompatible CLI is refused at the first free call, not halfway through the node milestones. |
| How do the paid nodes take media lists? | `is_input_list=True`; each media socket arrives whole, and every other input is read as its one value by B's `_read_single`, which also takes a plain value. | The owner's rule for O: everything connected goes into one run. [23-live-shopping-provider.md](23-live-shopping-provider.md) calls the nodes from Python with plain values. |
| Which names do the functions take? | Every public function starts with a verb of `rules/NAMING.md`: `send_command`, `parse_reply`, `validate_cli`, `find_canvas`, `create_canvas`, `wait_for_operation`, `validate_lost_run`, `wait_until_settled`. | The function check refuses any other verb (`python.function-verb`), and `ensure` is a banned term. |

## When each part is built

| Part | Steps | Milestone | Why then |
| ---- | ----- | --------- | -------- |
| A | 1 to 6 | **Foundation**, between [05-foundation.md](05-foundation.md#when-each-part-is-built)'s Part A (its Steps 1 to 14) and its Part B (Steps 15 to 22), committed with 05 | 05's sign-in, install, and status routes call `send_command`, `parse_reply`, `build_failure`, and `is_current_version`. Part A reads only 05 Part A's `ErrorCode`, `DreaminaError`, `Reply`, `Json`, `parse_json`, and `src/config/patterns.py`. Everything in it is free. |
| B | 7 to 19 | **Media and runs**, after the contract runs of [21-test-runs.md](21-test-runs.md#part-1-contract-checks) | The operation reads the model, chooses the mode, and builds the flags (06), encodes, uploads, and downloads (07), and its state words come from runs C-7, C-8, and C-14 |

Within the Media and runs milestone, Part B and [07-media.md](07-media.md)
interleave, because each reads the other's records:

1. 07 Steps 1 to 5: the media constants, messages, placeholder pattern, and
   `Reference` and `LocalMedia`.
1. This plan's Steps 7 to 9: the run constants, the reply records 07's
   uploads and downloads read (`UploadReply`, `DownloadReply`, `NodeView`),
   and `src/types/generations.py`, whose `OutputFile` 07's downloads build.
1. 07 Steps 6 to 10: conversions, uploads, references and placeholders,
   downloads, and 07's allowlist entries.
1. This plan's Steps 10 to 19.

## Step 1: CLI constants

Create `src/config/dreamina.py`, with the docstring "The Dreamina Canvas
CLI: its file names and install folders, the arguments every call carries,
the commands this extension uses, its exit codes, the reply limits, and the
pages messages name." The values are
[02-dreamina-contract.md](02-dreamina-contract.md#how-the-pack-calls-the-cli)'s.

```python
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

# The release the pack's contract was read from; an older one is refused.
MINIMUM_VERSION = "1.0.3"

# The reply format the pack reads, in the envelope and in the schema reply.
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
        "project-id", "mode", "model", "prompt", "ref", "count", "title", "run", "submit-id", "credit-ceiling",
        "resource-id", "import-kind",
    ),
    "node create video": (
        "project-id", "mode", "model", "prompt", "ref", "count", "title", "run", "submit-id", "credit-ceiling",
    ),
    "node create audio": (
        "project-id", "mode", "scenario", "model", "prompt", "ref", "title", "run", "submit-id", "credit-ceiling",
    ),
    "node create element": ("project-id", "main", "auxiliary", "voice", "title", "description"),
    "node upscale image": ("project-id", "node-id", "submit-id", "mode", "resolution", "detail", "credit-ceiling"),
    "node show": ("project-id", "node-id"),
    "operation status": ("project-id",),
    "operation wait": ("project-id", "timeout"),
}

# The exit codes the pack reads by number: success, a local refusal, a stop at the quote, sign-in, and an operation
# that did not finish in this call.
EXIT_CODES = {
    "OK": 0,
    "INVALID": 2,
    "CONFIRM": 10,
    "SIGN_IN": 11,
    "INCOMPLETE": 20,
}

# How long one call may take when no run's deadline bounds it, in seconds. LOCAL bounds version and schema, which read
# only this computer.
CALL_SECONDS = {
    "LOCAL": 10,
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
```

The module ends with `__all__` listing the names in ASCII order.
[05-foundation.md](05-foundation.md#step-15-installer-constants-account-limits-and-units)
adds `ACCOUNT_TIMEOUTS`, `SIGN_IN_FAILURES`, and `SIGN_IN_SECONDS` below
them in its Part B, [Step 7](#step-7-run-constants-messages-and-storage-names)
adds the run's constants, and [13-node-element.md](13-node-element.md) adds
`TITLE_MAX_UNITS`.

Every command and flag of `REQUIRED_COMMANDS` is in the schema (schema:
`subcommands`, each command's `flags[].name`), with these users:

| Command path          | Flags                                                        | Used by |
| --------------------- | ------------------------------------------------------------ | ------- |
| `auth status`, `auth login`, `auth account`, `auth logout` | none                    | [05-foundation.md](05-foundation.md#step-17-sign-in-and-the-account) |
| `auth wait`           | `device-code`, `timeout`                                     | 05 |
| `model list`          | `type`                                                       | [06-model-check.md](06-model-check.md) |
| `model`               | `type` (and the positional canonical name)                   | [15-node-model-info.md](15-node-model-info.md) |
| `voice list`          | `model`, `offset`, `count`                                   | [15-node-model-info.md](15-node-model-info.md) |
| `canvas create`       | `project-id` (and the positional name)                       | [Step 10](#step-10-the-canvas) |
| `canvas ls`           | `limit`, `cursor`                                            | Step 10 |
| `resource upload`     | `project-id`, `file`, `type`, `resource-id`                  | [07-media.md](07-media.md#step-7-uploads) |
| `resource download`   | `project-id`, `output`                                       | [07-media.md](07-media.md#step-9-downloads) |
| `node create image`   | the run flags, and `resource-id` and `import-kind` for the upscale import | [Step 14](#step-14-generation-operation), [12-node-upscale.md](12-node-upscale.md) |
| `node create video`   | the run flags                                                | Step 14 |
| `node create audio`   | the run flags with `scenario` and without `count`            | Step 14 ("All audio workflows produce one output; omit `--count`", `skill: references/identity-and-references.md#audio-model-and-voice-selection`) |
| `node create element` | `project-id`, `main`, `auxiliary`, `voice`, `title`, `description` | [13-node-element.md](13-node-element.md) |
| `node upscale image`  | `project-id`, `node-id`, `submit-id`, `mode`, `resolution`, `detail`, `credit-ceiling` | 12 |
| `node show`           | `project-id`, `node-id`                                      | Step 14 |
| `operation status`    | `project-id`                                                 | [Step 13](#step-13-the-wait-a-lost-reply-and-a-failed-generation) |
| `operation wait`      | `project-id`, `timeout`                                      | Step 13 |

Why these values:

- **`version` and `schema` are not listed.** The gate runs them to read the
  list, so a CLI without them has already failed
  ([Step 6](#step-6-the-version-gate)).
- **Flags never sent are left out**, such as `--wait`, `--yes`, `--use`,
  `--profile`, `--node-id` on `node create`, and `--interval`. So is
  `resource get`: no module calls it
  ([04-architecture.md](04-architecture.md#srcdreamina)).
- **Model flags are not listed.** `--duration`, `--ratio`, `--resolution`,
  and `--voice-name` come from `arguments`, which
  [06-model-check.md](06-model-check.md) checks against the live
  `model list` ("`flags` contains only flags that the current CLI actually
  accepts", `skill: SKILL.md#preflight`).
- **`REPLY_BYTES["STDOUT"]`** is about 15 times the largest reply the pack
  reads (capture: `schema.json`, 272,322 bytes). A larger reply is refused
  as unreadable, not read without limit.
- **`MAX_REPLY_DEPTH`** exists because 05's `JSON_LIMITS["MAX_DEPTH"]` of 16
  (`F/src/config/security.py:38-41`) would refuse the schema reply, which
  nests 23 levels (capture: `schema.json`).
- **`CALL_SECONDS["LOCAL"]`** matches 05's `ACCOUNT_TIMEOUTS["LOCAL"]`.
  [Step 7](#step-7-run-constants-messages-and-storage-names) adds the run's
  keys.
- **`DREAMINA_URLS`** are written without the scheme, as F's
  `DASHBOARD_URLS` are (`F/src/config/fal.py`): the home page and the CLI
  page that [research/cli.md](research/cli.md#account-and-plan-gate) cites.

Add `ENVIRONMENT_VARIABLES["INSTALL_DIRECTORY"] = "DREAMINA_CANVAS_INSTALL_DIR"`
to `src/config/storage.py`, as
[05-foundation.md](05-foundation.md#step-4-storage-constants)'s table gives
it, and change the comment above `ENVIRONMENT_VARIABLES` to "An absolute
folder that replaces the platform's own state folder, and the installer's
own folder for the CLI, which find_binary checks first."

Add `VERSION_PATTERN` and `REASON_PATTERNS` to `src/config/patterns.py`, with
the values and comments [05-foundation.md](05-foundation.md#step-5-patterns)
fixes, in the steps that first compile them ([Step 4](#step-4-failures) and
[Step 6](#step-6-the-version-gate)).

## Step 2: CLI and run messages

Create `src/config/messages/cli.py`, with the docstring "Messages for a
Dreamina CLI that is missing, too old, changed, or unreadable, and for its
installer." Constants in ASCII order. 05 adds the installer's messages in its
Part B ([05-foundation.md](05-foundation.md#step-16-installer-and-sign-in-messages)).

| Constant                 | Code            | Text |
| ------------------------ | --------------- | ---- |
| `CLI_CHANGED`            | `CONFIGURATION` | `The Dreamina CLI does not offer {command}, which this extension uses. Update the Dreamina extension in ComfyUI to its latest release.` |
| `CLI_MISSING`            | `CONFIGURATION` | `ComfyUI could not find the Dreamina CLI. Select Install in Dreamina Settings.` |
| `CLI_NOT_STARTED`        | `CONFIGURATION` | `The Dreamina CLI is installed but could not start on this computer. Select Update in Dreamina Settings to install it again.` |
| `CLI_REPLY_INVALID`      | `TRANSPORT`     | `The Dreamina CLI gave a reply this extension cannot read. Try again. If it happens again, select Update in Dreamina Settings.` |
| `CLI_TIMEOUT`            | `TRANSPORT`     | `The Dreamina CLI did not answer within {seconds} seconds, so ComfyUI stopped it. Check the internet connection, then try again.` |
| `CLI_OUTDATED`            | `CONFIGURATION` | `The Dreamina CLI is version {version}, and this extension needs version {minimum} or later. Select Update in Dreamina Settings.` |
| `CLI_VERSION_UNREADABLE` | `CONFIGURATION` | `The Dreamina CLI did not report its version and commands in a form this extension reads. Select Update in Dreamina Settings.` |

Create `src/config/messages/run.py`, with the docstring "Messages for the
failures the Dreamina CLI reports." and the second paragraph "{reason} is
the CLI's cleaned reason, ending as a sentence, and page placeholders are
filled from DREAMINA_URLS." Constants in ASCII order. A message that carries
a page placeholder is always formatted with `**DREAMINA_URLS`, together with
its other values.

| Constant                 | Code             | Text |
| ------------------------ | ---------------- | ---- |
| `CEILING_TOO_LOW`        | `CREDITS`        | `This run needs {minimum} credits, more than its credit_ceiling of {ceiling}. Nothing was billed. Raise credit_ceiling to {minimum} or more to run it.` |
| `CLI_FAILED`             | the map's row    | `The Dreamina CLI stopped with an error: {reason} Try again. If it happens again, select Update in Dreamina Settings.` |
| `CREDENTIALS_DENIED`     | `AUTHENTICATION` | `The Dreamina CLI may not open this computer's sign-in store. Run ComfyUI as the user who signed in to Dreamina, then try again.` |
| `CREDENTIALS_UNREADABLE` | `AUTHENTICATION` | `The Dreamina CLI could not read this computer's sign-in store: {reason} Check that ComfyUI runs as the user who signed in. If it does, contact Dreamina support before you sign in again.` |
| `DNS_FAILED`             | `TRANSPORT`      | `The Dreamina CLI could not look up Dreamina's servers. Check this computer's internet connection and DNS settings, then try again.` |
| `FLAG_REFUSED`           | `INVALID_INPUT`  | `The Dreamina CLI refused a flag or a value, so nothing was sent: {reason} Check arguments against the model's flags in Model: Info.` |
| `LOCAL_STATE_FAILED`     | `CONFIGURATION`  | `The Dreamina CLI could not save its own records on this computer: {reason} Check that the user running ComfyUI can write to its home folder, then try again.` |
| `MODE_REQUIRED`          | `INVALID_INPUT`  | `The Dreamina CLI needs a mode for this run, so nothing was sent. Set "mode" in arguments to one of the model's modes in Model: Info.` |
| `NETWORK_DENIED`         | `TRANSPORT`      | `This computer stopped the Dreamina CLI from reaching the internet. Allow dreamina-canvas in your firewall or security software, then try again.` |
| `NETWORK_TIMEOUT`        | `TRANSPORT`      | `The connection to Dreamina timed out. Check the internet connection, then try again.` |
| `NO_REASON`              | none             | `no reason given.` |
| `OPERATION_INCOMPLETE`   | `TRANSPORT`      | `Dreamina did not finish this step before the Dreamina CLI stopped waiting for it. Try again.` |
| `PRICE_UNKNOWN`          | `CREDITS`        | `Dreamina could not work out the price of this run, so it stopped before running. Nothing was billed. Try again in a few minutes.` |
| `REFERENCE_REFUSED`      | `INVALID_INPUT`  | `The Dreamina CLI refused a reference, so nothing was sent: {reason} Connect references only from Dreamina nodes.` |
| `REFERENCE_UNAVAILABLE`  | `UNAVAILABLE`    | `A reference or an uploaded file is not available on the ComfyUI canvas: {reason} Connect a current output, or run the node that made it again.` |
| `REGION_UNAVAILABLE`     | `UNAVAILABLE`    | `The Dreamina CLI is not available for this account's region: {reason} See {cli_page} for who can use it.` |
| `RUN_REFUSED`            | the map's row    | `Dreamina refused this run, so it did not start and nothing was billed: {reason} Change the prompt, the connected inputs, or arguments, then run again.` |
| `SIGN_IN_LIMITED`        | `RATE_LIMITED`   | `Dreamina is limiting sign-in requests from this computer: {reason} Wait a few minutes, then try again.` |
| `SIGN_IN_REQUIRED`       | `AUTHENTICATION` | `You are not signed in to Dreamina. In Dreamina Settings, select Sign in, then try again.` |
| `TITLE_REQUIRED`         | `INVALID_INPUT`  | `Dreamina needs words in the prompt to name this run, so nothing was sent. Describe the result in prompt, then run again.` |
| `UPGRADE_REQUIRED`       | `CONFIGURATION`  | `Dreamina no longer accepts this version of the Dreamina CLI. Select Update in Dreamina Settings, then try again.` |

`RUN_REFUSED` arrives in Part B with its first reader, the run call of
[Step 14](#step-14-generation-operation), as the owner's rule for messages
says ([research/owner-rules.md](research/owner-rules.md#process-and-plans)).

Why the texts say what they say:

- **Billing.** A message says "Nothing was billed" or "nothing was sent"
  only when the failure itself proves it: exit 2 is refused locally
  (capture: `error-invalid-flag.json`), exit 10 "stops after the quote ...
  and nothing has been charged" (`skill: references/credits-and-hitl.md`),
  and the run call's refusals are not exit 20, which the CLI gives "after an
  accepted media submission" (`skill: references/recovery-and-idempotency.md`).
  The other messages make no billing claim, because the same failure can
  follow an accepted run, where [Step 14](#step-14-generation-operation)
  adds the record's state.
- **Next steps.** No message a free call can raise says "run again". "Try
  again" fits a free read, and a failure of the wait is wrapped in
  `GENERATION_UNCOLLECTED`, which sends the person to **Generation:
  Download** instead.
- **The dialog's words.** "Install", "Update", and "Sign in" are the button
  names of Dreamina Settings ([01-decisions.md](01-decisions.md#the-cli-on-the-persons-computer),
  [16-frontend.md](16-frontend.md)).
- **No identifiers.** No message holds a path, a user ID, a submit ID, or
  `meta.requestId` ([05-foundation.md](05-foundation.md#porting-rules) rule
  10). Reasons are cleaned of them ([Step 4](#step-4-failures)).
- **Credentials.** `CREDENTIALS_UNREADABLE` does not say to sign out,
  because the skill says to "preserve records and contact support before
  clearing or replacing them" (`skill: references/authentication.md#authentication`).
- **What has no message of its own.** Not enough credits, a plan that cannot
  use the model, and the safety check have no documented `error.code`,
  `class`, or `reason` in release 1.0.3 (strings, schema, and skill; see
  [research/cli.md](research/cli.md#the-json-envelope)). They reach the
  caller's `context` message or `GENERATION_FAILED` with Dreamina's own
  cleaned reason, which names the cause in English ("JSON error messages are
  always English", `skill: references/authentication.md#authentication`).
  The owner does not change the account to provoke them
  ([research/owner-rules.md](research/owner-rules.md#paid-requests-and-live-checks)).
  When a run records their fields, each gets a row in
  [Step 4](#step-4-failures) and a message here, recorded in
  [README.md](README.md#changes-made-while-building).

## Step 3: CLI records and the first reply records

Every record below reads the CLI's JSON. A field whose wire name differs
from its Python name carries `Field(alias="<wire name>")`, as 06's model
records do; the tables give each alias after the field.

Create `src/types/cli.py`, with the docstring "The envelope every Dreamina
CLI reply has, and the result of one call; unknown fields are ignored."

| Record               | Kind | Fields |
| -------------------- | ---- | ------ |
| `Validation`         | `Reply` | `reason_code: str = ""` (`reasonCode`), `field_path: str \| None = None` (`fieldPath`), `detail: str = ""` |
| `LocalStorage`       | `Reply` | `submission_phase: str \| None = None` (`submissionPhase`); its `reason` is not declared, because no row reads it (row 3 quotes `_choose_reason`) |
| `CliFailure`         | `Reply` | `code: str = ""`, `failure_class: str = ""` (`class`), `message: str = ""`, `reason: str \| None = None`, `retryable: bool = False`, `required_action: str \| None = None` (`requiredAction`), `validation: Validation \| None = None`, `local_storage: LocalStorage \| None = None` (`localStorage`) |
| `CreditConfirmation` | `Reply` | `reason: str = ""`, `minimum_credit_ceiling: int \| None = None` (`minimumCreditCeiling`) |
| `PartialItem`        | `Reply` | `node_id: str \| None = None` (`nodeId`), `submit_id: str \| None = None` (`submitId`), `source_node_id: str \| None = None` (`sourceNodeId`) |
| `PartialRun`         | `Reply` | `items: tuple[PartialItem, ...] = ()` |
| `CliMeta`            | `Reply` | `request_id: str \| None = None` (`requestId`) |
| `CliReply`           | `Reply` | `schema_version: str` (`schemaVersion`), `ok: bool`, `payload: Json = None` (`data`), `error: CliFailure \| None = None`, `credit_confirmation: CreditConfirmation \| None = None` (`creditConfirmation`), `partial: PartialRun \| None = None` (`partialData`), `meta: CliMeta \| None = None` |
| `CliResult`          | `@dataclass(frozen=True, slots=True)` | `exit_code: int`, `reply: CliReply` |

- The fields are the envelope's ([02-dreamina-contract.md](02-dreamina-contract.md#replies);
  captures `error-auth-required.json`, `error-invalid-flag.json`,
  `error-login-expired.json`, `auth-account.json`;
  [research/cli.md](research/cli.md#the-json-envelope)).
- `class` is a Python keyword and `data` a banned word. `partialData` would
  read as `partial_data`, which holds `data`, so it is `partial`
  ([01-decisions.md](01-decisions.md#banned-words-that-shape-names)).
- `payload` stays raw JSON. Each caller reads it into its own reply record
  with `parse_reply` ([Step 5](#step-5-the-cli-runner)), so one envelope
  serves every command.
- `meta.requestId` is on every reply (capture: `auth-account.json`). It is
  read only for `result` ([Step 17](#step-17-node-outputs)), because the
  skill keeps it "for support" (`skill: SKILL.md#hard-boundaries`).
- `clientUpgrade`, `deletionConfirmation`, and the localStorage `store`,
  `stage`, and `directory` are not declared. The pack never runs a command
  from a reply, deletes no node, and shows no path.
- `retryable` is read by [07-media.md](07-media.md) for its second try of an
  upload or a download. The run call never reads it
  ([02-dreamina-contract.md](02-dreamina-contract.md#exit-codes-and-failure-fields)).
- `PartialItem.source_node_id` is read by [12-node-upscale.md](12-node-upscale.md)
  (`partialData.items[].sourceNodeId/submitId`,
  `skill: references/credits-and-hitl.md#image-upscale-uses-its-own-approval-scope`).

The module ends with `__all__` listing the nine records in ASCII order.

Create `src/types/replies.py`, with the docstring "The parts of the Dreamina
CLI's success replies the extension reads; unknown fields are ignored." Part
A adds the records that the version gate and
[05-foundation.md](05-foundation.md#step-17-sign-in-and-the-account) read.
[Step 8](#step-8-run-reply-records) adds the rest.

| Record          | Fields | Reads | Schema fields not declared |
| --------------- | ------ | ----- | -------------------------- |
| `VersionReply`  | `version: str` | `version` | `commit`, `buildTime`, `edition`, `distribution`, `releaseDate`, `releaseNotes` |
| `SchemaFlag`    | `name: str` | One flag of a command | `type`, `required`, `default`, `description`, `constraints` |
| `SchemaCommand` | `name: str`, `flags: tuple[SchemaFlag, ...] = ()`, `subcommands: tuple[SchemaCommand, ...] = ()` | One command and the commands under it | `summary`, `reads`, `writes`, `formats`, `dryRun`, `confirmation`, `declaredExitCodes`, `arguments`, `constraints`, `successData`, `dryRunData` |
| `SchemaReply`   | `schema_version: str` (`schemaVersion`), `subcommands: tuple[SchemaCommand, ...]` | `schema` | `edition`, `distribution`, `locale`, `command`, `globalFlags` |
| `AuthState`     | `logged_in: bool` (`loggedIn`) | `auth login` and `auth wait` `data.state` | `expiresAt`, `credentialStorage` |
| `AuthChallenge` | `device_code: str = Field(alias="deviceCode", repr=False)`, `user_code: str` (`userCode`), `verification_uri: str` (`verificationUri`), `verification_uri_complete: str \| None = None` (`verificationUriComplete`), `poll_seconds: int` (`pollSeconds`), `expires_at: str \| None = None` (`expiresAt`) | `data.challenge` | none |
| `AuthReply`     | `logged_in: bool \| None = None` (`loggedIn`), `status: str \| None = None`, `state: AuthState \| None = None`, `challenge: AuthChallenge \| None = None` | `auth status` (`loggedIn` at the top), `auth login`, `auth wait` | `profile`, `region`, `environment`, `authMode`, `distribution`, `version`, `edition`, and `auth status`'s `expiresAt` and `credentialStorage` |
| `AccountReply`  | `user_id: int` (`userId`), `is_vip: bool \| None = None` (`isVip`), `vip_level: str \| None = None` (`vipLevel`) | `auth account` | none |

- Every name is the schema's, in snake_case (schema: `version`, `schema`,
  `auth status`, `auth login`, `auth wait`, `auth account` `successData`).
- `SchemaCommand.subcommands` refers to `SchemaCommand` itself; Pydantic
  resolves the self-reference by itself.
- `AuthReply` reads both shapes with optional fields, because 05 reads
  `logged_in` from `auth status` and `status`, `state`, and `challenge` from
  `auth login` and `auth wait`. The owner's approval returned `status`
  `logged_in` and `state.loggedIn` `true`
  ([02-dreamina-contract.md](02-dreamina-contract.md#results-of-the-contract-runs)).
- `device_code` has `repr=False`, so no record's text shows it
  ([05-foundation.md](05-foundation.md#names-this-plan-uses-from-other-plans)).
- `auth logout`'s `loggedOut` is not read: exit 0 is enough
  ([05-foundation.md](05-foundation.md#step-17-sign-in-and-the-account)).

## Step 4: Failures

Create `src/dreamina/failures.py`, ported from `F/src/fal/failures.py`, with
the docstring "Turn the Dreamina CLI's failure replies into reviewed
messages, reading structured fields only." and the second paragraph "The
CLI's message text is never matched; it is shown, cleaned, only where no
field names the cause." Compile `REASON_PATTERNS["URL"]`, `["PATH"]`, and
`["IDENTIFIER"]` ([05-foundation.md](05-foundation.md#step-5-patterns)) as
`_URL`, `_PATH`, and `_IDENTIFIER`.

| Function | Does |
| -------- | ---- |
| `sanitize_reason(text: str) -> str` | F's `_sanitize_reason` (`F/src/fal/failures.py:98-111`), made public for 05's installer output: removes links (`_URL`), then paths (`_PATH`), then identifier-shaped text (`_IDENTIFIER`); collapses whitespace; cuts to `MAX_REASON_CHARACTERS` with `…`; adds a full stop when the text does not end in a `REASON_ENDINGS` character. An empty result is `NO_REASON`. |
| `build_failure(result: CliResult, context: str, *, credit_ceiling: int \| None = None) -> DreaminaError` | The map below. `context` is the caller's message for a failure no row names. `credit_ceiling` is the run's, passed by a run call so a stop at the quote names it. |

Callers pass these contexts:

| Caller | `context` |
| ------ | --------- |
| Every free call: 05's sign-in, account, and status calls, 06's model list, 13's Element, 15's voices, and this plan's canvas, wait, and `node show` calls | `CLI_FAILED` |
| A run call: the generation run of [Step 14](#step-14-generation-operation) and the upscale of [12-node-upscale.md](12-node-upscale.md) | `RUN_REFUSED`, with `credit_ceiling` |
| [07-media.md](07-media.md)'s uploads and downloads | `UPLOAD_REFUSED`, `DOWNLOAD_FAILED` |

The private `_choose_reason(validation: Validation | None, message: str) ->
str` builds the text before cleaning: `"{field_path}: {detail}"` when
`validation` has a `field_path`, `validation.detail` when it has none, and
`message` when there is no `validation`. "`detail` is only display and
correction context"
(`skill: references/identity-and-references.md#diagnose-reference-rejection-without-guessing`),
so it is shown, never matched.

`build_failure` takes `failure = result.reply.error`. A failure reply with no
`error` object reads as `CliFailure()`, whose fields are all empty, so it
reaches the last row. The rows are tried in this order, and the first that
matches decides:

| Order | When | Code | Message | `{reason}` |
| ----- | ---- | ---- | ------- | ---------- |
| 1 | `exit_code == EXIT_CODES["CONFIRM"]`, or `required_action == "confirm"` | `CREDITS` | `CEILING_TOO_LOW` with `minimum=credit_confirmation.minimum_credit_ceiling` and `ceiling=credit_ceiling`; `PRICE_UNKNOWN` when `minimumCreditCeiling` is absent | none |
| 2 | `required_action == "upgrade"` | `CONFIGURATION` | `UPGRADE_REQUIRED` | none |
| 3 | `local_storage` is present | `CONFIGURATION` | `LOCAL_STATE_FAILED` | `_choose_reason` |
| 4 | `reason` is in `_REASON_FAILURES` | its row | its row | `_choose_reason` |
| 5 | `exit_code == EXIT_CODES["SIGN_IN"]`, `required_action == "login"`, or `failure_class == "auth_required"` | `AUTHENTICATION` | `SIGN_IN_REQUIRED` | none |
| 6 | `code` is in `_CODE_FAILURES` | its row | its row | `_choose_reason` |
| 7 | `exit_code == EXIT_CODES["INCOMPLETE"]`, `required_action == "resume"`, or `failure_class == "operation_incomplete"` | `TRANSPORT` | `OPERATION_INCOMPLETE` | none |
| 8 | `exit_code == EXIT_CODES["INVALID"]`, or `failure_class == "invalid_input"` | `INVALID_INPUT` | `context` | `_choose_reason` |
| 9 | Anything else: an unknown code, and exit codes 1, 12, 13, 21, and 22 | `TRANSPORT` | `context` | `_choose_reason` |

The private `_REASON_FAILURES: dict[str, tuple[ErrorCode, str]]`, from
`skill: references/authentication.md#authentication`:

| `error.reason`                       | Code             | Message                  |
| ------------------------------------ | ---------------- | ------------------------ |
| `dns_resolution_failed`              | `TRANSPORT`      | `DNS_FAILED`             |
| `network_permission_denied`          | `TRANSPORT`      | `NETWORK_DENIED`         |
| `network_timeout`                    | `TRANSPORT`      | `NETWORK_TIMEOUT`        |
| `credential_store_permission_denied` | `AUTHENTICATION` | `CREDENTIALS_DENIED`     |
| `credential_store_unavailable`       | `AUTHENTICATION` | `CREDENTIALS_UNREADABLE` |
| `credential_store_corrupt`           | `AUTHENTICATION` | `CREDENTIALS_UNREADABLE` |

The private `_CODE_FAILURES: dict[str, tuple[ErrorCode, str]]`, from the
codes in the binary ([research/cli.md](research/cli.md#the-json-envelope)):

| `error.code`                     | Code            | Message                 | Source |
| -------------------------------- | --------------- | ----------------------- | ------ |
| `cli.generation_mode_required`   | `INVALID_INPUT` | `MODE_REQUIRED`         | exit 2 (`skill: references/identity-and-references.md#image-and-video-generation-edits`) |
| `cli.generation_title_required`  | `INVALID_INPUT` | `TITLE_REQUIRED`        | "create --run needs explicit title when prompt is empty" (schema: `node create video` `--prompt`) |
| `cli.invalid_flag`               | `INVALID_INPUT` | `FLAG_REFUSED`          | capture: `error-invalid-flag.json` |
| `cli.invalid_resource_reference` | `INVALID_INPUT` | `REFERENCE_REFUSED`     | "rejected **locally** with an invalid-input exit" (`skill: references/identity-and-references.md#public-identity-model`) |
| `cli.resource_unavailable`       | `UNAVAILABLE`   | `REFERENCE_UNAVAILABLE` | strings |
| `cli.region_not_available`       | `UNAVAILABLE`   | `REGION_UNAVAILABLE`    | strings |
| `cli.passport_rate_limited`      | `RATE_LIMITED`  | `SIGN_IN_LIMITED`       | strings |

How the named codes reach their messages:

| Code or field | Row | Message |
| ------------- | --- | ------- |
| `cli.authentication_required` (exit 11, class `auth_required`) | 5 | `SIGN_IN_REQUIRED` |
| `cli.login_expired` (exit 11) outside 05's sign-in wait | 5 | `SIGN_IN_REQUIRED`; 05's wait reads the code itself first ([05-foundation.md](05-foundation.md#step-17-sign-in-and-the-account)) |
| `cli.generation_confirmation_required` with `minimumCreditCeiling` | 1 | `CEILING_TOO_LOW` |
| `cli.generation_confirmation_required` without it (`occupancy_unknown`) | 1 | `PRICE_UNKNOWN` |
| `cli.invalid_flag`, `cli.generation_mode_required`, `cli.generation_title_required`, `cli.invalid_resource_reference` | 6 | Their own |
| Any other `invalid_input` code, such as a server refusal at save | 8 | The caller's `context`, with `validation.detail` |
| `cli.resource_unavailable`, `cli.region_not_available`, `cli.passport_rate_limited` | 6 | Their own |
| `requiredAction` `upgrade` | 2 | `UPGRADE_REQUIRED` |
| `dns_resolution_failed`, `network_permission_denied`, `network_timeout`, `credential_store_*` | 4 | Their own |
| `operation_incomplete` (exit 20) where a caller does not expect it | 7 | `OPERATION_INCOMPLETE` |
| Unknown codes, and exits 1, 12, 13, 21, 22 | 9 | The caller's `context`, with the cleaned `error.message` |

Why this order:

- **A finer field decides before a coarser one.** The reason refines the
  class it comes with, and a known code refines its exit code's general
  message. Every row reads a structured field; no row reads `message`
  ("Branch on structured fields and exit classes, never localized message
  text", `skill: SKILL.md#error-decisions`).
- **Exit 10 comes first** because its refusal carries Dreamina's quote and
  "nothing has been charged" (`skill: references/credits-and-hitl.md`).
- **Upgrade comes before sign-in**, because "Authentication, permission,
  upgrade, and invalid-response errors are not automatically retried or
  converted to `resume`: follow their original `requiredAction`"
  (`skill: references/recovery-and-idempotency.md`).
- **Local storage comes before the codes.** Its own reason is what the
  person can fix, and "Local-only failure does not prove a remote generation
  failed" (`skill: references/authentication.md#local-business-state-storage`).
  The run call reads `after_submit` before it ever calls `build_failure`
  ([Step 14](#step-14-generation-operation)).
- **Credential-store reasons come before sign-in,** so a store the CLI may
  not open never tells the person to sign in, which would not help.
- **Codes other plans own** join `_CODE_FAILURES` in their own milestone,
  with their messages: the upload and download codes from
  [07-media.md](07-media.md) (`cli.download_too_large` among them), and
  `cli.image_upscale_unavailable` and `cli.upscale_already_submitted` from
  [12-node-upscale.md](12-node-upscale.md). `cli.credit_flags_conflict` and
  `cli.audio_music_model_required` need no row: the pack never sends both
  credit flags, and always sends `--model`.

Each message is formatted with
`template.format(reason=…, minimum=…, ceiling=…, **DREAMINA_URLS)`. A
template without a placeholder drops that value, as in F
(`F/src/fal/failures.py:166-175`).

F's `read_failure`, `_read_reason`, `_read_refusal`, `_describe_refusal`,
`_read_retry_after`, `_choose_status_failure`, and the status table are not
ported: they read fal's HTTP bodies and headers.

The module ends with `__all__ = ["build_failure", "sanitize_reason"]`.
[Step 13](#step-13-the-wait-a-lost-reply-and-a-failed-generation) adds
`build_generation_failure`.

## Step 5: The CLI runner

Create `src/dreamina/cli.py`, with the docstring "Find the Dreamina CLI and
run it, the only place the extension starts it." and the second paragraph
"Each call is one process with closed input and capped output. A cancel or a
timeout kills the process and waits for it to end, so no child outlives its
node." It defines the private `_SYSTEM = "WINDOWS" if sys.platform ==
"win32" else "POSIX"`, with the comment "The key of the server's system in
BINARY_NAMES and INSTALL_FOLDERS."

| Function | Does |
| -------- | ---- |
| `find_binary() -> Path \| None` | Returns the first executable file of: `Path(os.environ[ENVIRONMENT_VARIABLES["INSTALL_DIRECTORY"]]) / BINARY_NAMES[_SYSTEM]` when the variable is set; `shutil.which(BINARY_NAMES[_SYSTEM])`; and `Path.home().joinpath(*INSTALL_FOLDERS[_SYSTEM], BINARY_NAMES[_SYSTEM])`. A file counts when `path.is_file()` and `os.access(path, os.X_OK)`. `None` when none does. |
| `send_command(arguments: Sequence[str], timeout_seconds: float) -> CliResult` | Runs one call, as below |
| `parse_reply[R: Reply](payload: Json, record: type[R]) -> R` | `record.model_validate(payload)`; a `pydantic.ValidationError` raises `CLI_REPLY_INVALID` with `TRANSPORT`. Every caller reads a success payload with it. |

The order is [01-decisions.md](01-decisions.md#the-cli-on-the-persons-computer)'s.
A variable that names an empty folder falls through to `PATH`, as the
installer itself keeps the folder of a `dreamina-canvas` already on `PATH`
([research/cli.md](research/cli.md#release-and-install)). `Path.home()`
reads `USERPROFILE` on Windows, which gives `%USERPROFILE%\bin`.
`find_binary` runs at every call, so an install or a move is found at once.

`send_command`:

1. `binary = find_binary()`; `None` raises `CLI_MISSING` with
   `CONFIGURATION`.
1. Start `asyncio.create_subprocess_exec(binary, *GLOBAL_ARGUMENTS,
   *arguments, stdin=asyncio.subprocess.DEVNULL,
   stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)`. No
   `env` is passed, so the server's environment reaches the CLI unchanged and
   it finds the person's credentials ([02-dreamina-contract.md](02-dreamina-contract.md#how-the-pack-calls-the-cli)).
   An `OSError` raises `CLI_NOT_STARTED` with `CONFIGURATION`.
1. Inside `asyncio.timeout(timeout_seconds)`, `asyncio.gather` the private
   `_read_stream(process.stdout, REPLY_BYTES["STDOUT"])`,
   `_read_stream(process.stderr, REPLY_BYTES["STDERR"])`, and
   `process.wait()`. Reading both streams at once keeps a full pipe from
   stopping the child.
1. A `TimeoutError` raises `CLI_TIMEOUT` with `TRANSPORT`, formatted with
   `seconds=math.ceil(timeout_seconds)`.
1. In `finally`, when `process.returncode is None` (a timeout, a cancel, or a
   reply over its cap): `process.kill()`, with `ProcessLookupError`
   suppressed, then `await asyncio.shield(process.wait())`. A cancel keeps
   propagating after the child is killed.
1. Return `_parse_result(exit_code, stdout, stderr)`.

Private helpers:

| Helper | Does |
| ------ | ---- |
| `_read_stream(stream, max_bytes) -> bytes` | Reads `REPLY_BYTES["CHUNK"]` at a time until end of file. More than `max_bytes` raises `CLI_REPLY_INVALID` with `TRANSPORT`. |
| `_parse_result(exit_code, stdout, stderr) -> CliResult` | Reads stdout on `EXIT_CODES["OK"]` and stderr otherwise: UTF-8, then `parse_json(text, max_bytes=len(content) + 1, max_depth=MAX_REPLY_DEPTH)`, then an object, then `parse_reply(document, CliReply)`. Raises `CLI_REPLY_INVALID` with `TRANSPORT` for a `UnicodeError`, a `DreaminaError` from `parse_json`, a value that is not an object, or a reply whose `ok` is not `exit_code == EXIT_CODES["OK"]`. Returns `CliResult(exit_code, reply)`. |

Failure rules:

| Event | Raises | Code |
| ----- | ------ | ---- |
| No binary | `CLI_MISSING` | `CONFIGURATION` |
| The process cannot start | `CLI_NOT_STARTED` | `CONFIGURATION` |
| `timeout_seconds` passes | `CLI_TIMEOUT` | `TRANSPORT` |
| A reply over its cap, not UTF-8, not one JSON object, or whose `ok` disagrees with the exit code | `CLI_REPLY_INVALID` | `TRANSPORT` |
| A cancel | `asyncio.CanceledError`, after the child is killed | none |
| Any exit code with a valid reply | Nothing: the `CliResult` is returned | none |

Details:

- **The caller decides what a failure reply means.** `send_command` returns
  exit 20, exit 10, and every other failure as a `CliResult`, because exit
  20 is the normal answer of a short wait ([Step 13](#step-13-the-wait-a-lost-reply-and-a-failed-generation))
  and exit 10 is the run's quote ([Step 14](#step-14-generation-operation)).
- **An unreadable reply is `TRANSPORT` for every call.** For the run call,
  [Step 14](#step-14-generation-operation) turns it into a read-only check
  and then `UNCERTAIN`, as [02-dreamina-contract.md](02-dreamina-contract.md#replies)
  decides. A timeout is `TRANSPORT` too, as F treats a free read that runs
  out of time (`F/src/fal/transport.py:104-120`).
- **The argument list is never a shell line.** `create_subprocess_exec`
  passes each item as one argument, so a prompt with quotes, newlines, or
  `$` needs no escaping, and a literal `{{` stays the person's `\{{`
  ([02-dreamina-contract.md](02-dreamina-contract.md#how-the-pack-calls-the-cli)).
- **Threads.** ComfyUI runs nodes on its executor loop in another thread.
  Python 3.12's child watcher serves a loop in any thread, and Windows uses
  the proactor loop, which supports subprocesses.

The module ends with `__all__ = ["find_binary", "parse_reply", "send_command"]`.

## Step 6: The version gate

Create `src/dreamina/contract.py`, with the docstring "Check once per
process that the installed Dreamina CLI is recent enough and offers every
command and flag this extension sends." Compile `VERSION_PATTERN` as
`_VERSION`, and parse `MINIMUM_VERSION` once into `_MINIMUM` (its three
groups as integers).

```python
# The binaries whose contract passed in this process, by path and modification time.
_VALIDATED: set[str] = set()
# The validations in flight on each event loop, keyed like _VALIDATED, which callers asking at the same time share.
_VALIDATIONS: weakref.WeakKeyDictionary[asyncio.AbstractEventLoop, dict[str, asyncio.Task[None]]] = (
    weakref.WeakKeyDictionary()
)
```

| Function | Does |
| -------- | ---- |
| `is_current_version(version: str \| None) -> bool` | `False` for `None`, a CLI not found; otherwise `True` when `_VERSION` matches and groups 1 to 3, as integers, are at least `_MINIMUM` |
| `validate_cli() -> None` | Its key is `find_binary()`'s path and its `st_mtime_ns`. Returns at once when the key is in `_VALIDATED`. Otherwise shares one `_read_contract()` per key and event loop, awaited through `asyncio.shield`, as F shares model reads (`F/src/fal/models.py:96-107`); adds the key to `_VALIDATED` when it passes. No binary, or one that cannot be read, raises `CLI_MISSING`. |

No reset function exists: 05's `save_cli` rewrites the binary, which changes
its modification time, so the next run checks it again. A one-statement
`reset_cli_validation` would be refused by `python.trivial-function`.

The private `_read_contract() -> None`, whose calls find the binary through
`send_command`:

1. Run `send_command(("version",), CALL_SECONDS["LOCAL"])`. A failure reply,
   a `schema_version` other than `REPLY_SCHEMA_VERSION`, a payload that is
   not a `VersionReply`, or a `TRANSPORT` error raises
   `CLI_VERSION_UNREADABLE` with `CONFIGURATION`. `CLI_MISSING` and
   `CLI_NOT_STARTED` pass through.
1. A version that is not current raises `CLI_OUTDATED` with `CONFIGURATION`,
   formatted with `version` and `minimum=MINIMUM_VERSION`.
1. Run `send_command(("schema",), CALL_SECONDS["LOCAL"])` and read
   `SchemaReply`, with the same refusals as step 1.
1. Build `{path: names}` from the tree: each command's path is its parents'
   names and its own, joined by one space (`node create video`), and `names`
   is the frozenset of its flags' `name`.
1. For each entry of `REQUIRED_COMMANDS` in order, a missing path raises
   `CLI_CHANGED` with `command=<path>`, and a missing flag raises
   `CLI_CHANGED` with `command=f"{path} --{flag}"`, both with
   `CONFIGURATION`.

The private `_delete_validation(validations, path, task)` is F's
`_delete_read` (`F/src/fal/models.py:50-61`): it drops a finished
validation, and takes its exception so one whose callers all canceled never
fails unseen.

Why this shape:

- **Once per process.** [01-decisions.md](01-decisions.md#the-cli-on-the-persons-computer):
  "On first use it runs `version` and `schema`". Two local calls of under a
  second each. The per-loop sharing is F's, because ComfyUI runs each prompt
  on a new loop and a task belongs to its loop.
- **Keyed by path.** A CLI found elsewhere after a move is checked again.
- **The server can still refuse a current CLI.** An upgrade pushed by the
  server reaches `UPGRADE_REQUIRED` through `build_failure`
  ([02-dreamina-contract.md](02-dreamina-contract.md#install-upgrade-and-the-version-gate)).
- **Who calls it.** `GenerateNode.validate_inputs` and the operations of
  [Step 14](#step-14-generation-operation), [12-node-upscale.md](12-node-upscale.md),
  [13-node-element.md](13-node-element.md), and
  [15-node-model-info.md](15-node-model-info.md), before their first other
  call. `send_command` does not call it, so 05's status route and the gate's
  own calls never wait on it.

The module ends with
`__all__ = ["is_current_version", "validate_cli"]`.

Part A ends here; see [Step 19](#step-19-allowlist-and-commits) for its
allowlist entry.

## Step 7: Run constants, messages, and storage names

Part B starts here.

Add to `src/config/dreamina.py`, below Part A's constants, and to its
`__all__`:

```python
# One short operation wait; the loop calls it again until the run ends or the request timeout passes. A Go duration.
WAIT_SLICE = "15s"

# The canvas every node of this extension lives on.
CANVAS_NAME = "ComfyUI"

# The canvases listed per canvas ls page, the CLI's maximum.
CANVAS_PAGE_SIZE = 100
```

and three keys to `CALL_SECONDS`, extending its comment with "READ bounds a
canvas call and the read-only check of a lost run reply. RUN bounds the run
call, which saves, quotes, approves, and submits, and returns once Dreamina
accepts the run. WAIT bounds one operation wait of WAIT_SLICE, with room for
the CLI to start and to finish its last read.":

```python
    "READ": 60,
    "RUN": 120,
    "WAIT": 45,
```

- `WAIT_SLICE` is a Go duration because a bare number is refused with
  `cli.invalid_flag` (capture: `error-invalid-flag.json`; schema:
  `operation wait` `--timeout` is `duration`).
- `CANVAS_PAGE_SIZE` is the schema's maximum (schema: `canvas ls` `--limit`,
  `1..100`).
- `CALL_SECONDS` are the pack's own bounds. `READ` allows one network read
  with the CLI's own retries ("Wait retries a transient status-query failure
  at most twice", `skill: references/recovery-and-idempotency.md`), as 06's
  `LIST_TIMEOUT_SECONDS` of 60 does. Run C-7 records how long a run call
  takes.

Create `src/config/generations.py`, with the docstring "How the extension
records a generation Dreamina accepted, waits for it, and labels it.":

```python
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
```

The module ends with `__all__` listing the six names in ASCII order.

How each value is fixed:

- **`OPERATION_STATES` is filled from the contract runs.** The values above
  are the skill's documented words: the resource axis is "`pending` /
  `running` / `succeeded` / `failed`", and "submission state is `absent`"
  (`skill: references/recovery-and-idempotency.md`). Run C-8 records the
  resource state of a finished image, and C-14 of a finished video. Before
  this step is built, the builder writes the word they recorded as
  `SUCCEEDED`, and records the value and the run in
  [README.md](README.md#changes-made-while-building) and
  [02-dreamina-contract.md](02-dreamina-contract.md#results-of-the-contract-runs).
  Run C-16 confirms `ABSENT` the same way. Run C-7 records the run reply's
  `submission.state` on acceptance. The pack does not branch on it: a run
  Dreamina refuses after its reply shows as a failed generation at the first
  wait ([Step 14](#step-14-generation-operation)). Other words the skill
  uses elsewhere (`completed`, `in_progress`, `ACCEPTED`) name other axes,
  and `success` is the node resource's `status`, which 07 reads as its own
  `RESOURCE_SUCCESS`.
- **No running or terminal state is listed.** `operation wait` answers exit
  0 only for "a terminal state" (schema: `operation wait` summary) and exit
  20 while the run continues, so the exit code says which.
- **`RECORD_RETENTION_SECONDS`** is 30 days, as F keeps a request record
  (`F/src/config/queue.py:25-26`). No run in
  [21-test-runs.md](21-test-runs.md) measures how long Dreamina keeps a known
  submission readable; C-16 reads only an unknown one. When a run measures
  it, a shorter time replaces this one, recorded in the changes table.
- **`LABEL_CHARACTERS`**: eight characters of a UUID tell one person's
  records apart, and the label also holds the model and the minute. Sixteen
  characters of an ISO time are `YYYY-MM-DDTHH:MM`, as F's label
  (`F/src/fal/queue/records.py:78-87`).
- **`WAIT_REREAD_SECONDS`** replaces F's `STREAM_REOPEN_SECONDS` of 2
  (`F/src/config/queue.py:19-20`).
- **`UPSCALE_FLAGS`**, which [04-architecture.md](04-architecture.md#srcconfig)
  lists in this module, arrives with its only reader in
  [12-node-upscale.md](12-node-upscale.md).

Create `src/config/execution.py` with the exact module
[05-foundation.md](05-foundation.md#step-6-execution-constants) fixes:
`PROGRESS_STEPS` (`CHECKED` 1, `UPLOADED` 2, `ACCEPTED` 3, `RUNNING` 4,
`DOWNLOADED` 5, `TOTAL` 6) and `CANCELLATION_POLL_SECONDS` (0.1). Its readers
arrive in this part ([Step 14](#step-14-generation-operation),
[Step 15](#step-15-run-wrapper)).

Add the names [06-model-check.md](06-model-check.md#when-each-step-is-built)
fixes for this part, with 06's values and comments: `DEFAULT_ARGUMENTS` in
`src/config/models.py`, `src/config/inputs.py` without `DEFAULT_CEILINGS`,
and `SINGLE_VALUE` in `src/config/messages/inputs.py`. `GenerateNode` and
`PaidNode` are their first readers ([Step 16](#step-16-node-base),
[Step 18](#step-18-generate-node)). `DEFAULT_CEILINGS` joins
`src/config/inputs.py` one key at a time, with 06's text, in
[09-node-image.md](09-node-image.md), [11-node-audio.md](11-node-audio.md),
and [10-node-video.md](10-node-video.md), whose node classes read it.

Create `src/config/messages/generations.py`, with the docstring "Messages
for a generation's outcomes after the run call." Constants in ASCII order,
formatted with `**DREAMINA_URLS` where they hold a page placeholder:

| Constant                   | Code             | Text |
| -------------------------- | ---------------- | ---- |
| `GENERATION_ABSENT`        | `UNAVAILABLE`    | `Dreamina no longer has a record of this generation, so its record here was deleted. If it finished, its output is on its canvas in your Dreamina projects at {home_page}.` |
| `GENERATION_EMPTY`         | `INVALID_INPUT`  | `Dreamina finished this run without any output. Change the prompt or the connected inputs, then run again.` |
| `GENERATION_EXPIRED`       | `UNAVAILABLE`    | `This generation was recorded too long ago for Dreamina to report it, so its record was deleted. If it finished, its output is on its canvas in your Dreamina projects at {home_page}.` |
| `GENERATION_FAILED`        | `INVALID_INPUT`  | `The generation failed on Dreamina: {reason} Change the prompt or the connected inputs, then run again.` |
| `GENERATION_GONE`          | `UNAVAILABLE`    | `This generation's node is no longer on its Dreamina canvas, so its outputs cannot be collected, and its record was deleted. Run the node that made it again.` |
| `GENERATION_KEEPS_RUNNING` | `INTERRUPTED`    | `Dreamina cannot stop a generation it accepted, so this one keeps running and is billed. It stays recorded. Collect its outputs with Generation: Download.` |
| `GENERATION_UNCOLLECTED`   | the failure's    | `Dreamina accepted this run and bills it, but ComfyUI could not collect it. {reason} It stays recorded, so collect it with Generation: Download instead of running the paid node again.` |
| `RUN_UNCERTAIN`            | `UNCERTAIN`      | `The Dreamina CLI stopped before it said whether Dreamina accepted this run, and Dreamina shows no run for it yet. It may still start and be billed. Look for it on the ComfyUI canvas in your Dreamina projects at {home_page} before you run again.` |
| `RUN_UNRECORDED`           | `UNCERTAIN`      | `Dreamina accepted this run, but its reply could not be read, so ComfyUI cannot collect it. It keeps running and is billed. Find its output on the ComfyUI canvas in your Dreamina projects at {home_page}.` |
| `STATUS_CODE_REASON`       | none             | `Dreamina gave error code {code}.` |
| `WAIT_LIMIT`               | `TIMEOUT`        | `Dreamina accepted this run, so it is billed, but its outputs did not arrive within the request timeout of {seconds} seconds in Dreamina Settings. It stays recorded. Collect it later with Generation: Download.` |

- `GENERATION_UNCOLLECTED`'s `{reason}` is the whole message of the failure
  it wraps, and its code is that failure's code.
- `GENERATION_FAILED` says nothing about billing. Whether a failed
  generation is billed is unknown until run C-17, and the skill warns
  against describing "net spend or refund status" without ledger facts
  (`skill: references/credits-and-hitl.md`). C-17's result may add one
  sentence, recorded in the changes table.
- `GENERATION_ABSENT` and `GENERATION_EXPIRED` name Dreamina's projects page,
  not the saved canvas, because the record's canvas may be one the pack has
  since replaced ([Step 10](#step-10-the-canvas)).
- `RUN_UNCERTAIN` and `RUN_UNRECORDED` name the projects page too. The
  canvas link is only in each `result`, which these runs do not return, and
  Dreamina Settings shows no canvas link
  ([16-frontend.md](16-frontend.md)).
- `STATUS_CODE_REASON` avoids the banned word `service` in its name; it shows
  Dreamina's `serviceCode`.
- [14-node-download.md](14-node-download.md) adds `GENERATIONS_EMPTY` and
  `GENERATION_UNKNOWN` to this module with its label lookup, their first
  reader. [12-node-upscale.md](12-node-upscale.md) reuses `RUN_UNCERTAIN`
  and `RUN_UNRECORDED` for its run call.

Add to `src/config/storage.py` the values
[05-foundation.md](05-foundation.md#step-4-storage-constants)'s table gives
this plan, and grow the comments of `FILE_NAMES` and `MAX_FILE_BYTES` and
`__all__` to match:

| Constant                       | Value             |
| ------------------------------ | ----------------- |
| `FILE_NAMES["CANVAS"]`         | `"canvas.json"`   |
| `MAX_FILE_BYTES["CANVAS"]`     | `4_096`           |
| `MAX_FILE_BYTES["GENERATION"]` | `16_384`          |
| `GENERATION_FOLDER`            | `"generations"`, with the comment "The generation records: one file per submit ID, in this folder of the state folder." |
| `GENERATION_SUFFIX`            | `".json"`, with the comment "A generation record's file name is its submit ID and this suffix." |

`GENERATION_SUFFIX` is F's `REQUEST_FILES["SUFFIX"]`
(`F/src/config/storage.py:34-38`). A record holds two UUIDs, a node ID, a
model name, and a time, so 16 KB is many times its size; the canvas file
holds one UUID and one link.

## Step 8: Run reply records

Add to `src/types/replies.py` the records the run path and 07 read, and
change the module's `__all__` to match. Every name is the schema's in
snake_case, with its alias as in [Step 3](#step-3-cli-records-and-the-first-reply-records).

| Record              | Fields | Reads | Added in |
| ------------------- | ------ | ----- | -------- |
| `CanvasProject`     | `project_id: str` (`projectId`), `web_url: str` (`webUrl`) | `canvas create` `data.project`, one `canvas ls` item | This step |
| `CanvasReply`       | `project: CanvasProject` | `canvas create` | This step |
| `CanvasListReply`   | `items: tuple[CanvasProject, ...] = ()`, `next_cursor: str \| None = None` (`nextCursor`), `has_more: bool = False` (`hasMore`) | `canvas ls` | This step |
| `NodeResource`      | `resource_id: str` (`resourceId`), `type: str`, `status: str`, `submit_id: str \| None = None` (`submitId`) | One `node.resources[]` item | This step |
| `NodeView`          | `node_id: str` (`nodeId`), `title: str \| None = None`, `resources: tuple[NodeResource, ...] = ()` | A saved node, in the run reply and in `node show` | This step |
| `RunSubmission`     | `submit_id: str` (`submitId`), `state: str` | The run reply's `data.submission` | This step |
| `RunReply`          | `node: NodeView`, `submission: RunSubmission` | `node create image\|video\|audio --run` | This step |
| `OperationResource` | `resource_id: str` (`resourceId`), `state: str`, `status_code: int \| None = None` (`serviceCode`), `required_action: str \| None = None` (`requiredAction`) | One `resources[]` item of an operation | This step |
| `Submission`        | `state: str` | An operation's `submission` | This step |
| `SubmissionError`   | `status_code: int \| None = None` (`serviceCode`), `message: str = ""`, `reason: str \| None = None`, `required_action: str \| None = None` (`requiredAction`), `validation: Validation \| None = None` | An operation's `submissionError` | This step |
| `OperationReply`    | `resources: tuple[OperationResource, ...] = ()`, `submission: Submission \| None = None`, `submission_error: SubmissionError \| None = None` (`submissionError`) | `operation wait`, `operation status` | This step |
| `NodeShowItem`      | `node: Mapping[str, Json] \| None = None` | One `node show` item | This step |
| `NodeShowReply`     | `nodes: tuple[NodeShowItem, ...] = ()` | `node show` | This step |
| `UploadReply`       | `resource_id: str` (`resourceId`), `media_type: str` (`mediaType`) | `resource upload` | This step, for [07-media.md](07-media.md#step-7-uploads) |
| `DownloadReply`     | `resource_id: str` (`resourceId`), `path: str`, `size: int`, `sha256: str` | `resource download` | This step, for [07-media.md](07-media.md#step-9-downloads) |
| `ElementReply`      | `node: NodeView` | `node create element`, and the import `node create image --resource-id` | [12-node-upscale.md](12-node-upscale.md), its first reader by build order |
| `UpscaleError`, `UpscaleItem`, `UpscaleReply` | `UpscaleError`: `status_code: int \| None = None` (`serviceCode`), `message: str = ""`; `UpscaleItem`: `source_node_id: str` (`sourceNodeId`), `submit_id: str` (`submitId`), `node_id: str \| None = None` (`nodeId`), `resource_ids: tuple[str, ...] = ()` (`resourceIds`), `state: str`, `error: UpscaleError \| None = None`; `UpscaleReply`: `items: tuple[UpscaleItem, ...] = ()` | `node upscale image` | 12 |
| `NodeView.subjects` | `subjects: Mapping[str, Json] \| None = None` (`subjectBindings`) | An Element node's bindings | [13-node-element.md](13-node-element.md) |
| `Voice`, `VoiceCatalog`, `VoicePage` | `Voice`: `voice_name: str` (`voiceName`); `VoiceCatalog`: `items: tuple[Voice, ...] = ()`, `has_more: bool` (`hasMore`), `next_offset: int` (`nextOffset`), `total_count: int` (`totalCount`); `VoicePage`: `models: Mapping[str, VoiceCatalog]` | `voice list` | [15-node-model-info.md](15-node-model-info.md) |

The schema's fields that are not declared, and why:

- **`canvas create`**: `draftVersion`, `current`, and
  `localStorageWarning`, which "does not negate a successful remote result"
  (`skill: references/authentication.md#local-business-state-storage`). The
  project's `name`, `createdAt`, and `updatedAt` are not read.
- **The run reply**: `mutation`, `quote`, `approval`, and the submission's
  `resources`, `error`, and `localStorageWarning`. The pack needs the node ID
  and the submit ID (schema: `node create video` `successData`).
- **`node.resources[]`**: `name`, `errorCode`, `createdAt`,
  `canRegenerate`, `source`, `creditsAmount`. They reach `result` through
  `NodeShowItem.node`, which keeps the whole node as JSON
  ([01-decisions.md](01-decisions.md#outputs)).
- **`NodeView`**: `parentNodeId`, `type`, `description`, `tags`, `text`,
  `status`, `upstreamNodeIds`, `downstreamNodeIds`,
  `executionDependencyNodeIds`, `generation`, `subjectBindings` (until 13),
  `timelineTracks`, `layout`, `resourceObservedAtMs`. All of them reach
  `result` in the raw node.
- **An operation**: `operationRef` (it is the submit ID), `state` (the exit
  code says whether it is terminal), the resources' `retryable`, `width`,
  `height`, and `format`, the submission's `resubmittable`, `adviceCode`,
  and `advice`, `submissionError.retryable`, `awaitingConfirmation`, and
  `localStorageWarning` (schema: `operation wait` `successData`).
- **`node show`**: each item's `nodeId`, `result`, `errorCode`, and
  `errmsg`, and the reply's `draftVersion`. An item without `node` is a node
  Dreamina did not find.
- **Upscale**: each item's `authorizedCredits`, `generationState`, and
  `resources`, and the reply's `totalMaxCredits` and `creditsApproved`.

Notes:

- `serviceCode` holds the banned word `service`, so it is `status_code`.
  `subjectBindings` holds `bind`, so it is `subjects`
  ([01-decisions.md](01-decisions.md#banned-words-that-shape-names)).
- `type` is a wire name in `NodeResource`, as in F's records
  (`F/src/types/replies.py:8-22`); Pydantic allows it.
- `NodeShowItem.node` stays raw JSON, so `result` shows the node exactly as
  Dreamina returned it, and `parse_reply(item.node, NodeView)` reads the
  parts the pack uses.
- `RunReply` requires `node` and `submission`, which the schema marks
  optional because a save without `--run` has no submission. A run reply
  without them is unreadable, and [Step 14](#step-14-generation-operation)
  treats it as a lost reply.
- The records of a later milestone arrive with their first reader, as the
  owner's rule for constants says ([research/owner-rules.md](research/owner-rules.md#process-and-plans)).
  This table fixes their fields so the plans agree.

## Step 9: Generation records

Create `src/types/generations.py`, with the docstring "Generations: the
canvas they live on, the record kept while one runs, the run a node asks
for, and what it made."

```python
class GenerationRecord(Value):
    """One run Dreamina accepted, recorded before the first wait so a run that keeps going can be collected.

    Attributes:
        version: File format version; any other is refused.
        submit_id: The run's submit ID, which also names the record's file.
        project_id: The canvas the run was sent to.
        node_id: The canvas node that holds the run's outputs.
        kind: The kind of node that sent it.
        model: The canonical model name, or what the upscale node records in its place.
        mode: The mode that ran.
        submitted_at: When the run call was sent, in ISO 8601 and UTC.
        source_node_id: The image node an upscale started from; None for a generation.

    """

    version: Literal[1]
    submit_id: str
    project_id: str
    node_id: str
    kind: Kind
    model: str
    mode: str
    submitted_at: str
    source_node_id: str | None = None
```

| Record             | Kind | Fields |
| ------------------ | ---- | ------ |
| `CanvasRecord`     | `Value` | `version: Literal[1]`, `project_id: str`, `web_url: str` |
| `GenerationPlan`   | `@dataclass(frozen=True, slots=True)` | `kind: Kind`; `title: str`, the node's display name; `model: str`, as typed, stripped; `prompt: str`; `arguments: str`, the JSON text; `credit_ceiling: int`; `references: tuple[Reference, ...]`, in socket order; `local: tuple[LocalMedia, ...]`, from 07's `list_local_media` |
| `OutputFile`       | `@dataclass(frozen=True, slots=True)` | `resource_id: str`; `kind: Kind`; `content: bytes` |
| `GenerationResult` | `@dataclass(frozen=True, slots=True)` | `record: GenerationRecord`; `node: Mapping[str, Json]`, the node as `node show` returned it; `title: str \| None`, the node's title; `files: tuple[OutputFile, ...]`, in the node's resource order; `canvas_url: str \| None`; `request_id: str \| None`, the run call's `meta.requestId` |

- `GenerationRecord` is F's `RequestRecord`
  (`F/src/types/queue.py:12-34`) with Dreamina's IDs: a submit ID instead of
  a request ID, the canvas and node instead of three addresses, and the mode.
  It holds the fields [01-decisions.md](01-decisions.md#paid-runs) lists, and
  only public IDs ("Keep only durable public identities",
  `skill: SKILL.md#persist-minimal-job-state`). The file stays snake_case:
  it is the pack's own, read with `Value`.
- `source_node_id` is for [12-node-upscale.md](12-node-upscale.md), whose
  records set `model` to its `UPSCALE_MODEL`.
- `GenerationPlan` is F's `QueuedRequest` (`F/src/types/queue.py:37-58`): the
  node's inputs as they came. The model is read and the flags are built
  inside the operation, which runs after the CLI check.
- `OutputFile` is one downloaded file, which 07's `download_resources`
  builds after its byte-count and SHA-256 checks. 07's downloads are built
  after this step ([When each part is built](#when-each-part-is-built)).
- `CanvasRecord` lives here because the canvas is where generations live; it
  is the file `canvas.json`.
- [12-node-upscale.md](12-node-upscale.md) adds `UpscaleRequest` to this
  module.

The module ends with
`__all__ = ["CanvasRecord", "GenerationPlan", "GenerationRecord", "GenerationResult", "OutputFile"]`.

## Step 10: The canvas

Create `src/storage/canvas.py`, with the docstring "Keep the pack's
Dreamina canvas: its ID and its link."

`CanvasStore(path: Path)`, with a `threading.Lock`, because the server loop
reads it for the status and the executor loop writes it:

| Method | Does |
| ------ | ---- |
| `read() -> CanvasRecord \| None` | Under the lock, `None` when the file does not exist; reads at most `MAX_FILE_BYTES["CANVAS"]` with `read_file`; a file that is not a valid `CanvasRecord` is `None`, so the next save replaces it; an `OSError` raises `STATE_UNREADABLE` with `CONFIGURATION` |
| `save(record: CanvasRecord) -> None` | Under the lock, `save_file(path, (record.model_dump_json(indent=2) + "\n").encode())` |
| `delete() -> None` | Under the lock, `path.unlink(missing_ok=True)`, with F's `bearer:disable python_lang_path_traversal` comment and the reason "The canvas file is a fixed name inside the private state folder." |

The module ends with `__all__ = ["CanvasStore"]`.

Create `src/dreamina/canvas.py`, with the docstring "Find the canvas every
node writes to, and create it when there is none." and the second paragraph
"Every run lists the account's canvases first, so a canvas the person
deleted on Dreamina is replaced before anything is uploaded or run." Callers
take `await find_canvas(store) or await create_canvas(store)`.

| Function | Does |
| -------- | ---- |
| `find_canvas(store: CanvasStore) -> CanvasRecord \| None` | Reads the saved record in a worker thread. `None` when none is saved. When one is saved and `_is_listed(record.project_id)`, returns it. Otherwise deletes the saved record in a worker thread and returns `None`. |
| `create_canvas(store: CanvasStore) -> CanvasRecord` | `project_id = str(uuid.uuid4())`. Runs `canvas create <CANVAS_NAME> --project-id <project_id>` with `CALL_SECONDS["READ"]`. A `DreaminaError` with `TRANSPORT` from `send_command` sends the same call once more, with the same ID. A failure reply raises `build_failure(result, CLI_FAILED)`. Reads `parse_reply(payload, CanvasReply)`, saves `CanvasRecord(version=RECORD_VERSION, project_id=reply.project.project_id, web_url=reply.project.web_url)` in a worker thread, and returns it. |

The private `_is_listed(project_id) -> bool` runs `canvas ls --limit
<CANVAS_PAGE_SIZE>`, then `--cursor <next_cursor>` while `has_more` and
`next_cursor` are set, with `CALL_SECONDS["READ"]` per page. It returns
`True` at the first page whose `items` hold `project_id`, else `False`. A
failure reply raises `build_failure(result, CLI_FAILED)`.

Why this shape:

- **Every call names the canvas.** The pack never passes `--use`, so the
  CLI's current canvas, which the person's own agent sessions may use, never
  changes ([01-decisions.md](01-decisions.md#the-canvas)). "An explicit
  `--project-id` avoids reading the current-canvas record"
  (`skill: references/authentication.md#local-business-state-storage`).
- **The deleted canvas.** A failed save cannot say whether the canvas or a
  reference is gone, because both return the same error
  (`skill: references/identity-and-references.md#resolution-rules`). `canvas
  ls` lists "accessible canvases with locator fields only" (schema: `canvas
  ls` summary), so a saved ID it does not list is gone. This happens before
  anything is uploaded or billed, as [01-decisions.md](01-decisions.md#the-canvas)
  requires. One list call per run costs less than a second, and no state is
  kept between runs to go stale. A canvas deleted during a run makes that
  run's next canvas call fail with its mapped message, and the next run
  replaces it. So no caller sends an upload or a run call a second time on a
  new canvas.
- **The one repeat.** The client-made `--project-id` exists so "a retry of
  the same call is safe" ([01-decisions.md](01-decisions.md#the-canvas);
  schema: `canvas create` `--project-id`, "reuse the same value when
  retrying"). Only a lost or unreadable reply is repeated, once, so a lost
  reply does not leave a second canvas named `ComfyUI`.
- **No canvas yet.** `canvas ls` with no canvases returns `items` `[]` and
  `hasMore` `false` (run C-0), so the first run creates the canvas.

The module ends with `__all__ = ["create_canvas", "find_canvas"]`.

## Step 11: Operation protocol

Port `F/src/fal/operation.py` to `src/dreamina/operation.py`, with the
docstring "Define the operation every node hands to the run wrapper, and how
a paid call is awaited through a cancel."

```python
type Progress = Callable[[int], Awaitable[None]]


class Operation[Result](Protocol):
    """One Dreamina operation, validated before anything is sent."""

    def validate(self, settings: Settings) -> None:
        """Refuse inputs the settings do not allow, before anything is sent."""
        raise NotImplementedError(settings)

    async def send(self, configuration: Configuration, progress: Progress | None) -> Result:
        """Send the operation, report each step reached, and return its result."""
        raise NotImplementedError(configuration, progress)
```

`wait_until_settled[T](task: asyncio.Task[T]) -> bool` is F's private
`_wait_settled` (`F/src/fal/queue/operation.py:60-71`), made public because
[Step 14](#step-14-generation-operation)'s run call and
[12-node-upscale.md](12-node-upscale.md)'s upscale call both use it: it waits
until the task ends, however often a cancel arrives, and reports whether one
arrived.

`Settings` and `Configuration` are 05's
([05-foundation.md](05-foundation.md#step-11-settings-records)). F's
`validate_upload_size` (`F/src/fal/operation.py:31-37`) moves to 07's
uploads. The module ends with `__all__ = ["Operation", "wait_until_settled"]`;
`Progress` is imported by name.

## Step 12: Generation store, the runtime, and the status

Create `src/dreamina/generations/__init__.py` with the docstring "Generations
Dreamina accepted: their records, the wait, and the operation that runs and
collects them."

Port `F/src/fal/queue/records.py` to `src/dreamina/generations/records.py`,
with the docstring "Keep a private record of every generation Dreamina
accepted." and the second paragraph "A generation keeps running after a
cancel, a timeout, or a ComfyUI restart, and its record lets Generation:
Download collect it." Changes:

- `RequestStore` becomes `GenerationStore(directory: Path)`, with F's
  `threading.Lock`. Files are named `<submit id>GENERATION_SUFFIX`, and
  reads are capped at `MAX_FILE_BYTES["GENERATION"]`.
- `save(record)` and `delete(submit_id)` are F's
  (`F/src/fal/queue/records.py:47-59`), with F's `bearer:disable` comment on
  the `unlink` and the reason "Record names are submit IDs this extension made,
  inside the private generations folder." `save_file` writes each record
  atomically, in a private folder
  ([05-foundation.md](05-foundation.md#step-12-private-files)).
- `list_records()` is F's (`F/src/fal/queue/records.py:61-65`): every record
  of every kind, newest first; a damaged, oversized, or other-version file is
  skipped.
- F's `read(request_id)` and `_REQUEST_ID` are not ported.
  [14-node-download.md](14-node-download.md) adds `find_record(label)`, which
  reads a record back by its label.
- The private `_build_label(record) -> str` joins, with `LABEL_SEPARATOR`:
  the first `LABEL_CHARACTERS["SUBMIT_ID"]` characters of `submit_id`; the
  `model`; and the first `LABEL_CHARACTERS["TIME"]` characters of
  `submitted_at` with `T` replaced by a space. `submitted_at` is written in
  UTC, so the label's minute is UTC. 14's `find_record` uses it too.
- `list_generation_labels(generations: GenerationStore) -> list[str]` labels
  every record with `_build_label`, newest first, for 14's dropdown.

The module ends with `__all__ = ["GenerationStore", "list_generation_labels"]`.

Add the two stores to `Runtime` in one change, as
[05-foundation.md](05-foundation.md#step-19-runtime)'s table gives them: the
slots `canvas` and `generations` in `__slots__` order, the class
annotations, the `Attributes:` lines `canvas: The pack's saved Dreamina
canvas.` and `generations: Recorded generations, one per submit ID.`, and in
`__init__`:

```python
self.canvas = CanvasStore(self.configuration.directory / FILE_NAMES["CANVAS"])
self.generations = GenerationStore(self.configuration.directory / GENERATION_FOLDER)
```

Neither store creates a file or folder until it saves.

The status document gets no canvas: Dreamina Settings shows no canvas link,
so `SettingsRoutes` and `register_routes` stay as
[05-foundation.md](05-foundation.md#step-20-settings-routes-and-the-status-document)
builds them. The canvas link reaches the person only in each `result`
([Step 17](#step-17-node-outputs)).

## Step 13: The wait, a lost reply, and a failed generation

Create `src/dreamina/generations/waiting.py`, with the docstring "Wait for
one accepted generation with short read-only waits, and check a run whose
reply was lost." and the second paragraph "Each call here is free and safe
to repeat; a cancel kills it at once." It is kept apart so `operation.py`
stays under 300 lines ([04-architecture.md](04-architecture.md#srcdreamina)).

`wait_for_operation(submit_id: str, project_id: str, deadline: float,
progress: Progress | None) -> OperationReply | None`:

1. While `remaining = deadline - time.monotonic()` is above 0:
   1. Run `operation wait <submit_id> --project-id <project_id> --timeout
      <WAIT_SLICE>` with `min(remaining, CALL_SECONDS["WAIT"])`.
   1. A `DreaminaError` with `TRANSPORT` from `send_command` (a timeout or an
      unreadable reply) sleeps `WAIT_REREAD_SECONDS` and loops. Any other
      `DreaminaError` from `send_command`, such as `CLI_MISSING`, is raised.
   1. Exit `EXIT_CODES["INCOMPLETE"]` (20): the run is still going. The first
      time, report `PROGRESS_STEPS["RUNNING"]`. Loop at once; the CLI already
      waited `WAIT_SLICE`.
   1. Exit `EXIT_CODES["OK"]`: return `parse_reply(payload, OperationReply)`.
      A payload that does not validate sleeps `WAIT_REREAD_SECONDS` and
      loops, as an unreadable reply does.
   1. Any other exit raises `build_failure(result, CLI_FAILED)`.
1. Return `None`: the deadline passed.

Why this shape:

- **Exit 20 is the normal answer.** "After an accepted media submission,
  exhausted transient errors, timeout, or interruption return `ok=false`,
  exit `20` … a new read-only `operation wait` with the returned submit ID
  is safe" (`skill: references/recovery-and-idempotency.md`). So a transient
  network failure inside the CLI also arrives as exit 20, and the loop calls
  again.
- **`--project-id` always.** It is "needed only when the local recovery
  record is missing and the service must be queried directly" (schema:
  `operation wait` `--project-id`). Passing it always makes a wait from
  Generation: Download, after a restart, or after the person's own agent
  session cleared the CLI's journal work the same way.
- **The cancel.** `wait_for_run` cancels the operation's task when ComfyUI's
  cancel arrives ([Step 15](#step-15-run-wrapper)). The `CanceledError`
  reaches `send_command`, which kills the wait process at once. A wait is
  read-only, so killing it stops nothing on Dreamina.
- **The deadline returns `None`** instead of raising, so the caller formats
  `WAIT_LIMIT` with the settings it holds.
- **`WAIT_REREAD_SECONDS`** keeps a CLI that answers garbage at once from
  starting processes in a tight loop; the deadline still bounds it, as F's
  stream reopen pause does (`F/src/fal/queue/operation.py:195-209`).

`validate_lost_run(submit_id: str, project_id: str) -> NoReturn` runs
`operation status <submit_id> --project-id <project_id>` once, with
`CALL_SECONDS["READ"]`, for a run call whose reply was lost:

- Exit 20, or exit 0 with an `OperationReply` whose `submission` is absent
  or whose `submission.state` is not `OPERATION_STATES["ABSENT"]`: Dreamina
  knows the run. Raise `RUN_UNRECORDED` with `UNCERTAIN`. No record is saved,
  because no node ID is known: the status reply carries none (schema:
  `operation status` `successData`).
- Anything else, including a `DreaminaError` from this call: raise
  `RUN_UNCERTAIN` with `UNCERTAIN`.

It uses its own bound, not the run's deadline, because it must answer even
when the run call took the last of the request timeout.
[12-node-upscale.md](12-node-upscale.md) calls it for each submit ID of a
lost upscale reply.

The module ends with `__all__ = ["validate_lost_run", "wait_for_operation"]`.

Add to `src/dreamina/failures.py`, and to its `__all__`:

`build_generation_failure(reply: OperationReply) -> DreaminaError`, for a
terminal reply with no successful resource:

1. With `submission_error`: `GENERATION_FAILED` with `INVALID_INPUT`, its
   `{reason}` from `_choose_reason(submission_error.validation,
   submission_error.message)`, cleaned with `sanitize_reason`; when that is
   empty and `status_code` is set, `STATUS_CODE_REASON.format(code=…)`.
1. Otherwise, with a resource whose `state` is not
   `OPERATION_STATES["SUCCEEDED"]` and whose `status_code` is set:
   `GENERATION_FAILED` with `STATUS_CODE_REASON.format(code=status_code)`.
1. Otherwise: `GENERATION_EMPTY` with `INVALID_INPUT`. "An empty resource
   set is not 'all succeeded'" (`skill: references/recovery-and-idempotency.md#completion-rule`).

[02-dreamina-contract.md](02-dreamina-contract.md#waiting-and-recovery)
names exactly these fields for a failed generation.

## Step 14: Generation operation

Port `F/src/fal/queue/operation.py` to `src/dreamina/generations/operation.py`,
with the docstring "Run one generation with one call, record it as soon as
Dreamina accepts it, then wait for it, read its node, and download what it
made." and the second paragraph "Dreamina has no cancel for a generation it
accepted. A cancel stops the wait, and the record stays for Generation:
Download." F's `_wait_settled` moves to `wait_until_settled`
([Step 11](#step-11-operation-protocol)). F's `_send_cancel`,
`_parse_status`, `_read_queue_reply`, `_list_encoded`, and `_download_file`
are not ported.

### `CollectOperation`

F's `CollectOperation` (`F/src/fal/queue/operation.py:132-274`), for a
generation Dreamina already accepted. It serves Generation: Download
directly, [12-node-upscale.md](12-node-upscale.md), and `GenerationOperation`
after its run call.

```python
class CollectOperation:
    """Wait for one recorded generation, read its node, and download its outputs; none of it bills."""

    def __init__(
        self,
        record: GenerationRecord,
        generations: GenerationStore,
        canvas: CanvasStore,
        deadline: float | None = None,
        request_id: str | None = None,
    ) -> None: ...
```

`deadline` is the `time.monotonic()` value at which the sending run's
request timeout ends; Generation: Download passes none, and the collection
then starts its own. `request_id` is the run call's `meta.requestId`, for
`result`. [14-node-download.md](14-node-download.md) passes `runtime.canvas`.
`validate` accepts every record: there is nothing to refuse before reading
its status.

`send(configuration, progress) -> GenerationResult`, with `deadline` set to
`self.deadline`, or `time.monotonic() +
configuration.settings.request_timeout_seconds` when it is `None`:

1. **Expired.** A record whose `submitted_at` plus
   `RECORD_RETENTION_SECONDS` is past is deleted, in a worker thread, and
   raises `GENERATION_EXPIRED` with `UNAVAILABLE`, without a call
   (`F/src/fal/queue/operation.py:249-253`).
1. **Wait.** `reply = await wait_for_operation(record.submit_id,
   record.project_id, deadline, progress)`. `None` raises `WAIT_LIMIT` with
   `TIMEOUT`, formatted with `request_timeout_seconds`; the record stays.
1. **Absent.** `reply.submission` whose `state` is
   `OPERATION_STATES["ABSENT"]` deletes the record and raises
   `GENERATION_ABSENT` with `UNAVAILABLE`. Absent "can have expired"; it
   never proves nothing ran
   ([02-dreamina-contract.md](02-dreamina-contract.md#waiting-and-recovery)),
   so the message sends the person to the canvas, and nothing is sent again.
1. **Failed.** No resource of the reply whose `state` is
   `OPERATION_STATES["SUCCEEDED"]`: the record is deleted, and
   `build_generation_failure(reply)` is raised. Nothing is left to collect.
1. **The node.** Run `node show --project-id <record.project_id> --node-id
   <record.node_id>` with `deadline - time.monotonic()`. A failure reply
   raises `build_failure(result, CLI_FAILED)`. The first item's `node` is the
   raw node; when it is missing, the record is deleted and `GENERATION_GONE`
   is raised with `UNAVAILABLE`. `view = parse_reply(node, NodeView)`.
1. **The outputs.** `files = await download_resources(record.project_id,
   view, record.submit_id, configuration.settings, deadline)`
   ([07-media.md](07-media.md#step-9-downloads)), which downloads the node's
   finished resources of this submit ID, in the node's order, and checks each
   file. Report `PROGRESS_STEPS["DOWNLOADED"]`.
1. **Done.** Delete the record, in a worker thread, only after every
   download, and return `GenerationResult(record, node, view.title, files,
   canvas_url, self.request_id)`. `canvas_url` is the saved
   `CanvasRecord.web_url` when `await asyncio.to_thread(canvas.read)` returns
   a record whose `project_id` is the record's, else `None`.

Two rules cover the calls after acceptance:

- **A cancel** during steps 2, 5, or 6 raises `DreaminaError(ErrorCode.INTERRUPTED,
  GENERATION_KEEPS_RUNNING)` from the `CanceledError`. The record stays.
  "Deleting a node does not ... cancel accepted generation tasks or refund
  credits" (`skill: references/node-deletion.md#supported-scope`).
- **A `DreaminaError`** raised by a call in steps 2 and 5, other than
  `WAIT_LIMIT`, is raised as `DreaminaError(error.code,
  GENERATION_UNCOLLECTED.format(reason=str(error)))`. The record stays, so a
  sign-out during the wait or an upgrade Dreamina pushed can be collected
  later. A failure in step 6 is raised as 07 words it: every download
  message says the run stays recorded
  ([07-media.md](07-media.md#step-2-media-messages)).

The outcomes of steps 1, 3, 4, and the missing node of step 5 are raised as
they are, after the record is deleted. They are the generation's own
answer, and reading again gives the same one.

Why success is read from the wait: completion is "a terminal state with at
least one resource whose state is the success value"
([02-dreamina-contract.md](02-dreamina-contract.md#waiting-and-recovery)),
and only `operation wait` reports it. `node show` gives the node for
`result` and the resources' order and kind, which 07 reads with its own
`RESOURCE_SUCCESS` for the node resource's `status`.

### `GenerationOperation`

F's `QueueOperation` (`F/src/fal/queue/operation.py:277-358`), for one new
run.

```python
class GenerationOperation:
    """One generation, sent with one run call and recorded as soon as Dreamina accepts it."""

    def __init__(
        self,
        plan: GenerationPlan,
        generations: GenerationStore,
        canvas: CanvasStore,
        encode: Callable[[LocalMedia, Path], Path],
    ) -> None: ...
```

`encode` is [07-media.md](07-media.md#step-6-conversions)'s
`encode_local_file`, which `GenerateNode` passes in, because `src/dreamina/`
may not import `src/comfy/` ([04-architecture.md](04-architecture.md#import-layers)).

`validate(settings)` accepts every plan: each check needs the model, which
`send` reads after the CLI check.

`send(configuration, progress)`, in this order, so every refusal comes before
anything leaves the computer and the run call is the last step that can
bill. The checks follow [06-model-check.md](06-model-check.md#what-08-does-with-these):

1. **Deadline.** `deadline = time.monotonic() +
   configuration.settings.request_timeout_seconds`.
1. **CLI.** `await validate_cli()`.
1. **Arguments.** `values = parse_arguments(plan.arguments)` (06).
1. **Model.** `listed = await find_model(plan.model, plan.kind)` (06): the
   canonical name, from the live list, cached for the process.
1. **Names.** `validate_argument_names(listed, values)` (06).
1. **Mode.** `items = (*plan.references, *plan.local)`, and `connected =
   tuple(item.media for item in items)`, in `--ref` order. `mode =
   choose_mode(listed, plan.kind, connected, values)` (06). For video, one or
   two images and nothing else give `first_last_frame`, and the count
   chooses its one-image or two-image entry. Anything else gives `m2v`.
   `"mode": "m2v"` in `arguments` overrides the choice
   ([01-decisions.md](01-decisions.md#how-the-mode-is-chosen)).
1. **Prompt and flags.** `prompt = choose_prompt(plan.prompt, values)`, then
   `flags = build_flags(mode, prompt, values)` (06).
1. **References.** `validate_references(mode, items, values)`
   ([07-media.md](07-media.md#validate_references)). Report
   `PROGRESS_STEPS["CHECKED"]`.
1. **Canvas.** `canvas_record = await find_canvas(self.canvas) or await
   create_canvas(self.canvas)` ([Step 10](#step-10-the-canvas)), and
   `project_id = canvas_record.project_id`. A saved canvas that `canvas ls`
   no longer lists is cleared and replaced here, before any upload.
1. **Uploads.** `uploaded = await send_media(project_id, plan.local,
   self.encode, configuration.settings, deadline)`
   ([07-media.md](07-media.md#step-7-uploads)). Then `ordered, placed =
   plan_references(plan.references, plan.local, uploaded)`, and, when
   `prompt` is not empty, `text = format_prompt(prompt, placed)` (07). Report
   `PROGRESS_STEPS["UPLOADED"]`.
1. **Run.** Build the arguments below, with `submit_id = str(uuid.uuid4())`.
   Run the private `_send_run(arguments, submit_id, project_id, mode,
   listed)` in its own task, and wait for it with `wait_until_settled`. Then
   take its result, which raises the call's refusal. When a cancel arrived
   during the call, raise `DreaminaError(ErrorCode.INTERRUPTED,
   GENERATION_KEEPS_RUNNING)`: the run was accepted and recorded.
1. Report `PROGRESS_STEPS["ACCEPTED"]`.
1. **Wait and collect.** Return `await CollectOperation(record,
   self.generations, self.canvas, deadline, request_id).send(configuration,
   progress)`.

A cancel during steps 2 to 10 stops the run with nothing sent to the model:
`send_command` kills the call in progress, and the checks, the canvas, and
the uploads bill nothing. It shows as ComfyUI's own
`InterruptProcessingException`, because Dreamina has accepted nothing
([Step 15](#step-15-run-wrapper)).

The run call's arguments, in this order:

```python
(
    "node", "create", plan.kind,
    "--project-id", project_id,
    "--model", listed.name,
    *flags,
    *(("--prompt", text) if prompt else ("--title", plan.title)),
    *(item for reference in ordered for item in ("--ref", reference.typed_value)),
    "--run",
    "--submit-id", submit_id,
    "--credit-ceiling", str(plan.credit_ceiling),
)
```

- `flags` are 06's: `--mode`, `--scenario` for speech, one `--<flag>
  <value>` per `arguments` key, and `--count 1` when the entry lists
  `--count` and `arguments` does not set it. No audio entry lists it.
- `prompt` is 06's `choose_prompt`: the `prompt` box, or `prompt` in
  `arguments`, as typed, or `""`. It is sent with its placeholders written in
  the CLI's form. With no prompt, `--title` is the node's display name, such
  as "Video: Generate": "create --run needs explicit title when prompt is
  empty" (schema: `node create video` `--prompt`;
  [01-decisions.md](01-decisions.md#what-a-run-sends)).
- `typed_value` is 07's `node:<id>` or `res:<uuid>`
  ([07-media.md](07-media.md#step-5-reference-records)).
- No `--wait`, `--yes`, `--use`, `--profile`, `--node-id`, or `--update-id`
  is ever sent ([02-dreamina-contract.md](02-dreamina-contract.md#generation-runs)).

`_send_run(arguments, submit_id, project_id, mode, listed) ->
tuple[GenerationRecord, str | None]` sends the run call once and records an
accepted run before anything waits for it:

1. `submitted_at = datetime.now(UTC).isoformat()`.
1. `result = await send_command(arguments, CALL_SECONDS["RUN"])`. A
   `DreaminaError` with `TRANSPORT` (a timeout, a reply over its cap, or an
   unreadable reply) is a lost reply: `await validate_lost_run(submit_id,
   project_id)` ([Step 13](#step-13-the-wait-a-lost-reply-and-a-failed-generation)).
   Any other `DreaminaError` from `send_command` (`CLI_MISSING`,
   `CLI_NOT_STARTED`) is raised: no process ran.
1. **Exit 0.** `reply = parse_reply(result.reply.payload, RunReply)`; a
   payload that does not validate is a lost reply. The node ID is
   `reply.node.node_id`.
1. **Exit 10.** Raise `build_failure(result, RUN_REFUSED,
   credit_ceiling=plan.credit_ceiling)`: Dreamina's quote, nothing billed.
   The saved draft stays on the canvas, and the pack never reuses it
   ([02-dreamina-contract.md](02-dreamina-contract.md#credit-approval)).
1. **Exit 20, or `error.local_storage.submission_phase == "after_submit"`.**
   The run was accepted. The node ID is the `node_id` of the
   `partial.items` entry whose `submit_id` is `submit_id`; when there is
   none, raise `RUN_UNRECORDED` with `UNCERTAIN`.
1. **Any other failure**, including `before_submit`, which "means only this
   invocation stopped before sending"
   (`skill: references/authentication.md#local-business-state-storage`):
   raise `build_failure(result, RUN_REFUSED,
   credit_ceiling=plan.credit_ceiling)`.
1. **Record.** Build `GenerationRecord(version=RECORD_VERSION,
   submit_id=submit_id, project_id=project_id, node_id=…, kind=plan.kind,
   model=listed.name, mode=mode.name, submitted_at=submitted_at)`, save it in
   a worker thread, and return it with `result.reply.meta.request_id` when
   `meta` is set.

Why the run call works this way:

- **Sent once.** Every run gets one new submit ID and one call, and the call
  is never sent again, whatever happens ([01-decisions.md](01-decisions.md#paid-runs)).
  "Reusing the same `submitId` replays the first run and does not charge
  twice" (`skill: references/credits-and-hitl.md`), but a replay of a run
  that never arrived "becomes a first submission and really charges"
  (`skill: references/recovery-and-idempotency.md`).
- **Shielded.** A cancel during the call waits for its answer, so an
  accepted run is always recorded (`F/src/fal/queue/operation.py:347-354`).
  Only the read-only waits and downloads are stopped at once.
- **Its own time limit.** The run call gets `CALL_SECONDS["RUN"]`, not what
  is left of the request timeout, so a run that starts near the deadline is
  never cut off between acceptance and its reply.
- **Recorded before the first wait.** `_send_run` saves the record inside
  the shielded task, so the record exists even when the cancel comes while
  the call returns ([01-decisions.md](01-decisions.md#paid-runs)).
- **Exit 20 and `after_submit` are accepted runs.** A failure after an
  accepted submission is exit 20 (`skill: references/recovery-and-idempotency.md`),
  and the media `--run` recovery row keeps "`partialData.items[0].nodeId`,
  `submitId`" for the read-only wait. So the pack records them from
  `partialData` and waits as usual
  ([02-dreamina-contract.md](02-dreamina-contract.md#the-clis-own-state)).
- **Every other failure is a refusal.** The CLI reports an accepted run as
  exit 0 or 20, so another exit code means the run did not start, and
  `RUN_REFUSED` says nothing was billed. Run C-16 records the codes met; if
  one follows acceptance, this rule and `RUN_REFUSED` change.
- **The run reply's own state.** The pack records every exit 0 (02's run
  reply: `node`, `mutation`, `quote`, `approval`, and `submission`). A run
  Dreamina refused after its reply ends at the first wait as a failed
  generation, which deletes the record (run C-7 records the reply's
  `submission.state`).
- **Uncertain runs are never recorded.** The owner rejected records of
  uncertain jobs (O `6340e4a`). `RUN_UNCERTAIN` sends the person to the
  canvas instead.

The module ends with `__all__ = ["CollectOperation", "GenerationOperation"]`.
It stays under 300 lines because the wait and the lost-reply check live in
`waiting.py`.

## Step 15: Run wrapper

Port `F/src/comfy/execution.py` to `src/comfy/execution.py`, with the
docstring "Run Dreamina operations with ComfyUI's progress bar and its
cancel." Changes:

- `_wait_shielded` and `wait_for_thread(work)` are F's, unchanged
  (`F/src/comfy/execution.py:22-41`).
- `wait_for_request` becomes `wait_for_run(task)`, with the docstring
  "Forward ComfyUI's cancel to the owned asyncio task that runs an
  operation." Its loop is F's (`F/src/comfy/execution.py:44-54`): it checks
  `throw_exception_if_processing_interrupted()` every
  `CANCELLATION_POLL_SECONDS`, and in `finally` cancels and gathers the task
  when it is not done. One change: when that gather returns a `DreaminaError`
  whose code is `INTERRUPTED`, it is raised in place of ComfyUI's
  `InterruptProcessingException`, so its message shows. ComfyUI shows no
  text for an interrupt (`C/execution.py:618-626`, `:692-699`), and the
  person must learn that the generation keeps running and is billed.
- `send_request` becomes `send_run(operation, build_outputs, node_id)`. It
  builds `progress = functools.partial(ComfyAPI().execution.set_progress,
  max_value=PROGRESS_STEPS["TOTAL"], node_id=node_id)` when `node_id` is not
  `None`, else `None`, and:
  1. sets progress 0;
  1. reads the configuration snapshot in a thread
     (`get_runtime().configuration.read_snapshot`);
  1. runs `operation.validate(configuration.settings)`;
  1. awaits `operation.send(configuration, progress)` through
     `wait_for_run`; the operation reports the steps it reaches;
  1. builds the outputs through `wait_for_thread`;
  1. sets progress `PROGRESS_STEPS["TOTAL"]`.
- F's two conversions in `send_request` go (`F/src/comfy/execution.py:75-81`).
  An `INTERRUPTED` error is shown as it is, as above. No stray
  `TimeoutError` reaches `send_run`: `send_command` turns its own timeout
  into `CLI_TIMEOUT`, and the wait turns the deadline into `WAIT_LIMIT`.

A node that another node or pack calls has no ID, so it leaves the calling
node's bar alone, as in F. The module ends with
`__all__ = ["send_run", "wait_for_run", "wait_for_thread"]`.

## Step 16: Node base

Port `F/src/nodes/base.py` to `src/nodes/base.py`, with the docstring "Share
the cache key, the run number, and the list inputs of the paid nodes."
`PaidNode(io.ComfyNode)` is F's, with B's list handling
(`B/src/nodes/base.py:22-52`, `:94-102`):

```python
class PaidNode(io.ComfyNode):
    """Own the cache key, the run-number input, and the list inputs every paid node shares.

    Attributes:
        send: Typed entry point that receives every saved input except the run number.
        list_inputs: The media inputs of the node; each reaches send as the whole list, and every other input as its
            one value.

    """

    send: ClassVar[Callable[..., Awaitable[io.NodeOutput]]]
    list_inputs: ClassVar[frozenset[str]] = frozenset()
```

| Member | Does |
| ------ | ---- |
| `fingerprint_inputs(cls, **_inputs)` (async classmethod) | Adds the signed-in account's token to the cache key, as [05-foundation.md](05-foundation.md#step-13-settings-schema-and-store) describes: `snapshot = await asyncio.to_thread(store.read_snapshot)`; return `snapshot.account` when it is set; otherwise `account = await read_account()` and return `await asyncio.to_thread(store.create_account_token, account.user_id, snapshot.account_changes)` |
| `execute(cls, **inputs)` (async classmethod) | Drops `INPUT_NAMES["RUN_NUMBER"]`, reads every input not in `list_inputs` with `_read_single`, and calls `send` |

The private `_read_single(name: str, value: object) -> object` is B's less
its dynamic-dropdown branch, which no Dreamina node needs: a value that is
not a `list` is returned as it is; a list must hold exactly one item, which
is returned; any other list raises `SINGLE_VALUE` with `INVALID_INPUT`,
formatted with `name`.

- **The account token** follows the account, not a key
  ([01-decisions.md](01-decisions.md#sign-in-and-privacy)). A signed-out read
  raises the sign-in error, as F's `fingerprint_inputs` raised without a key
  (`F/src/nodes/base.py:25-29`). ComfyUI then gives the node a cache key
  that never matches, so it runs, and its own checks refuse it with the
  sign-in message (`C/execution.py:96-102`).
- **Plain values pass.** Inside ComfyUI a node with input lists receives
  every input as a list (`C/execution.py:319-320`). A call from Python
  passes plain values for everything but the media lists
  ([23-live-shopping-provider.md](23-live-shopping-provider.md#calling-a-paid-node-from-python)),
  and both work.
- **Upscale** uses the same base: its `images` socket is a list input
  ([12-node-upscale.md](12-node-upscale.md)).

`base.py` holds `PaidNode` only, and its `__all__` is `["PaidNode"]`.

## Step 17: Node outputs

Create `src/nodes/outputs.py`, with the docstring "Fill a Dreamina node's
outputs from what its generation made."

| Function | Does |
| -------- | ---- |
| `build_result_document(result: GenerationResult) -> dict[str, Json]` | `{"canvas": result.canvas_url, "requestId": result.request_id, "node": result.node}`, without the keys whose value is `None` |
| `build_node_outputs(result: GenerationResult, output_ids: Sequence[str]) -> io.NodeOutput` | One value per ID, in the order given, as below |

| Output ID    | Value |
| ------------ | ----- |
| `images`     | `decode_images` of the contents of every `image` file, in order: a list of `[1, H, W, 3]` tensors ([07-media.md](07-media.md#decoding)) |
| `video`      | `decode_video(content)` of every `video` file, as a list |
| `audio`      | `decode_audio(content)` of every `audio` file, as a list |
| `references` | One file: `(Reference(origin="node", value=record.node_id, media=file.kind, title=result.title),)`. Several: one `Reference(origin="resource", value=file.resource_id, media=file.kind, title=result.title)` per file, in order. None: empty. |
| `result`     | `json.dumps(build_result_document(result), indent=2, ensure_ascii=False)` |

- Only the outputs the node shows are decoded, as F's builder does
  (`F/src/nodes/outputs.py:24-43`).
- An empty list or an empty `references` tuple becomes
  `ExecutionBlocker(None)` from `comfy_execution.graph`, so connected nodes
  are skipped. `result` is always filled
  ([01-decisions.md](01-decisions.md#outputs)).
- **References** follow [01-decisions.md](01-decisions.md#references): a
  one-output node goes on as `--ref node:<id>`, which keeps the canvas edge;
  several outputs go on as `--ref res:<uuid>` each, so the next node gets
  every output, not only the node's selected one.
- **`result`** is the node as `node show` returned it, unchanged, plus the
  canvas link and the run call's request ID, which the skill keeps "for
  support" (`skill: SKILL.md#hard-boundaries`). Generation: Download has no
  request ID, and a record from a replaced canvas has no link.
  [12-node-upscale.md](12-node-upscale.md)'s output builder writes a list of
  `build_result_document` objects, one per source.
- The run wrapper calls the function in a worker thread
  ([Step 15](#step-15-run-wrapper)), so decoding never blocks the loop.

The module ends with `__all__ = ["build_node_outputs", "build_result_document"]`.

## Step 18: Generate node

Fill `src/nodes/generate.py`, which [03-repository-setup.md](03-repository-setup.md)
made a docstring-only stub, with the docstring "The paid node every
generation node is: any Dreamina model of its kind, named by its canonical
name, and one run." `GenerateNode(PaidNode)`:

```python
class GenerateNode(PaidNode):
    """Run one generation with any Dreamina model of the node's kind and fill the node's outputs.

    Attributes:
        kind: What the node's models make; a model of another kind is refused before paying.
        display_name: The node's name in menus, also sent as the canvas node's title when the prompt is empty.
        default_ceiling: The starting credit_ceiling: the default model's quote at its starting arguments.
        outputs: The node's output sockets in order; build_node_outputs fills them by ID.

    """

    kind: ClassVar[Kind]
    display_name: ClassVar[str]
    default_ceiling: ClassVar[int]
    outputs: ClassVar[tuple[io.Output, ...]]
```

Members:

| Member | Does |
| ------ | ---- |
| `build_schema(cls, *, category: str, description: str) -> io.Schema` (classmethod) | The schema every kind node returns from its `define_schema`: `node_id=f"{NODE_PREFIX}{cls.__name__}"`, `display_name=cls.display_name`, the category and description, the inputs below, `outputs=list(cls.outputs)`, `is_input_list=True`, and `hidden=[io.Hidden.unique_id]`. No `is_api_node`. |
| `validate_inputs(cls, model: object = None, prompt: object = None, arguments: object = None) -> bool \| str` (async classmethod) | The checks [06-model-check.md](06-model-check.md#step-6-the-queue-time-check) fixes, below |
| `send(cls, *, model: str, credit_ceiling: int, prompt: str = "", arguments: str = "", references: tuple[Reference, ...] \| None = None, images: list[torch.Tensor] \| None = None, videos: list[Input.Video] \| None = None, audio: list[Input.Audio] \| None = None) -> io.NodeOutput` (async classmethod) | The run, below |

Inputs, in this order: the media sockets the node shows, then `references`,
then the widgets, the text boxes last, as
[01-decisions.md](01-decisions.md#the-inputs-of-a-paid-node) fixes:

| ID               | Declaration |
| ---------------- | ----------- |
| `images`         | `io.Image.Input(INPUT_NAMES["IMAGES"], optional=True, tooltip=TOOLTIPS["IMAGES"])`, when `INPUT_NAMES["IMAGES"]` is in `cls.list_inputs` |
| `videos`         | `io.Video.Input(INPUT_NAMES["VIDEOS"], optional=True, tooltip=TOOLTIPS["VIDEOS"])`, when in `cls.list_inputs` |
| `audio`          | `io.Audio.Input(INPUT_NAMES["AUDIO"], optional=True, tooltip=TOOLTIPS["AUDIO"])`, when in `cls.list_inputs` |
| `references`     | `io.Custom(SOCKET_TYPES["REFERENCES"]).Input(INPUT_NAMES["REFERENCES"], optional=True, tooltip=TOOLTIPS["REFERENCES"])` |
| `model`          | `io.String.Input(INPUT_NAMES["MODEL"], default=DEFAULT_MODELS[cls.kind], tooltip=TOOLTIPS["MODEL"])` |
| `credit_ceiling` | `io.Int.Input(INPUT_NAMES["CREDIT_CEILING"], default=cls.default_ceiling, min=CREDIT_CEILING_RANGE["MIN"], max=CREDIT_CEILING_RANGE["MAX"], tooltip=TOOLTIPS["CREDIT_CEILING"])` |
| `run_number`     | `io.Int.Input(INPUT_NAMES["RUN_NUMBER"], default=RUN_NUMBER["DEFAULT"], min=RUN_NUMBER["MIN"], max=RUN_NUMBER["MAX"], tooltip=TOOLTIPS["RUN_NUMBER"])` |
| `prompt`         | `io.String.Input(INPUT_NAMES["PROMPT"], default="", multiline=True, tooltip=TOOLTIPS["PROMPT"])` |
| `arguments`      | `io.String.Input(INPUT_NAMES["ARGUMENTS"], default=DEFAULT_ARGUMENTS[cls.kind], multiline=True, tooltip=ARGUMENTS_TOOLTIPS[cls.kind])` |

The names and values are 06's (`src/config/inputs.py` and
`src/config/models.py`). Each kind node sets `default_ceiling` from
`DEFAULT_CEILINGS[<kind>]`, its default model's quote at its starting
`arguments`, rounded up to the next 10
([01-decisions.md](01-decisions.md#credits)). `GenerateNode` reads the class
attribute, not `DEFAULT_CEILINGS`, because each key arrives with its node's
milestone. `references` is one socket, read as its one value; the media
sockets are lists.

`validate_inputs`, as 06 fixes it:

1. ComfyUI calls a node with input lists once, with each value as a list
   (`C/execution.py:194`, `:319-320`), and a linked input as `(None,)`
   (`C/execution.py:177`). The private `_read_queued(value) -> str | None`
   returns the one item of a list or tuple that holds exactly one `str`, the
   value itself when it is a `str`, and `None` otherwise.
1. `model` reads as `None`: return `True`.
1. `await validate_cli()`.
1. `values = parse_arguments(arguments)` when `arguments` reads as text,
   else an empty object.
1. `listed = await find_model(model, cls.kind)`.
1. `validate_argument_names(listed, values)`.
1. `choose_prompt(prompt, values)` when `prompt` reads as text.
1. Return `True`, or the `DreaminaError`'s message, which ComfyUI shows
   against the node. A failed read, such as a signed-out list, is returned
   the same way.

The validator names only `model`, `prompt`, and `arguments`, all text inputs
with no range, and takes no `**kwargs`: ComfyUI skips its own checks only
for the inputs a validator names (`C/execution.py:1019`), so `credit_ceiling`
and `run_number` keep their range checks. ComfyUI awaits an async validator
(`C/execution.py:1091`).

`send`:

1. `node_id = cls.hidden.unique_id if cls.hidden is not None else None`, as
   F (`F/src/nodes/endpoint.py:108`).
1. `local = list_local_media(images or (), videos or (), audio or ())`
   ([07-media.md](07-media.md#splitting-and-encoding)): one item per image
   frame, video, and audio clip, numbered per kind for the placeholders.
1. Build `GenerationPlan(kind=cls.kind, title=cls.display_name,
   model=model.strip(), prompt=prompt, arguments=arguments,
   credit_ceiling=credit_ceiling, references=references or (),
   local=local)`.
1. Return `await send_run(GenerationOperation(plan, runtime.generations,
   runtime.canvas, encode_local_file), partial(build_node_outputs,
   output_ids=…), node_id)`, where `output_ids` are the IDs of `cls.outputs`.
   The operation makes every check again, because a linked input and a
   direct call skip `validate_inputs`; the CLI validation and the model read
   are cached, so this costs nothing after the first run.

`list_local_media` runs in the node, on the loop: it only slices tensors.
The encoding, which blocks, runs in 07's `send_media` in a worker thread.

A kind node is then only its settings and outputs. For example
([10-node-video.md](10-node-video.md) fixes its own):

```python
class VideoGenerate(GenerateNode):
    """Generate a video with any Dreamina video model."""

    kind = "video"
    display_name = "Video: Generate"
    default_ceiling = DEFAULT_CEILINGS["video"]
    list_inputs = frozenset({INPUT_NAMES["IMAGES"], INPUT_NAMES["VIDEOS"], INPUT_NAMES["AUDIO"]})
    outputs = (
        io.Video.Output("video", display_name="video", is_output_list=True),
        io.Custom(SOCKET_TYPES["REFERENCES"]).Output("references", display_name="references"),
        io.String.Output("result", display_name="result"),
    )

    @classmethod
    @override
    def define_schema(cls) -> io.Schema:
        """Describe the node: its name, its menu, and its inputs."""
        return cls.build_schema(category=MENUS["VIDEO"], description="…")
```

In the same change, `HOST_NODE_BASES` in
`quality/config/repository/functions.py` gains
`"src.nodes.generate.GenerateNode"`, with the comment "The paid nodes reach
ComfyNode through PaidNode, and the kind nodes through GenerateNode.", as
[03-repository-setup.md](03-repository-setup.md) says. The quality check
exempts a host hook only on a class whose direct base is listed
(`F/quality/repository/functions/python.py:272-277`), and each kind node's
`define_schema` is one statement.

### Calls from another pack

[23-live-shopping-provider.md](23-live-shopping-provider.md#calling-a-paid-node-from-python)
calls the generation nodes from Python. A direct call works under this
contract:

- Look the class up by node ID in `nodes.NODE_CLASS_MAPPINGS`, such as
  `DreaminaVideoGenerate`, clone it with `PREPARE_CLASS_CLONE(None)`, give
  it an empty hidden holder, and `await clone.execute(**inputs)`.
- `model`, `prompt`, `arguments`, `credit_ceiling`, `run_number`, and
  `references` may be plain values or one-item lists; `images`, `videos`,
  and `audio` are Python lists of ComfyUI media, in order.
- `validate_inputs` is not called; `send` makes the same checks before
  anything is uploaded or paid.
- The node shows no progress bar, because the clone has no node ID.
- The result is an `io.NodeOutput` whose values are the outputs in the
  node's order.
- A cancel after acceptance raises `DreaminaError` with `INTERRUPTED`; a
  cancel before it raises ComfyUI's `InterruptProcessingException`.

The module ends with `__all__ = ["GenerateNode"]`.

## Step 19: Allowlist and commits

`repo:lint:policy` refuses a public module-level function no other module
names (`python.module-only-public`,
`F/quality/repository/functions/names.py:68-87`). Each public function no
other module calls yet gets an exact entry in the `allowlist` of
`quality/config/repository/functions.json`, one entry per file, with the
reason "Called by a node built in a later milestone.", and the named plan
removes each name with its first call, and the entry with its last name.

| Milestone | File | Names | Removed by |
| --------- | ---- | ----- | ---------- |
| Foundation (Part A) | `src/dreamina/contract.py` | `validate_cli` | This plan's Part B ([Step 14](#step-14-generation-operation)) |
| Media and runs (Part B) | `src/dreamina/generations/records.py` | `list_generation_labels` | [14-node-download.md](14-node-download.md) |
| Media and runs (Part B) | `src/nodes/outputs.py` | `build_result_document` | [12-node-upscale.md](12-node-upscale.md) |

Every other public name of Part A is called in the Foundation milestone:
`send_command`, `parse_reply`, `find_binary`, and `build_failure` by
`contract.py` and 05's account and installer modules; `sanitize_reason` by
`failures.py`'s callers and 05's installer; `is_current_version` by 05's
status. In Part B:
`find_canvas`, `create_canvas`, `wait_for_operation`, `validate_lost_run`,
`build_generation_failure`, and `wait_until_settled` by `operation.py`;
`send_run` and `build_node_outputs` by `generate.py`; `wait_for_run` and
`wait_for_thread` by `send_run`; and 07's functions by `operation.py` and
`generate.py`.

Two method entries stay for good, with F's reason "The run wrapper calls it
through the Operation protocol.": `GenerationOperation.validate` and
`CollectOperation.validate` in `src/dreamina/generations/operation.py`, as
[03-repository-setup.md](03-repository-setup.md) names them.

Commits, as [README.md](README.md#build-order) names them:

- Part A goes in the Foundation milestone's commit,
  `feat(nodes): add the settings, sign-in routes and extension loading`,
  with [05-foundation.md](05-foundation.md).
- Part B goes in `feat(nodes): add uploads, runs and downloads`, with
  [07-media.md](07-media.md). No node is registered yet, so `NODE_TYPES` is
  unchanged, and the workflow checks have nothing new to find.

## Rules every node plan follows

- Class names, IDs, and categories come from
  [01-decisions.md](01-decisions.md#the-nodes):
  `node_id=f"{NODE_PREFIX}{cls.__name__}"`, `category=MENUS[…]`.
- `display_name` is `Family: Action`; there are no `search_aliases`;
  `description` is one sentence.
- Inputs show their IDs. A generation node's inputs are its media sockets
  (`images`, `videos`, `audio`), `references`, `model`, `credit_ceiling`,
  `run_number`, `prompt`, and `arguments`, in that order. Dreamina's flag
  names appear only in what a person types into `arguments`. Every output
  has a `display_name` equal to its ID, because examples and help pages link
  and name outputs that way.
- The three generation nodes subclass `GenerateNode`; set `kind`,
  `display_name`, `default_ceiling`, `list_inputs`, and `outputs`; and return
  `cls.build_schema(...)` from `define_schema`. They hold no `send`.
  Image: Upscale subclasses `PaidNode` and runs its own operation, which
  reuses `CollectOperation`. Generation: Download builds its own schema and
  calls `CollectOperation` and `build_node_outputs`.
- Every node that sends a billed run has no usage, cost, or price output, and
  no node sets `is_api_node`. The only credits a node shows are Dreamina's
  own quote in `CEILING_TOO_LOW`.
- Every refusal happens before paying: the model and text checks in
  `validate_inputs` before the workflow runs, and all of 06's and 07's checks
  in `send` before any upload. Every refusal is a constant in
  `src/config/messages/`.
- Outputs never change: every output socket is always declared, and a socket
  the result does not fill returns `ExecutionBlocker(None)`.
- Every CLI call goes through `send_command`, and every success payload
  through `parse_reply`. Every call that touches a canvas passes
  `--project-id`. No call passes `--yes`, `--use`, `--profile`, or `--wait`.
- Nothing paid is sent twice. Each run has one new submit ID and one run
  call, which is never sent again; a lost reply is checked read-only with
  `validate_lost_run`. The run number sends the same run again.
- An accepted run is recorded before the first wait, and the record stays
  through a cancel, a timeout, and any failure of a free read; Generation:
  Download collects it. A cancel after acceptance shows
  `GENERATION_KEEPS_RUNNING`.
- A paid node sends `--count 1` unless `arguments` sets `count`, never for
  audio, and `--title` only when the prompt is empty.
- Every message with a page placeholder is formatted with `**DREAMINA_URLS`.
- Every node gets a help page in `web/docs/<node id>.md`
  ([18-documentation.md](18-documentation.md)), at least one example workflow
  ([17-scripts-and-workflows.md](17-scripts-and-workflows.md)), and a row in
  the README node table; the checks fail without them.
- Each node plan ends by adding its class to `NODE_TYPES` in the order of
  [04-architecture.md](04-architecture.md#srcnodes).

## What the live runs settle

[21-test-runs.md](21-test-runs.md) runs these before the Media and runs
milestone is built. A result that differs changes this plan before building
further, and the change is recorded in
[README.md](README.md#changes-made-while-building) and
[02-dreamina-contract.md](02-dreamina-contract.md#results-of-the-contract-runs).

| Run | Settles | If it differs |
| --- | ------- | ------------- |
| C-0 (done) | Flags written `--name`; `canvas ls` with no canvases; `meta.requestId` on every reply | Recorded; `CliMeta` and Step 10 follow it |
| C-1 | The `canvas create` reply, and a second call with the same ID | `CanvasReply`, `CanvasProject`, and `create_canvas`'s one repeat |
| C-5 | Exit 10 with `minimumCreditCeiling` and `partialData.items[]` | `CreditConfirmation`, `PartialItem`, and row 1 of the failure map |
| C-7 | The run reply on acceptance without `--wait`: `node.nodeId`, `submission.submitId`, `submission.state`, and how long the call takes | `RunReply`, `RunSubmission`, and `CALL_SECONDS["RUN"]` |
| C-8 | The `operation wait` reply of a finished image: the resources' `state` word; `node show`'s resources and their `submitId` and `status` | `OPERATION_STATES["SUCCEEDED"]`, `OperationReply`, and `CollectOperation` |
| C-9 | Values the server refuses: their exit code, `class`, and `validation` | The failure map's rows 6 and 8 |
| C-14 | A video run whose wait is killed, then resumed by `operation wait` from a new process: the states and exit codes on the way | `wait_for_operation`, `OPERATION_STATES`, and `CollectOperation` |
| C-15 | The error for a canvas that does not exist, the same for an upload, a run, and an Element | The message of a canvas deleted during a run; `find_canvas` itself relies on `canvas ls` |
| C-16 | `operation status` of an unknown submit ID; every exit code met | `validate_lost_run`'s test, `OPERATION_STATES["ABSENT"]`, the rule that only exit 20 follows acceptance, and rows 7 and 9 |
| C-17 | Whether a failed generation is billed | `GENERATION_FAILED`'s text |
| V-4, D-1 | A cancel after acceptance through ComfyUI, then Generation: Download collecting the run | `GENERATION_KEEPS_RUNNING`, `wait_for_run`'s interrupt rule, and `CollectOperation` |

C-2 to C-4 (uploads and downloads), C-6 (placeholders), C-10 to C-13, and
the Element part of C-15 settle [07-media.md](07-media.md) and the node
plans.

## Names this plan uses from other plans

When an owning plan fixes a different signature, this plan's call sites
follow it, as the owner's rule for two plans says
([research/owner-rules.md](research/owner-rules.md#process-and-plans)).

| Name | Owner | Used for |
| ---- | ----- | -------- |
| `ErrorCode`, `DreaminaError`, `Json`, `Kind`, `MediaKind`, `Value`, `Reply` | [05-foundation.md](05-foundation.md) | Every module |
| `parse_json` | 05 | `send_command`'s reply parsing |
| `save_file`, `read_file` | 05 | `CanvasStore`, `GenerationStore` |
| `ConfigurationStore.read_snapshot`, `create_account_token`; `Configuration` (`settings`, `account`, `account_changes`); `Settings` (`request_timeout_seconds`, `max_upload_megabytes`, `max_download_megabytes`) | 05 | `send_run`, `PaidNode.fingerprint_inputs`, the request timeout |
| `read_account` | 05, `src/dreamina/account.py` | The account token |
| `Runtime`, `get_runtime`, `SettingsRoutes`, `register_routes` | 05 | Step 12 adds the stores; `SettingsRoutes` and `register_routes` stay as 05 builds them |
| `ENVIRONMENT_VARIABLES`, `FILE_NAMES`, `MAX_FILE_BYTES`, and the values this plan adds | 05, `src/config/storage.py` | `find_binary`, the stores |
| `VERSION_PATTERN`, `REASON_PATTERNS` (`URL`, `PATH`, `IDENTIFIER`) | 05, `src/config/patterns.py` | The version gate, reason cleaning |
| `PROGRESS_STEPS`, `CANCELLATION_POLL_SECONDS` | 05 fixes the values; Step 7 creates the file | The progress bar and the cancel poll |
| `STATE_UNREADABLE` | 05, `src/config/messages/settings.py` | `CanvasStore.read` |
| `parse_arguments(text)`, `validate_argument_names(listed, values)`, `choose_prompt(prompt, values)`, `build_flags(mode, prompt, values)` | [06-model-check.md](06-model-check.md) | The checks and the run's flags, without `--prompt` |
| `find_model(name, kind)` → `ListedModel` (`name`) | 06 | The model check and `--model` |
| `choose_mode(listed, kind, connected, values)` → `ModelMode` (`name`, `scenario`) | 06 | The mode, with `connected` the `MediaKind` of each item, in `--ref` order |
| `INPUT_NAMES`, `TOOLTIPS`, `ARGUMENTS_TOOLTIPS`, `RUN_NUMBER`, `CREDIT_CEILING_RANGE`, `DEFAULT_MODELS`, `DEFAULT_ARGUMENTS`, `SINGLE_VALUE` | 06 | `GenerateNode`'s inputs and `_read_single` |
| `DEFAULT_CEILINGS` | 06 fixes its text; [09-node-image.md](09-node-image.md), [11-node-audio.md](11-node-audio.md), and [10-node-video.md](10-node-video.md) add one key each | Each kind node's `default_ceiling` |
| `send_media(project_id, items, encode, settings, deadline)` → `tuple[Reference, ...]` | [07-media.md](07-media.md) | Uploads |
| `validate_references(mode, items, arguments)`, `plan_references(references, local, uploaded)` → `(ordered, placed)`, `format_prompt(prompt, placed)` | 07 | The reference limits, the `--ref` order, the prompt |
| `download_resources(project_id, node, submit_id, settings, deadline)` → `tuple[OutputFile, ...]` | 07 | Downloads with the byte-count and SHA-256 checks |
| `list_local_media`, `encode_local_file`, `decode_images`, `decode_video`, `decode_audio` | 07, `src/comfy/media.py` | The local items, encoding, decoding |
| `Reference` (`origin`, `value`, `media`, `title`, `typed_value`), `LocalMedia` (`media`, `value`, `position`) | 07, `src/types/references.py` | `references`, the local items, `--ref` |
| `UPLOAD_REFUSED`, `DOWNLOAD_FAILED` | 07, `src/config/messages/media.py` | 07's `context` for `build_failure` |
| Each kind node's outputs | [09-node-image.md](09-node-image.md), [10-node-video.md](10-node-video.md), [11-node-audio.md](11-node-audio.md) | `build_node_outputs` |
| `UPSCALE_FLAGS`, `UPSCALE_MODEL`, `UpscaleRequest`, the upscale codes and messages | [12-node-upscale.md](12-node-upscale.md) | Image: Upscale, reusing `CollectOperation`, `wait_until_settled`, and `validate_lost_run` |
| `TITLE_MAX_UNITS`, `NodeView.subjects` | [13-node-element.md](13-node-element.md) | Element: Add |
| `find_record`, `GENERATIONS_EMPTY`, `GENERATION_UNKNOWN`, the input ID `generation` | [14-node-download.md](14-node-download.md) | Generation: Download |
| `VoicePage` | [15-node-model-info.md](15-node-model-info.md) | Model: Info's voices |
| `HOST_NODE_BASES`, the two permanent allowlist entries | [03-repository-setup.md](03-repository-setup.md) | The function policy |
| Runs C-0 to C-17, V-4, D-1 | [21-test-runs.md](21-test-runs.md) | [What the live runs settle](#what-the-live-runs-settle) |
| The direct-call contract | [23-live-shopping-provider.md](23-live-shopping-provider.md) | [Calls from another pack](#calls-from-another-pack) |
