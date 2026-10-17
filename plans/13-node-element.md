# Element Node

This plan builds **Element: Add** (`ElementAdd`), the free node that makes a
Dreamina Element: one recurring character, product, or place, bound to a main
image, more angles, and a voice. A later **Video: Generate**, **Image:
Generate**, or **Audio: Generate** takes the Element in `references`, and
`{{reference1}}` places it in the prompt. Creating an Element generates
nothing and bills nothing.

It is built on the skeleton of F's **File: Add** (`F/src/nodes/files.py`):
input lists, connected media split into items, and one output value
([04-architecture.md](04-architecture.md#port-map)). The shared machinery is
in [07-media.md](07-media.md) (local media, uploads, references) and
[08-runs.md](08-runs.md) (the CLI runner, the failure map, the version gate,
the canvas).

This plan owns `src/dreamina/elements.py`, `src/nodes/element.py`, the
Element's messages, its help page, its README row, the node settings of its
example, and its first live run. The facts are from the CLI's `schema` for
release 1.0.3 (`node create element`),
[02-dreamina-contract.md](02-dreamina-contract.md#elements), and the skill
(`SKILL.md`, "Offer optional building blocks" and "Consistency across
outputs"), read on 2026-10-16.

It ships in the **Elements** milestone, the last node milestone, because its
example feeds the Element to Video: Generate
([README.md](README.md#build-order)). Commit:
`feat(nodes): add the element node`.

## Contents

- [Why the node exists](#why-the-node-exists)
- [Decisions](#decisions)
- [Step 1: Constants, records, and messages](#step-1-constants-records-and-messages)
- [Step 2: Creating the Element](#step-2-creating-the-element)
- [Step 3: Element: Add](#step-3-element-add)
- [Step 4: What fills the output](#step-4-what-fills-the-output)
- [Step 5: Register](#step-5-register)
- [Step 6: Help page](#step-6-help-page)
- [Step 7: README row and examples](#step-7-readme-row-and-examples)
- [Step 8: Live checks](#step-8-live-checks)
- [Names this plan uses from other plans](#names-this-plan-uses-from-other-plans)

## Why the node exists

A live-shopping video shows the same host and the same product in shot after
shot. Each shot is a separate run, and a prompt alone does not keep a face or
a label the same. Dreamina's skill says so, and names the Element as its own
answer:

- "Repeating names or descriptions does not bind a specific object."
- "An **Element** represents a recurring character, object, product,
  environment, or other visual identity. When the same object needs a
  consistent identity across independently generated images or shots,
  consider creating or reusing an Element as the shared reference for later
  image/video nodes."
- "Choose clear, recognizable material as the Element's primary source and
  suitable additional images as auxiliary sources."
- "Bind suitable existing material directly; creating an Element does not
  require extra generation."

A paid node can already take the host image itself in `references`. The
Element adds two things a single image cannot: more angles of the same
subject, and a voice, kept together under one name on the canvas. The skill
also says Elements are optional ("not prerequisites for every task"), so the
pack offers the node and never adds an Element by itself. The owner confirms
keeping it ([01-decisions.md](01-decisions.md#decisions-the-owner-should-confirm)).

## Decisions

| Question | Decision | Why |
| -------- | -------- | --- |
| Is it paid? | No. One `node create element` call, with no `--run`, no submit ID, and no ceiling. It is not a `PaidNode`: no `run_number`, no `credit_ceiling`, no account cache token. | The schema: "Create an element node without starting generation", `confirmation: false`. [02-dreamina-contract.md](02-dreamina-contract.md#what-is-billed-when-something-fails): Elements are not billed. |
| What does `main` take? | Exactly one image: one ComfyUI image frame, or one `references` item whose media is `image`. | `--main` is required and "must be usable and type-matched": an image ([02-dreamina-contract.md](02-dreamina-contract.md#elements)). |
| What does `auxiliary` take? | Any number of images: ComfyUI image frames and image references. The pack sets no count; Dreamina decides. | `--auxiliary` is repeatable, images only. The schema gives no count, and the owner's rule forbids invented limits. |
| What does `voice` take? | At most one audio: one ComfyUI audio clip, or one `references` item whose media is `audio`, such as Audio: Generate's output. | `--voice` takes one audio node or resource. |
| How do the bindings name their sources? | Bare IDs: a node reference's `node_…` ID, a resource reference's UUID, and an upload's new resource UUID. Never the `node:` or `res:` forms. | The schema and the skill: "Subject elements and timeline selectors keep their existing bare Node ID / Resource ID contracts". |
| Node or resource? | A reference keeps its origin. A node binding "follows that node"; a resource binding is "frozen". A ComfyUI image or clip is uploaded and bound by its resource UUID. | The schema's `--main`: "Prefer Node ID for an existing canvas source … Use Resource ID for media without a source node (such as uploads)". |
| The order of `auxiliary` | Node bindings first, then resource bindings, each in socket order. | The schema's `--auxiliary` constraint: "node sources precede resource sources". |
| Why input lists (`is_input_list=True`)? | Image: Generate outputs its images as a list. Without input lists, ComfyUI would run the node once per image and make one Element each. With them, every connected value arrives whole, and the node makes one Element. | F's File: Add takes input lists for the same reason. |
| Why must `title` be set? | It is the Element's name on the canvas, where the person finds and reuses it. An empty title is refused, as F's File: Add refuses an empty `field`, so no Element is made without a name the person chose. Its length is checked against the schema's limit, 512 UTF-16 code units, before anything is uploaded. | The schema's `--title`: "at most 512 UTF-16 code units". A refusal after the uploads would leave uploaded files on the canvas. |
| `description` | Sent as `--description` when it is not blank. Empty sends nothing. | The owner's rule: empty sends nothing. The schema gives it no limit. |
| ComfyUI's cache | The node keeps ComfyUI's normal cache. The same inputs return the Element made last; a new input makes a new Element on the canvas. | A free node with no run number, as F's free nodes. A second Element of the same subject costs nothing. |
| Progress bar | None, as F's File: Add and Model: Info have none. The work is a few uploads and one free call. | No paid steps to report. |
| Timeout and cancel | The **Request timeout (seconds)** setting bounds the uploads and the call together. A cancel or a timeout stops the CLI call, which `send_command` kills. Nothing is billed either way; an Element made just before the stop stays on the canvas. | Free calls are safe to stop. |
| How is it used? | A later paid node takes the output in `references`. Video: Generate then chooses `m2v`, Image: Generate `i2i`, and Audio: Generate `tts` with `omni-dubbing`, by 01's mode rules. `{{reference1}}` in the prompt becomes `{{node:<element node ID>}}`. | [01-decisions.md](01-decisions.md#how-the-mode-is-chosen); the skill: "Pass it as `--ref node:<element-node-id>` with `--mode m2v`". An Element "must not occupy a `first_last_frame` frame slot". |

How a mode's reference limits count an Element is run C-15's question. The
lists name only `image`, `video`, and `audio` as media types
([research/catalog.md](research/catalog.md#what-the-lists-show)). 07's
`validate_references` owns that rule, and C-15's result corrects it.

## Step 1: Constants, records, and messages

Add to `src/config/dreamina.py` ([08-runs.md](08-runs.md) creates it), with
its comment directly above it:

```python
# The schema's limit for a node or Element title: at most 512 UTF-16 code units.
TITLE_MAX_UNITS = 512
```

08's `REQUIRED_COMMANDS` already lists `"node create element"` with
`project-id`, `main`, `auxiliary`, `voice`, `title`, and `description`, so
the version gate refuses a CLI without any flag the node sends.

Add to `src/types/references.py` ([07-media.md](07-media.md) creates it):

```python
@dataclass(frozen=True, slots=True)
class ElementRequest:
    """One Element to create, every source already on the canvas.

    Attributes:
        main: The primary image.
        auxiliary: More images of the same subject, node sources first.
        voice: The voice, or None.
        title: The Element's name on the canvas.
        description: A note kept with the Element; empty sends nothing.

    """

    main: Reference
    auxiliary: tuple[Reference, ...]
    voice: Reference | None
    title: str
    description: str
```

Add to `src/config/messages/inputs.py` ([06-model-check.md](06-model-check.md)
creates it):

| Constant                  | Text |
| ------------------------- | ---- |
| `ELEMENT_MAIN_COUNT`      | `Connect one image to main: the clearest image of the subject. Connect other angles to auxiliary.` |
| `ELEMENT_MAIN_MEDIA`      | `Connect an image to main. An Element, a video, or audio cannot be an Element's main image.` |
| `ELEMENT_AUXILIARY_MEDIA` | `Connect only images to auxiliary, such as the side and the back of the subject.` |
| `ELEMENT_VOICE_COUNT`     | `Connect one voice clip to voice.` |
| `ELEMENT_VOICE_MEDIA`     | `Connect audio to voice, such as the references output of Audio: Generate.` |
| `ELEMENT_TITLE_EMPTY`     | `Type the Element's name into title, such as Host. Your Dreamina canvas shows the Element under this name.` |
| `ELEMENT_TITLE_LENGTH`    | `Shorten title to at most {maximum} characters. An emoji counts as two.` |

A timeout uses `FREE_TIMEOUT` in `src/config/messages/run.py`, which
[15-node-model-info.md](15-node-model-info.md) adds for Model: Info, the
first free node that needs it: `{node} did not finish within the request
timeout of {seconds} seconds in Dreamina Settings. It bills nothing. Select
Run to try again.`

A title or description that arrives as a list of several different values
(only a linked list of texts can do that) is refused with `SINGLE_VALUE`, the
message the paid nodes' input-list rule uses for the same case
([08-runs.md](08-runs.md)).

## Step 2: Creating the Element

Create `src/dreamina/elements.py` with the docstring "Create a Dreamina
Element from sources already on the canvas; it generates nothing and bills
nothing.".

```python
async def create_element(project_id: str, request: ElementRequest, deadline: float) -> Reference:
```

1. Build the arguments, each source as its bare `Reference.value`:

   ```text
   node create element --project-id <canvas> --main <main>
     [--voice <voice>] [--auxiliary <id>]… --title <title>
     [--description <description>]
   ```

   `--voice` only when `request.voice` is set, one `--auxiliary` per item in
   `request.auxiliary`, and `--description` only when it is not blank.
1. `send_command(arguments, deadline - time.monotonic())`. `deadline` is the
   `time.monotonic()` value at which the request timeout ends, as 07's calls
   take it. A non-zero exit raises `build_failure(result, …)`
   ([08-runs.md](08-runs.md#step-4-failures)), which maps a source Dreamina
   finds unusable to its invalid-input message with the CLI's cleaned
   `validation.detail`.
1. Read the reply with 08's `ElementReply` (`node: NodeView`, whose
   `subjects` reads `subjectBindings`), which
   [12-node-upscale.md](12-node-upscale.md) adds for its import reply. A
   payload that does not validate raises 08's `CLI_REPLY_INVALID` with
   `TRANSPORT`. Return `Reference(origin="node", value=reply.node.node_id,
   media="element", title=request.title)`: the Element node, which later runs
   send as `--ref node:<id>`.

The pack never retries the call. A lost reply is reported with 08's message;
a second run makes a second Element, for free.

`__all__`: `create_element`.

## Step 3: Element: Add

Create `src/nodes/element.py` with the docstring "Element: Add: make a
Dreamina Element from a main image, more angles, and a voice, for later
runs." and `ElementAdd(io.ComfyNode)`.

```python
_REFERENCES = io.Custom(SOCKET_TYPES["REFERENCES"])


class ElementAdd(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id=f"{NODE_PREFIX}{cls.__name__}",
            display_name="Element: Add",
            category=MENUS["SHARED"],
            description="Make a Dreamina Element from a main image, more angles, and a voice, so later runs keep the "
            "subject the same. It bills nothing.",
            inputs=[
                io.MultiType.Input(
                    "main",
                    types=[io.Image, _REFERENCES],
                    tooltip="The Element's main image: one ComfyUI image, or one image from another Dreamina node's "
                    "references.",
                ),
                io.MultiType.Input(
                    "auxiliary",
                    types=[io.Image, _REFERENCES],
                    optional=True,
                    tooltip="More images of the same subject, such as its side and back.",
                ),
                io.MultiType.Input(
                    "voice",
                    types=[io.Audio, _REFERENCES],
                    optional=True,
                    tooltip="The Element's voice: one ComfyUI audio clip, or the references of Audio: Generate.",
                ),
                io.String.Input(
                    "title",
                    default="",
                    tooltip="The Element's name on your Dreamina canvas, such as Host.",
                ),
                io.String.Input(
                    "description",
                    default="",
                    multiline=True,
                    tooltip="A note kept with the Element on your canvas. Leave it empty to send none.",
                ),
            ],
            outputs=[_REFERENCES.Output("references", display_name="references")],
            is_input_list=True,
        )
```

- The inputs are in F's order: sockets first, then the short text, the text
  box last. Each sets the CLI flag of the same name (`--main`, `--auxiliary`,
  `--voice`, `--title`, `--description`), as the owner's rule asks.
- `io.MultiType.Input` with no widget gives a socket that takes either type,
  as F's File: Add takes several types on `file`.
- The node has no `hidden` input, since it shows no progress bar.

`execute(cls, *, main: list[object], title: list[str], description:
list[str], auxiliary: list[object] | None = None, voice: list[object] | None
= None) -> io.NodeOutput` (async, `@classmethod` and `@override`, with F's
pyright reason comment) returns
`await wait_for_run(asyncio.create_task(_add_element(...)))`, so ComfyUI's
cancel stops the work.

The private `_add_element` makes every check before anything is uploaded:

1. `title` and `description`: each list's stripped values must be one value,
   else `SINGLE_VALUE` with the input's name. An empty title raises
   `ELEMENT_TITLE_EMPTY`. A title longer than `TITLE_MAX_UNITS` UTF-16 code
   units (`len(title.encode("utf-16-le")) // 2`) raises
   `ELEMENT_TITLE_LENGTH` with `maximum=TITLE_MAX_UNITS`.
1. The connected values are split by kind. Image batches and audio values
   are ComfyUI media; tuples are references. One call to 07's
   `list_local_media((*main images, *auxiliary images), (), voice audio)`
   makes one `LocalMedia` per frame and per clip, numbered within one upload
   call as 07 requires. The first image items, as many as `main`'s frames,
   are `main`'s; the other image items are `auxiliary`'s; the audio items are
   `voice`'s.
1. `main`: its local items and references together must be exactly one item,
   else `ELEMENT_MAIN_COUNT`. A reference whose media is not `image` raises
   `ELEMENT_MAIN_MEDIA`.
1. `auxiliary`: a reference whose media is not `image` raises
   `ELEMENT_AUXILIARY_MEDIA`.
1. `voice`: more than one item raises `ELEMENT_VOICE_COUNT`. A reference
   whose media is not `audio` raises `ELEMENT_VOICE_MEDIA`.
1. The settings snapshot (`get_runtime().configuration.read_snapshot`, in a
   worker thread) gives the request timeout, `seconds`, and `deadline =
   time.monotonic() + seconds`. Steps 7 to 10 run inside
   `asyncio.timeout(seconds)`. A `TimeoutError` raises
   `DreaminaError(ErrorCode.TIMEOUT, FREE_TIMEOUT.format(node="Element: Add",
   seconds=seconds))`.
1. `validate_cli()`. The canvas comes from 08's canvas lookup, as the paid
   nodes get it: `find_canvas(get_runtime().canvas)`, or `create_canvas` when
   the saved canvas is missing or no longer listed. Its `project_id` names
   every call below.
1. One `send_media(project_id, local, encode_local_file, settings, deadline)`
   call uploads every local item and returns one resource `Reference` per
   item, in item order. References are kept as they are.
1. `auxiliary` is ordered with node references first, then resource
   references, each in socket order.
1. `create_element(project_id, ElementRequest(...), deadline)`.
1. Return `io.NodeOutput((element,))`.

`__all__`: `ElementAdd`.

## Step 4: What fills the output

`references` holds one `Reference`: origin `node`, the Element's node ID,
media `element`, and the title. It is not an output list: one Element is one
value, so a paid node that takes it runs once.

Where it goes next, as [01-decisions.md](01-decisions.md#media-references-and-placeholders)
says:

- **Video: Generate.** Any Element connected makes the mode `m2v`. The
  Element is sent as `--ref node:<id>`, first among the references.
  `{{reference1}}` in the prompt names it.
- **Image: Generate.** The mode is `i2i`.
- **Audio: Generate.** The mode is `tts` with `omni-dubbing`, within the
  model's reference limits.
- **Image: Upscale** refuses it with `UPSCALE_REFERENCE_MEDIA`
  ([12-node-upscale.md](12-node-upscale.md)).

## Step 5: Register

1. In `src/nodes/__init__.py`, import `ElementAdd` and add it to
   `NODE_TYPES` right after `AudioGenerate`
   ([04-architecture.md](04-architecture.md#srcnodes)). After this milestone
   `NODE_TYPES` is the full order: `ImageGenerate`, `ImageUpscale`,
   `VideoGenerate`, `AudioGenerate`, `ElementAdd`, `GenerationDownload`,
   `ModelInfo`.
1. `DreaminaElementAdd` matches none of
   [04-architecture.md](04-architecture.md#ids-other-packs-use).
1. `quality/config/repository/functions.json` needs no entry: `ElementAdd`
   is named by `NODE_TYPES`, and `create_element` by the node.

## Step 6: Help page

Create `web/docs/DreaminaElementAdd.md`. Its reference is F's
`FalFileAdd.md` (35 lines).

```markdown
# Element: Add

Makes a Dreamina Element: one character, product, or place that later runs
keep the same. Give it the clearest image of the subject, more angles, a
voice, and a name. It bills nothing.

## Inputs

| Input         | What it takes                                                               |
| ------------- | --------------------------------------------------------------------------- |
| `main`        | One image of the subject, or one image from a Dreamina node's `references`. |
| `auxiliary`   | More images of the same subject, such as its side and back.                 |
| `voice`       | One voice clip, or the `references` of **Audio: Generate**.                 |
| `title`       | The Element's name on your Dreamina canvas.                                 |
| `description` | A note kept with the Element.                                               |

## Outputs

| Output       | What it carries                          |
| ------------ | ---------------------------------------- |
| `references` | The Element, for the next Dreamina node. |

## Use

1. Connect the subject's clearest image to `main`, and type a `title`.
2. Connect `references` to **Video: Generate** or **Image: Generate**.
3. Write `{{reference1}}` in that node's prompt where the subject appears.

ComfyUI images and audio are uploaded to your canvas first. The same inputs
give back the same Element, and new inputs make a new one. Example:
**video-03-keep-a-host-across-shots**.

[Dreamina Canvas CLI](https://dreamina.capcut.com/canvas-cli)
```

## Step 7: README row and examples

The README node table row ([18-documentation.md](18-documentation.md)), after
Audio: Generate's:

| Node | What it does | Paid |
| ---- | ------------ | ---- |
| [Element: Add](web/docs/DreaminaElementAdd.md) | Makes an Element that keeps a character, product, or place the same across runs. | No |

The example is [17-scripts-and-workflows.md](17-scripts-and-workflows.md)'s
`video-03-keep-a-host-across-shots`, built in this milestone, which owns its
slug, layout, notes, prompts, and save names. What this plan asks of it:

| Slug | What it shows | Nodes and settings this plan asks for |
| ---- | ------------- | ------------------------------------- |
| `video-03-keep-a-host-across-shots` | One host kept the same in two separate shots | **Cast**: **Image: Generate** draws the host. **Keep**: **Element: Add** with `main` ← Cast's `references` and `title` `Host`; `auxiliary`, `voice`, and `description` left empty. **Shot 1** and **Shot 2**: two **Video: Generate** nodes, each with `references` ← Keep's `references`. **Save Video** `video/dreamina/host-shot-1` and `video/dreamina/host-shot-2`. |

- **`title` must be set.** 17 keeps Element: Add's other inputs at their
  defaults, but `title` starts empty and an empty title is refused
  (`ELEMENT_TITLE_EMPTY`). So the example sets `title` to `Host`.
- 17's Keep note says what an Element is in everyday words, that making one
  is free, and that an Element can also hold more angles and a voice. Each
  shot's note ends with 17's `RECOVER_NOTE`.

## Step 8: Live checks

[21-test-runs.md](21-test-runs.md) lists contract run C-15 in Part 1
(milestone 4, outside ComfyUI) and run E-1 in Part 2, after this
milestone's commit, with the owner's approval of its credits. The free
checks below go with it. I-1 and A-1 are 09's and 11's first runs; their
outputs come from ComfyUI's cache, for free.

| Run | What | Settles | Credits | If it differs |
| --- | ---- | ------- | ------- | ------------- |
| C-15 | Upload a PNG; `node create element --main <uuid> --title Test`; `node show` it; then a `node create video --mode m2v --ref node:<element> --credit-ceiling 0 --run` quote; then a save to a canvas ID that does not exist | The Element reply (`node.nodeId`, `subjectBindings`); that an upload binds by bare UUID; that `m2v` takes the Element and how its limits count it; the gone-canvas error | 0 | Step 2's call; 07's `MEDIA_TYPES`; 08's gone-canvas map |
| Free | `title` empty; then a two-frame batch into `main`; then A-1's `references` into `main` | `ELEMENT_TITLE_EMPTY`, `ELEMENT_MAIN_COUNT`, and `ELEMENT_MAIN_MEDIA`, before any upload | 0 | Step 3's checks |
| Free | `main` ← I-1's `references`, `auxiliary` ← **Load Image**, `voice` ← A-1's `references`, `title` `Apple`, `description` `A red apple` | One Element node on the canvas with the node binding, one uploaded auxiliary, and the voice (`node show`'s `subjectBindings`); `references` holds origin `node` and media `element` | 0 | Step 2's arguments |
| Free | **Image: Upscale** with `references` ← the Element | `UPSCALE_REFERENCE_MEDIA` before anything is sent | 0 | 12's reference check |
| E-1 | **Element: Add** with `main` ← **Load Image** `dreamina-test-apple.png` (an upload) and `title` `Apple`; then **Video: Generate** with `references` ← its `references`, 21's M2V-E model and cheapest `arguments`, `prompt` "{{reference1}} rolls across a wooden table." | The upload bound by bare UUID; `m2v` chosen for the Element; the Element sent as `--ref node:<id>` and placed in the prompt; the video saved | 21's `M2V-E` | 06's mode choice, 07's placeholder rewrite, or this plan's binding |

Record each result in [README.md](README.md#changes-made-while-building).

## Names this plan uses from other plans

| Name | Owner | Used for |
| ---- | ----- | -------- |
| `NODE_PREFIX`, `MENUS["SHARED"]`, `SOCKET_TYPES["REFERENCES"]`, `NODE_TYPES`, `DreaminaError`, `ErrorCode.TIMEOUT`, `get_runtime` (`configuration`, `canvas`), the **Request timeout (seconds)** setting | [05-foundation.md](05-foundation.md) | Names, errors, the runtime, the timeout |
| `src/config/messages/inputs.py` | [06-model-check.md](06-model-check.md) | The module the refusals join |
| `Reference` (`value`), `LocalMedia`, `src/types/references.py`, `list_local_media`, `send_media`, `encode_local_file`, `MEDIA_TYPES`, `FRAME_MODES`, `validate_references` | [07-media.md](07-media.md) | Local media, uploads, and how later runs count the Element |
| `send_command`, `build_failure`, `CLI_REPLY_INVALID`, `validate_cli`, `REQUIRED_COMMANDS`, `src/config/dreamina.py`, `find_canvas`, `create_canvas`, `ElementReply`, `NodeView`, `wait_for_run`, `src/config/messages/run.py` | [08-runs.md](08-runs.md) | The call, its failures, and the owned task |
| `SINGLE_VALUE` | [06-model-check.md](06-model-check.md) | The refusal of a list where one value is expected |
| `FREE_TIMEOUT` | [15-node-model-info.md](15-node-model-info.md) | The timeout message |
| `ImageGenerate`, run I-1 | [09-node-image.md](09-node-image.md) | `main` in the example and in a free check |
| `VideoGenerate`, its mode choice | [10-node-video.md](10-node-video.md) | The example's shots and E-1 |
| `AudioGenerate`, run A-1 | [11-node-audio.md](11-node-audio.md) | `voice` in a free check |
| `UPSCALE_REFERENCE_MEDIA` | [12-node-upscale.md](12-node-upscale.md) | A free check |
| `video-03-keep-a-host-across-shots`, `RECOVER_NOTE` | [17-scripts-and-workflows.md](17-scripts-and-workflows.md) | The example and its notes |
| Runs C-15 and E-1, the `M2V-E` quote | [21-test-runs.md](21-test-runs.md) | The live checks |
