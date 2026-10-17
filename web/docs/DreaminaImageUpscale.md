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
the wait: the upscale is still made and billed.

Example: **image-03-upscale-a-poster**.

[Dreamina](https://dreamina.capcut.com/ai-tool/home)
