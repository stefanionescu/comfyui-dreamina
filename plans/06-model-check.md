# Model Check

This plan builds the check every generation node makes before it pays:

1. It reads the person's live model list from the Dreamina CLI.
1. It matches the typed name against it.
1. It chooses the mode, and the mode entry whose reference limits fit what is
   connected.
1. It checks every `arguments` key and value against that entry.
1. It builds the mode and flag part of the run call.

Every refusal comes before anything is uploaded or billed.

**The person types any model name.** Nothing in the code lists, limits, or
filters Dreamina's models. The typed name and every setting are checked
against the person's own list when ComfyUI queues the workflow and again when
the node runs. A model Dreamina adds works the moment its name is typed. The
only model names in the code are the starting values of the three generation
nodes' `model` boxes, in `DEFAULT_MODELS`, which the person replaces freely
([01-decisions.md](01-decisions.md#how-the-nodes-cover-every-model)).

It is the counterpart of `F/plans/06-model-check.md` in the fal pack
(`F=/Users/dr_stone/Documents/work/comfyui-fal`, commit `cef8b6e`). F reads
one model's OpenAPI document from fal's listing. This plan reads one
`model list --type <kind>` reply per kind, which already holds every mode's
flags, allowed values, and reference limits, so there is no schema parser.

Readers: the engineer who writes `src/config/models.py`,
`src/config/inputs.py`, `src/config/messages/{models,inputs}.py`,
`src/types/models.py`, and `src/dreamina/{models,modes,arguments}.py`, and the
authors of [07-media.md](07-media.md), [08-runs.md](08-runs.md), and
[15-node-model-info.md](15-node-model-info.md), which call them.

The facts come from the owner's captures of 2026-10-16
([research/catalog.md](research/catalog.md),
`research/captures/model-list-{image,video,audio}.json`, and
`research/captures/voices-*.json`), the CLI's `schema`
(`research/captures/schema.json`), and the skill, cited as
[research/cli.md](research/cli.md) does. Nothing is built yet.

It uses from [05-foundation.md](05-foundation.md): `Json`, `Kind`,
`MediaKind`, and `Reply` (`src/types/__init__.py`); `DreaminaError` and
`ErrorCode`; `parse_json` and `JSON_SYNTAX`. It uses from
[08-runs.md](08-runs.md) Part A: `send_command(arguments, timeout_seconds)`,
`CliResult` with its exit code and its reply, whose success JSON is
`result.reply.payload`, `build_failure(result, context)`, and
`validate_cli()`. It shares `MEDIA_TYPES` with [07-media.md](07-media.md).

## Contents

- [Why a live check](#why-a-live-check)
- [Decisions this plan makes](#decisions-this-plan-makes)
- [When each step is built](#when-each-step-is-built)
- [Step 1: Configuration and messages](#step-1-configuration-and-messages)
- [Step 2: Records](#step-2-records)
- [Step 3: Read the model list](#step-3-read-the-model-list)
- [Step 4: Choose the mode](#step-4-choose-the-mode)
- [Step 5: Check and build the arguments](#step-5-check-and-build-the-arguments)
- [Step 6: The queue-time check](#step-6-the-queue-time-check)
- [Four runs walked through](#four-runs-walked-through)
- [Step 7: Allowlist and commits](#step-7-allowlist-and-commits)
- [Live check](#live-check)
- [When Dreamina changes](#when-dreamina-changes)
- [Names this plan uses from other plans](#names-this-plan-uses-from-other-plans)

## Why a live check

[01-decisions.md](01-decisions.md#checking-a-model-before-paying) gives the
design. In short:

- **Dreamina's models do not share settings.** Seedream takes `2K` and `4K`,
  GPT Image 2.5 also takes `1K`, Seedance 2.0 Fast takes only `720p`, and
  Seedance 2.5 takes 4 to 30 seconds where the others stop at 15
  ([research/catalog.md](research/catalog.md#image-models),
  [research/catalog.md](research/catalog.md#video-models)). So each node
  takes the model as text and its settings as `arguments` under the CLI's own
  flag names.
- **The live list holds every constraint.** `model list` returns, per mode,
  each flag with `required`, `values`, `min`, `max`, `step`, `minLength`, and
  `maxLength`, and the reference limits per media type
  ([02-dreamina-contract.md](02-dreamina-contract.md#model-discovery)).
- **A refusal after the save leaves a draft on the canvas.** The CLI saves
  the node before it quotes and runs, so the pack refuses locally what the
  list says the server would refuse. Each check reads a field the list
  returned and copies no rule of Dreamina's.
- **The list is free and fast.** One call per kind returns every model of
  that kind, so the pack reads it once per ComfyUI process and shares the
  read between nodes, as F shares its model reads.

## Decisions this plan makes

| Question | Decision | Why |
| -------- | -------- | --- |
| Which names a node takes | Any name equal, ignoring case, to a model's canonical `model` or one of its `aliases` in the live list of the node's kind. The canonical name is sent. | The skill: "`aliases` only helps match … never submit an alias as the model" ([research/cli.md](research/cli.md#model-discovery)) |
| Substring matches | Never. A miss is refused with the closest canonical names by `difflib` ratio. | The skill: "never select the first item by default" ([research/cli.md](research/cli.md#model-discovery)) |
| A model of another kind | Refused, naming the node that runs it, after the name misses in this kind's list | [01-decisions.md](01-decisions.md#how-the-nodes-cover-every-model) |
| What is kept | Each kind's parsed list, in memory, for the life of the process | Free, and the same for every node of the kind |
| What is read again | A kind's list, once, when a name misses in a list read earlier in the process | A model Dreamina added since then is found |
| Flag names in `arguments` | The list's `flag` without its two leading dashes: `ratio`, `resolution`, `duration`, `count`, `voice-name`, `scenario`, `prompt`. A key written with dashes is refused with the right spelling. | The capture writes `--ratio` ([research/catalog.md](research/catalog.md#what-the-lists-show)) |
| Selection keys | `mode` and `scenario` choose the mode entry and are never sent as flags of their own. `--mode` and `--scenario` come from the chosen entry. | `--mode` is never listed; `--scenario` is listed with the entry's one value |
| A mode listed twice | The first entry, in list order, whose total and per-type reference limits fit what is connected | Every video model lists `first_last_frame` twice: two images, then one image ([research/catalog.md](research/catalog.md#what-the-lists-show)) |
| Reference refusals | Made by 07's `validate_references` against the entry chosen here. This plan refuses only when several entries of one mode all miss, and names each entry's limits. | [07-media.md](07-media.md#validate_references) owns the counts; [01-decisions.md](01-decisions.md#how-the-mode-is-chosen) asks for each entry's limits |
| An Element in the limits | Counted under `MEDIA_TYPES["element"]`, `image`, as 07 counts it | The lists name only `image`, `video`, and `audio`; run C-15 settles it |
| Values | Checked against `values` exactly as listed, case included, and against `min`, `max`, `step`, `minLength`, and `maxLength` | The lists mix `720p`, `4K`, and `4k` ([research/catalog.md](research/catalog.md#video-models)); the server's spelling is the list's |
| Value types | JSON text and numbers are sent as text. A whole number has no `.0`. `true`, `false`, `null`, lists, and objects are refused. | No generation flag of `node create image`, `video`, or `audio` is a boolean (schema: `node create image`, `node create video`, `node create audio`); every listed flag takes text or a number |
| `--count 1` | Added when the chosen entry lists `--count` and `arguments` does not set it | [01-decisions.md](01-decisions.md#credits). No audio entry lists `--count`, because the CLI has none for audio (schema: `node create audio`). |
| `--prompt` | Never built here. 08 sends it after 07's `format_prompt`. This plan checks it: one place only, required when the entry says so, within the entry's lengths. | `format_prompt` needs the uploads' IDs, which exist only after the checks ([04-architecture.md](04-architecture.md#how-a-paid-run-flows)) |
| Membership fields | Kept for Model: Info; never used to refuse | [01-decisions.md](01-decisions.md#checking-a-model-before-paying) |
| File size and length limits | Not checked here | `model list` does not carry them; the server refuses an oversized file at save, before any charge ([research/catalog.md](research/catalog.md#file-limits)) |
| Voices | Not checked against `voice list` | The server checks a voice for free; Model: Info lists the voices ([15-node-model-info.md](15-node-model-info.md)) |
| `music` | Supported as any mode is: chosen when it is a model's only mode, or when `arguments` sets `"mode": "music"` | It is a CLI mode; no model on the owner's list has it ([research/catalog.md](research/catalog.md#audio-models)) |

## When each step is built

All seven steps are the **Model check** milestone of the
[build order](README.md#build-order). 08 Part A's runner, failure map, and
`validate_cli` ship earlier, in the Foundation milestone with
[05-foundation.md](05-foundation.md#when-each-part-is-built). This milestone
holds this plan alone. It is free and makes no paid run.

Some names this plan fixes have their first user in a later milestone. A
constant or message arrives with the milestone that first reads it, so the
repository's checks never meet an unused name:

| Names | Added in | First user |
| ----- | -------- | ---------- |
| `DEFAULT_ARGUMENTS`, `SINGLE_VALUE`, and `src/config/inputs.py` without `DEFAULT_CEILINGS` | Media and runs | 08 Part B's `GenerateNode` and `PaidNode` |
| `DEFAULT_CEILINGS`, one key per node milestone | Image, Audio, and Video and downloads | Each node's `default_ceiling` ([09](09-node-image.md), [11](11-node-audio.md), [10](10-node-video.md)) |

The opposite case: `MEDIA_TYPES` is 07's constant, but `choose_mode` reads it
one milestone before 07 is built. So this plan creates `src/config/media.py`
holding `MEDIA_TYPES` alone, with 07's docstring, comment, and value, and
07's Step 1 adds its other constants to the module
([Step 1](#step-1-configuration-and-messages)).

## Step 1: Configuration and messages

### `src/config/models.py`

Create it with the docstring "The names the model check reads from
Dreamina's model list, and each generation node's starting values." Every
constant has its comment above it. The constants carry no annotations:
`src.config` may not import `Kind` or `MediaKind`
([04-architecture.md](04-architecture.md#import-linter-contracts)).

```python
# The generation nodes, by what their models make, in menu order; each is a model list type.
KINDS = ("image", "video", "audio")

# The node that runs each kind, as a refusal names it.
KIND_NODES = {
    "image": "Image: Generate",
    "video": "Video: Generate",
    "audio": "Audio: Generate",
}

# The starting value of each node's model box. The person types any other name; these are the only model names here.
DEFAULT_MODELS = {
    "image": "seedream_5.0_lite",
    "video": "seedance_2.0_mini",
    "audio": "seed_audio_v1",
}

# The starting value of each node's arguments box: the required flags of the default model's first mode.
DEFAULT_ARGUMENTS = {
    "image": '{"ratio": "1:1", "resolution": "2K"}',
    "video": '{"ratio": "16:9", "resolution": "720p", "duration": 4}',
    "audio": '{"voice-name": "Jessie"}',
}

# The modes a node chooses by itself, by kind and role. Any other mode a model lists runs when arguments sets it.
MODES = {
    "image": {"TEXT": "t2i", "IMAGES": "i2i"},
    "video": {"TEXT": "t2v", "FRAMES": "first_last_frame", "MULTIMODAL": "m2v"},
    "audio": {"SPEECH": "tts"},
}

# The speech scenarios a node chooses by itself: reading text when nothing is connected, dubbing when something is.
SCENARIOS = {"READING": "text-reading", "DUBBING": "omni-dubbing"}

# The arguments keys that choose the mode entry; they are never sent as flags of their own.
SELECTION_KEYS = {"MODE": "mode", "SCENARIO": "scenario"}

# The flag the prompt box fills.
PROMPT_FLAG = "prompt"

# The flag that sets how many outputs a run makes, and the value sent when arguments does not set it.
COUNT_FLAG = "count"
COUNT_VALUE = "1"

# The dashes model list writes before each flag name, and the pack writes back when it builds the call.
FLAG_PREFIX = "--"

# The most images first_last_frame takes: the first frame, then the last.
FRAME_IMAGES = 2

# How many close model names a refusal suggests.
SUGGESTION_COUNT = 3

# The CLI call that lists one kind's models; the kind follows it.
LIST_COMMAND = ("model", "list", "--type")

# Seconds one model list read may take. A read takes well under a second; this bounds a CLI that stops answering.
LIST_TIMEOUT_SECONDS = 60
```

Why these values:

- **`DEFAULT_ARGUMENTS`.** The lists mark `--ratio`, `--resolution`, and
  `--duration` required with no default, and text reading marks
  `--voice-name` required. An empty box would refuse the default model, and
  the owner's rule is that a node's defaults make its default model work. The
  values are the smallest each default model lists: `2K` for Seedream 5.0
  Lite, `720p` and 4 seconds for Seedance 2.0 Mini, and `Jessie`, a voice in
  `voices-seed_audio_v1-page-0.json`.
- **`MODES`.** Only the modes the node chooses by itself are named. A model's
  other modes, such as `music`, run when `arguments` sets them or when they
  are the model's only mode, so they need no constant.

`__all__` lists the 15 names in ASCII order. `DEFAULT_ARGUMENTS` arrives
with 08 Part B, whose `GenerateNode.build_schema` reads it by kind
([When each step is built](#when-each-step-is-built)).

### `src/config/media.py`

Create it with 07's docstring, "How local media is written for upload, how
references reach the CLI, and how outputs are sorted.", holding only 07's
`MEDIA_TYPES`, with 07's comment and value
([07-media.md](07-media.md#step-1-media-constants)):

```python
# The mediaType the live model list counts each kind of reference as. The lists name no Element type, and an Element
# is expected to count as an image (run C-15).
MEDIA_TYPES = {
    "image": "image",
    "video": "video",
    "audio": "audio",
    "element": "image",
}
```

`__all__ = ["MEDIA_TYPES"]`. 07's Step 1 adds its other 11 constants to this
module and to its `__all__`.

### `src/config/inputs.py`

Create it in the Media and runs milestone, ported from
`F/src/config/inputs.py:1-36`, with the docstring "Names and tooltips of the
inputs every generation node shares."

```python
# The inputs every generation node can show, in node order: sockets first, then the short values, then the text boxes.
INPUT_NAMES = {
    "IMAGES": "images",
    "VIDEOS": "videos",
    "AUDIO": "audio",
    "REFERENCES": "references",
    "MODEL": "model",
    "CREDIT_CEILING": "credit_ceiling",
    "RUN_NUMBER": "run_number",
    "PROMPT": "prompt",
    "ARGUMENTS": "arguments",
}

# The run number's default and range; changing it sends the same run again.
RUN_NUMBER = {"DEFAULT": 0, "MIN": 0, "MAX": 2**31 - 1}

# The credit ceiling's range: the CLI takes any whole number from 0, and ComfyUI's number widget stops at 2**31 - 1.
CREDIT_CEILING_RANGE = {"MIN": 0, "MAX": 2**31 - 1}

# Tooltips of the inputs every generation node shares, in plain words.
TOOLTIPS = {
    "IMAGES": "Images uploaded with the run. Create List joins several. In the prompt, {{image1}} is the first.",
    "VIDEOS": "Videos uploaded with the run. Create List joins several. In the prompt, {{video1}} is the first.",
    "AUDIO": "Audio clips uploaded with the run. Create List joins several. In the prompt, {{audio1}} is the first.",
    "REFERENCES": (
        "Outputs of other Dreamina nodes and Elements, sent with no upload, before any image, video, or audio. In "
        "the prompt, {{reference1}} is the first."
    ),
    "MODEL": (
        "The Dreamina model to run, by its exact name. A name that is not in your Dreamina model list is refused "
        "before paying, with the closest names."
    ),
    "CREDIT_CEILING": "The most credits this run may cost. Dreamina stops a run that costs more, and nothing is billed.",
    "RUN_NUMBER": "Change it to send the same run again.",
    "PROMPT": (
        "The prompt, sent as written. Point at a connected input with {{image1}}, {{reference1}}, and so on. Leave "
        "it empty to send none."
    ),
}

# The arguments box's tooltip, by kind. A speech voice fits only text reading, so the audio tooltip says when to clear
# it.
_ARGUMENTS = (
    'The model\'s settings as a JSON object, under Dreamina\'s flag names, such as {"duration": 5}. Model: Info lists '
    'them. Set "mode" to choose the mode.'
)
ARGUMENTS_TOOLTIPS = {
    "image": _ARGUMENTS,
    "video": _ARGUMENTS,
    "audio": (
        'The model\'s settings as a JSON object, under Dreamina\'s flag names, such as {"voice-name": "Jessie"}. A '
        "voice applies to text reading, when nothing is connected. For omni dubbing, or a model that lists no "
        "voice-name, leave {}."
    ),
}
```

`DEFAULT_CEILINGS`, in the same module, has one key per kind, and each key
arrives with its node's milestone, as 08's `GenerateNode` reads it through
each node's `default_ceiling`. Each value is the default model's
quote at its starting `arguments`, rounded up to the next multiple of 10,
from Part 0's price sweep in [21-test-runs.md](21-test-runs.md). The sweep
records each quote in [research/catalog.md](research/catalog.md#prices), and
the value is written here and in the README's changes table
([01-decisions.md](01-decisions.md#credits)):

| Key | The quote it is made from | Quote on 2026-10-17 | Value |
| --- | ------------------------- | ------------------- | ----- |
| `"image"` | IMG-D: `seedream_5.0_lite`, `t2i`, `{"ratio": "1:1", "resolution": "2K"}`, `--count 1` | 6 credits | 10 |
| `"video"` | VID-D: `seedance_2.0_mini`, `t2v`, `{"ratio": "16:9", "resolution": "720p", "duration": 4}`, `--count 1` | 16 credits | 20 |
| `"audio"` | AUD-D: `seed_audio_v1`, `tts` `text-reading`, `{"voice-name": "Jessie"}`, as the sweep job `seed_audio_v1+tts+text-reading` sends it | 12 credits | 20 |

Its comment: "The starting credit_ceiling of each generation node: its default
model's quote at its starting arguments, rounded up to the next 10, from
Part 0's price sweep." If Part 0 switches a default model, as
[research/catalog.md](research/catalog.md#defaults) allows, the same change
updates `DEFAULT_MODELS`, `DEFAULT_ARGUMENTS`, and `DEFAULT_CEILINGS`.

`INPUT_NAMES` keeps F's dict form, which `scripts/nodes/schema.py` reads
([04-architecture.md](04-architecture.md#srcconfig)), and
[12-node-upscale.md](12-node-upscale.md) reads these keys too. The tooltips
are not filled with `str.format`, so `{{image1}}` shows as typed: it is the
placeholder's own spelling
([01-decisions.md](01-decisions.md#placeholders)). The `MODEL` tooltip names
the refusal instead of Model: Info, because Model: Info reads a model the
person has already named. `ARGUMENTS_TOOLTIPS` is keyed by kind, as
`DEFAULT_ARGUMENTS` is: the audio box starts with a voice, which only text
reading takes, so its tooltip says when to leave the box as `{}`
([11-node-audio.md](11-node-audio.md#decisions-this-plan-makes)).
`__all__` lists `ARGUMENTS_TOOLTIPS`, `CREDIT_CEILING_RANGE`,
`DEFAULT_CEILINGS` (from the Image milestone), `INPUT_NAMES`, `RUN_NUMBER`,
and `TOOLTIPS`.

### `src/config/messages/models.py`

Create it with the docstring "Messages about finding a model in the person's
Dreamina model list, choosing its mode, and checking its flags." Every
message starts with a capital letter and never with a model or flag name,
which are lowercase. These messages hold no literal braces. The refusals that
name a mode say "Mode {mode} of this model", as 07's do.

| Constant | Code | Text |
| -------- | ---- | ---- |
| `MODEL_EMPTY` | `INVALID_INPUT` | `Type a Dreamina model name in model, such as {example}.` |
| `MODEL_UNKNOWN` | `UNAVAILABLE` | `The model {model} is not in your Dreamina model list. The closest names are {names}. Copy one into model.` |
| `MODEL_AMBIGUOUS` | `INVALID_INPUT` | `The name {model} matches more than one Dreamina model: {names}. Type one of them in model.` |
| `MODEL_KIND` | `INVALID_INPUT` | `The model {model} makes {made}, so it runs in {node}, not in {this}.` |
| `MODEL_LIST_EMPTY` | `UNAVAILABLE` | `Your Dreamina model list holds no {made} models. Check that your Dreamina plan includes them.` |
| `MODEL_LIST_UNREADABLE` | `TRANSPORT` | `The Dreamina CLI sent a model list this extension cannot read. Update the extension, or try again later.` |
| `MODE_UNKNOWN` | `INVALID_INPUT` | `The model {model} has no mode named {mode}. Set "mode" in arguments to one of its modes: {modes}.` |
| `MODE_NOT_OFFERED` | `INVALID_INPUT` | `The connected inputs call for the {mode} mode, which the model {model} does not have. Set "mode" in arguments to one of its modes: {modes}.` |
| `SCENARIO_UNKNOWN` | `INVALID_INPUT` | `The model {model} has no scenario named {scenario}. Set "scenario" in arguments to one of: {scenarios}.` |
| `SCENARIO_NOT_OFFERED` | `INVALID_INPUT` | `The connected inputs call for the {scenario} scenario, which the model {model} does not have. Set "scenario" in arguments to one of: {scenarios}.` |
| `REFERENCES_NO_ENTRY` | `INVALID_INPUT` | `No entry of mode {mode} of this model takes what is connected ({connected}). Its entries take {limits}. Change the inputs, or set another mode in arguments.` |
| `ARGUMENT_UNKNOWN` | `INVALID_INPUT` | `The model {model} has no flag named {flag}. Its flags are {flags}.` |
| `ARGUMENT_DASHES` | `INVALID_INPUT` | `Write the flag {flag} without its leading dashes, as "{name}".` |
| `FLAG_NOT_IN_MODE` | `INVALID_INPUT` | `Mode {mode} of this model has no flag named {flag}. Its flags are {flags}. Remove it from arguments, or set another mode.` |
| `FLAG_REQUIRED` | `INVALID_INPUT` | `Set "{flag}" in arguments. Mode {mode} of this model needs it, and Model: Info lists its allowed values.` |
| `VALUE_TYPE` | `INVALID_INPUT` | `Write {flag} as text or a number, not {shape}.` |
| `VALUE_CHOICES` | `INVALID_INPUT` | `The flag {flag} does not take {value}. Write one of: {values}.` |
| `VALUE_NUMBER` | `INVALID_INPUT` | `The flag {flag} takes a number, and it has {value}.` |
| `VALUE_TOO_LOW` | `INVALID_INPUT` | `The flag {flag} takes {minimum} or more, and it has {value}.` |
| `VALUE_TOO_HIGH` | `INVALID_INPUT` | `The flag {flag} takes at most {maximum}, and it has {value}.` |
| `VALUE_STEP` | `INVALID_INPUT` | `The flag {flag} takes steps of {step}, so {value} cannot be sent. Write {lower} or {upper}.` |
| `VALUE_TOO_SHORT` | `INVALID_INPUT` | `The flag {flag} takes at least {minimum} characters, and it has {count}.` |
| `VALUE_TOO_LONG` | `INVALID_INPUT` | `The flag {flag} takes at most {maximum} characters, and it has {count}.` |

The Code column is the `ErrorCode` each refusal raises with
([05-foundation.md](05-foundation.md#step-9-errors)). The message modules
hold only text; the code is chosen where the refusal is raised.
[07-media.md](07-media.md#step-3-reference-and-placeholder-messages) adds the
reference messages (`REFERENCES_ANY_OF`, `REFERENCES_ELEMENT_FRAME`,
`REFERENCES_EXCLUSIVE`, `REFERENCES_NONE`, `REFERENCES_TOTAL`,
`REFERENCE_KIND_COUNT`, `REFERENCE_KIND_REFUSED`, and `VOICE_COUNTED`) to this
module in its own milestone. This plan does not define them.

The pieces the messages are built from, in the same module:

```python
# What each kind of model makes, as the refusals name it.
KIND_NAMES = {"image": "images", "video": "videos", "audio": "audio"}

# A mode with a scenario, as the refusals name it, such as "tts (text-reading)".
MODE_LABEL = "{name} ({scenario})"

# One mode entry's reference limits, as REFERENCES_NO_ENTRY lists them, such as "1 to 1 references (image 1 to 1)".
REFERENCE_LIMITS = "{minimum} to {maximum} references ({types})"

# One media type's limits inside REFERENCE_LIMITS, and the text for an entry that enables none.
TYPE_LIMITS = "{media} {minimum} to {maximum}"
NO_MEDIA = "no media"

# What is connected, as REFERENCES_NO_ENTRY says it: one count per media type, or nothing.
CONNECTED_COUNT = "{media} {count}"
NOTHING_CONNECTED = "nothing"
```

How the parts are filled:

- `{example}` is `DEFAULT_MODELS[kind]`, or `DEFAULT_MODELS["image"]` when
  Model: Info passes no kind.
- `{mode}` is `entry.label` ([Step 2](#step-2-records)): the
  name, or `MODE_LABEL` for an entry with a scenario. 07's messages use the
  same function.
- `{names}`, `{modes}`, `{scenarios}`, `{values}`, and `{flags}` join their
  items with ", ". `{modes}` names each distinct mode once. `{flags}` is the
  flag names without their dashes, in list order: for `ARGUMENT_UNKNOWN`
  every name `validate_argument_names` allows except `mode` and `scenario`,
  and for `FLAG_NOT_IN_MODE` the chosen entry's flags.
- `{limits}` joins one `REFERENCE_LIMITS` per entry with " or ", each with
  its `TYPE_LIMITS` joined by ", ", or `NO_MEDIA`. `{connected}` joins one
  `CONNECTED_COUNT` per media type with a count above zero, or is
  `NOTHING_CONNECTED`.
- Numbers are written as `build_flags` writes values: a whole number without
  `.0`.
- `{made}` is `KIND_NAMES[kind]`, or `ANY_KIND` ("images, videos, or
  audio") when Model: Info passes no kind.

Filled examples:

- `The model seedance 2 fast is not in your Dreamina model list. The closest names are seedance_2.0_fast, seedance_pro_fast, seedance_2.0. Copy one into model.`
- `The model seedance_2.0 makes videos, so it runs in Video: Generate, not in Image: Generate.`
- `The flag resolution does not take 1080p. Write one of: 720p.`
- `No entry of mode first_last_frame of this model takes what is connected (image 3). Its entries take 2 to 2 references (image 2 to 2) or 1 to 1 references (image 1 to 1). Change the inputs, or set another mode in arguments.`

### `src/config/messages/inputs.py`

Create it with the docstring "Refusals of a generation node's prompt,
arguments, placeholders, and connected values, made before anything is
uploaded or paid." Ported from `F/src/config/messages/inputs.py:3-8, 54,
73-79` for the shared parts:

| Constant | Code | Text | Added in |
| -------- | ---- | ---- | -------- |
| `ARGUMENTS_INVALID` | `INVALID_INPUT` | `The arguments input is not valid JSON. Write a JSON object, such as {{"ratio": "16:9"}}.` | This milestone |
| `ARGUMENTS_SHAPE` | `INVALID_INPUT` | `The arguments input holds {shape}. Write a JSON object of flag names and values, such as {{"ratio": "16:9"}}.` | This milestone |
| `PROMPT_TWICE` | `INVALID_INPUT` | `The prompt input and arguments both set prompt. Remove it from one of them.` | This milestone |
| `PROMPT_REQUIRED` | `INVALID_INPUT` | `Write a prompt. Mode {mode} of this model needs one.` | This milestone |
| `SINGLE_VALUE` | `INVALID_INPUT` | `Connect one value to {name}, not a list.` | Media and runs, with 08's `PaidNode` |

```python
# How a refusal names a JSON value that is not text or a number, or not an object.
JSON_SHAPES = {
    "array": "a JSON list",
    "string": "text in double quotes",
    "number": "a number",
    "boolean": "true or false",
    "null": "null",
    "object": "a JSON object",
}
```

The literal braces in `ARGUMENTS_INVALID` and `ARGUMENTS_SHAPE` are doubled,
because every message is filled with `str.format`. `SINGLE_VALUE` is O's and
B's text. The generation nodes take input lists, so every widget value
arrives as a list, and a linked widget could carry several
([Step 6](#step-6-the-queue-time-check)). F's 06 left it out, and F's Image
milestone had to add it (F's changes table, plans 09, 14, and 17).
[07-media.md](07-media.md#step-3-reference-and-placeholder-messages) adds
`PLACEHOLDER_UNCONNECTED` to this module.

## Step 2: Records

Create `src/types/models.py` with the docstring "What the pack reads about
Dreamina's models from the CLI's model list." The list is the CLI's JSON, so
every record is a `Reply` (unknown keys ignored, frozen). Local names avoid
builtins and the banned words: `min`, `max`, and `type` would shadow
builtins, and `vipResolutions` holds the banned `resolution`
([01-decisions.md](01-decisions.md#banned-words-that-shape-names)). Each wire
name stays the CLI's through `Field(alias=…)`.

```python
class ModelFlag(Reply):
    name: str = Field(alias="flag")
    required: bool
    values: tuple[str, ...] | None = None
    minimum: float | None = Field(default=None, alias="min")
    maximum: float | None = Field(default=None, alias="max")
    step: float | None = None
    min_length: int | None = Field(default=None, alias="minLength")
    max_length: int | None = Field(default=None, alias="maxLength")


class ReferenceLimit(Reply):
    media_type: str = Field(alias="mediaType")
    minimum: int = Field(alias="min")
    maximum: int = Field(alias="max")


class ModelReferences(Reply):
    minimum: int = Field(alias="min")
    maximum: int = Field(alias="max")
    limits: tuple[ReferenceLimit, ...] = Field(alias="types")
    required_types: tuple[str, ...] = Field(default=(), alias="requireAnyOfTypes")
    exclusive_types: tuple[str, ...] = Field(default=(), alias="mutuallyExclusiveTypes")


class ModelMode(Reply):
    name: str
    scenario: str | None = None
    flags: tuple[ModelFlag, ...] = ()
    references: ModelReferences | None = None
    vip_required: bool | None = Field(default=None, alias="vipRequired")
    vip_sizes: tuple[str, ...] | None = Field(default=None, alias="vipResolutions")


class ListedModel(Reply):
    kind: Kind = Field(alias="type")
    name: str = Field(alias="model")
    aliases: tuple[str, ...] = ()
    modes: tuple[ModelMode, ...]


class ModelListReply(Reply):
    items: tuple[ListedModel, ...]
```

What each attribute means (the class docstrings' `Attributes:` sections say
the same in one line each, as `F/src/types/models.py:13-46` does):

| Attribute | Meaning |
| --------- | ------- |
| `ModelFlag.name` | The flag as the list writes it, with its two leading dashes, such as `--ratio` |
| `ModelFlag.required` | The run is refused without it |
| `ModelFlag.values` | The allowed values, exactly as listed; `None` when any text is allowed |
| `ModelFlag.minimum`, `maximum`, `step` | Numeric bounds, and the step from `minimum`, or from 0 when there is no minimum |
| `ModelFlag.min_length`, `max_length` | Text length bounds, in characters |
| `ReferenceLimit.media_type` | `image`, `video`, or `audio` |
| `ReferenceLimit.minimum`, `maximum` | How many references of that type the entry takes |
| `ModelReferences.minimum`, `maximum` | How many references the entry takes in all |
| `ModelReferences.limits` | The media types the entry enables; an empty tuple enables none |
| `ModelReferences.required_types` | At least one of these types must be connected; empty when there is no such rule |
| `ModelReferences.exclusive_types` | These types may not be connected together; empty when there is no such rule |
| `ModelMode.name` | The mode, such as `first_last_frame`, sent as `--mode` |
| `ModelMode.scenario` | The speech scenario, sent as `--scenario`; `None` for every other mode |
| `ModelMode.flags` | The flags this entry accepts, in list order |
| `ModelMode.references` | The entry's reference limits; `None` when the list leaves them out, which means the entry takes none |
| `ModelMode.vip_required`, `vip_sizes` | The membership fields, for Model: Info only |
| `ListedModel.kind` | The list's `type`, which is the kind the list was read for |
| `ListedModel.name` | The canonical name, sent as `--model` |
| `ListedModel.aliases` | Other names that match; never sent |
| `ListedModel.modes` | The mode entries in list order; one mode name can appear more than once |
| `ModelListReply.items` | The models of one kind |

The flag name keeps its dashes in the record, as the list writes it, so
Model: Info shows it unchanged. `src/dreamina/arguments.py` removes
`FLAG_PREFIX` in one place ([Step 5](#step-5-check-and-build-the-arguments)).

`ListedModel.kind` is read as `Kind`. `model list --type <kind>` returns only
that kind, so a value outside `Kind` cannot occur in a list the pack reads.
Model: Info, which passes no kind, reads it to know which node runs the model
and whether to read voices.

`__all__` lists the six records.

## Step 3: Read the model list

Create `src/dreamina/models.py`, ported from `F/src/fal/models.py`, with the
docstring "Read each kind's models from the person's live Dreamina model list
before a run is paid, sharing reads and keeping each list." and the second
paragraph "Each list is kept for the life of the process. The read is free,
and a name it misses reads the list again once."

```python
async def find_model(name: str, kind: Kind | None) -> ListedModel: ...
async def _read_model_list(kind: Kind) -> tuple[ListedModel, ...]: ...
```

`find_model` is the module's one public function. The generation nodes call
it with their kind, and Model: Info calls `find_model(name, None)`
([15-node-model-info.md](15-node-model-info.md)). `_read_model_list` is
private, because only `find_model` calls it, and the function policy refuses
a public function no other module names
([05-foundation.md](05-foundation.md#porting-rules), rule 6).

### The cache and shared reads

Kept from `F/src/fal/models.py:42-60` and `:96-107`, renamed:

- `_LISTS: dict[str, tuple[ListedModel, ...]]`, with the comment "Each kind's
  models, read once per ComfyUI process; a name a list misses reads it
  again."
- `_READS`, the reads in flight per event loop, keyed by kind, as a
  `weakref.WeakKeyDictionary[asyncio.AbstractEventLoop, dict[str,
  asyncio.Task[tuple[ListedModel, ...]]]]`.
- `_delete_read`, unchanged: it drops a finished read and takes its exception,
  so a read whose callers all canceled never fails unseen.
- `_read_listing(kind)`: one task per kind per loop, created once and awaited
  through `asyncio.shield`, so one caller's cancel leaves the read running for
  the others. ComfyUI runs each prompt on a new event loop, and validates
  queued prompts on the server's loop, which is why the reads are kept per
  loop.

The read itself, private `_send_model_list(kind)`:

1. `result = await send_command((*LIST_COMMAND, kind), LIST_TIMEOUT_SECONDS)`.
1. A non-zero exit code raises `build_failure(result, context)` with the
   context 08 Part A gives free reads. A signed-out read becomes the sign-in
   message that names **Dreamina Settings**
   ([01-decisions.md](01-decisions.md#checking-a-model-before-paying)).
1. `ModelListReply.model_validate(result.reply.payload)`. A
   `ValidationError` raises `DreaminaError(ErrorCode.TRANSPORT,
   MODEL_LIST_UNREADABLE)`.
1. It stores `items` in `_LISTS[kind]` and returns them.

A failed read stores nothing, so the next caller reads again.
`_read_model_list(kind)` returns `_LISTS[kind]` when it is there, and
otherwise awaits `_read_listing(kind)`.

The callers run `validate_cli()` first, as
[04-architecture.md](04-architecture.md#how-a-paid-run-flows) says, so a
missing or old CLI is refused with its own message before any list is read.

A list read once keeps its first reading until ComfyUI restarts, apart from
the second read below. Dreamina's server revalidates every run against its
latest specification ("discovery is not durable authorization",
[research/cli.md](research/cli.md#model-discovery)). A stale list can only
let through what the server then refuses at save, before any charge.

### `find_model`

In order:

1. **Empty.** Strip the name. Empty raises `MODEL_EMPTY` with
   `{example}` = `DEFAULT_MODELS[kind or "image"]`.
1. **This kind.** Note whether `_LISTS` already holds the kind, then read it
   with `_read_model_list(kind)`. Model: Info passes `kind=None`, and every
   kind in `KINDS` order is searched instead.
1. **The match**, private `_find_match(models, typed)`, with `typed` the
   stripped name after `casefold()`:
   - a model whose canonical name, after `casefold()`, equals `typed` is the
     match;
   - otherwise the models with an alias equal to `typed` after `casefold()`:
     one is the match, and several raise `MODEL_AMBIGUOUS` with their
     canonical names;
   - otherwise no match. No substring, prefix, or ranking match is ever taken.
1. **Read again once.** No match, and the list came from `_LISTS` (read
   earlier in the process): remove `_LISTS[kind]`, read it again, and match
   again. A list read in this same call is not read twice.
1. **Another kind.** Still no match, for a paid node: read each other kind in
   `KINDS` order and match there. A match raises `MODEL_KIND` with `{made}`
   from `KIND_NAMES[found kind]`, `{node}` from `KIND_NODES[found kind]`, and
   `{this}` from `KIND_NODES[kind]`. A failed read of another kind stops the
   run with its own message, as every failed read does.
1. **Refusal.** An empty list raises `MODEL_LIST_EMPTY`. Otherwise
   `MODEL_UNKNOWN` with `{names}`: the `SUGGESTION_COUNT` canonical names of
   the searched kinds ranked by `difflib.SequenceMatcher(None, typed,
   candidate).ratio()`, best first. Each model scores its best ratio over its
   canonical name and its aliases, after `casefold()`. Equal scores keep list
   order.
1. Return the match.

`__all__ = ["find_model"]`.

## Step 4: Choose the mode

Create `src/dreamina/modes.py` with the docstring "Choose the mode entry a
run uses, from arguments or from what is connected." It is new; no F module
chooses a mode.

```python
def choose_mode(
    model: ListedModel, kind: Kind, connected: Sequence[MediaKind], arguments: Mapping[str, Json]
) -> ModelMode: ...
```

`connected` is the `MediaKind` of every item the run will send, in `--ref`
order: each reference's `media`, then `image` for each image frame, `video`
for each video, and `audio` for each audio clip. 08's `GenerationOperation`
builds it before any upload, from the same items it passes to 07's
`validate_references` ([08-runs.md](08-runs.md#generationoperation)). The
mode rules count it; its order matters only to 07. The result is one
`ModelMode` entry of the model. Its `name` is sent as `--mode`, and its
`scenario`, when set, as `--scenario`.

`ModelMode.label`, a property in `src/types/models.py`, returns `mode.name`,
or `MODE_LABEL` filled with the name and scenario. `src/dreamina/arguments.py`
and 07's `src/dreamina/references.py` use it in their refusals. A one-line
`describe_mode` function would be refused by `python.trivial-function`;
properties are exempt.

### The mode name

1. **From `arguments`.** `arguments[SELECTION_KEYS["MODE"]]`, read as text
   (`str()` of a value that is not text, so a value that is no mode name is
   refused as one). A name no entry of the model has raises `MODE_UNKNOWN`.
1. **The model's only mode.** Otherwise, when every entry of the model has
   the same name and scenario, that name.
1. **What is connected.** Otherwise, by kind. "Images" are local images and
   image references; an Element is not an image here:

   | Kind | Connected | Mode name |
   | ---- | --------- | --------- |
   | image | No image and no Element | `MODES["image"]["TEXT"]`, `t2i` |
   | image | Any image or Element | `MODES["image"]["IMAGES"]`, `i2i` |
   | video | Nothing | `MODES["video"]["TEXT"]`, `t2v` |
   | video | One to `FRAME_IMAGES` images, and nothing else | `MODES["video"]["FRAMES"]`, `first_last_frame` |
   | video | Anything else: a video, audio, an Element, or more than `FRAME_IMAGES` images | `MODES["video"]["MULTIMODAL"]`, `m2v` |
   | audio | Anything | `MODES["audio"]["SPEECH"]`, `tts` |

   A chosen name the model lacks raises `MODE_NOT_OFFERED`.

This is the table in
[01-decisions.md](01-decisions.md#how-the-mode-is-chosen). The video rows
follow the skill's "Video mode follows the resolved source type"
([research/cli.md](research/cli.md#generation-nodes)). The skill also sends
"One image with a caller-selected output ratio" to `m2v`, but the lists mark
`--ratio` required in every video mode, `first_last_frame` included
([research/catalog.md](research/catalog.md#video-models)). So a ratio in
`arguments` never changes the mode. One or two images alone are frames, and a
person who wants them as references sets `"mode": "m2v"`. The starting
`arguments` of Video: Generate hold a ratio for the same reason.

### The scenario

Only when the entries with the chosen name carry scenarios:

1. **From `arguments`.** `arguments[SELECTION_KEYS["SCENARIO"]]`, read as
   text. A scenario none of them has raises `SCENARIO_UNKNOWN`.
1. **What is connected.** Otherwise `SCENARIOS["READING"]` when nothing is
   connected, and `SCENARIOS["DUBBING"]` when anything is. A chosen scenario
   none of them has raises `SCENARIO_NOT_OFFERED`.

`"scenario"` without `"mode"` picks the entries with that scenario, whose
mode is `tts`. For `seed_audio_v1`, nothing connected gives `tts`
`text-reading`, and an image, audio, or Element gives `tts` `omni-dubbing`
([research/catalog.md](research/catalog.md#audio-models)).

### The entry

The candidates are the model's entries with the chosen name and, when one
was chosen, that scenario, in list order.

- **One candidate:** it is the entry. 07's `validate_references` then checks
  every count against it and refuses with its own messages.
- **Several:** the first that fits, by the private `_is_fitting(mode,
  counts)`. `counts` counts each item of `connected` under its `MEDIA_TYPES`
  type, so an Element counts as `image`, as 07 counts it. An entry fits when
  the total is within its `references` `minimum` to `maximum` (0 to 0 when
  `references` is `None`), and every type with a count is in `limits` with
  its count within that type's `minimum` to `maximum`. When none fits,
  `REFERENCES_NO_ENTRY` names what is connected and each candidate's limits,
  as [01-decisions.md](01-decisions.md#how-the-mode-is-chosen) asks.

So the two `first_last_frame` entries of every video model are told apart by
the image count: two images take the first entry, and one image the second
([research/catalog.md](research/catalog.md#video-models)). The flags the
next step checks are the chosen entry's.

`_is_fitting` reads only the totals and the per-type limits, which is what
tells two entries of one mode apart on the owner's lists. Every other rule
(`requireAnyOfTypes`, `mutuallyExclusiveTypes`, an Element in a frame, a
voice that fills an audio slot) is 07's, checked once, on the chosen entry
([07-media.md](07-media.md#validate_references)).

Private helpers keep `choose_mode` under the complexity limit:
`_choose_name`, `_choose_scenario`, `_list_candidates`, `_is_fitting`, and
`_describe_limits`.

`__all__ = ["choose_mode"]`.

## Step 5: Check and build the arguments

Create `src/dreamina/arguments.py`, ported from `F/src/fal/arguments.py`,
with the docstring "Check a generation node's arguments and prompt against
the model's flags, and build the mode and flag part of the run call." and the
second paragraph "Every refusal is made before anything is uploaded or paid.
Each check reads a field of the live model list."

```python
def parse_arguments(text: str) -> dict[str, Json]: ...
def validate_argument_names(model: ListedModel, arguments: Mapping[str, Json]) -> None: ...
def choose_prompt(prompt: str, arguments: Mapping[str, Json]) -> str: ...
def build_flags(mode: ModelMode, prompt: str, arguments: Mapping[str, Json]) -> tuple[str, ...]: ...
```

Every refusal raises `DreaminaError(ErrorCode.INVALID_INPUT, …)`.

### `parse_arguments`

Ported from `F/src/fal/arguments.py:44-62` (`_SHAPES` and
`_parse_arguments_text`) unchanged apart from the names:

1. Blank text (after `strip()`) is an empty object.
1. Otherwise `parse_json(text)`. Its `JSON_SYNTAX` refusal becomes
   `ARGUMENTS_INVALID`. Its other refusals (too large, too deep, values JSON
   cannot carry) pass through.
1. A value that is not an object raises `ARGUMENTS_SHAPE` with `{shape}`
   from `JSON_SHAPES`, named by F's `_SHAPES` order (`bool` before `int`).
1. Return the object, keys in the person's order.

Keys are flag names exactly as `model list` writes them, without the leading
dashes: `{"ratio": "16:9", "resolution": "720p", "duration": 4}`,
`{"voice-name": "Jessie"}`.

### `validate_argument_names`

The check that needs no connected input, run at queue time and at run time.
For each key, in order:

1. A key that starts with `-` raises `ARGUMENT_DASHES` with `{flag}` the key
   and `{name}` the key without its leading dashes.
1. The allowed names are the union, over every entry of the model, of each
   flag's name without `FLAG_PREFIX`, plus `PROMPT_FLAG` and
   `SELECTION_KEYS["MODE"]`, plus `SELECTION_KEYS["SCENARIO"]` when any entry
   has a scenario. Another key raises `ARGUMENT_UNKNOWN`.

So `{"duration": 4}` on `seedream_5.0_lite`, whose flags are `prompt`,
`ratio`, `resolution`, and `count`, is refused when the workflow is queued,
for free.

The flag names are listed by one property, `ModelMode.named_flags ->
dict[str, ModelFlag]`, keyed by the flag name with `FLAG_PREFIX` removed
(`str.removeprefix`). It is the only place the dashes are removed, and
`build_flags` uses it too. A later release that writes names without dashes
needs no change. It is a property because a one-line private function would
be refused by `python.trivial-function`.

### `choose_prompt`

The one prompt the run sends:

1. `arguments` holds `PROMPT_FLAG` and the prompt box holds text after
   `strip()`: `PROMPT_TWICE`.
1. `arguments` holds `PROMPT_FLAG`: its value, which must be text
   (`VALUE_TYPE` otherwise).
1. Otherwise the box when it holds text after `strip()`, as typed, and
   otherwise the empty string.

08 hands the result to 07's `format_prompt`, so placeholders work in either
place, and sends it as `--prompt`, or sends `--title` when it is empty
([01-decisions.md](01-decisions.md#what-a-run-sends)).

### `build_flags`

`prompt` is the text `choose_prompt` returned, before placeholders are
written in the CLI's form: the person's own text, which the length bounds are
read against. In order:

1. **The mode.** Start with `--mode` and `mode.name`, then `--scenario` and
   `mode.scenario` when it is set.
1. **The prompt.** When the entry lists `--prompt`: an empty prompt with the
   flag required raises `PROMPT_REQUIRED` with `{mode}` from
   `mode.label`. A prompt with text is checked against the flag's
   `min_length` and `max_length` as any value is (below), under the name
   `prompt`. The prompt itself is not added here.
1. **Each key**, in the person's order, skipping `SELECTION_KEYS` values and
   `PROMPT_FLAG`:
   - not a flag of this entry: `FLAG_NOT_IN_MODE`;
   - the value as text, by `_format_value` (below);
   - the value's checks (below);
   - append `FLAG_PREFIX + key` and the text.
1. **The count.** The entry lists `COUNT_FLAG` and `arguments` does not set
   it: append `--count` and `COUNT_VALUE`.
1. **Required flags.** Each flag of the entry with `required` true that
   neither `arguments` nor the steps above set raises `FLAG_REQUIRED`.
   `prompt` was checked in step 2. `scenario` is set by the entry itself,
   whose scenario is the flag's one listed value.
1. Return the tuple.

**The value as text** (`_format_value(name, value)`):

| JSON value | Text sent |
| ---------- | --------- |
| text | As written |
| a whole number (`4`, `4.0`) | Without a decimal part: `4` |
| any other number (`4.5`) | Python's `str`: `4.5` |
| `true`, `false`, `null`, a list, an object | Refused with `VALUE_TYPE`, `{shape}` from `JSON_SHAPES` |

`bool` is tested before `int`, which it subclasses. The same number writing
fills the numbers in every refusal.

**The value's checks**, each for a flag that has the field:

1. `values`: the text must be one of them, exactly, case included.
   Otherwise `VALUE_CHOICES` with every allowed value.
1. `minimum`, `maximum`, or `step`: the number is the JSON number, or the
   text read with `float()`. Text that is no finite number raises
   `VALUE_NUMBER`. Then `VALUE_TOO_LOW` below `minimum`, `VALUE_TOO_HIGH`
   above `maximum`, and `VALUE_STEP` when `(number - base) / step` is not a
   whole number (`math.isclose` with `abs_tol=1e-9`), with `base` the minimum
   or 0. `{lower}` and `{upper}` are the two allowed values around it.
1. `min_length` or `max_length`: the text's length in characters, as
   Python's `len` counts it: `VALUE_TOO_SHORT` or `VALUE_TOO_LONG`. The CLI
   counts its title in UTF-16 code units, which are never fewer, so this
   check never refuses text the server would take.

Text and numbers are treated alike because the CLI receives text either way:
`"duration": 5` and `"duration": "5"` both send `--duration 5`. Private
helpers keep each function under the complexity limit: `_validate_choice`,
`_validate_number`, `_validate_length`, and `_format_number`.

`__all__ = ["build_flags", "choose_prompt", "parse_arguments", "validate_argument_names"]`.

### What 08 does with these

At run time, before any upload, 08's `GenerationOperation` calls, in order
([04-architecture.md](04-architecture.md#how-a-paid-run-flows)):

1. `validate_cli()`;
1. `parse_arguments(arguments)`;
1. `find_model(model, kind)`;
1. `validate_argument_names(listed, values)`;
1. `choose_mode(listed, kind, connected, values)`;
1. `choose_prompt(prompt, values)`;
1. `build_flags(mode, prompt, values)`;
1. 07's `validate_references(mode, (*references, *local), values)`.

`build_flags` comes before `validate_references`, so a `voice-name` the
chosen entry does not list, such as in `seed_audio_v1` omni dubbing, is
refused as a flag before 07 could count it as a voice.

08 then finds or creates the canvas, has 07 send the media, plan the
references, and format the prompt, and sends one call made of `node create
<kind>`, `--project-id`, `--model` with `listed.name`, the tuple from
`build_flags`, `--prompt` or `--title`, each `--ref`, `--run`, `--submit-id`,
and `--credit-ceiling`. The CLI reads flags in any order; only the order of
`--ref` matters.

## Step 6: The queue-time check

`GenerateNode.validate_inputs` is [08-runs.md](08-runs.md)'s, in
`src/nodes/generate.py`, ported from `F/src/nodes/endpoint.py:73-92`. This
step fixes what it checks, so 08 builds it as written here.

```python
@classmethod
@override
async def validate_inputs(cls, model: object = None, prompt: object = None, arguments: object = None) -> bool | str: ...
```

- **The input lists.** The generation nodes declare `is_input_list=True`,
  so each media list arrives whole. ComfyUI then passes every named input to
  `validate_inputs` as a list too: a widget's value as a one-item list, and
  an input fed by a link as `(None,)`. 08's private `_read_queued` reads each
  of the three as its one item when it is a list or tuple holding exactly one
  text, as the text itself on a direct call, and as linked otherwise
  ([08-runs.md](08-runs.md#step-18-generate-node)).
- **What it names.** Only `model`, `prompt`, and `arguments`. ComfyUI skips
  its own checks only for the inputs named here, so `credit_ceiling` and
  `run_number` keep ComfyUI's range checks, as F's docstring says
  (`F/src/nodes/endpoint.py:78-81`).

In order, each `DreaminaError` returned as its text, which ComfyUI shows
before the queue starts:

1. `model` linked: return `True`. Nothing can be checked without a name.
1. `await validate_cli()`.
1. `values = parse_arguments(arguments)` when `arguments` is text, else an
   empty object.
1. `listed = await find_model(model, cls.kind)`.
1. `validate_argument_names(listed, values)`.
1. `choose_prompt(prompt, values)` when `prompt` is text.
1. Return `True`.

The mode, the values, the required flags, and the references wait for the
run: they depend on what is connected, which ComfyUI does not pass here. A
`"mode"` or `"scenario"` the model lacks is refused then too, before any
upload.

## Four runs walked through

From the owner's lists of 2026-10-16
(`research/captures/model-list-{image,video,audio}.json`). Each call is the
one 08 sends, after the global `--format json --non-interactive`. `<canvas>`
is the saved canvas ID, `<submit>` the run's new UUID, `<ceiling>` the node's
`credit_ceiling`, and `<res-…>` and `node_…` the IDs 07 gets from its uploads
and references.

### Seedream 5.0 Lite with a prompt only

**Image: Generate** as it starts: `model` `seedream_5.0_lite`, `arguments`
`{"ratio": "1:1", "resolution": "2K"}`, `prompt` `A red apple on a white
table`, nothing connected.

1. `find_model` matches the canonical name.
1. `choose_mode`: the model has `i2i` and `t2i`, nothing is connected, so
   `t2i`. Its one entry is the candidate. 07 finds 0 references against
   0 to 0.
1. `build_flags` reads the `t2i` flags: `--prompt` (required, 1 to 4,000
   characters), `--ratio` (required, eight values), `--resolution`
   (required, `2K` or `4K`), and `--count` (1 to 8). The prompt has 28
   characters, both values are listed, and `--count 1` is added.

```text
node create image --project-id <canvas> --model seedream_5.0_lite
  --mode t2i --ratio 1:1 --resolution 2K --count 1
  --prompt "A red apple on a white table"
  --run --submit-id <submit> --credit-ceiling <ceiling>
```

The refusals around it:

- `model` `5.0LITE` matches the alias `5.0lite`, ignoring case, and sends
  `seedream_5.0_lite`.
- `model` `seedance_2.0`: `The model seedance_2.0 makes videos, so it runs in Video: Generate, not in Image: Generate.`
- `arguments` `{"resolution": "2K"}`: `Set "ratio" in arguments. Mode t2i of this model needs it, and Model: Info lists its allowed values.`
- `arguments` `{"ratio": "1:1", "resolution": "1K"}`: `The flag resolution does not take 1K. Write one of: 2K, 4K.`
- an empty prompt: `Write a prompt. Mode t2i of this model needs one.`

### Seedance 2.0 Fast from a first and a last frame

**Video: Generate**, `model` `seedance_2.0_fast`, `prompt` `The host turns
from the camera to the shelf`, two images in `images` (two **Load Image**
nodes joined by **Create List**, both 9:16).

With `arguments` `{"duration": 5, "resolution": "720p"}`:

1. `choose_mode`: two images and nothing else, so `first_last_frame`. Its
   two entries are the candidates. The first takes exactly two images, which
   fits.
1. `build_flags`: `duration` 5 is within 4 to 15 in steps of 1, and `720p`
   is the one listed resolution. `--ratio` is required and missing, so:
   `Set "ratio" in arguments. Mode first_last_frame of this model needs it, and Model: Info lists its allowed values.`

With `arguments` `{"ratio": "9:16", "resolution": "720p", "duration": 5}`,
07 sends the two images in order:

```text
node create video --project-id <canvas> --model seedance_2.0_fast
  --mode first_last_frame --ratio 9:16 --resolution 720p --duration 5 --count 1
  --prompt "The host turns from the camera to the shelf"
  --ref res:<res-first> --ref res:<res-last>
  --run --submit-id <submit> --credit-ceiling <ceiling>
```

Around it:

- one image takes the second `first_last_frame` entry, exactly one image;
- three images give `m2v`, whose one entry takes 1 to 12 references with up
  to nine images;
- `"mode": "m2v"` with the two images sends them as references in `m2v`;
- `"mode": "first_last_frame"` with three images: `No entry of mode first_last_frame of this model takes what is connected (image 3). Its entries take 2 to 2 references (image 2 to 2) or 1 to 1 references (image 1 to 1). Change the inputs, or set another mode in arguments.`
- `"resolution": "1080p"`: `The flag resolution does not take 1080p. Write one of: 720p.`
- `"duration": 4.5`: `The flag duration takes steps of 1, so 4.5 cannot be sent. Write 4 or 5.`

### Seedance 2.0 Fast with an Element

**Video: Generate**, `model` `seedance_2.0_fast`, `references` from
**Element: Add** (one `Reference`, media `element`), `prompt`
`{{reference1}} walks into a bright kitchen and waves at the camera`,
`arguments` `{"ratio": "9:16", "resolution": "720p", "duration": 4}`.

1. `choose_mode`: an Element, so `m2v`, and its one entry is the candidate.
   07 counts the Element as one image: the total 1 is within 1 to 12,
   `image` 1 is within 0 to 9, and `requireAnyOfTypes` (`image`, `video`) is
   met. `m2v` is no frame mode, so 07's Element rule does not apply.
1. `build_flags` returns `--mode m2v --ratio 9:16 --resolution 720p
   --duration 4 --count 1`.
1. 07's `format_prompt` writes `{{reference1}}` as the Element's
   `{{node:…}}` form, and its `--ref` stays; the CLI merges the two into one
   slot ([01-decisions.md](01-decisions.md#placeholders)).

```text
node create video --project-id <canvas> --model seedance_2.0_fast
  --mode m2v --ratio 9:16 --resolution 720p --duration 4 --count 1
  --prompt "{{node:node_…}} walks into a bright kitchen and waves at the camera"
  --ref node:node_…
  --run --submit-id <submit> --credit-ceiling <ceiling>
```

Run C-15 sends this call's quote. If the server counts an Element otherwise,
`MEDIA_TYPES["element"]` changes, as 07 says, and both plans follow it.

### Seed Audio reading a script

**Audio: Generate** as it starts: `model` `seed_audio_v1`, `arguments`
`{"voice-name": "Jessie"}`, `prompt` `Welcome back to the shop! Today we
unbox a bottle that keeps coffee hot all day.`, nothing connected.

1. `choose_mode`: the model has two `tts` entries with scenarios. Nothing is
   connected, so `text-reading`, whose one entry is the candidate.
1. `build_flags`: `--scenario` is required with the one value
   `text-reading`, which the entry sets. `--voice-name` is required and set;
   it lists no `values`, so any voice name passes, and the server checks it.
   `--prompt` takes 1 to 3,000 characters. No `--count`.
1. 07's `validate_references` counts the voice as one audio reference, which
   the entry's 0 to 1 audio takes.

```text
node create audio --project-id <canvas> --model seed_audio_v1
  --mode tts --scenario text-reading --voice-name Jessie
  --prompt "Welcome back to the shop! Today we unbox a bottle that keeps coffee hot all day."
  --run --submit-id <submit> --credit-ceiling <ceiling>
```

Around it:

- an image connected gives `omni-dubbing`, whose entry lists no
  `--voice-name`: `Mode tts (omni-dubbing) of this model has no flag named voice-name. Its flags are scenario, prompt. Remove it from arguments, or set another mode.`
  With `arguments` empty it sends `--mode tts --scenario omni-dubbing`.
- an image and an audio clip together are refused by 07's
  `REFERENCES_EXCLUSIVE`, from the entry's `mutuallyExclusiveTypes`.

## Step 7: Allowlist and commits

Add to `quality/config/repository/functions.json` `python.allowlist`, last,
the entries for public names no other module calls yet. The plan whose
change first calls a name removes it:

```json
{
    "path": "src/dreamina/models.py",
    "names": ["find_model"],
    "reason": "The generation nodes and Model: Info find models here; 08 Part B removes this entry with GenerationOperation."
},
{
    "path": "src/dreamina/modes.py",
    "names": ["choose_mode"],
    "reason": "The generation run chooses its mode here; 08 Part B removes this entry with GenerationOperation."
},
{
    "path": "src/dreamina/arguments.py",
    "names": ["build_flags", "choose_prompt", "parse_arguments", "validate_argument_names"],
    "reason": "The generation run and its queue check read arguments here; 08 Part B removes this entry with GenerateNode."
}
```

`_read_model_list` needs no entry: it is private.

Commit Steps 1 to 7 with `feat(nodes): add the live model check`, the
subject the [build order](README.md#build-order) gives this milestone.

## Live check

Run K-1 in [21-test-runs.md](21-test-runs.md#k-1-the-model-check-and-the-refusals)
checks this plan through ComfyUI. It runs after the Image milestone's commit,
the first milestone with a node that calls these functions, with ComfyUI
restarted so no list is in memory. Every step is free. Each is one **Image:
Generate** node at its starting values unless the step says otherwise.

| Step | Input | Expected | If it differs |
| ---- | ----- | -------- | ------------- |
| 1 | `model` `no_such_model`, queued twice with different `run_number` values | At queue time, both times: `The model no_such_model is not in your Dreamina model list. The closest names are …` with three image models. The first queue reads the image list for the first time; the second reads it again because the name missed a list kept in memory. | Fix `find_model`'s second read or the ranking |
| 2 | `model` `seedance_2.0_fast` | `The model seedance_2.0_fast makes videos, so it runs in Video: Generate, not in Image: Generate.` | Fix the other-kind lookup |
| 3 | `arguments` `{"ratio": "1:1", "resolution": "2K", "duration": 4}` | `The model seedream_5.0_lite has no flag named duration. Its flags are prompt, ratio, resolution, count.` | Fix `validate_argument_names` or `ModelMode.named_flags` |
| 4 | `arguments` `{"ratio": "5:4", "resolution": "2K"}`, then `{"ratio": "1:1", "resolution": "2K", "count": 9}` | `The flag ratio does not take 5:4. Write one of: 21:9, 16:9, 3:2, 4:3, 1:1, 3:4, 2:3, 9:16.`, then `The flag count takes at most 8, and it has 9.` | Fix the value checks |
| 5 | `arguments` `{"resolution": "2K"}` | `Set "ratio" in arguments. Mode t2i of this model needs it, and Model: Info lists its allowed values.` | Fix the required check |
| 6 | The starting values with `credit_ceiling` one below IMG-D, Part 0's quote | Dreamina stops the run at the quote with 08's ceiling message, and a draft stays on the canvas | 08's exit 10 map |

Steps 1 to 3 are refused when the workflow is queued, and steps 4 and 5
when the node runs, before any upload, because the values and the required
flags belong to the chosen mode entry. Steps 1 to 5 leave nothing on the canvas. After
step 1, steps 2 to 5 answer from the list in memory, with no CLI call. A step
that sends anything is a fault, fixed before the first paid run. The results
are recorded in the README's changes table.

## When Dreamina changes

There is no model list in the pack to rebuild. What can change, and what
happens:

1. **A new model.** It works the same day. Its name misses the list kept in
   memory, the list is read again once, and the name matches.
1. **A new flag, allowed value, or mode entry on a model already read.** It
   works after ComfyUI restarts, which reads the list again. Until then the
   node refuses it before paying, with what the earlier list allows.
1. **A renamed flag.** Only runs that use it break. Before a restart, the
   earlier list lets the old name through, and the CLI refuses it locally
   (`cli.invalid_flag`, exit 2, nothing sent). After a restart the node
   refuses it with `ARGUMENT_UNKNOWN`. Runs that do not set it are unchanged.
1. **A removed model.** The node refuses it with the closest names. If it is
   a default, Part 0's rule in [research/catalog.md](research/catalog.md#defaults)
   picks a new one, and the same change updates `DEFAULT_MODELS`,
   `DEFAULT_ARGUMENTS`, `DEFAULT_CEILINGS`, the node's help page, and the
   README.
1. **A removed command or flag the pack itself uses**, such as `model list`
   or `--type`. `validate_cli()` finds it missing from `schema` and stops
   every run with the message to update the extension
   ([01-decisions.md](01-decisions.md#the-cli-on-the-persons-computer)).
1. **A new mode name**, such as a new video mode. It runs when `arguments`
   sets it, as soon as the CLI accepts it. The node never chooses it by
   itself until `MODES` names it.
1. **Two entries of one mode that differ in more than counts.** `_is_fitting`
   reads only totals and per-type limits. If a list ever separates two
   entries of one mode by another field, `_is_fitting` reads that field too.
1. **A new media type in `references`.** 07's `MEDIA_TYPES` gains an entry
   only when the pack connects such media.
1. **Flag names written without dashes.** `ModelMode.named_flags` uses
   `removeprefix`, so nothing changes.
1. **`--voice-name` listed for omni dubbing.** The skill says omni dubbing
   can take one voice, but the owner's list leaves the flag out. Once the
   list names it, it is accepted there after a restart, and 07 counts it as
   an audio reference.

## Names this plan uses from other plans

| Name | Owner | Used for |
| ---- | ----- | -------- |
| `Json`, `Kind`, `MediaKind`, `Reply` | [05-foundation.md](05-foundation.md) | Records and signatures |
| `DreaminaError`, `ErrorCode` | [05-foundation.md](05-foundation.md) | Every refusal |
| `parse_json`, `JSON_SYNTAX` | [05-foundation.md](05-foundation.md) | `parse_arguments` |
| `send_command`, `CliResult`, `build_failure`, `validate_cli` | [08-runs.md](08-runs.md) Part A | The list read and its failures |
| `GenerateNode`, `PaidNode`, `GenerationOperation` | [08-runs.md](08-runs.md) Part B | The callers: the queue check, the run, and the starting values |
| `MEDIA_TYPES`, `LocalMedia`, `Reference`, `list_local_media`, `validate_references`, `format_prompt`, the reference messages | [07-media.md](07-media.md) | `connected`, the reference checks on the chosen entry, and the prompt sent |
| `ModelInfo` | [15-node-model-info.md](15-node-model-info.md) | A caller of `find_model(name, None)`, which searches every kind |
| Part 0's price sweep, runs C-11 and C-15 | [21-test-runs.md](21-test-runs.md) | `DEFAULT_CEILINGS`, voices, and how an Element counts |
