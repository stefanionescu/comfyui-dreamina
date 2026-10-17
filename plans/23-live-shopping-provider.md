# Live-Shopping Provider

This plan describes how the owner's `comfyui-live-shopping` pack
(`L=/Users/dr_stone/Documents/work/comfyui-live-shopping`) would later add
Dreamina, through this pack, as an optional third provider of videos and
images, beside fal (through `comfyui-fal`) and OpenRouter (through
`comfyui-openrouter`). It states what this pack guarantees to L, gives the
call for each L use that Dreamina can serve, lists what L changes, and orders
the change.

It is the counterpart of F's live-shopping plan
(`F=/Users/dr_stone/Documents/work/comfyui-fal`, commit `cef8b6e`,
`plans/23-live-shopping-switch.md`). F's plan moved L from an old pack to F.
This one adds a provider and removes nothing: L's fal and OpenRouter models
keep working unchanged.

Readers: the engineer or agent who writes L's own plan for the change, and
the owner. This plan is written in this repository only, and it changes
nothing in L. Nothing in L changes until the owner asks. L's plan is then
written in L's repository from this one, in L's plan format and under L's
rules, after this pack's video model sweep
([README.md](README.md#build-order), milestone 14).

Facts about L come from L's code at commit `03ba221a` (2026-10-16), cited as
`L/<path>:<lines>`, and from `L/SHOWS.md`, cited by section because it changes
often. Model names and limits come from the owner's live lists, captured on
2026-10-16 ([research/catalog.md](research/catalog.md)). Every model name
below is an example from that list. L's plan checks each against
[research/catalog.md](research/catalog.md) and the account's live list before
it names one.

## Contents

- [What live-shopping does today](#what-live-shopping-does-today)
- [What this pack guarantees](#what-this-pack-guarantees)
- [The call for each use](#the-call-for-each-use)
- [What live-shopping changes](#what-live-shopping-changes)
- [Order of the change](#order-of-the-change)
- [Checks](#checks)
- [Open questions](#open-questions)
- [Names this plan uses from other plans](#names-this-plan-uses-from-other-plans)

## What live-shopping does today

- **Two provider packs.** L needs `comfyui-fal`, installed as
  `custom_nodes/fal-ai`, and `comfyui-openrouter`, installed as
  `custom_nodes/openrouter` (`L/README.md:38-43`). No workflow holds a
  provider node. L's picker nodes choose a model per role, such as **Image
  Model** and **Video Model** (`L/src/nodes/shared/video_model.py`), and L
  calls the provider nodes from Python.
- **One call path.** `L/src/comfy/execution.py:45-61` looks a node up in
  `nodes.NODE_CLASS_MAPPINGS`, requires a V3 `io.ComfyNode`, clones it with
  `PREPARE_CLASS_CLONE(None)` and an empty hidden holder, and calls
  `execute(**inputs)`. It first fills every setting L leaves out with the
  default the node declares (`list_node_defaults`,
  `L/src/comfy/schemas.py:46-57`), and wraps each default in a one-item list
  when the node declares `INPUT_IS_LIST`. An `ExecutionBlocker` output reads
  as `None` (`L/src/comfy/execution.py:64-66`). `send_call` returns a failure
  instead of raising it (`L/src/comfy/execution.py:104-110`), and
  `send_calls` sends a node's calls all at once
  (`L/src/comfy/execution.py:90-101`).
- **Platform modules behind neutral ones.** `L/src/providers/` holds the
  platform-neutral modules (`images.py`, `videos.py`, `masks.py`,
  `upscale.py`, `voices.py`, `models.py`, `specs.py`, `results.py`,
  `analysis.py`) and two platform packages, `fal/` and `openrouter/`. The
  neutral modules pick the platform module for each model, as
  `read_image_model` and `encode_image_request` do by spec type
  (`L/src/providers/images.py:64-105`).
- **Import contracts.** The packages stack as `src.nodes`, `src.logic`,
  `src.storage | src.providers`, `src.comfy`, `src.resources`, `src.state`,
  `src.config` (`L/pyproject.toml:202-214`). The contract "Logic and nodes
  reach providers only through the platform-neutral modules" forbids
  `src.logic` and `src.nodes` from importing `src.providers.fal` and
  `src.providers.openrouter` (`L/pyproject.toml:240-246`).
- **Images.** `IMAGE_MODELS` (`L/src/config/generation/models.py:18-45`) holds
  fal entries, each with a `TEXT_MODEL` and an `EDIT_MODEL` such as
  `openai/gpt-image-2.5/sunburst/edit`, and OpenRouter entries with a
  `MODEL_ID`, such as Seedream 5 Pro's `bytedance-seed/seedream-5-0-pro` and
  Nano Banana Pro's `google/gemini-3-pro-image`. The spec union is
  `FalImageSpec | OpenRouterImageSpec`
  (`L/src/state/shared/images.py:25`). An OpenRouter model is asked for the
  listed shape nearest the wanted size, at the smallest listed size that
  covers it (`L/src/providers/openrouter/images.py:19-59`).
- **Videos.** `VIDEO_MODELS` (`L/src/config/generation/videos.py:7-28`) holds
  one entry, Wan 3.0 Reference on fal (`alibaba/wan-3.0/reference-to-video`).
  It maps the roles prompt, duration, size, ratio, images, and audio to fal's
  inputs, and names its prompt file (`wan`), its starting size (`720p`), and
  its shortest voice clip (1.0 second). `VideoModelSpec` has only a fal
  `model` field (`L/src/state/shared/videos.py:22-42`). Every show video runs
  at least `SHORTEST_DURATION`, 15 seconds
  (`L/src/config/generation/videos.py:32`).
- **One show video, one call.** `send_video`
  (`L/src/logic/show/videos.py:58-75`) sends the reference images in the
  order the prompt names them, the frame the video starts on first, and the
  host's lines as reference audio, one clip a line. The prompt names them as
  the prompt file's `[image-name]` and `[audio-name]` sections write them,
  `Image {number}` and `Audio {number}`
  (`L/resources/prompts/show/models/wan.txt:30-34`).
- **Limits read at start.** `read_model_reports`
  (`L/src/providers/models.py:16-30`) reads every fal model's report when
  ComfyUI starts, so Video Model can offer each model's lengths and sizes. A
  report that cannot be read leaves the model with its starting values.
- **Errors.** `describe_failure` (`L/src/providers/results.py:150-153`) reads
  an error's `code` attribute and shows ComfyUI's content-blocked sentence for
  `refused` (`L/src/config/generation/messages.py:78`). Every other failure
  shows the provider's own message.
- **Retries.** A node sends each request once. After a partial failure,
  **Host: Generate**, **Product: Cut Out**, and **Product: Generate** send all
  their requests again on the next run (`L/README.md:150-157`).
- **Plans already made in L.** `L/SHOWS.md` section 5.15, "Plugging in other
  models", decides that `VIDEO_MODELS` entries gain the roles `first_frame`
  and `last_frame`, and that each entry names how its model takes the voice:
  `clips` (one clip a line, as Wan), `track` (one joined track, as OmniHuman),
  or `text` (the model speaks the quoted lines itself). Nothing there is
  started yet.
- **Spending.** A show clip costs about 0.75 US dollars on fal, and a run of
  28 scenes with three videos each about 63 US dollars (`L/SHOWS.md` section
  4.4).

## What this pack guarantees

These hold from this pack's first release and change only with a major
version, because another pack may depend on them.

### Node IDs

| L's use                                              | Node ID                      | Display name         |
| ---------------------------------------------------- | ---------------------------- | -------------------- |
| Host, product, scene, and cover images               | `DreaminaImageGenerate`      | Image: Generate      |
| Show videos                                          | `DreaminaVideoGenerate`      | Video: Generate      |
| Reading a model's modes, flags, and limits           | `DreaminaModelInfo`          | Model: Info          |
| Collecting a run left running                        | `DreaminaGenerationDownload` | Generation: Download |

This pack also has `DreaminaAudioGenerate`, `DreaminaImageUpscale`, and
`DreaminaElementAdd` ([01-decisions.md](01-decisions.md#the-nodes)). This
plan leaves them out: L's voices stay on OpenRouter, and its upscales stay on
fal. A model is a typed name in the node's `model` input, not a node of its
own. No ID here matches a `Fal*`, `OpenRouter*`, or L node ID
([04-architecture.md](04-architecture.md#ids-other-packs-use)), so the three
provider packs stay installed together.

### Calling a paid node from Python

L's call path in `L/src/comfy/execution.py:45-61` calls the paid nodes
unchanged, as F's ADVANCED guide shows under "Use from another extension"
(`F/ADVANCED.md:210-236`):

```python
clone = nodes.NODE_CLASS_MAPPINGS["DreaminaVideoGenerate"].PREPARE_CLASS_CLONE(None)
clone.hidden = io.HiddenHolder.from_dict({})
output = await clone.execute(
    model="seedance_2.5",
    prompt=prompt,
    arguments=json.dumps({"mode": "m2v", "ratio": "9:16", "resolution": "720p", "duration": 15}),
    credit_ceiling=ceiling,
    images=[first_frame, scene, host_front, product_front],
    audio=[line_1, line_2],
)
video = output.args[0][0]
```

- **Plain values, except the media lists.** `model`, `prompt`, `arguments`,
  `credit_ceiling`, and `run_number` are plain values, as F's paid nodes take
  them (`F/ADVANCED.md:228`). `images`, `videos`, and `audio` are Python lists
  of ComfyUI media, one item each, in order: an IMAGE tensor
  `[1, H, W, 3]` per image, so images of different sizes go as separate
  items, a VIDEO per video, and an AUDIO dict per clip. `references` is the
  tuple another Dreamina node returned.
- **`model`** is Dreamina's canonical model name, as the account's list gives
  it. An alias also matches, ignoring case, and the node sends the canonical
  name ([01-decisions.md](01-decisions.md#checking-a-model-before-paying)).
- **`prompt`** is sent as `--prompt` when it is not empty. The placeholders
  `{{image1}}`, `{{video1}}`, `{{audio1}}`, and `{{reference1}}` bind the
  first item of each list to that place in the prompt. Any other `{{…}}` text
  goes as written, and a literal `{{` is written `\{{`
  ([01-decisions.md](01-decisions.md#placeholders)).
- **`arguments`** is one JSON object, as text, of the mode's flags under
  Dreamina's names without the leading dashes, such as `ratio`, `resolution`,
  and `duration`, with Dreamina's own values. It may set `mode`, and
  `scenario` for speech. L builds it with `json.dumps`.
- **`credit_ceiling`** is the most credits the run may cost, sent as
  `--credit-ceiling`. L sets it on every call: the node's default fits only
  the node's default model at its starting settings
  ([01-decisions.md](01-decisions.md#credits)). A run whose quote is above it
  stops before it runs, with nothing billed, and leaves a draft on the
  canvas.
- **`run_number`** is optional. L leaves it at its default.
- **No hidden values are needed.** With an empty hidden holder, the node
  leaves the calling node's progress bar alone, as F's nodes do.
- **The model is checked before paying.** The node reads the account's live
  model list, free, once per kind per ComfyUI process. Before any upload, it
  refuses an unknown model, a model of another kind, a mode the model lacks,
  a flag the mode lacks, a value outside the flag's values or bounds, a
  missing required flag, `prompt` set twice, and references outside the
  mode's limits ([01-decisions.md](01-decisions.md#checking-a-model-before-paying)).
  A call from Python gets the same checks as a node in a workflow.

[08-runs.md](08-runs.md) and [10-node-video.md](10-node-video.md) own the
code that reads these inputs, and the guarantees above are requirements on
that code. A paid node whose media lists reach one run must take every input
as a list inside ComfyUI. It must still accept the form above from Python.
L's call path already wraps the defaults it fills when a node declares
`INPUT_IS_LIST`, but sends its own values as written.

### Reading a model's modes and limits

**Model: Info** is the one way. It is free, but unlike fal's it needs the CLI
signed in, because `model list` does
([02-dreamina-contract.md](02-dreamina-contract.md#model-discovery)).
`await clone.execute(model="<name>")` on a `DreaminaModelInfo` clone returns
`info`, a JSON report with:

- the model as `model list` gives it: `type`, `model`, `aliases`, and each
  mode's `name`, `scenario`, `flags[]` (`flag`, `required`, `values`, `min`,
  `max`, `step`, `minLength`, `maxLength`), `references` (`min`, `max`,
  `types[]` with `mediaType`, `min`, and `max`, `requireAnyOfTypes`,
  `mutuallyExclusiveTypes`), `vipRequired`, and `vipResolutions`;
- the file limits `model <name>` adds: each media type's file size, pixel
  size, and duration, and the total seconds of video and of audio
  ([research/catalog.md](research/catalog.md#file-limits));
- the voices of a speech model.

[15-node-model-info.md](15-node-model-info.md) owns the exact shape, and the
shape is part of this guarantee. L reads from it what it reads from fal's
report today:

| L reads                          | From the report                                                                    |
| -------------------------------- | ---------------------------------------------------------------------------------- |
| Video lengths                    | The mode's `duration` flag: `min`, `max`, and `step`                               |
| Video sizes                      | The `resolution` flag's `values`                                                   |
| Orientations                     | The `ratio` flag's `values`, which must hold `9:16` and `16:9`                     |
| Most reference images            | `references.types[]` for `image`: `max`                                            |
| Most voice clips                 | `references.types[]` for `audio`: `max`                                            |
| Most references in all           | `references.max`, which counts images and clips together                           |
| Shortest voice clip              | The audio file limit's shortest duration (1.8 seconds on `seedance_2.5`)           |
| Seconds of voice in all          | The total audio duration (30.2 seconds on `seedance_2.5`)                          |
| Image shapes and sizes           | The image mode's `ratio` and `resolution` values, such as `9:16` and `2K`          |
| Most edit references             | The `i2i` mode's `references.types[]` for `image`: `max`                           |

### Outputs

`output.args` holds the outputs in the node's order
([01-decisions.md](01-decisions.md#outputs)):

| Node                 | `args`                                                                                                                   |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| Image: Generate      | `(images, references, result)`: `images` a list of `[1, H, W, 3]` tensors; `references` a tuple of Dreamina references; `result` the node as Dreamina's `node show` returns it, with the canvas link, as JSON text |
| Video: Generate      | `(video, references, result)`: `video` a list of ComfyUI videos                                                          |
| Generation: Download | `(images, video, audio, references, result)`                                                                             |
| Model: Info          | `(info,)`                                                                                                                |

An output with nothing in it is ComfyUI's `ExecutionBlocker`, which L already
reads as `None`. So:

- One image call's image is `args[0][0]`, and one video call's video is
  `args[0][0]`. L's `parse_image` and `parse_video` already take the first
  item of a list (`L/src/providers/results.py:28-45`,
  `L/src/providers/results.py:80-95`).
- `references` holds what the run made, for the next Dreamina node, with no
  download or upload. L treats it as an opaque value. Across L's own nodes,
  L passes images, which this pack uploads again.
- `result` carries each resource's `creditsAmount`, Dreamina's own field. L's
  spending count can read it there.

### Errors

A refusal or failure is `DreaminaError`, a `RuntimeError` whose `code`
attribute is a string from F's `ErrorCode`, and whose text is a complete
sentence from `src/config/messages/`
([01-decisions.md](01-decisions.md#errors)). L matches the code, which never
changes, not the text, which may be reworded. L's `describe_failure` already
does this, so `refused` gets ComfyUI's content-blocked sentence with no
change in L.

| `code`           | When                                                                                                          |
| ---------------- | ------------------------------------------------------------------------------------------------------------- |
| `configuration`  | The CLI is missing, too old, or changed, or the pack's settings or state cannot be read                        |
| `authentication` | The CLI is not signed in, or the sign-in ended, or the plan may not use the CLI or the model                   |
| `credits`        | The quote is above `credit_ceiling`, with nothing billed, or the account has too few credits                   |
| `refused`        | Dreamina's safety check refused an input or the output                                                         |
| `invalid_input`  | A local refusal before paying (the model check, `arguments`, references, placeholders), or an input Dreamina refused before running |
| `unavailable`    | A model not in the account's list, or a run Dreamina no longer has a record of                                 |
| `rate_limited`   | Dreamina asked the CLI to wait                                                                                 |
| `timeout`        | The request timeout passed. The generation keeps running and billing, and stays recorded                       |
| `interrupted`    | A cancel after Dreamina accepted the run (`GENERATION_KEEPS_RUNNING`). The generation keeps running and is billed, and stays recorded |
| `transport`      | The CLI could not reach Dreamina, or a free read, upload, or download failed                                   |
| `uncertain`      | Dreamina may have accepted and billed the run, but its reply could not be read. The run is checked read-only   |
| `media`          | Media that cannot be encoded or decoded, or a file over a size limit                                           |

A cancel before Dreamina accepts the run is ComfyUI's
`InterruptProcessingException`, and nothing is billed. A cancel after
acceptance is `DreaminaError` with `interrupted`. [08-runs.md](08-runs.md)
owns the full map, and any change there changes this table in the same
change.

### Cancel, records, and time

- **No cancel at Dreamina.** Dreamina has no cancel for a run it accepted. A
  ComfyUI cancel stops the wait, the generation keeps running and is billed,
  and the record stays for **Generation: Download**
  ([02-dreamina-contract.md](02-dreamina-contract.md#waiting-and-recovery)).
  This differs from fal, where a cancel removes a request still in fal's
  queue, unbilled. A cancel during a batch of show videos bills every video Dreamina
  already accepted.
- **The run call is never cut off.** A cancel that arrives while the run call
  is in flight waits for it to return, so an accepted run is always recorded.
- **Records.** Every accepted run is recorded in this pack's state folder
  before the first wait, and deleted once its outputs are downloaded.
- **One request timeout.** The **Request timeout** in **Dreamina Settings →
  Request limits** bounds each call, from the first upload to the last
  download (default 1,800 seconds).
- **Never sent twice.** Each call is one new generation. The pack never
  retries a run call, and a lost reply is checked read-only. A `timeout` or
  `uncertain` failure may mean a billed generation is still running, so L
  never sends it again on its own.
- **Uploads every call.** Each call uploads its local images and clips again,
  free. Nothing is remembered between calls.
- **The canvas.** Every call lands on the owner's `ComfyUI` canvas, with its
  prompt and its uploaded images and clips
  ([22-owner-setup.md](22-owner-setup.md#step-5-know-the-comfyui-canvas)).
- **The sign-in.** The CLI must be signed in, as the macOS user that runs L's
  ComfyUI, on every machine that runs a Dreamina entry
  ([22-owner-setup.md](22-owner-setup.md#step-2-sign-in)).

## The call for each use

The inputs for each L use that Dreamina can serve, with flag names and limits
from the owner's lists on 2026-10-16. `<prompt>`, `<ceiling>`, and the other
names in angle brackets are L's own values. L sets every required flag:
`ratio`, `resolution`, and `duration` are required, and the lists give no
defaults ([research/catalog.md](research/catalog.md#what-the-lists-show)).

| # | Use                                                  | Node                    | Mode               | Model (example)                                               |
| - | ---------------------------------------------------- | ----------------------- | ------------------ | ------------------------------------------------------------- |
| 1 | Show video with references and the host's voice      | `DreaminaVideoGenerate` | `m2v`              | `seedance_2.5`; `seedance_2.0`, `seedance_2.0_fast`, and `seedance_2.0_mini` with smaller limits |
| 2 | A silent shot between a first and a last frame       | `DreaminaVideoGenerate` | `first_last_frame` | `seedance_2.5`                                                |
| 3 | Host, product, scene, and cover images from text     | `DreaminaImageGenerate` | `t2i`              | `dreamina_gpt_image_2_5_sunburst`, `seedream_5.0_pro`, `gemini_3_image_pro` |
| 4 | The same with reference images                       | `DreaminaImageGenerate` | `i2i`              | The same models                                               |

Each call shows the keyword inputs of `execute`; `arguments` is shown as the
dict L passes to `json.dumps`.

```python
# 1. Show video (m2v). The images go in the order the prompt names them, the frame the video starts on first, then
#    the scene, host, and product images. Each line of the host's voice is one AUDIO item, in line order. Seedance 2.5
#    takes up to 30 images and 10 clips, 50 references in all, each clip 1.8 to 30.2 seconds and 30.2 seconds in all,
#    and 4 to 30 seconds of video at 480p, 720p, or 1080p. Seedance 2.0 takes 9 images and 3 clips, 15 seconds in all.
model="seedance_2.5", prompt=<prompt>, credit_ceiling=<ceiling>,
images=[<first frame>, <scene>, <host 1>, <product 1>, ...], audio=[<line 1>, <line 2>, ...],
arguments={"mode": "m2v", "ratio": <orientation>, "resolution": <size>, "duration": <seconds>}

# 2. Frames-only shot (first_last_frame): the first frame, then the last, in the same shape. ratio is required here
#    too. No other image and no audio, so the shot is silent.
model="seedance_2.5", prompt=<prompt>, credit_ceiling=<ceiling>, images=[<first frame>, <last frame>],
arguments={"mode": "first_last_frame", "ratio": <orientation>, "resolution": <size>, "duration": <seconds>}

# 3. Image from text (t2i): the listed shape nearest the wanted size, at the smallest listed size that covers it.
model="dreamina_gpt_image_2_5_sunburst", prompt=<prompt>, credit_ceiling=<ceiling>,
arguments={"mode": "t2i", "ratio": <listed shape>, "resolution": <listed size>}

# 4. Image with references (i2i): each reference its own tensor, in order. GPT Image 2.5 Sunburst takes 1 to 16,
#    Seedream 5.0 Pro 1 to 10, and Nano Banana Pro 1 to 6.
model="dreamina_gpt_image_2_5_sunburst", prompt=<prompt>, credit_ceiling=<ceiling>, images=[<image 1>, <image 2>, ...],
arguments={"mode": "i2i", "ratio": <listed shape>, "resolution": <listed size>}
```

Notes on these calls:

- **L sets `mode` itself.** The node would choose a mode from what is
  connected, but an explicit mode keeps a model change from switching it
  silently. Two images with `first_last_frame` take the mode's two-image
  entry; every model lists the mode twice, once for two images and once for
  one.
- **The prompt names each item with the pack's placeholders.** A Dreamina
  prompt file's `[image-name]` section is `{{{{image{number}}}}}` and its
  `[audio-name]` section `{{{{audio{number}}}}}`. `read_prompt` fills
  sections with `str.format_map` (`L/src/resources/prompts.py:37-42`), which
  turns each doubled brace into one, so the prompt reads `{{image1}}` and
  `{{audio1}}`. The node binds each placeholder to its item. Whether a placeholder binds an uploaded file is run C-6 in
  [21-test-runs.md](21-test-runs.md). If it does not, the prompt names the
  items by order in words, as Wan's does.
- **The orientation and size match L's own values.** Both of L's
  orientations, `9:16` and `16:9`, are listed, and Seedance 2.5 writes its
  sizes `480p`, `720p`, and `1080p`, as L's Wan entry writes its starting
  `720p`.
- **L's always-sent inputs do not apply.** `ALWAYS_SENT`
  (`L/src/config/generation/inputs.py:42-46`) names fal and OpenRouter
  inputs. L sends one only where Model: Info lists a flag of that name, and no
  Dreamina model lists any of them. The node refuses an unknown flag before
  paying.
- **The node sends one output per run.** It sends `--count 1` unless
  `arguments` sets `count` ([01-decisions.md](01-decisions.md#credits)).
- **Images go as PNG, never resized by the pack.** L's sent-image limits
  (384 to 4,096 pixels a side, 20 MB, `L/src/config/generation/images.py:40-44`)
  fall inside Seedance's (300 to 8,192 pixels, 50 MB).
- **Image models take no exact size.** Dreamina's image models take a listed
  shape and size, so a Dreamina image entry works as L's OpenRouter entries
  do, with no quality control. Its sizes (`1K`, `1.5K`, `2K`, `4K`) match L's
  listed-size pattern (`L/src/config/generation/openrouter.py:33-36`).
- **The prompt has a length limit.** `--prompt` takes up to 15,000
  characters on `seedance_2.5` and 4,000 on the other models. The node
  refuses a longer prompt before paying.
- **Same models, another bill.** `dreamina_gpt_image_2_5_sunburst` is GPT
  Image 2.5 Sunburst, L's default image model on fal, and
  `gemini_3_image_pro` is Nano Banana Pro, which L runs on OpenRouter. A
  Dreamina entry bills Dreamina credits instead.
- **What Dreamina does not serve.** Dreamina lists no Wan or MiniMax model,
  so Wan 3.0 stays on fal. The CLI has no mask, cut-out, or video upscale
  model, no avatar model such as OmniHuman, and no text model, so L's masks,
  upscales, voices, analysis, and scripts keep their providers.

## What live-shopping changes

L's own plan turns each row into steps. This is the full list of files the
change touches in L.

| L file | Change |
| ------ | ------ |
| `src/config/generation/dreamina.py` | New. `DREAMINA_NODES`: `IMAGE` `DreaminaImageGenerate`, `VIDEO` `DreaminaVideoGenerate`, `MODEL_INFO` `DreaminaModelInfo`, `DOWNLOAD` `DreaminaGenerationDownload` |
| `src/state/shared/providers.py` | New `DreaminaReport` record for Model: Info's report: the modes with their flags and references, and the file limits, read with `extra="ignore"` |
| `src/state/shared/images.py` | New `DreaminaImageSpec` (`DREAMINA_MODEL`, the model's canonical name, and `CREDIT_CEILING`). `ImageModelSpec` becomes `FalImageSpec \| OpenRouterImageSpec \| DreaminaImageSpec`; each entry's own required key tells them apart |
| `src/state/shared/videos.py` | `VideoModelSpec` is renamed `FalVideoSpec`. New `DreaminaVideoSpec` (`DREAMINA_MODEL`, `INPUTS`, `PROMPT_FILE`, `DEFAULT_SIZE`, `CREDIT_CEILING`), whose shortest clip and seconds of voice come from Model: Info. `type VideoModelSpec = FalVideoSpec \| DreaminaVideoSpec`. `SelectedVideoModel` gains `reference_total`, the most references in all |
| `src/providers/dreamina/__init__.py` | New platform package |
| `src/providers/dreamina/models.py` | New. Reads each model's report through Model: Info once per process, as `L/src/providers/fal/models.py:24-31` does, and reads the lengths, sizes, shapes, limits, and clip seconds from it. Stops before anything is paid when a flag L sends is missing from the mode |
| `src/providers/dreamina/calls.py` | New. `build_dreamina_call` builds a `ProviderCall` for the image or video node: `model`, `prompt`, `arguments` as JSON with `mode` and each role's flag, `images` and `audio` as lists, and the entry's `credit_ceiling` |
| `src/providers/dreamina/videos.py` | New. `encode_video_request` for a Dreamina entry: `m2v` with the references and the voice clips |
| `src/providers/dreamina/images.py` | New. `encode_image_request` for a Dreamina entry: `t2i`, or `i2i` with references, at the listed shape and size |
| `src/providers/videos.py` | `list_video_choices`, `read_video_model`, and `encode_video_request` pick the fal or Dreamina module by spec type |
| `src/providers/images.py` | `read_image_model` and `encode_image_request` gain the Dreamina branch. `read_quality_input` returns `None` for a Dreamina spec |
| `src/providers/models.py` | `read_model_reports` also reads each Dreamina entry's report at start. A failed read, such as with the CLI signed out, leaves the entry with its starting values, as today |
| `src/logic/show/references.py`, `src/logic/show/checks.py` | Count the voice clips against `reference_total` too, when a model gives one total for images and clips |
| `src/config/generation/videos.py` | One `VIDEO_MODELS` entry per Dreamina video model, with its `CREDIT_CEILING` and the reason for it in a comment |
| `src/config/generation/models.py` | One `IMAGE_MODELS` entry per Dreamina image model, named so it is told apart from the fal or OpenRouter entry of the same model |
| `resources/prompts/show/models/<name>.txt` | New prompt file per Dreamina video family, such as `seedance.txt`, with every section `MODEL_SECTIONS` lists (`L/src/config/show/sections.py:35`), worded from ByteDance's own Seedance prompt guide |
| `src/config/generation/messages.py` | `PROVIDER["MISSING_NODE"]` names comfyui-dreamina (as `custom_nodes/dreamina`) too. New `PROVIDER["NO_DREAMINA_REPORT"]` for a report that cannot be read |
| `pyproject.toml` | Add `"src.providers.dreamina"` to `forbidden_modules` of the contract "Logic and nodes reach providers only through the platform-neutral modules" |
| `README.md`, `ADVANCED.md` | Requirements: comfyui-dreamina is optional, needed only for Dreamina models, with a Dreamina account that can use the Canvas CLI and the CLI installed and signed in from **Dreamina Settings**. Install: clone it into a folder named `dreamina` |

A Dreamina video entry has this shape, with values from the video sweep:

```python
"Seedance 2.5": {
    "DREAMINA_MODEL": "seedance_2.5",
    "INPUTS": {"prompt": "prompt", "duration": "duration", "size": "resolution", "ratio": "ratio",
               "images": "image", "audio": "audio"},
    "PROMPT_FILE": "seedance",
    "DEFAULT_SIZE": "720p",
    # The quote at the longest length and largest size Video Model offers, rounded up to the next 10.
    "CREDIT_CEILING": <from check 3>,
},
```

`images` and `audio` name the reference `mediaType` each role fills, as the
lists write them. The provider is chosen per show on **Video Model** and
**Image Model**: an entry names its provider, so the owner picks a Dreamina
entry for one show and a fal entry for the next, with no new control. No show
workflow changes.

## Order of the change

1. **Finish the prerequisites in this repository.** This pack's Video and
   downloads milestone and the video model sweep
   ([README.md](README.md#build-order), milestones 11 and 14) settle the
   models, their limits, and their credits. The owner settles the commercial
   use question below. Then the owner asks for the change.
1. **Install this pack next to F and O.** Link this repository into
   `custom_nodes/dreamina` of the ComfyUI that Comfy Desktop runs, where
   `fal-ai` and `openrouter` already sit, and restart ComfyUI with the owner's
   permission. The CLI is signed in as the same macOS user
   ([22-owner-setup.md](22-owner-setup.md#step-2-sign-in)). The packs' node
   IDs, routes, and socket types differ.
1. **Write L's plan** in L from this one, in L's own plan format, and record
   the owner's decisions in `L/SHOWS.md`, as L's rules for shows ask.
1. **Lay the shared groundwork** in one commit: `dreamina.py` in config, the
   report record, `src/providers/dreamina/models.py` and `calls.py`, the
   message changes, and the import contract. No entry exists yet, so nothing
   offers Dreamina. The records and the call builder come before any caller.
1. **Add images**: the image spec, `src/providers/dreamina/images.py`, its
   branch in `src/providers/images.py` and `models.py`, one `IMAGE_MODELS`
   entry, and the README and ADVANCED requirements. Images come first because
   their calls are the simplest and the cheapest.
1. **Add show videos with references and the voice**: the video spec rename,
   `src/providers/dreamina/videos.py`, its branch in `src/providers/videos.py`,
   `reference_total` and its readers, the prompt file, and one `VIDEO_MODELS`
   entry. It maps to L's planned `clips` voice mode, or to `text` if check 6
   shows that Seedance speaks the quoted lines instead of the clips.
1. **Add frames-only shots** only after L has built its planned `first_frame`
   and `last_frame` roles (`L/SHOWS.md` section 5.15) and the owner has
   decided which show videos use them. The Dreamina entry then maps the two
   roles to `first_last_frame` with call 2.

Each step is one commit in L, with L's checks passing, so L works at every
point. L's fal and OpenRouter entries are unchanged throughout.

## Checks

Paid checks run only with the owner's approval and their credits stated, in
L's own live runs. The credits come from check 3, which costs nothing.

| # | Check | Expected | Credits |
| - | ----- | -------- | ------- |
| 1 | Free: Model: Info for every Dreamina entry L names | Every flag L sends exists on its mode, `ratio` lists `9:16` and `16:9`, `duration` reaches 15, and the image, clip, and total limits are read | 0 |
| 2 | Free: a call with a misspelled flag in `arguments` (`"duraton": 15`) | `invalid_input` before any upload or charge, naming the flag and the model | 0 |
| 3 | Free: each entry at L's settings with `credit_ceiling` 0 | `credits` with Dreamina's quote and nothing billed. The quote sets the entry's `CREDIT_CEILING`. Each leaves a draft on the canvas ([22-owner-setup.md](22-owner-setup.md#step-6-delete-drafts-left-by-refusals)) | 0 |
| 4 | One host image from text (use 3) at L's scene size | One `[1, H, W, 3]` image in the listed shape nearest the wanted size | The quote from check 3 |
| 5 | One edit with two references of different sizes (use 4) | Both references reach Dreamina in order: `result` shows them in `generation.references[]` | The quote from check 3 |
| 6 | One 15-second show video on `seedance_2.5` with references and two voice lines (use 1), at 720p | The video starts near the first frame and keeps the host and the product. The host speaks each line in the voice's timbre at its step. `result`'s `generation.promptParts` shows each placeholder bound | The quote from check 3 |
| 7 | Cancel check 6's run during its wait, then collect it | The message says the generation keeps running. **Generation: Download** collects it, and it is billed once | None beyond check 6 |
| 8 | When frames-only shots exist: one shot between L's first and closing frames (use 2) | The video starts on the first frame and ends on the last | The quote from check 3 |

## Open questions

| Question | Who decides |
| -------- | ----------- |
| Is a show video on Dreamina worth its credits next to fal's 0.75 US dollars a clip? Credits have a money value only through the plan's price. The owner's plan was discounted, so the comparison uses the regular price on Dreamina's pricing page | The owner, after the video model sweep |
| Do Dreamina's terms allow commercial use of the outputs under the owner's plan, as live-shopping needs? The terms say the services are "generally provided for private, non-commercial use", and the pricing FAQ ties commercial use to the terms and the plan ([research/terms.md](research/terms.md#1-the-terms)) | The owner, from Dreamina's terms and pricing pages ([22-owner-setup.md](22-owner-setup.md#questions-only-the-website-can-answer)) |
| The CLI must be signed in, as the macOS user that runs L's ComfyUI, on every machine that runs a Dreamina entry. Model: Info needs the sign-in too, unlike fal's | The owner, for each machine |
| How many Dreamina generations run at once on one account, and how long does a 15-second video take? Raise the request timeout for show batches, or collect late videos with Generation: Download? | The owner, with L's plan, after check 6 |
| Does Seedance speak an audio reference's line in its timbre, as Wan does? If it speaks the quoted lines itself instead, the entry takes L's planned `text` voice mode | Check 6, then the owner |
| Which Dreamina models become entries, and under which public names? | The owner, from [research/catalog.md](research/catalog.md) |
| One `CREDIT_CEILING` per entry in config, or a control on Video Model and Image Model? L adds no option without the owner's word | The owner, with L's plan |
| After a partial failure, L's image nodes send all their requests again. With Dreamina, a `timeout` or `uncertain` request may still run and bill. Keep that rule for Dreamina entries, or collect such requests instead? | The owner, with L's plan |
| How do L's test loops count Dreamina spending: `creditsAmount` from each `result`, or the balance before and after (`L/SHOWS.md` section 4.4)? | L's plan |

## Names this plan uses from other plans

| Name | Owner | Used for |
| ---- | ----- | -------- |
| `DreaminaImageGenerate`, `DreaminaVideoGenerate`, `DreaminaModelInfo`, `DreaminaGenerationDownload` | [01-decisions.md](01-decisions.md#names-and-identifiers), [04-architecture.md](04-architecture.md) | The node IDs L calls |
| The paid node's inputs, `credit_ceiling`, and `--count 1` | [01-decisions.md](01-decisions.md#the-inputs-of-a-paid-node), [08-runs.md](08-runs.md), [10-node-video.md](10-node-video.md) | The call from Python |
| The modes and the placeholders | [01-decisions.md](01-decisions.md#how-the-mode-is-chosen), [06-model-check.md](06-model-check.md), [07-media.md](07-media.md) | `m2v`, `first_last_frame`, `t2i`, `i2i`, and `{{image1}}` |
| `DREAMINA_REFERENCES` and the `references` output | [01-decisions.md](01-decisions.md#outputs), [07-media.md](07-media.md) | Passing Dreamina outputs on |
| `DreaminaError` and `ErrorCode` | [05-foundation.md](05-foundation.md), [08-runs.md](08-runs.md) | Matching failures by code |
| Model: Info's report | [15-node-model-info.md](15-node-model-info.md) | L's lengths, sizes, and limits |
| Generation records and the request timeout | [08-runs.md](08-runs.md), [14-node-download.md](14-node-download.md), [16-frontend.md](16-frontend.md) | Late videos, and videos left running after a cancel |
| The sign-in, the canvas, and drafts | [22-owner-setup.md](22-owner-setup.md) | Running L's ComfyUI with Dreamina |
| The owner's models and limits | [research/catalog.md](research/catalog.md) | The entries and their examples |
| Runs C-6 and the video model sweep | [21-test-runs.md](21-test-runs.md) | Placeholders and credits |
