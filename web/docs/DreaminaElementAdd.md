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
