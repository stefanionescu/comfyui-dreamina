# Dreamina Canvas CLI Facts

This report holds every fact about the Dreamina Canvas CLI that the plans rely
on, with its source. [../02-dreamina-contract.md](../02-dreamina-contract.md)
turns these facts into the contract the code follows.

Sources, cited by short names:

- **schema**: [captures/schema.json](captures/schema.json). The output of
  `dreamina-canvas --format json --non-interactive schema` for release 1.0.3,
  build `244064d` of 2026-10-14. It is the binary's own command contract.
  Cited as `schema: <command path>`.
- **skill**: [docs/dreamina-canvas-cli/](docs/dreamina-canvas-cli/SKILL.md). The
  skill installed with the CLI. Cited as `skill: <file>#<section>`.
- **installer**: `https://dreamina.capcut.com/canvas-cli/install.sh` and
  `install.ps1`, read on 2026-10-16.
- **strings**: text found in the macOS arm64 binary (25 MB, Go).
  Identical, byte for byte, to the binary the installer placed at
  `~/.local/bin/dreamina-canvas`.
- **capture**: a file in [captures/](captures/) from a call made on 2026-10-16.

The skill says the installed binary is "the source of truth for commands,
flags, models, and every other executable fact"; this skill "only describes
capabilities and boundaries" (`skill: SKILL.md#preflight`). Where they differ,
the schema wins.

## Contents

