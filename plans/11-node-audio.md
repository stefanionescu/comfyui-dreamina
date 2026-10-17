# Audio Node

This plan builds **Audio: Generate** (`AudioGenerate`), the paid node for
every Dreamina model that makes audio: text read aloud in a chosen voice
(`tts`, scenario `text-reading`), speech for a connected picture or audio
clip (`tts`, scenario `omni-dubbing`), and music (`music`). It is one of the
three generation nodes. The shared machinery is in
[06-model-check.md](06-model-check.md), [07-media.md](07-media.md), and
[08-runs.md](08-runs.md), as for [09-node-image.md](09-node-image.md).

**The person types any model name.** Nothing in the code lists or limits
models. The name and every setting are checked against the person's own
Dreamina model list when the workflow is queued and again when the node runs.
The only model name in this node is the starting value of its `model` box,
`seed_audio_v1`, which the person replaces freely
([01-decisions.md](01-decisions.md#how-the-nodes-cover-every-model)).

This plan owns the node's class and outputs, what fills them, the starting
values and the voice they carry, the help page, the README row, the audio
examples' node settings, and the first live runs. It is the counterpart of
`F/plans/11-node-audio.md` in the fal pack
(`F=/Users/dr_stone/Documents/work/comfyui-fal`, commit `cef8b6e`), and ports
`F/src/nodes/audio.py`. The facts are the owner's audio list and voice list
of 2026-10-16 ([research/catalog.md](research/catalog.md#audio-models),
`research/captures/model-list-audio.json`,
`research/captures/voices-seed_audio_v1-page-0.json`). Nothing is built yet.

It ships in the **Audio** milestone, before Video, because audio-02 defines
the host step that video-02 and video-03 place again
([README.md](README.md#build-order)). The same milestone registers Model:
Info with its example, audio-01. Readers: the engineer who writes
`src/nodes/audio.py` and `web/docs/DreaminaAudioGenerate.md`, and the writers
of [17-scripts-and-workflows.md](17-scripts-and-workflows.md) and
[21-test-runs.md](21-test-runs.md).

## Contents

- [Decisions this plan makes](#decisions-this-plan-makes)
- [What Dreamina's audio models look like](#what-dreaminas-audio-models-look-like)
- [Step 1: Audio: Generate](#step-1-audio-generate)
- [Step 2: What fills each output](#step-2-what-fills-each-output)
- [Step 3: Register](#step-3-register)
- [Step 4: Help page](#step-4-help-page)
- [Step 5: README row and examples](#step-5-readme-row-and-examples)
- [Step 6: Live checks](#step-6-live-checks)
- [Names this plan uses from other plans](#names-this-plan-uses-from-other-plans)

## Decisions this plan makes

| Question | Decision | Why |
| -------- | -------- | --- |
| Which models? | Any name in the person's live `model list --type audio`. `seed_audio_v1` is the speech model. A model of another kind is refused before paying, naming the node that runs it. | One node per kind of output ([01-decisions.md](01-decisions.md#the-nodes)); 06's match |
| Starting `model` | `seed_audio_v1` (`DEFAULT_MODELS["audio"]`) | The current speech model ([research/catalog.md](research/catalog.md#defaults)) |
| Starting `arguments` | `{"voice-name": "Jessie"}` (`DEFAULT_ARGUMENTS["audio"]`) | With nothing connected the node chooses text reading, whose entry marks `--voice-name` required with no default. An empty box would refuse the starting model. `Jessie` is one of the 13 voices `voice list --model seed_audio_v1` returned. |
| Starting `credit_ceiling` | `DEFAULT_CEILINGS["audio"]` = 20: AUD-D, the quote of the starting values (12 credits on 2026-10-17), rounded up to the next multiple of 10 | Part 0, Step 7 of [21-test-runs.md](21-test-runs.md#step-7-check-the-starting-values-and-the-ceiling-defaults) measures AUD-D and records it in [research/catalog.md](research/catalog.md#prices) and the README's changes table ([01-decisions.md](01-decisions.md#credits)) |
| Mode and scenario | A model with one mode entry runs it. For `seed_audio_v1`, nothing connected gives `tts` `text-reading`, and a picture, audio, or an Element gives `tts` `omni-dubbing`. `"mode"` and `"scenario"` in `arguments` override it. | 06's rule ([06-model-check.md](06-model-check.md#the-scenario)) |
| Where the voice applies | Only where the chosen entry lists `--voice-name`: on the owner's list, `seed_audio_v1` text reading. In omni dubbing, a `voice-name` is refused before paying, and the help page, the `arguments` tooltip, and the refusal say to leave `arguments` as `{}`. | The live list is authoritative, and one rule keeps it simple. `seed_audio_v1` lists no `--voice-name` for omni dubbing ([research/catalog.md](research/catalog.md#audio-models)). Part 0 found that the CLI accepts one there anyway; the pack still follows the list. |
| The voice and the reference limits | In text reading, 07 counts the voice as one audio reference, which fills the entry's 0 to 1 audio | "A voice counts as an audio reference" ([07-media.md](07-media.md#validate_references)); run C-11 checks what the one audio slot is for |
| How many clips | One per run. No `--count` is sent. | "All audio workflows produce one output; omit `--count`" ([research/cli.md](research/cli.md#generation-nodes)); no audio entry lists `--count` |
| Music | Supported as any mode is: chosen when it is a model's only mode, or with `"mode": "music"`, and `duration` checked against the model's bounds | It is a CLI mode (schema: `node create audio` `--mode`). No model on the owner's list has it, so no example or live run uses it ([research/catalog.md](research/catalog.md#audio-models)). |
| Output formats | Whatever Dreamina returns, decoded by 07's `decode_audio` | Run C-11 records the format of a downloaded clip; if `resource download` cannot fetch audio, this milestone stops ([07-media.md](07-media.md#live-checks)) |
| Cancel | A cancel stops only the wait. The audio is still made and billed, and Generation: Download collects it. | Dreamina has no cancel ([01-decisions.md](01-decisions.md#paid-runs)) |

## What Dreamina's audio models look like

These facts shape the help page and the examples; none needs code here
([research/catalog.md](research/catalog.md#audio-models),
[research/catalog.md](research/catalog.md#voices)):

- **`seed_audio_v1` text reading**: `--scenario` (the one value
  `text-reading`), `--voice-name` required, `--prompt` required, 1 to 3,000
  characters. It takes 0 to 1 audio reference.
- **`seed_audio_v1` omni dubbing**: `--scenario` (the one value
  `omni-dubbing`) and `--prompt`, required, 1 to 3,000 characters. It takes 0
  to 3 references: up to one image and up to three audio clips, and an image
  and audio may not go together.
- **Voices.** `seed_audio_v1` has 13: Good Guy, Fussy male, Jessie, Queen,
  Wacky, Santa II, Chill Girl, Valley Girl, Trickster, Old Style Advertising
  Male, Elfy, Cute Boy, and Adorable Girl. Model: Info lists them
  ([15-node-model-info.md](15-node-model-info.md)). A voice name goes to
  `--voice-name` unchanged, spaces included.
- **File limits** for `seed_audio_v1` omni dubbing: images up to 10 MB and
  8,192 pixels, audio up to 10 MB and 3 to 30 seconds. The server refuses a
  larger file at save, before any charge
  ([research/catalog.md](research/catalog.md#file-limits)).

## Step 1: Audio: Generate

Create `src/nodes/audio.py`, ported from `F/src/nodes/audio.py`, with the
docstring "Audio: Generate, the paid node for every Dreamina model that makes
audio." and `AudioGenerate(GenerateNode)`:

```python
class AudioGenerate(GenerateNode):
    """Make speech, dubbing, or music with any Dreamina audio model."""

    kind = "audio"
    display_name = "Audio: Generate"
    default_ceiling = DEFAULT_CEILINGS["audio"]
    list_inputs = frozenset({INPUT_NAMES["IMAGES"], INPUT_NAMES["AUDIO"]})
    outputs = (
        io.Audio.Output("audio", display_name="audio", is_output_list=True),
        io.Custom(SOCKET_TYPES["REFERENCES"]).Output("references", display_name="references"),
        io.String.Output("result", display_name="result"),
    )

    @classmethod
    @override
    def define_schema(cls) -> io.Schema:
        """Describe the node: its name, its menu, and its inputs."""
        return cls.build_schema(
            category=MENUS["AUDIO"],
            description="Make speech, dubbing, or music with any Dreamina audio model.",
        )
```

The class attributes are the ones 08's `GenerateNode` reads
([08-runs.md](08-runs.md#step-18-generate-node)), as
[09-node-image.md](09-node-image.md#step-1-image-generate) describes them.
`list_inputs` names `images` and `audio`, the media omni dubbing takes, so
`GenerateNode.build_schema` shows those two and no `videos`.

In the same change, add the `"audio"` key to `DEFAULT_CEILINGS` in
`src/config/inputs.py`: AUD-D, rounded up to the next multiple of 10
([06-model-check.md](06-model-check.md#srcconfiginputspy)).

`GenerateNode.build_schema` returns this schema for the class, written out:

```python
io.Schema(
    node_id=f"{NODE_PREFIX}{cls.__name__}",
    display_name=cls.display_name,
    category=MENUS["AUDIO"],
    description="Make speech, dubbing, or music with any Dreamina audio model.",
    inputs=[
        io.Image.Input(INPUT_NAMES["IMAGES"], optional=True, tooltip=TOOLTIPS["IMAGES"]),
        io.Audio.Input(INPUT_NAMES["AUDIO"], optional=True, tooltip=TOOLTIPS["AUDIO"]),
        io.Custom(SOCKET_TYPES["REFERENCES"]).Input(
            INPUT_NAMES["REFERENCES"], optional=True, tooltip=TOOLTIPS["REFERENCES"]
        ),
        io.String.Input(INPUT_NAMES["MODEL"], default=DEFAULT_MODELS["audio"], tooltip=TOOLTIPS["MODEL"]),
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
            default=DEFAULT_ARGUMENTS["audio"],
            multiline=True,
            tooltip=ARGUMENTS_TOOLTIPS["audio"],
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
| Node ID | `DreaminaAudioGenerate` |
| Display name | `Audio: Generate` |
| Category | `Dreamina/Audio` |
| Description | `Make speech, dubbing, or music with any Dreamina audio model.` |
| Inputs, in order | `images`, `audio`, `references`, `model`, `credit_ceiling`, `run_number`, `prompt`, `arguments` |
| `model` default | `seed_audio_v1` |
| `credit_ceiling` default and range | `DEFAULT_CEILINGS["audio"]` = 20 (AUD-D, 12 credits, rounded up to the next 10); 0 to 2,147,483,647 |
| `run_number` default and range | 0; 0 to 2,147,483,647 |
| `arguments` default | `{"voice-name": "Jessie"}` |
| Tooltips | 06's `TOOLTIPS`, and `ARGUMENTS_TOOLTIPS["audio"]` for `arguments`, exactly ([06-model-check.md](06-model-check.md#srcconfiginputspy)) |
| Outputs | `audio` (AUDIO, list), `references` (`DREAMINA_REFERENCES`), `result` (STRING); each label equals its ID |
| Input lists | `is_input_list=True` |
| Hidden | `io.Hidden.unique_id` |

The `arguments` tooltip says where the voice applies, in 06's words:
"The model's settings as a JSON object, under Dreamina's flag names, such as
{"voice-name": "Jessie"}. A voice applies to text reading, when nothing is
connected. For omni dubbing, or a model that lists no voice-name, leave {}."

The class holds no `send` of its own. `GenerateNode` sends the run and fills
the outputs by ID with 08's `build_node_outputs`. The module has no other
code.

### What a run sends

Two runs of this node, as 06 builds them
([06-model-check.md](06-model-check.md#seed-audio-reading-a-script)):

| Model | Connected | `arguments` | Mode entry | Flags 06 builds |
| ----- | --------- | ----------- | ---------- | --------------- |
| `seed_audio_v1` | Nothing | `{"voice-name": "Jessie"}` | `tts` `text-reading` | `--mode tts --scenario text-reading --voice-name Jessie` |
| `seed_audio_v1` | `references` ← a portrait | `{}` | `tts` `omni-dubbing` | `--mode tts --scenario omni-dubbing` |

08 adds `--model`, `--prompt`, each `--ref`, `--run`, `--submit-id`, and
`--credit-ceiling`. Omni dubbing refuses `{"voice-name": "Jessie"}` with
`Mode tts (omni-dubbing) of this model has no flag named voice-name. Its flags are scenario, prompt. Remove it from arguments, or set another mode.`,
when the node runs, before anything is uploaded or paid.

## Step 2: What fills each output

The rules 08's `build_node_outputs` implements for these outputs:

1. `audio`: every downloaded file of kind `audio` from the run's submit ID,
   decoded by 07's `decode_audio` in a worker thread into ComfyUI's AUDIO
   form, `{"waveform": [1, channels, samples], "sample_rate": rate}`, at the
   file's own sample rate and channel count. A run makes one clip, so the
   list holds one.
1. `references`: one `Reference(origin="node", value=<node ID>,
   media="audio", …)`. A video run can take it as an audio reference in
   `m2v`, and Element: Add as a voice, with no download or upload.
1. `result`: as in [09-node-image.md](09-node-image.md#step-2-what-fills-each-output).
1. An empty `audio` list becomes `ExecutionBlocker(None)`.

08's `GenerationOperation` downloads only the files this node decodes.

## Step 3: Register

In `src/nodes/__init__.py`, import `AudioGenerate` and add it to `NODE_TYPES`
after `ImageUpscale`, where it stays once `VideoGenerate` is inserted before
it in the Video and downloads milestone
([04-architecture.md](04-architecture.md#srcnodes)). This milestone also
registers `ModelInfo`, last, as
[15-node-model-info.md](15-node-model-info.md) says, so `NODE_TYPES` becomes
`(ImageGenerate, ImageUpscale, AudioGenerate, ModelInfo)`.

## Step 4: Help page

Create `web/docs/DreaminaAudioGenerate.md`. Its reference is F's
`web/docs/FalAudioGenerate.md` (46 lines), and this page is no longer.

```markdown
# Audio: Generate

Runs any Dreamina model that makes audio: text read in a chosen voice, or
speech for a connected picture or audio clip, called omni dubbing.

## Inputs

| Input            | What it takes                                                                                   |
| ---------------- | ----------------------------------------------------------------------------------------------- |
| `images`         | A picture for omni dubbing, uploaded with the run.                                              |
| `audio`          | Audio clips for omni dubbing, uploaded with the run. **Create List** joins several.             |
| `references`     | Outputs of other Dreamina nodes, and Elements, sent with no upload.                             |
| `model`          | The model's Dreamina name. The default is `seed_audio_v1`.                                      |
| `credit_ceiling` | The most credits the run may cost. A run that costs more stops, and nothing is billed.          |
| `run_number`     | Change it to send the same run again.                                                           |
| `prompt`         | The words to speak.                                                                             |
| `arguments`      | The model's settings as JSON, under Dreamina's flag names, such as `{"voice-name": "Jessie"}`. |

**Model: Info** shows a model's modes, flags, and voices. The node checks
every setting against your Dreamina model list before it pays. With nothing
connected, it reads the prompt in the `voice-name` voice. With a picture,
audio, or a reference, it uses omni dubbing, which takes no voice, so set
`arguments` to `{}`. Do the same for a model that lists no `voice-name`.

## Outputs

| Output       | What it carries                                                    |
| ------------ | ------------------------------------------------------------------ |
| `audio`      | The audio clip.                                                    |
| `references` | The new audio on your Dreamina canvas, for the next Dreamina node. |
| `result`     | Dreamina's record of the run as JSON, with a link to your canvas.  |

## Use

1. Write the words in `prompt`.
2. Copy a voice from **Model: Info**, and set it as `voice-name`.
3. To dub instead, connect a picture or audio, and set `arguments` to `{}`.
4. Connect `audio` to **Save Audio (Advanced)** or **Preview Audio**, and
   select **Run**.

Once Dreamina accepts a run, a cancel stops only the wait: the clip is still
made and billed. Collect it with **Generation: Download**.

Examples: **audio-01-voice-a-script** and **audio-02-give-a-host-a-voice**.

[Dreamina](https://dreamina.capcut.com/ai-tool/home)
```

The eight rows are the node's inputs, in node order, as `comfy:nodes:check`
requires. The page ships in the Audio milestone with its cancel paragraph
ending after "billed.", because Generation: Download ships later. The Video
and downloads milestone adds "Collect it with **Generation: Download**.", as
[14-node-download.md](14-node-download.md#step-5-help-page) says. Both
examples ship in this milestone.

## Step 5: README row and examples

The README node table row ([18-documentation.md](18-documentation.md)):

| Node | What it does | Paid |
| ---- | ------------ | ---- |
| [Audio: Generate](web/docs/DreaminaAudioGenerate.md) | Reads text in a chosen voice, or dubs speech for a picture, with any Dreamina audio model. | Yes |

The README example table rows:

| Workflow | Input |
| -------- | ----- |
| [Audio: Voice a Script](example_workflows/audio-01-voice-a-script.json) | A script |
| [Audio: Give a Host a Voice](example_workflows/audio-02-give-a-host-a-voice.json) | A host and a line |

The audio examples' **Audio: Generate** settings.
[17-scripts-and-workflows.md](17-scripts-and-workflows.md#example-workflows)
owns the examples: their layout, notes, prompts, and save names. When 17
differs, 17 wins and this plan is corrected. Each step's credits are Part 0's
quotes, which [21-test-runs.md](21-test-runs.md) Part 4 states before each
example runs.

| Slug | Steps before | Audio step | `model` | `arguments` | Connected and mode | Saved as |
| ---- | ------------ | ---------- | ------- | ----------- | ------------------ | -------- |
| `audio-01-voice-a-script` | **Voices**: Model: Info with `model` `seed_audio_v1`, its report shown by **Preview as Text** | Voice | starting value | `{"voice-name": "Good Guy"}` | nothing, **Script** → `prompt`: `tts` `text-reading` | `audio/dreamina/script-voice` |
| `audio-02-give-a-host-a-voice` | **Cast**: Image: Generate, `{"ratio": "3:4", "resolution": "2K"}` | Speak | starting value | `{}` | `references` ← Cast's portrait, **Line** → `prompt`: `tts` `omni-dubbing` | `audio/dreamina/host-voice` |

- **audio-01** shows a voice chosen from Model: Info's list: **Good Guy**,
  one of the 13, instead of the starting **Jessie**. Its note says to copy a
  name from **Info** into `voice-name`. It is Model: Info's example, so it
  registers that node.
- **audio-02** shows the scenario the node chooses by itself: a picture in
  `references` makes it omni dubbing. Omni dubbing takes no `voice-name`, so
  `arguments` is `{}`, and the note says so and points to audio-01 for a
  chosen voice. Its **Cast** step is `CAST`, which video-02 and video-03 place
  again ([17-scripts-and-workflows.md](17-scripts-and-workflows.md#audio-02-give-a-host-a-voice)).
- No example uses `music`: no model on the owner's list has it.

## Step 6: Live checks

Run these through the node after the Audio milestone's commit, with the
owner's approval. [21-test-runs.md](21-test-runs.md#part-2-first-run-of-each-node-milestone)
lists them under Part 2, after M-1, Model: Info's free run. I-1 is the image
run of [09-node-image.md](09-node-image.md#step-6-live-checks). The credit
names are Part 0's quotes ([21-test-runs.md](21-test-runs.md#step-8-prices-the-later-tables-use)).

| Run | Request | Settles | Credits | If it differs |
| --- | ------- | ------- | ------- | ------------- |
| A-1 | First, free: `model` `seedance_2.0_fast`. Then the starting `model` and `arguments`, `prompt` "Hello from Dreamina.", the default `credit_ceiling` → **Save Audio (Advanced)** `audio/dreamina/a1` | The other-kind refusal naming **Video: Generate**; `tts` `text-reading` chosen with nothing connected; the voice sent unchanged; no `--count`; the default ceiling covers the starting values; the clip downloaded and decoded at its own sample rate; **Save Audio (Advanced)** and **Preview Audio** taking the list; `references` holding one node | AUD-D | Fix 07's `decode_audio` or 06's scenario choice |
| A-2 | `references` ← I-1's `references`, `prompt` "A cheerful voice says: hello from Dreamina."; first with the starting `arguments`, then with `{}` | The free refusal of `voice-name` in omni dubbing, before any upload, naming the mode's flags; then `tts` `omni-dubbing` chosen for a picture, the picture sent as `--ref node:…`, and a clip made | DUB | Fix 06's entry choice or 07's counts |

No run checks `music`, because no model on the owner's list has it. When one
appears, a run with `{"mode": "music", "duration": <the model's minimum>}`
is added here and to 21. Record each result in the README's changes table.

## Names this plan uses from other plans

| Name | Owner | Used for |
| ---- | ----- | -------- |
| `GenerateNode` (`build_schema`, `kind`, `display_name`, `default_ceiling`, `outputs`), `PaidNode` (`list_inputs`), `build_node_outputs`, `GenerationOperation` | [08-runs.md](08-runs.md) | The node base and the run |
| `DEFAULT_MODELS`, `DEFAULT_ARGUMENTS`, `DEFAULT_CEILINGS`, `INPUT_NAMES`, `TOOLTIPS`, `ARGUMENTS_TOOLTIPS`, `RUN_NUMBER`, `CREDIT_CEILING_RANGE`, the mode and scenario choice, `FLAG_NOT_IN_MODE`, `ARGUMENT_UNKNOWN` | [06-model-check.md](06-model-check.md) | The inputs, their starting values, and the checks before paying |
| `decode_audio`, `encode_local_file`, `Reference`, `validate_references` (the voice count), runs C-4 and C-11 | [07-media.md](07-media.md) | Decoding, uploads, references, and audio formats |
| `NODE_PREFIX`, `MENUS["AUDIO"]`, `SOCKET_TYPES["REFERENCES"]`, `NODE_TYPES` | [05-foundation.md](05-foundation.md) | Names and registration |
| `ModelInfo`, its voice list | [15-node-model-info.md](15-node-model-info.md) | audio-01 and the help page's pointer to voices |
| `GenerationDownload`, its help-page sentence | [14-node-download.md](14-node-download.md) | The cancel sentence added in the Video and downloads milestone |
| `ImageGenerate`, run I-1 | [09-node-image.md](09-node-image.md) | audio-02's Cast step and A-2 |
| The examples, `CAST` | [17-scripts-and-workflows.md](17-scripts-and-workflows.md) | Step 5 |
| AUD-D, DUB, M-1, A-1, A-2 | [21-test-runs.md](21-test-runs.md) | The starting ceiling and the live checks |
