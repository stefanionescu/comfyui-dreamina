# Scripts and Example Workflows

This plan finishes the development scripts under `scripts/` and builds the
example workflows under `example_workflows/` and their blueprints under
`subgraphs/`. The scripts are F's
(`F=/Users/dr_stone/Documents/work/comfyui-fal`, commit `cef8b6e`), copied
and re-valued by [03-repository-setup.md](03-repository-setup.md), and
changed here for the nodes Dreamina's examples place. F's plan 17
(`F/plans/17-scripts-and-workflows.md`) is the model for this plan's shape.
Example workflows are generated from Python descriptions by F's engine and
never saved by hand; [The page engine](#the-page-engine) explains how it
places, sizes, and checks them.

Readers: the engineer or agent who builds the scripts, adds an example, or
adds a node to one; and the owner, who approves each example's paid run.

The examples follow F's form: each is a small job a person would really do,
with a note above every group, a subgraph for each step after the inputs, and
each subgraph shipped as a blueprint named after its step. They use only this
pack's nodes and ComfyUI's own nodes, ship no media, and make their own
inputs with Dreamina models wherever they can. One example, image-02, edits a
photo the person uploads. Together they cover the live-shopping jobs the
owner runs today: a host portrait, a product photo edited with GPT Image 2.5
Sunburst, a poster enlarged for print, a host animated and filmed with a
product with Seedance, one host kept the same across shots with an Element,
and a host given a voice with Seed Audio.

The node plans (09 to 15) own every node's input and output IDs. Where an
example below names an input or an output that a node plan names
differently, the node plan wins and the description is corrected; the build
raises `KeyError` on an ID a node does not have, so a mismatch cannot ship.
For an example's prompts, settings, and save names this plan wins
([README.md](README.md#how-to-use-these-plans)).

What every example relies on, from
[01-decisions.md](01-decisions.md#the-inputs-of-a-paid-node):

- A generation node takes a typed `model`, a `prompt`, a `credit_ceiling`,
  and `arguments`, a JSON object of the model's own settings under the CLI's
  flag names without the leading dashes (`ratio`, `resolution`, `duration`,
  `count`, `voice-name`, `scenario`, and `mode`).
- Local media reaches a paid node through the list sockets `images`,
  `videos`, and `audio`, and is uploaded with each run.
- What another Dreamina node made reaches it through `references`, one
  socket of type `DREAMINA_REFERENCES`, with no download or upload. One
  connection reaches it, as
  [12-node-upscale.md](12-node-upscale.md#step-3-image-upscale) declares the
  socket and [23-live-shopping-provider.md](23-live-shopping-provider.md)
  passes "the tuple another Dreamina node returned".
- The placeholders `{{image1}}` and `{{reference1}}` mark where an item goes
  in the prompt ([01-decisions.md](01-decisions.md#placeholders)).

The models, flags, and values each example sets were read from the owner's
live model lists captured on 2026-10-16
([research/catalog.md](research/catalog.md),
`research/captures/model-list-*.json`). Every video model there marks
`ratio`, `resolution`, and `duration` as required with no default, and every
image model marks `ratio` and `resolution` the same way (except
`seedream_5.0_pro`'s `ratio`), so each example's `arguments` sets them.
Credits come from Part 0's price sweep in
[21-test-runs.md](21-test-runs.md#part-0-free-reads-and-the-price-sweep) and
appear only in these plans.

## Contents

- [Step 1: Scripts the hooks need](#step-1-scripts-the-hooks-need)
- [The page engine](#the-page-engine)
- [Step 2: Workflow texts](#step-2-workflow-texts)
- [Step 3: Workflow descriptions](#step-3-workflow-descriptions)
- [Example workflows](#example-workflows)
- [Step 4: Build the examples](#step-4-build-the-examples)
- [Step 5: Run each example once](#step-5-run-each-example-once)

## Step 1: Scripts the hooks need

Built in the Tooling milestone, after 03's
[Step 7](03-repository-setup.md#step-7-re-value-the-scripts). The hooks run
`comfy:frontend:check` (pre-commit), and `comfy:nodes:check` and
`comfy:workflows:check` (pre-push, through `repo:check`). With no nodes
registered and `FAMILIES` empty, each passes: there is nothing to check.

Every file of `F/scripts/` is ported. This table lists each, with the edit it
gets and the plan that makes it:

| F file                                                        | Dreamina change                                                                                       | Made by |
| ------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- | ------- |
| `scripts/__init__.py`, `paths.py`, `types.py`, `dependencies.py` | None: no docstring or value names fal                                                              | 03      |
| `scripts/frontend.py`                                         | None: it bundles `web/scripts/extension.ts` and keeps ComfyUI's `app.js` and `api.js` external          | 03      |
| `scripts/nodes/check.py`                                      | Line 86: `f"Put {node_id} in a Dreamina menu."`                                                       | 03      |
| `scripts/nodes/host.py`                                       | The members Dreamina's examples place ([below](#scriptsnodeshostpy))                                  | This step |
| `scripts/nodes/schema.py`                                     | 03: the temporary prefix `comfyui-dreamina-schema-`, B's one-line widget test, and the `main` docstring naming Generation: Download. This step: Load Image's upload flag ([below](#scriptsnodesschemapy)) | 03, this step |
| `scripts/workflows/build.py`                                  | 03: no family import and an empty `FAMILIES` in F's `cast` form. Each node milestone: its family ([Step 3](#step-3-workflow-descriptions)) | 03, Step 3 |
| `scripts/workflows/page/config.py`                            | `TEXT_PREVIEW` removed and `DOM_SIZES` replaced ([below](#scriptsworkflowspageconfigpy))              | This step |
| `scripts/workflows/page/graph.py`                             | Line 15: `NAMESPACE = uuid.UUID("05f62da6-1302-4067-b6d8-e83cf4a52f83")`                              | 03      |
| `scripts/workflows/page/layout.py`, `palette.py`, `serialize.py`, `sizes.py` | None                                                                                     | 03      |
| `scripts/workflows/page/widgets.py`                           | B's widget type read and O's upload button value ([below](#scriptsworkflowspagewidgetspy))            | This step |
| `scripts/workflows/descriptions/__init__.py`                  | None                                                                                                  | 03      |
| `scripts/workflows/descriptions/texts.py`                     | 03: the three titles the engine reads. Each node milestone: its titles ([Step 2](#scriptsworkflowsdescriptionstextspy)) | 03, Step 2 |
| `scripts/workflows/descriptions/notes.py`                     | 03: the docstring only. Each node milestone: its texts ([Step 2](#scriptsworkflowsdescriptionsnotespy)) | 03, Step 2 |
| `scripts/workflows/descriptions/{nodes,image,audio,video,elements}.py` | New, one per milestone ([Step 3](#step-3-workflow-descriptions))                              | Step 3  |

The namespace is new, never F's `72ee9f58-7bbd-418b-af1f-7f48a5f198bf`:
ComfyUI identifies workflows and subgraphs by ID, and a Dreamina step whose
slug and name matched an F one would otherwise get F's ID.

`build.py` after the Tooling milestone, as 03 leaves it:

```python
# Each family's workflows, with the node menu their subgraph blueprints are listed in.
# The cast keeps the empty tuple from narrowing to no type until the first family is added.
FAMILIES = cast("tuple[tuple[tuple[Workflow, ...], str], ...]", ())
WORKFLOWS = tuple(workflow for workflows, _menu in FAMILIES for workflow in workflows)
```

The Image milestone adds the first family. `FAMILIES` then becomes a plain
tuple, the second comment and the `cast` go, and the `MENUS` import returns
([Step 3](#step-3-workflow-descriptions)).

### `scripts/nodes/host.py`

Replace F's 14 members with the ComfyUI nodes the Dreamina examples place:

```python
"""The ComfyUI nodes the example workflows place beside this extension's own."""

from enum import StrEnum


class HostNode(StrEnum):
    """One ComfyUI node, by the name ComfyUI registers it under."""

    IMAGE = "LoadImage"
    PREVIEW = "PreviewAny"
    TEXT_BLOCK = "PrimitiveStringMultiline"
    SAVE_IMAGE = "SaveImage"
    PREVIEW_IMAGE = "PreviewImage"
    SAVE_AUDIO = "SaveAudioAdvanced"
    SAVE_VIDEO = "SaveVideo"


__all__ = ["HostNode"]
```

| Member          | Display name in 0.37.2 | Used by                                                                 |
| --------------- | ---------------------- | ----------------------------------------------------------------------- |
| `IMAGE`         | Load Image             | image-02                                                                |
| `PREVIEW`       | Preview as Text        | audio-01                                                                |
| `TEXT_BLOCK`    | Text (Multiline)       | Every example's inputs                                                  |
| `SAVE_IMAGE`    | Save Image             | image-01, image-02, image-03                                            |
| `PREVIEW_IMAGE` | Preview Image          | Every step that draws an input it does not save: audio-02, video-01, video-02, video-03 |
| `SAVE_AUDIO`    | Save Audio (Advanced)  | audio-01, audio-02                                                      |
| `SAVE_VIDEO`    | Save Video             | video-01, video-02, video-03, video-04                                  |

Every ID is in ComfyUI 0.37.2: F found `SaveAudioAdvanced`
(`comfy_extras/nodes_audio.py:255`), `SaveVideo` (`nodes_video.py:139`), and
`PrimitiveStringMultiline` (`nodes_primitive.py:28`) in its own node
definitions, B checked `PreviewAny`, `SaveImage`, and `PreviewImage` against
`nodes.NODE_CLASS_MAPPINGS`, and O places `LoadImage`
(`O/scripts/nodes/host.py`). `SaveAudio`, `SaveAudioMP3`, and `SaveAudioOpus`
are deprecated in 0.37.2 (`nodes_audio.py:173`, `:203`, `:234`), so the audio
examples save with **Save Audio (Advanced)**, which writes FLAC by default.

Not members, because no example places them: **Load Audio** and **Load
Video**, F's `StringFormat` (each prompt box holds the whole prompt),
`GetItemFromList` (the save nodes take a node's whole output list), and F's
text, mesh, and mixing nodes.

### `scripts/nodes/schema.py`

03 has already made this file's three edits. This step adds one line to
`_build_host_schema`, so the page knows that **Load Image** draws an upload
button after its dropdown. The host input dictionary gains the flag, as O's
`scripts/nodes/schema.py:68` writes it:

```python
                    "default": settings.get("default"),
                    "image_upload": bool(settings.get("image_upload")),
                    # A host list can name the files of this machine, so none is kept.
                    "options": [],
```

Nothing else changes. The paid-node parameter check stays: a paid node's
`send` parameters plus `INPUT_NAMES["RUN_NUMBER"]` must equal its input IDs.
It covers the three generation nodes and Image: Upscale, which subclass
`PaidNode` ([08-runs.md](08-runs.md), [12-node-upscale.md](12-node-upscale.md)).
Element: Add, Generation: Download, and Model: Info are checked by their
`execute` parameters. The export runs with a new empty state folder and
never starts the Dreamina CLI: `create_runtime()` builds stores only
([05-foundation.md](05-foundation.md#step-19-runtime)), so Generation:
Download's dropdown has no entries and the export is the same on every
machine.

### `scripts/workflows/page/widgets.py`

Two edits:

1. **B's widget type.** `_validate_widget_value` and `read_widget_default`
   read the widget's kind from `item["type"]`, as
   `B/scripts/workflows/page/widgets.py:13` and `:61` do, instead of F's
   `item.get("widgetType", item["type"])`, and F's comment on
   `widgetType` goes. 03 removed the multi-typed widget test from
   `schema.py` for the reason that applies here too: no Dreamina node has a
   multi-typed widget input, so no input carries `widgetType`. Element:
   Add's `main`, `auxiliary`, and `voice` are multi-typed sockets with no
   widget ([13-node-element.md](13-node-element.md#step-3-element-add)), so
   B's test marks them sockets, as ComfyUI draws them. A later node with a
   multi-typed widget brings back F's lines in both files in the same change.
1. **O's upload button.** In `encode_widget_values`, after the
   `control_after_generate` branch, add O's lines
   (`O/scripts/workflows/page/widgets.py:96-98`):

   ```python
           if item.get("image_upload"):
               # The page adds an upload button after an upload dropdown.
               result.append("image")
   ```

   ComfyUI saves **Load Image** as `["<file>", "image"]`, the file name and
   then the upload button's value, and O's shipped examples hold
   `['', 'image']`. Without the second value, frontend 1.52.7 loads the node
   but the build's file differs from the one ComfyUI saves.

### `scripts/workflows/page/config.py`

1. Remove `TEXT_PREVIEW` and its `__all__` entry: no Dreamina example saves
   text, so no subgraph exposes a text preview. The comment above the
   previews becomes:

   ```python
   # The previews a save node draws, which a placed subgraph can show: an image, an audio and a video player.
   ```

1. Replace `DOM_SIZES` with the panel nodes of the new `HostNode`:

   ```python
   DOM_SIZES: dict[str, tuple[int, int]] = {
       HostNode.IMAGE: (340, 314),
       HostNode.PREVIEW: (340, 122),
       HostNode.SAVE_IMAGE: (340, 58),
       HostNode.PREVIEW_IMAGE: (340, 26),
       HostNode.SAVE_AUDIO: (340, 136),
       HostNode.SAVE_VIDEO: (340, 106),
   }
   ```

   | Member          | Value     | Source                                                                                                        |
   | --------------- | --------- | ------------------------------------------------------------------------------------------------------------- |
   | `IMAGE`         | 340 × 314 | Measured on frontend 1.52.7, 2026-10-17: the height a new Load Image takes, which holds a photo and its size line; O's 350 left 36 px empty |
   | `PREVIEW`       | 340 × 122 | F's, measured by B on frontend 1.52.7; confirmed 2026-10-17                                                   |
   | `SAVE_IMAGE`    | 340 × 58  | F's, measured by B on frontend 1.52.7; confirmed 2026-10-17                                                   |
   | `PREVIEW_IMAGE` | 340 × 26  | F's, measured by B on frontend 1.52.7; confirmed 2026-10-17                                                   |
   | `SAVE_AUDIO`    | 340 × 136 | F's, taken from Load Audio's size; measured on Save Audio (Advanced) on frontend 1.52.7, 2026-10-17          |
   | `SAVE_VIDEO`    | 340 × 106 | F's, measured by B on frontend 1.52.7; confirmed 2026-10-17                                                   |

   The save nodes are sized for their empty state; ComfyUI grows them as
   their viewers fill. `IMAGE` and `SAVE_AUDIO` were measured as below.

There is no `AUDIO_PREVIEW` or `VIDEO_PREVIEW`: frontend 1.52.7 shows no
audio player on a placed subgraph, and a broken image in place of a video
(Results, 2026-10-17). Only `IMAGE_PREVIEW` is exposed, and each note says
where its files are saved.

### Re-measure the page on frontend 1.52.7

B measured ComfyUI 0.37.2's frontend 1.52.7 on 2026-10-11 and F kept those
measurements, so the plain node constants hold. These things are new and are
measured once:

- a generation node with its `credit_ceiling` widget and its two text boxes,
  `prompt` and `arguments` (image-01, video-02);
- Image: Upscale, with `arguments` and no `prompt` (image-03);
- **Load Image** with its upload button (image-02);
- Element: Add, Generation: Download, and Model: Info, placed on the canvas
  (video-03, video-04, audio-01);
- **Save Audio (Advanced)** and its player (audio-01);
- the audio player on a placed subgraph (audio-01, audio-02);
- video-04's step that ships turned off.

The measuring is done in the Documentation and brand milestone, in the same
session as the screenshots of
[19-brand-assets.md](19-brand-assets.md#step-4-screenshots), because the
owner's rule is not to use ComfyUI during the build unless the owner says.
Every node exists by then. The procedure is F's:

1. Start ComfyUI from the installation in `.mise.local.toml`, open it in
   Chrome with **Modern Node Design (Nodes 2.0)** off, browser zoom and canvas
   zoom at 100%.
1. **Plain nodes.** Open each generated example in a new tab from **Browse
   Templates → dreamina**, then run in DevTools:

   ```js
   app.rootGraph.nodes.map((node) => [node.type, node.size[1], node.computeSize()[1]])
   ```

   Open each subgraph and run the same line. Every node without a panel must
   keep its saved height: Image: Generate, Video: Generate, and Audio:
   Generate with their multiline `prompt` and `arguments`, Image: Upscale,
   Element: Add, Generation: Download, and Model: Info. If a socket row is
   counted wrong, correct `scripts/nodes/schema.py`'s export, not the
   constants.
1. **Panel nodes.** Add **Load Image** and **Save Audio (Advanced)** to an
   empty canvas, select each, and read its size:

   ```js
   Object.values(app.canvas.selected_nodes).map((node) => [node.type, node.size])
   ```

   Write each pair into `DOM_SIZES`.
1. **Notes.** No note's `scrollHeight` may exceed its `clientHeight`, and
   when every note has more than 24 pixels to spare, lower
   `NOTE_LINE_HEIGHT` or `NOTE_CHARACTER_WIDTH` by 1 until one has less.
1. **A step that ships turned off.** Open video-04 and run
   `await app.graphToPrompt()` in DevTools. Its `output` must hold
   `DreaminaGenerationDownload` and one `SaveVideo`, and no
   `DreaminaVideoGenerate`, which shows that a bypassed subgraph also
   bypasses the nodes inside it. If a paid node is there, remove the
   **Shot** group from video-04, so it ships as F's single recover group,
   and record the change. [21-test-runs.md](21-test-runs.md) makes its
   videos to recover in run V-4 and in video-01, so its runs stay as they
   are.
1. **Subgraph previews.** After the first run of audio-01
   ([Step 5](#step-5-run-each-example-once)), close and reopen it, and check
   that **Voice** shows its audio player. If it shows none on 1.52.7, remove
   `AUDIO_PREVIEW` and every audio entry in `previews`; the notes already say
   where each file is saved. This check waits for the run, so its fix is a
   commit of the example runs.
1. Edit the constants or rules, run `mise run comfy:workflows:build`, reopen
   the example in a new tab, and repeat until every plain node keeps its
   saved size and no note scrolls.

Record the old and new values in
[Changes made while building](README.md#changes-made-while-building). The
measuring needs ComfyUI started with the finished nodes, so it is done after
the milestone's commit, and the changed constants and rebuilt files go in a
commit of their own.

#### Results, 2026-10-17

Measured headless on ComfyUI 0.37.2 with frontend 1.52.7, Nodes 2.0 off,
canvas zoom 1, with nothing queued.

| What | Saved | Computed on load |
| ---- | ----- | ---------------- |
| Image: Generate (image-01, image-03, audio-02, video-01, video-02, video-03) | 254 | 254 |
| Video: Generate (video-01 to video-04) | 274 | 274 |
| Audio: Generate (audio-01, audio-02) | 254 | 254 |
| Image: Upscale (image-03) | 176 | 176 |
| Element: Add (video-03) | 152 | 152 |
| Generation: Download (video-04) | 138 | 138 |
| Model: Info (audio-01) | 58 | 58 |
| A placed subgraph: one output, two outputs, none | 88, 108, 26 | 88, 108, 26 |
| Load Image, added new; with no photo; with a photo | 314; 102; 326 | panel |
| Save Audio (Advanced), added new | 136 | 136 |

- Every plain node keeps its saved height, inside subgraphs too, so
  `scripts/nodes/schema.py` and the row constants stand.
- `IMAGE` became 340 × 314, the size a new Load Image takes; at that
  height a photo and its size line fit, and image-02 was rebuilt.
- No note's text scrolls: the rendered `.ProseMirror` box is never taller
  than its frame. The note's raw-text editor sits under it at opacity 0 and
  does scroll, which shows only while editing. The tightest notes have
  4 px to spare, so the note constants stand.
- video-04's `graphToPrompt()` output holds `DreaminaGenerationDownload`
  and `SaveVideo` only: the bypassed **Shot** bypasses its inner nodes, and
  the group stays.
- **Subgraph previews.** Each kind was checked by replaying a real run's
  output into the opened template (ComfyUI's `executed` event for the inner
  node), with the same event sent to the same node placed on the page as a
  control, with Nodes 2.0 off and on. Every control showed its result.

  | Placed subgraph (inner node)                                        | Nodes 2.0 off                                    | Nodes 2.0 on                                 |
  | ------------------------------------------------------------------- | ------------------------------------------------ | -------------------------------------------- |
  | Voice (`7:102` Save Audio (Advanced)), audio-01                     | Nothing, also after switching workflows and back | Nothing                                      |
  | Design (`4:102` Save Image), image-01                               | Nothing, also at 340 × 420                       | The image                                    |
  | Portrait (`6:102` Preview Image), video-01                          | Nothing                                          | The image                                    |
  | Animate (`7:202` Save Video), video-01; Shot 1 (`11:202`), video-03 | Nothing                                          | "Image failed to load" in place of the video |

  `AUDIO_PREVIEW`, `VIDEO_PREVIEW`, and their `previews` entries are
  removed, and audio-01, audio-02, video-01 to video-04, and the **Voice**,
  **Speak**, **Animate**, **Film**, **Shot**, **Shot 1**, and **Shot 2**
  blueprints are rebuilt. `IMAGE_PREVIEW` stays: it shows with Nodes 2.0 on
  and draws nothing with it off.

## The page engine

F's engine, unchanged, builds every workflow from a `Workflow` record and
writes the JSON ComfyUI saves. This section is what an implementer needs to
add an example or a node to one; the code is in `scripts/workflows/`.

### What a description holds

- **`Node(key, kind, values, title, is_paid, is_bypassed)`.** `key` is unique
  within its workflow or subgraph. `kind` is a node ID, a `HostNode` member,
  or a subgraph's name. `values` holds only the widget values that differ
  from the node's defaults. `title` comes from `SHARED_TEXTS`.
- **`Group(title, columns, colour, note)`.** A titled frame. `columns` is a
  tuple of columns, left to right; each column is a tuple of node keys, top
  to bottom. `colour` is `INPUT_COLOUR` (`#55746b`, the default) or
  `STAGE_COLOUR` (`#68688c`). `note` is the text of the note above it.
- **`Subgraph(name, nodes, links, columns, inputs, outputs, description,
  previews)`.** A step placed as one node. `inputs` and `outputs` pair a
  name the placed node shows with the inner `key.socket` it reaches.
  `previews` pairs an inner key with the preview its placed node shows.
- **`Workflow(slug, nodes, links, stacks, subgraphs)`.** `stacks` is a tuple
  of stacks, left to right; each stack is a tuple of groups, top to bottom.
- **Links** are `("key.output", "key.input")`. A link string splits at its
  first dot, so `"draw.images"` is output `images` of node `draw`.

### Measuring

`scripts/workflows/page/sizes.py` sizes each node as frontend 1.52.7 computes
it, so a loaded workflow keeps its layout:

1. A kind in `DOM_SIZES` takes that size. These nodes draw their own panel.
1. Otherwise `measure` counts rows. Each socket input is one row of
   `SLOT_HEIGHT` (20), and a growing row of sockets shows its linked slots,
   one more, and a free row below. The node is as tall as its socket rows or
   its outputs, whichever is more, times 20, plus `NODE_PADDING` (6).
1. Each widget adds `WIDGET_HEIGHT` (20), or `MULTILINE_HEIGHT` (50) for a
   multiline text box, plus `WIDGET_GAP` (4) after it, and the widgets
   together add `WIDGETS_PADDING` (8). A seed's control widget adds a row,
   and a dropdown whose options add widgets counts the chosen option's.
1. Every node is `NODE_WIDTH` (340) wide.

F's **Image: Generate** checks the arithmetic: two socket inputs and four
outputs make four rows (86), and `model`, `run_number`, `prompt`, and
`arguments` add 24 + 24 + 54 + 54 + 8 (164), so it is 340 × 250, the size in
`F/example_workflows/video-01-animate-a-host.json`. A placed subgraph is
measured the same way from the inputs and outputs it exposes; an input linked
to a widget inside it shows as that widget.

`measure_note(text, width)` sizes a note: `NOTE_PADDING` (26), plus
`NOTE_LINE_HEIGHT` (12) for each wrapped line, plus `NOTE_PARAGRAPH_GAP` (10)
for each blank line, and at least `NOTE_MIN_HEIGHT` (88). A line wraps at the
note's width less `NOTE_SIDE_PADDING` (20), and less `NOTE_LIST_INDENT` (40)
for a numbered step. Plain characters count `NOTE_CHARACTER_WIDTH` (5) each
and code characters `NOTE_CODE_CHARACTER_WIDTH` (7); bold and code marks
count nothing.

### Aligning

`scripts/workflows/page/layout.py` places every node; no position is written
by hand:

- **Columns.** `place_columns` puts columns side by side. A column is as wide
  as its widest node, and the next column starts `NODE_GAP` (40) to its
  right. Nodes in a column are stacked with `STACK_GAP` (64) between them,
  room for the lower node's title bar and source badge.
- **Groups.** A group's note sits at its stack's left edge, `TITLE_HEIGHT`
  (30) below the stack's top. The frame starts `GUTTER` (30) below the note.
  Nodes start `GUTTER` in from the frame's left edge and `GROUP_TOP` (110)
  below its top, under the group's title. The frame ends `GUTTER` past the
  right and bottom of its nodes.
- **Stacks.** `place_stacks` starts at `CANVAS_ORIGIN` (0, 30). Groups in a
  stack are `GUTTER` apart, and the next stack starts `GUTTER` to the right
  of the stack's widest frame.
- **Notes above groups.** `_build_notes` in `build.py` makes one
  `MarkdownNote` per group, titled **Start Here** for the first group and
  **Note** for every other. Each note is as wide as its group's frame (its
  columns plus a `GUTTER` on each side), and every note in a workflow is as
  tall as the tallest, so all frames start on one line. The note sits
  outside its frame, so moving or bypassing the group leaves it in place. The
  build refuses a group with no note or a title another group has.
- **Every node in exactly one group.** The build refuses a workflow whose
  placed nodes and notes differ from its nodes and notes ("Place every node
  of {slug} in exactly one group."): a node in two columns or in none stops
  the build.
- **Inside a subgraph.** Its columns start at `INNER_ORIGIN` (200, 140). Its
  input ports sit `PORT_GAP` (90) to the left and its output ports `PORT_GAP`
  past its last column, 20 pixels apart.
- **Colors and modes.** A node with `is_paid=True` gets `PAID_COLOURS`
  (`{"color": "#432", "bgcolor": "#653"}`). A node with `is_bypassed=True`
  ships in `BYPASS_MODE` (4), switched off. A widget with
  `control_after_generate` ships `fixed`, so opening an example never sends
  a run by itself. The canvas opens at 50% zoom.

### Blueprints and IDs

`_encode_blueprints` writes each subgraph to `subgraphs/<name>.json`, a
one-node workflow that places it, with the family's menu as its `category`
and its description. ComfyUI lists each under **Subgraph Blueprints** in its
node library, named after the file. Two workflows may place the same
subgraph only when it is the same record; two different subgraphs with one
name stop the build ("Give the subgraph {name} in {slug} a name no other
subgraph has."). When one record is placed by two families, the last family
in `FAMILIES` names its menu.

IDs come from `NAMESPACE`: a workflow is `uuid5(NAMESPACE, slug)`, a subgraph
inside it `uuid5(NAMESPACE, "<slug>/<name>")`, a blueprint
`uuid5(NAMESPACE, "blueprint.<name>")`, and a port
`uuid5(NAMESPACE, "<subgraph id>.<side>.<name>")`. A subgraph's inner nodes
are numbered from its position times `SUBGRAPH_ID_STEP` (100), plus 1, and
each placed subgraph's `previewExposures` point at those numbers.

### `--check`

`mise run comfy:workflows:build` writes every file. `mise run
comfy:workflows:check` runs the same build with `--check` and writes nothing.
It reports:

- a file in `example_workflows/` or `subgraphs/` no description makes
  ("Remove or describe …");
- a missing or stale file ("Build …" or "Rebuild … with mise run
  comfy:workflows:build.");
- a workflow the README does not link ("Link
  example_workflows/{slug}.json from README.md.");
- a registered node no workflow or subgraph places ("Add a workflow for
  {node_id}.").

Both read the node definitions through ComfyUI's Python, so every value is
checked against the real inputs, and a widget value an input refuses stops
the build ("{node}.{input} does not accept …").

### Adding a node to a workflow

1. **A ComfyUI node not in `HostNode`.** Find its registered ID in ComfyUI
   0.37.2's own definitions and add a member. If it draws its own panel, add
   a `DOM_SIZES` entry and measure it as
   [above](#re-measure-the-page-on-frontend-1527).
1. **The node.** Add `Node(key, kind, values)` to the workflow's or the
   subgraph's `nodes`, with only the values that differ from its defaults.
   A paid node gets `is_paid=True`. A step that would bill a second time
   gets `is_bypassed=True`, and its note says how to turn it on.
1. **Its place.** Put its key in exactly one column of one group, or in the
   subgraph's `columns`. A node the person edits or reads beside a step goes
   in that step's group.
1. **Its links.** Add each link as `("key.output", "key.input")`. A subgraph
   input or output it feeds goes in the subgraph's `inputs` or `outputs`.
1. **Its result.** If it saves or shows a result inside a subgraph, add it
   to `previews`: `IMAGE_PREVIEW` for **Save Image** and **Preview Image**.
   **Save Audio (Advanced)** and **Save Video** take none: frontend 1.52.7
   shows no audio player on a placed subgraph, and a broken image in place
   of a video.
1. **Its texts.** A title or a new group takes a `SHARED_TEXTS` key; a new
   group takes a note, and a new subgraph a description, in `notes.py`.
1. Run `mise run comfy:workflows:build`, and read the build's message if it
   stops.

## Step 2: Workflow texts

Built in the first node milestone that builds an example (Image), then
extended by each milestone that adds one.

### How notes are written

The owner asked for notes that read like everyday speech, with technical
terms only where a person needs them. These rules apply to every note, every
subgraph description, and every title. They come from `rules/WRITING.md`
(ISO 24495-1), `rules/DOCUMENTATION.md`, and the rules the owner set while
building B, O, and F
([research/owner-rules.md](research/owner-rules.md#example-workflows-and-notes)).

**Who reads a note.** A person who uses ComfyUI and has opened this example
to get a job done. They have never used Dreamina's CLI, and they should not
need to.

1. **Say what happens before how.** Start with what the step makes or does,
   in words a shop owner would use: "draws the host", "reads the script
   aloud", "films the host holding the product". The mechanism comes second,
   and only if the person needs it to act.
1. **Short sentences, one idea each.** Aim for 20 words or fewer. Split a
   long sentence instead of using a semicolon or a dash.
1. **Explain a technical term once, the first time the note needs it, then
   use it the same way.** These are the only technical terms the notes use,
   each with the plain words that introduce it:

   | Term             | Introduced as                                                                                        |
   | ---------------- | ---------------------------------------------------------------------------------------------------- |
   | `model`          | "`model`, the model's name on Dreamina"                                                              |
   | `arguments`      | "`arguments` holds the model's own settings, written by the names Dreamina gives them"               |
   | `references`     | "`references`, what an earlier Dreamina step made, passes it on with no download or upload"          |
   | placeholder      | "`{{image1}}` in the prompt marks where your photo goes"                                             |
   | mode             | "the node uses `first_last_frame`, the mode that starts the video on that picture"                   |
   | `credit_ceiling` | "`credit_ceiling` is the most credits one run may cost"                                              |
   | canvas           | "your Dreamina canvas, the project named ComfyUI that holds every run"                               |
   | upload           | "the pack uploads your photo to your Dreamina canvas, so the model can read it"                      |
   | Element          | "an Element, a character Dreamina keeps so it looks the same in every video"                         |
   | text reading     | "text reading, Seed Audio's way to read a script in a chosen voice"                                  |
   | omni dubbing     | "omni dubbing, Seed Audio's way to voice a picture"                                                  |

   Any other technical word is replaced by the everyday one: "file" for
   resource, "picture" for image input, "make" for generate, "setting" for
   flag, "run" for generation in running text.
1. **Write what the person sees exactly.** Input and output names are in code
   style and spelled as the node shows them: `model`, `arguments`,
   `references`. A model's own settings are in code style under the names
   written in `arguments`: `ratio`, `resolution`, `duration`, `voice-name`.
   Values are in code style as Dreamina writes them: `720p`, `2K`, `9:16`.
   Node titles, group titles, menu paths, and buttons are bold: **Video:
   Generate**, **Film**, **Run**.
1. **Name a model plainly, once.** Use its everyday name ("Seedream 5.0
   Lite", "Seedance 2.5", "GPT Image 2.5 Sunburst", "Seed Audio") and give
   the model name only where the person has to type or choose it.
1. **Say what to change, not everything that could change.** One or two
   inputs a person is likely to want, with the useful range.
1. **Say "billed" and "credits" only where the person needs them**, such as
   a cancel, a run that may cost more than its ceiling, or a step that makes
   a second paid run. Never a price, a cost, or a number of credits.
1. **No promises and no history.** No "best", "always", "new", or "now".
   State what the step does today.
1. **Mechanics.** Present tense, second person ("you"), US English, serial
   comma, numbers zero to nine in words and 10 and up in figures (but `4K`,
   `9:16`, and other values exactly), no em dashes, no exclamation marks in
   notes.

Examples:

| Instead of                                                                                     | Write                                                                                         | Why                                  |
| ---------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- | ------------------------------------ |
| "Runs `node create video --run` with `--ref node:<id>` and `--mode m2v`."                      | "Seedance 2.5 films the host holding the product."                                            | What happens, in everyday words      |
| "The tensor is PNG-encoded and registered as a `res:` resource."                               | "The pack uploads your photo to your Dreamina canvas first, so the model can read it."        | Explains the term once, plainly      |
| "Set Resolution to 720P."                                                                      | "Set `resolution` to `720p`."                                                                 | The exact name and value on the node |
| "Seedance 2.5 is the best video model."                                                        | "Seedance 2.5 makes `480p` videos, and takes up to 30 pictures as references."                | No promotional words                 |
| "Note: this run costs about 20 credits."                                                       | (nothing)                                                                                     | No prices                            |
| "Pick a model ID."                                                                             | "Type another `model`, the model's name on Dreamina."                                         | A term the first time it is needed   |
| "Add `--duration` to the flags."                                                               | "Raise `duration` in `arguments` for a longer video."                                         | The person's words, the exact name   |
| "The submit ID is idempotent, so the run is never replayed."                                   | (nothing)                                                                                     | The person cannot act on it          |

**Start Here.** The first group's note, titled **Start Here** by the engine,
is steps only. Step 1 is exactly `SIGN_IN_STEP`:

```text
1. Sign in to Dreamina in **ComfyUI menu → Extensions → Dreamina → Dreamina Settings**.
```

The next steps say what to type, choose, or upload, naming each node or
group in bold; the last step is "Press **Run**." followed by where the
results are saved. Nothing comes after the list. A recover workflow's note
is F's exception: it starts with when to use it and ends with what happens
to the list.

**Other notes.** Every other group's note says what the step does, which
model does it, and what the person can change, in two short paragraphs at
most. A step that runs a video ends with `RECOVER_NOTE`, as its own
paragraph. Image: Upscale's step ends with `UPSCALE_RECOVER_NOTE`, as
[12-node-upscale.md](12-node-upscale.md#step-7-readme-row-and-examples) asks.

**Subgraph descriptions.** One sentence that starts with a verb, such as
"Draws the host and saves the image."

### `scripts/workflows/descriptions/texts.py`

Replace 03's three-title stub with every title the examples use. A group, a
subgraph, and a node title all come from here; a group's note key in
`notes.py` is the same key as its title.

```python
"""The titles of the shipped workflows' groups, subgraphs, notes and nodes."""

SHARED_TEXTS = {
    "start": "Start Here",
    "note": "Note",
    "input": "Input",
    "host": "Host",
    "design": "Design",
    "photo": "Photo",
    "change": "Change",
    "edit": "Edit",
    "brief": "Brief",
    "poster": "Poster",
    "enlarge": "Enlarge",
    "script": "Script",
    "voices": "Voices",
    "info": "Info",
    "voice": "Voice",
    "line": "Line",
    "cast": "Cast",
    "speak": "Speak",
    "scene": "Scene",
    "portrait": "Portrait",
    "animate": "Animate",
    "product": "Product",
    "packshot": "Packshot",
    "film": "Film",
    "collect": "Collect",
    "shot": "Shot",
    "opening": "Opening",
    "closing": "Closing",
    "keep": "Keep",
    "shot_1": "Shot 1",
    "shot_2": "Shot 2",
}

__all__ = ["SHARED_TEXTS"]
```

A milestone adds only the titles its examples use, in this order: Image from
`host` to `edit`, Upscale from `brief` to `enlarge`, Audio from `script` to
`speak`, Video and downloads from `scene` to `shot`, and Elements from
`opening` to `shot_2`.

**Host** and **Product** title the input boxes where the person describes
the host and the product, so the steps that draw them are **Cast** and
**Packshot**, as in F's video-02: a group and a box never share a title.

### `scripts/workflows/descriptions/notes.py`

The Tooling milestone created it holding only its docstring
(`"""The group notes and subgraph descriptions of the shipped workflows, in plain language."""`).
Fill it in F's shape: the docstring, the constants below, and
`WORKFLOW_TEXTS[slug][key]`, where `key` is a group's title key for its note
and `<subgraph key>_description` for a subgraph's description.
`__all__ = ["WORKFLOW_TEXTS"]`.

```python
SIGN_IN_STEP = "1. Sign in to Dreamina in **ComfyUI menu → Extensions → Dreamina → Dreamina Settings**.\n"
CANCEL_NOTE = "A cancel does not stop a video Dreamina has accepted. It keeps running and is billed."
RECOVER_NOTE = CANCEL_NOTE + " Collect it with **Generation: Download** in **video-04-recover-a-video**."
UPSCALE_RECOVER_NOTE = (
    "A cancel does not stop an upscale Dreamina has accepted. It keeps running and is billed. Collect it with "
    "**Generation: Download**."
)
```

The Image milestone adds `SIGN_IN_STEP`. The Upscale milestone adds
`UPSCALE_RECOVER_NOTE` ending after "is billed.", because Generation:
Download does not ship yet; the Video and downloads milestone adds its last
sentence, `CANCEL_NOTE`, and `RECOVER_NOTE`.

The cancel sentences follow Dreamina's documented behavior: there is no
cancel command, and deleting a node "does not ... cancel accepted generation
tasks or refund credits" ([02-dreamina-contract.md](02-dreamina-contract.md#waiting-and-recovery),
[01-decisions.md](01-decisions.md#paid-runs)). A cancel stops the pack's
wait, the record stays, and **Generation: Download** collects the result.
[14-node-download.md](14-node-download.md#the-recover-note) quotes the same
constants. Runs C-14 and D-1 and the video-01 run of
[21-test-runs.md](21-test-runs.md) check it; if a live cancel behaves
differently, the constants are rewritten to match the run, as B rewrote its
own after its run 14.

The exact text of every note is in [Example workflows](#example-workflows).
In the note tables there, `SIGN_IN_STEP`, `RECOVER_NOTE`, `CANCEL_NOTE`, and
`UPSCALE_RECOVER_NOTE` stand for the constants, and the quoted text is the
Python string that follows or precedes them, with `\n` for a line break.

## Step 3: Workflow descriptions

Create one module per family in `scripts/workflows/descriptions/`, each in
F's form (`F/scripts/workflows/descriptions/image.py` is the model): a module
docstring, constants for model names, `arguments` objects, and long prompts,
`<SLUG>_TEXTS = WORKFLOW_TEXTS["<slug>"]` lookups, `Subgraph` records,
`Workflow` records, the family's tuple, and `__all__`.

| Module        | Tuple               | Workflows                                   | Created in the milestone of |
| ------------- | ------------------- | ------------------------------------------- | --------------------------- |
| `image.py`    | `IMAGE_WORKFLOWS`   | image-01 and image-02; image-03 in Upscale  | Image                       |
| `audio.py`    | `AUDIO_WORKFLOWS`   | audio-01, audio-02                          | Audio                       |
| `video.py`    | `VIDEO_WORKFLOWS`   | video-01, video-02, video-04                | Video and downloads         |
| `elements.py` | `ELEMENT_WORKFLOWS` | video-03                                    | Elements                    |

video-03 has its own module because it needs Element: Add, which ships in
the last node milestone; `video.py` is then never edited after its
milestone. Its tuple is listed right after `VIDEO_WORKFLOWS` in `FAMILIES`,
with the same menu, as F lists `VOICE_WORKFLOWS`.

Module docstrings and exports:

| Module        | Docstring                                                                                          | `__all__`                      |
| ------------- | -------------------------------------------------------------------------------------------------- | ------------------------------ |
| `image.py`    | `"""The image workflows: design a host, edit a product photo, and upscale a poster."""`           | `["IMAGE_WORKFLOWS"]`          |
| `audio.py`    | `"""The audio workflows: voice a script in a chosen voice, and give a drawn host a voice."""`     | `["AUDIO_WORKFLOWS", "CAST"]`  |
| `video.py`    | `"""The video workflows: animate a host, film a product ad, and recover a video left running."""` | `["VIDEO_WORKFLOWS"]`          |
| `elements.py` | `"""The Element workflow: keep one host the same across two shots."""`                            | `["ELEMENT_WORKFLOWS"]`        |

`scripts/workflows/descriptions/nodes.py`, created in the Image milestone,
defines the paid node IDs once; each milestone adds the IDs its examples
first place:

```python
"""The node IDs of the paid nodes the shipped workflows place."""

from src.config.namespace import NODE_PREFIX

IMAGE_GENERATE = f"{NODE_PREFIX}ImageGenerate"
IMAGE_UPSCALE = f"{NODE_PREFIX}ImageUpscale"
VIDEO_GENERATE = f"{NODE_PREFIX}VideoGenerate"
AUDIO_GENERATE = f"{NODE_PREFIX}AudioGenerate"

__all__ = ["AUDIO_GENERATE", "IMAGE_GENERATE", "IMAGE_UPSCALE", "VIDEO_GENERATE"]
```

Free nodes placed once are written inline:
`f"{NODE_PREFIX}ModelInfo"`, `f"{NODE_PREFIX}GenerationDownload"`, and
`f"{NODE_PREFIX}ElementAdd"`. The model names that differ from a node's
starting model are constants of the one module that uses them: `SUNBURST`
(`dreamina_gpt_image_2_5_sunburst`) in `image.py`, `SEED_AUDIO`
(`seed_audio_v1`, Model: Info's `model`) in `audio.py`, and `SEEDANCE_2_5`
(`seedance_2.5`) in `video.py`. Each example's `<NAME>_ARGUMENTS` is a
constant of its module.

Shared record: `CAST`, the host portrait step, is defined in `audio.py` and
imported by `video.py` and `elements.py`, because audio-02, video-02, and
video-03 place the same step.

In `scripts/workflows/build.py`, each milestone adds its import and its
family. With every milestone built:

```python
FAMILIES = (
    (IMAGE_WORKFLOWS, MENUS["IMAGE"]),
    (AUDIO_WORKFLOWS, MENUS["AUDIO"]),
    (VIDEO_WORKFLOWS, MENUS["VIDEO"]),
    (ELEMENT_WORKFLOWS, MENUS["VIDEO"]),
)
```

The `MENUS` keys are [05-foundation.md](05-foundation.md#step-1-namespace-constants)'s;
the values are 04's `Dreamina/Image`, `Dreamina/Audio`, and `Dreamina/Video`.
`CAST`'s blueprint is listed under `Dreamina/Audio` from the Audio
milestone, and under `Dreamina/Video` once a video family places it, the
last family to place it.

Rules for every example, from F's descriptions:

- Paid nodes are `Node(..., is_paid=True)`, so they get `PAID_COLOURS`.
  Image: Generate, Image: Upscale, Video: Generate, and Audio: Generate are
  paid. Element: Add, Generation: Download, and Model: Info are not.
- The first group holds the inputs, in `Group`'s default `INPUT_COLOUR`.
  video-04 is the exception: its first group is the recover step, as F's
  video-05 is. Each later step is one `STAGE_COLOUR` group holding the
  step's subgraph and any node the person edits or reads beside it. Its
  title is the subgraph's name, so the person sees one name per step.
- Each step after the inputs is a `Subgraph` holding the step's paid node
  and the node that saves or shows its result, with `previews` exposing that
  result. Two kinds of node stay on the canvas instead: a free node the
  example exists to show (audio-01's Model: Info with its **Preview as
  Text**, video-03's Element: Add), and the nodes of a recover group.
- `model` is written `{"model": <NAME>}`, and only when it differs from the
  node's starting model ([01-decisions.md](01-decisions.md#choosing-a-model)).
- `arguments` is written `{"arguments": <NAME>_ARGUMENTS}`, a module constant
  made with `json.dumps(..., indent=2)`, only when it differs from the
  node's starting `arguments`. It holds every setting the example sets, the
  required ones included, at the cheapest values that prove the point: `2K`
  for Seedream (its smallest), `1K` for GPT Image 2.5 Sunburst, `720p` for
  Seedance 2.0 Mini (its only size), `480p` for Seedance 2.5, and four
  seconds, the shortest any video model on the list takes.
- `prompt` is linked from an input, or written `{"prompt": <text>}`.
  Placeholders are typed in the prompt as the person would: `{{image1}}`,
  `{{reference1}}`.
- `credit_ceiling` is left at the node's starting value, except where Part 0
  of [21-test-runs.md](21-test-runs.md) quotes the example's settings above
  it. That node sets `{"credit_ceiling": <quote rounded up to the next
  multiple of 10>}`, and Part 0 records the value in this plan.
- No example sets a seed: the lists give no seed flag, and `run_number` sends
  a run again.
- Media inputs ship empty (`{"image": ""}`, `{"generation": ""}`); the Start
  Here note says what to choose.
- Save prefixes are `image/dreamina/<name>`, `video/dreamina/<name>`, and
  `audio/dreamina/<name>`.
- Subgraph names are unique across all examples unless the subgraph is the
  same record, as `CAST` is.
- A step that would bill a second time ships bypassed, with a note saying how
  to turn it on: video-04's **Shot**. A step that makes something different,
  such as video-03's second shot, ships on.

## Example workflows

Nine examples cover every node. A workflow is built in the first milestone in
which all its nodes exist; the coverage check in `comfy:workflows:check` then
finds every registered node in at least one example.

The models the examples use, from the owner's live lists of 2026-10-16
([research/catalog.md](research/catalog.md)):

| Name                              | Model                              | Node                         | Used by                                                          | Settings used                    |
| --------------------------------- | ---------------------------------- | ---------------------------- | ---------------------------------------------------------------- | -------------------------------- |
| Seedream 5.0 Lite (starting)      | `seedream_5.0_lite`                | Image: Generate              | image-01, image-03, audio-02, video-01, video-02, video-03       | `ratio` `3:4`, `9:16`, or `1:1`; `resolution` `2K` |
| GPT Image 2.5 Sunburst (`SUNBURST`) | `dreamina_gpt_image_2_5_sunburst` | Image: Generate              | image-02                                                         | `ratio` `1:1`; `resolution` `1K` |
| Dreamina's upscale (no model)     | none                               | Image: Upscale               | image-03                                                         | `resolution` `2K`, mode `pro`    |
| Seedance 2.0 Mini (starting)      | `seedance_2.0_mini`                | Video: Generate              | video-01, video-03, video-04                                     | `720p`, 4 seconds; `9:16`, or the starting `16:9` in video-04 |
| Seedance 2.5 (`SEEDANCE_2_5`)     | `seedance_2.5`                     | Video: Generate              | video-02                                                         | `9:16`, `480p`, 4 seconds, `m2v` |
| Seed Audio (starting)             | `seed_audio_v1`                    | Audio: Generate, Model: Info | audio-01, audio-02                                               | Text reading with `voice-name`; omni dubbing |

GPT Image 2.5 Sunburst is the model live-shopping uses through fal today and
takes up to 16 pictures in `i2i`. Seedance 2.5 is the one video model on the
list that makes `480p`. Every value above is in the model's `values` or
range in the captures. Credits come from Part 0's price sweep, the
`minimumCreditCeiling` of a run with `--credit-ceiling 0`, which bills
nothing; this plan writes each run's parts, and Part 0 fills the numbers.

In the text graphs below, `<NAME>_ARGUMENTS` is a module constant holding the
JSON object shown under the graph, written with `json.dumps(..., indent=2)`.

### Summary

| Slug | Title | Milestone | Nodes it covers | The person provides | Credits of one run |
| ---- | ----- | --------- | --------------- | ------------------- | ------------------ |
| `image-01-design-a-host` | Image: Design a Host | Image | Image: Generate | Nothing; a host description is included | One Seedream 5.0 Lite image at `2K`, from Part 0 |
| `image-02-edit-a-product-photo` | Image: Edit a Product Photo | Image | Image: Generate | A product photo | One GPT Image 2.5 Sunburst edit at `1K`, from Part 0 |
| `image-03-upscale-a-poster` | Image: Upscale a Poster | Upscale | Image: Generate, Image: Upscale | Nothing | One `2K` image and one `2K` `pro` upscale, from Part 0 |
| `audio-01-voice-a-script` | Audio: Voice a Script | Audio | Audio: Generate, Model: Info | Nothing | One Seed Audio text reading of 103 characters, from Part 0; Model: Info is free |
| `audio-02-give-a-host-a-voice` | Audio: Give a Host a Voice | Audio | Image: Generate, Audio: Generate | Nothing | One `2K` image and one omni dubbing line of 83 characters, from Part 0 |
| `video-01-animate-a-host` | Video: Animate a Host | Video and downloads | Image: Generate, Video: Generate | Nothing | One `2K` image and one four-second `720p` Seedance 2.0 Mini video, from Part 0 |
| `video-02-film-a-product-ad` | Video: Film a Product Ad | Video and downloads | Image: Generate, Video: Generate | Nothing | Two `2K` images and one four-second `480p` Seedance 2.5 video, from Part 0 |
| `video-03-keep-a-host-across-shots` | Video: Keep a Host across Shots | Elements | Image: Generate, Element: Add, Video: Generate | Nothing | One `2K` image and two four-second `720p` Seedance 2.0 Mini videos, from Part 0; the Element is free |
| `video-04-recover-a-video` | Video: Recover a Video | Video and downloads | Generation: Download; Video: Generate ships turned off | A video left running | Free as shipped |

The nine runs, with video-01 canceled and collected by video-04, must fit
the 250 credits that [README.md](README.md#before-the-first-paid-run) gives
Part 4. If Part 0's quotes add up to more, this plan lowers the most
expensive example's settings first, and records it.

Milestones, as [README.md](README.md#build-order) orders them:

- **Model: Info** is built before Image and registered with audio-01 in the
  Audio milestone, so no example waits for it.
- **image-03** waits for the Upscale milestone, after Image, because it
  upscales an image Image: Generate made.
- **Audio** comes before Video and defines `CAST`, the step video-02 and
  video-03 place again.
- **Generation: Download** ships with Video: Generate because its only
  example, video-04, collects a video.
- **video-03** waits for the Elements milestone. Until then the README lists
  video-01, video-02, and video-04, and video-03's row goes in its place in
  slug order.

### `image-01-design-a-host`

Scenario: a live-shopping team designs an on-screen host with Seedream 5.0
Lite, the image node's starting model. It is the least expensive example
that needs nothing from the person, so it is the README's first run. What 09
asks for is in [09-node-image.md](09-node-image.md).

```text
Group Input (input): columns [host]
  host      TEXT_BLOCK  title Host
            value HOST_PROMPT

Group Design (design, STAGE): columns [design]
  design    subgraph Design

Subgraph Design: inputs host → draw.prompt; previews save IMAGE_PREVIEW
  draw      DreaminaImageGenerate (paid)  {arguments: DESIGN_ARGUMENTS}
  save      SAVE_IMAGE  {filename_prefix: "image/dreamina/host"}
  links     draw.images → save.images
  columns   [draw] [save]

Links: host.STRING → design.host
```

`HOST_PROMPT`: "Studio portrait of a live-shopping host: a cheerful woman in
her late twenties with shoulder-length auburn hair, a mustard knit sweater,
and small gold hoop earrings. Waist up, facing the camera, plain light gray
background, soft light."

`DESIGN_ARGUMENTS`: `{"ratio": "3:4", "resolution": "2K"}`.

`model` stays at the starting `seedream_5.0_lite`. `resolution` `2K` is its
smallest size and needs no membership; `3:4` is the only change from the
starting `arguments`, a portrait frame. With nothing connected the node
chooses `t2i`, and the pack sends `--count 1`. Credits: one image, from
Part 0.

| Key | Text |
| --- | ---- |
| `input` | `SIGN_IN_STEP` + "2. Describe your host in **Host**: how they look, what they wear, and the background.\n3. Press **Run**. The image is saved under `image/dreamina`." |
| `design` | "Seedream 5.0 Lite, the image node's starting model, draws the host from the waist up. `arguments` holds the model's own settings, written by the names Dreamina gives them: `ratio` `3:4` and `resolution` `2K`, its smallest size. To draw with another model, open **Design** and type another `model`, the model's name on Dreamina.\n\n`credit_ceiling` is the most credits one run may cost. A run that would cost more stops before anything is billed." |
| `design_description` | "Draws the host and saves the image." |

### `image-02-edit-a-product-photo`

Scenario: a seller puts their own product photo in a new setting for a
listing. GPT Image 2.5 Sunburst edits it. It is the one example that needs a
file from the person, and it shows an upload and the `{{image1}}`
placeholder. What 07 and 09 ask for is in [07-media.md](07-media.md) and
[09-node-image.md](09-node-image.md).

```text
Group Input (input): columns [photo, change]
  photo     IMAGE  {image: ""}  title Photo
  change    TEXT_BLOCK  title Change
            value CHANGE_PROMPT

Group Edit (edit, STAGE): columns [edit]
  edit      subgraph Edit

Subgraph Edit: inputs photo → draw.images, change → draw.prompt; previews save IMAGE_PREVIEW
  draw      DreaminaImageGenerate (paid)  {model: SUNBURST, arguments: EDIT_ARGUMENTS}
  save      SAVE_IMAGE  {filename_prefix: "image/dreamina/product-edit"}
  links     draw.images → save.images
  columns   [draw] [save]

Links: photo.IMAGE → edit.photo; change.STRING → edit.change
```

`CHANGE_PROMPT`: "Place the product from {{image1}} on a light oak table
beside a sunny window, with a soft shadow under it. Keep its shape, colors,
and label exactly as they are."

`EDIT_ARGUMENTS`: `{"ratio": "1:1", "resolution": "1K"}`.

With an image connected the node chooses `i2i`, which GPT Image 2.5 Sunburst
takes with 1 to 16 pictures. Its `ratio` and `resolution` are required, and
`1K` is its smallest size. Its `count` is 1 to 1, so `--count 1` changes
nothing. The pack uploads the photo as PNG, free, and `{{image1}}` becomes
the upload's `{{res:…}}` form, which run C-6 confirms
([01-decisions.md](01-decisions.md#placeholders)); if C-6 shows an upload
cannot be a placeholder, the prompt says "the product in the photo" instead.
**Photo** ships empty. Credits: one edit, from Part 0. Part 0 also shows
whether the quote passes the image node's starting `credit_ceiling`; if not,
**Edit**'s node sets it as the rules say.

| Key | Text |
| --- | ---- |
| `input` | `SIGN_IN_STEP` + "2. In **Photo**, upload a photo of one product, such as a bottle or a shoe.\n3. In **Change**, say where to put it. `{{image1}}` stands for your photo.\n4. Press **Run**. The edited photo is saved under `image/dreamina`." |
| `edit` | "The pack uploads your photo to your Dreamina canvas, the project named ComfyUI that holds every run, so the model can read it. GPT Image 2.5 Sunburst then redraws it as **Change** asks, at `1:1` and `1K`, its smallest size. `{{image1}}` in the prompt marks where your photo goes.\n\nTo combine several products, give **Edit** a list of up to 16 photos, and name them `{{image1}}`, `{{image2}}`, and so on." |
| `edit_description` | "Edits the product photo and saves it." |

### `image-03-upscale-a-poster`

Scenario: a shop makes an event poster at `2K`, then upscales it in `pro`
mode at `2K`, which adds fine detail for print. Image: Upscale starts from
the poster Dreamina already made, so nothing is downloaded or uploaded in
between. What 12 asks for is in
[12-node-upscale.md](12-node-upscale.md#step-7-readme-row-and-examples).

```text
Group Input (input): columns [brief]
  brief     TEXT_BLOCK  title Brief
            value POSTER_PROMPT

Group Poster (poster, STAGE): columns [poster]
  poster    subgraph Poster

Group Enlarge (enlarge, STAGE): columns [enlarge]
  enlarge   subgraph Enlarge

Subgraph Poster: inputs brief → draw.prompt; outputs references ← draw.references; previews save IMAGE_PREVIEW
  draw      DreaminaImageGenerate (paid)  {arguments: POSTER_ARGUMENTS}
  save      SAVE_IMAGE  {filename_prefix: "image/dreamina/poster"}
  links     draw.images → save.images
  columns   [draw] [save]

Subgraph Enlarge: inputs references → up.references; previews save IMAGE_PREVIEW
  up        DreaminaImageUpscale (paid)
  save      SAVE_IMAGE  {filename_prefix: "image/dreamina/poster-upscaled"}
  links     up.images → save.images
  columns   [up] [save]

Links: brief.STRING → poster.brief; poster.references → enlarge.references
```

`POSTER_PROMPT`: 'A poster for a summer night market: the title "Night
Market" in bold hand-lettered type at the top, paper lanterns and food stalls
in silhouette, and the date "August 14" at the bottom. Flat illustration in
deep blue and orange.'

`POSTER_ARGUMENTS`: `{"ratio": "3:4", "resolution": "2K"}`.

**Enlarge**'s Image: Upscale keeps its starting values: the CLI's default
mode `pro` and `arguments` `{"resolution": "2K"}`, the lowest `pro` size,
since every example uses the lowest settings. `detail` keeps its default, 50. The poster is
already `2K`, and Dreamina decides whether a target fits its source; run U-1
of 12 and Part 4's run of this example check that it takes `2K`. The poster
is saved as well, so the two can be compared. The starting `credit_ceiling`,
10, covers Part 0's quote of 2 credits for a `2K` `pro` upscale. Credits: one
image and one upscale, 6 + 2 = 8, from Part 0.

| Key | Text |
| --- | ---- |
| `input` | `SIGN_IN_STEP` + "2. Describe the poster in **Brief**. Put any words it must show in quotation marks.\n3. Press **Run**. The poster and its upscaled version are saved under `image/dreamina`." |
| `poster` | "Seedream 5.0 Lite draws the poster at `2K`, its smallest size, in a `3:4` frame. `references`, what an earlier Dreamina step made, passes the poster on to **Enlarge** with no download or upload." |
| `poster_description` | "Draws the poster and saves it." |
| `enlarge` | "**Image: Upscale** redraws the poster at `2K` in its `pro` mode, which adds fine detail. For a larger print, set `resolution` in `arguments` to `4K` or `8K`. `detail`, from 1 to 100, sets how much detail it adds. For a plain enlargement to twice the size, set `mode` to `normal` and leave out `resolution`.\n\n" + `UPSCALE_RECOVER_NOTE` |
| `enlarge_description` | "Upscales the poster and saves it." |

### `audio-01-voice-a-script`

Scenario: a host's opening line, read aloud in a chosen voice. **Voices**
shows Model: Info's report on Seed Audio, with its 13 voices, and **Voice**
reads the script in one of them. Built in the Audio milestone, which
registers Model: Info. What 11 and 15 ask for is in
[11-node-audio.md](11-node-audio.md) and
[15-node-model-info.md](15-node-model-info.md).

```text
Stack 1:
  Group Input (input): columns [script]
    script    TEXT_BLOCK  title Script
              value SCRIPT_PROMPT
  Group Voices (voices): columns [info] [row]
    info      DreaminaModelInfo  {model: SEED_AUDIO}
    row       PREVIEW  title Info

Group Voice (voice, STAGE): columns [voice]
  voice     subgraph Voice

Subgraph Voice: inputs script → speak.prompt
  speak     DreaminaAudioGenerate (paid)  {arguments: VOICE_ARGUMENTS}
  save      SAVE_AUDIO  {filename_prefix: "audio/dreamina/script-voice"}
  links     speak.audio → save.audio
  columns   [speak] [save]

Links: script.STRING → voice.script; info.info → row.source
```

`SCRIPT_PROMPT`: "Welcome back to the show. Today we have three new
sneakers, and the first pair is already selling fast."

`VOICE_ARGUMENTS`: `{"voice-name": "Good Guy"}`.

`model` stays at the starting `seed_audio_v1`. With nothing connected the
node chooses `tts` with the scenario `text-reading`, whose `voice-name` is
required; **Good Guy** is one of the 13 voices `voice list` returned, set so
the example shows choosing one other than the starting **Jessie**. Audio
takes no `count`. Model: Info's input is `model`, and its starting value is
the image node's model ([15-node-model-info.md](15-node-model-info.md#step-4-model-info)),
so **Voices** sets `seed_audio_v1`. The node runs on every **Run**, free,
because **Preview as Text** is an output node. The save name is
`script-voice`, as F named its own. Credits: one reading of 103 characters,
from Part 0.

| Key | Text |
| --- | ---- |
| `input` | `SIGN_IN_STEP` + "2. In **Script**, write what the host says.\n3. Press **Run**. The voice is saved under `audio/dreamina`." |
| `voices` | "**Model: Info** shows what a Dreamina model takes: its modes, its settings with their choices and limits, and a speech model's voices. It is free. **Info** shows Seed Audio, the audio node's starting model, with its 13 voices.\n\nTo change the voice, copy a name from **Info**, open **Voice**, and put it in `arguments` as `voice-name`." |
| `voice` | "Seed Audio reads **Script** aloud in the voice that `voice-name` names: here `Good Guy`. `arguments` holds the model's own settings, written by the names Dreamina gives them. With nothing connected, the node uses text reading, Seed Audio's way to read a script in a chosen voice.\n\nConnect a picture instead, and Seed Audio makes a voice that suits it, as **audio-02-give-a-host-a-voice** does." |
| `voice_description` | "Reads the script aloud and saves the voice." |

### `audio-02-give-a-host-a-voice`

Scenario: the voice of a host the team designed. Seedream draws a host
portrait, then Seed Audio's omni dubbing speaks a line in a voice that suits
the face, with no voice chosen. It shows a reference reaching Audio: Generate
and the scenario the node chooses by itself. What 11 asks for is in
[11-node-audio.md](11-node-audio.md).

```text
Group Input (input): columns [host, line]
  host      TEXT_BLOCK  title Host
            value CAST_HOST
  line      TEXT_BLOCK  title Line
            value LINE_PROMPT

Group Cast (cast, STAGE): columns [cast]
  cast      subgraph Cast

Group Speak (speak, STAGE): columns [speak]
  speak     subgraph Speak

Subgraph Cast (CAST): inputs host → draw.prompt; outputs references ← draw.references; previews look IMAGE_PREVIEW
  draw      DreaminaImageGenerate (paid)  {arguments: CAST_ARGUMENTS}
  look      PREVIEW_IMAGE
  links     draw.images → look.images
  columns   [draw] [look]

Subgraph Speak: inputs references → speak.references, line → speak.prompt
  speak     DreaminaAudioGenerate (paid)  {arguments: SPEAK_ARGUMENTS}
  save      SAVE_AUDIO  {filename_prefix: "audio/dreamina/host-voice"}
  links     speak.audio → save.audio
  columns   [speak] [save]

Links: host.STRING → cast.host; cast.references → speak.references; line.STRING → speak.line
```

`CAST_HOST`: "A friendly live-shopping host in his thirties with short curly
hair and a denim jacket. Waist up, facing the camera, in a bright studio,
photorealistic."

`LINE_PROMPT`: "Hi everyone, it's so good to see you. I've got something
special to show you today."

`CAST_ARGUMENTS`: `{"ratio": "3:4", "resolution": "2K"}`.
`SPEAK_ARGUMENTS`: `{}`.

A picture in `references` makes the node choose `tts` with the scenario
`omni-dubbing` ([01-decisions.md](01-decisions.md#how-the-mode-is-chosen)).
`seed_audio_v1` lists omni dubbing with `scenario` and `prompt` only, 0 to 1
image, and image and audio not together. The starting `arguments`,
`{"voice-name": "Jessie"}`, would be refused there as a setting the mode
does not list, so **Speak** sends the empty object. Credits: one image and
one line of 83 characters, from Part 0.

`CAST` is one record for three workflows. Its description comes from this
example's texts; each workflow writes its own note for it.

| Key | Text |
| --- | ---- |
| `input` | `SIGN_IN_STEP` + "2. Describe the host in **Host**.\n3. In **Line**, write what the host says.\n4. Press **Run**. The voice is saved under `audio/dreamina`." |
| `cast` | "Seedream 5.0 Lite draws the host from the waist up. `references`, what an earlier Dreamina step made, passes the portrait on to **Speak** with no download or upload." |
| `cast_description` | "Draws the host." |
| `speak` | "Seed Audio looks at the portrait and speaks **Line** in a voice that suits the host. A picture in `references` makes the node use omni dubbing, Seed Audio's way to voice a picture. Omni dubbing takes no `voice-name`, so `arguments` is empty (`{}`).\n\nTo choose the voice yourself, leave the portrait out and set `voice-name`, as **audio-01-voice-a-script** does." |
| `speak_description` | "Speaks the line in a voice that suits the host and saves it." |

### `video-01-animate-a-host`

Scenario: Seedream draws a host in a vertical frame, and Seedance 2.0 Mini,
the video node's starting model, starts the video on that picture. The
picture reaches Seedance as a reference. What 10 asks for is in
[10-node-video.md](10-node-video.md).

```text
Group Input (input): columns [host, scene]
  host      TEXT_BLOCK  title Host
            value PORTRAIT_HOST
  scene     TEXT_BLOCK  title Scene
            value ANIMATE_SCENE

Group Portrait (portrait, STAGE): columns [portrait]
  portrait  subgraph Portrait

Group Animate (animate, STAGE): columns [animate]
  animate   subgraph Animate

Subgraph Portrait (PORTRAIT): inputs host → draw.prompt; outputs references ← draw.references; previews look IMAGE_PREVIEW
  draw      DreaminaImageGenerate (paid)  {arguments: PORTRAIT_ARGUMENTS}
  look      PREVIEW_IMAGE
  links     draw.images → look.images
  columns   [draw] [look]

Subgraph Animate (ANIMATE): inputs references → video.references, scene → video.prompt
  video     DreaminaVideoGenerate (paid)  {arguments: ANIMATE_ARGUMENTS}
  save      SAVE_VIDEO  {filename_prefix: "video/dreamina/host"}
  links     video.video → save.video
  columns   [video] [save]

Links: host.STRING → portrait.host; portrait.references → animate.references; scene.STRING → animate.scene
```

`PORTRAIT_HOST`: "A friendly man in his thirties with short curly hair and a
denim jacket, standing in a bright studio with shelves of sneakers behind
him. Waist up, looking at the camera, photorealistic."

`ANIMATE_SCENE`: "He smiles, picks up a sneaker from the shelf, and turns it
toward the camera. Slow push-in, warm light."

`PORTRAIT_ARGUMENTS`: `{"ratio": "9:16", "resolution": "2K"}`.
`ANIMATE_ARGUMENTS`: `{"ratio": "9:16", "resolution": "720p", "duration": 4}`.

One picture and nothing else makes the node choose `first_last_frame`, and
its one-image entry ([01-decisions.md](01-decisions.md#how-the-mode-is-chosen)).
`ratio` is required in that mode too, so it is set to the picture's own
`9:16`. `720p` is Seedance 2.0 Mini's only size, and four seconds its
shortest; only `ratio` differs from the starting `arguments`. Credits: one
image and one video, from Part 0.

| Key | Text |
| --- | ---- |
| `input` | `SIGN_IN_STEP` + "2. Describe your host in **Host**, and what they do in **Scene**.\n3. Press **Run**. The video is saved under `video/dreamina`." |
| `portrait` | "Seedream 5.0 Lite draws the host in a `9:16` frame. This picture becomes the video's first frame. `references`, what an earlier Dreamina step made, passes it on to **Animate** with no download or upload." |
| `portrait_description` | "Draws the host." |
| `animate` | "Seedance 2.0 Mini, the video node's starting model, starts on the host and makes a four-second `720p` video. With one picture connected, the node uses `first_last_frame`, the mode that starts the video on that picture. A second picture would set the last frame. Raise `duration` in `arguments` for up to 15 seconds.\n\n" + `RECOVER_NOTE` |
| `animate_description` | "Turns the host into a video and saves it." |

### `video-02-film-a-product-ad`

Scenario: a host holds up a product in a vertical ad. Seedream draws the host
and the product, and Seedance 2.5 films them together in `m2v`, with
placeholders marking who and what in the prompt. What 10 asks for is in
[10-node-video.md](10-node-video.md).

```text
Group Input (input): columns [host, product, scene]
  host      TEXT_BLOCK  title Host
            value FILM_HOST
  product   TEXT_BLOCK  title Product
            value FILM_PRODUCT
  scene     TEXT_BLOCK  title Scene
            value FILM_SCENE

Group Cast (cast, STAGE): columns [cast]
  cast      subgraph Cast

Group Packshot (packshot, STAGE): columns [packshot]
  packshot  subgraph Packshot

Group Film (film, STAGE): columns [film]
  film      subgraph Film

Subgraph Cast: CAST, as in audio-02

Subgraph Packshot: inputs product → draw.prompt; outputs images ← draw.images; previews look IMAGE_PREVIEW
  draw      DreaminaImageGenerate (paid)
  look      PREVIEW_IMAGE
  links     draw.images → look.images
  columns   [draw] [look]

Subgraph Film: inputs host → video.references, product → video.images, scene → video.prompt
  video     DreaminaVideoGenerate (paid)  {model: SEEDANCE_2_5, arguments: FILM_ARGUMENTS}
  save      SAVE_VIDEO  {filename_prefix: "video/dreamina/product-ad"}
  links     video.video → save.video
  columns   [video] [save]

Links: host.STRING → cast.host; product.STRING → packshot.product; cast.references → film.host;
       packshot.images → film.product; scene.STRING → film.scene
```

`FILM_HOST`: "A cheerful woman in her late twenties with shoulder-length
auburn hair and a mustard knit sweater. Waist up, facing the camera, in a
bright studio, photorealistic."

`FILM_PRODUCT`: "A pair of white canvas sneakers with red laces, side view,
on a plain white background, soft studio light."

`FILM_SCENE`: "The host in {{reference1}} holds up the sneakers from
{{image1}}, smiles, and turns them toward the camera to show the red laces.
Bright studio, slow push-in."

`FILM_ARGUMENTS`: `{"mode": "m2v", "ratio": "9:16", "resolution": "480p", "duration": 4}`.

How the two pictures reach Seedance: `references` takes one connection, so
the host comes from **Cast**'s `references`, with no upload, and the product
from **Packshot**'s `images`, which the pack uploads again, free. The `--ref`
order is `references` first, then `images`
([01-decisions.md](01-decisions.md#order)), so the host is the first
reference and the product the second, and the placeholders `{{reference1}}`
and `{{image1}}` bind each to its place in the prompt. One reference and one
image and nothing else would make the node choose `first_last_frame`, so
`arguments` sets `"mode": "m2v"`, as 01 says
([01-decisions.md](01-decisions.md#how-the-mode-is-chosen)); the note says
so. `seedance_2.5` takes 0 to 30 images in `m2v` and needs one image, video,
or audio. **Packshot** keeps the image node's starting `arguments`
(`{"ratio": "1:1", "resolution": "2K"}`), so it sets no value. Credits: two
images and one video, from Part 0; if the quote passes the video node's
starting `credit_ceiling`, **Film**'s node sets it as the rules say.

If the owner wants both pictures to travel as references with no upload,
[10-node-video.md](10-node-video.md) and [08-runs.md](08-runs.md) need a
growing row of `references` sockets or a node that joins references; this
example then links **Packshot**'s `references` too, and its prompt says
`{{reference2}}`.

| Key | Text |
| --- | ---- |
| `input` | `SIGN_IN_STEP` + "2. Describe the host in **Host** and the product in **Product**.\n3. In **Scene**, say what happens. `{{reference1}}` stands for the host and `{{image1}}` for the product.\n4. Press **Run**. The video is saved under `video/dreamina`." |
| `cast` | "Seedream 5.0 Lite draws the host from the waist up. `references`, what an earlier Dreamina step made, passes the portrait on to **Film** with no download or upload." |
| `packshot` | "Seedream 5.0 Lite draws the product on a plain background. **Film** takes it from `images`, and the pack uploads it to your Dreamina canvas again, because `references` takes one connection." |
| `packshot_description` | "Draws the product." |
| `film` | "Seedance 2.5 films the host holding the product, four seconds at `480p`, its smallest size, in a `9:16` frame. `model`, the model's name on Dreamina, is `seedance_2.5`. Two pictures alone would become the first and last frames, so `arguments` sets `mode` to `m2v`, the mode that uses them as references. **Scene** names them `{{reference1}}` and `{{image1}}`.\n\n" + `RECOVER_NOTE` |
| `film_description` | "Films the host with the product and saves the video." |

### `video-03-keep-a-host-across-shots`

Built in the Elements milestone. Scenario: two shots of one ad, with the same
host in both. Seedream draws the host, Element: Add keeps the portrait as a
Dreamina Element, free, and two Seedance 2.0 Mini shots reference the
Element, so the face and outfit match. Element: Add stays on the canvas,
because the example exists to show it. What 13 asks for is in
[13-node-element.md](13-node-element.md#step-7-readme-row-and-examples).

```text
Group Input (input): columns [host, opening, closing]
  host      TEXT_BLOCK  title Host
            value KEEP_HOST
  opening   TEXT_BLOCK  title Opening
            value OPENING_SCENE
  closing   TEXT_BLOCK  title Closing
            value CLOSING_SCENE

Group Cast (cast, STAGE): columns [cast]
  cast      subgraph Cast

Group Keep (keep, STAGE): columns [keep]
  keep      DreaminaElementAdd  {title: "Host"}

Group Shot 1 (shot_1, STAGE): columns [shot_1]
  shot_1    subgraph Shot 1

Group Shot 2 (shot_2, STAGE): columns [shot_2]
  shot_2    subgraph Shot 2

Subgraph Cast: CAST, as in audio-02

Subgraph Shot 1: inputs element → video.references, scene → video.prompt
  video     DreaminaVideoGenerate (paid)  {arguments: SHOT_ARGUMENTS}
  save      SAVE_VIDEO  {filename_prefix: "video/dreamina/host-shot-1"}
  links     video.video → save.video
  columns   [video] [save]

Subgraph Shot 2: as Shot 1, with save {filename_prefix: "video/dreamina/host-shot-2"}

Links: host.STRING → cast.host; cast.references → keep.main; keep.references → shot_1.element;
       keep.references → shot_2.element; opening.STRING → shot_1.scene; closing.STRING → shot_2.scene
```

`KEEP_HOST`: "A friendly man in his thirties with short curly hair and a
denim jacket. Waist up, facing the camera, plain light gray background,
photorealistic."

`OPENING_SCENE`: "The host from {{reference1}} stands behind a counter of
sneakers, waves at the camera, and picks up a white sneaker. Bright studio,
medium shot."

`CLOSING_SCENE`: "The host from {{reference1}} holds the white sneaker next
to his face and points at it, smiling. Close-up, warm light."

`SHOT_ARGUMENTS`: `{"ratio": "9:16", "resolution": "720p", "duration": 4}`.

Element: Add takes the portrait in `main`, a socket that takes a ComfyUI
image or one image from another Dreamina node's `references`
([13-node-element.md](13-node-element.md#step-3-element-add)). Its `title`
is required, so the example sets `Host`, as 13 asks; `auxiliary`, `voice`,
and `description` stay empty. It uploads nothing here, because the portrait
is already on the canvas, and it outputs one Element in `references`. An
Element connected makes the node choose `m2v`
([01-decisions.md](01-decisions.md#how-the-mode-is-chosen)), so the shots set
no `mode`, and `{{reference1}}` in each prompt marks the host, as 13's help
page tells a person to write it. `seedance_2.0_mini` lists `m2v` with
`requireAnyOfTypes` image or video, and 07 counts an Element as an image
([07-media.md](07-media.md#step-8-references-and-placeholders)); run C-15
confirms how Dreamina counts it. If C-15 shows Seedance refuses an Element
alone, each shot also takes **Cast**'s portrait in `images`, and 07 and this
plan are corrected.

**Shot 2 ships on.** The owner's rule is "a step that would bill twice ships
bypassed": a step that sends again what an earlier step already made, such
as B's **Finish**, which re-rendered B's **Draft**, or a recover group that
would start a generation again. **Shot 2** films a different shot, the
second half of the ad, and B's video-02 shipped both of its shots on. The
Start Here note says two videos are made, and **Shot 2**'s note says each
shot is billed. Credits: one image and two videos, from Part 0; creating the
Element is free.

| Key | Text |
| --- | ---- |
| `input` | `SIGN_IN_STEP` + "2. Describe the host in **Host**.\n3. Say what happens in the first shot in **Opening**, and in the second in **Closing**.\n4. Press **Run**. Both shots are saved under `video/dreamina`." |
| `cast` | "Seedream 5.0 Lite draws the host from the waist up. `references`, what an earlier Dreamina step made, passes the portrait on to **Keep**." |
| `keep` | "**Element: Add** saves the portrait as an Element named **Host**, a character Dreamina keeps so it looks the same in every video. Making an Element is free. Its `references` output gives both shots the same host.\n\nTo keep more angles of the host, connect them to `auxiliary`. A voice clip goes in `voice`." |
| `shot_1` | "Seedance 2.0 Mini films **Opening** with the host from **Keep**, four seconds at `720p` in a `9:16` frame. With an Element connected, the node uses `m2v`, the mode that takes references, and `{{reference1}}` in the prompt marks the host.\n\n" + `RECOVER_NOTE` |
| `shot_1_description` | "Films the first shot with the kept host and saves it." |
| `shot_2` | "Seedance 2.0 Mini films **Closing** with the same Element, so the host matches **Shot 1**. Each shot is its own run and is billed.\n\n" + `RECOVER_NOTE` |
| `shot_2_description` | "Films the second shot with the kept host and saves it." |

### `video-04-recover-a-video`

Scenario: collect a video Dreamina kept making after a cancel, a timeout, or
a restart. It follows the recover pattern the owner set for B and F: the
recover group ships on, and the video step that would bill again ships
bypassed beside it, so a person can make a video here, cancel it, turn the
step off, and collect it, all in one tab. What 14 asks for is in
[14-node-download.md](14-node-download.md#the-example). Part 4 of
[21-test-runs.md](21-test-runs.md) runs it after video-01, with **Shot**
left off.

The bypassed step is a video step of its own, not a copy of video-01's
**Animate**. **Animate** needs **Portrait**'s picture, so copying it would
bring a second paid step and an inputs group into a workflow whose job is to
collect. **Shot** is one Video: Generate at the node's starting model and
`arguments`, with its prompt inside, so turning it on bills one video and
nothing else.

```text
Group Collect (collect, STAGE): columns [download] [save]
  download  DreaminaGenerationDownload  {generation: ""}
  save      SAVE_VIDEO  {filename_prefix: "video/dreamina/recovered"}

Group Shot (shot, STAGE): columns [shot]
  shot      subgraph Shot  (bypassed)

Subgraph Shot
  video     DreaminaVideoGenerate (paid)  {prompt: SHOT_PROMPT}
  save      SAVE_VIDEO  {filename_prefix: "video/dreamina/shot"}
  links     video.video → save.video
  columns   [video] [save]

Links: download.video → save.video
```

`SHOT_PROMPT`: "A white canvas sneaker with red laces turns slowly on a plain
white turntable. Soft studio light, slow push-in."

`generation` ships empty, so the first run stops at Generation: Download
until the person chooses a generation; 14 owns the input's ID. Generation:
Download fills only the outputs the generation made, and **Save Video** saves
the video. **Shot** keeps the starting `seedance_2.0_mini` and
`{"ratio": "16:9", "resolution": "720p", "duration": 4}`, its cheapest
settings, and with nothing connected the node chooses `t2v`. It is
`Node(..., is_bypassed=True)`, so a run as shipped bills nothing; the
re-measurement checks that the frontend leaves its inner paid node out of the
prompt ([Step 1](#re-measure-the-page-on-frontend-1527)). The recover group
is the first group, so its note is **Start Here**, and it keeps F's recover
form: when to use it, the steps, then what happens to the list. Credits: none
as shipped; with **Shot** turned on, one four-second `720p` video, the
price 21 calls `VID-D`.

| Key | Text |
| --- | ---- |
| `collect` | "Use this after you cancel a video Dreamina has already accepted, after a run times out, or after ComfyUI restarts while a video is being made. Dreamina keeps making it and bills it, and the pack keeps a record of it.\n\n" + `SIGN_IN_STEP` + "2. In **Collect**, choose the video in `generation`. Each entry shows the start of its ID, its model, and when it started, in UTC. Press R to list videos started after the page loaded.\n3. Press **Run**. The video is saved under `video/dreamina`.\n\nA video leaves the list once it is saved. If Dreamina no longer has its record, the node says so, and you can look for the video on your Dreamina canvas." |
| `shot` | "Seedance 2.0 Mini makes a four-second `720p` clip from the prompt inside **Shot**. **Shot** ships turned off, so a run here makes nothing new and bills nothing. To make a video to recover, select **Shot**, press Ctrl+B to turn it on, press **Run**, and cancel once **Shot** has started. Then turn it off again, choose the video in **Collect**, and run.\n\n" + `CANCEL_NOTE` + " **Collect** downloads it." |
| `shot_description` | "Makes a four-second clip and saves it." |

## Step 4: Build the examples

In every milestone that adds or changes an example, after its description
module and notes:

```sh
mise run comfy:workflows:build
```

It writes `example_workflows/<slug>.json` for every workflow in `FAMILIES`
and `subgraphs/<name>.json` for every subgraph, with `indent=2` and a
trailing newline. Commit the files with the descriptions that produced them.

| Milestone           | Examples                    | Blueprints added                     |
| ------------------- | --------------------------- | ------------------------------------ |
| Image               | image-01, image-02          | Design, Edit                         |
| Upscale             | image-03                    | Poster, Enlarge                      |
| Audio               | audio-01, audio-02          | Voice, Cast, Speak                   |
| Video and downloads | video-01, video-02, video-04 | Portrait, Animate, Packshot, Film, Shot |
| Elements            | video-03                    | Shot 1, Shot 2                       |

Fourteen blueprints in all. **Input**, **Voices**, **Keep**, and **Collect**
are groups with no subgraph.

In the same milestone, add each workflow's row to the README **Example
workflows** table ([18-documentation.md](18-documentation.md#step-2-readme-text)),
because `mise run comfy:workflows:check`, run by the pre-push hook, refuses
a workflow the README does not link, a file no description makes, a stale
file, and a node that no workflow places
([The page engine](#--check)).

Rebuild after any change to a node's schema, a host node, `texts.py`,
`notes.py`, or a description module. The build reads nothing from Dreamina:
a model name or a setting in `arguments` is checked by the node before
paying ([06-model-check.md](06-model-check.md)), and every example's are
checked by its run in [21-test-runs.md](21-test-runs.md). When Dreamina
removes a model an example uses, the example moves to a current model in a
commit of its own. ComfyUI lists the files under **Browse Templates →
dreamina**, after the install folder; a person who opened an older copy
opens the new one in a new tab.

The page is measured once, in the Documentation and brand milestone
([Step 1](#re-measure-the-page-on-frontend-1527)), and the rebuilt files go
in a commit of their own.

## Step 5: Run each example once

Each example is run once before release, in
[Part 4 of 21-test-runs.md](21-test-runs.md#part-4-run-every-example-once),
after the Documentation milestone and apart from its commit. 21 gives the
order (image-01, image-02, image-03, audio-01, audio-02, video-01, video-04,
video-02, video-03), the checks, and the credits. Its Step 1 quotes every
paid node of every example with this plan's exact values and
`--credit-ceiling 0`, free, and shows the owner the filled table; the nine
must add up to at most 250 credits. Ask the owner first; each run spends the
owner's Dreamina credits, and the owner approves each.

How, as F's runs were made:

- Open the example from **Browse Templates → dreamina**, set what its
  **Start Here** note asks, and press **Run**.
- Or run `example_workflows/<slug>.json` through the comfy-mcp `run_workflow`
  tool, which expands subgraphs.
- Or build each prompt with ComfyUI's own frontend, `app.graphToPrompt()` in
  a headless page, so subgraphs and bypassed steps are handled as **Run**
  handles them, then queue it through `/prompt`. F's runs used this way.

Rules for the runs:

- ComfyUI keeps only the last run's results in its cache, so run each
  multi-step example start to finish before opening the next; B's two-stage
  example had to run twice when another ran between its stages.
- image-02 needs a product photo in ComfyUI's `input` folder: 21 uses
  `dreamina-test-apple.png`, made in its Part 0.
- video-01 is canceled once its generation record appears, and video-04
  collects that video with **Shot** left off. If the video finishes before
  the cancel lands, run video-01 again and cancel sooner.
- Afterwards the state folder's `generations/` folder is empty, every run
  shows on the **ComfyUI** canvas, and the owner compares the credits each
  run took with Part 0's quotes. Record anything that differs, and every
  fix, in [Changes made while building](README.md#changes-made-while-building),
  each fix in a commit of its own.
