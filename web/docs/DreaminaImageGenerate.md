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
billed.

Examples: **image-01-design-a-host**, **image-02-edit-a-product-photo**, and
**image-03-upscale-a-poster**.

[Dreamina](https://dreamina.capcut.com/ai-tool/home)
