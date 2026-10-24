# Video: Generate

Runs any Dreamina model that makes video: from a prompt, from a first and
last frame, or from images, video, audio, and Elements together. It outputs the
video, and a reference to it for the next Dreamina node.

## Inputs

| Input            | What it takes                                                                                          |
| ---------------- | ------------------------------------------------------------------------------------------------------ |
| `images`         | Frames or reference images, uploaded with the run. **Create List** joins several.                      |
| `videos`         | Reference videos, uploaded with the run.                                                               |
| `audio`          | Reference audio, uploaded with the run. A recorded line becomes the speech in the video.               |
| `references`     | Outputs of other Dreamina nodes, and Elements, sent with no upload.                                    |
| `model`          | The model's Dreamina name, such as `seedance_2.5`. The default is `seedance_2.0_mini`.                 |
| `credit_ceiling` | The most credits the run may cost. A run that costs more stops, and nothing is billed.                 |
| `ratio`          | The shape of the video, such as `16:9` or `9:16`.                                                      |
| `resolution`     | The size of the video, such as `720p`.                                                                 |
| `duration`       | The length in seconds.                                                                                 |
| `count`          | How many videos to make. Dreamina bills each one.                                                      |
| `run_number`     | Change this number to send the same run again.                                                         |
| `prompt`         | What happens. `{{image1}}`, `{{video1}}`, or `{{reference1}}` points at an input.                      |
| `arguments`      | Any other flag of the model as JSON, under its Dreamina name, such as `{"mode": "m2v"}`. Starts empty. |

**Model: Info** shows the modes and flags of a model, and their allowed values. The node
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

Dreamina cannot stop a run it has accepted. If you cancel, ComfyUI
restarts, or the request timeout passes, the video is still made and billed.
Collect it with **Generation: Download**.

Examples: **video-01-animate-a-host**, **video-02-film-a-product-ad**,
**video-03-keep-a-host-across-shots**, and **video-04-recover-a-video**.

[Dreamina](https://dreamina.capcut.com/ai-tool/home)
