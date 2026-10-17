# ![comfyui-dreamina: a ComfyUI extension that runs Dreamina models](docs/images/brand/banner.svg)

[![ComfyUI 0.37.2 or later](docs/images/badges/comfyui.svg)](#requirements)
[![Frontend 1.52.7 or later](docs/images/badges/frontend.svg)](#requirements)
[![Python 3.12 or later](docs/images/badges/python.svg)](#requirements)
[![MIT license](docs/images/badges/license.svg)](LICENSE.md)

Run Dreamina's image, video, and audio models in ComfyUI with your own Dreamina
account.

## Contents

- [Requirements](#requirements)
- [Install](#install)
- [Example workflows](#example-workflows)
- [Nodes](#nodes)
- [License](#license)

## Requirements

- Python 3.12 or later.
- ComfyUI 0.37.2 or later, with frontend 1.52.7 or later in the 1.x series.
- A Dreamina account that can use the
  [Dreamina Canvas CLI](https://dreamina.capcut.com/canvas-cli).

## Install

Put the extension in `ComfyUI/custom_nodes/dreamina`, install its
`requirements.txt` with ComfyUI's Python, and restart ComfyUI.

### Comfy Desktop

1. In the instance chooser, select the **⋮** icon on the instance card, then
   **Manage**.
2. Under **About**, copy **Location**. In that folder, find the `ComfyUI` folder
   that holds `main.py`, and put the extension in its `custom_nodes` folder.
3. Select **Terminal** in the same panel and run:

```sh
pip install -r custom_nodes/dreamina/requirements.txt
```

### macOS or Linux

From the ComfyUI folder:

```sh
.venv/bin/python -m pip install -r custom_nodes/dreamina/requirements.txt
```

With uv:

```sh
uv pip install --python .venv/bin/python -r custom_nodes/dreamina/requirements.txt
```

### Windows

From the ComfyUI folder, in PowerShell:

```powershell
.\.venv\Scripts\python.exe -m pip install -r .\custom_nodes\dreamina\requirements.txt
```

### Windows portable

From the folder that holds `ComfyUI` and `python_embeded`, in PowerShell:

```powershell
.\python_embeded\python.exe -m pip install -r .\ComfyUI\custom_nodes\dreamina\requirements.txt
```

**Dreamina Settings** installs the Dreamina CLI. To install it from a terminal instead:

- macOS or Linux: `curl -fsSL https://dreamina.capcut.com/canvas-cli/install.sh | bash`
- Windows PowerShell: `irm https://dreamina.capcut.com/canvas-cli/install.ps1 | iex`

## Example workflows

| Workflow                                                                            | Input                        |
| ----------------------------------------------------------------------------------- | ---------------------------- |
| [Image: Design a Host](example_workflows/image-01-design-a-host.json)               | A host description           |
| [Image: Edit a Product Photo](example_workflows/image-02-edit-a-product-photo.json) | A product photo and a change |
| [Image: Upscale a Poster](example_workflows/image-03-upscale-a-poster.json)         | A brief                      |
| [Audio: Voice a Script](example_workflows/audio-01-voice-a-script.json)             | A script                     |
| [Audio: Give a Host a Voice](example_workflows/audio-02-give-a-host-a-voice.json)   | A host and a line            |

They are in **Browse Templates → dreamina**. Start with each workflow's
**Start Here** note. Most steps are subgraphs. Media inputs start empty, and
most workflows make their own inputs with Dreamina models.

## Nodes

The nodes are under **Dreamina** in the node menu, and each has a help page.

| Node                                                 | What it does                                                                               | Paid |
| ---------------------------------------------------- | ------------------------------------------------------------------------------------------ | ---- |
| [Image: Generate](web/docs/DreaminaImageGenerate.md) | Makes or edits images with any Dreamina image model.                                       | Yes  |
| [Image: Upscale](web/docs/DreaminaImageUpscale.md)   | Makes images larger and sharper with Dreamina's upscale.                                   | Yes  |
| [Audio: Generate](web/docs/DreaminaAudioGenerate.md) | Reads text in a chosen voice, or dubs speech for a picture, with any Dreamina audio model. | Yes  |
| [Model: Info](web/docs/DreaminaModelInfo.md)         | Shows a model's modes, settings, reference and file limits, and voices, as JSON.           | No   |

## License

[MIT](LICENSE.md).