- [Release and install](#release-and-install)
- [Global flags and output](#global-flags-and-output)
- [The JSON envelope](#the-json-envelope)
- [Exit codes](#exit-codes)
- [Sign-in](#sign-in)
- [Account and plan gate](#account-and-plan-gate)
- [Commands the pack uses](#commands-the-pack-uses)
- [Model discovery](#model-discovery)
- [Voices](#voices)
- [Canvases](#canvases)
- [Generation nodes](#generation-nodes)
- [Credits](#credits)
- [Operations and recovery](#operations-and-recovery)
- [Resources: upload and download](#resources-upload-and-download)
- [Image upscale](#image-upscale)
- [Elements](#elements)
- [References and placeholders](#references-and-placeholders)
- [Local state the CLI keeps](#local-state-the-cli-keeps)
- [Hosts and telemetry](#hosts-and-telemetry)
- [Commands the pack does not use](#commands-the-pack-does-not-use)
- [Open questions](#open-questions)

## Release and install

- **Release.** `version` returns:
  - `version` `1.0.3`, `commit` `244064d`, `buildTime`
    `2026-10-14T03:36:35Z`;
  - `edition` `public`, `distribution` `global`, `releaseDate` `2026-10-09`;
  - release notes: "Select one voice as an audio reference for omni dubbing
    and preflight references against model specifications while preserving
    legacy audio compatibility." (capture: `version.json`)
- **Install commands**, from the CLI page:
  - macOS and Linux: `curl -fsSL https://dreamina.capcut.com/canvas-cli/install.sh | bash`
  - Windows PowerShell: `irm https://dreamina.capcut.com/canvas-cli/install.ps1 | iex`
  - Windows CMD: `curl.exe -fsSLO https://dreamina.capcut.com/canvas-cli/install.bat && install.bat`
- **What the installer downloads.** Files come from
  `https://dreamina.capcut.com/canvas-cli/install/1_0_0_22/`:
  - the platform binary, such as `dreamina-canvas_darwin_arm64`;
  - `skill.tar.gz`.

  `DREAMINA_CANVAS_DOWNLOAD_BASE` overrides the base. It must be https.
  (installer)
- **Where it installs.**

  | System        | Binary                                       | Skill                                         |
  | ------------- | -------------------------------------------- | --------------------------------------------- |
  | macOS, Linux  | `~/.local/bin/dreamina-canvas`               | `~/.agents/skills/dreamina-canvas-cli`        |
  | Windows       | `%USERPROFILE%\bin\dreamina-canvas.exe`      | `%USERPROFILE%\.agents\skills\dreamina-canvas-cli` |

  - `DREAMINA_CANVAS_INSTALL_DIR` overrides the binary folder. On Windows,
    `INSTALL_DIR` does too.
  - `DREAMINA_CANVAS_SKILL_DIR` overrides the skill folder.
  - An existing `dreamina-canvas` on `PATH` keeps its folder.
  - Windows supports only `AMD64`.
  - `DREAMINA_CANVAS_SKIP_PATH=1` skips the Windows PATH change.

  (installer)
- **The installer keeps the binary and skill working during an upgrade.**
  - It takes a lock folder `.dreamina-canvas.install.lock` and stages the new
    files.
  - It keeps a backup and replaces the files in place.
  - It reports a retained backup path if a step fails.

  (installer; `skill: references/authentication.md#installation-and-upgrade-permissions`)
- **Upgrades are server-driven.** An old client gets an error with
  `requiredAction=upgrade`. The error may carry `clientUpgrade.installCommands`
  (one per OS and terminal) or a legacy `upgradeUrl`. "An upgrade response
  does not itself authorize command execution."
  (`skill: references/authentication.md#installation-and-upgrade-permissions`;
  strings: `InstallCommands json:"installCommands,omitempty"`,
  `UpgradeURL json:"upgradeUrl"`)

## Global flags and output

`schema` lists four global flags (schema: `globalFlags`):

| Flag                | Type    | Default   | Meaning                                                    |
| ------------------- | ------- | --------- | ---------------------------------------------------------- |
| `--format`          | string  | `auto`    | `json` or `table`                                          |
| `--non-interactive` | boolean | `false`   | Disable interactive prompts                                |
| `--yes`             | boolean | `false`   | "Approve permitted operations without an interactive prompt" |
| `--profile`         | string  | `default` | "Local sign-in state profile"                              |

There is no `--region` flag in this release. `auth status` reports `region`
`auto` and `distribution` `global` (capture: `auth-status-signed-out.json`).

With `--format json`, a successful command writes one JSON object to stdout,
and a failed command writes one JSON object to stderr and nothing to stdout.
(captures: `version.json`, `error-auth-required.json`,
`error-invalid-flag.json`; `skill: references/node-deletion.md` says the
deletion summary "leaves stdout empty, and returns approval details in
stderr")

## The JSON envelope

Success (capture: `version.json`):

```json
{ "schemaVersion": "1", "ok": true, "data": { "...": "..." } }
```

Failure (captures: `error-auth-required.json`, `error-invalid-flag.json`):

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

Other fields a failure can carry, from the skill and the binary's field names:

| Field                                   | Meaning                                                                                       | Source |
| --------------------------------------- | --------------------------------------------------------------------------------------------- | ------ |
| `error.reason`                          | Finer cause, such as `dns_resolution_failed`, `network_permission_denied`, `credential_store_permission_denied`, `credential_store_unavailable`, `credential_store_corrupt`, `network_timeout`, `auth_dependency_failed` | `skill: references/authentication.md#authentication` |
| `error.validation.reasonCode`, `fieldPath`, `detail` | Invalid input diagnosis; `detail` is display text only                          | `skill: references/identity-and-references.md#diagnose-reference-rejection-without-guessing` |
| `error.localStorage`                    | A local state failure: `store`, `stage`, `reason`, `directory`, `submissionPhase` (`before_submit` or `after_submit`) | `skill: references/authentication.md#local-business-state-storage` |
| `creditConfirmation.reason`, `minimumCreditCeiling` | The run stopped at the quote; the ceiling that would pass                         | `skill: references/credits-and-hitl.md` |
| `partialData.items[].nodeId`, `submitId` | The identities already fixed when the run stopped                                            | same   |
| `clientUpgrade.installCommands`, `upgradeUrl` | Upgrade instructions                                                                     | `skill: references/authentication.md` |
| `deletionConfirmation`, `deletionRecovery` | Node deletion approval and recovery                                                          | `skill: references/node-deletion.md` |
| `meta.requestId`                        | Correlation ID for support                                                                    | `skill: SKILL.md#hard-boundaries` |

The skill's rule: "Branch on structured fields and exit classes, never
localized message text" (`skill: SKILL.md#error-decisions`). JSON messages are
always English (`skill: references/authentication.md#authentication`).

Error codes found in the binary that matter to the pack (strings):

- **Generation:** `cli.generation_confirmation_required`,
  `cli.generation_mode_required`, `cli.generation_title_required`,
  `cli.credit_flags_conflict`, `cli.audio_music_model_required`.
- **Media and resources:** `cli.invalid_resource_reference`,
  `cli.resource_unavailable`, `cli.download_transport_failed`,
  `cli.download_filesystem_failed`, `cli.upload_state_unknown`,
  `cli.unsupported_upload_region`.
- **Upscale and operations:** `cli.image_upscale_unavailable`,
  `cli.upscale_already_submitted`, `cli.operation_wait_interrupted`,
  `cli.invalid_wait_timeout`.
- **Sign-in and access:** `cli.authentication_required`,
  `cli.cookie_auth_forbidden`, `cli.passport_rate_limited`,
  `cli.region_not_available`.
- **Input:** `cli.invalid_flag`.

## Exit codes

Every command's schema declares its exit codes (schema:
`declaredExitCodes`). Media `node create … --run` declares
`0, 1, 2, 10, 11, 12, 13, 20, 21, 22`. The meanings below are confirmed by a
capture or stated by the skill:

| Code | Meaning                                                                                  | Source                                                       |
| ---- | ---------------------------------------------------------------------------------------- | ------------------------------------------------------------ |
| 0    | Success                                                                                  | captures                                                     |
| 2    | Invalid input, rejected locally before anything is sent (`class` `invalid_input`)        | capture: `error-invalid-flag.json`; `skill: references/identity-and-references.md#image-and-video-generation-edits` |
| 10   | Confirmation required: the run stopped after the quote and nothing was charged           | `skill: references/credits-and-hitl.md`                      |
| 11   | Sign-in required (`class` `auth_required`, `requiredAction` `login`)                     | capture: `error-auth-required.json`                          |
| 20   | Operation incomplete: accepted and still running, or a wait that ran out (`class` `operation_incomplete`, `requiredAction` `resume`) | `skill: references/recovery-and-idempotency.md` |
| 1, 12, 13, 21, 22 | Not documented. The pack reads `error.class`, `error.requiredAction`, and `error.retryable` for them, never the number. | None |

The test runs ([../21-test-runs.md](../21-test-runs.md)) capture each code the
pack meets.

## Sign-in

- **Device authorization.** `auth login` returns `status`
  `authorization_required` and a `challenge` (capture: the shape below; the
  codes are not kept):

  ```json
  {
      "status": "authorization_required",
      "challenge": {
          "deviceCode": "<opaque>",
          "userCode": "XXXX-XXXX",
          "verificationUri": "https://dreamina.capcut.com/ai-tool/cli-auth-os?cli_name=canvas_cli",
          "verificationUriComplete": "https://dreamina.capcut.com/ai-tool/cli-auth-os?cli_name=canvas_cli&user_code=XXXX-XXXX",
          "pollSeconds": 5,
          "expiresAt": "2026-10-16T22:53:28.675524+01:00"
      },
      "profile": "default",
      "region": "auto",
      "environment": "prod",
      "authMode": "oauth",
      "distribution": "global",
      "version": "1.0.3",
      "edition": "public"
  }
  ```

  The challenge lasted about ten minutes.
- **Waiting for approval.** `auth wait --device-code <code> --timeout <duration>`
  waits for the person to approve. `--timeout` is a Go duration such as `9m`.
  A bare number such as `600` is refused with `cli.invalid_flag`, exit 2
  (capture: `error-invalid-flag.json`). The default is `10m`.
- **Two ways a wait ends without approval:**
  - A wait whose `--timeout` runs out before the challenge expires exits 20
    with `cli.login_wait_timeout`, class `operation_incomplete`,
    `requiredAction` `resume`, `retryable` `true` (capture:
    `error-login-wait-timeout.json`). The same device code can be waited on
    again.
  - A wait that reaches the challenge's `expiresAt` exits 11 with
    `cli.login_expired`, class `auth_required`, `requiredAction` `login`
    (capture: `error-login-expired.json`). A new `auth login` is needed.
- **Other auth commands.**
  - `auth status` reads the local state without the network:
    `loggedIn`, `profile`, `region`, `environment`, `authMode`,
    `distribution`, `version`, `edition`; when signed in, also `expiresAt`
    and `credentialStorage` (schema: `auth login` success `state`).
  - `auth account` reads the account from the service: `userId` (integer),
    `isVip`, `vipLevel` (schema: `auth account`).
  - `auth refresh` renews the credentials.
  - `auth logout` clears the profile's local sign-in state and returns
    `loggedOut`.
  - `auth login --force` clears the state and signs in again.
- **Where credentials live.** The pack never reads them.
  - macOS: the Keychain, with a cache lock under
    `~/Library/Caches/byted_auth_client/locks`.
  - Linux: files under `~/.local/share/<service>/<account>.json`.
  - Windows: `HKCU\Software\BytedAuthClient\keychain`, encrypted with the
    current user's DPAPI.

  (`skill: references/authentication.md#authentication`)
- **The token is bound to the device.** The binary signs requests with a
  device key (DPoP); strings include "parse DPoP public key". So the
  credentials work only for the OS user and machine that signed in. ComfyUI
  must run as that same user.
- **The skill's rule for agents:** "Once a challenge is returned, present its
  official verification URL and user code, then follow the installed schema's
  wait flow. Do not start another login, log out, or use `--force` merely
  because authorization is pending."
  (`skill: references/authentication.md#authentication`)

## Account and plan gate

The CLI page says "Private beta · Advanced subscribers only".

- Signed out, `model list` fails with `cli.authentication_required`, exit 11
  (capture: `error-auth-required.json`).
- Signed in (2026-10-16, third sign-in link):
  - `auth wait` exited 0 with `status` `logged_in` and `state`
    `{loggedIn: true, expiresAt: "2026-12-15T22:15:28Z", credentialStorage:
    "keyring"}`.
  - `auth account` returned `isVip` `true`, `vipLevel` `standard`
    ([captures/auth-account.json](captures/auth-account.json), with `userId`
    removed).
  - `model list` returned 12 image, 5 video, and 2 audio models.

  **The "Advanced subscribers only" gate did not stop a Standard account.**
  [catalog.md](catalog.md) holds the lists.
- Every success reply carries a top-level `meta.requestId`.

## Commands the pack uses

| Command                         | Reads | Writes | Confirmation | Used for                                          |
| ------------------------------- | ----- | ------ | ------------ | ------------------------------------------------- |
| `version`                       | yes   | no     | no           | The version gate                                  |
| `schema`                        | yes   | no     | no           | Checking the commands the pack needs exist        |
| `auth status/login/wait/account/logout` | yes | local | no      | The settings dialog                               |
| `model list --type`, `model find` | yes | no     | no           | The model check and Model: Info                   |
| `voice list`                    | yes   | no     | no           | Model: Info for speech models                     |
| `canvas create`, `canvas ls`    | yes   | yes    | no           | The pack's canvas                                 |
| `resource upload`               | no    | yes    | no           | Local media                                       |
| `node create image/video/audio --run` | yes | yes | yes         | Paid runs                                         |
| `node create element`           | yes   | yes    | no           | Element: Add                                      |
| `node create image --resource-id --import-kind local_upload` | yes | yes | no | Importing a local image before an upscale |
| `node upscale image`            | yes   | yes    | yes          | Image: Upscale                                    |
| `operation status/wait`         | yes   | no     | no           | Waiting and recovery                              |
| `node show`                     | yes   | no     | no           | Reading a finished node's resources               |
| `resource download`, `resource get` | yes | no    | no           | Fetching outputs                                  |

(schema: each command's `reads`, `writes`, and `confirmation`)

## Model discovery

`model list --type image|video|audio` and `model find <name...> [--type]`
return the same shape (schema: `model list`, `model find`):

```
items[]:
  type            string            image | video | audio
  model           string            the canonical value for --model
  aliases[]       string?           names that help match; never sent as --model
  modes[]:
    name          string            t2i, i2i, t2v, first_last_frame, m2v, tts, music
    scenario      string?           for tts: text-reading or omni-dubbing
    flags[]?:
      flag        string            the flag name
      required    boolean
      values[]    string?           allowed values
      min, max, step     number?
      minLength, maxLength integer?
    references?:
      min, max    integer           total material count
      types[]:    mediaType, min, max
      requireAnyOfTypes[]      string?
      mutuallyExclusiveTypes[] string?
    vipRequired   boolean?
    vipResolutions[] string?
```

The skill's rules for these fields:

- "`model` is the canonical value to pass to `--model`. `aliases` only helps
  match … never submit an alias as the model."
- "`flags` contains only flags that the current CLI actually accepts and whose
  dynamic constraints came from the live generation specification."
- "`references` is omitted when that specification does not provide
  materials, and `references.types` contains only material types the
  specification enables."
- "An omitted `references` means the upstream specification supplied no
  materials; `types: []` means the specification explicitly enabled no
  material type. Do not conflate them."
- `model find` ranks "exact canonical model, exact alias, canonical
  substring, then alias substring. If several items remain, resolve the intent
  or ask the user; never select the first item by default."
- "The server revalidates the latest specification at submission time;
  discovery is not durable authorization."
- In `model <name>` output, "`generation.isVip` is a model-level membership
  requirement and `vipConfigs[]` carries resolution-level membership
  requirements. An explicit `false` differs from an absent field."

(`skill: SKILL.md#model-and-voice-discovery`, `SKILL.md#preflight`)

`model <canonical-name>` returns the full underlying specification under
`matches[].generation`. It is "only for one model's full underlying
specification" (`skill: SKILL.md#select-a-callable-model`). The captures hold
it for every listed model.

## Voices

`voice list [--offset N] [--count 1..100] [--model <canonical>]` returns
`models{<model>: {items[].voiceName, hasMore, nextOffset, totalCount}}`.
Paging repeats with `--offset <nextOffset> --model <model>` until `hasMore` is
false. `--count` defaults to 50 and allows 1 to 100. There is no
`--language`. A voice name is passed unchanged to `--voice-name`.
(schema: `voice list`; `skill: SKILL.md#select-a-tts-voice`)

## Canvases

- `canvas create <name> [--project-id <uuid>] [--use]` returns
  `project.projectId`, `name`, `createdAt`, `updatedAt`, `webUrl`,
  `draftVersion`, and `current`. A client-made `--project-id` makes a retry
  safe. (schema: `canvas create`)
- `canvas ls [--limit] [--cursor]` returns `items[]` with `projectId`,
  `name`, `createdAt`, `updatedAt`, `webUrl`, plus `nextCursor` and
  `hasMore`. (schema: `canvas ls`)
- Without `--project-id`, node commands use the CLI's "current project", a
  local record that `canvas create --use` sets. The pack always passes
  `--project-id`. "An explicit `--project-id` avoids reading the
  current-canvas record."
  (`skill: references/authentication.md#local-business-state-storage`)

## Generation nodes

`node create image|video|audio` saves a node, and with `--run` saves, quotes,
approves, and runs it in one call (schema: `node create video`). Flags of
`node create video`, from the schema:

| Flag              | Type      | Notes from the schema                                                                    |
| ----------------- | --------- | ---------------------------------------------------------------------------------------- |
| `--project-id`    | UUID      | "omit to use the current project"                                                        |
| `--node-id`       | Node ID   | "generated when omitted"                                                                 |
| `--update-id`     | UUID      | "generated when omitted"                                                                 |
| `--title`         | string    | At most 512 UTF-16 code units. `create --run` needs a title when the prompt is empty.     |
| `--mode`          | string    | `t2v|first_last_frame|m2v`. Required with any generation flag.                           |
| `--prompt`        | string    | `{{node:…}}`, `{{res:…}}`, `{{uri:…}}`, `{{vid:…}}` references; `\{{` for a literal `{{` |
| `--model`         | string    | "Video model ID registered by the service"                                               |
| `--ratio`         | string    | Such as `16:9`                                                                           |
| `--resolution`    | string    | Such as `720P`                                                                           |
| `--duration`      | number    | Default 5, more than 0                                                                   |
| `--count`         | integer   | Default 1; "the maximum is the --count max returned by model list"                       |
| `--ref`           | string[]  | Ordered `type:value` references; `node:` needs the `node_` prefix; `res:` needs a lowercase UUID |
| `--resource-id`, `--import-kind` | | Import registered resources as this node's output                              |
| `--run`           | boolean   | Save, estimate, approve, run                                                             |
| `--submit-id`     | UUID      | "generated when omitted with --run"; reused to resume                                    |
| `--credit-token`  | string    | From `node confirm`; excludes `--credit-ceiling`                                         |
| `--credit-ceiling`| integer   | At least 0; "stops before run when the estimate exceeds it"                              |
| `--wait`, `--timeout`, `--interval` | | Wait after `--run`; timeout default `10m`, interval `5s`                     |
| `--dry-run`       | boolean   | Local validation only                                                                    |
| `--x`, `--y`, `--tag`, `--clear-tags`, `--resource-source` | | Placement, tags, cross-project resources |

- `node create image` has the same flags without `--duration`. Its modes are
  `t2i` and `i2i`.
- `node create audio` has `--duration`, `--voice-name`, and `--scenario`, but
  no `--ratio`, `--resolution`, or `--count`. Its modes are `tts` and `music`.
  (schema: `node create image`, `node create audio`)

Mode rules (`skill: references/identity-and-references.md`):

- There is no default mode. `--mode` is required whenever any generation
  field is supplied; a missing mode fails locally with
  `cli.generation_mode_required`, exit 2.
- Video mode follows the resolved source type:

  | Material                                             | Mode               |
  | ---------------------------------------------------- | ------------------ |
  | No media                                             | `t2v`              |
  | One image as a locked-ratio first frame              | `first_last_frame` |
  | Two ordered images (first, last), same ratio         | `first_last_frame` |
  | One image with a caller-chosen output ratio          | `m2v`              |
  | An Element, or mixed media                           | `m2v`              |

- "Image-to-video is not a public CLI mode".
- `t2v` takes no reference at all.
- `t2i` takes only Text references.
- `i2i` needs at least one image, Element, or image Resource.
- Audio:

  | Purpose                              | Arguments                                                      |
  | ------------------------------------ | -------------------------------------------------------------- |
  | Speech without choosing a model      | `--mode tts --voice-name <voice>`; omit model, scenario, duration, ref |
  | Text reading with a model            | `--mode tts --model <m> --scenario text-reading --voice-name <voice>`; no references |
  | Omni dubbing                         | `--mode tts --model <m> --scenario omni-dubbing [--voice-name <voice>]`; image, audio, or Element references within the spec |
  | Music                                | `--mode music --model <m> --duration <seconds>`; no voice, scenario, or references |

  "All audio workflows produce one output; omit `--count`."
- "Generation is a complete replacement, not a field-level patch."

The skill asks for one node per requested output, with `--count 1` where the
mode supports it (`skill: SKILL.md#build-the-minimum-sufficient-graph`).

## Credits

- **The four-step path.** "save latest draft → authoritative quote → user
  approves a ceiling when required → server adjudicates against the latest
  draft before running → run only if latest total <= approved ceiling."
- **How `--run` takes approval.**

  | Approval            | Meaning                                                                                   |
  | ------------------- | ----------------------------------------------------------------------------------------- |
  | `--credit-ceiling <n>` | "Proceed only when the quote is at most `n`. … the cap holds unconditionally; a server-side 'no confirmation required' does not lift it" |
  | `--credit-token <t>`   | Already approved with `node confirm`                                                   |
  | interactive `y/N`      | A terminal prompt                                                                      |
  | `--yes`                | "Approves any amount. Use only when the price is genuinely unknowable beforehand"     |

- **Exit 10.** With none of these on a non-TTY, the command "stops after the
  quote and exits `10`. **The node is already saved and nothing has been
  charged.**" The failure carries:
  - `error.code` `cli.generation_confirmation_required` and `requiredAction`
    `confirm`;
  - `creditConfirmation.reason` and `minimumCreditCeiling`;
  - `partialData.items[].nodeId` and `submitId`.
- **The same applies when the quote is above the ceiling.** An absent
  `minimumCreditCeiling` means `occupancy_unknown`. "It is **not** zero".
- **Reuse.** "Reusing the same `submitId` replays the first run and does not
  charge twice; a fresh `submitId` is a second run and charges again."
- **Quotes.** `node quote --node-id …` prices saved nodes:
  - `items[].maxCredits`, `totalMaxCredits`;
  - `confirmable`, `confirmationRequired`;
  - per-item `error.validation`.
  
  It is "read-only information".
- **Batch runs.** `node confirm --credit-ceiling` issues a short-lived
  `creditConfirmationToken` for `node run --credit-token`.
- "Do not describe the nominal pre-charge snapshot as final net spend or
  refund status unless the release exposes settlement/ledger facts that prove
  it."

(`skill: references/credits-and-hitl.md`; schema: `node quote`,
`node confirm`, `node run`)

## Operations and recovery

- **The operation reference.** The `submitId` of a run is its operation
  reference: `operation status <submitId>` queries once, and
  `operation wait <submitId> [--timeout] [--interval]` polls until a terminal
  state.
- **When `--project-id` is needed.** "needed only when the local recovery
  record is missing and the service must be queried directly". Passing it
  always is allowed.
  (schema: `operation wait`)
- **What a wait returns.**
  - `operationRef`, `state`;
  - `resources[]` with `resourceId`, `state`, `width`, `height`, `format`,
    and on failure `serviceCode`, `retryable`, `requiredAction`;
  - `submission`: `state`, `resubmittable`, `adviceCode`, `advice`;
  - `submissionError`: `serviceCode`, `message`, `reason`, `retryable`,
    `requiredAction`, `validation`;
  - `awaitingConfirmation`: `nodeId`, `totalMaxCredits`, `quotedAtMs`;
  - `localStorageWarning`.

  (schema: `operation wait`)
- **Exit 20.** "After an accepted media submission, exhausted transient
  errors, timeout, or interruption return `ok=false`, exit `20`,
  `class=operation_incomplete`, `retryable=false`, and
  `requiredAction=resume`. This means the original create/edit/run must not
  be retried; a new read-only `operation wait` with the returned submit ID is
  safe." `--timeout 0` queries once. The wait retries a transient status
  failure at most twice.
- **Recovery rules.**
  - "submit response was lost: inspect read-only with the same submit ID;
    **do not replay the run**".
  - "submission state is `absent`: do not infer that nothing ran: the record
    can have expired."
  - "An empty resource set is not 'all succeeded.'"
- **There is no cancel.** Deleting a node "does not delete media resources,
  cancel accepted generation tasks or refund credits"
  (`skill: references/node-deletion.md#supported-scope`). The schema has no
  cancel command.

(`skill: references/recovery-and-idempotency.md`)

## Resources: upload and download

- **Upload.** `resource upload --project-id <uuid> --file <path>` registers a
  local image, video, or audio file as a project resource and returns
  `resourceId` and `mediaType`.
  - `--project-id` is required.
  - `--type image|video|audio` overrides the extension.
  - `--resource-id <uuid>` is an idempotency key "reused for retries across
    processes".
  - `--name` sets a display name.
  - `--source-url` takes an image URL instead of a file.
  - `--import-kind` takes `local_upload` (the default) or
    `external_generated`.

  (schema: `resource upload`)
- **Upload is a gated capability.** "Local-file upload is a gated runtime
  capability that not every such artifact composes. When it is not composed,
  the server's admission decision is authoritative. Local image, video, and
  audio files use direct upload before registration."
  (`skill: references/identity-and-references.md#upload-material-identity`)
- **Download.** `resource download <resource-id> --project-id <uuid>
  --output <file or folder>` returns `resourceId`, `path`, `size`, and
  `sha256`. The output is "used verbatim; no transcoding". Its summary reads
  "Safely download a successful image resource". Whether it downloads video
  and audio is a contract check. (schema: `resource download`)
- **Resource state.** `resource get <id>` returns `type`, `status`, `name`,
  `createdAt`, `errorCode`, `creditsAmount`, and `source`, in any state.
  (schema: `resource get`)
- **Download checks.**
  - "inspect the byte count returned by the CLI; a zero-byte or clearly
    implausible file is not a valid delivery";
  - "record the SHA256 returned by the CLI";
  - check the actual content.

  (`skill: references/completion-and-validation.md#download-checks`)

## Image upscale

`node upscale image --node-id <id>… [--submit-id <uuid>…] [--mode normal|pro]
[--resolution 2K|4K|8K] [--detail 1..100] [--title] --credit-ceiling <n>
[--wait]`:

- **Source and output.** It takes 1 to 20 successful image nodes and creates
  a new node and resource per source.
- **Mode.** `pro` (smart upscale, the default) needs `--resolution`;
  `normal` refuses it.
- **Approval.** It has its own approval scope: an ordinary `node confirm`
  token is not accepted. "Explicit ceilings remain binding below the
  threshold." The schema shows `--credit-ceiling` with default `0` and the
  constraint "approval only when explicitly provided".
- **Exit 10.** It returns `partialData.items[].sourceNodeId/submitId`, and no
  output node has been created yet.
- **Success.** It returns `items[]` with:
  - `sourceNodeId`, `submitId`, `nodeId`;
  - `resourceIds[]`, `state`, `authorizedCredits`, `generationState`;
  - `resources[]` with `width`, `height`, `format`.

  It also returns `totalMaxCredits` and `creditsApproved`.

(schema: `node upscale image`; `skill: references/credits-and-hitl.md#image-upscale-uses-its-own-approval-scope`)

## Elements

`node create element --main <node or resource> [--voice …] [--auxiliary …]…
[--title] [--description]` creates an Element node:

- It is a recurring identity, bound to a primary image, an optional voice,
  and auxiliary images.
- `--main` is required on create.
- A Resource ID binding is "frozen". A Node ID binding "follows that node".
- Elements cost nothing to create: "Bind suitable existing material directly;
  creating an Element does not require extra generation."
- An Element is referenced as `--ref node:<element-node-id>` with
  `--mode m2v` for video, or `i2i` for images. It must not occupy a
  `first_last_frame` slot.

(schema: `node create element`; `skill: SKILL.md#consistency-across-outputs`,
`references/identity-and-references.md#video-mode-follows-the-resolved-source-type`)

## References and placeholders

| Form                     | Meaning                                                                                       |
| ------------------------ | --------------------------------------------------------------------------------------------- |
| `--ref node:node_xxx`    | A canvas node's selected output; keeps the upstream edge; may point at a node still generating (checked at run time) |
| `--ref res:<uuid>`       | One concrete resource, frozen; must already be successful at save time                       |
| `{{node:node_xxx}}`      | Binds that node to this position in the prompt                                               |
| `{{res:<uuid>}}`         | Binds that resource to this position (named in the `--prompt` flag description)              |
| `\{{`                    | A literal `{{` in the prompt                                                                  |
| `uri:`, `vid:`           | Reserved; the server answers unsupported                                                      |

- A Resource ID has "exactly one accepted spelling: canonical lowercase UUID".
- "If the same node appears in both a prompt placeholder and `--ref`, it is
  merged into one reference slot. Read the saved `generation.references[]` for
  the final slot order".
- Text nodes may be references but never placeholders.
- "Does not exist", "no permission", and "already unlinked" return the same
  error.

(`skill: references/identity-and-references.md`; schema: `node create video`
`--prompt`, `--ref`)

## Local state the CLI keeps

- The CLI keeps a current-canvas record and an operation journal (the
  recovery records `operation wait` reads). `DREAMINA_CANVAS_STATE_DIR` moves
  them to "an approved private persistent absolute directory". "This option
  changes business records only, not authentication credentials".
- A local store failure reports `error.localStorage` and does not prove a
  remote failure.

(`skill: references/authentication.md#local-business-state-storage`)

## Hosts and telemetry

- **Hosts.** Found in the binary (strings): `dreamina-api.us.capcut.com`,
  `mweb-api-sg.capcut.com`, `login.us.capcut.com`, and `dreamina.capcut.com`.
  The pack never contacts them itself.
- **Telemetry.** The binary reads `DREAMINA_CLI_CALLER_AGENT` and reports an
  `outside_agent` field in telemetry (strings:
  `OutsideAgent json:"outside_agent,omitempty"`). The pack leaves the
  variable unset. The skill does not document it, and the owner's rules
  forbid inventing values.
- **Headers.** The binary sends `X-Tt-Cli-App-Version`,
  `X-Tt-Cli-Device-Type`, and `X-Tt-Cli-Install-Base-Url` (strings). This is
  how the server knows the client version it may refuse.

## Commands the pack does not use

| Command                                   | Why not                                                                         |
| ----------------------------------------- | ------------------------------------------------------------------------------- |
| `node create/edit text`, `timeline`       | Text context and timelines are out of scope ([../01-decisions.md](../01-decisions.md#out-of-scope)) |
| `node edit image/video/audio`             | Each run creates a new node; editing would reuse a node, which the owner's "one new job per run" rule forbids |
| `node delete` and its `confirm`, `status` | Needs the person's explicit approval of each batch; the pack never deletes      |
| `node find`                               | The pack keeps its own node IDs                                                 |
| `node quote`, `node confirm`, `node run`  | `--run --credit-ceiling` does the same in one call                              |
| `canvas create --use`                     | The pack never changes the CLI's current canvas                                 |
| `auth refresh`                            | The CLI refreshes credentials on its own when a call needs it (to confirm in the test runs) |
| `--yes`, `--profile`                      | No blanket approval; one profile                                                |

## Open questions

These are settled by the free reads and the test runs. Each result is
recorded in [../02-dreamina-contract.md](../02-dreamina-contract.md#results-of-the-contract-runs).

1. Does `resource download` fetch video and audio, or images only?
2. Which audio formats does `resource upload` accept (WAV, MP3)? What are the
   size limits for each media type?
3. Does `{{res:<uuid>}}` bind an uploaded resource in a prompt, as the
   `--prompt` description says?
4. What does `node create … --run` return on acceptance without `--wait`: the
   `node` and `items[].submitId` with `state`?
5. What does `operation wait` return for a video: `resources[].format`,
   `width`, `height`? Does it return a duration?
6. Can `node upscale image` take an image node imported with
   `--resource-id … --import-kind local_upload`?
7. What do exit codes 1, 12, 13, 21, and 22 carry?
8. Does a run above the plan's allowance fail at save, at quote, or at run,
   and with which `error.code`?
9. Is there a credit balance anywhere in the CLI? `auth account` has `isVip`
   and `vipLevel` but no balance.
10. How long does a submission record stay readable by `operation wait`?
