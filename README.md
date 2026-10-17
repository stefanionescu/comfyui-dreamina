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
- [License](#license)

## Requirements

- Python 3.12 or later.
- ComfyUI 0.37.2 or later, with frontend 1.52.7 or later in the 1.x series.
- A Dreamina account that can use the
  [Dreamina Canvas CLI](https://dreamina.capcut.com/canvas-cli).
- The Dreamina Canvas CLI, installed with its official command.

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

## License

[MIT](LICENSE.md).
