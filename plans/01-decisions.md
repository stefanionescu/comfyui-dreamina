# Design Decisions

This plan fixes every decision the other plans depend on. Each decision states
what was chosen and why.

The reference repositories:

- **F**, the fal pack (`F=/Users/dr_stone/Documents/work/comfyui-fal`, commit
  `cef8b6e`, 2026-10-16). The newest of the owner's packs. It was ported from
  B and carries every rule the owner set while building B, O, and F.
- **B**, the BytePlus pack (`B=/Users/dr_stone/Documents/work/comfyui-byteplus`,
  commit `472cf10`).
- **O**, the OpenRouter pack (`O=/Users/dr_stone/Documents/work/comfyui-openrouter`,
  commit `c076f37`).

This pack ports F's code. Where it differs from F, the difference is named
here.

The facts behind these decisions are in
[02-dreamina-contract.md](02-dreamina-contract.md) and
[research/cli.md](research/cli.md). The owner's rules are in
[research/owner-rules.md](research/owner-rules.md); every plan follows them.

## Contents

- [What the pack is](#what-the-pack-is)
- [Why the CLI](#why-the-cli)
- [What is copied from fal](#what-is-copied-from-fal)
- [Names and identifiers](#names-and-identifiers)
- [The nodes](#the-nodes)
- [How the nodes cover every model](#how-the-nodes-cover-every-model)
- [Checking a model before paying](#checking-a-model-before-paying)
- [The inputs of a paid node](#the-inputs-of-a-paid-node)
- [How the mode is chosen](#how-the-mode-is-chosen)
- [What a run sends](#what-a-run-sends)
- [Media, references, and placeholders](#media-references-and-placeholders)
- [Outputs](#outputs)
- [Choosing a model](#choosing-a-model)
- [The CLI on the person's computer](#the-cli-on-the-persons-computer)
- [Sign-in and privacy](#sign-in-and-privacy)
- [The canvas](#the-canvas)
- [Paid runs](#paid-runs)
- [Credits](#credits)
- [Errors](#errors)
- [Records and state](#records-and-state)
- [Media formats](#media-formats)
- [Subprocesses and concurrency](#subprocesses-and-concurrency)
- [Browser code](#browser-code)
- [Documentation, notes, and examples](#documentation-notes-and-examples)
- [Brand and images](#brand-and-images)
- [Tooling](#tooling)
- [Banned words that shape names](#banned-words-that-shape-names)
- [Live-shopping](#live-shopping)
- [Out of scope](#out-of-scope)
- [Decisions the owner should confirm](#decisions-the-owner-should-confirm)

## What the pack is

A ComfyUI custom node pack, `dreamina` (repository `comfyui-dreamina`). It runs
Dreamina's image, video, and audio models on the person's own Dreamina account
and credits. Inside ComfyUI it is **Dreamina**: the menu, the node menu root,
the settings dialog, and every label say Dreamina.

Dreamina is ByteDance's creative app at `dreamina.capcut.com`. It serves:

- image models: Seedream, GPT Image, and Gemini (Nano Banana), among others;
- Seedance video models;
- speech models.

On 2026-10-16 the owner's account listed 12 image models, 5 video models, and
2 speech models ([research/catalog.md](research/catalog.md)). It listed no
music model, although the CLI has a music mode.

Its models run on the person's credits, which come with a subscription or as
top-ups.

As in F, B, and O, the person types a model ID into a node of the right kind.
The model ID is Dreamina's canonical model name, such as `seedance_2.5`. The
person writes the model's settings in `arguments` under Dreamina's exact flag
names, as **Model: Info** shows them.

Before paying, the pack reads the model from the person's own live model list
and refuses what the model would reject. It keeps no list of Dreamina's
models.

Everything else happens in the background:

- uploads of ComfyUI images, video, and audio;
- the credit approval;
- the run and the wait;
- downloads;
- recovery;
- error translation.

The pack is not ComfyUI's ByteDance partner nodes, which bill the Comfy
account. It is not the owner's `comfyui-byteplus` pack either, which bills a
BytePlus ModelArk key. This pack bills the Dreamina account the person signs
in with, and sends nothing to any third party.

## Why the CLI

Dreamina has no public HTTP API for international accounts. ByteDance
publishes one route for software: the **Dreamina Canvas CLI**
(`dreamina-canvas`) and its skill
([research/terms.md](research/terms.md#2-what-bytedance-publishes-for-software)).
The skill forbids undocumented endpoints and raw HTTP requests. The binary
refuses cookie sign-in. Dreamina's terms forbid other automated access.

So the pack runs the person's installed CLI as a subprocess, with
`--format json --non-interactive`, and reads its JSON. That is the only way
it talks to Dreamina.

What this gives the pack, all from the CLI's own contract
([02-dreamina-contract.md](02-dreamina-contract.md)):

- **Sign-in.** A device-code sign-in, with the credentials kept in the OS
  credential store. The pack never sees them.
- **Live discovery.** `model list` returns each model's modes, flags, allowed
  values, ranges, and reference limits, from the live generation
  specification. `voice list` returns the speech voices.
- **A server-enforced credit approval.** `--credit-ceiling N` runs only when
  the quote is at most N, and otherwise stops with nothing charged.
- **Idempotent runs.** Reusing a run's `--submit-id` never charges twice.
  `operation wait <submitId>` observes a run from any process.

What it costs:

- The person must install the CLI. The pack offers ByteDance's own installer
  from its settings dialog ([16-frontend.md](16-frontend.md)).
- Every call starts a process. A call takes well under a second for reads,
  which matters only for the free model check.
- The CLI page calls it a private beta for Advanced subscribers. The owner's
  Standard account passed it on 2026-10-16
  ([research/catalog.md](research/catalog.md#account)). The README says the
  account must be able to use the Dreamina Canvas CLI, and leaves plan
  details to Dreamina's pages.

## What is copied from fal

Everything that is not specific to fal is copied from F's current code, not
from F's plans.

| Area                                   | Followed | Dreamina change                                                                                   |
| -------------------------------------- | -------- | ------------------------------------------------------------------------------------------------- |
| `rules/`, `AGENTS.md`, `CLAUDE.md`     | F        | Copied unchanged                                                                                  |
| `quality/`, `.mise/`, `.githooks/`     | F        | Copied, then re-valued ([03-repository-setup.md](03-repository-setup.md))                         |
| Package layout and import layers       | F        | `src/fal/` becomes `src/dreamina/`                                                                |
| `PaidNode`, run number, cache token    | F        | The cache token changes when the signed-in account changes, not when a key changes                |
| Transport                              | None      | New: one subprocess per CLI call (`src/dreamina/cli.py`); no HTTP to Dreamina                      |
| Request records and the Download node  | F        | Generation records keyed by submit ID; one **Generation: Download** node                         |
| Model check before paying              | F        | Reads `model list --type <kind>` from the CLI instead of fal's listing; checks flags instead of OpenAPI fields |
| `arguments` JSON                       | F        | Keys are Dreamina's flag names; each becomes `--<flag> <value>`                                    |
| File: Add                              | F        | Not ported. Paid nodes take media lists directly, and Dreamina outputs travel as `references` ([Media, references, and placeholders](#media-references-and-placeholders)) |
| Request Options                        | F        | Not ported. Dreamina has no per-request options outside the model's flags, which go in `arguments` |
| Model: Info                            | F        | Reads one model's modes, flags, references, and voices from the CLI                               |
| Settings dialog                        | F        | The API key section becomes **Dreamina CLI** (install, update) and **Account** (sign in, sign out); the request limits stay |
| Help pages, README, ADVANCED           | F        | Same shapes, lengths, and checks                                                                  |
| Example workflow generator             | F        | Engine copied; new descriptions and a new UUID namespace                                           |
| No retries, no parallel cap            | F        | Same                                                                                              |
| No prices in nodes or help pages       | F        | Same. Credits appear only as the person's own `credit_ceiling` and Dreamina's quote in a refusal ([Credits](#credits)) |

## Names and identifiers

| Item                                  | Value                                                                                |
| ------------------------------------- | ------------------------------------------------------------------------------------ |
| Repository                            | `comfyui-dreamina` (`stefanionescu/comfyui-dreamina`)                                |
| Python project name and Registry ID   | `dreamina` (free on the Comfy Registry on 2026-10-16: `api.comfy.org/nodes/dreamina` answers 404, and a search for "dreamina" finds nothing) |
| Install folder                        | `dreamina` (`ComfyUI/custom_nodes/dreamina`)                                         |
| Registry display name                 | `Dreamina`                                                                           |
| Browser extension name                | `dreamina`                                                                           |
| Node ID prefix (`NODE_PREFIX`)        | `Dreamina`                                                                           |
| Node ID                               | `NODE_PREFIX` plus the class name, for example `DreaminaVideoGenerate`                |
| Menu root and node categories         | `Dreamina`, `Dreamina/Image`, `Dreamina/Video`, `Dreamina/Audio`                     |
| Settings command and menu path        | `dreamina.OpenSettings`; **Extensions → Dreamina → Dreamina Settings**               |
| Local route prefix                    | `/dreamina/v1`                                                                       |
| Write-request header (local only)     | `X-Dreamina-Comfy: 1`                                                                |
| CSS class prefix                      | `dreamina-`                                                                          |
| Runtime package for Dreamina code     | `src/dreamina/`                                                                      |
| Error type                            | `DreaminaError`                                                                      |
| CLI folder variable                   | `DREAMINA_CANVAS_INSTALL_DIR`, the installer's own                                   |
| State folder override variable        | `DREAMINA_COMFY_STATE_DIRECTORY`                                                     |
| State folder, macOS                   | `~/Library/Application Support/DreaminaComfyUI`                                      |
| State folder, Windows                 | `%LOCALAPPDATA%\DreaminaComfyUI`                                                     |
| State folder, Linux                   | `${XDG_STATE_HOME:-~/.local/state}/dreamina-comfy`                                   |
| Temporary file prefix                 | `.dreamina-`                                                                         |
| Custom socket type                    | `DREAMINA_REFERENCES`                                                                |
| Canvas name                           | `ComfyUI`                                                                            |
| Save prefixes in examples             | `image/dreamina/<name>`, `video/dreamina/<name>`, `audio/dreamina/<name>`            |
| Commit scopes                         | `nodes`, `frontend`, `workflows`, `docs`, `hooks`, `quality`, `root`, `deps`         |

Labels write "Dreamina", as Dreamina writes its own name. Class names and
constants follow Python case (`DreaminaError`, the `Dreamina` prefix).
`DreaminaError` and `X-Dreamina-Comfy` hold no banned word, so they need no
naming exception.

The install folder is `dreamina`, as O installs as `openrouter`, because
ComfyUI names the **Browse Templates** group and the node badges after the
folder. The README's purpose sentence names the pack as a ComfyUI extension
that runs Dreamina models, so nothing reads as Dreamina's own product.

### Node ID clashes

ComfyUI skips a custom node whose ID matches a core node's. Between two custom
packs, the one loaded later silently replaces the other. On 2026-10-16:

| Source                                         | IDs                                                                                       |
| ---------------------------------------------- | ----------------------------------------------------------------------------------------- |
| ComfyUI core 0.37.2 (`comfy_api_nodes`)        | 16 `ByteDance*` IDs, such as `ByteDance2ReferenceNode` and `ByteDanceSeedreamNodeV3`; none starts with `Dreamina` |
| Comfy Registry packs                           | None named "dreamina". Jimeng packs: `ComfyUI-Jimeng-API`, `ComfyUI-WBLESS`; Seedance packs: 21, none using a `Dreamina` prefix |
| `comfyui-byteplus` (owner's pack)              | `BytePlus*` IDs; its model table names Seedance models `dreamina-seedance-…`, which are model IDs, not node IDs |

No ID in [The nodes](#the-nodes) matches. Workflows save node IDs, so the IDs
never change after the first release. Display names follow F: `Family:
Action`, no pack suffix, no `search_aliases`.

## The nodes

Seven nodes. Four paid nodes and three free nodes.

| Class                | Display name         | Category          | Sends                                                    | Main outputs                                              | Plan |
| -------------------- | -------------------- | ----------------- | -------------------------------------------------------- | --------------------------------------------------------- | ---- |
| `ImageGenerate`      | Image: Generate      | `Dreamina/Image`  | uploads, one paid run, the wait, downloads               | `images`, `references`, `result`                          | 09   |
| `VideoGenerate`      | Video: Generate      | `Dreamina/Video`  | the same                                                 | `video`, `references`, `result`                           | 10   |
| `AudioGenerate`      | Audio: Generate      | `Dreamina/Audio`  | the same                                                 | `audio`, `references`, `result`                           | 11   |
| `ImageUpscale`       | Image: Upscale       | `Dreamina/Image`  | uploads and imports, one paid upscale, the wait, downloads | `images`, `references`, `result`                        | 12   |
| `ElementAdd`         | Element: Add         | `Dreamina`        | uploads and one free Element node                        | `references`                                              | 13   |
| `GenerationDownload` | Generation: Download | `Dreamina`        | free status reads and downloads                          | `images`, `video`, `audio`, `references`, `result`        | 14   |
| `ModelInfo`          | Model: Info          | `Dreamina`        | free model and voice reads                               | `info`                                                    | 15   |

Why one paid node per kind of output:

- The owner asked for nodes that each handle a class of models, as F's do.
- A ComfyUI node's outputs are fixed when ComfyUI starts. The kind of output
  is the one thing every model a node runs must share.
- Dreamina's `model list` already groups models by `type`: `image`, `video`,
  or `audio`.

Image: Upscale is a separate node because Dreamina's upscale is its own
command (`node upscale image`). It takes no model, has its own approval scope,
and starts from an existing image node
([research/cli.md](research/cli.md#image-upscale)).

Why each free node exists:

| Node                 | Why                                                                                                            |
| -------------------- | -------------------------------------------------------------------------------------------------------------- |
| Element: Add         | Makes a Dreamina Element: one recurring character, product, or place, bound to a main image, more angles, and a voice. Later runs keep it consistent. It is free: creating an Element generates nothing. |
| Generation: Download | Collects a generation that keeps running, and billing, after a cancel, a timeout, or a restart                 |
| Model: Info          | Shows a model's modes, flags, allowed values, reference limits, and voices, as the live list gives them, before paying |

Custom socket type, declared in `src/config/namespace.py`:

| Constant     | Value                 | Carries                                                                                          |
| ------------ | --------------------- | ------------------------------------------------------------------------------------------------ |
| `REFERENCES` | `DREAMINA_REFERENCES` | `tuple[types.references.Reference, ...]`: Dreamina canvas nodes or resources, each with its media kind (image, video, audio, or element), in order |

## How the nodes cover every model

Each paid generation node takes the model as text, `model`. The model's
settings go in `arguments`: a JSON object whose keys are Dreamina's flag
names, as `model list` returns them, and whose values are Dreamina's own
values.

Why not one widget per setting:

- Dreamina's models do not share settings. One video model takes 480p to
  1080p and 4 to 15 seconds; another takes 4K; a speech model takes a voice
  and a scenario.
- Each model's allowed values come from the live specification and change
  when Dreamina changes them.
- Fixed widgets would invent shared names and freeze the allowed values.
  Widgets built per model would need a stored model list, which the owner
  rejected for O, B, and F.

**The person types any model name.** Nothing in the code lists, limits, or
filters Dreamina's models. When the workflow is queued, and again when the
node runs, the typed name and every setting are checked against the person's
live list, as O's and F's nodes check theirs. A model Dreamina adds tomorrow
works the moment its name is typed. A name that is not in the list is refused
before anything is uploaded or billed, and the message names the closest
models that are. The only model names in the code are the starting values of
the three generation nodes' `model` boxes
([Choosing a model](#choosing-a-model)), which the person replaces freely.

So:

1. **Every setting is the flag itself.** Its name and value are Dreamina's, as
   the person writes them in `arguments`.
1. **The pack checks every flag, value, and reference before paying**, from
   the live specification
   ([Checking a model before paying](#checking-a-model-before-paying)).
1. **Outputs never change.** A socket the run does not fill stops the nodes
   connected to it (`ExecutionBlocker`), as in F.

Which node runs which model is decided by the model's `type` in the live list.
A model of another type is refused before paying, with the name of the node
that runs it.

## Checking a model before paying

Before anything is uploaded or paid, the pack reads the typed model from the
person's live model list:

1. **One free read per kind.** `dreamina-canvas model list --type <kind>`
   returns every model of that kind the account can call, with each mode's
   flags and references
   ([02-dreamina-contract.md](02-dreamina-contract.md#model-discovery)).
1. **The typed name must match exactly.** It matches a model when it equals
   the canonical `model`, or one of its `aliases`, ignoring case. The pack
   then sends the canonical name. A name that matches nothing is refused, and
   the message lists the closest canonical names in the list. The skill's
   rule: "never select the first item by default"
   ([research/cli.md](research/cli.md#model-discovery)).
1. **Read once per ComfyUI process.** Each kind's list is kept in memory. Two
   nodes that need the same kind at once share one read, as in F. A name that
   is not found causes one new read of that kind before the refusal, so a
   model Dreamina added since the last read is found.
1. **The other kinds are read only to name the right node.** A name not in
   this kind's list is looked up in the other two kinds' lists. If found, the
   message names the node that runs it.
1. **Sign-in comes first.** The list needs sign-in. A signed-out read is
   refused with the sign-in message, which names **Dreamina Settings**.
1. **A failed read stops the run.** Nothing is sent when the list cannot be
   read, and the message says why.

When ComfyUI queues the workflow, the paid node's `validate_inputs` runs the
checks that need no connected input:

- the model;
- the JSON shape of `arguments`;
- each `arguments` key against the union of the model's flags.

Inputs fed by links arrive as `None` there and are checked at run time.

At run time, before any upload, the node also checks:

| Refused before paying                                                         | Why                                                                                   |
| ----------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| A model name not in the person's list                                         | Nothing to run                                                                        |
| A model of another type                                                       | Its output has no socket on this node; the message names the right node              |
| A `mode` the model does not have, or a mode that the connected inputs cannot fill | The CLI would refuse it; the message names the model's modes                     |
| `arguments` that is not a JSON object                                          | Nothing can be sent                                                                   |
| An `arguments` key that is not a flag of the chosen mode                       | It would be refused, or would set nothing                                            |
| A value outside the flag's `values`, `min`, `max`, `step`, `minLength`, or `maxLength` | The server would refuse it                                                      |
| A required flag left out                                                       | The server would refuse it                                                            |
| `prompt` set in both the box and `arguments`                                   | Two values for one flag                                                               |
| Fewer or more references than the mode's `references.min` and `max`, or than a media type's own limits | The server would refuse it                                    |
| References of a media type the mode does not enable, two `mutuallyExclusiveTypes` together, or none of `requireAnyOfTypes` | The server would refuse it            |

Why the pack checks values here, when F leaves values to fal: a Dreamina
refusal after the save leaves a saved draft on the canvas, and the live list
already holds every constraint. The checks cost nothing and add no copy of
Dreamina's rules. Each one reads a field the list returned.

Membership fields (`vipRequired`, `vipResolutions`) are shown by Model: Info
and never used to refuse. They describe the model, not the person's plan.
"The server's final admission decision remains authoritative"
([research/cli.md](research/cli.md#model-discovery)).

[06-model-check.md](06-model-check.md) owns the read, the match, the mode
choice, and the checks.

## The inputs of a paid node

The three generation nodes share their inputs, in F's order: sockets first,
then widgets, text boxes last.

| Input            | Type                         | What it does                                                                                                   |
| ---------------- | ---------------------------- | -------------------------------------------------------------------------------------------------------------- |
| `images`         | IMAGE, as a list             | Local images, uploaded with the run. Audio: Generate takes them for omni dubbing.                              |
| `videos`         | VIDEO, as a list             | Local videos (Video: Generate only)                                                                            |
| `audio`          | AUDIO, as a list             | Local audio (Video: Generate and Audio: Generate)                                                              |
| `references`     | `DREAMINA_REFERENCES`        | Outputs of other Dreamina nodes and Elements, with no upload                                                   |
| `model`          | text                         | The model name; the default is the kind's default model ([Choosing a model](#choosing-a-model))                |
| `credit_ceiling` | number                       | The most credits this run may cost, sent as `--credit-ceiling` ([Credits](#credits))                           |
| `run_number`     | number                       | Changing it sends the same run again, as in F                                                                  |
| `prompt`         | multiline text               | Sent as `--prompt`; empty sends nothing                                                                        |
| `arguments`      | multiline text               | A JSON object of Dreamina's flag names and values; empty sends nothing                                         |

- Each media kind is one list socket, and everything connected goes into one
  run, as the owner's rule for O says.
- `prompt` has its own box because almost every mode takes a prompt, and a
  prompt is easier to write and connect outside JSON.
- Image: Upscale has `images`, `references`, `credit_ceiling`, `run_number`,
  and `arguments`, and no `model` or `prompt`
  ([12-node-upscale.md](12-node-upscale.md)).

## How the mode is chosen

Every Dreamina generation has a mode, and the CLI has no default mode
([research/cli.md](research/cli.md#generation-nodes)):

- image: `t2i`, `i2i`;
- video: `t2v`, `first_last_frame`, `m2v`;
- audio: `tts` with a scenario, and `music`.

The person may set it in `arguments` as `"mode"`. Speech also takes
`"scenario"`. When `mode` is not set, the node chooses it from what is
connected, using the CLI's own rules:

| Node            | Connected                                                                 | Mode                                    |
| --------------- | ------------------------------------------------------------------------- | --------------------------------------- |
| Any             | The model has one mode for this node's type                               | That mode                               |
| Image: Generate | No image or Element                                                       | `t2i`                                   |
| Image: Generate | Any image or Element                                                      | `i2i`                                   |
| Video: Generate | Nothing                                                                   | `t2v`                                   |
| Video: Generate | One or two images, and nothing else                                       | `first_last_frame` (first image, then last) |
| Video: Generate | Anything else: videos, audio, an Element, or three or more images         | `m2v`                                   |
| Audio: Generate | Nothing connected                                                         | `tts`, scenario `text-reading`          |
| Audio: Generate | Images, audio, or an Element connected                                    | `tts`, scenario `omni-dubbing`          |

For speech, `seed_audio_v1` has two `tts` entries, text reading and omni
dubbing, and the last two rows choose between them
([research/catalog.md](research/catalog.md#audio-models)).

**One mode can appear twice.** The live lists show it: every video model
lists `first_last_frame` twice, once for exactly two images (first and last
frame) and once for exactly one image (first frame only). A mode name
therefore picks a set of entries, and the node takes the entry whose
reference limits fit what is connected. Its flags are the ones checked. When
no entry fits, the message names each entry's limits.

Why choose instead of always asking:

- The CLI's skill gives this table for video ("Video mode follows the
  resolved source type").
- The image and audio rules follow from what each mode accepts.

The skill also separates one image used as a frame from one image used as a
reference with "a caller-selected output ratio". The live lists mark `ratio`
as required in every video mode, `first_last_frame` included, so the ratio
cannot tell the two apart. One or two images alone are frames. To use them as
references instead, the person sets `"mode": "m2v"`. Model: Info lists each
model's modes.
Model: Info lists each model's modes. The result output names the mode that
ran.

## What a run sends

One `dreamina-canvas node create <kind> --run` call per run, with:

1. `--project-id`: the pack's canvas ([The canvas](#the-canvas)).
1. `--mode`, and `--scenario` for speech: as chosen above.
1. `--model`: the canonical name the check matched.
1. `--prompt`: the `prompt` box, with the pack's placeholders rewritten
   ([Media, references, and placeholders](#media-references-and-placeholders)),
   when not empty.
1. `--ref`: one per reference, in order.
1. `--<flag> <value>`: one per `arguments` key, as written.
1. `--count 1`: when the mode has a `count` flag and `arguments` does not set
   it ([Credits](#credits)).
1. `--title`: only when the prompt is empty, which the CLI requires for a run
   ("create --run needs explicit title when prompt is empty"). The title is
   the node's display name, such as "Video: Generate".
1. `--submit-id`: a new UUID for this run ([Paid runs](#paid-runs)).
1. `--credit-ceiling`: the node's `credit_ceiling`.

Nothing else is sent. A flag the person did not set takes Dreamina's default,
which Model: Info shows. The pack invents no flag and fills no prompt
template.

## Media, references, and placeholders

### Local media

A connected ComfyUI image, video, or audio is uploaded with each run:

1. It is encoded to a temporary file: PNG, MP4, or WAV
   ([Media formats](#media-formats)).
1. `resource upload --project-id <canvas> --file <path> --type <kind>` uploads
   it.
1. The returned resource ID is sent as `--ref res:<uuid>`.

The temporary files are deleted after the run. Nothing is remembered between
runs: F's owner dropped F's upload memory because a remembered link can
outlive its file. Uploads are free.

### References

`references` carries Dreamina canvas nodes and resources between this pack's
nodes:

- **What fills it.** Each paid node's `references` output holds what it made
  ([Outputs](#outputs)). Element: Add's output holds the Element node. A
  reference goes to the next node with no download or upload.
- **Node references.** A one-output node is sent as `--ref node:<node-id>`,
  which keeps the edge between the two nodes on the Dreamina canvas.
  Dreamina's skill prefers this for an existing canvas source.
- **Resource references.** A run with several outputs (a `count` above 1) has
  one node and several resources. Each is sent as `--ref res:<uuid>`, so the
  next node gets each output, not only the node's selected one.

### Order

The `--ref` order matters for `first_last_frame` (first frame, then last) and
for model slots. The order is:

1. `references`, in socket order;
1. `images`;
1. `videos`;
1. `audio`.

The help pages say so.

### Placeholders

A model can bind a reference to a place in the prompt, such as "the woman in
{{image1}} holds the bottle in {{image2}}". The CLI's own placeholders,
`{{node:<id>}}` and `{{res:<uuid>}}`, need IDs the person cannot know before
the run. So the node accepts:

| Placeholder        | Means                                       |
| ------------------ | ------------------------------------------- |
| `{{image1}}`, …    | The first, second, … item of `images`       |
| `{{video1}}`, …    | The items of `videos`                       |
| `{{audio1}}`, …    | The items of `audio`                        |
| `{{reference1}}`, … | The items of `references`                  |

Each is rewritten to the CLI's `{{res:…}}` or `{{node:…}}` form for that item,
which also stays in `--ref`. The CLI merges the two into one slot. A
placeholder for an item that is not connected is refused. Any other `{{…}}`
text is sent unchanged, so the CLI's own forms work as typed, and the CLI
refuses anything else, for free.

Whether `{{res:<uuid>}}` binds an uploaded file as the CLI's flag description
says is contract check C-6 in [21-test-runs.md](21-test-runs.md). If it does
not, placeholders are limited to `references` (node IDs), and the plans are
corrected.

## Outputs

| Output       | Type                    | Holds                                                                                   |
| ------------ | ----------------------- | --------------------------------------------------------------------------------------- |
| `images`     | IMAGE, as a list        | Every image, one `[1, H, W, 3]` tensor each, so sizes may differ                        |
| `video`      | VIDEO, as a list        | Every video, from the downloaded bytes                                                  |
| `audio`      | AUDIO, as a list        | Every audio file                                                                        |
| `references` | `DREAMINA_REFERENCES`   | What the run made, for the next Dreamina node: the node for one output, each resource for several |
| `result`     | STRING                  | The node as Dreamina's `node show` returns it, as JSON, plus the canvas link            |

`result` returns every part of the reply the pack has no socket for, so
nothing is dropped:

- the prompt as saved;
- the reference slots;
- each resource's ID, size, and format;
- the resources' `creditsAmount`, which is Dreamina's own field.

## Choosing a model

- **Starting values.** `model` and `arguments` start at values that run as
  they are, with only a prompt typed. Dreamina's lists mark `ratio`,
  `resolution`, and `duration` as required and give them no default, so a
  starting `arguments` must fill them. Each starting model:
  - is in the owner's live list ([research/catalog.md](research/catalog.md));
  - is current and inexpensive.

  | Node            | `model` starts at   | `arguments` starts at                                    |
  | --------------- | ------------------- | -------------------------------------------------------- |
  | Image: Generate | `seedream_5.0_lite` | `{"ratio": "1:1", "resolution": "2K"}`                   |
  | Video: Generate | `seedance_2.0_mini` | `{"ratio": "16:9", "resolution": "720p", "duration": 4}` |
  | Audio: Generate | `seed_audio_v1`     | `{"voice-name": "Jessie"}`                               |
  | Image: Upscale  | (no model)          | `{"resolution": "2K"}`                                   |

  These are the only model names in the code, and they restrict nothing.
  Part 0 of [21-test-runs.md](21-test-runs.md) checks each against Dreamina's
  quotes, and may switch it to an equally current, cheaper model of the same
  kind. Any switch is recorded in the changes table.
- **The `model` tooltip** says to copy the name from Model: Info or Dreamina's
  model picker.
- **Dreamina's defaults can be the expensive setting**, such as a high
  resolution or a long duration. The examples set the cheaper value
  explicitly, and each example's first run in
  [21-test-runs.md](21-test-runs.md) states its credits.

## The CLI on the person's computer

- **Never bundled.** The pack does not ship the binary. Reasons:
  - there is no license to redistribute it;
  - it is about 25 MB per platform;
  - the server refuses old clients
    ([research/terms.md](research/terms.md#4-rejected-routes)).
- **Found at each run.** In this order:
  1. `$DREAMINA_CANVAS_INSTALL_DIR/dreamina-canvas`;
  1. `dreamina-canvas` on the ComfyUI server's `PATH`;
  1. the installer's default folder: `~/.local/bin` on macOS and Linux,
     `%USERPROFILE%\bin` on Windows, with `.exe`.

  The installer's default folder matters because Comfy Desktop and launch
  agents often start ComfyUI without `~/.local/bin` on `PATH`.
- **Installed from the settings dialog.** **Install** runs ByteDance's
  official installer for the server's OS, from its fixed address
  ([16-frontend.md](16-frontend.md)):
  - macOS and Linux: `install.sh` run with `bash`;
  - Windows: `install.ps1` run with PowerShell.

  The dialog shows one button: **Install** when the CLI is missing,
  **Update** when it is installed. The README and ADVANCED give the one-line
  command, for people who prefer a terminal.
- **The version gate.**
  - The pack works with release 1.0.3 or later, the release its contract was
    read from.
  - On first use it runs `version` and `schema`, and checks that every
    command and flag it uses exists.
  - A missing command means the CLI changed, and the message says to update
    the extension.
  - A server answer with `requiredAction` `upgrade` means the CLI is too old.
    The message says to select **Update** in Dreamina Settings, which runs the
    same installer.
- **Never told to approve anything by itself.** The pack never passes
  `--yes`, never answers a prompt, and always passes `--non-interactive`.

## Sign-in and privacy

- **The CLI signs in, with Dreamina's device authorization.**
  1. **Sign in** in Dreamina Settings runs `auth login`.
  1. The dialog shows the link and code, and opens the link in a new tab.
  1. The person approves on dreamina.capcut.com.
  1. The pack waits with `auth wait` until the CLI reports a sign-in.
- **The credentials never reach the pack.** They stay in the OS credential
  store the CLI uses ([research/cli.md](research/cli.md#sign-in)). The pack
  has no API key, no credential file, and no credential setting.
- **The sign-in belongs to one OS user and one machine.** It is bound to the
  device. ComfyUI must run as the OS user who signed in.
- **Sign out** runs `auth logout`, which clears the CLI's local sign-in.
- **Guards.** Signing in, signing out, installing, and saving settings need a
  local, same-origin, single-user connection and the `X-Dreamina-Comfy: 1`
  header, as F's key routes do.
- **What leaves the computer.** Prompts, settings, and uploaded media go to
  Dreamina through the CLI, onto the person's own canvas, where the person
  can see and delete them on dreamina.capcut.com. The pack keeps no logs and
  no copy of prompts or outputs.
- **The cache token.** It is the signed-in account's `userId`, hashed, read
  once per process and again after a sign-in or sign-out. A new account runs
  paid nodes again instead of reusing another account's cached outputs. This
  is F's key-generation token, with the account in place of the key.

## The canvas

- Every node the pack makes lives on one Dreamina canvas named `ComfyUI`, in
  the person's account.
  - The canvas doubles as a history the person can browse on
    dreamina.capcut.com.
  - The canvas link is only in each `result`.
- The first run that needs the canvas creates it:
  - with `canvas create ComfyUI --project-id <new uuid>`, so a retry of the
    same call is safe;
  - then saves its `projectId` and `webUrl` in the state folder.
- **Every call names the canvas with `--project-id`.** The pack never uses or
  changes the CLI's "current canvas", which the person's own agent sessions
  may use.
- **Each run checks the saved canvas.** `find_canvas` looks for the saved
  canvas ID in `canvas ls`, which is free. When the person has deleted it, the
  saved ID is cleared and `create_canvas` makes a new `ComfyUI` canvas before
  anything is uploaded. The pack does not infer a deleted canvas from a
  failed save, because the CLI returns the same error for a missing canvas
  and a missing reference. A canvas deleted in the middle of a run fails that
  run, and nothing is sent again ([08-runs.md](08-runs.md)).

## Paid runs

- **One call per run.** `node create <kind> --run --credit-ceiling <n>
  --submit-id <uuid>` saves the node, gets Dreamina's quote, checks it against
  the ceiling, and runs. The pack does not pass `--wait`, so the call returns
  as soon as Dreamina accepts the run.
- **Recorded on acceptance.** Each run is written to the state folder as soon
  as Dreamina accepts it, before the first wait:
  - the submit ID;
  - the canvas;
  - the node ID;
  - the kind;
  - the model;
  - the time.

  The record is deleted once the outputs are downloaded. **Generation:
  Download** collects any recorded run.
- **The wait.** The pack waits with `operation wait <submitId> --project-id
  <canvas> --timeout 15s`, again and again, until a terminal state or the
  request timeout. Between waits it checks ComfyUI's cancel and moves the
  progress bar.
- **The outputs.** It reads the finished node with `node show`, downloads
  each resource with `resource download`, checks each file's byte count, and
  decodes it.
- **No cancel exists.** Dreamina has no cancel for an accepted generation;
  deleting the node does not stop it or refund it. So a ComfyUI cancel stops
  the wait, the record stays, and the message says the generation keeps
  running and is billed, and that **Generation: Download** collects it.
- **The submit call is never cut off.** A cancel that arrives during the
  `node create --run` call waits for that call to finish, so a run Dreamina
  accepted is always recorded. Only the read-only waits and downloads are
  stopped at once.
- **Nothing is sent twice.** Each run gets one new submit ID and one call.
  The pack never retries a run call:
  - a lost reply is checked read-only with the same submit ID, through
    `operation status`;
  - the CLI's own rule: "do not replay the run".

  Status reads, uploads, and downloads are free and are tried again within
  the request timeout.
- **One new run per run.** Every run sends one new generation, as the
  owner's rule says. There is no identical-run detection and no request
  hashing. **run number** sends the same run again.
- **One request timeout** (default 1,800 seconds) bounds a run from the first
  upload to the last download. On a timeout the record stays, and the message
  names **Generation: Download**. The run call itself always gets its own
  bound (`CALL_SECONDS["RUN"]`, 120 seconds), so a run started near the
  deadline is never cut off between Dreamina's acceptance and its reply.

## Credits

Dreamina's CLI will not run anything without an approval
([research/cli.md](research/cli.md#credits)):

- a credit ceiling;
- a token from `node confirm`;
- an interactive yes;
- or `--yes`, which "approves any amount".

So:

1. **`credit_ceiling` is the CLI's own flag.** Every paid node has a
   `credit_ceiling` number, sent as `--credit-ceiling`. It is not a
   pack-made cap: it is the approval Dreamina's own protocol requires, under
   its own name. The pack never sends `--yes`.
1. **A run above the ceiling costs nothing.** Dreamina stops it after the
   quote, with nothing charged. The node says so with Dreamina's
   `minimumCreditCeiling`: "This run needs 120 credits, more than its
   credit_ceiling of 100. Nothing was billed. Raise credit_ceiling to 120 or
   more to run it."
1. **The default ceiling makes the default model work**, as the owner's rule
   for defaults says.
   - It is the default model's quote at its defaults, measured in Part 0 of
     [21-test-runs.md](21-test-runs.md), rounded up to the next multiple of
     10.
   - The value is written into [09-node-image.md](09-node-image.md),
     [10-node-video.md](10-node-video.md),
     [11-node-audio.md](11-node-audio.md), and
     [12-node-upscale.md](12-node-upscale.md) from that run, and recorded in
     the changes table.
1. **`--count 1` is sent unless `arguments` sets `count`.** Dreamina's skill
   asks for one output per node by default. The server's own default might
   make several outputs and bill each. This is the one spending-safety flag
   the pack sends by itself. The owner's "empty sends nothing" rule allows
   such named exceptions.
1. **No prices anywhere else.** The README, ADVANCED, help pages, tooltips,
   and notes name no prices. The word "credits" appears where the person
   needs it, as "billed" does in F. The only number of credits the pack shows
   is Dreamina's own quote, in the refusal above.
1. **No balance display.** `auth account` returns no balance
   ([research/cli.md](research/cli.md#open-questions), question 9). If a later
   release adds one, that is a new decision.

A run that stops at the ceiling leaves its saved draft node on the canvas,
not run and not billed. The pack does not delete it: deleting a node needs
the person's explicit approval of each batch
([research/cli.md](research/cli.md#commands-the-pack-does-not-use)). ADVANCED
says so.

## Errors

- **One exception type.** `DreaminaError(code, message)` uses F's `ErrorCode`
  values. [08-runs.md](08-runs.md) maps every CLI failure.
- **The map reads structured fields only.** It uses the exit code, then
  `error.code`, `error.class`, `error.requiredAction`, `error.reason`,
  `error.retryable`, and `error.validation`. It never matches message text,
  which the skill forbids.
- **Messages.** Every message is a constant in `src/config/messages/`: a
  complete sentence that says what to do and where.
- **The CLI's own detail.** For an invalid input, the message adds the CLI's
  `validation.detail`, cleaned as F cleans reasons:
  - whitespace collapsed;
  - links removed;
  - token-shaped strings removed;
  - cut to 300 characters.
- **Errors with a fixed fix get their own message:**
  - CLI missing or too old;
  - not signed in;
  - over the ceiling;
  - an input the model refused;
  - a timeout;
  - a run that keeps going after a cancel.
- **Failures with no documented fields yet.** Too few credits, a plan that
  cannot use a model, and a safety refusal have no documented `error.code`,
  `class`, or `reason` in release 1.0.3. Until a test run captures them, they
  show Dreamina's own cleaned reason inside the general message. Each one
  captured gets its own message, recorded in the changes table.
- **A cancel.**
  - Before Dreamina accepts a run, a cancel shows as ComfyUI's
    `InterruptProcessingException`.
  - After acceptance, the node raises `DreaminaError` with code
    `INTERRUPTED` and the message that the generation keeps running, is
    billed, and can be collected with **Generation: Download**.
  - ComfyUI shows no text for its own interrupt, and the person must learn
    that the run goes on.
- **No logging.** No log files and no stack traces.

## Records and state

- F's record rules:
  - frozen dataclasses for in-process records;
  - Pydantic `Value` (`extra="forbid"`) for the pack's own files;
  - Pydantic `Reply` (`extra="ignore"`) for the CLI's JSON.
- Banned wire names become domain names through `Field(alias=…)`. The CLI's
  `data`, `serviceCode`, and `subjectBindings` hold the banned words `data`,
  `service`, and `bind` ([Banned words that shape names](#banned-words-that-shape-names)).
- The state folder holds:
  - `settings.json`;
  - `canvas.json`;
  - `generations/<submitId>.json`, one per recorded run.

  Each record carries `version`, and readers refuse unknown versions.
- The pack keeps only what the skill allows: public IDs (canvas, node, submit,
  resource). It never keeps tokens, signed links, credit tokens, or the
  device code ([research/cli.md](research/cli.md#local-state-the-cli-keeps)).

## Media formats

- **Uploads.**
  - Images are uploaded as PNG, never resized.
  - Audio is uploaded as 16-bit WAV.
  - Video is uploaded as MP4 through ComfyUI's own video code, which copies
    the streams of a video that is already an MP4 file.
  - Contract check C-4 confirms WAV; if Dreamina refuses WAV, audio is
    uploaded as MP3 through PyAV and the plans are corrected.
- **Image outputs** are lists (`is_output_list=True`), one `[1, H, W, 3]`
  tensor each.
- **Video outputs** are `InputImpl.VideoFromFile` over the downloaded bytes in
  memory.
- **Audio outputs** are decoded through PyAV into ComfyUI's AUDIO form.
- **Conversions.** Every one is ComfyUI's own helper, as in F's
  `src/comfy/media.py`. ComfyUI's API-node request helpers are never used.

## Subprocesses and concurrency

- **One way to call the CLI.** Every CLI call goes through one function,
  `send_command`, in `src/dreamina/cli.py`. It starts
  `asyncio.create_subprocess_exec(binary, "--format", "json",
  "--non-interactive", *arguments)`:
  - stdin is closed;
  - stdout and stderr are read with byte caps;
  - the run's remaining timeout applies;
  - the server's own environment is passed unchanged, so the CLI finds the
    person's credentials.
- **The reply.** `send_command` parses the one JSON object the CLI prints, on
  stdout for success and stderr for failure, and returns the exit code with
  it.
- **No retries, no parallel cap.** ComfyUI runs one prompt at a time. Model
  checks of several nodes may run at once, and share one read per kind.
- **No Python dependency is added.** `asyncio` and Pydantic do everything.
  The installer download uses `aiohttp`, which ComfyUI supplies.

## Browser code

F's, re-valued:

- TypeScript in `web/scripts/`, bundled by esbuild into the committed
  `web/extension.js` and `web/extension.css`;
- one settings dialog with three parts: **Dreamina CLI**, **Account**, and
  **Request limits**, then a footer with **Reload settings**
  ([16-frontend.md](16-frontend.md));
- valibot for every local route reply;
- all text in `web/scripts/text.ts`.

Generation: Download's list of records is F's plain dropdown, refreshed with
ComfyUI's own **R**. No node has a dynamic dropdown.

## Documentation, notes, and examples

- **README and ADVANCED.** `README.md` and `ADVANCED.md` take F's section
  shapes and lengths, with nothing beyond them
  ([18-documentation.md](18-documentation.md)).
- **Help pages.** One per node in `web/docs/<node id>.md`, in F's checked
  format.
- **Examples.** Generated from Python descriptions by F's generator:
  - scenario workflows;
  - a note above every group;
  - a subgraph for each step after the inputs, each shipped as a blueprint in
    `subgraphs/`

  ([17-scripts-and-workflows.md](17-scripts-and-workflows.md)).
- **Start Here.** Every example's **Start Here** note starts with "Sign in to
  Dreamina in **ComfyUI menu → Extensions → Dreamina → Dreamina Settings**."
- **No media files ship.** Most examples make their own inputs with Dreamina
  models, so they run with no uploads. The rest say what to load in **Start
  Here**.
- **How notes and docs are written.** F's rules:
  - everyday words first, in short sentences, for a person who uses ComfyUI
    but has never used Dreamina's CLI;
  - flag names written exactly, in code style, because the person types them
    in `arguments`.
- **Every example is run once** before release, with the credits stated
  ([21-test-runs.md](21-test-runs.md)).

## Brand and images

- **The image set is F's:**
  - four badges;
  - the banner;
  - the logo, which is also the Registry icon;
  - the node map;
  - three screenshots.
- **The layout is the family design** the owner asked F to return to. The
  colors combine BytePlus's blue, OpenRouter's indigo and electric yellow,
  and Dreamina's star gradient
  ([research/brand.md](research/brand.md#5-this-packs-palette)).
- **The mark** is a redrawn four-point star in Dreamina's gradient, with a
  yellow socket, as the owner asked for Dreamina's star in the banner. The
  owner chose the redraw over Dreamina's own logo on 2026-10-17
  ([19-brand-assets.md](19-brand-assets.md)).
- **The banner title** is "Dreamina", with the subtitle "Image, video, and
  audio models, inside ComfyUI." The owner chose it on 2026-10-17.

## Tooling

F's tooling, copied whole and re-valued ([03-repository-setup.md](03-repository-setup.md)):

- `quality/` (220 files), `.mise/` (35 tasks), `.githooks/`, `rules/`, root
  configs, and `scripts/`;
- Python 3.12, uv, bun, ruff, basedpyright strict, import-linter, the custom
  AST rules, ESLint, stylelint, the security scanners, and the license checks.

Two of F's values have no Dreamina counterpart:

- **gitleaks.** There is no API key, so F's key rule is dropped. The gitleaks
  config keeps only the default rules.
- **semgrep.** F's secrets rule for `FAL_KEY` is dropped.

## Banned words that shape names

`quality/config/naming/terms.json` bans words that Dreamina's CLI uses. Local
names avoid them. Wire fields keep the CLI's spelling through Pydantic
aliases.

| CLI word or field           | Banned term | Local name                                                                                   |
| --------------------------- | ----------- | -------------------------------------------------------------------------------------------- |
| `data` (envelope)           | `data`      | `payload`, with `Field(alias="data")`                                                        |
| `serviceCode`               | `service`   | `status_code`, with an alias                                                                 |
| `subjectBindings`           | `bind`      | `subjects`, with an alias                                                                    |
| `partialData`               | `data`      | `partial`, with an alias                                                                     |
| `vipResolutions`            | `resolution` | `membership_resolutions`, with an alias                                                     |
| `--resolution`              | `resolution` | Only ever a key inside `arguments` (a string), so no identifier needs it                    |
| "model catalog"             | `catalog`   | Modules and functions say `models`, `listing`, or `model_list`                               |
| `info` in Model: Info       | `info`      | `ModelInfo` keeps F's naming exception for its class                                         |
| "fetch" a download          | `fetch`     | `download_…`                                                                                 |
| "smart upscale" (`pro`)     | `smart`     | Only in help text                                                                            |

## Live-shopping

The owner's `comfyui-live-shopping` pack uses F and O today. Adding Dreamina
there is a separate, later change, planned in
[23-live-shopping-provider.md](23-live-shopping-provider.md). Nothing in
live-shopping changes while this pack is built.

## Out of scope

| Left out                                                  | Why                                                                                                        |
| --------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| Timelines (`node create timeline`)                        | ComfyUI joins clips with its own video nodes; whether a timeline downloads as one file is not documented   |
| Text nodes as context (`node create text`)                | The prompt box holds the text                                                                              |
| Editing an existing Dreamina node (`node edit`)           | Every run is one new generation                                                                            |
| Deleting nodes                                             | Needs the person's explicit approval per batch; the person does it on the canvas                          |
| The mainland China (Jimeng) service                       | This release has no region flag; the global CLI signs in international accounts only                      |
| CLI profiles (`--profile`)                                | One sign-in per OS user is enough                                                                          |
| A credit balance                                          | The CLI exposes none                                                                                       |
| Video upscale, lip sync onto an existing video, avatars   | Not in the CLI                                                                                             |
| A model list, prices, or a spending guard in the pack     | The owner's rules                                                                                          |
| Automated tests and logging                               | The owner's rules                                                                                          |

## Decisions the owner should confirm

Decided by the owner on 2026-10-17:

- **The mark:** the redrawn star, not Dreamina's own logo.
- **The banner title:** "Dreamina".
- **The pack may create canvases and drafts in the owner's account freely**
  for its runs and tests.
- **Installing the CLI:** the owner kept the button. **Install** in Dreamina
  Settings runs ByteDance's installer, and **Update** runs it again. The
  dialog has three parts, with no button to check again, no command, and no
  canvas link. The one-line command is in the README and ADVANCED.

Still open:

| Decision                                  | Recommended                                                                         | Alternative                                                                  |
| ----------------------------------------- | ----------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| Element: Add                              | Keep: it is free and keeps a host or product consistent across shots                | Drop it; references from earlier runs already carry identity                 |
| `credit_ceiling` default                  | The default model's quote at its defaults, rounded up to the next 10               | One shared default, such as 100, for every node                              |
| Placeholders                              | `{{image1}}`, `{{video1}}`, `{{audio1}}`, `{{reference1}}`                          | None; references only by order                                               |
| Install folder and Registry ID            | `dreamina`                                                                          | `comfyui-dreamina`, as B keeps `comfyui-byteplus`                            |
