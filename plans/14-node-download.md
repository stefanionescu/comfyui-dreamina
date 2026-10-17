# Download Node

This plan builds **Generation: Download** (`GenerationDownload`), the free
node that collects a Dreamina generation that kept running after a cancel, a
timeout, or a ComfyUI restart. It reads the record a paid node saved when
Dreamina accepted the run, waits for the generation with read-only calls,
downloads what it made, and returns it through the same outputs as the paid
nodes. It never starts a run.

It is the Dreamina form of F's **Request: Download**
(`F/src/nodes/download.py`), ported as
[04-architecture.md](04-architecture.md#port-map) says. One node collects
every kind, because every Dreamina run, image, video, audio, or upscale, is
followed the same way: `operation wait <submitId>`, `node show`, and
`resource download`.

The machinery is [08-runs.md](08-runs.md)'s: `GenerationStore`,
`list_generation_labels`, `CollectOperation`, `send_run`, `wait_for_run`, and
`build_node_outputs`. This plan owns `src/nodes/download.py`, the empty-list
message, the node's help page, its README row, the node settings of its
example, and its first live run.

It ships in the **Video and downloads** milestone, built before
[10-node-video.md](10-node-video.md), because its only example,
`video-04-recover-a-video`, collects a video run
([README.md](README.md#build-order)). Commit:
`feat(nodes): add the video node and generation downloads`.

## Contents

- [Decisions](#decisions)
- [Step 1: Label lookup and messages](#step-1-label-lookup-and-messages)
- [Step 2: Generation: Download](#step-2-generation-download)
- [Step 3: What fills each output](#step-3-what-fills-each-output)
- [Step 4: Register](#step-4-register)
- [Step 5: Help page](#step-5-help-page)
- [Step 6: README row and examples](#step-6-readme-row-and-examples)
- [Step 7: Live checks](#step-7-live-checks)
- [Names this plan uses from other plans](#names-this-plan-uses-from-other-plans)

## Decisions

| Question | Decision | Why |
| -------- | -------- | --- |
| Why is the node needed? | Dreamina has no cancel for a generation it accepted, and deleting the node "does not … cancel accepted generation tasks or refund credits". A cancel, a timeout, or a restart stops only ComfyUI's wait. The generation is still made and billed, and its record stays. | [02-dreamina-contract.md](02-dreamina-contract.md#waiting-and-recovery); [01-decisions.md](01-decisions.md#paid-runs). |
| Does it start anything? | Never. It runs only `operation wait`, `node show`, and `resource download`, all free and read-only. | The skill: "a new read-only `operation wait` with the returned submit ID is safe"; "do not replay the run". |
| How does it list records? | A plain `io.Combo` whose options are `list_generation_labels(get_runtime().generations)`, read each time ComfyUI builds the node definitions. ComfyUI's **R** (Refresh Node Definitions) reads them again and updates a node already on the canvas. No route and no frontend code. | F's Request: Download; [01-decisions.md](01-decisions.md#browser-code). |
| What does a label show? | `<first 8 characters of the submit ID> · <model> · <YYYY-MM-DD HH:MM>`, the time in UTC, newest first. An upscale shows the model `upscale`. | 08's label form; enough to tell runs apart without the whole UUID. |
| A label recorded after the definitions were built | Accepted. `validate_inputs(**inputs)` returns `True` for any label, so ComfyUI skips its own dropdown check, as F's and O's Download nodes do. The node finds the record when it runs. | The owner's rule: a Download node's `validate_inputs` takes `**inputs`. |
| One node for every kind? | Yes. The outputs are the union of the paid nodes' outputs, in [01-decisions.md](01-decisions.md#outputs)'s order. An output the generation did not fill stops the nodes connected to it (`ExecutionBlocker`). | Any example that saves a paid node's output can save this node's the same way. |
| Which files are downloaded? | Every successful resource of the record's submit ID, whatever its media, because the node does not know which output the person saves. | 08's `CollectOperation` rule, as F's collects every file. |
| When is the record deleted? | After every download, so a failed download can be collected again. Also when the generation failed, when Dreamina reports its submission `absent`, when its node is no longer on the canvas, and when the record is older than `RECORD_RETENTION_SECONDS`. | [04-architecture.md](04-architecture.md#how-a-recorded-generation-is-collected). |
| `submission.state` `absent` | The record is deleted with 08's `GENERATION_ABSENT`, which sends the person to their Dreamina projects, where the result may be. | The skill: "do not infer that nothing ran: the record can have expired." |
| A record past retention | Deleted with `GENERATION_EXPIRED`, with no CLI call. | Dreamina no longer answers for it. |
| Cancel | Stops the wait with 08's `GENERATION_KEEPS_RUNNING`. The record stays. Nothing is sent, since there is nothing to cancel. | Collecting never started the generation. |
| Is it a paid node? | No. Collecting bills nothing, and one record always gives the same outputs, so ComfyUI's cache is right and the node needs no run number. | F's Request: Download. |

## Step 1: Label lookup and messages

### Label lookup

This step adds `find_record(label: str) -> GenerationRecord` to 08's
`GenerationStore` in `src/dreamina/generations/records.py`, as
[08-runs.md](08-runs.md#step-12-generation-store-the-runtime-and-the-status)
leaves it to this plan. It returns the newest record whose label, built by
the same private `_build_label` as `list_generation_labels`, equals `label`,
else raises `DreaminaError(ErrorCode.INVALID_INPUT, GENERATION_UNKNOWN)`.
Comparing whole labels, not only the eight characters of the submit ID,
keeps two records whose IDs start alike apart. It blocks, so the node calls
it in a worker thread.

`list_generation_labels` has its first caller here, so this milestone removes
its entry from `quality/config/repository/functions.json`, as 08's allowlist
table says. `find_record` is a method, so it needs no entry.

### Messages

Generation: Download uses 08's messages in `src/config/messages/generations.py`
for every outcome of a collect: `GENERATION_ABSENT`, `GENERATION_EXPIRED`,
`GENERATION_GONE`, `GENERATION_FAILED`, `GENERATION_EMPTY` (a run that
finished with no output), `GENERATION_KEEPS_RUNNING`,
`GENERATION_UNCOLLECTED`, and `WAIT_LIMIT`. `GENERATION_ABSENT` and
`GENERATION_EXPIRED` send the person to the Dreamina projects page, where the
canvas holds the output if the generation finished. No message prints a
canvas or submit ID.

This step adds the two messages 08 leaves to it, for a node with nothing to
collect and for a label that matches no record, to that module, in ASCII
order and in `__all__`:

| Constant             | Code            | Text |
| -------------------- | --------------- | ---- |
| `GENERATIONS_EMPTY`  | `INVALID_INPUT` | `No generation is recorded on this server. A paid Dreamina node records each run Dreamina accepts, and it stays listed here until its outputs are collected.` |
| `GENERATION_UNKNOWN` | `INVALID_INPUT` | `This generation is not recorded on this server, or it was already collected. Press R to list the generations recorded here, then choose one.` |

`GENERATIONS_EMPTY`, with an S, is the empty list. 08's `GENERATION_EMPTY`
is a run that finished with no output.

## Step 2: Generation: Download

Create `src/nodes/download.py` with the docstring "Collect a recorded
Dreamina generation that kept running after a cancel, a restart, or a
timeout.", ported from `F/src/nodes/download.py`.

```python
_REFERENCES = io.Custom(SOCKET_TYPES["REFERENCES"])
# Every output of every paid node, in the order the nodes list them; Generation: Download fills whichever the run made.
_OUTPUTS = (
    io.Image.Output("images", display_name="images", is_output_list=True),
    io.Video.Output("video", display_name="video", is_output_list=True),
    io.Audio.Output("audio", display_name="audio", is_output_list=True),
    _REFERENCES.Output("references", display_name="references"),
    io.String.Output("result", display_name="result"),
)


class GenerationDownload(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id=f"{NODE_PREFIX}{cls.__name__}",
            display_name="Generation: Download",
            category=MENUS["SHARED"],
            description="Collect a Dreamina generation that kept running after a cancel, a restart, or a timeout. It "
            "bills nothing.",
            inputs=[
                io.Combo.Input(
                    "generation",
                    options=list_generation_labels(get_runtime().generations),
                    tooltip="A generation recorded on this server. Press R to list generations recorded later.",
                )
            ],
            outputs=list(_OUTPUTS),
            hidden=[io.Hidden.unique_id],
        )
```

The input is named `generation`, the thing it chooses, as F's `request` is.
It sets no CLI flag. `hidden` gives the node ID for the progress bar.

`validate_inputs(cls, **inputs: object) -> bool | str` (`@classmethod`,
`@override`) returns `True`, with F's docstring reason: ComfyUI skips its own
list check only for inputs the validator takes as extra keywords, and a run
recorded after the definitions were built must pass. The quality tooling's
host-hook exemption covers its one statement.

`execute(cls, *, generation: str = "") -> io.NodeOutput` (async, with F's
pyright reason comment) returns
`await wait_for_run(asyncio.create_task(_download_generation(generation, cls.hidden.unique_id)))`,
so ComfyUI's cancel stops the wait and keeps the record.

The private `_download_generation(label: str, node_id: str | None)`:

1. `runtime = get_runtime()`.
1. An empty `label`: when `await asyncio.to_thread(runtime.generations.list_records)`
   is empty, raise `DreaminaError(ErrorCode.INVALID_INPUT,
   GENERATIONS_EMPTY)`. ComfyUI gives an empty text when the dropdown has no
   options.
1. `record = await asyncio.to_thread(runtime.generations.find_record, label)`.
   A label that matches no record, empty or not, raises `GENERATION_UNKNOWN`.
1. `operation = CollectOperation(record, runtime.generations,
   runtime.canvas)`, with no deadline, so the wait starts its own request
   timeout, and no request ID.
1. Return `await send_run(operation, partial(build_node_outputs,
   output_ids=tuple(output.id for output in _OUTPUTS)), node_id)`.

What happens in each case, all through 08's `CollectOperation`:

| Case | What happens |
| ---- | ------------ |
| The generation finished with at least one successful resource | `node show` reads the node; every successful resource of the record's submit ID is downloaded and checked; the outputs are built; the record is deleted |
| It is still running (`operation wait` exits 20) | The wait goes on, slice by slice, until a terminal state or the request timeout. On a timeout, `WAIT_LIMIT`, and the record stays |
| It ended with `submissionError`, or with no successful resource | `GENERATION_FAILED` or `GENERATION_EMPTY`; the record is deleted, since nothing is left to collect |
| `submission.state` is `absent` | `GENERATION_ABSENT`; the record is deleted |
| The record is older than `RECORD_RETENTION_SECONDS` | `GENERATION_EXPIRED`; the record is deleted with no CLI call |
| The node is no longer on the canvas | `GENERATION_GONE`; the record is deleted |
| A read or a download fails, or the person signed out | `GENERATION_UNCOLLECTED` with the failure's own message; the record stays, so Generation: Download can collect it again |
| The person cancels | `GENERATION_KEEPS_RUNNING`; the wait stops, the record stays, and nothing is sent to Dreamina |
| Another node collects the same record first | The second delete finds nothing to delete; each node returns what it downloaded |

`__all__`: `GenerationDownload`.

## Step 3: What fills each output

08's `build_node_outputs`, with this node's output IDs, in a worker thread:

1. `images`: every downloaded image, one `[1, H, W, 3]` tensor each, through
   07's `decode_images`.
1. `video`: every downloaded video, through 07's `decode_video`.
1. `audio`: every downloaded audio file, through 07's `decode_audio`.
1. `references`: what the generation made, by the paid nodes' rule: its node
   for one output, each resource for several. An upscale's record gives its
   new node.
1. `result`: the node as `node show` returns it, with the canvas link, as
   JSON.
1. Each output with nothing in it is `ExecutionBlocker(None)`.

## Step 4: Register

1. In `src/nodes/__init__.py`, import `GenerationDownload` and add it to
   `NODE_TYPES` right before `ModelInfo`
   ([04-architecture.md](04-architecture.md#srcnodes)). With Video:
   Generate, added in the same milestone, `NODE_TYPES` is then
   `(ImageGenerate, ImageUpscale, VideoGenerate, AudioGenerate,
   GenerationDownload, ModelInfo)`.
1. `DreaminaGenerationDownload` matches none of
   [04-architecture.md](04-architecture.md#ids-other-packs-use).
1. `quality/config/repository/functions.json` needs no new entry: the class
   is named by `NODE_TYPES`.

## Step 5: Help page

Create `web/docs/DreaminaGenerationDownload.md`. Its reference is F's
`FalRequestDownload.md` (37 lines).

```markdown
# Generation: Download

Downloads what Dreamina made for a run after the run stopped: you canceled
it, ComfyUI restarted, or it took longer than the request timeout. Dreamina
keeps working on a run it accepted, and bills it. This node bills nothing.

## Inputs

| Input        | What it takes                                                                                     |
| ------------ | ------------------------------------------------------------------------------------------------- |
| `generation` | A run started on this server, shown as the start of its ID, its model, and its start time in UTC. |

## Outputs

| Output       | What it carries                                        |
| ------------ | ------------------------------------------------------ |
| `images`     | Every image the run made.                              |
| `video`      | Every video the run made.                              |
| `audio`      | Every audio file the run made.                         |
| `references` | What the run made, for the next Dreamina node.         |
| `result`     | The run's canvas node as Dreamina returns it, as JSON. |

## Use

1. Choose the run in `generation`. Press R to list runs started after the
   page loaded.
2. Connect the output you need, such as `video` to **Save Video**.
3. Select **Run**.

A run leaves the list once its outputs are downloaded, or when Dreamina no
longer has it. An upscale shows `upscale` as its model. Outputs the run did
not make stop the nodes connected to them. Example:
**video-04-recover-a-video**.

[Dreamina Canvas CLI](https://dreamina.capcut.com/canvas-cli)
```

In the same milestone, Image: Upscale's help page gets its last sentence,
"Collect it with **Generation: Download**."
([12-node-upscale.md](12-node-upscale.md#step-6-help-page)).

## Step 6: README row and examples

The README node table row ([18-documentation.md](18-documentation.md)),
after Element: Add's place in `NODE_TYPES` order (Element: Add's row arrives
later, above it):

| Node | What it does | Paid |
| ---- | ------------ | ---- |
| [Generation: Download](web/docs/DreaminaGenerationDownload.md) | Downloads what Dreamina made for a run after the run stopped. | No |

The README example table row, in this milestone, after video-02's:

| Workflow | Input |
| -------- | ----- |
| [Video: Recover a Video](example_workflows/video-04-recover-a-video.json) | A video left running |

### The recover note

Every step that runs a video ends its note with `RECOVER_NOTE`, and Image:
Upscale's step with `UPSCALE_RECOVER_NOTE`, both in 17's
`scripts/workflows/descriptions/notes.py`, as F's steps end with F's. The
text follows Dreamina's behavior, not fal's: there is no cancel, so a
canceled run is always made and billed. 17's constants, which this
milestone completes:

```python
CANCEL_NOTE = "A cancel does not stop a video Dreamina has accepted. It keeps running and is billed."
RECOVER_NOTE = CANCEL_NOTE + " Collect it with **Generation: Download** in **video-04-recover-a-video**."
```

`UPSCALE_RECOVER_NOTE` gets its last sentence, "Collect it with
**Generation: Download**.", in this milestone, when the node ships. Runs V-4
and D-1 check the sentences against a live cancel. If Dreamina behaves
differently, 17 rewrites them to match the runs, as B and F rewrote theirs.

### The example

The example is 17's `video-04-recover-a-video`, which owns its layout, notes,
and save name. What this plan asks of it:

| Slug | What it shows | Nodes and settings this plan asks for |
| ---- | ------------- | ------------------------------------- |
| `video-04-recover-a-video` | Collect a video run after a cancel, a timeout, or a restart, without paying again | **Collect**: **Generation: Download** with `generation` empty → **Save Video** `video/dreamina/recovered`. **Shot**: one **Video: Generate** at its starting `model` and `arguments`, with its prompt inside → **Save Video** `video/dreamina/shot`, shipped bypassed. |

- **The paid step ships bypassed, so pressing Run collects and never bills
  again.** This is F's and B's recover pattern: the recover group ships on,
  and the step that would bill again ships off. A person can turn **Shot**
  on with Ctrl+B, run, cancel once **Shot** has started, turn it off again,
  choose the video in **Collect**, and run again, all in one tab.
- **Collect**'s note starts with when to use it, then gives the steps:
  choose the video in `generation`, where each entry shows the start of its
  ID, its model, and its start time in UTC, pressing R to list videos started
  after the page loaded; press **Run**. It ends with what happens to the
  list: a video leaves it once saved, and the node says so when Dreamina no
  longer has the record.

## Step 7: Live checks

Contract runs C-14 and C-16 come first, in Part 1 of
[21-test-runs.md](21-test-runs.md), outside ComfyUI. Run D-1 is listed in
Part 2 and runs after this milestone's commit. It is free: the paid cancel
is 10's run V-4.

| Run | What | Settles | Credits | If it differs |
| --- | ---- | ------- | ------- | ------------- |
| C-14 | A video run sent with `--credit-ceiling`, its first `operation wait` killed; then `operation wait <submitId> --project-id <canvas> --timeout 15s` from a new process until terminal; then `node show` and `resource download` | That a wait resumes from another process; the terminal reply; the video download | 21's `T2V`, counted in Part 3 | 08's wait; 07's download |
| C-16 | `operation status <new uuid4> --project-id <canvas>` | What an unknown submit ID returns (`submission.state` `absent`, or an error and its exit code) | 0 | 08's absent rule; this plan's `GENERATION_ABSENT` case |
| D-1 | Free. First, **Generation: Download** with no records: `GENERATIONS_EMPTY`. Then, after 10's run V-4 (V-1's graph with a new `run_number`, canceled once its record appears in the state folder's `generations/`): press R, choose V-4's record, listed as `<8 characters> · seedance_2.0_mini · <UTC minute>`, and **Run** | The empty-list message; the label; the video saved under `video/dreamina/recovered`; the record deleted; the label gone after R; Dreamina's canvas shows one run, billed once | 0 (V-4 is 10's `VID-D`) | Step 1's lookup; 08's collect; `RECOVER_NOTE` |
| Free | Copy any record file in the state folder's `generations/` folder, give the copy a new `uuid4` as its submit ID and file name, then collect it | `GENERATION_ABSENT` (or C-16's answer), and the copy deleted | 0 | 08's absent rule |
| Free | Set a copied record's time earlier than `RECORD_RETENTION_SECONDS` ago, then collect it | `GENERATION_EXPIRED` with no CLI call, and the copy deleted | 0 | 08's retention rule |
| Optional | Only with the owner's permission to restart ComfyUI: run video-04 with **Shot** turned on, restart ComfyUI while **Shot** waits, then collect | The record outlives the restart | 21's `VID-D` | 08's record handling |

Record each result in [README.md](README.md#changes-made-while-building),
and check each billed run on the `ComfyUI` canvas at dreamina.capcut.com.

## Names this plan uses from other plans

| Name | Owner | Used for |
| ---- | ----- | -------- |
| `NODE_PREFIX`, `MENUS["SHARED"]`, `SOCKET_TYPES["REFERENCES"]`, `NODE_TYPES`, `DreaminaError`, `ErrorCode.INVALID_INPUT`, `get_runtime` (`generations`), the **Request timeout (seconds)** setting | [05-foundation.md](05-foundation.md) | Names, errors, the runtime |
| `download_resources`, `decode_images`, `decode_video`, `decode_audio`, `Reference` | [07-media.md](07-media.md) | Downloads through `CollectOperation`, decoding through `build_node_outputs` |
| `GenerationStore` (`list_records`, `_build_label`, and `find_record`, added here), `GenerationRecord`, `list_generation_labels`, `LABEL_SEPARATOR`, `LABEL_CHARACTERS`, `RECORD_RETENTION_SECONDS`, `CanvasStore`, `CollectOperation`, `send_run`, `wait_for_run`, `build_node_outputs`, `src/config/messages/generations.py` and its messages, the allowlist entry for `list_generation_labels` | [08-runs.md](08-runs.md) | Records, collecting, outputs |
| `VideoGenerate`, runs V-1 and V-4 | [10-node-video.md](10-node-video.md) | video-04's steps and run D-1 |
| `UPSCALE_MODEL` | [12-node-upscale.md](12-node-upscale.md) | An upscale's label |
| `video-04-recover-a-video`, `CANCEL_NOTE`, `RECOVER_NOTE`, `UPSCALE_RECOVER_NOTE` | [17-scripts-and-workflows.md](17-scripts-and-workflows.md) | The example and every video and upscale step's note |
| Runs C-14, C-16, V-4, and D-1 | [21-test-runs.md](21-test-runs.md) | The live checks |
