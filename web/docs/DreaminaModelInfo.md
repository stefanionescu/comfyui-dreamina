# Model: Info

Shows what a Dreamina model takes, as JSON. It lists the modes, the settings of
each mode with their values and ranges, the references and files the model takes,
and the voices of a speech model. Use it to write the `arguments` of a paid node.
It reads your live model list, so it needs sign-in. It bills nothing.

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

A paid node takes `ratio`, `resolution`, `duration`, `count`, and the voice
in their own inputs, with underscores for dashes, as `voice_name` for the
`voice-name` flag. Write any other setting in `arguments` under its `flag`
name, such as `{"mode": "m2v"}`. The flags are exactly what the paid node accepts, so the
paid node cannot send a voice listed for a model with no `voice-name` flag. A value
Dreamina does not give is null. Example: **audio-01-voice-a-script**.

[Dreamina Canvas CLI](https://dreamina.capcut.com/canvas-cli)
