# Upscale Node

This plan builds **Image: Upscale** (`ImageUpscale`), the paid node that
makes images larger and sharper with Dreamina's own upscale command,
`node upscale image`. It takes no model. It starts from image nodes on the
person's canvas: the outputs of **Image: Generate**, which it uses where they
are, and ComfyUI images, which it uploads and imports as image nodes first.

The shared machinery is in other plans:

- [07-media.md](07-media.md): encoding, uploads, references, downloads, and
  decoding;
- [08-runs.md](08-runs.md): the CLI runner, the failure map, the version gate,
  the canvas, generation records, the wait, collecting, and the paid node
  base;
- [06-model-check.md](06-model-check.md): the shared inputs and the JSON read
  of `arguments`.

This plan owns `src/dreamina/upscale.py`, `src/nodes/upscale.py`, the
upscale's constants and messages, its help page, its README row, the node
settings of its example, and its first live run. The facts are from the CLI's
`schema` for release 1.0.3 (`node upscale image`, `node create image`),
[02-dreamina-contract.md](02-dreamina-contract.md#image-upscale), and
[research/cli.md](research/cli.md#image-upscale), read on 2026-10-16.

It ships in the **Upscale** milestone, after the Image milestone, because its
example upscales an image that Image: Generate made
([README.md](README.md#build-order)). Commit:
`feat(nodes): add the upscale node`.

## Contents

- [Decisions](#decisions)
- [If imported nodes cannot be upscaled](#if-imported-nodes-cannot-be-upscaled)
- [Step 1: Constants, records, and messages](#step-1-constants-records-and-messages)
- [Step 2: The upscale operation](#step-2-the-upscale-operation)
- [Step 3: Image: Upscale](#step-3-image-upscale)
- [Step 4: What fills each output](#step-4-what-fills-each-output)
- [Step 5: Register](#step-5-register)
- [Step 6: Help page](#step-6-help-page)
- [Step 7: README row and examples](#step-7-readme-row-and-examples)
- [Step 8: Live checks](#step-8-live-checks)
- [Names this plan uses from other plans](#names-this-plan-uses-from-other-plans)

## Decisions

| Question | Decision | Why |
| -------- | -------- | --- |
| Why a node of its own? | Dreamina's upscale is its own command. It takes no model, has its own approval scope, and starts from existing image nodes, not from a prompt. | [01-decisions.md](01-decisions.md#the-nodes); the skill: "`node upscale image` operates on existing successful image nodes" (`references/credits-and-hitl.md`). |
| Which sources? | `references` items whose media is `image` and whose origin is `node`, used as they are, with no upload. ComfyUI images, uploaded and imported as image nodes. At least one source in all, and at most the schema's maximum (20 in 1.0.3). | `--node-id` takes "1..20 unique canonical source Node IDs; each must resolve to one eligible successful image" (schema). |
| Why import a ComfyUI image? | `--node-id` takes only canvas node IDs, and an upload is a resource. `node create image --resource-id <uuid> --import-kind local_upload --submit-id <uuid> --title "Image: Upscale"` makes the upload an image node, for free. | The skill: imports "take the save-only path but still need a submission identity"; "this is the only case where `--submit-id` works without `--run`" (`references/identity-and-references.md#upload-material-identity`). Part 0 confirmed the imported node can be upscaled, and that the import needs `--title`. |
| A reference that is one output of a multi-output run | Refused before anything is sent, with the fix: connect that node's `images` output to `images`. | Such a reference is a resource (`res:`), and `--node-id` takes no resource. Importing a generated resource as `local_upload` is not documented. |
| An Element, a video, or audio in `references` | Refused before anything is sent. | Only images can be upscaled. |
| What goes in `arguments`? | Exactly the schema's own flags `mode`, `resolution`, and `detail`, under those names. Each value is checked against the flag's constraints in the live `schema`, read once per process by `validate_cli`. The mode rules (pro needs `resolution`; normal takes neither `resolution` nor `detail`) come from the same schema text and are kept in `UPSCALE_MODES`. | The owner's rule: an input that sets a request field takes the field's exact name and the API's own values. Checking first refuses a bad value before any upload or import, which would leave nodes on the canvas, and also when the workflow is queued. |
| The starting `arguments` | `{"resolution": "2K"}`. | The CLI's default mode is `pro`, which "requires `--resolution`" (schema). Empty `arguments` would be refused. 2K is the smallest target ([research/catalog.md](research/catalog.md#defaults)). |
| The starting `credit_ceiling` | 10: the quote Part 0 of [21-test-runs.md](21-test-runs.md) measured on 2026-10-17 for one 2K `pro` upscale (2 credits), rounded up to the next multiple of 10, in `UPSCALE_DEFAULTS["CREDIT_CEILING"]`. The same run found `normal` upscales free, 4K `pro` 4 credits, and 8K `pro` 8. | [01-decisions.md](01-decisions.md#credits): the default ceiling makes the default work. |
| One call or one per image? | One `node upscale image` call for every source, with one submit ID per source in the same order, and one `--credit-ceiling` for the whole batch. | The schema: "Approved credit ceiling for the whole batch"; the skill: "supply one `--submit-id` per `--node-id`". |
| Is the call protected from a cancel? | Yes, as the run call is: a cancel waits for the call to return, so an upscale Dreamina accepted is always recorded. | [01-decisions.md](01-decisions.md#paid-runs). |
| Records | One `GenerationRecord` per accepted source, with kind `image`, model `upscale`, the new node's ID, and the source's node ID, saved before the first wait. | **Generation: Download** collects an upscale left running, as it collects a generation. |
| A source Dreamina refuses in an accepted batch | The accepted sources are recorded first. Then the node stops with `UPSCALE_PARTLY_REFUSED`, which names the refused image and says the others keep running and are billed. | The skill: "One failed item must not erase the identities or credit facts of accepted items." The outputs list one image per source, so a gap cannot be filled. |
| Waiting and downloading | Each record is collected in source order by 08's `CollectOperation`: the wait, `node show`, the downloads, then the record's deletion. | One implementation of collecting, as F's `QueueOperation` reuses `CollectOperation`. |
| Cancel | As every run: Dreamina has no cancel. A cancel stops the wait, the records stay, and 08's `GENERATION_KEEPS_RUNNING` says the upscale keeps running and is billed. | [02-dreamina-contract.md](02-dreamina-contract.md#waiting-and-recovery). |
| `--title`, `--wait`, `--dry-run`, `--credit-token` | Never sent. | Empty sends nothing; the pack waits with `operation wait` and approves with the ceiling. |

## If imported nodes cannot be upscaled

Part 0 on 2026-10-17 settled it: an imported upload is an eligible source.
A `normal` upscale of an imported 1280×720 image ran free and returned a
2560×1440 PNG ([02-dreamina-contract.md](02-dreamina-contract.md#results-of-the-contract-runs)).
This section stays only in case a later CLI release changes it. If it does:

1. Image: Upscale takes only `references`. The `images` input, the import
   step (Step 2, step 7), `UPSCALE_IMPORT_KIND`, and the `images` rows of the
   tooltip, help page, and `UPSCALE_SOURCE_EMPTY` are left out.
1. image-03 feeds the upscale from **Image: Generate**'s `references`, as it
   does already.
1. The change is recorded in the README's changes table, and
   [01-decisions.md](01-decisions.md#the-inputs-of-a-paid-node) is corrected.

## Step 1: Constants, records, and messages

### Constants

Add to `src/config/generations.py` ([08-runs.md](08-runs.md) creates it, and
[04-architecture.md](04-architecture.md#srcconfig) lists `UPSCALE_FLAGS`
there), each with its comment directly above it:

```python
# The arguments keys Image: Upscale takes: node upscale image's own flags. Their allowed values, ranges, and defaults
# are read from the CLI's schema each process.
UPSCALE_FLAGS = ("mode", "resolution", "detail")

# What each upscale mode needs and takes besides mode, as the schema's constraints state it: pro needs resolution and
# takes detail; normal takes neither.
UPSCALE_MODES = {
    "pro": {"REQUIRED": ("resolution",), "TAKEN": ("resolution", "detail")},
    "normal": {"REQUIRED": (), "TAKEN": ()},
}

# The model name an upscale's record carries, so Generation: Download labels it.
UPSCALE_MODEL = "upscale"

# How node create image registers an uploaded resource as an image node's output.
UPSCALE_IMPORT_KIND = "local_upload"

# How the schema writes a flag's rule: the text before the first ";" of constraints lists the allowed values split by
# "|", or gives a whole-number range such as "1..100".
SCHEMA_CONSTRAINTS = {"PART": ";", "CHOICE": "|"}
```

A mode the live schema lists but `UPSCALE_MODES` does not is sent with no
rule of its own, and the CLI checks it for free.

Add to `src/config/patterns.py` ([05-foundation.md](05-foundation.md)):

```python
# A whole-number range at the start of a schema constraint, such as "1..100" or "1..20 unique canonical source Node IDs".
SCHEMA_RANGE_PATTERN = r"^(\d+)\.\.(\d+)\b"
```

Add `UPSCALE_DEFAULTS` to `src/config/generations.py` as well, next to the
other upscale constants (06's `DEFAULT_ARGUMENTS` and `DEFAULT_CEILINGS` are
keyed by model kind, and the upscale has no model), with the comment
`# Image: Upscale's starting values; the ceiling is Part 0's quote for one 2K pro upscale, rounded up to the next 10.`
directly above it:

| Key              | Value                                                                                                   |
| ---------------- | ------------------------------------------------------------------------------------------------------- |
| `CREDIT_CEILING` | The quote Part 0 of [21-test-runs.md](21-test-runs.md) measures for one 2K `pro` upscale, rounded up to the next multiple of 10, as an integer. The number is written in from that run. |
| `ARGUMENTS`      | `'{"resolution": "2K"}'`                                                                                |

[01-decisions.md](01-decisions.md#credits) sets the same rule for every paid
node's ceiling, and the README's changes table records the number.

08's `REQUIRED_COMMANDS` (`src/config/dreamina.py`) already lists every
command and flag this plan sends: `"node upscale image"` with `project-id`,
`node-id`, `submit-id`, `mode`, `resolution`, `detail`, and `credit-ceiling`,
and `"node create image"` with `resource-id`, `import-kind`, and `submit-id`.

### The schema's flags

The version gate reads the CLI's `schema` once per process
([08-runs.md](08-runs.md#step-6-the-version-gate)) but keeps only each
command's flag names, and `validate_cli()` returns nothing. The upscale needs
the rule of three flags, so this step extends the gate, with one read of the
schema for both uses:

1. `SchemaFlag` in `src/types/replies.py` gains the three schema fields 08
   leaves undeclared that the upscale reads: `type: str = ""`,
   `default: str | None = None`, and `constraints: str = ""`.
1. `src/dreamina/contract.py` keeps, for each binary whose contract passed,
   each `REQUIRED_COMMANDS` path's flags by name, beside `_VALIDATED`:
   `_FLAGS: dict[str, dict[str, dict[str, SchemaFlag]]]`, keyed by binary
   path, then command path. `_read_contract` fills it from the tree it already
   walks, and `reset_cli_validation()` clears it with `_VALIDATED`.
1. A new public `read_command_flags(path: str) -> Mapping[str, SchemaFlag]`
   returns the flags of one command for the binary `find_binary()` gives.
   It is called after `validate_cli()`, so the entry exists. Its docstring
   says so.

`quality/config/repository/functions.json` needs no entry for it: the node
module and `src/dreamina/upscale.py` call it in this milestone.

### Records

Add to `src/types/generations.py` ([08-runs.md](08-runs.md)):

```python
@dataclass(frozen=True, slots=True)
class UpscaleRequest:
    """One upscale a node asks for, as its inputs came; send checks it against the CLI's schema.

    Attributes:
        images: The ComfyUI images to upload and import, one per frame, in order.
        references: The connected references, in socket order.
        credit_ceiling: The most credits the whole batch may cost.
        arguments: The arguments input's JSON text.

    """

    images: tuple[LocalMedia, ...]
    references: tuple[Reference, ...]
    credit_ceiling: int
    arguments: str
```

Add to `src/types/replies.py` the two records 08's table leaves to this
plan, and the item error it lets this plan declare
([08-runs.md](08-runs.md#step-8-run-reply-records)):

| Record         | Fields |
| -------------- | ------ |
| `UpscaleError` | `status_code: int \| None = Field(default=None, alias="serviceCode")`, `message: str = ""` |
| `UpscaleItem`  | `source_node_id: str`, `submit_id: str`, `node_id: str \| None = None`, `resource_ids: tuple[str, ...] = ()`, `state: str`, `error: UpscaleError \| None = None` |
| `UpscaleReply` | `items: tuple[UpscaleItem, ...] = ()` |

The import's reply (`node`, `mutation`) has the same shape as the Element
reply, `node: NodeView`, so it is read with 08's `ElementReply`, one record
per reply shape. `ElementReply` arrives in this milestone, before
[13-node-element.md](13-node-element.md), with the fields 08 gives it. The
pack reads only `node.node_id`.

08's `GenerationRecord` already carries `source_node_id`, and requires
`mode`: an upscale's record sets `mode` to `arguments`' `mode`, or else the
`mode` flag's schema `default` (`pro` in 1.0.3), so the record says which
upscale ran.

### Shared JSON read

06's public `parse_arguments(text)` (`src/dreamina/arguments.py`, F's
`_parse_arguments_text` renamed) reads the `arguments` box as one JSON
object: blank text is an empty object, bad JSON is `ARGUMENTS_INVALID`, and
another JSON value is `ARGUMENTS_SHAPE`. Image: Upscale reads its box with
it, so the JSON read has one implementation.

### Messages

Add to `src/config/messages/inputs.py` ([06-model-check.md](06-model-check.md)
creates it):

| Constant                     | Text |
| ---------------------------- | ---- |
| `UPSCALE_SOURCE_EMPTY`       | `Connect what to upscale: ComfyUI images to images, or the references output of Image: Generate to references.` |
| `UPSCALE_SOURCE_LIMIT`       | `Connect at most {maximum} images to Image: Upscale. It has {count}.` |
| `UPSCALE_REFERENCE_MEDIA`    | `Image: Upscale takes only images. Connect the references output of Image: Generate or Image: Upscale. An Element, a video, or audio cannot be upscaled.` |
| `UPSCALE_REFERENCE_RESOURCE` | `One of the references is a single image of a run that made several, and Image: Upscale takes whole canvas nodes only. Connect that node's images output to images instead.` |
| `UPSCALE_ARGUMENT_KEY`       | `Image: Upscale takes only {keys} in arguments, not {key}.` |
| `UPSCALE_ARGUMENT_CHOICE`    | `Set {key} in arguments to one of {values}.` |
| `UPSCALE_ARGUMENT_RANGE`     | `Set {key} in arguments to a whole number from {minimum} to {maximum}.` |
| `UPSCALE_FLAG_NEEDED`        | `Add {key} to arguments: the {mode} mode needs it. Choose one of {values}.` |
| `UPSCALE_MODE_FLAG`          | `Leave {key} out of arguments when mode is {mode}: that mode does not take it.` |

Add to `src/config/messages/run.py` ([08-runs.md](08-runs.md) creates it):

| Constant                 | Text |
| ------------------------ | ---- |
| `UPSCALE_REFUSED`        | `Dreamina refused to upscale image {number}: {reason}` |
| `UPSCALE_PARTLY_REFUSED` | `Dreamina refused to upscale image {number}: {reason} The other images are being upscaled and billed. Collect them with Generation: Download.` |

`{keys}` and `{values}` are joined with ", ". `{number}` counts the sources
from 1, `references` first. `{reason}` is the item's `error.message`, cleaned
with 08's `sanitize_reason`, or 08's `STATUS_CODE_REASON` when the message
is empty. `UPSCALE_PARTLY_REFUSED` names Generation: Download in code before
that node ships, as 08's cancel and timeout messages do. A help page names it
only from the Video and downloads milestone.

The ceiling refusal is 08's: `build_failure(result,
credit_ceiling=request.credit_ceiling)` turns exit 10 into `CEILING_TOO_LOW`
with Dreamina's `creditConfirmation.minimumCreditCeiling`, or its
unknown-price message when the field is absent. Run C-13 records the
upscale's exit 10 reply. If it carries the quote only as `totalMaxCredits`,
08's map reads that field for this command, and
[02-dreamina-contract.md](02-dreamina-contract.md#image-upscale) records it.

## Step 2: The upscale operation

Create `src/dreamina/upscale.py` with the docstring "Upscale image nodes with
Dreamina's own command: import ComfyUI images, send one paid call for every
source, record each accepted source, and collect it.".

### `parse_upscale_arguments`

```python
def parse_upscale_arguments(text: str, flags: Mapping[str, SchemaFlag]) -> tuple[str, ...]:
```

It returns the `--flag value` pairs to send, and raises
`DreaminaError(ErrorCode.INVALID_INPUT, …)` for each refusal. `flags` is
`read_command_flags("node upscale image")`, after `validate_cli()`. Both the
node's `validate_inputs` and the operation call it.

1. `parse_arguments(text)` (06) reads the object. Blank text is `{}`.
1. A key not in `UPSCALE_FLAGS` raises `UPSCALE_ARGUMENT_KEY` with `key` and
   `keys=", ".join(UPSCALE_FLAGS)`.
1. Each key's value is checked against its flag's rule. The private
   `_read_rule(flag)` takes the text before the first
   `SCHEMA_CONSTRAINTS["PART"]` of `flag.constraints`:
   - `SCHEMA_RANGE_PATTERN` matches: a whole-number range;
   - it holds `SCHEMA_CONSTRAINTS["CHOICE"]`: the allowed values, split and
     stripped;
   - otherwise no rule.

   In 1.0.3 this gives `mode` `normal`, `pro`; `resolution` `2K`, `4K`, `8K`;
   and `detail` 1 to 100. A flag whose `type` is `integer` takes a JSON
   integer that is not a boolean, within its range, else
   `UPSCALE_ARGUMENT_RANGE`. Any other flag takes a JSON string among its
   values, else `UPSCALE_ARGUMENT_CHOICE`. Values are compared exactly, as the
   schema writes them. A flag with no rule sends its value as written, and the
   CLI checks it.
1. The mode is `arguments["mode"]`, or else the `mode` flag's schema
   `default` (`pro` in 1.0.3). With `UPSCALE_MODES[mode]`:
   - each `REQUIRED` key missing from `arguments` raises
     `UPSCALE_FLAG_NEEDED` with `key`, `mode`, and that flag's values;
   - each key of `arguments` other than `mode` that is not `TAKEN` raises
     `UPSCALE_MODE_FLAG` with `key` and `mode`.
1. It returns `("--mode", …, "--resolution", …, "--detail", …)` for the keys
   that `arguments` sets, in `UPSCALE_FLAGS` order, each value as text. A key
   left out sends nothing, so the CLI's default applies.

`SchemaFlag` (with the fields Step 1 adds) and `read_command_flags` are the
version gate's, so the rules come from the same schema read that checks the
command exists.

### `UpscaleOperation`

`UpscaleOperation` implements 08's `Operation[tuple[GenerationResult, ...]]`:

```python
class UpscaleOperation:
    def __init__(
        self,
        request: UpscaleRequest,
        generations: GenerationStore,
        canvas: CanvasStore,
        encode: Callable[[LocalMedia, Path], Path],
    ) -> None: ...
```

`encode` is 07's `encode_local_file`, passed in by the node, because this
package may not import ComfyUI. `validate(settings)` accepts every request:
each check needs the schema, which `send` reads. It gets the permanent
`quality/config/repository/functions.json` allowlist entry F's
`QueueOperation.validate` has: "The run wrapper calls it through the
Operation protocol."

`send(configuration, progress)` sets `deadline = time.monotonic() +
configuration.settings.request_timeout_seconds` first. Every CLI call gets
`deadline - time.monotonic()` seconds, and 07's and 08's calls take the
deadline itself, so one request timeout bounds the whole upscale, from the
first upload to the last download. Every refusal comes before anything is
uploaded or paid:

1. `validate_cli()`, then `flags = read_command_flags("node upscale image")`.
1. `parse_upscale_arguments(request.arguments, flags)` gives the flag pairs.
1. Each reference whose `media` is not `image` raises
   `UPSCALE_REFERENCE_MEDIA`. Each image reference whose `origin` is
   `resource` raises `UPSCALE_REFERENCE_RESOURCE`.
1. The sources are the references, then the images, in order. None raises
   `UPSCALE_SOURCE_EMPTY`. More than the `--node-id` flag's range maximum
   (`_read_rule`, 20 in 1.0.3) raises `UPSCALE_SOURCE_LIMIT` with `maximum`
   and `count`.
1. Progress `CHECKED`.
1. The canvas comes from 08's canvas lookup, as `GenerationOperation` gets
   it: `find_canvas(self.canvas)`, or `create_canvas(self.canvas)` when the
   saved canvas is missing or no longer listed. Its `project_id` is the
   canvas ID every call below names.
1. 07's `send_media(project_id, request.images, self.encode,
   configuration.settings, deadline)` uploads every image and returns one
   resource `Reference` per image, in order. Then, for each in order, one free
   call through `send_command`:

   ```text
   node create image --project-id <canvas> --resource-id <reference.value>
     --import-kind local_upload --submit-id <new uuid4> --title "Image: Upscale"
   ```

   `--title` is required: Part 0 found an import refused without one
   (`cli.invalid_node_input`, `validation.fieldPath` `title`). The title is the
   node's display name, so the person sees on the canvas which node imported
   the image.

   A failure goes through `build_failure`. The reply, read as `ElementReply`,
   gives the source node, `node.node_id`. The pack never retries the import:
   a lost reply is reported, and the import costs nothing. Two images with
   the same bytes share one upload and are imported as two nodes, each its
   own source.
1. Progress `UPLOADED`.
1. One new `uuid4` submit ID per source, in source order. Then one call
   through `send_command`:

   ```text
   node upscale image --project-id <canvas>
     --node-id <source 1> --node-id <source 2> …
     --submit-id <uuid 1> --submit-id <uuid 2> …
     [--mode <m>] [--resolution <r>] [--detail <d>]
     --credit-ceiling <credit_ceiling>
   ```

   A reference source is sent as its bare `Reference.value`, the `node_…` ID.
   The private `_send_upscale(arguments, sources, submit_ids, project_id,
   mode)` sends the call once and saves the records, as 08's `_send_run`
   does for a run. It runs in its own task, awaited with
   `wait_until_settled`, so a cancel waits for its answer and an accepted
   upscale is always recorded. The call gets `CALL_SECONDS["RUN"]`, not what
   is left of the deadline, as the run call does. The answers:
   - **Exit 0.** Read `UpscaleReply`. Its `items` are matched to the sources
     by `source_node_id`, so the order follows the sources whatever order the
     reply uses. An item is accepted when it has a `node_id` and no `error`.
   - **Exit 10.** `build_failure(result, credit_ceiling=…)`: `CEILING_TOO_LOW`
     with Dreamina's quote. Nothing is billed and no output node exists; the
     imported nodes stay on the canvas, free.
   - **Exit 20, or `error.local_storage.submission_phase` `after_submit`.**
     The upscale was accepted. Each `partial.items` entry with a `node_id`
     is an accepted source, matched by `source_node_id`. None with a
     `node_id` raises 08's `RUN_UNRECORDED`.
   - **A `TRANSPORT` error from `send_command`, or an exit 0 payload that is
     not an `UpscaleReply`.** No node ID is known, so nothing can be
     recorded: 08's `RUN_UNCERTAIN`, which sends the person to the canvas.
     The call is never sent again.
   - **Any other failure:** `build_failure(result, credit_ceiling=…)`.

   Each accepted source is saved as a `GenerationRecord` before any wait:
   `submit_id`, `project_id`, the new `node_id`, kind `image`, model
   `UPSCALE_MODEL`, the mode, `submitted_at`, and `source_node_id`.
1. Progress `ACCEPTED`.
1. If a cancel arrived during the call, `DreaminaError(ErrorCode.INTERRUPTED,
   GENERATION_KEEPS_RUNNING)` is raised now, and the records stay.
1. If an item was refused, the first refused item's position and cleaned
   reason raise `UPSCALE_PARTLY_REFUSED` when another item was accepted, else
   `UPSCALE_REFUSED`.
1. Progress `RUNNING`. For each record, in source order,
   `CollectOperation(record, self.generations, self.canvas,
   deadline).send(configuration, None)` (08) waits with
   `wait_for_operation`, reads the node with `node show`, downloads its
   resources with 07's `download_resources`, deletes the record, and returns
   a `GenerationResult`. Progress `None` keeps the bar from moving back for
   each source. A cancel during a wait is 08's `GENERATION_KEEPS_RUNNING`.
1. Progress `DOWNLOADED`. Return the results in source order.

On a timeout (08's `WAIT_LIMIT`) or a cancel, the records not yet collected
stay for Generation: Download.

`wait_until_settled(task: asyncio.Task[T]) -> bool` is 08's public function
in `src/dreamina/operation.py`, made public there for this second caller.
`GenerationOperation`'s run call uses the same function.

`__all__`: `UpscaleOperation`, `parse_upscale_arguments`.

## Step 3: Image: Upscale

Create `src/nodes/upscale.py` with the docstring "Image: Upscale, the paid
node for Dreamina's upscale of image nodes and ComfyUI images." and
`ImageUpscale(PaidNode)`.

```python
_REFERENCES = io.Custom(SOCKET_TYPES["REFERENCES"])
# The node's outputs in order; each label equals its ID.
_OUTPUTS = (
    io.Image.Output("images", display_name="images", is_output_list=True),
    _REFERENCES.Output("references", display_name="references"),
    io.String.Output("result", display_name="result"),
)


class ImageUpscale(PaidNode):
    list_inputs = frozenset({INPUT_NAMES["IMAGES"], INPUT_NAMES["REFERENCES"]})

    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id=f"{NODE_PREFIX}{cls.__name__}",
            display_name="Image: Upscale",
            category=MENUS["IMAGE"],
            description="Make images larger and sharper with Dreamina's upscale.",
            inputs=[
                io.Image.Input(
                    INPUT_NAMES["IMAGES"],
                    optional=True,
                    tooltip="ComfyUI images to upscale. Each is uploaded to your Dreamina canvas first.",
                ),
                _REFERENCES.Input(
                    INPUT_NAMES["REFERENCES"],
                    optional=True,
                    tooltip="Images from Image: Generate or Image: Upscale, upscaled where they are, with no upload. "
                    "They go before images.",
                ),
                io.Int.Input(
                    INPUT_NAMES["CREDIT_CEILING"],
                    default=UPSCALE_DEFAULTS["CREDIT_CEILING"],
                    min=CREDIT_CEILING_RANGE["MIN"],
                    max=CREDIT_CEILING_RANGE["MAX"],
                    tooltip="The most credits this upscale may cost, for all its images together. Above it, "
                    "Dreamina runs nothing and bills nothing.",
                ),
                io.Int.Input(
                    INPUT_NAMES["RUN_NUMBER"],
                    default=RUN_NUMBER["DEFAULT"],
                    min=RUN_NUMBER["MIN"],
                    max=RUN_NUMBER["MAX"],
                    tooltip=TOOLTIPS["RUN_NUMBER"],
                ),
                io.String.Input(
                    INPUT_NAMES["ARGUMENTS"],
                    default=UPSCALE_DEFAULTS["ARGUMENTS"],
                    multiline=True,
                    tooltip='The upscale settings as JSON: mode, resolution, and detail, such as {"resolution": '
                    '"4K"}. The pro mode, the default, needs a resolution.',
                ),
            ],
            outputs=list(_OUTPUTS),
            is_input_list=True,
            hidden=[io.Hidden.unique_id],
        )
```

- `INPUT_NAMES`, `TOOLTIPS["RUN_NUMBER"]`, `RUN_NUMBER`, and
  `CREDIT_CEILING_RANGE` are 06's, in `src/config/inputs.py`, with 06's keys.
- `is_input_list=True`: Image: Generate outputs its images as a list, and
  without input lists ComfyUI would run the node, and bill, once per image.
  `list_inputs` is 08's `PaidNode` rule for the generation nodes: the two
  sockets reach `send` as whole lists, and every other input as its one value.
- The tooltips are the node's own, as F's free nodes keep theirs. Only
  `run_number`'s is shared.

`validate_inputs(cls, arguments: object = None) -> bool | str` (async,
`@override`, with F's pyright reason comment) runs when the workflow is
queued. With input lists, `arguments` arrives as a one-item list. When it
holds one text, the node runs `validate_cli()`, then
`parse_upscale_arguments` on it with `read_command_flags("node upscale
image")`, and returns the refusal's text or `True`. A linked value, `[None]`
until the workflow runs, is checked at run time. ComfyUI skips its own
checks only for the inputs named here, so `credit_ceiling` and `run_number`
keep their range checks.

`send(cls, *, credit_ceiling: int, arguments: str, images: list[torch.Tensor]
| None = None, references: list[tuple[Reference, ...]] | None = None) ->
io.NodeOutput`:

1. `node_id` is `cls.hidden.unique_id`, or `None` when another pack calls the
   class directly, as F's `EndpointNode.send` reads it.
1. `UpscaleRequest`: `images` is 07's `list_local_media(images or (), (), ())`,
   one `LocalMedia` per frame of every connected image batch, in order;
   `references` is every item of every connected tuple, in order.
1. `runtime = get_runtime()`, then `send_run(UpscaleOperation(request,
   runtime.generations, runtime.canvas, encode_local_file),
   _build_upscale_outputs, node_id)`.

`__all__`: `ImageUpscale`.

## Step 4: What fills each output

The private `_build_upscale_outputs(results: Sequence[GenerationResult]) ->
io.NodeOutput`, in `src/nodes/upscale.py`, runs in a worker thread, as every
output builder does ([08-runs.md](08-runs.md)):

1. `images`: 07's `decode_images` over the `content` of each result's
   `OutputFile`s of kind `image`, in source order. Each upscale makes one
   image, so the list holds one `[1, H, W, 3]` tensor per source, each at its
   own size.
1. `references`: one `Reference(origin="node", value=result.record.node_id,
   media="image", title=result.title)` per result, in source order, as 08's
   rule gives a one-output node. The next node uses each new node with no
   download or upload.
1. `result`: `json.dumps([...], indent=2, ensure_ascii=False)` of a list with
   one item per source, in order. Each item is 08's
   `build_result_document(result)`, the document `build_node_outputs` writes
   as one generation's `result`: `{"canvas", "requestId", "node"}` without
   the keys whose value is `None`, the node as `node show` returned it. Both
   builders call the one function in `src/nodes/outputs.py`, so the shape
   has one implementation.
1. An empty list becomes `ExecutionBlocker(None)`. A successful upscale always
   fills all three.

## Step 5: Register

1. In `src/nodes/__init__.py`, import `ImageUpscale` and add it to
   `NODE_TYPES` right after `ImageGenerate`
   ([04-architecture.md](04-architecture.md#srcnodes)). At this milestone
   `NODE_TYPES` is `(ImageGenerate, ImageUpscale)`.
1. `DreaminaImageUpscale` matches none of
   [04-architecture.md](04-architecture.md#ids-other-packs-use).
1. `quality/config/repository/functions.json`: add the
   `UpscaleOperation.validate` entry (Step 2), which
   [03-repository-setup.md](03-repository-setup.md#tooling-that-later-milestones-add)
   lists for this milestone. `parse_upscale_arguments` needs none, since the
   node module calls it. Remove 08's entry for `build_result_document`, whose
   first caller outside its module is this node
   ([08-runs.md](08-runs.md#step-19-allowlist-and-commits)).

## Step 6: Help page

Create `web/docs/DreaminaImageUpscale.md`. Its reference is F's
`FalImageGenerate.md` (44 lines). The last sentence of the cancel paragraph
is added in the Video and downloads milestone, when Generation: Download
ships; until then the paragraph ends after "billed.".

```markdown
# Image: Upscale

Makes images larger and sharper with Dreamina's upscale. It takes the images
another Dreamina node made, or ComfyUI images, which it uploads to your
canvas first. It outputs each upscaled image.

## Inputs

| Input            | What it takes                                                                         |
| ---------------- | ------------------------------------------------------------------------------------- |
| `images`         | ComfyUI images, each uploaded to your Dreamina canvas.                                |
| `references`     | Images from **Image: Generate** or **Image: Upscale**, with no upload. They go first. |
| `credit_ceiling` | The most credits the whole upscale may cost.                                          |
| `run_number`     | Change it to send the same upscale again.                                             |
| `arguments`      | The upscale's settings as JSON: `mode`, `resolution`, and `detail`.                   |

`mode` is `pro`, the default, or `normal`. `pro` needs `resolution`, the
target size: `2K`, `4K`, or `8K`. `detail`, from 1 to 100, sets how much
detail `pro` adds. `normal` takes neither. One upscale takes up to 20 images.
The node checks every setting before it uploads anything.

## Outputs

| Output       | What it carries                                                 |
| ------------ | --------------------------------------------------------------- |
| `images`     | Every upscaled image, one for each image given, in order.       |
| `references` | The upscaled images on your canvas, for the next Dreamina node. |
| `result`     | Each new canvas node as Dreamina returns it, as a JSON list.    |

## Use

1. Connect **Image: Generate**'s `references`, or ComfyUI `images`.
2. Set the target size in `arguments`, such as `{"resolution": "4K"}`.
3. Connect `images` to **Save Image**, and select **Run**.

If the upscale costs more than `credit_ceiling`, Dreamina runs nothing and
bills nothing, and the node shows the price. Dreamina decides whether a
target size fits each image. Once it accepts the upscale, a cancel stops only
the wait: the upscale is still made and billed. Collect it with **Generation:
Download**.

Example: **image-03-upscale-a-poster**.

[Dreamina](https://dreamina.capcut.com/ai-tool/home)
```

## Step 7: README row and examples

The README node table row ([18-documentation.md](18-documentation.md)), after
Image: Generate's:

| Node | What it does | Paid |
| ---- | ------------ | ---- |
| [Image: Upscale](web/docs/DreaminaImageUpscale.md) | Makes images larger and sharper with Dreamina's upscale. | Yes |

The example is [17-scripts-and-workflows.md](17-scripts-and-workflows.md)'s
`image-03-upscale-a-poster`, which owns its slug, layout, notes, prompt, and
save names. What this plan asks of it:

| Slug | What it shows | Nodes and settings this plan asks for |
| ---- | ------------- | ------------------------------------- |
| `image-03-upscale-a-poster` | An image Image: Generate made, upscaled where it is, with no download or upload | **Poster**: **Image: Generate** draws the poster at `2K`. **Enlarge**: **Image: Upscale** with `references` ← Poster's `references` and its starting values: mode `pro`, `arguments` `{"resolution": "2K"}`, and the starting `credit_ceiling` 10, which covers Part 0's quote of 2 credits. **Save Image** `image/dreamina/poster-upscaled`. |

- image-03 keeps the starting `2K`, as every example uses the lowest
  settings, though the poster is already 2K. Dreamina decides whether a
  target size fits its source ("target-vs-source eligibility remains
  server-authoritative", schema), so U-1 and Part 4's run of image-03 check
  that it takes `2K`.
- **Enlarge**'s note ends with 17's `UPSCALE_RECOVER_NOTE`, which ends after
  "is billed." until the Video and downloads milestone adds its last
  sentence, as this help page does.

## Step 8: Live checks

Contract run C-13 comes first, outside ComfyUI, in milestone 4.
[21-test-runs.md](21-test-runs.md) lists run U-1 in Part 2, after this
milestone's commit, with the owner's approval of its credits. The
free checks below go with it. I-1 is 09's first image run, whose outputs come
from ComfyUI's cache for free.

| Run | What | Settles | Credits | If it differs |
| --- | ---- | ------- | ------- | ------------- |
| C-13 | Upload a PNG, import it with `node create image --resource-id … --import-kind local_upload --submit-id …`, then `node upscale image` it at `--credit-ceiling 0`, then at a ceiling that passes | Whether an imported node can be upscaled; the exit 10 reply (`minimumCreditCeiling` or `totalMaxCredits`, `partialData`); the success reply's `items` and their `state` | 21's `UP` | [If imported nodes cannot be upscaled](#if-imported-nodes-cannot-be-upscaled); 08's exit 10 map |
| Free | Queue with `arguments` empty, then `{"mode": "normal", "detail": 70}`, then `{"resolution": "16K"}`, then `{"scale": 2}` | `UPSCALE_FLAG_NEEDED`, `UPSCALE_MODE_FLAG`, `UPSCALE_ARGUMENT_CHOICE`, and `UPSCALE_ARGUMENT_KEY` at queue time, with nothing sent | 0 | Step 2's parse |
| Free | **Load Image** → **Repeat Image Batch** (`amount` 21) → `images` | `UPSCALE_SOURCE_LIMIT` before anything is uploaded | 0 | Step 2's source check |
| Free | `references` ← I-1's `references`, `credit_ceiling` 0 | The ceiling refusal with Dreamina's quote; no output node on the canvas; nothing billed | 0 | 08's exit 10 map for this command |
| U-1 | `images` ← **Load Image** `dreamina-test-apple.png` (the import path), the starting `arguments` `{"resolution": "2K"}`, the default `credit_ceiling` | The upload and the import node on the canvas; the upscale; one image saved; `references` holds the new node; `result` is a one-item list; the record created, then deleted. If the test image is already 2K or larger, whether Dreamina takes a target the size of its source | 21's `UP-D` | A refused target shows `UPSCALE_REFUSED` with Dreamina's reason: record it, and the starting value moves to `4K` with a new ceiling, recorded in the changes table. If C-13 failed, U-1 takes `references` ← I-1's `references` instead |

In the Audio milestone, A-1's `references` connected to Image: Upscale give
`UPSCALE_REFERENCE_MEDIA`, free, from ComfyUI's cache of A-1.

Record each result in [README.md](README.md#changes-made-while-building),
with the credits Dreamina's canvas shows for each run.

## Names this plan uses from other plans

| Name | Owner | Used for |
| ---- | ----- | -------- |
| `NODE_PREFIX`, `MENUS["IMAGE"]`, `SOCKET_TYPES["REFERENCES"]`, `NODE_TYPES`, `DreaminaError`, `ErrorCode.INVALID_INPUT`, `get_runtime` (`generations`, `canvas`), `PROGRESS_STEPS`, `src/config/patterns.py` | [05-foundation.md](05-foundation.md) | Names, errors, the runtime, progress |
| `INPUT_NAMES`, `TOOLTIPS["RUN_NUMBER"]`, `RUN_NUMBER`, `CREDIT_CEILING_RANGE`, `src/config/inputs.py`, `src/config/messages/inputs.py`, `parse_arguments`, `ARGUMENTS_INVALID`, `ARGUMENTS_SHAPE` | [06-model-check.md](06-model-check.md) | The shared inputs and the JSON read |
| `LocalMedia`, `Reference` (`value`), `list_local_media`, `send_media`, `encode_local_file`, `download_resources`, `decode_images`, `OutputFile` | [07-media.md](07-media.md) | Splitting, uploads, references, downloads, decoding |
| `validate_cli`, `read_command_flags` and `SchemaFlag` (extended here), `reset_cli_validation`, `REQUIRED_COMMANDS`, `CALL_SECONDS`, `send_command`, `build_failure`, `CEILING_TOO_LOW`, `RUN_UNCERTAIN`, `RUN_UNRECORDED`, `GENERATION_KEEPS_RUNNING`, `WAIT_LIMIT`, `find_canvas`, `create_canvas`, `CanvasStore`, `wait_for_operation`, `GenerationStore`, `GenerationRecord` (`mode`, `source_node_id`), `GenerationResult`, `CollectOperation`, `Operation`, `wait_until_settled`, `send_run`, `PaidNode` (`list_inputs`, the account cache token), `UpscaleItem`, `UpscaleReply`, `ElementReply`, `NodeView`, `build_node_outputs`, `build_result_document` (its allowlist entry removed here), `src/config/generations.py`, `src/config/messages/run.py`, `sanitize_reason` | [08-runs.md](08-runs.md) | The run, records, collecting, and outputs |
| `ImageGenerate` and its `references` output; run I-1 | [09-node-image.md](09-node-image.md) | The sources of image-03 and U-1 |
| `GenerationDownload` | [14-node-download.md](14-node-download.md) | The help page's last sentence, from the Video and downloads milestone |
| `image-03-upscale-a-poster`, `UPSCALE_RECOVER_NOTE` | [17-scripts-and-workflows.md](17-scripts-and-workflows.md) | The example and its note |
| Part 0's upscale quotes (`UP`, `UP-D`), runs C-13 and U-1 | [21-test-runs.md](21-test-runs.md) | The ceiling default and the live checks |
