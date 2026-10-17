# Dreamina Contract

This plan records the Dreamina Canvas CLI behavior that the pack's code
relies on. The plans follow it in every:

- CLI call;
- reply record;
- upload and download;
- failure map.

It was read on 2026-10-16 from three sources:

- the CLI's own `schema` for release 1.0.3 (captured in
  [research/captures/schema.json](research/captures/schema.json));
- the skill installed with it (mirrored in
  [research/docs/dreamina-canvas-cli/](research/docs/dreamina-canvas-cli/SKILL.md));
- free calls to the installed binary.

No paid run has been made. Each fact that needs a run is listed in
[Facts to confirm by test runs](#facts-to-confirm-by-test-runs) with the run
in [21-test-runs.md](21-test-runs.md) that settles it.
[research/cli.md](research/cli.md) holds the evidence for each fact, with its
source.

Readers: the engineer who writes `src/dreamina/`, `src/config/dreamina.py`,
and `src/config/generations.py`, and the model check of
[06-model-check.md](06-model-check.md).

**Unconfirmed** marks a fact that no document or free call settles.

## Contents

- [How the pack calls the CLI](#how-the-pack-calls-the-cli)
- [Install, upgrade, and the version gate](#install-upgrade-and-the-version-gate)
- [Replies](#replies)
- [Exit codes and failure fields](#exit-codes-and-failure-fields)
- [Sign-in](#sign-in)
- [The account](#the-account)
- [Canvases](#canvases)
- [Model discovery](#model-discovery)
- [Voices](#voices)
- [Generation runs](#generation-runs)
- [Credit approval](#credit-approval)
- [Waiting and recovery](#waiting-and-recovery)
- [Reading a finished node](#reading-a-finished-node)
- [Uploads](#uploads)
- [Downloads](#downloads)
- [Image upscale](#image-upscale)
- [Elements](#elements)
- [The CLI's own state](#the-clis-own-state)
- [What is billed when something fails](#what-is-billed-when-something-fails)
- [Facts to confirm by test runs](#facts-to-confirm-by-test-runs)

## How the pack calls the CLI

- **Every call has the same shape:**

  ```text
  <binary> --format json --non-interactive <command> <arguments…>
  ```

  `--format` and `--non-interactive` are global flags (schema
  `globalFlags`). `--format json` makes every reply one JSON object.
  `--non-interactive` makes a call that would prompt stop instead. `--yes`
  and `--profile` are never passed.
- **The binary** is found as [01-decisions.md](01-decisions.md#the-cli-on-the-persons-computer)
  says. It is `dreamina-canvas` on macOS and Linux and `dreamina-canvas.exe`
  on Windows.
- **The environment** is the ComfyUI server's own, passed unchanged. The CLI
  needs `HOME` (or `USERPROFILE`) to find its credentials and state.
- **Input and output.** stdin is closed. stdout and stderr are read whole,
  each up to `REPLY_BYTES`.
- **Arguments** are passed as a list, never through a shell. A prompt with
  quotes, newlines, or `$` needs no escaping.
- **A literal `{{`** in a prompt is written `\{{`
  (schema `node create video` `--prompt`). The pack never adds or removes
  that escape. It sends the person's prompt as written, apart from its own
  placeholders ([01-decisions.md](01-decisions.md#placeholders)).

## Install, upgrade, and the version gate

- **Install** ([research/cli.md](research/cli.md#release-and-install)):

  | System       | Installer                                                  | Run as                                                                 | Installs to                           |
  | ------------ | ---------------------------------------------------------- | ---------------------------------------------------------------------- | ------------------------------------- |
  | macOS, Linux | `https://dreamina.capcut.com/canvas-cli/install.sh`        | `bash <file>`                                                          | `~/.local/bin/dreamina-canvas`        |
  | Windows      | `https://dreamina.capcut.com/canvas-cli/install.ps1`       | `powershell.exe -NoProfile -ExecutionPolicy Bypass -File <file>`       | `%USERPROFILE%\bin\dreamina-canvas.exe` |

  - Each address answers 301 to `/canvas-cli/install/install.sh` (or
    `.ps1`) on the same host, then 302 to the release on ByteDance's CDN,
    `sf16-web-login-neutral.capcutstatic.com` (read on 2026-10-17). The pack
    follows at most three redirects and keeps the script only from HTTPS on a
    CapCut domain.
  - The installer honors `DREAMINA_CANVAS_INSTALL_DIR`. It keeps the folder
    of a `dreamina-canvas` already on `PATH`. It also installs the skill
    under `~/.agents/skills/dreamina-canvas-cli`; the pack never reads the
    skill.
  - Windows supports only `AMD64`.
- **Version.** `version` returns
  `{"version","commit","buildTime","edition","distribution","releaseDate","releaseNotes"}`.
  The pack compares `version` with `MINIMUM_VERSION` (`1.0.3`) as dotted
  numbers.
- **Schema.** `schema` returns the command tree (`subcommands[]`, each with
  `name`, `flags[]`, `declaredExitCodes`, and `successData`). The pack checks
  that every command path and flag in `REQUIRED_COMMANDS` exists. The list is
  in [08-runs.md](08-runs.md#step-1-cli-constants).
- **Upgrades are pushed by the server.** An old client gets a failure with
  `error.requiredAction` `upgrade`, and possibly
  `clientUpgrade.installCommands` or `upgradeUrl`
  ([research/cli.md](research/cli.md#release-and-install)). The pack never
  runs a command taken from a reply. **Update** in the settings dialog runs
  the same fixed installer as **Install**.

## Replies

- **Success:** exit code 0, and one object on stdout:

  ```json
  { "schemaVersion": "1", "ok": true, "data": { "...": "..." } }
  ```

- **Failure:** a non-zero exit code, nothing on stdout, and one object on
  stderr:

  ```json
  {
      "schemaVersion": "1",
      "ok": false,
      "error": {
          "code": "cli.authentication_required",
          "class": "auth_required",
          "message": "Authentication is required. Run auth login and retry.",
          "retryable": false,
          "requiredAction": "login"
      }
  }
  ```

  (captures: `version.json`, `error-auth-required.json`,
  `error-invalid-flag.json`, `error-login-wait-timeout.json`)

- **A failure can also carry, next to `error`:**
  - `creditConfirmation`;
  - `partialData`;
  - `clientUpgrade`;
  - `meta.requestId`.

  `error` itself can carry `reason`, `validation`, and `localStorage`
  ([research/cli.md](research/cli.md#the-json-envelope)).
- **Reading a reply.** The pack reads every reply with Pydantic `Reply`
  records (`extra="ignore"`), so new fields from a later release change
  nothing. A reply that is not one JSON object, or whose `ok` disagrees with
  the exit code, is an invalid reply: `UNCERTAIN` for the run call,
  `TRANSPORT` for any other call.

## Exit codes and failure fields

The map in [08-runs.md](08-runs.md#step-4-failures) reads these fields only,
never `error.message`:

| Exit | Meaning                                                                 | Evidence                                    |
| ---- | ----------------------------------------------------------------------- | ------------------------------------------- |
| 0    | Success                                                                 | captures                                    |
| 2    | Invalid input, refused locally; nothing was sent                        | `error-invalid-flag.json` (`cli.invalid_flag`, class `invalid_input`) |
| 10   | Confirmation required; the node is saved and nothing was charged        | skill, credits page                         |
| 11   | Sign-in required (`requiredAction` `login`)                             | `error-auth-required.json`                  |
| 20   | Operation incomplete (`requiredAction` `resume`)                        | `error-login-wait-timeout.json` (`cli.login_wait_timeout`); skill, recovery page |
| 1, 12, 13, 21, 22 | **Unconfirmed**; declared in the schema                    | schema `declaredExitCodes`                  |

The fields that decide a message, in this order:

1. **The exit code**, for 2, 10, 11, and 20.
1. **`error.requiredAction`**: `login`, `confirm`, `resume`, `upgrade`, or
   `none`.
1. **`error.class`**: seen so far `invalid_input`, `auth_required`, and
   `operation_incomplete`.
1. **`error.code`**: the codes the pack maps by name are in
   [research/cli.md](research/cli.md#the-json-envelope).
1. **`error.reason`**, for network and credential-store failures.
1. **`error.validation.reasonCode`, `fieldPath`, `detail`.** `detail` is
   added to the message, cleaned. It is never matched.
1. **`error.retryable`**: says whether a free read may be tried again. It is
   never used for the run call.

Exit codes 1, 12, 13, 21, and 22 have no message of their own. Their
`class`, `requiredAction`, and `code` decide, and an unknown combination gets
the general message with the cleaned `error.message`. The test runs record
each code met
([21-test-runs.md](21-test-runs.md#part-1-contract-checks), run C-16).

## Sign-in

| Call                                                     | Reply `data`                                                                                   |
| -------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| `auth status`                                            | `loggedIn`, `profile`, `region`, `environment`, `authMode`, `distribution`, `version`, `edition`; signed in also `expiresAt`, `credentialStorage` |
| `auth login`                                             | `status` (`authorization_required`), `challenge` (`deviceCode`, `userCode`, `verificationUri`, `verificationUriComplete`, `pollSeconds`, `expiresAt`), and the same profile fields |
| `auth wait --device-code <code> --timeout <duration>`    | On approval: `status` and `state.loggedIn` `true`. Wait ran out first: exit 20, `cli.login_wait_timeout` (wait again with the same code). Challenge expired: exit 11, `cli.login_expired` (start a new sign-in) |
| `auth logout`                                            | `loggedOut`                                                                                    |

- **`auth status` reads only local state.** The pack uses it for the dialog,
  where a network failure must not hide the sign-in state.
- **`--timeout` is a Go duration** such as `540s`. A bare number is refused
  with `cli.invalid_flag`, exit 2.
- **The challenge lasted 10 minutes** in both captures. The pack waits until
  `expiresAt`.
- **The device code is kept in memory only.** It never reaches the browser
  or a file.
- **What approval returns.** `auth wait` exits 0 with `status` `logged_in`
  and `state` `{loggedIn: true, expiresAt, credentialStorage: "keyring"}`.
  Confirmed by the owner's sign-in on 2026-10-16. The credentials lasted
  about 60 days.

## The account

- **`auth account`** reads the account from the service: `userId` (integer),
  `isVip` (boolean, optional), and `vipLevel` (string, optional) (schema
  `auth account`).
- **Signed out,** it fails with exit 11.
- **No balance.** It holds no credit balance. No command in 1.0.3 returns
  one.
- **How the pack uses it:**
  - it hashes `userId` into the cache token;
  - it shows `vipLevel` in the dialog when present;
  - it never writes `userId` to disk or sends it to the browser.

## Canvases

| Call                                                          | Reply `data`                                                                                 |
| ------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| `canvas create ComfyUI --project-id <uuid>`                   | `project` (`projectId`, `name`, `createdAt`, `updatedAt`, `webUrl`), `draftVersion`, `current`; optional `localStorageWarning` |
| `canvas ls --limit 100 [--cursor <c>]`                        | `items[]` (`projectId`, `name`, `createdAt`, `updatedAt`, `webUrl`), `nextCursor`, `hasMore` |

- **The client-made `--project-id`.** A lost reply can be resolved by
  creating again with the same ID, which the CLI documents for retries.
- **No `--use`.** The pack never passes it, so the CLI's current canvas never
  changes.
- **A canvas that is gone.** A save or upload to it fails. The skill says a
  missing, forbidden, or unlinked ID all return "the **same** error"
  ([research/cli.md](research/cli.md#references-and-placeholders)), so an
  error code cannot tell a deleted canvas from a missing reference. The pack
  therefore checks for the saved canvas in `canvas ls` before each run
  ([08-runs.md](08-runs.md)). Run C-15 records the error a deleted canvas
  gives.

## Model discovery

`model list --type <kind>` (`kind` is `image`, `video`, or `audio`) returns
`items[]`. Each item:

| Field                         | Type              | Use                                                                         |
| ----------------------------- | ----------------- | --------------------------------------------------------------------------- |
| `type`                        | string            | The kind; checked against the node's kind                                   |
| `model`                       | string            | The canonical name, sent as `--model`                                       |
| `aliases`                     | string[]?         | Matched like `model`, never sent                                            |
| `modes[].name`                | string            | `t2i`, `i2i`, `t2v`, `first_last_frame`, `m2v`, `tts`, `music`              |
| `modes[].scenario`            | string?           | For `tts`: `text-reading` or `omni-dubbing`                                 |
| `modes[].flags[].flag`        | string            | A flag the CLI accepts for this mode                                        |
| `modes[].flags[].required`    | boolean           | Must be set                                                                 |
| `modes[].flags[].values`      | string[]?         | Allowed values                                                              |
| `modes[].flags[].min`, `max`, `step` | number?    | Numeric bounds                                                              |
| `modes[].flags[].minLength`, `maxLength` | integer? | Text length bounds                                                         |
| `modes[].references.min`, `max` | integer         | The total number of references                                              |
| `modes[].references.types[]`  | `mediaType`, `min`, `max` | Per media type                                                      |
| `modes[].references.requireAnyOfTypes` | string[]? | At least one of these types                                                |
| `modes[].references.mutuallyExclusiveTypes` | string[]? | Not together                                                          |
| `modes[].vipRequired`         | boolean?          | Shown by Model: Info                                                        |
| `modes[].vipResolutions`      | string[]?         | Shown by Model: Info                                                        |

The skill's rules for these fields:

- "`flags` contains only flags that the current CLI actually accepts and
  whose dynamic constraints came from the live generation specification."
- An omitted `references` means the mode takes none; `types: []` means no
  type is enabled.

The owner's capture of 2026-10-16 (`model-list-image.json`,
`model-list-video.json`, `model-list-audio.json`) settled the flag format
([research/catalog.md](research/catalog.md#what-the-lists-show)):

- **`flag` is written with two dashes,** such as `--ratio`.
- **The flags that appear** are `--prompt`, `--ratio`, `--resolution`,
  `--duration`, `--count`, `--voice-name`, and `--scenario`.
- **`ratio`, `resolution`, and `duration` are marked required** wherever they
  appear, with no default in the list.
- **One mode name can appear more than once with different `references`.**
  Video `first_last_frame` appears once with exactly two images and once with
  exactly one.

The pack strips the dashes for `arguments` keys (`ratio`, `voice-name`), and
writes `--<name>` back when it builds the call.

`model find <name> [--type <kind>]` returns the same shape. The pack does not
use it: one `model list` per kind gives every name to match, and the pack
matches exactly ([01-decisions.md](01-decisions.md#checking-a-model-before-paying)).
`model <canonical>` gives one model's full specification under
`matches[].generation`:

- per media type: file size, pixel size, and duration limits;
- `maxBatchGenCount`;
- `isVip` and `vipConfigs`;
- the service's own parameter names.

Model: Info shows the `model list` shape, which is what the pack checks
against, plus these limits and membership fields from `model <canonical>`,
under the CLI's flag names
([15-node-model-info.md](15-node-model-info.md)). The run check does not
refuse on the limits: the server refuses an oversized file at save, before
any charge.

## Voices

`voice list --model <canonical> --offset <n> --count 100` returns:

```text
models: { <model>: { items[].voiceName, hasMore, nextOffset, totalCount } }
```

- The pack repeats the call with `--offset <nextOffset>` until `hasMore` is
  false.
- `voiceName` goes unchanged to `--voice-name`.
- A model with no voice catalog fails ("explicit unsupported routes fail").
  Model: Info then shows no voices.

## Generation runs

The run call:

```text
node create <kind> --project-id <canvas> --mode <mode> [--scenario <s>]
  --model <canonical> [--prompt <text>] [--ref <type:value>]…
  [--<flag> <value>]… [--count 1] [--title <text>]
  --run --submit-id <uuid> --credit-ceiling <n>
```

- **Kinds and flags.** `<kind>` is `image`, `video`, or `audio`. The flags
  each kind accepts are in [research/cli.md](research/cli.md#generation-nodes).
- **No `--wait`.** It is not passed, so the call returns after acceptance.
- **No `--node-id` or `--update-id`.** The CLI generates them. The reply
  carries the node ID.
- **`--mode` is always passed** (`cli.generation_mode_required` otherwise,
  exit 2).
- **`--title` is passed only with an empty prompt**
  (`cli.generation_title_required` otherwise).
- **`--count` is passed only for image and video.** Audio has no `--count`:
  "All audio workflows produce one output".

The success reply's `data` (schema `node create video` `successData`):

- `node`: the saved node view;
- `mutation`: `action`, `savedDraftVersion`, `effectiveGeneration`,
  `generationDiff`;
- with `--run`: the run items.

With `--run`, the schema adds:

- `quote`: `maxCredits`, `draftVersion`, `confirmable`,
  `confirmationRequired`;
- `approval`: `creditCeiling`;
- `submission`: `submitId`, `state`, `resources[]`, `error`,
  `localStorageWarning`.

The node ID is `node.nodeId`. The pack needs the node ID, `submission.state`,
and `submission.error`. The values of `submission.state` on acceptance are
**unconfirmed** (run C-7).

**Modes and references** ([research/cli.md](research/cli.md#generation-nodes)):

- `t2v` takes no reference at all.
- `first_last_frame` takes one or two image references, first frame then
  last; two must share their aspect ratio.
- `m2v` takes images, videos, audio, and Elements within the model's limits.
- `t2i` takes only Text references, which the pack never sends. So `t2i`
  gets none.
- `i2i` needs at least one image, Element, or image resource.
- Audio:

  | Purpose                  | Flags                                                                  |
  | ------------------------ | ---------------------------------------------------------------------- |
  | Text reading             | `--mode tts --model <m> --scenario text-reading --voice-name <voice>`; no references |
  | Omni dubbing             | `--mode tts --model <m> --scenario omni-dubbing`; image, audio, or Element references within the spec |
  | Music                    | `--mode music --model <m> --duration <seconds>`; no voice, scenario, or references |

  Every paid node sends a model. The CLI also accepted `--voice-name` for
  omni dubbing in Part 0, but the list does not show it there, so the pack
  does not send it.

**References:**

- `--ref node:<node-id>` for a node.
- `--ref res:<uuid>` for an uploaded resource; the canonical lowercase UUID
  only.
- Prompt placeholders `{{node:<node-id>}}` and `{{res:<uuid>}}`. The `res:`
  form in prompts is named by the flag description and is **unconfirmed** for
  uploads (run C-6).
- "If the same node appears in both a prompt placeholder and `--ref`, it is
  merged into one reference slot".

## Credit approval

- **The ceiling.** `--credit-ceiling <n>` (integer, at least 0) with `--run`:
  the run goes ahead only when Dreamina's latest quote is at most `n`. It
  excludes `--credit-token`.
- **Exit 10.** Above the ceiling, the call exits 10:

  ```json
  {
      "ok": false,
      "error": { "code": "cli.generation_confirmation_required", "requiredAction": "confirm" },
      "creditConfirmation": { "reason": "unconfirmed", "minimumCreditCeiling": 120 },
      "partialData": { "items": [{ "nodeId": "node_xxx", "submitId": "uuid" }] }
  }
  ```

  The node is saved, and nothing was charged
  ([research/cli.md](research/cli.md#credits)).
- **No price.** An absent `minimumCreditCeiling` means Dreamina could not
  price the run (`occupancy_unknown`). The pack then says the price is
  unknown and does not suggest a number.
- **A free price check.** With `--credit-ceiling 0`, any priced run stops at
  exit 10 with its price, and nothing is charged. The test runs use this for
  a free price check of every model
  ([21-test-runs.md](21-test-runs.md#part-0-free-reads-and-the-price-sweep)).
  The pack itself never sends 0 on purpose. The node's minimum is 0 because
  the CLI allows it, and a person may use it the same way.
- **The draft stays.** The saved draft of a run stopped at exit 10 stays on
  the canvas. The pack does not reuse it.

## Waiting and recovery

| Call                                                               | Reply                                                                                        |
| ------------------------------------------------------------------ | -------------------------------------------------------------------------------------------- |
| `operation wait <submitId> --project-id <canvas> --timeout 15s`    | Terminal: exit 0 with `operationRef`, `state`, `resources[]` (`resourceId`, `state`, `width`, `height`, `format`, and on failure `serviceCode`, `retryable`, `requiredAction`), `submission`, `submissionError`. Still running: exit 20 |
| `operation status <submitId> --project-id <canvas>`                | The same fields, from one query                                                              |

- **Always `--project-id`.** The pack always passes it, so the wait works
  even when the CLI's own journal is gone ("needed only when the local
  recovery record is missing").
- **Exit 20 is not a failure for the pack.** It is the normal "still
  running" answer of a short wait. The loop calls again. "A new read-only
  `operation wait` with the returned submit ID is safe."
- **The state values** (`state` of the operation and of each resource) are
  **unconfirmed** (runs C-7, C-8, C-14). The skill names `accepted`,
  `rejected`, and `unknown` on the run axis, and `pending`, `running`,
  `succeeded`, and `failed` on the resource axis. `OPERATION_STATES` in
  `src/config/generations.py` takes the values the runs record.
- **Completion.** A terminal state with at least one resource whose state is
  the success value is a success. A terminal state with none is a failure,
  mapped from `submissionError` or the failed resource's
  `serviceCode` and `requiredAction`. "An empty resource set is not 'all
  succeeded.'"
- **`submission.state` `absent`.** It means the server has no record, which
  "can have expired". It never proves nothing ran. Generation: Download
  deletes such a record with a message that sends the person to the canvas.
- **No cancel.** There is no cancel command. Deleting a node "does not ...
  cancel accepted generation tasks or refund credits".

## Reading a finished node

`node show --project-id <canvas> --node-id <node>` returns `nodes[]`. Each
item carries `nodeId`, `result`, `node`, `errorCode`, and `errmsg`, and
`node` carries:

- `resources[]`: `resourceId`, `type`, `status`, `name`, `errorCode`,
  `submitId`, `createdAt`, `canRegenerate`, `source`, `creditsAmount`;
- `generation`: `mode`, `prompt`, `model`, `ratio`, `resolution`,
  `outputCount`, `durationSeconds`, `scenario`, `voiceName`, `references[]`,
  `promptParts[]`;
- `upstreamNodeIds`, `layout`, `title`, `status`, `resourceObservedAtMs`.

The pack downloads the resources of the run's submit ID, in order. Every
resource of the node carries `submitId`. The whole `node` goes into `result`
([01-decisions.md](01-decisions.md#outputs)).

## Uploads

```text
resource upload --project-id <canvas> --file <path> --type <image|video|audio> --resource-id <uuid>
```

- **The reply.** It returns `resourceId` and `mediaType`.
- **The client-made `--resource-id`.** It makes a retry after a lost reply
  safe: the "Resource ID idempotency key ... reused for retries across
  processes".
- **Which formats Dreamina accepts, and each kind's size limit,** are
  **unconfirmed** (runs C-2 to C-4). The skill says "Local-file upload is a
  gated runtime capability"; the server decides.
- **Uploads are free.** The result is a canvas resource the person can see.

## Downloads

```text
resource download <resourceId> --project-id <canvas> --output <file>
```

- **The reply.** It returns `resourceId`, `path`, `size`, and `sha256`.
  `--output` names a file, "used verbatim; no transcoding".
- **Checks.** The pack checks that `size` is above 0 and at most
  `max_download_megabytes`. It reads the file, and checks that its length
  equals `size` and its SHA256 equals `sha256`.
- **Video and audio** are **unconfirmed**, because the schema's summary says
  "Safely download a successful image resource" (run C-3). If video or audio
  cannot be downloaded, [07-media.md](07-media.md) and the node plans are
  corrected before the Video milestone.

## Image upscale

```text
node upscale image --project-id <canvas> --node-id <source>… --submit-id <uuid>…
  [--mode normal|pro] [--resolution 2K|4K|8K] [--detail 1..100]
  --credit-ceiling <n>
```

- **Sources.** 1 to 20 sources, one submit ID per source, in the same order.
- **Mode.** `pro` (the default) needs `--resolution`; `normal` refuses it.
- **Approval.** It has its own approval scope. A ceiling of `n` covers the
  whole batch. Exit 10 returns `partialData.items[].sourceNodeId` and
  `submitId`, and no output node exists yet.
- **Success.** It returns `items[]` with `sourceNodeId`, `submitId`,
  `nodeId`, `resourceIds`, `state`, and `authorizedCredits`, plus
  `totalMaxCredits` and `creditsApproved`.
- **Importing a local image.** A local image must first be an image node:

  ```text
  node create image --project-id <canvas> --resource-id <uuid> --import-kind local_upload --submit-id <uuid>
  ```

  "this is the only case where `--submit-id` works without `--run`". Whether
  an imported node is an "eligible successful image" for upscale is
  **unconfirmed** (run C-13).

## Elements

```text
node create element --project-id <canvas> --main <node-id|resource-id>
  [--voice <node-id|resource-id>] [--auxiliary <node-id|resource-id>]…
  [--title <text>] [--description <text>]
```

- **Bare IDs.** Element bindings take bare Node IDs (`node_…`) or bare
  Resource IDs (UUIDs), not `node:`/`res:` forms.
- **Bindings.**
  - `--main` must be an image.
  - `--voice` must be audio.
  - `--auxiliary` must be images.
- **The reply.** It returns `node` (with `subjectBindings`) and `mutation`.
- **Free.** Creating an Element generates nothing and costs nothing
  ([research/cli.md](research/cli.md#elements)).
- **Use.** A later run references it as `--ref node:<element-node-id>`, with
  `m2v` for video or `i2i` for images.

## The CLI's own state

- **The journal.** The CLI keeps a current-canvas record and an operation
  journal in its own state folder. The pack never sets
  `DREAMINA_CANVAS_STATE_DIR`, so the person's agent sessions and the pack
  share one journal. This is harmless, because the pack always passes
  `--project-id`.
- **Local store failures.** `error.localStorage` with `submissionPhase`
  `before_submit` means nothing was sent. With `after_submit`, the run was
  sent: the pack records it from `partialData` and waits as usual.
  `localStorageWarning` on a success changes nothing.

## What is billed when something fails

| Event                                                  | Billed?                                                                                 | Evidence |
| ------------------------------------------------------ | --------------------------------------------------------------------------------------- | -------- |
| Refused locally (exit 2)                               | No; nothing was sent                                                                    | skill    |
| Stopped at the ceiling (exit 10)                       | No: "nothing has been charged"                                                          | skill    |
| Refused at save, before the quote                      | No                                                                                      | skill (save precedes quote) |
| Accepted, then the wait is canceled or times out      | Yes, the generation keeps running                                                       | skill: no cancel |
| Accepted, then the generation fails                    | **Unconfirmed**. The skill warns against describing "net spend or refund status" without ledger facts | run C-17 |
| A replayed submit ID                                   | No: "reusing the same `submitId` replays the first run and does not charge twice"        | skill    |
| Uploads, Elements, imports, reads                      | No                                                                                      | skill    |

## Facts to confirm by test runs

Each fact is settled by a run in [21-test-runs.md](21-test-runs.md). Every
result is recorded below and in the README's changes table, and the plans it
names are corrected before building further.

| Fact                                                                                   | Run   | Plans it may change |
| -------------------------------------------------------------------------------------- | ----- | ------------------- |
| What `auth wait` returns on approval                                                   | owner sign-in | 05 |
| `auth account` signed in: `isVip`, `vipLevel`; the plan gate                           | C-0   | 22, 01 |
| How `model list` writes `flags[].flag`; which flags each mode lists                    | C-0   | 06, 09 to 11, catalog |
| `canvas create` reply                                                                  | C-1   | 08 |
| PNG upload; reply; the image size limit                                                | C-2   | 07 |
| MP4 upload and `resource download` of a video                                          | C-3   | 07, 10, 14 |
| WAV and MP3 upload; `resource download` of audio                                       | C-4   | 07, 11 |
| Exit 10 reply with `minimumCreditCeiling` and `partialData`                            | C-5   | 08 |
| `{{res:<uuid>}}` in a prompt binds an upload (`node show` `promptParts`)              | C-6   | 01, 07 |
| The run reply on acceptance without `--wait`                                           | C-7   | 08 |
| `operation wait` states and `resources[]`; `node show` resources; image download       | C-8   | 08 |
| An input the server refuses: exit code, `error.validation`                             | C-9   | 08 |
| `i2i` with an uploaded image                                                           | C-10  | 09 |
| Speech with a voice; audio download                                                    | C-11  | 11 |
| Omni dubbing with an image or audio reference; a too-short audio reference refused at save | C-12  | 11 |
| Import an upload as a node; upscale it; the upscale reply                              | C-13  | 12 |
| A video run whose wait is stopped, then resumed by `operation wait` from a new process | C-14  | 08, 14 |
| An Element from an upload; an `m2v` quote that references it; a gone canvas            | C-15  | 13, 08 |
| `operation status` of an unknown submit ID; the exit codes met                         | C-16  | 08, 14 |
| Whether a failed generation is billed (balance before and after, read by the owner)    | C-17  | 18, 02 |

### Results of the contract runs

Filled in as the runs are made.

| Run | Date | Result |
| --- | ---- | ------ |
| Owner sign-in | 2026-10-16 | Two links expired unapproved (`cli.login_wait_timeout`, exit 20, then `cli.login_expired`, exit 11). The third was approved: `auth wait` exit 0, `status` `logged_in`, credentials in the keyring until 2026-12-15. |
| C-0 (reads only) | 2026-10-16 | `auth account`: `isVip` `true`, `vipLevel` `standard`; the plan gate passed on Standard. `model list`: 12 image, 5 video, 2 audio models; flags written `--name`; `ratio`, `resolution`, `duration` required; video `first_last_frame` listed twice; `mediaType` values `image`, `video`, `audio`; no music model. `voice list`: 13 voices for `seed_audio_v1`. `canvas ls`: none. |
| Part 0 (free) | 2026-10-17 | Canvas "ComfyUI tests" created; a second `canvas create` with the same `--project-id` returned the same canvas (C-1). PNG, WAV, and MP4 uploads accepted with the client-made `--resource-id` echoed (C-2 to C-4 in part). An import (`node create image --resource-id … --import-kind local_upload`) needs `--title`: without it, exit 2, `cli.invalid_node_input`, `validation.fieldPath` `title`. 45 price checks with `--credit-ceiling 0`: 42 stopped at exit 10 with a price, code `cli.generation_credit_ceiling_too_low`, class `confirmation_required`, `creditConfirmation.reason` `ceiling_too_low`, plus `creditConfirmation.nodeIds`, `error.requestId`, and `error.operationRef` (C-5); 2 ran because their quote was 0 (`seedream_4.0`); 1 was refused locally: a listed speech model that takes no scenario cannot be run by name (`cli.invalid_command`, `fieldPath` `model/scenario`); the pack ignores it. The free runs settled C-7 and C-8: on acceptance `submission.state` `accepted` with `submission.resources[].resourceId` and `node.status` `empty`; `operation status` and `wait` end with `state` `succeeded`, resource `state` `succeeded` with `width`, `height`, `format` (`jpeg` for images), and `submission.state` `completed`; `node show` gives the resource `status` `success`, `source` `generated`, `creditsAmount`; `resource download` wrote the file with `size` and `sha256` matching the bytes. Upscale: an imported node is an eligible source (C-13 in part); `normal` ran free and doubled 1280×720 to a 2560×1440 PNG; `pro` quoted 2, 4, and 8 credits for 2K, 4K, and 8K; the upscale reply's item `state` is `ACCEPTED`. No credits spent. |
| Part 1 (C-1 to C-16) | 2026-10-17 | 28 credits (C-11a 12, C-14 16). Image uploads above 30 MiB (31,457,280 bytes) are refused locally: exit 2, `cli.invalid_upload_file`. MP4, WAV, and MP3 upload and download back byte for byte. `{{res:<id>}}` in a prompt adds its reference by itself and merges with the same `--ref` into one slot. The server substitutes some invalid values instead of refusing them (`5:4` became `1:1`, `1080p` became `720p`, a missing ratio became `16:9`), so the pack's own checks are the only guard; count 99 and duration 2 are refused at save with `service.2`. Text reading takes no `--ref` (exit 2, `cli.invalid_command`, `fieldPath` `ref`); speech is MP3. Audio and video terminal replies give `format`, `width`, and `height` as null. While a video runs, `operation status` answers exit 0 with state `running`, and `submission.state` is already `completed`; a short wait answers exit 20, `cli.operation_wait_timeout`. A killed wait ends at once; a new `operation wait` resumes. A deleted canvas gives exit 2, `service.20009`, for an upload, a run, and an Element. An unknown submit ID gives exit 20, `cli.operation_submission_absent`, never a state `absent`; without `--project-id`, exit 2, `cli.operation_not_found`. Exit codes met: 0, 2, 10, 20. The upscale item state is `ACCEPTED`. An Element saves with `subjectBindings` `main`, `voice`, `auxiliaries`, and an `m2v` run with only an Element is accepted. C-17 (is a failed generation billed) needs the owner's balance readings and is still open. |
