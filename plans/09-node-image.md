# Image Node

This plan builds **Image: Generate** (`ImageGenerate`), the paid node for
every Dreamina model that makes images: from a prompt (`t2i`), and from
images, earlier Dreamina outputs, and Elements (`i2i`). It is one of the three
generation nodes. Everything it shares with the others is built elsewhere:

- [06-model-check.md](06-model-check.md) reads the typed model from the
  person's live model list, chooses the mode entry, checks `prompt` and
  `arguments` against it, and builds the mode and flag part of the run call.
- [07-media.md](07-media.md) splits and uploads connected images, checks the
  references against the chosen entry, orders them, writes the placeholders
  in the CLI's form, and decodes downloaded images.
- [08-runs.md](08-runs.md) builds `GenerateNode`, which sends the run, records
  it, waits, downloads, and fills the node's outputs by their IDs.

**The person types any model name.** Nothing in the code lists or limits
models. The name and every setting are checked against the person's own
Dreamina model list when the workflow is queued and again when the node runs.
The only model name in this node is the starting value of its `model` box,
`seedream_5.0_lite`, which the person replaces freely
([01-decisions.md](01-decisions.md#how-the-nodes-cover-every-model)).

This plan owns what is particular to images: the node's class and outputs,
what fills them, the starting values, the help page, the README row, the
image examples' node settings, and the first live runs. It is the counterpart
of `F/plans/09-node-image.md` in the fal pack
(`F=/Users/dr_stone/Documents/work/comfyui-fal`, commit `cef8b6e`), and ports
`F/src/nodes/image.py`. The facts are the owner's image list of 2026-10-16
([research/catalog.md](research/catalog.md#image-models),
`research/captures/model-list-image.json`). Nothing is built yet.

It ships in the **Image** milestone of the [build order](README.md#build-order),
after Media and runs and Model: Info. Readers: the engineer who writes
`src/nodes/image.py` and `web/docs/DreaminaImageGenerate.md`, and the
writers of [17-scripts-and-workflows.md](17-scripts-and-workflows.md) and
[21-test-runs.md](21-test-runs.md).

## Contents

- [Decisions this plan makes](#decisions-this-plan-makes)
- [What Dreamina's image models look like](#what-dreaminas-image-models-look-like)
- [Step 1: Image: Generate](#step-1-image-generate)
- [Step 2: What fills each output](#step-2-what-fills-each-output)
- [Step 3: Register](#step-3-register)
- [Step 4: Help page](#step-4-help-page)
- [Step 5: README row and examples](#step-5-readme-row-and-examples)
- [Step 6: Live checks](#step-6-live-checks)
- [Names this plan uses from other plans](#names-this-plan-uses-from-other-plans)

## Decisions this plan makes

| Question | Decision | Why |
| -------- | -------- | --- |
| Which models? | Any name in the person's live `model list --type image`: 12 models on the owner's account on 2026-10-16. A model of another kind is refused before paying, naming the node that runs it. | One node per kind of output ([01-decisions.md](01-decisions.md#the-nodes)); 06's match |
| Starting `model` | `seedream_5.0_lite` (`DEFAULT_MODELS["image"]`) | Current Seedream, and its `2K` needs no membership ([research/catalog.md](research/catalog.md#defaults)) |
| Starting `arguments` | `{"ratio": "1:1", "resolution": "2K"}` (`DEFAULT_ARGUMENTS["image"]`) | Every image model marks `--resolution` required, and all but `seedream_5.0_pro` mark `--ratio` required, with no default. An empty box would refuse the starting model. `2K` is its smallest size. |
| Starting `credit_ceiling` | `DEFAULT_CEILINGS["image"]` = 10: IMG-D, the quote of the starting values (6 credits on 2026-10-17), rounded up to the next multiple of 10 | Part 0, Step 7 of [21-test-runs.md](21-test-runs.md#step-7-check-the-starting-values-and-the-ceiling-defaults) measures IMG-D and records it in [research/catalog.md](research/catalog.md#prices) and the README's changes table ([01-decisions.md](01-decisions.md#credits)) |
| Mode | `t2i` with nothing connected; `i2i` with any image, image reference, or Element. `"mode"` in `arguments` overrides it. | 06's rule. `seedream_4.6` and `seedream_4.7` list `t2i` with 0 to 14 images, so `"mode": "t2i"` with images works there, as the list says ([07-media.md](07-media.md#validate_references)). |
| How many images | One, unless `arguments` sets `count`, within the model's `--count` maximum (1, 4, or 8 on the owner's list) | 06 sends `--count 1` when `count` is not set ([01-decisions.md](01-decisions.md#credits)) |
| Image order | `images` holds the run's resources in the order `node show` lists them | 07's download order ([07-media.md](07-media.md#step-9-downloads)) |
| Masks | None. `images` is three channels, `[1, H, W, 3]`. | Dreamina's image modes make opaque pictures, and 01 has no mask socket ([07-media.md](07-media.md#decisions-this-plan-makes)) |
| `references` output | The run's canvas node for one image; each resource for several | [01-decisions.md](01-decisions.md#references): the next node gets each output, not only the node's selected one |
| A run with no image | `images` stops the nodes connected to it (`ExecutionBlocker`); `result` still carries the node | Outputs never change ([01-decisions.md](01-decisions.md#how-the-nodes-cover-every-model)) |
| Cancel | A cancel stops only the wait. The images are still made and billed, and Generation: Download collects them. | Dreamina has no cancel ([01-decisions.md](01-decisions.md#paid-runs)) |
| Membership sizes | Never refused; Model: Info shows `vipResolutions` | [01-decisions.md](01-decisions.md#checking-a-model-before-paying) |

## What Dreamina's image models look like

These facts shape the help page and the examples; none needs code here
([research/catalog.md](research/catalog.md#image-models)):

- **Every image model has `t2i` and `i2i`,** with the same flags in both:
  `--prompt`, `--ratio`, `--resolution`, and `--count`. `--prompt` takes 1 to
  4,000 characters in `t2i` and 0 to 4,000 in `i2i`, so `i2i` runs with an
  empty prompt, and 08 sends the node's title then.
- **Sizes differ by model.** Seedream 4.x and 5.0 Lite take `2K` and `4K`.
  Seedream 5.0 Pro takes `1.5K`, `2K`, and `4K`. GPT Image 2, GPT Image 2.5
  Flare and Sunburst, Gemini 3 Image Pro (alias `nano_banana`), and
  `jm_image_model_gg_bp_21` take `1K`, `2K`, and `4K`.
- **Ratios** are the same eight on every model (21:9, 16:9, 3:2, 4:3, 1:1,
  3:4, 2:3, 9:16). `seedream_5.0_pro` alone leaves `--ratio` optional.
- **Counts** reach 1 on GPT Image 2.5, 4 on most others, and 8 on Seedream
  4.x and 5.0 Lite.
- **`i2i` image limits** run from 1 to 6 (Seedream, GPT Image 2, Gemini) up
  to 16 (GPT Image 2.5).
- **Membership.** `vipRequired` is false everywhere. `vipResolutions` names
  `4K` for Seedream and every size for the GPT, Gemini, and `jm_` models.
- **File limits** are 50 MB and 8,192 pixels per side for every image input.
  The server refuses a larger file at save, before any charge
  ([research/catalog.md](research/catalog.md#file-limits)).

## Step 1: Image: Generate

Create `src/nodes/image.py`, ported from `F/src/nodes/image.py`, with the
docstring "Image: Generate, the paid node for every Dreamina model that makes
images." and `ImageGenerate(GenerateNode)`:

```python
class ImageGenerate(GenerateNode):
    """Generate or edit images with any Dreamina image model."""

    kind = "image"
    display_name = "Image: Generate"
    default_ceiling = DEFAULT_CEILINGS["image"]
    list_inputs = frozenset({INPUT_NAMES["IMAGES"]})
    outputs = (
        io.Image.Output("images", display_name="images", is_output_list=True),
        io.Custom(SOCKET_TYPES["REFERENCES"]).Output("references", display_name="references"),
        io.String.Output("result", display_name="result"),
    )

    @classmethod
    @override
    def define_schema(cls) -> io.Schema:
        """Describe the node: its name, its menu, and its inputs."""
        return cls.build_schema(
            category=MENUS["IMAGE"],
            description="Generate or edit images with any Dreamina image model.",
        )
```

The class attributes are the ones 08's `GenerateNode` reads
([08-runs.md](08-runs.md#step-18-generate-node)):

- `kind`: the `Kind` 06's model check runs against;
- `display_name`: the node's name, also the canvas node's title when the
  prompt is empty;
- `default_ceiling`: the starting `credit_ceiling`;
- `list_inputs`: 08's `PaidNode` rule. `images` reaches `send` as the whole
  list, and every other input, `references` included, as its one value.
  `GenerateNode.build_schema` shows a media socket only when `list_inputs`
  names it, and always shows `references`;
- `outputs`: the output sockets, filled by ID.

In the same change, add `DEFAULT_CEILINGS` to `src/config/inputs.py` with its
`"image"` key, as [06-model-check.md](06-model-check.md#srcconfiginputspy)
fixes it: IMG-D, rounded up to the next multiple of 10. 11 and 10 add their
keys in their milestones.

`GenerateNode.build_schema` returns this schema for the class, written out:

```python
io.Schema(
    node_id=f"{NODE_PREFIX}{cls.__name__}",
    display_name=cls.display_name,
    category=MENUS["IMAGE"],
    description="Generate or edit images with any Dreamina image model.",
    inputs=[
        io.Image.Input(INPUT_NAMES["IMAGES"], optional=True, tooltip=TOOLTIPS["IMAGES"]),
        io.Custom(SOCKET_TYPES["REFERENCES"]).Input(
            INPUT_NAMES["REFERENCES"], optional=True, tooltip=TOOLTIPS["REFERENCES"]
        ),
        io.String.Input(INPUT_NAMES["MODEL"], default=DEFAULT_MODELS["image"], tooltip=TOOLTIPS["MODEL"]),
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
            default=DEFAULT_ARGUMENTS["image"],
            multiline=True,
            tooltip=ARGUMENTS_TOOLTIPS["image"],
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
| Node ID | `DreaminaImageGenerate` |
| Display name | `Image: Generate` |
| Category | `Dreamina/Image` |
| Description | `Generate or edit images with any Dreamina image model.` |
| Inputs, in order | `images`, `references`, `model`, `credit_ceiling`, `run_number`, `prompt`, `arguments` |
| `model` default | `seedream_5.0_lite` |
| `credit_ceiling` default and range | `DEFAULT_CEILINGS["image"]` = 10 (IMG-D, 6 credits, rounded up to the next 10); 0 to 2,147,483,647 |
| `run_number` default and range | 0; 0 to 2,147,483,647 |
| `arguments` default | `{"ratio": "1:1", "resolution": "2K"}` |
| Tooltips | 06's `TOOLTIPS`, and `ARGUMENTS_TOOLTIPS["image"]` for `arguments`, exactly ([06-model-check.md](06-model-check.md#srcconfiginputspy)) |
| Outputs | `images` (IMAGE, list), `references` (`DREAMINA_REFERENCES`), `result` (STRING); each label equals its ID |
| Input lists | `is_input_list=True` |
| Hidden | `io.Hidden.unique_id` |

- **`is_input_list=True`.** Image: Generate outputs its images as a list.
  Without input lists, ComfyUI would run the node, and bill it, once per
  image. With them, the image list arrives whole, and **Create List** joins
  several sources into `images`. `references` takes one connection.
- **The tooltips** are shared with Video: Generate and Audio: Generate, so the
  `images` tooltip names the `{{image1}}` placeholder and **Create List**.

The class holds no `send` of its own. `GenerateNode` sends the run and fills
the outputs by ID with 08's `build_node_outputs`. The module has no other
code.

## Step 2: What fills each output

08's `build_node_outputs` is one function shared by the three generation
nodes and Generation: Download
([14-node-download.md](14-node-download.md)). The rules for this node's
outputs:

1. `images`: every downloaded file of kind `image` from the run's submit ID,
   in the order `node show` lists the resources, decoded by 07's
   `decode_images` in a worker thread. Each is `[1, H, W, 3]` at its own size.
   A fourth channel is dropped.
1. `references`: one `Reference(origin="node", value=<node ID>,
   media="image", title=<node title>)` when the run made one image, and one
   `Reference(origin="resource", value=<resource ID>, media="image", …)` per
   image when it made several. The next Dreamina node uses them with no
   download or upload.
1. `result`: the canvas node as `node show` returns it, as JSON, with the
   canvas link: the prompt as saved, the reference slots, each resource's
   ID, size, and format, and `creditsAmount`
   ([01-decisions.md](01-decisions.md#outputs)).
1. An empty `images` list becomes `ExecutionBlocker(None)`. `result` is
   always filled.

08's `GenerationOperation` downloads only the files this node decodes.

## Step 3: Register

In `src/nodes/__init__.py`, import `ImageGenerate` and add it first to
`NODE_TYPES` ([04-architecture.md](04-architecture.md#srcnodes)). At this
milestone `NODE_TYPES` is `(ImageGenerate,)`: Model: Info is committed
unregistered before it, and registered in the Audio milestone.

## Step 4: Help page

Create `web/docs/DreaminaImageGenerate.md`. Its reference is F's
`web/docs/FalImageGenerate.md` (44 lines). This page is 43 lines, and 44 once
the Upscale milestone's Examples line wraps.

```markdown
# Image: Generate

Runs any Dreamina model that makes images, from a prompt or from images. It
outputs the images, and references to them for the next Dreamina node.

## Inputs

| Input            | What it takes                                                                                              |
| ---------------- | ---------------------------------------------------------------------------------------------------------- |
| `images`         | Images to edit or combine, uploaded with the run. **Create List** joins several.                           |
| `references`     | Images from other Dreamina nodes, and Elements, sent with no upload.                                       |
| `model`          | The model's Dreamina name, such as `gpt_image_2`. The default is `seedream_5.0_lite`.                      |
| `credit_ceiling` | The most credits the run may cost. A run that costs more stops, and nothing is billed.                     |
| `run_number`     | Change it to send the same run again.                                                                      |
| `prompt`         | What to make or change. `{{image1}}` or `{{reference1}}` points at an input.                               |
| `arguments`      | The model's settings as JSON, under Dreamina's flag names, such as `{"ratio": "1:1", "resolution": "2K"}`. |

**Model: Info** shows a model's flags and allowed values. The node checks
every setting against your Dreamina model list before it pays. It runs `t2i`
with nothing connected, and `i2i` with references or images, sent in that
order. Set `"mode"` in `arguments` to choose.

## Outputs

| Output       | What it carries                                                     |
| ------------ | ------------------------------------------------------------------- |
| `images`     | Every image, each at its own size.                                  |
| `references` | The new images on your Dreamina canvas, for the next Dreamina node. |
| `result`     | Dreamina's record of the run as JSON, with a link to your canvas.   |

## Use

1. Write the prompt, and set `ratio` and `resolution` in `arguments`.
2. To edit, connect images to `images`, or another node's `references`.
3. Connect `images` to **Save Image**, and select **Run**.

The node makes one image unless `arguments` sets `count`. Once Dreamina
accepts a run, a cancel stops only the wait: the images are still made and
billed. Collect them with **Generation: Download**.

Examples: **image-01-design-a-host** and **image-02-edit-a-product-photo**.

[Dreamina](https://dreamina.capcut.com/ai-tool/home)
```

The seven rows are the node's inputs, in node order, as `comfy:nodes:check`
requires ([17-scripts-and-workflows.md](17-scripts-and-workflows.md)). A
model's own flags are not listed: they differ for every model, and the page
points to **Model: Info** for them.

Two sentences arrive later, so the page never names a node or workflow that
has not shipped:

- **"Collect them with Generation: Download."** The page ships in the Image
  milestone with its cancel paragraph ending after "billed.". The Video and
  downloads milestone adds the sentence, as
  [14-node-download.md](14-node-download.md#step-5-help-page) says.
- **image-03.** The Upscale milestone adds **image-03-upscale-a-poster** to
  the Examples line, which becomes "Examples: **image-01-design-a-host**,
  **image-02-edit-a-product-photo**, and **image-03-upscale-a-poster**." Its
  Poster step is an Image: Generate
  ([17-scripts-and-workflows.md](17-scripts-and-workflows.md#image-03-upscale-a-poster)).

If run C-6 shows that `{{res:…}}` does not bind an upload, 07 refuses
`{{image1}}`, and the `prompt` row names `{{reference1}}` only
([07-media.md](07-media.md#live-checks)).

## Step 5: README row and examples

The README node table row ([18-documentation.md](18-documentation.md)):

| Node | What it does | Paid |
| ---- | ------------ | ---- |
| [Image: Generate](web/docs/DreaminaImageGenerate.md) | Makes or edits images with any Dreamina image model. | Yes |

The README example table rows, in the Image milestone (image-03's row
arrives with the Upscale milestone):

| Workflow | Input |
| -------- | ----- |
| [Image: Design a Host](example_workflows/image-01-design-a-host.json) | A host description |
| [Image: Edit a Product Photo](example_workflows/image-02-edit-a-product-photo.json) | A product photo and a change |

The image examples' **Image: Generate** settings.
[17-scripts-and-workflows.md](17-scripts-and-workflows.md#example-workflows)
owns the examples: their layout, notes, prompts, and save names. When 17
differs, 17 wins and this plan is corrected. `arguments` is written only
where it differs from the starting value. Each step's credits are Part 0's
quotes for these settings, which
[21-test-runs.md](21-test-runs.md) Part 4 states before each example runs.

| Slug | Milestone | Step | `model` | `arguments` | Connected | Saved as |
| ---- | --------- | ---- | ------- | ----------- | --------- | -------- |
| `image-01-design-a-host` | Image | Design | starting value | `{"ratio": "3:4", "resolution": "2K"}` | nothing: `t2i`; **Host** text block → `prompt` | `image/dreamina/host` |
| `image-02-edit-a-product-photo` | Image | Edit | starting value | `{"ratio": "1:1", "resolution": "2K"}` | `images` ← **Load Image** with the person's product photo: `i2i`; **Change** text block → `prompt`, naming `{{image1}}` | `image/dreamina/product-edit` |
| `image-03-upscale-a-poster` | Upscale | Poster | starting value | `{"ratio": "3:4", "resolution": "2K"}` | nothing: `t2i`; its `references` feed **Enlarge**, an Image: Upscale ([12-node-upscale.md](12-node-upscale.md#step-7-readme-row-and-examples)) | `image/dreamina/poster` |

- **image-01** is the least expensive example that needs nothing from the
  person. `3:4` is the only change from the starting `arguments`, a portrait
  frame, and `2K` is the starting model's smallest size, with no membership.
- **image-02** needs a file from the person, and it shows an upload and the
  `{{image1}}` placeholder. Seedream 5.0 Lite takes 1 to 6 pictures in
  `i2i`, and `2K` is its smallest size. Its quote of 6 passes
  `DEFAULT_CEILINGS["image"]`.
- **image-03** ships with the Upscale milestone, after Image, as
  `image-03-upscale-a-poster`.
- **audio-02**, **video-01**, **video-02**, and **video-03** start with an
  Image: Generate step of their own, at `{"ratio": "3:4", "resolution":
  "2K"}`, `{"ratio": "9:16", "resolution": "2K"}`, or the starting values
  ([17-scripts-and-workflows.md](17-scripts-and-workflows.md#example-workflows)).

## Step 6: Live checks

Run these through the node after the Image milestone's commit, with the
owner's approval. [21-test-runs.md](21-test-runs.md#part-2-first-run-of-each-node-milestone)
lists them under Part 2, after K-1, the free run of 06's refusals
([06-model-check.md](06-model-check.md#live-check)). The credit names are
Part 0's quotes ([21-test-runs.md](21-test-runs.md#step-8-prices-the-later-tables-use)).

| Run | Request | Settles | Credits | If it differs |
| --- | ------- | ------- | ------- | ------------- |
| I-1 | The starting `model` and `arguments`, `prompt` "A red apple on a white table.", the default `credit_ceiling` → **Save Image** `image/dreamina/i1` | The live read and the match; `t2i` chosen; `--count 1` sent; the default ceiling covers the starting values; `images` decoded at its own size; `references` holding one node; `result` with the node and the canvas link; the canvas created on first use; pressing **Run** again with nothing changed sends nothing | IMG-D | Fix 06's check or 08's output builder first |
| I-2 | `references` ← I-1's `references`, `prompt` "Make {{reference1}} green.", the starting `arguments` | `i2i` chosen for a reference; the reference sent as `--ref node:…` with no download or upload; `{{reference1}}` written as `{{node:…}}`; the canvas shows an edge from I-1's node | IMG-DE | Fix 07's `format_prompt` or 06's mode choice |
| I-3 | `images` ← **Load Image** `dreamina-test-apple.png`, `prompt` "Make {{image1}} blue."; then the same with a new `run_number` | The upload path: one PNG uploaded and sent as `--ref res:…`; `{{image1}}` written as `{{res:…}}`, bound as run C-6 found; the second run uploads again, with a new resource ID | 2 × IMG-DE | Fix 07's upload or placeholder code |

The ceiling refusal is K-1's step 6: the starting values with
`credit_ceiling` one below IMG-D stop at Dreamina's quote, bill nothing, and
leave a draft on the canvas. Record each result in the README's changes
table.

## Names this plan uses from other plans

| Name | Owner | Used for |
| ---- | ----- | -------- |
| `GenerateNode` (`build_schema`, `kind`, `display_name`, `default_ceiling`, `outputs`), `PaidNode` (`list_inputs`), `build_node_outputs`, `GenerationOperation` | [08-runs.md](08-runs.md) | The node base, the run, and output filling |
| `DEFAULT_MODELS`, `DEFAULT_ARGUMENTS`, `DEFAULT_CEILINGS`, `INPUT_NAMES`, `TOOLTIPS`, `ARGUMENTS_TOOLTIPS`, `RUN_NUMBER`, `CREDIT_CEILING_RANGE`, the mode choice, run K-1 | [06-model-check.md](06-model-check.md) | The inputs, their starting values, and the checks before paying |
| `decode_images`, `Reference`, `validate_references`, `format_prompt`, run C-6 | [07-media.md](07-media.md) | Decoding, the `references` output, and placeholders |
| `NODE_PREFIX`, `MENUS["IMAGE"]`, `SOCKET_TYPES["REFERENCES"]`, `NODE_TYPES` | [05-foundation.md](05-foundation.md) | Names and registration |
| `ImageUpscale` | [12-node-upscale.md](12-node-upscale.md) | image-03's Enlarge step |
| The examples, their notes, prompts, and save names | [17-scripts-and-workflows.md](17-scripts-and-workflows.md) | Step 5 |
| `GenerationDownload`, its help-page sentence | [14-node-download.md](14-node-download.md) | The cancel sentence added in the Video and downloads milestone |
| `ModelInfo` | [15-node-model-info.md](15-node-model-info.md) | The help page's pointer to each model's flags |
| IMG-D, IMG-DE, K-1, I-1 to I-3 | [21-test-runs.md](21-test-runs.md) | The starting ceiling and the live checks |
