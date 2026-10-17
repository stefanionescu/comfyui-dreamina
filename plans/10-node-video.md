# Video Node

This plan builds **Video: Generate** (`VideoGenerate`), the paid node for
every Dreamina model that makes video: from a prompt (`t2v`), from a first
frame or a first and last frame (`first_last_frame`), and from images,
videos, audio, and Elements together (`m2v`). It is one of the three
generation nodes. The shared machinery is in
[06-model-check.md](06-model-check.md) (the live model check, the mode entry,
and the flags), [07-media.md](07-media.md) (uploads, the reference checks
and order, placeholders, downloads, decoding), and [08-runs.md](08-runs.md)
(`GenerateNode`, the run, the record, the wait, and what a cancel does).

**The person types any model name.** Nothing in the code lists or limits
models. The name and every setting are checked against the person's own
Dreamina model list when the workflow is queued and again when the node runs.
The only model name in this node is the starting value of its `model` box,
`seedance_2.0_mini`, which the person replaces freely
([01-decisions.md](01-decisions.md#how-the-nodes-cover-every-model)).

This plan owns the node's class and outputs, what fills them, the starting
values, the frame order, what a cancel means for the person, the help page,
the README row, the video examples' node settings, and the first live runs.
It is the counterpart of `F/plans/10-node-video.md` in the fal pack
(`F=/Users/dr_stone/Documents/work/comfyui-fal`, commit `cef8b6e`), and ports
`F/src/nodes/video.py`. The facts are the owner's video list of 2026-10-16
([research/catalog.md](research/catalog.md#video-models),
`research/captures/model-list-video.json`). Nothing is built yet.

It ships in the **Video and downloads** milestone with
[14-node-download.md](14-node-download.md), because video-04 collects a video
run with Generation: Download ([README.md](README.md#build-order)). Readers:
the engineer who writes `src/nodes/video.py` and
`web/docs/DreaminaVideoGenerate.md`, and the writers of
[17-scripts-and-workflows.md](17-scripts-and-workflows.md) and
[21-test-runs.md](21-test-runs.md).

## Contents

- [Decisions this plan makes](#decisions-this-plan-makes)
- [What Dreamina's video models look like](#what-dreaminas-video-models-look-like)
- [Step 1: Video: Generate](#step-1-video-generate)
- [Step 2: What fills each output](#step-2-what-fills-each-output)
- [Step 3: Register](#step-3-register)
- [Step 4: Help page](#step-4-help-page)
- [Step 5: README row and examples](#step-5-readme-row-and-examples)
- [Step 6: Live checks](#step-6-live-checks)
- [Names this plan uses from other plans](#names-this-plan-uses-from-other-plans)

## Decisions this plan makes

| Question | Decision | Why |
| -------- | -------- | --- |
| Which models? | Any name in the person's live `model list --type video`: five models on the owner's account on 2026-10-16. A model of another kind is refused before paying, naming the node that runs it. | One node per kind of output ([01-decisions.md](01-decisions.md#the-nodes)); 06's match |
| Starting `model` | `seedance_2.0_mini` (`DEFAULT_MODELS["video"]`). Part 0 on 2026-10-17 switched it from `seedance_2.0_fast`: 16 credits against 24 at the same 720p and 4 seconds. | A current Seedance 2.0 model, and the least expensive video model on the owner's list at the starting settings ([research/catalog.md](research/catalog.md#defaults)) |
| Starting `arguments` | `{"ratio": "16:9", "resolution": "720p", "duration": 4}` (`DEFAULT_ARGUMENTS["video"]`) | Every video mode marks `--ratio`, `--resolution`, and `--duration` required with no default. `720p` is the model's only size and 4 seconds its shortest. |
| Starting `credit_ceiling` | `DEFAULT_CEILINGS["video"]` = 20: VID-D, the quote of the starting values (16 credits on 2026-10-17), rounded up to the next multiple of 10 | Part 0, Step 7 of [21-test-runs.md](21-test-runs.md#step-7-check-the-starting-values-and-the-ceiling-defaults) measures VID-D and records it in [research/catalog.md](research/catalog.md#prices) and the README's changes table ([01-decisions.md](01-decisions.md#credits)) |
| Mode | `t2v` with nothing connected; `first_last_frame` with one or two images and nothing else; `m2v` with anything else: a video, audio, an Element, or three or more images. `"mode"` in `arguments` overrides it. | 06's rule, from the skill's "Video mode follows the resolved source type" ([06-model-check.md](06-model-check.md#the-mode-name)) |
| The ratio | Never changes the mode. To use one or two images as references, the person sets `"mode": "m2v"`. | The lists mark `--ratio` required in every video mode, `first_last_frame` included, so it cannot tell a frame from a reference ([01-decisions.md](01-decisions.md#how-the-mode-is-chosen)) |
| Which `first_last_frame` entry | The two-image entry for two images, and the one-image entry for one | Every video model on the list but `seedance_pro_fast` lists the mode twice; 06 picks the entry whose limits fit ([06-model-check.md](06-model-check.md#the-entry)) |
| Frame order | `references` first, then `images`. The first of them is the first frame, and the second the last. | The `--ref` order of [01-decisions.md](01-decisions.md#order) is the frame order: "Two ordered images (first, last)" ([research/cli.md](research/cli.md#generation-nodes)) |
| An Element as a frame | Refused before paying | "An Element must not occupy a `first_last_frame` slot" ([07-media.md](07-media.md#validate_references)) |
| Several videos in one run | `video` is a list, one VIDEO per resource, in `node show` order. The node makes one unless `arguments` sets `count` (1 to 4 on the owner's list). | 06 sends `--count 1` when `count` is not set ([01-decisions.md](01-decisions.md#credits)) |
| Sound | Kept inside the VIDEO, as the downloaded file carries it | ComfyUI's VIDEO carries its audio track, and **Save Video** writes it |
| Last frame | No `last_frame` output | Dreamina returns no separate last frame. ComfyUI's **Get Video Components** gives the frames. |
| Cancel | Dreamina has no cancel. A cancel, a ComfyUI restart, or the request timeout stops only the wait; the generation keeps running and is billed; the record stays, and Generation: Download collects the video. | [01-decisions.md](01-decisions.md#paid-runs). Video runs are the long ones, so the help page says this. |
| Video downloads | Through `resource download`, as for images | Run C-3 confirms the CLI downloads a video. If it does not, this milestone stops, as [07-media.md](07-media.md#live-checks) says. |
| Membership sizes | Never refused; Model: Info shows `vipResolutions` | [01-decisions.md](01-decisions.md#checking-a-model-before-paying) |

## What Dreamina's video models look like

These facts shape the help page, the examples, and the live checks; none
needs code here ([research/catalog.md](research/catalog.md#video-models)):

- **Five models.** `seedance_2.5`, `seedance_2.0`, `seedance_2.0_fast`,
  `seedance_2.0_mini`, and `seedance_pro_fast` (alias `seedance1.0fast`).
- **`t2v`** takes no references on any model.
- **`first_last_frame`** is listed twice on the Seedance 2.x models: exactly
  two images, then exactly one. `seedance_pro_fast` lists only the one-image
  entry, and has no `m2v`.
- **`m2v`** takes 1 to 12 references on Seedance 2.0, Fast, and Mini: up to
  nine images, three videos, and three audio clips, with at least one image
  or video. Seedance 2.5 takes 1 to 50: up to 30 images, 10 videos, and 10
  audio clips, with at least one of the three.
- **Sizes differ, and so does their spelling.** Seedance 2.5 takes `480p`,
  `720p`, and `1080p`; Seedance 2.0 takes `720p`, `1080p`, and `4K`; Fast and
  Mini take only `720p`; Pro Fast takes `720p` and `1080p`. The node checks
  each value exactly as the list writes it.
- **Lengths.** 4 to 15 seconds in steps of 1 on Seedance 2.0, Fast, and Mini;
  4 to 30 on Seedance 2.5; 5 to 10 on Pro Fast.
- **Ratios** are the same six everywhere: 21:9, 16:9, 4:3, 1:1, 3:4, 9:16.
- **`--prompt`** is required in `t2v` and optional in the other modes. It
  takes up to 15,000 characters on Seedance 2.5 and 4,000 on the others.
- **File limits** come from `model <canonical>`, not `model list`: an `m2v`
  video of up to 52,428,800 bytes and 2.0 to 15.4 seconds on Seedance 2.0,
  Fast, and Mini, and 209,715,200 bytes and 1.8 to 30.2 seconds on Seedance
  2.5. The server refuses a larger file at save, before any charge
  ([research/catalog.md](research/catalog.md#file-limits)).
- **The service's own names** (`aspect_ratio`, `duration_ms`) appear only in
  `model <canonical>`. The node takes the CLI's: `ratio` and `duration` in
  seconds.

## Step 1: Video: Generate

Create `src/nodes/video.py`, ported from `F/src/nodes/video.py`, with the
docstring "Video: Generate, the paid node for every Dreamina model that makes
a video." and `VideoGenerate(GenerateNode)`:

```python
class VideoGenerate(GenerateNode):
    """Generate a video from a prompt, frames, or references with any Dreamina video model."""

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
        return cls.build_schema(
            category=MENUS["VIDEO"],
            description="Generate a video from a prompt, frames, or references with any Dreamina video model.",
        )
```

The class attributes are the ones 08's `GenerateNode` reads
([08-runs.md](08-runs.md#step-18-generate-node)), as
[09-node-image.md](09-node-image.md#step-1-image-generate) describes them.
`list_inputs` names the three media sockets, so `GenerateNode.build_schema`
shows all three, and `references` reaches `send` as its one value.

In the same change, add the `"video"` key to `DEFAULT_CEILINGS` in
`src/config/inputs.py`: VID-D, rounded up to the next multiple of 10
([06-model-check.md](06-model-check.md#srcconfiginputspy)).

`GenerateNode.build_schema` returns this schema for the class, written out:

```python
io.Schema(
    node_id=f"{NODE_PREFIX}{cls.__name__}",
    display_name=cls.display_name,
    category=MENUS["VIDEO"],
    description="Generate a video from a prompt, frames, or references with any Dreamina video model.",
    inputs=[
        io.Image.Input(INPUT_NAMES["IMAGES"], optional=True, tooltip=TOOLTIPS["IMAGES"]),
        io.Video.Input(INPUT_NAMES["VIDEOS"], optional=True, tooltip=TOOLTIPS["VIDEOS"]),
        io.Audio.Input(INPUT_NAMES["AUDIO"], optional=True, tooltip=TOOLTIPS["AUDIO"]),
        io.Custom(SOCKET_TYPES["REFERENCES"]).Input(
            INPUT_NAMES["REFERENCES"], optional=True, tooltip=TOOLTIPS["REFERENCES"]
        ),
        io.String.Input(INPUT_NAMES["MODEL"], default=DEFAULT_MODELS["video"], tooltip=TOOLTIPS["MODEL"]),
        io.Int.Input(
            INPUT_NAMES["CREDIT_CEILING"],
            default=cls.default_ceiling,
            min=CREDIT_CEILING_RANGE["MIN"],
            max=CREDIT_CEILING_RANGE["MAX"],
            tooltip=TOOLTIPS["CREDIT_CEILING"],
        ),
        io.Int.Input(
            INPUT_NAMES["RUN_NUMBER"],
            default=RUN_NUMBER["DEFAULT"],
            min=RUN_NUMBER["MIN"],
            max=RUN_NUMBER["MAX"],
            tooltip=TOOLTIPS["RUN_NUMBER"],
        ),
        io.String.Input(INPUT_NAMES["PROMPT"], default="", multiline=True, tooltip=TOOLTIPS["PROMPT"]),
        io.String.Input(
            INPUT_NAMES["ARGUMENTS"],
            default=DEFAULT_ARGUMENTS["video"],
            multiline=True,
            tooltip=ARGUMENTS_TOOLTIPS["video"],
        ),
    ],
    outputs=list(cls.outputs),
    is_input_list=True,
    hidden=[io.Hidden.unique_id],
)
```

The values it resolves to:

| Setting | Value |
| ------- | ----- |
| Node ID | `DreaminaVideoGenerate` |
| Display name | `Video: Generate` |
| Category | `Dreamina/Video` |
| Description | `Generate a video from a prompt, frames, or references with any Dreamina video model.` |
| Inputs, in order | `images`, `videos`, `audio`, `references`, `model`, `credit_ceiling`, `run_number`, `prompt`, `arguments` |
| `model` default | `seedance_2.0_mini` |
| `credit_ceiling` default and range | `DEFAULT_CEILINGS["video"]` = 20 (VID-D, 16 credits, rounded up to the next 10); 0 to 2,147,483,647 |
| `run_number` default and range | 0; 0 to 2,147,483,647 |
| `arguments` default | `{"ratio": "16:9", "resolution": "720p", "duration": 4}` |
| Tooltips | 06's `TOOLTIPS`, and `ARGUMENTS_TOOLTIPS["video"]` for `arguments`, exactly ([06-model-check.md](06-model-check.md#srcconfiginputspy)) |
| Outputs | `video` (VIDEO, list), `references` (`DREAMINA_REFERENCES`), `result` (STRING); each label equals its ID |
| Input lists | `is_input_list=True` |
| Hidden | `io.Hidden.unique_id` |

The class holds no `send` of its own. `GenerateNode` sends the run and fills
the outputs by ID with 08's `build_node_outputs`. The module has no other
code.

### What a run sends

Three runs of this node, as 06 builds them
([06-model-check.md](06-model-check.md#four-runs-walked-through)):

| Connected | `arguments` | Mode entry | Flags 06 builds |
| --------- | ----------- | ---------- | --------------- |
| Nothing | the starting value | `t2v` | `--mode t2v --ratio 16:9 --resolution 720p --duration 4 --count 1` |
| `references` ← one image from Image: Generate | `{"ratio": "9:16", "resolution": "720p", "duration": 4}` | `first_last_frame`, one image | `--mode first_last_frame --ratio 9:16 --resolution 720p --duration 4 --count 1` |
| `references` ← one image, `images` ← one image | `{"mode": "m2v", "ratio": "9:16", "resolution": "720p", "duration": 4}` | `m2v` | `--mode m2v --ratio 9:16 --resolution 720p --duration 4 --count 1` |

Without `"mode": "m2v"`, the third run would be `first_last_frame` with the
reference as the first frame and the image as the last.

## Step 2: What fills each output

The rules 08's `build_node_outputs` implements for these outputs:

1. `video`: every downloaded file of kind `video` from the run's submit ID,
   in the order `node show` lists the resources, each turned into ComfyUI's
   `InputImpl.VideoFromFile` over the bytes in memory by 07's
   `decode_video`, in a worker thread. The pack never writes the file to
   disk.
1. `references`: one `Reference(origin="node", value=<node ID>,
   media="video", …)` for one video, and one `Reference(origin="resource",
   …)` per video for several. The next Dreamina node takes the video as a
   reference with no download or upload.
1. `result`: as in [09-node-image.md](09-node-image.md#step-2-what-fills-each-output).
1. An empty `video` list becomes `ExecutionBlocker(None)`.

08's `GenerationOperation` downloads only the files this node decodes, up to
the **Maximum download size (MB)** setting
([05-foundation.md](05-foundation.md#step-3-settings-constants)).

## Step 3: Register

In `src/nodes/__init__.py`, import `VideoGenerate` and add it to
`NODE_TYPES` after `ImageUpscale`
([04-architecture.md](04-architecture.md#srcnodes)). With
[14-node-download.md](14-node-download.md) in the same milestone,
`NODE_TYPES` becomes `(ImageGenerate, ImageUpscale, VideoGenerate,
AudioGenerate, GenerationDownload, ModelInfo)`. The Elements milestone puts
`ElementAdd` before `GenerationDownload`.

## Step 4: Help page

Create `web/docs/DreaminaVideoGenerate.md`. Its reference is F's
`web/docs/FalVideoGenerate.md` (50 lines), and this page is no longer.

```markdown
# Video: Generate

Runs any Dreamina model that makes video: from a prompt, from a first and last
frame, or from images, video, audio, and Elements together. It outputs the
video, and a reference to it for the next Dreamina node.

## Inputs

| Input            | What it takes                                                                                                                  |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| `images`         | Frames or reference images, uploaded with the run. **Create List** joins several.                                              |
| `videos`         | Reference videos, uploaded with the run.                                                                                       |
| `audio`          | Reference audio, uploaded with the run.                                                                                        |
| `references`     | Outputs of other Dreamina nodes, and Elements, sent with no upload.                                                            |
| `model`          | The model's Dreamina name, such as `seedance_2.5`. The default is `seedance_2.0_mini`.                                         |
| `credit_ceiling` | The most credits the run may cost. A run that costs more stops, and nothing is billed.                                         |
| `run_number`     | Change it to send the same run again.                                                                                          |
| `prompt`         | What happens. `{{image1}}`, `{{video1}}`, or `{{reference1}}` points at an input.                                              |
| `arguments`      | The model's settings as JSON, under Dreamina's flag names, such as `{"ratio": "16:9", "resolution": "720p", "duration": 4}`. |

**Model: Info** shows a model's modes, flags, and allowed values. The node
checks every setting against your Dreamina model list before it pays. It runs
`t2v` with nothing connected, `first_last_frame` with one or two images and
nothing else, and `m2v` with anything else. To use one or two images as
references, set `"mode": "m2v"` in `arguments`.

## Outputs

| Output       | What it carries                                                    |
| ------------ | ------------------------------------------------------------------ |
| `video`      | The video, with any sound the model made.                          |
| `references` | The new video on your Dreamina canvas, for the next Dreamina node. |
| `result`     | Dreamina's record of the run as JSON, with a link to your canvas.  |

## Use

1. Write the prompt, and set `ratio`, `resolution`, and `duration`.
2. Connect frames or references. They go to the model in this order:
   `references`, `images`, `videos`, then `audio`. In `first_last_frame`,
   the first is the first frame, and the second the last.
3. Connect `video` to **Save Video**, and select **Run**.

Dreamina cannot stop a run it has accepted. If you cancel, ComfyUI restarts,
or the **Request timeout (seconds)** passes, the video is still made and
billed. Collect it with **Generation: Download**.

Examples: **video-01-animate-a-host**, **video-02-film-a-product-ad**, and
**video-04-recover-a-video**.

[Dreamina](https://dreamina.capcut.com/ai-tool/home)
```

The nine rows are the node's inputs, in node order, as `comfy:nodes:check`
requires. Generation: Download ships in this milestone, so the page names it
from the start. The Elements milestone adds
**video-03-keep-a-host-across-shots** to the Examples line, which becomes
"Examples: **video-01-animate-a-host**, **video-02-film-a-product-ad**,
**video-03-keep-a-host-across-shots**, and **video-04-recover-a-video**."
The cancel paragraph matches 17's `CANCEL_NOTE` and `RECOVER_NOTE`, which run
V-4 checks against a live cancel
([17-scripts-and-workflows.md](17-scripts-and-workflows.md#scriptsworkflowsdescriptionsnotespy)).

## Step 5: README row and examples

The README node table row ([18-documentation.md](18-documentation.md)):

| Node | What it does | Paid |
| ---- | ------------ | ---- |
| [Video: Generate](web/docs/DreaminaVideoGenerate.md) | Makes video from a prompt, frames, or references with any Dreamina video model. | Yes |

The README example table rows of this milestone (video-03's row arrives with
the Elements milestone, and video-04's is
[14-node-download.md](14-node-download.md)'s):

| Workflow | Input |
| -------- | ----- |
| [Video: Animate a Host](example_workflows/video-01-animate-a-host.json) | A host and a scene |
| [Video: Film a Product Ad](example_workflows/video-02-film-a-product-ad.json) | A host, a product, and a scene |

The video examples' **Video: Generate** settings.
[17-scripts-and-workflows.md](17-scripts-and-workflows.md#example-workflows)
owns the examples: their layout, notes, prompts, and save names. When 17
differs, 17 wins and this plan is corrected. `arguments` is written in full,
because every example but video-04 changes `ratio` from the starting value.
Each step's
credits are Part 0's quotes, which [21-test-runs.md](21-test-runs.md) Part 4
states before each example runs.

| Slug | Milestone | Steps before | Video step | `model` | `arguments` | Connected and mode | Saved as |
| ---- | --------- | ------------ | ---------- | ------- | ----------- | ------------------ | -------- |
| `video-01-animate-a-host` | Video and downloads | **Portrait**: Image: Generate, `{"ratio": "9:16", "resolution": "2K"}` | Animate | starting value | `{"ratio": "9:16", "resolution": "720p", "duration": 4}` | `references` ← Portrait: one image and nothing else, so `first_last_frame`, its one-image entry | `video/dreamina/host` |
| `video-02-film-a-product-ad` | Video and downloads | **Cast**: Image: Generate, `{"ratio": "3:4", "resolution": "2K"}`; **Packshot**: Image: Generate at its starting values | Film | `seedance_2.5` | `{"mode": "m2v", "ratio": "9:16", "resolution": "480p", "duration": 4}` | `references` ← Cast, `images` ← Packshot's `images`; the prompt names `{{reference1}}` and `{{image1}}`; `m2v` set in `arguments` | `video/dreamina/product-ad` |
| `video-03-keep-a-host-across-shots` | Elements | **Cast**; **Keep**: Element: Add, `title` `Host`, `main` ← Cast's `references` | Shot 1, Shot 2 | starting value | `{"ratio": "9:16", "resolution": "720p", "duration": 4}` | `references` ← Keep's Element: `m2v`; each prompt names `{{reference1}}` | `video/dreamina/host-shot-1`, `video/dreamina/host-shot-2` |
| `video-04-recover-a-video` | Video and downloads | none | Shot, shipped bypassed | starting value | starting value | nothing: `t2v` | `video/dreamina/shot`; **Collect** saves `video/dreamina/recovered` ([14-node-download.md](14-node-download.md#the-example)) |

- **video-01** sets `ratio` to the portrait's own `9:16`: the mode requires
  it, and a frame of another shape would not match. Its note says a second
  picture would set the last frame, and that `duration` reaches 15 seconds.
- **video-02** uses Seedance 2.5, the one video model on the list that makes
  `480p`. `references` takes one connection, so the product comes through
  `images`, uploaded again for free, and the host through `references`. One
  reference and one image alone would choose `first_last_frame`, so
  `arguments` sets `"mode": "m2v"`, and the note says why.
- **video-03** ships with the Elements milestone. An Element connected
  chooses `m2v` by itself, so the shots set no `mode`. Each shot is its own
  run and is billed, and **Shot 2** ships on, as 17 explains.
- **video-04** is Generation: Download's example. Its **Shot** ships
  bypassed, so a run as shipped bills nothing. Part 4 of 21 runs it after
  video-01, with **Shot** left off.
- Every video step's note ends with 17's `RECOVER_NOTE`, which says a cancel
  does not stop the generation.

## Step 6: Live checks

Run these through the node after the milestone's commit, with the owner's
approval. [21-test-runs.md](21-test-runs.md#part-2-first-run-of-each-node-milestone)
lists them under Part 2. I-1 is the image run of
[09-node-image.md](09-node-image.md#step-6-live-checks). The credit names are
Part 0's quotes ([21-test-runs.md](21-test-runs.md#step-8-prices-the-later-tables-use)).

| Run | Request | Settles | Credits | If it differs |
| --- | ------- | ------- | ------- | ------------- |
| V-1 | The starting `model` and `arguments`, `prompt` "Waves on a beach at sunset.", sent first with `credit_ceiling` 0, then with the default → **Save Video** `video/dreamina/v1` | The free refusal with Dreamina's quote; `t2v` chosen; the default ceiling covers the starting values; `video` decoded in memory, and **Save Video** writes it with any sound; `references` holding one node; `result` with the node and the canvas link | VID-D | Fix 07's `decode_video` or 08's output builder |
| V-2 | `references` ← I-1's `references` (one image, nothing else), `arguments` `{"ratio": "1:1", "resolution": "720p", "duration": 4}`, `prompt` "The apple rolls slowly off the table." | The one-image `first_last_frame` entry chosen by count; the image sent as `--ref node:…`, the first frame; `ratio` required in this mode | VID-F, quoted again at 1:1 | Fix 06's entry choice |
| V-3 | `images` ← **Load Image** `dreamina-test-apple.png`, `videos` ← **Load Video** `dreamina-test-clip.mp4`, `model` M2V's model with its cheapest `arguments`, `prompt` "{{image1}} bounces in time with {{video1}}." | `m2v` chosen for an image and a video; the MP4 uploaded; `{{image1}}` and `{{video1}}` written as `{{res:…}}`; `requireAnyOfTypes` met | M2V, quoted again with the video | Fix 07's video upload or placeholders |
| V-4 | V-1's graph with a new `run_number`; cancel once the record appears in the state folder's `generations/`; then D-1 collects it | The cancel message names Generation: Download and says the generation keeps running and is billed; the record stays; D-1 lists it, collects the video, and deletes the record; the canvas shows one run, billed once | VID-D | Change the help page's cancel paragraph, 17's `CANCEL_NOTE`, and 01's "Paid runs" to what Dreamina does |

If V-4's run ends before the cancel lands, the node collects it and deletes
the record itself; then V-4 runs again, canceled sooner, as 21 says. Record
each result in the README's changes table. V-4 and D-1 complete contract run
C-14, which stops a wait from outside ComfyUI.

## Names this plan uses from other plans

| Name | Owner | Used for |
| ---- | ----- | -------- |
| `GenerateNode` (`build_schema`, `kind`, `display_name`, `default_ceiling`, `outputs`), `PaidNode` (`list_inputs`), `build_node_outputs`, `GenerationOperation`, the cancel and record rules, `GENERATION_KEEPS_RUNNING` | [08-runs.md](08-runs.md) | The node base and the run |
| `DEFAULT_MODELS`, `DEFAULT_ARGUMENTS`, `DEFAULT_CEILINGS`, `INPUT_NAMES`, `TOOLTIPS`, `ARGUMENTS_TOOLTIPS`, `RUN_NUMBER`, `CREDIT_CEILING_RANGE`, the mode and entry choice | [06-model-check.md](06-model-check.md) | The inputs, their starting values, and the checks before paying |
| `decode_video`, `Reference`, `validate_references` (the Element frame rule), `plan_references`, `format_prompt`, run C-3 | [07-media.md](07-media.md) | Decoding, references, frame order, and placeholders |
| `NODE_PREFIX`, `MENUS["VIDEO"]`, `SOCKET_TYPES["REFERENCES"]`, `NODE_TYPES`, the **Maximum download size (MB)** and **Request timeout (seconds)** settings | [05-foundation.md](05-foundation.md) | Names, registration, and limits |
| `GenerationDownload`, video-04, run D-1 | [14-node-download.md](14-node-download.md) | Collecting a canceled run |
| `ElementAdd` | [13-node-element.md](13-node-element.md) | video-03's Keep step |
| `ImageGenerate`, run I-1 | [09-node-image.md](09-node-image.md) | The examples' first steps and V-2 |
| The examples, `CANCEL_NOTE`, `RECOVER_NOTE` | [17-scripts-and-workflows.md](17-scripts-and-workflows.md) | Step 5 and the help page's cancel paragraph |
| VID-D, VID-F, M2V, V-1 to V-4 | [21-test-runs.md](21-test-runs.md) | The starting ceiling and the live checks |
