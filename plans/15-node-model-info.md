# Model: Info Node

This plan builds **Model: Info** (`ModelInfo`), the free node that shows what
any Dreamina model takes, as JSON:

- every mode the model has, as the person's live `model list` gives it, with
  each mode's flags, allowed values, ranges, and reference limits;
- what `model <canonical>` adds for each mode: the file limits of each media
  type, the most outputs one run can make, and the membership marks;
- the voices of a speech model, from `voice list`.

It reads the same live list the paid nodes check a model against, so the
person writes `arguments` from it and the paid node accepts what it shows. It
needs sign-in and bills nothing.

**The person types any model name.** Nothing in the code lists or limits
models. The paid nodes check the typed name against the person's live list
when the workflow is queued and again when they run, and Model: Info reads
the same list when it runs. The only fixed model strings in the code are the
starting values of the `model` boxes. This node's starts at
`seedream_5.0_lite`, which the person replaces freely
([01-decisions.md](01-decisions.md#how-the-nodes-cover-every-model)).

It is the Dreamina form of F's Model: Info (`F/src/nodes/model.py`, F's plan
15 "Step 4: Model: Info"), with O's async read in an owned task. The model
reads are [06-model-check.md](06-model-check.md)'s; the CLI runner, the
failure map, and the version gate are [08-runs.md](08-runs.md)'s.

This plan owns `src/nodes/model.py`, `src/dreamina/voices.py`,
`src/dreamina/report.py`, `src/types/specifications.py`, Model: Info's
messages, its help page, its README row, the node settings of its example,
and its first live run. The facts are from the CLI's `schema` for release
1.0.3 (`model list`, `model`, `voice list`), the owner's captures of
2026-10-16 (`research/captures/model-list-*.json`,
`research/captures/models/*.json`, `research/captures/voices-*.json`), and
[research/catalog.md](research/catalog.md).

## Contents

- [Milestones](#milestones)
- [Decisions](#decisions)
- [Step 1: Constants, records, and messages](#step-1-constants-records-and-messages)
- [Step 2: Voices](#step-2-voices)
- [Step 3: The report](#step-3-the-report)
- [Step 4: Model: Info](#step-4-model-info)
- [Step 5: Register](#step-5-register)
- [Step 6: Help page](#step-6-help-page)
- [Step 7: README row and examples](#step-7-readme-row-and-examples)
- [Step 8: Live checks](#step-8-live-checks)
- [Names this plan uses from other plans](#names-this-plan-uses-from-other-plans)

## Milestones

Model: Info is built in two milestones, as F built its Model: Info
(`F/plans/README.md:246`):

1. **Model: Info milestone** (after Media and runs). Steps 1 to 4: the
   records, constants, messages, `src/dreamina/voices.py`,
   `src/dreamina/report.py`, and `src/nodes/model.py`, with the class left
   out of `NODE_TYPES`. Commit: `feat(nodes): add model info`.
1. **Audio milestone.** Steps 5 to 7: `ModelInfo` joins `NODE_TYPES`, with
   its help page, its README row, and its example,
   `audio-01-voice-a-script`, which lists a speech model's voices with it.
   The commit is the Audio milestone's, `feat(nodes): add the audio node`.

Why it is split: the pre-push `comfy:workflows:check` refuses a registered
node that no example places, and `comfy:nodes:check` refuses a help page of
an unregistered node. Its example is an audio example, so the node, its help
page, and its README row arrive together with Audio: Generate, and every push
passes the hooks. Run M-1 is made after the Audio milestone's commit, since an
unregistered node cannot run in ComfyUI.

## Decisions

| Question | Decision | Why |
| -------- | -------- | --- |
| Which names does it take? | Any name the person types, found by 06's `find_model(name, None)`: an exact match, after `casefold()`, on a model's canonical name or one of its aliases, in every kind's list. Nothing in the code lists or limits models. The `model` box starts at `DEFAULT_MODELS["image"]`, which the person replaces freely. | [01-decisions.md](01-decisions.md#how-the-nodes-cover-every-model): the person types any model name, and the live list is checked at run time. One match rule, 06's, for the paid nodes and Model: Info. |
| A name in no list | `find_model` reads a kind kept from earlier once more, so a model Dreamina added since is found, then refuses with 06's `MODEL_UNKNOWN` and the closest canonical names. An alias shared by several models is 06's `MODEL_AMBIGUOUS`; an empty name is 06's `MODEL_EMPTY`. | The skill: "never select the first item by default". |
| What does it read? | The three kinds' lists through 06's `find_model`, cached for the process; one `model <canonical> --type <kind>` per run; and, for a model with a `tts` mode, every page of `voice list --model <canonical> --count 100`. All free. | `model list` is what the paid nodes check against. `model <canonical>` gives "one model's full underlying specification" (skill), which holds the limits `model list` leaves out. |
| Which flag names does it show? | Only the CLI's own, as `model list` writes them, with 06's `FLAG_PREFIX` (the two leading dashes) removed: the keys a person writes in `arguments`, such as `ratio` and `voice-name`. 06's `ARGUMENT_DASHES` refuses a key written with its dashes, so the report shows the form that passes. | `model <canonical>` names the service's fields instead (`aspect_ratio` for `--ratio`, `duration_ms` for `--duration`), which the CLI does not take ([research/catalog.md](research/catalog.md#what-the-lists-show), item 10). Its `params` are never shown. |
| How are the limits attached to modes? | Each `model list` mode takes the `model <canonical>` entry with the same `mode`, the same `scenario`, and, when the mode lists `references`, a `materials.totalCount` with the same minimum and maximum. No fit, or more than one, gives null limits. | One mode can appear twice with different references: every video model lists `first_last_frame` once with two images and once with one ([research/catalog.md](research/catalog.md#what-the-lists-show), item 5). The counts tell the two entries apart. |
| Absent, false, and empty | Every key is always present. A value Dreamina leaves out is `null`, and an explicit `false` stays `false`. So `references` is `null` when the list omits it (the mode takes no materials) and has `"types": []` when the list enables no type, and a membership mark is `null` when Dreamina gives none. Four lists that 06's records keep as empty tuples when absent show `[]`: `aliases`, `flags`, `require_any_of`, and `mutually_exclusive`. For them an absent list and an empty one mean the same: no other name, no flag, no rule. | The skill: "An explicit `false` differs from an absent field"; "An omitted `references` means the upstream specification supplied no materials; `types: []` means the specification explicitly enabled no material type. Do not conflate them." |
| Voices | Read only for a model with a `tts` mode, every page, in Dreamina's order. A speech model with no voice catalog shows `"voices": []`. A model with no `tts` mode shows `null`. | `voice list` "explicit unsupported routes fail" (schema). |
| Membership fields | Shown, never used to refuse: the list's `vipRequired` and `vipResolutions`, and `model <canonical>`'s `isVip` and `vipConfigs`. | "These fields describe model specifications, not the current account's membership" (skill). |
| Prices | None. | [01-decisions.md](01-decisions.md#credits). |
| Cache | No `fingerprint_inputs`. ComfyUI's cache keeps one report per typed name; the lists are kept for the process by 06. | As F's Model: Info. |
| Cancel and timeout | The read runs in `wait_for_run(asyncio.create_task(...))`, so ComfyUI's cancel stops it. The **Request timeout (seconds)** setting bounds it, and a timeout is `FREE_TIMEOUT`. | As O's and F's Model: Info. |
| Progress bar | None, as F's Model: Info. | A few free reads. |
| JSON keys | snake_case, with no banned word: `membership.sizes` for `vipResolutions`, `size` for a `vipConfigs` item's `resolution`, and `max_outputs` for `maxBatchGenCount`. | `quality/config/naming/terms.json` bans `resolution`, `data`, `info`, and others; the owner asked for keys that avoid them. |
| The class name | `ModelInfo` keeps F's naming exception for the banned word `info`, which [03-repository-setup.md](03-repository-setup.md#naming-exceptions) copies with the reason naming `DreaminaModelInfo`. Every helper and message says "report". | Other extensions call the node by its ID, which ComfyUI builds from the class name. |

## Step 1: Constants, records, and messages

### Constants

Add to `src/config/models.py` ([06-model-check.md](06-model-check.md)
creates it), with its comment directly above it:

```python
# Voices read per voice list call: the CLI's largest page, so a catalog of up to 100 voices takes one call.
VOICE_PAGE_COUNT = 100
```

The speech mode is 07's `VOICE_REFERENCE["MODE"]` (`tts`), the one place the
pack names it.

08's `REQUIRED_COMMANDS` (`src/config/dreamina.py`) already lists
`"voice list"` with `model`, `offset`, and `count`, and `"model": ("type",)`,
the command `model <canonical> --type <kind>`, so the version gate refuses a
CLI without either. The model name is the command's argument, not a flag
(schema: `model` `arguments`).

### Records

Create `src/types/specifications.py` with the docstring "One model's full
specification, as `model <canonical>` returns it: the materials, file limits,
output count, and membership of each mode." It holds `Reply` records (05),
which ignore fields a later release adds. Each wire name keeps its spelling
through `Field(alias=…)`, and no local name holds a banned word:

| Record              | Fields (alias)                                                                                                                                                                   |
| ------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `CountRange`        | `minimum` (`min`), `maximum` (`max`)                                                                                                                                             |
| `MaterialLimits`    | `max_file_bytes` (`maxFileSizeBytes`), `min_width_px` (`minWidthPx`), `max_width_px` (`maxWidthPx`), `min_height_px` (`minHeightPx`), `max_height_px` (`maxHeightPx`), `min_duration_ms` (`minDurationMs`), `max_duration_ms` (`maxDurationMs`), each `int \| None = None` |
| `MaterialType`      | `media_type` (`mediaType`), `count` (`CountRange`), `limits` (`MaterialLimits \| None = None`)                                                                                   |
| `MaterialSet`       | `total_count` (`totalCount`, `CountRange`), `types` (`tuple[MaterialType, ...]`), `max_total_video_ms` (`maxTotalVideoDurationMs`), `max_total_audio_ms` (`maxTotalAudioDurationMs`), each total `int \| None = None` |
| `SizeMembership`    | `size` (`resolution`), `is_vip` (`isVip`)                                                                                                                                        |
| `ModeSpecification` | `model`, `mode`, `scenario` (`str \| None = None`), `materials` (`MaterialSet \| None = None`), `max_batch_count` (`maxBatchGenCount`, `int \| None = None`), `is_vip` (`isVip`, `bool \| None = None`), `vip_configs` (`vipConfigs`, `tuple[SizeMembership, ...] \| None = None`) |
| `SpecificationMatch` | `kind`, `generation` (`ModeSpecification \| None = None`)                                                                                                                       |
| `SpecificationReply` | `matches` (`tuple[SpecificationMatch, ...]`)                                                                                                                                    |

`__all__` lists the eight records. The reply's `params`, `aliases`,
`referenceRules`, `voiceNames`, and `postEdit` are not read: the CLI's flags,
names, and reference rules come from `model list`, and the voices from
`voice list`.

06's `ListedModel`, `ModelMode`, `ModelFlag`, `ModelReferences`, and
`ReferenceLimit` already keep what the report needs, as 06 writes them:
`ModelMode.references` and the two membership fields are `None` when absent,
and a flag's `name` keeps its dashes, as the list writes it.

### The model list read

Model: Info calls `find_model(name, None)` only, and `find_model` reads
every kind through 06's private `_read_model_list`. Neither needs an
allowlist change here: `_read_model_list` is private, and `find_model`'s
entry is removed by 08 Part B.

### Messages

Model: Info's refusals of a name are 06's, in `src/config/messages/models.py`:
`MODEL_EMPTY`, `MODEL_UNKNOWN`, `MODEL_AMBIGUOUS`, and `MODEL_LIST_EMPTY`. It
adds none of its own for names.

Add to `src/config/messages/run.py` ([08-runs.md](08-runs.md) creates it):

| Constant       | Text |
| -------------- | ---- |
| `FREE_TIMEOUT` | `{node} did not finish within the request timeout of {seconds} seconds in Dreamina Settings. It bills nothing. Select Run to try again.` |

`{node}` is the node's display name. Model: Info is its first user, and
Element: Add uses it too ([13-node-element.md](13-node-element.md)).

## Step 2: Voices

Create `src/dreamina/voices.py` with the docstring "Read every voice a speech
model's voice catalog lists, page by page.".

```python
async def read_voices(model: str, deadline: float) -> tuple[str, ...]:
```

`deadline` is the `time.monotonic()` value at which the request timeout
ends, as 07's calls take it.

1. Start at offset 0.
1. Call `send_command(("voice", "list", "--model", model, "--offset",
   str(offset), "--count", str(VOICE_PAGE_COUNT)), deadline -
   time.monotonic())`.
1. A failure whose exit code is 2 or whose `error.class` is `invalid_input`
   means the model has no voice catalog ("explicit unsupported routes
   fail"): return `()`. Any other failure raises `build_failure(result, …)`,
   so a sign-in, network, or upgrade failure has its own message. Run M-1
   records which fields an unsupported route gives, and this rule takes them.
1. Read the payload with 08's `VoicePage`. The entry for `model` in its
   `models` map, a `ModelVoices`, gives `items[].voice_name`, `has_more`,
   and `next_offset`. A payload that does not validate raises 08's
   `CLI_REPLY_INVALID` with `TRANSPORT`. A map without that entry returns the
   names read so far (an empty map is the CLI's answer for a region with no
   catalog).
1. Add each `voice_name`, unchanged, in the page's order. When `has_more` is
   false, return the names. Otherwise call again with `--offset
   <next_offset>` and the same `--model`.

The deadline bounds the pages. On 2026-10-16 `seed_audio_v1`'s catalog took
one page: 13 voices.

`__all__`: `read_voices`.

## Step 3: The report

Create `src/dreamina/report.py` with the docstring "Describe one model for
Model: Info: its listed modes, the limits `model <canonical>` adds, and its
voices." It keeps the node module small and holds no ComfyUI import.

### `read_specifications`

```python
async def read_specifications(model: str, kind: Kind, deadline: float) -> tuple[ModeSpecification, ...]:
```

One free call, `send_command(("model", model, "--type", kind), deadline -
time.monotonic())`. A failure raises `build_failure(result, …)`. The payload
is read as `SpecificationReply`; one that does not validate raises 08's
`CLI_REPLY_INVALID` with `TRANSPORT`. It returns the `generation` of every match
whose `kind` is `generation` and whose `generation.model` equals `model`, in
the reply's order.

### `describe_model`

```python
def describe_model(
    model: ListedModel, specifications: Sequence[ModeSpecification], voices: Sequence[str] | None
) -> dict[str, Json]:
```

It returns the report, every key present, in this order:

| Key       | Value |
| --------- | ----- |
| `model`   | `ListedModel.name`, the canonical name, which the paid nodes send |
| `aliases` | The list's `aliases`, `[]` when it gives none |
| `kind`    | `ListedModel.kind`, the list's `type`: `image`, `video`, or `audio` |
| `node`    | `KIND_NODES[kind]`, the paid node that runs it, such as `Image: Generate` |
| `modes`   | One object per `model list` mode, in the list's order (below) |
| `voices`  | `list(voices)`, or `null` when `voices` is `None` |

Each object of `modes`:

| Key           | Value |
| ------------- | ----- |
| `mode`        | The mode's `name` |
| `scenario`    | Its `scenario`, or `null` |
| `flags`       | One object per flag (below), in the list's order |
| `references`  | The object below, or `null` when the list omits `references` |
| `max_outputs` | The fitting specification's `maxBatchGenCount`, or `null` |
| `membership`  | The object below |

Each object of `flags`:

| Key          | Value |
| ------------ | ----- |
| `flag`       | `ModelFlag.name` without `FLAG_PREFIX`: the `arguments` key, such as `ratio` or `voice-name` |
| `required`   | `required` |
| `values`     | `values`, or `null` |
| `minimum`    | `min`, or `null` |
| `maximum`    | `max`, or `null` |
| `step`       | `step`, or `null` |
| `min_length` | `minLength`, or `null` |
| `max_length` | `maxLength`, or `null` |

`references`:

| Key                           | Value |
| ----------------------------- | ----- |
| `minimum`                     | `references.min` |
| `maximum`                     | `references.max` |
| `types`                       | One object per `types[]` entry: `media` (its `mediaType`), `minimum`, `maximum`, and `limits` (below, from the fitting specification's material type of the same `mediaType`, or `null`) |
| `require_any_of`              | `requireAnyOfTypes`, `[]` when the mode has no such rule |
| `mutually_exclusive`          | `mutuallyExclusiveTypes`, `[]` when the mode has no such rule |
| `max_total_video_ms` | The fitting specification's `maxTotalVideoDurationMs`, or `null` |
| `max_total_audio_ms` | Its `maxTotalAudioDurationMs`, or `null` |

`limits`: `max_file_bytes`, `min_width_px`, `max_width_px`, `min_height_px`,
`max_height_px`, `min_duration_ms`, and `max_duration_ms`, each the number
Dreamina gives or `null`.

`membership`:

| Key           | Value |
| ------------- | ----- |
| `required`    | `ModelMode.vip_required`, the list's `vipRequired`: `true`, `false`, or `null` |
| `sizes`       | `ModelMode.vip_sizes`, the list's `vipResolutions`, or `null` |
| `model_level` | The fitting specification's `isVip`: `true`, `false`, or `null` |
| `by_size`     | Its `vipConfigs`, each as `{"size": …, "required": …}`, or `null` |

How it works:

- The private `_find_specification(mode, specifications)` returns the one
  specification whose `mode` and `scenario` equal the list mode's and, when
  the list mode has `references`, whose `materials.total_count` minimum and
  maximum equal `references.min` and `references.max`. None, or more than
  one, returns `None`, and every key that reads it is `null`.
- A bound that is a whole number shows without a decimal point (`4`, not
  `4.0`), as F's `_format_bound` writes it.
- Units are in the key names: bytes, pixels, and milliseconds, as Dreamina
  gives them. The CLI's `duration` flag is in seconds; a material's duration
  limits are in milliseconds.

The private helpers keep each function within Ruff's complexity of 8 and
four returns: one per object above (`_describe_flag`, `_describe_limits`,
`_describe_references`, `_describe_membership`, `_describe_mode`), plus
`_find_specification` and `_format_bound`.

`__all__`: `describe_model`, `read_specifications`.

## Step 4: Model: Info

Create `src/nodes/model.py` with the docstring "Report what any Dreamina
model takes, from the live model list, its full specification, and its
voices." and `ModelInfo(io.ComfyNode)`.

```python
class ModelInfo(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id=f"{NODE_PREFIX}{cls.__name__}",
            display_name="Model: Info",
            category=MENUS["SHARED"],
            description="Show what a Dreamina model takes, as JSON: its modes, settings, allowed values, reference "
            "and file limits, and voices. It bills nothing.",
            inputs=[
                io.String.Input(
                    INPUT_NAMES["MODEL"],
                    default=DEFAULT_MODELS["image"],
                    tooltip="A model name from your Dreamina model list, or one of its other names. Case does not "
                    "matter.",
                )
            ],
            outputs=[io.String.Output("info", display_name="info")],
        )
```

The node has no `hidden` input, since it shows no progress bar, and no
`validate_inputs`: the read is the check.

`execute(cls, *, model: str) -> io.NodeOutput` (async, `@classmethod` and
`@override`, with F's pyright reason comment) returns
`await wait_for_run(asyncio.create_task(_read_report(model.strip())))`.

The private `_read_report(name: str) -> io.NodeOutput`:

1. The settings snapshot (`get_runtime().configuration.read_snapshot`, in a
   worker thread) gives the request timeout, `seconds`, and `deadline =
   time.monotonic() + seconds`. Steps 2 to 6 run inside
   `asyncio.timeout(seconds)`. A `TimeoutError` raises
   `DreaminaError(ErrorCode.TIMEOUT, FREE_TIMEOUT.format(node="Model: Info",
   seconds=seconds))`.
1. `validate_cli()`, the version gate, as 06 asks of every caller.
1. `found = await find_model(name, None)` (06). An empty name is
   `MODEL_EMPTY` with no list read. A signed-out read fails with 08's sign-in
   message, which names **Dreamina Settings**. A name in no list is
   `MODEL_UNKNOWN` with the closest names.
1. `read_specifications(found.name, found.kind, deadline)`.
1. When any mode's `name` is `VOICE_REFERENCE["MODE"]`,
   `read_voices(found.name, deadline)`; otherwise `None`.
1. Return `io.NodeOutput(json.dumps(describe_model(found, specifications,
   voices), ensure_ascii=False))`.

`__all__`: `ModelInfo`.

In the Model: Info milestone nothing registers the class. If 08 left a
`functions.json` allowlist entry for `wait_for_run`, this milestone removes
it, since Model: Info calls it.

## Step 5: Register

In the Audio milestone:

1. In `src/nodes/__init__.py`, import `ModelInfo` and add it last in
   `NODE_TYPES` ([04-architecture.md](04-architecture.md#srcnodes)). At that
   milestone `NODE_TYPES` is `(ImageGenerate, ImageUpscale, AudioGenerate,
   ModelInfo)`.
1. `DreaminaModelInfo` matches none of
   [04-architecture.md](04-architecture.md#ids-other-packs-use).
1. Check that `quality/config/naming/policy.json` holds the `ModelInfo`
   exception (path `^src/nodes/model\.py$`, category `classes`, names
   `["ModelInfo"]`, `allowed_banned_terms: ["info"]`), which
   [03-repository-setup.md](03-repository-setup.md#naming-exceptions)
   copies.

## Step 6: Help page

Create `web/docs/DreaminaModelInfo.md` in the Audio milestone. Its reference
is F's `FalModelInfo.md` (65 lines). The help page checker reads a table row
whose first cell is a backticked lowercase name as a socket, so the key
tables name keys without backticks, as F's page does.

````markdown
# Model: Info

Shows what a Dreamina model takes, as JSON: its modes, the settings of each
mode with their values and ranges, the references and files it takes, and a
speech model's voices. Use it to write a paid node's `arguments`. It reads
your live model list, so it needs sign-in. It bills nothing.

## Inputs

| Input   | What it takes                                                  |
| ------- | -------------------------------------------------------------- |
| `model` | A model name from your Dreamina list, or another of its names. |

## Outputs

| Output | What it carries                         |
| ------ | --------------------------------------- |
| `info` | The model as JSON, with the keys below. |

| Key     | What it holds                                                           |
| ------- | ----------------------------------------------------------------------- |
| model   | The model's name, as the paid nodes send it.                            |
| aliases | Its other names, which `model` also takes.                              |
| kind    | What it makes: `image`, `video`, or `audio`.                            |
| node    | The paid node that runs it, such as `Image: Generate`.                  |
| modes   | Each mode, with the keys below. A mode can appear twice.                |
| voices  | A speech model's voices: empty when it has none, null for other models. |

| Mode key    | What it holds                                                         |
| ----------- | --------------------------------------------------------------------- |
| mode        | The mode, such as `t2v`, and its `scenario` for speech.               |
| flags       | Each setting the paid node takes in `arguments`, with its limits.     |
| references  | How many references of each media type, and each type's file limits.  |
| max_outputs | The most outputs one run can make.                                    |
| membership  | What Dreamina marks for members only. The server decides at run time. |

For example, one flag of `seedance_2.0_fast`:

```json
{
    "flag": "duration",
    "required": true,
    "values": null,
    "minimum": 4,
    "maximum": 15,
    "step": 1,
    "min_length": null,
    "max_length": null
}
```

## Use

1. Type or connect the model name.
2. Connect `info` to **Preview as Text** to read it.

Write each setting in `arguments` under its `flag` name, such as
`{"duration": 4}`. The flags are exactly what the paid node accepts, so a
voice listed for a model with no `voice-name` flag cannot be sent. A value
Dreamina does not give is null. Example: **audio-01-voice-a-script**.

[Dreamina Canvas CLI](https://dreamina.capcut.com/canvas-cli)
````

## Step 7: README row and examples

The README node table row ([18-documentation.md](18-documentation.md)), last,
in the Audio milestone:

| Node | What it does | Paid |
| ---- | ------------ | ---- |
| [Model: Info](web/docs/DreaminaModelInfo.md) | Shows a model's modes, settings, reference and file limits, and voices, as JSON. | No |

The example this plan asks for. [17-scripts-and-workflows.md](17-scripts-and-workflows.md)
owns its layout, notes, prompt, and save name; when 17 differs, 17 wins and
this plan is corrected.

| Slug | What it shows | Nodes and settings this plan asks for |
| ---- | ------------- | ------------------------------------- |
| `audio-01-voice-a-script` | A speech model's voices, read before choosing one | **Voices**: **Model: Info** with `model` `seed_audio_v1` → **Preview as Text**, titled **Info**. **Voice**: **Audio: Generate** at its starting `model`, with `arguments` `{"voice-name": "Good Guy"}` and the script in `prompt` → **Save Audio (Advanced)** `audio/dreamina/script-voice`. |

- 17's Voices note says Model: Info shows what a model takes and a speech
  model's voices, and that a name copied from **Info** goes in `voice-name`
  in Audio: Generate's `arguments`, written exactly as listed.
- Model: Info has no link to Audio: Generate, so the person reads the voices
  first and runs again with another voice.

## Step 8: Live checks

Part 0 of [21-test-runs.md](21-test-runs.md) (C-0) already captured the
lists, the specifications, and the voices on 2026-10-16
(`research/captures/`). Run M-1 is listed in Part 2 and is made after the
Audio milestone's commit. Every part is free.

| Run | What | Settles | Credits | If it differs |
| --- | ---- | ------- | ------- | ------------- |
| C-0 | `model list --type` for each kind, `model <canonical>` for each model, and `voice list --model <m> --count 100` for each speech model, outside ComfyUI | The shapes Steps 1 to 3 read | 0 | Steps 1 and 3 |
| M-1a | `model` `seedream_5.0_lite` | `kind` `image`, `node` `Image: Generate`; `i2i` and `t2i` with the captured flags, shown as `ratio`, `resolution`, `count`, and `prompt`; `i2i`'s image `limits` 52,428,800 bytes and 8,192 pixels; `max_outputs` 8; `membership.sizes` `["4K"]` and `membership.by_size` `2K` false and `4K` true; `voices` null | 0 | Step 3 |
| M-1b | `model` `seedance_2.5` | `first_last_frame` twice, one with 2 images and one with 1, each with its own limits; `m2v` with its three media types, their file limits, and both total durations | 0 | `_find_specification` |
| M-1c | `model` `seed_audio_v1` | Two `tts` modes with their scenarios; omni dubbing's `mutually_exclusive` `["image", "audio"]`; `voices` the 13 captured names, in order | 0 | Step 2 or 3 |
| M-1d | `model` `nano_banana`, then `NANO_BANANA` | Both report `gemini_3_image_pro`: an alias matches in any case, and `model` is the canonical name | 0 | 06's match |
| M-1e | `model` `no_such_model`, then empty | 06's `MODEL_UNKNOWN` with the closest names; then `MODEL_EMPTY` | 0 | 06's refusals |
| M-1f | Outside ComfyUI, `voice list --model seedream_5.0_lite --count 100` | The fields an unsupported route gives | 0 | Step 2's rule for "no voice catalog" |

Record each result in [README.md](README.md#changes-made-while-building).

## Names this plan uses from other plans

| Name | Owner | Used for |
| ---- | ----- | -------- |
| `NODE_PREFIX`, `MENUS["SHARED"]`, `NODE_TYPES`, `DreaminaError`, `ErrorCode.INVALID_INPUT`, `ErrorCode.TIMEOUT`, `Json`, `Kind`, `Reply`, `get_runtime` (`configuration`), the **Request timeout (seconds)** setting | [05-foundation.md](05-foundation.md) | Names, errors, records, the timeout |
| `find_model`, `ListedModel` (`name`, `kind`, `aliases`, `modes`), `ModelMode` (`vip_required`, `vip_sizes`), `ModelFlag`, `ModelReferences`, `ReferenceLimit`, `FLAG_PREFIX`, `KIND_NODES`, `DEFAULT_MODELS`, `INPUT_NAMES["MODEL"]`, `MODEL_EMPTY`, `MODEL_UNKNOWN`, `MODEL_AMBIGUOUS`, `MODEL_LIST_EMPTY`, `src/config/models.py` | [06-model-check.md](06-model-check.md) | The match, the refusals, and the report |
| `VOICE_REFERENCE["MODE"]` | [07-media.md](07-media.md) | The speech mode |
| `send_command`, `build_failure`, `CLI_REPLY_INVALID`, `validate_cli`, `REQUIRED_COMMANDS`, `VoicePage`, `ModelVoices`, `wait_for_run`, the sign-in message, `src/config/messages/run.py` | [08-runs.md](08-runs.md) | The calls, their failures, and the owned task |
| `AudioGenerate`, its starting values | [11-node-audio.md](11-node-audio.md) | audio-01 and the Audio milestone |
| `FREE_TIMEOUT`'s second user | [13-node-element.md](13-node-element.md) | Element: Add's timeout |
| The `ModelInfo` naming exception | [03-repository-setup.md](03-repository-setup.md) | The banned word `info` |
| The example's layout and notes | [17-scripts-and-workflows.md](17-scripts-and-workflows.md) | audio-01 |
| Runs C-0 and M-1 | [21-test-runs.md](21-test-runs.md) | The live checks |
