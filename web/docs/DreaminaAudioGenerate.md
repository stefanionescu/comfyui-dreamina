# Audio: Generate

Runs any Dreamina model that makes audio: text read in a chosen voice, or
speech for a connected picture or audio clip, called omni dubbing.

## Inputs

| Input            | What it takes                                                                                  |
| ---------------- | ---------------------------------------------------------------------------------------------- |
| `images`         | A picture for omni dubbing, uploaded with the run.                                             |
| `audio`          | Audio clips for omni dubbing, uploaded with the run. **Create List** joins several.            |
| `references`     | Outputs of other Dreamina nodes, and Elements, sent with no upload.                            |
| `model`          | The model's Dreamina name. The default is `seed_audio_v1`.                                     |
| `credit_ceiling` | The most credits the run may cost. A run that costs more stops, and nothing is billed.         |
| `run_number`     | Change it to send the same run again.                                                          |
| `prompt`         | The words to speak.                                                                            |
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
made and billed.

Examples: **audio-01-voice-a-script** and **audio-02-give-a-host-a-voice**.

[Dreamina](https://dreamina.capcut.com/ai-tool/home)
