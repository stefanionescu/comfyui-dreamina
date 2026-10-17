# Documentation

This plan writes the public documentation: `README.md`, `ADVANCED.md`, and the
shared format of the help pages in `web/docs/`. It follows the fal pack's
shipped documents (`F=/Users/dr_stone/Documents/work/comfyui-fal`, commit
`cef8b6e`: `README.md` at 203 lines, `ADVANCED.md` at 546 lines, and
`web/docs/*.md`) and F's plan 18 (`F/plans/18-documentation.md`), which wrote
them. The images themselves, their palette, their alt text, and how each is
made belong to [19-brand-assets.md](19-brand-assets.md); this plan places
them and copies their alt text.

Readers of the documents: the README is for people who install and use the
pack; the advanced guide is the reference for people who already use it, and
for developers; the help pages open from ComfyUI's node **Info** panel.
Readers of this plan: the engineer who writes the documents milestone by
milestone, and the owner, who reviews them.

## Contents

- [How the documents are written](#how-the-documents-are-written)
- [Step 1: README start](#step-1-readme-start)
- [Step 2: README text](#step-2-readme-text)
- [Step 3: Advanced guide](#step-3-advanced-guide)
- [Step 4: Help pages](#step-4-help-pages)
- [Step 5: Screenshots](#step-5-screenshots)
- [When each part is added](#when-each-part-is-added)

## How the documents are written

Every text follows `rules/WRITING.md` and `rules/DOCUMENTATION.md`, and the
owner's rules in [research/owner-rules.md](research/owner-rules.md#readme-advanced-and-help-pages):

- Plain language (ISO 24495-1:2023): short sentences, one idea each, familiar
  words, second person, US English, present state only.
- Everyday words first. The owner asked for documents a ComfyUI user can
  follow without ever having used Dreamina's CLI. A technical term appears
  only where the person needs it to act, and is explained once in plain words
  where it first appears: "the model name, Dreamina's name for the model, such
  as `seedance_2.5`". After that, the same term is used every time.
- "Dreamina" is written as Dreamina writes it, and the product the pack runs
  is the "Dreamina Canvas CLI" the first time and "the Dreamina CLI" after.
  The documents say "model name", never "model ID" or "endpoint", and
  "setting" in running text where the CLI says "flag"; the setting itself is
  written by its flag name, without dashes, such as `ratio`.
- Inputs, outputs, settings, and file names are written exactly, in code
  style (`credit_ceiling`, `voice-name`, `run_number`); UI labels are bold,
  exactly as [16-frontend.md](16-frontend.md#step-3-browser-text) writes
  them, in sentence case: **Install**, **Update**, **Sign in**, **Sign out**,
  **Save limits**, **Reload settings**. The dialog's title and menu entry are
  **Dreamina Settings**. Its three parts are **Dreamina CLI**, **Account**,
  and **Request limits**; it shows no install command and no canvas link.
- The repository and the README's banner say `comfyui-dreamina`; the install
  folder, the **Browse Templates** group, and the Registry ID are `dreamina`,
  as O's README says `comfyui-openrouter` and installs to `openrouter`.
- Title case for H1 titles, sentence case below; a `## Contents` section in
  long pages; no em dashes or double hyphens as punctuation; serial comma; no
  bold labels used as small headings; no layout or file-map section.
- No prices, credit amounts, spending caps of the pack's own, or spending
  warnings anywhere. "Billed" and "credits" appear where the person needs to
  know a run may cost something: `credit_ceiling`, a cancel, a run stopped at
  the ceiling. The only number of credits the pack ever shows is Dreamina's
  own quote in a refusal, and no document repeats one
  ([01-decisions.md](01-decisions.md#credits)).
- No bullet list above **Contents**; the README opens with the banner, four
  badges, and one sentence.
- F's shipped README (203 lines) and ADVANCED (546 lines) are the ceilings,
  section by section. F's **Keys and access** and **Files and uploads** have
  Dreamina counterparts (**Sign-in and access**, **References and uploads**).
  **The Dreamina CLI**, **Credit ceiling**, and **The canvas** are new, short,
  and paid for by F's sections with no counterpart, so the guide stays within
  550 lines.
- A page names only nodes, dialogs, and workflows that exist when it ships.
  Facts owned by another plan (a message, a setting, an input, an example
  slug, an alt text) are copied from that plan; when the two differ, the
  owning plan wins and the document is corrected in the same change.

The drafted text below is final, with these facts copied from the plans that
own them:

| Fact                                                    | Owning plan                                                                                                     |
| ------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| Example slugs, titles, inputs, and group names          | [17-scripts-and-workflows.md](17-scripts-and-workflows.md)                                                      |
| Setting names, defaults, and ranges                     | [05-foundation.md](05-foundation.md#step-3-settings-constants)                                                  |
| Dialog labels and parts                                 | [16-frontend.md](16-frontend.md)                                                                                |
| Starting models and `arguments`                         | [01-decisions.md](01-decisions.md#choosing-a-model), from [research/catalog.md](research/catalog.md#defaults)   |
| How the mode is chosen                                  | [01-decisions.md](01-decisions.md#how-the-mode-is-chosen), [06-model-check.md](06-model-check.md)               |
| Message titles in **Troubleshooting**                   | [05-foundation.md](05-foundation.md), [06-model-check.md](06-model-check.md), [07-media.md](07-media.md), and [08-runs.md](08-runs.md) once written |
| Local refusals in **When a node stops**                 | [06-model-check.md](06-model-check.md), [07-media.md](07-media.md), [08-runs.md](08-runs.md), [12-node-upscale.md](12-node-upscale.md), [13-node-element.md](13-node-element.md), [14-node-download.md](14-node-download.md), [15-node-model-info.md](15-node-model-info.md) |
| What another extension may call                         | [23-live-shopping-provider.md](23-live-shopping-provider.md)                                                    |
| Alt text, the **Images** subsection, and the screenshot procedure | [19-brand-assets.md](19-brand-assets.md)                                                              |

## Step 1: README start

Built in the Tooling milestone. The workflow check reads `README.md`, and the
Markdown and local link checks lint it and every image it links, so the
README start, the banner, and the four badges exist before the first commit
([03-repository-setup.md](03-repository-setup.md);
[19-brand-assets.md](19-brand-assets.md#step-1-badges-and-banner)). Nothing in
it describes a node or the settings dialog, because neither exists yet.

### `README.md` at the first commit

````markdown
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
````

Notes on Step 1:

- The minimums are [03-repository-setup.md](03-repository-setup.md)'s:
  `requires-comfyui = ">=0.37.2"`, frontend 1.52.7, and Python 3.12. They are
  F's, so the badges keep F's text, and their `aria-label` and `<title>`
  equal the alt text above ([19-brand-assets.md](19-brand-assets.md#badges)).
  When 03 changes a minimum, the README, the badge, and this plan change
  with it.
- The H1 alt text is F's form with the vendor changed, and the banner's own
  `aria-label` says the same. The purpose sentence names the pack as an
  extension that runs Dreamina's models with the person's own account, so
  nothing reads as Dreamina's own product
  ([01-decisions.md](01-decisions.md#names-and-identifiers)).
- **Requirements** has an account line, unlike F's, because the CLI decides
  who may use it. It names no plan: Dreamina's page says "Private beta ·
  Advanced subscribers only", yet the owner's Standard account passed the
  gate on 2026-10-16 ([research/catalog.md](research/catalog.md#account)), and
  the owner leaves a vendor's account conditions to the vendor's pages (B
  `61e08d8`). The link is the one external link the README has, and
  `repo:links:external` checks it on every push.
- The CLI line says "with its official command" until the settings dialog
  ships. The Frontend milestone removes it and ends **Install** with a short
  paragraph that names **Dreamina Settings** and gives the one-line commands
  for a terminal ([When each part is added](#when-each-part-is-added)).
- The install folder is `dreamina`
  ([01-decisions.md](01-decisions.md#names-and-identifiers)): ComfyUI names the
  **Browse Templates** group and the node badges after it, and
  `quality/config/repository/links.js` gets the link alias `dreamina`
  ([03-repository-setup.md](03-repository-setup.md)).

## Step 2: README text

The finished README, as it ships after the Documentation and brand milestone.
Sections arrive milestone by milestone as
[When each part is added](#when-each-part-is-added) says. Its outline is F's,
heading for heading. Sections that keep F's text word for word with names
changed: **Install** (Step 1) and **License**. **Development** keeps F's setup
and points to the advanced guide for every other task.

The example rows, titles, inputs, and the group names in **First run** are
copied from [17-scripts-and-workflows.md](17-scripts-and-workflows.md#summary);
17 owns them. Node rows go in `NODE_TYPES` order
([04-architecture.md](04-architecture.md#srcnodes)); workflow rows in slug
order.

The finished README keeps Step 1's opening, **Install**, and **License**,
with five changes:

1. **Contents** lists all ten sections:

   ```markdown
   - [Requirements](#requirements)
   - [Install](#install)
   - [First run](#first-run)
   - [Example workflows](#example-workflows)
   - [Nodes](#nodes)
   - [Models](#models)
   - [How a run works](#how-a-run-works)
   - [Development](#development)
   - [Common problems](#common-problems)
   - [License](#license)
   ```

1. **Requirements** loses its last line, the CLI line, from the Frontend
   milestone. The account line still names the Dreamina Canvas CLI, and
   **Install** says how to install it.

1. After the **Windows portable** command, **Install** gets the CLI
   paragraph, from the Frontend milestone:

   ```markdown
   **Dreamina Settings** installs the Dreamina CLI. To install it from a terminal instead:

   - macOS or Linux: `curl -fsSL https://dreamina.capcut.com/canvas-cli/install.sh | bash`
   - Windows PowerShell: `irm https://dreamina.capcut.com/canvas-cli/install.ps1 | iex`
   ```

1. After the CLI paragraph, from the Documentation and brand milestone,
   **Install** ends with:

   ```markdown
   To update or remove the extension, see the
   [advanced guide](ADVANCED.md#update-or-remove).
   ```

1. These sections go between **Install** and **License**, in this order:

````markdown
## First run

1. Open **ComfyUI menu → Extensions → Dreamina → Dreamina Settings**. If it
   says the Dreamina CLI is not installed, select **Install**.
2. Select **Sign in**, and approve the sign-in on dreamina.capcut.com.
3. Open **Browse Templates → dreamina → image-01-design-a-host** and select
   **Run**.
4. See your host in **Design** and on the **ComfyUI** canvas in Dreamina.

To send the same run again, change `run_number`.

## Example workflows

| Workflow                                                                                    | Input                          |
| ------------------------------------------------------------------------------------------- | ------------------------------ |
| [Image: Design a Host](example_workflows/image-01-design-a-host.json)                       | A host description             |
| [Image: Edit a Product Photo](example_workflows/image-02-edit-a-product-photo.json)         | A product photo and a change   |
| [Image: Upscale a Poster](example_workflows/image-03-upscale-a-poster.json)                 | A brief                        |
| [Audio: Voice a Script](example_workflows/audio-01-voice-a-script.json)                     | A script                       |
| [Audio: Give a Host a Voice](example_workflows/audio-02-give-a-host-a-voice.json)           | A host and a line              |
| [Video: Animate a Host](example_workflows/video-01-animate-a-host.json)                     | A host and a scene             |
| [Video: Film a Product Ad](example_workflows/video-02-film-a-product-ad.json)               | A host, a product, and a scene |
| [Video: Keep a Host across Shots](example_workflows/video-03-keep-a-host-across-shots.json) | A host and two scenes          |
| [Video: Recover a Video](example_workflows/video-04-recover-a-video.json)                   | A video left running           |

They are in **Browse Templates → dreamina**. Start with each workflow's
**Start Here** note. Most steps are subgraphs. Media inputs start empty, and
most workflows make their own inputs with Dreamina models.

![Screenshot of video-02: the Start Here note and a note for each step sit above four groups. Input holds the Host, Product, and Scene prompts; Cast draws the host; Packshot draws the product; and Film sends both to Seedance 2.5.](docs/images/screenshots/video-02-workflow.png)

## Nodes

The nodes are under **Dreamina** in the node menu, and each has a help page.

![Node map: one card for each kind of node. Image: Generate, Video: Generate, and Audio: Generate each run any Dreamina model of their kind, and Image: Generate feeds Image: Upscale. The references output of Element: Add and of every paid node feeds any paid node. Generation: Download collects runs left running, and Model: Info shows what a model takes. A blue square marks a node that starts a paid run, and a hollow square one that bills nothing.](docs/images/diagrams/node-map.svg)

| Node                                                           | What it does                                                                               | Paid |
| -------------------------------------------------------------- | ------------------------------------------------------------------------------------------ | ---- |
| [Image: Generate](web/docs/DreaminaImageGenerate.md)           | Makes or edits images with any Dreamina image model.                                       | Yes  |
| [Image: Upscale](web/docs/DreaminaImageUpscale.md)             | Makes images larger and sharper with Dreamina's upscale.                                   | Yes  |
| [Video: Generate](web/docs/DreaminaVideoGenerate.md)           | Makes video from a prompt, frames, or references with any Dreamina video model.            | Yes  |
| [Audio: Generate](web/docs/DreaminaAudioGenerate.md)           | Reads text in a chosen voice, or dubs speech for a picture, with any Dreamina audio model. | Yes  |
| [Element: Add](web/docs/DreaminaElementAdd.md)                 | Makes an Element that keeps a character, product, or place the same across runs.           | No   |
| [Generation: Download](web/docs/DreaminaGenerationDownload.md) | Downloads what Dreamina made for a run after the run stopped.                              | No   |
| [Model: Info](web/docs/DreaminaModelInfo.md)                   | Shows a model's modes, settings, reference and file limits, and voices, as JSON.           | No   |

## Models

Type any Dreamina model name in `model`, such as `seedance_2.5`. Nothing in
the extension lists or limits models. When you queue a workflow, and again
when it runs, the node checks the name and your settings against your own
model list from Dreamina, before anything is paid. **Model: Info** shows any
model's modes, settings, and voices, for free.

![Video: Generate on the canvas: the images, videos, audio, and references inputs; model set to seedance_2.0_mini; credit_ceiling; run_number; a prompt about a host holding up a green bottle; and arguments holding ratio 16:9, resolution 720p, and duration 4.](docs/images/screenshots/video-generate-node.png)

Write the model's settings in `arguments` as JSON, under Dreamina's names,
such as `{"ratio": "9:16", "resolution": "720p", "duration": 5}`. The node
stops if the model makes another kind of output, or does not take a setting
or value you sent. The [advanced guide](ADVANCED.md#models) says how the
mode is chosen.

## How a run works

1. The node checks your inputs against your model list, and stops before
   anything is paid.
2. It uploads your images, video, and audio to the **ComfyUI** canvas in your
   Dreamina account, and sends one run with `credit_ceiling`, the most
   credits the run may cost. Dreamina runs it only if its price is within
   that.
3. The node records the run, waits, and downloads the outputs. They also
   carry `references` to what Dreamina made, so the next Dreamina node uses
   it with no download or upload.

The [advanced guide](ADVANCED.md#what-each-node-sends) lists what each node
sends.

## Development

Development needs mise. Point the checks at ComfyUI in `.mise.local.toml`:

```toml
[env]
COMFYUI_PATH = "/path/to/ComfyUI"
COMFYUI_PYTHON = "/path/to/ComfyUI/.venv/bin/python"
```

Install the tools, dependencies, and Git hooks, and run the full check:

```shell
mise trust
mise run repo:setup
mise run repo:check
```

Restart ComfyUI after changing Python. The
[advanced guide](ADVANCED.md#development) lists every task.

## Common problems

| Problem                                 | Fix                                                                                                                   |
| --------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| ComfyUI could not find the Dreamina CLI | Select **Install** in **Dreamina Settings**, or run the command under [Install](#install) on the ComfyUI computer.    |
| You are not signed in to Dreamina       | Select **Sign in** in **Dreamina Settings**. ComfyUI must run as the computer user who signed in.                     |
| A run stops above its `credit_ceiling`  | Nothing was billed. Raise `credit_ceiling` to the number the message gives, and run again.                            |
| The model is not in your list           | Copy a name the message suggests, or check it with **Model: Info**. Your Dreamina plan may not offer that model.      |
| A canceled run was billed               | Dreamina cannot stop a run it accepted. Collect its outputs with **Generation: Download**.                            |
| No Dreamina nodes in the menu           | Check that the folder is `ComfyUI/custom_nodes/dreamina` and the console shows no import error, then restart ComfyUI. |
| The templates are missing               | Reinstall the whole extension, including `example_workflows`.                                                         |

More in the [advanced guide's troubleshooting](ADVANCED.md#troubleshooting).
````

Notes on Step 2:

- **First run** is four steps, one more than F's, because the CLI is
  installed and signed in from the dialog where F saved a key. It names
  image-01 and its group **Design**: 17 picks the first-run example as B and
  F did, the least expensive example that needs nothing from the person. If
  17 names another example or group, this text follows 17. The last step
  names the canvas, because the person can see every run there
  ([01-decisions.md](01-decisions.md#the-canvas)). Step 1 names only
  **Install**: the dialog reads the CLI's state when it opens.
- **Install**'s CLI paragraph gives the CLI page's one-line commands
  ([research/cli.md](research/cli.md#release-and-install)) for people who
  prefer a terminal, because the dialog shows no command
  ([16-frontend.md](16-frontend.md)). They are plain text, not read from
  code.
- **Example workflows** has F's two columns and F's paragraph with "fal
  models" changed to "Dreamina models". F's line about opening the examples
  in a new tab after an update is left to ADVANCED's **Update or remove**,
  which says it, to keep the README within 203 lines. The screenshot is video-02, the
  example whose media moves between nodes as `references`
  ([19-brand-assets.md](19-brand-assets.md#step-4-screenshots)). Its alt text
  is drafted in 19's form with 17's group names; it is rewritten from the
  capture ([Step 5](#step-5-screenshots)).
- **Nodes** keeps F's sentence. The node map's alt text is the SVG's own
  `aria-label` and `<title>`, word for word
  ([19-brand-assets.md](19-brand-assets.md#step-3-node-map)). The rows come
  from the node plans: Image: Upscale's from
  [12-node-upscale.md](12-node-upscale.md#step-7-readme-row-and-examples),
  Element: Add's from [13-node-element.md](13-node-element.md#step-7-readme-row-and-examples),
  Generation: Download's from [14-node-download.md](14-node-download.md#step-6-readme-row-and-examples),
  Model: Info's from [15-node-model-info.md](15-node-model-info.md#step-7-readme-row-and-examples),
  and Image: Generate's from [09-node-image.md](09-node-image.md#step-5-readme-row-and-examples).
  Video: Generate's and Audio: Generate's are drafted here until 10 and 11
  write theirs; then theirs win.
- **Models** says plainly what the owner asked for: any model name, nothing
  in the pack that lists or limits models, the check against the person's
  live list when the workflow is queued and again when the node runs, before
  paying, and **Model: Info** for any model's settings. It does not call the
  starting values the pack's only model names, because the examples name
  models too (video-02 sets `seedance_2.5`)
  ([01-decisions.md](01-decisions.md#how-the-nodes-cover-every-model)). It
  links no model page: Dreamina's site has no public page of model names,
  and the names come from the person's own list. The screenshot's alt text is
  19's: the starting model `seedance_2.0_mini` and its starting `arguments`
  ([research/catalog.md](research/catalog.md#defaults)). It is corrected to
  the capture.
- **How a run works** keeps F's three steps. Step 2 names `credit_ceiling`
  because Dreamina's own approval is part of every run
  ([01-decisions.md](01-decisions.md#credits)), and the **ComfyUI** canvas
  the uploads go to; step 3 says the outputs are downloaded and carry
  `references` where F said fal links.
- **Common problems** keeps F's seven rows, re-valued for what goes wrong
  with a CLI and an account instead of a key. A row named for a message uses
  the message's first sentence. Dreamina's "no longer accepts this version"
  row gave way to "A canceled run was billed": that message already says
  **Update**, and a cancel that keeps billing is the Dreamina behavior no
  message can show before it happens. F's rows on multi-user mode,
  `pydantic`, help pages, and duplicate folders move to the advanced guide or
  drop: the first is a troubleshooting entry there, and the others did not
  happen in F's or B's use.
- Length: 201 lines, within F's 203.

## Step 3: Advanced guide

Written whole in the Documentation and brand milestone; no earlier plan edits
`ADVANCED.md`. The outline is F's, with **Keys and access** renamed **Sign-in
and access**, **Files and uploads** renamed **References and uploads**,
**Recover a request** renamed **Recover a generation**, and three short
sections added for what F has no counterpart for:

```text
# ComfyUI Dreamina Advanced Guide
## Contents
## What each node sends
## Sign-in and access
## The Dreamina CLI
## Settings
## Models
## Credit ceiling
## References and uploads
## Caching and reruns
## Recover a generation
## The canvas
## Limits
## When a node stops
## Use from another extension
## Update or remove
## Development
### Setup
### Generated files
### Full check
### Format
### Lint
### Types
### Generated-file checks
### Security and licenses
### Git hooks
### Test a change
### Import rules
### Function names
### Images
### Change text
## Package and publish
## Troubleshooting
```

The finished text:

````markdown
# ComfyUI Dreamina Advanced Guide

## Contents

- [What each node sends](#what-each-node-sends)
- [Sign-in and access](#sign-in-and-access)
- [The Dreamina CLI](#the-dreamina-cli)
- [Settings](#settings)
- [Models](#models)
- [Credit ceiling](#credit-ceiling)
- [References and uploads](#references-and-uploads)
- [Caching and reruns](#caching-and-reruns)
- [Recover a generation](#recover-a-generation)
- [The canvas](#the-canvas)
- [Limits](#limits)
- [When a node stops](#when-a-node-stops)
- [Use from another extension](#use-from-another-extension)
- [Update or remove](#update-or-remove)
- [Development](#development)
- [Package and publish](#package-and-publish)
- [Troubleshooting](#troubleshooting)

## What each node sends

- **Image: Generate**, **Video: Generate**, and **Audio: Generate** first read
  your model list of their kind from the Dreamina CLI, for free. They upload
  your images as PNG, your video as MP4, and your audio as WAV to your
  Dreamina canvas, and send `prompt`, the settings in `arguments`, and every
  reference, with `credit_ceiling`. They send one run, record it as soon as
  Dreamina accepts it, and wait. Then they download each output and return
  it, with `references` to what was made, and `result`: JSON with the canvas
  link, the request ID, and Dreamina's record of the run.
- **Image: Upscale** upscales up to 20 images in one run, the same way. Each
  ComfyUI image is first uploaded and imported to the canvas, for free.
- **Element: Add** makes an Element on your canvas from a main image, more
  angles, and a voice, and returns it in `references`. It bills nothing.
- **Generation: Download** downloads a recorded run's outputs, for free.
- **Model: Info** returns one model's modes, settings, limits, and voices as
  JSON, for free.

## Sign-in and access

Select **Sign in** in **ComfyUI menu → Extensions → Dreamina → Dreamina
Settings**, check that Dreamina's page shows the dialog's code, and approve.
The Dreamina CLI keeps the sign-in in your computer's sign-in store, for your
computer user only. The extension never sees it. **Sign out** clears it.
ComfyUI must run as the user who signed in, on the same computer.

Dreamina Settings works only from a browser on the ComfyUI computer, at a
localhost address. In ComfyUI's multi-user mode it shows the state but
changes nothing. From another computer, or in multi-user mode, run
`dreamina-canvas auth login` on the server as the user that runs ComfyUI.

The private folder holds the settings, the canvas ID, and the run records:

| System  | Folder                                             |
| ------- | -------------------------------------------------- |
| macOS   | `~/Library/Application Support/DreaminaComfyUI`    |
| Linux   | `${XDG_STATE_HOME:-~/.local/state}/dreamina-comfy` |
| Windows | `%LOCALAPPDATA%\DreaminaComfyUI`                   |

To use another folder, set `DREAMINA_COMFY_STATE_DIRECTORY` to an absolute
path outside ComfyUI, the extension, and their media folders. Files are
unencrypted, with owner-only permissions.

## The Dreamina CLI

The extension runs the Dreamina Canvas CLI, `dreamina-canvas`, release 1.0.3
or later. It looks for it in the folder `DREAMINA_CANVAS_INSTALL_DIR` names,
then on the ComfyUI server's `PATH`, then in the installer's folder:
`~/.local/bin` on macOS and Linux, and `%USERPROFILE%\bin` on Windows.

**Install** in **Dreamina Settings** runs ByteDance's official installer from
dreamina.capcut.com, and **Update** runs it again. Or run it from a terminal:

- macOS or Linux: `curl -fsSL https://dreamina.capcut.com/canvas-cli/install.sh | bash`
- Windows PowerShell: `irm https://dreamina.capcut.com/canvas-cli/install.ps1 | iex`

The extension checks the CLI's version and commands once, and again after
the CLI is installed or updated. When Dreamina says the CLI is too old,
select **Update**. When a command is missing, update the extension.

## Settings

Change these in **Dreamina Settings**. New runs use the saved values.

![The Dreamina Settings dialog, signed in: Dreamina CLI with the installed version and Update; Account with the plan and Sign out; Request limits with Request timeout (seconds), Maximum upload size (MB), Maximum download size (MB), and Save limits; and Reload settings at the bottom.](docs/images/screenshots/settings-dialog.png)

| Setting                        | Default | Range      | What it limits                                                         |
| ------------------------------ | ------- | ---------- | ---------------------------------------------------------------------- |
| **Request timeout (seconds)**  | 1800    | 10 to 3600 | How long one run may take, from the first upload to the last download. |
| **Maximum upload size (MB)**   | 210     | 1 to 210   | Each image, video, or audio file uploaded to your Dreamina canvas.     |
| **Maximum download size (MB)** | 512     | 16 to 4096 | Each output file accepted.                                             |

## Models

Type any model name from your Dreamina model list in `model`, such as
`seedance_2.5`, or another name the list gives it, in any case. The node
sends the model's own name. Nothing in the extension lists or limits models.
Each node starts with a model and settings that run as they are:

| Node            | Runs models of kind | `model` starts at   | `arguments` starts at                                    |
| --------------- | ------------------- | ------------------- | -------------------------------------------------------- |
| Image: Generate | `image`             | `seedream_5.0_lite` | `{"ratio": "1:1", "resolution": "2K"}`                   |
| Video: Generate | `video`             | `seedance_2.0_mini` | `{"ratio": "16:9", "resolution": "720p", "duration": 4}` |
| Audio: Generate | `audio`             | `seed_audio_v1`     | `{"voice-name": "Jessie"}`                               |
| Image: Upscale  | none                | none                | `{"resolution": "2K"}`                                   |

The node reads your model list once while ComfyUI runs, and again when a name
is not found.

`arguments` is a JSON object of the model's settings by the CLI's names,
without dashes, such as `ratio`, `resolution`, `duration`, `count`,
`voice-name`, and `scenario`, with values the list gives, such as `720p`.
**Model: Info** lists every setting with its choices and limits.

Each run has a mode. Set it in `arguments` as `"mode"`, and `"scenario"` for
speech, or let the node choose. A model with one mode uses it. Otherwise:

- **Image: Generate** uses `t2i`, or `i2i` when images, references, or an
  Element are connected.
- **Video: Generate** uses `t2v` with nothing connected, `first_last_frame`
  with one or two images and nothing else, and `m2v` with anything else. Set
  `"mode": "m2v"` to use one or two images as references instead.
- **Audio: Generate** reads the prompt aloud (`text-reading`) with nothing
  connected, and dubs what is connected (`omni-dubbing`). `voice-name` fits
  text reading only: for dubbing, set `arguments` to `{}`.

## Credit ceiling

`credit_ceiling` is the most credits one run may cost. It is Dreamina's own
approval: the CLI runs nothing without one, and the extension never approves
an amount for you. Dreamina prices each run when it is saved and runs it only
within the ceiling. A run priced above it stops with nothing billed, and the
message gives the price to raise it to, or says Dreamina could not price it.
Each node's starting ceiling covers its starting model at its starting
settings, so a larger size, a longer video, or another model may need more.

A stopped run leaves an unrun draft on your canvas, which bills nothing and
which the extension never deletes. Unless `arguments` sets `count`, each run
asks for one output, so a model never makes and bills several by default.

## References and uploads

`references` carries what a Dreamina node made to the next, with no download
or upload: a paid node's `references` output, or **Element: Add**'s Element.
One connection reaches each `references` input. ComfyUI images, video, and
audio connected to `images`, `videos`, or `audio` are uploaded to your canvas
with each run, for free.

The model gets `references` first, then `images`, `videos`, and `audio`,
which matters for `first_last_frame`. Mark where each goes in the prompt with
`{{reference1}}`, `{{image1}}`, `{{video1}}`, or `{{audio1}}` for the first
item of each, and so on. A placeholder for an item that is not connected
stops the node. Write `\{{` for a `{{` the prompt should keep.

## Caching and reruns

- Change `run_number` to send the same run again. ComfyUI reuses a node's
  last result while none of its inputs change.
- Signing in to another account runs paid nodes again. Changing settings
  does not.
- Every run is sent once, and a lost reply is checked without a new run.
- Each run uploads its ComfyUI files again, and `references` go as they are.
- Dreamina has no cancel. Cancelling stops the wait, not the run: a run
  Dreamina accepted keeps going and is billed.

## Recover a generation

Every paid node records each run as soon as Dreamina accepts it. The run
keeps going, and is billed, after a cancel, a restart, or the **Request
timeout (seconds)**. Collect it with **Generation: Download** (press R to
list new runs). A record leaves the list once its outputs are collected,
when Dreamina no longer has the run, or after 30 days. Then look for it on
your canvas.

## The canvas

Every run goes on one canvas named **ComfyUI** in your Dreamina account, made
by the first run that needs it. The link in each node's `result` opens it,
with each run's prompt and outputs. The extension names this canvas in every
call, so your other Dreamina tools keep their own. If you delete it, the next
run makes a new one.

## Limits

The extension adds no limits of its own. Only the **Request limits** in
**Dreamina Settings** and the limits **Model: Info** reports apply. The
Dreamina CLI refuses an image over 30 MB before uploading it, and Dreamina
refuses a file outside its limits before anything is billed. Your Dreamina
plan sets your models and your credits.

## When a node stops

Paid nodes check these before uploading or sending anything. Image: Generate,
Video: Generate, and Audio: Generate stop when:

- `model` is empty, matches no model or several in your list, or makes
  another kind of output.
- The mode or scenario is not one the model has, or what is connected fits
  none of its entries.
- `arguments` is not a JSON object, names a setting the mode does not take,
  leaves out a required one, or gives a value outside its choices or limits.
- `prompt` is set twice, or is empty where the mode needs one.
- References are too few, too many, or of kinds the mode does not take, an
  Element is a frame, or a placeholder names an item that is not connected.
- A file is over the upload limit.
- The Dreamina CLI is missing or too old, or you are not signed in.

**Image: Upscale** stops when no image or more than 20 are connected, a
reference is not an image, or a setting is not one the upscale takes.
**Element: Add** stops when `main` is not one image, `title` is empty or too
long, `auxiliary` holds anything but images, or `voice` holds more than one
clip. **Generation: Download** stops when the chosen run is not recorded on
this server. **Model: Info** stops when `model` is empty or not in your model
list.

## Use from another extension

Another extension can call these nodes instead of copying a model's settings:

```python
clone = nodes.NODE_CLASS_MAPPINGS["DreaminaModelInfo"].PREPARE_CLASS_CLONE(None)
clone.hidden = io.HiddenHolder.from_dict({})
output = await clone.execute(model="seedance_2.5")
model = json.loads(output.args[0])
```

- Call a node on a class clone with an empty hidden holder, as above.
- A paid node takes `model`, `prompt`, and `arguments` as text, the last a
  JSON object of Dreamina's setting names, and `credit_ceiling` as a number.
  `images`, `videos`, and `audio` are lists of ComfyUI media, and
  `references` is what another Dreamina node returned.
- Set `credit_ceiling` on every call: the starting value fits only the
  starting model at its starting settings.
- A failed run raises an error whose `code` names its kind, such as
  `timeout` or `uncertain`. Check `code`, not the message text.
- Do not send a failed paid run again: it may have run and been billed.

## Update or remove

To update, replace the `custom_nodes/dreamina` folder, install its
`requirements.txt` with ComfyUI's Python, and restart. Open the updated
examples in a new tab. **Update** in **Dreamina Settings** updates the CLI.

To remove it, select **Sign out** if you want the sign-in gone, move the
folder out of `custom_nodes`, and restart. The
[private folder](#sign-in-and-access), the CLI, and its skill folder,
`~/.agents/skills/dreamina-canvas-cli`, stay until you delete them.

## Development

### Setup

Point the checks at ComfyUI in `.mise.local.toml`, which Git ignores:

```toml
[env]
COMFYUI_PATH = "/path/to/ComfyUI"
COMFYUI_PYTHON = "/path/to/ComfyUI/.venv/bin/python"
```

Then install the tools, dependencies, Semgrep rules, and Git hooks:

```shell
mise trust && mise run repo:setup
```

### Generated files

```shell
mise run repo:deps:export          # Regenerate requirements.txt from pyproject.toml
mise run comfy:frontend:build      # Build the browser files
mise run comfy:workflows:build     # Build the example workflows
```

The example workflows are generated from `scripts/workflows/descriptions/`:
one module per category, the notes in `notes.py`, and the titles in
`texts.py`. The build reads the node definitions through ComfyUI's Python. It
also writes every subgraph to `subgraphs/`, which ComfyUI lists under
**Subgraph Blueprints** in its node library.

### Full check

```shell
mise run repo:check                # Run every check below
```

This runs `repo:deps:verify`, `repo:format:check`, `repo:lint`, `repo:type`,
`comfy:frontend:check`, `comfy:nodes:check`, `comfy:workflows:check`,
`repo:security`, `repo:licenses`, and `repo:links:external`.

### Format

```shell
mise run repo:format               # Format Python, pyproject.toml, web, and Markdown files
mise run repo:format:check         # List files that need formatting
```

This uses Ruff for Python, pyproject-fmt for `pyproject.toml`, and Prettier for
web and Markdown files.

### Lint

```shell
mise run repo:lint                 # Run every linter
```

- `repo:lint:policy`: repository structure, naming, and function rules.
- `repo:lint:python`: Ruff, the custom Python rules, import-linter, pydoclint,
  interrogate, deptry, and vulture.
- `repo:lint:frontend`: ESLint, naming, stylelint, knip, madge, and jscpd.
- `repo:lint:shell`, `repo:lint:hooks`, and `repo:lint:mise`: shell syntax,
  ShellCheck, shfmt, and the shell rules.
- `repo:lint:docs`: markdownlint, typos, and local links.
- `repo:lint:quality`: the quality tools and their configuration.

### Types

```shell
mise run repo:type                 # Check Python and TypeScript types
```

This runs basedpyright in strict mode against your ComfyUI installation, and
`tsc` for the browser code.

### Generated-file checks

```shell
mise run comfy:frontend:check      # The browser files match their source
mise run comfy:nodes:check         # The help pages and menus match the nodes
mise run comfy:workflows:check     # The workflows match their descriptions, and the README links each one
```

The workflow check also requires every node to appear in at least one
workflow.

### Security and licenses

```shell
mise run repo:security             # Run the secret, code, and dependency scanners
mise run repo:licenses             # Check dependency licenses
```

`repo:security` runs Gitleaks, Bearer, Bandit, the Python and Bun advisory
audits, Semgrep with the pinned rules, and CodeQL for Python and the browser
code.

### Git hooks

`mise run repo:setup` installs the hooks:

- **pre-commit** checks for private files and staged secrets, then runs the
  source, formatting, type, and browser-file checks.
- **commit-msg** checks the [conventional
  commit](https://www.conventionalcommits.org/) format, `type(scope): subject`.
- **pre-push** runs the full check.

To skip a run, set `SKIP_HOOKS=1`. To skip only part of it, set `SKIP_LINT=1`
(the pre-commit checks), `SKIP_ENV_CHECK=1` (the private-file check), or
`SKIP_COMMITLINT=1` (the commit message check).

### Test a change

Testing is manual: restart ComfyUI after Python changes, or rebuild the
browser files and reload after browser changes, then run the affected
workflows at the smallest sizes and shortest durations.

### Import rules

Each package imports only the packages below it:

```text
src.nodes
src.comfy
src.dreamina | src.settings
src.storage
src.types
src.config
```

- ComfyUI is imported only in `src/nodes/`, `src/comfy/`, and the package's
  `__init__.py`.
- Every Dreamina CLI call is in `src/dreamina/`. `src/dreamina/cli.py` is the
  one place that starts the CLI, and `src/dreamina/installer.py` the one place
  that downloads and runs its installer.
- Every message and every other fixed value, such as a limit, a file name, or
  a route, is a constant in `src/config/`. The dialog text is in
  `web/scripts/text.ts`.
- The import contracts in `pyproject.toml` enforce these rules.
- Node names, descriptions, and tooltips are in each node's `io.Schema` call,
  and the tooltips of the inputs every paid node shares are in
  `src/config/inputs.py`. A model's own settings come from your model list,
  read when a node runs.

### Function names

Every function in `src/`, `scripts/`, and `__init__.py` starts with a verb from
the table in `rules/NAMING.md`, or is an `is_` or `has_` predicate. The verbs
are `read`, `save`, `send`, `parse`, `build`, `create`, `choose`, `list`,
`find`, `plan`, `rank`, `validate`, `describe`, `format`, `get`, `set`,
`reset`, `decode`, `encode`, `sanitize`, `wait`, `register`, `delete`,
`download`, `measure`, and `place`. In each module and class, private
functions come first, `__all__` lists no private name, and a function only
its own module uses is private. `repo:lint:policy` checks all four.

### Images

The README's and this guide's images are in `docs/images/`:

- `brand/banner.svg`, `diagrams/node-map.svg`, and the four `badges/*.svg`
  files are SVG files; edit them as text. They use near-black `#080A12`,
  surfaces `#121522`, hairlines `#252A3A`, light text `#EEF3FF`, muted text
  `#8C93A8`, aqua `#60D5E6`, the gradient `#7FE3F0` to `#2F80FF` to
  `#6366F1`, and yellow `#F0FF41` for the mark's socket and one sparkle in
  each rail. Headings use Helvetica Neue with tight spacing; labels use a
  monospace font in wide-spaced capitals. The badges name the ComfyUI,
  frontend, and Python versions and the license; update them when those
  change.
- `brand/logo.png` is the extension's mark: a tilted four-point star,
  orange at its top point through aqua to blue, cut by a curved gap, with a
  yellow socket at the end of its right point, at 400 × 400 pixels on a
  transparent background. Its source is `.artifacts/brand/logo.svg`, which
  Git ignores; render it with `rsvg-convert` and compress it with `oxipng`.
  The banner draws the same mark between two rails of small sparkles, and
  `pyproject.toml` names `brand/logo.png` as the Registry icon.
- The node map has one card for each kind of node. A blue square marks a
  node that starts a paid run, a hollow square one that bills nothing, and
  an arrow an output that feeds the next node.
- `screenshots/video-02-workflow.png` is video-02 at 100% zoom, with link
  midpoint markers off, in 256 colors.
- `screenshots/video-generate-node.png` is a new **Video: Generate** node,
  420 pixels wide, at 100% zoom, with a prompt typed in.
- `screenshots/settings-dialog.png` is the **Dreamina Settings** dialog,
  signed in, with default request limits.

The star is this extension's own drawing, not Dreamina's logo. Keep each
image under 100 KB, and give it alt text.

### Change text

- **A message:** edit its constant in `src/config/messages/`, and its entry
  under [troubleshooting](#troubleshooting) if it has one.
- **A node's labels or tooltips:** edit its `io.Schema` call in `src/nodes/`,
  or `TOOLTIPS` in `src/config/inputs.py` for the inputs every paid node
  shares, then its help page in `web/docs/`.
- **The dialog:** edit `web/scripts/text.ts`, then rebuild the browser files.
- **A workflow's notes:** edit `scripts/workflows/descriptions/notes.py`; for
  titles, `texts.py`; for nodes, models, or prompts, the workflow's module. Then
  rebuild the workflows.
- **A node's starting model or settings:** edit `src/config/models.py`, then
  the table under [models](#models), the node's help page, and the examples
  that rely on them.

## Package and publish

The Comfy Registry package is made with
[comfy-cli](https://github.com/Comfy-Org/comfy-cli). These steps use version
1.20.0.

1. Create a publisher and a publishing key in the
   [Comfy Registry](https://docs.comfy.org/registry/publishing).
2. In `pyproject.toml`, set `[tool.comfy].PublisherId` to your publisher ID, add
   `Repository` under `[project.urls]`, and set `[project].version`. Use a new
   version number for each release.
3. Rebuild the generated files:

    ```sh
    mise run repo:deps:export
    mise run comfy:frontend:build
    mise run comfy:workflows:build
    ```

4. Commit everything. The packer takes only files Git tracks, and
   `.comfyignore` leaves out development files.
5. Build and check the package:

    ```sh
    mise run comfy:release:package
    ```

    This runs the full check, builds `node.zip` with `comfy node pack`, lists
    its contents, and scans it for secrets.

6. Publish:

    ```sh
    mise run comfy:release:publish
    ```

    This repeats the package checks, then asks for the publishing key.

7. Install the published version with ComfyUI Manager, and check that the nodes,
   menus, help pages, and templates load.

Publishing rebuilds the archive from the checkout, so publish the same commit
you packaged.

## Troubleshooting

Most messages say what to do. These need more.

### ComfyUI could not find the Dreamina CLI

Select **Install** in **Dreamina Settings**. For a CLI in another folder, set
`DREAMINA_CANVAS_INSTALL_DIR` to it where ComfyUI starts, and restart.

### The Dreamina installer finished, but the Dreamina CLI does not answer

Run `dreamina-canvas version` in a terminal, as the user that runs ComfyUI.
On Windows, the CLI runs only on 64-bit Intel and AMD processors.

### Dreamina no longer accepts this version of the Dreamina CLI

Select **Update**. If a command is still missing afterward, update the
extension.

### You are not signed in to Dreamina

Approve the sign-in before its link expires, as the dialog shows. ComfyUI
must run as the computer user who signed in.

### Open Dreamina Settings from a browser on the ComfyUI computer, at a localhost address

For remote access or multi-user mode, run `dreamina-canvas auth login` on the
server instead, as the user that runs ComfyUI.

### The model is not in your Dreamina model list

Copy a name the message suggests, or check it with **Model: Info**. Your plan
may not offer the model, or Dreamina may have renamed or removed it.

### Your Dreamina model list holds no models of this kind

Your Dreamina plan offers none. Check it on dreamina.capcut.com.

### The Dreamina settings file has an unknown setting

Delete the settings file in the [private folder](#sign-in-and-access) to
return to the defaults.

### A Dreamina state file is larger than expected

Delete it. A run record can go once you have its outputs.
````

Notes on Step 3:

- **What each node sends** keeps F's one bullet per node, with the three
  generation nodes in one bullet because they send the same way. `result`
  is named by what `build_result_document` writes: the canvas link, the
  request ID, and the node. F's closing sentence is dropped, since **Caching
  and reruns** says every run is sent once. Image: Upscale's bullet is
  [12-node-upscale.md](12-node-upscale.md#step-2-the-upscale-operation)'s
  flow; Element: Add's is [13-node-element.md](13-node-element.md#step-3-element-add)'s.
- **Sign-in and access** takes F's **Keys and access** shape: how to sign in,
  where the sign-in lives, the local-only rule and its way around, and the
  private folder table with `DREAMINA_COMFY_STATE_DIRECTORY`. As built, every
  Dreamina Settings route is local-only, reading too, and multi-user mode
  shows the dialog with changes disabled (`src/settings/access.py`); the
  folder must lie outside ComfyUI, the extension, and their media folders
  (`PRIVATE_STATE_LOCATION`)
  ([01-decisions.md](01-decisions.md#sign-in-and-privacy),
  [05-foundation.md](05-foundation.md#step-4-storage-constants)). The dialog's
  own words are [16-frontend.md](16-frontend.md#step-3-browser-text)'s
  `account.code` and `account.notice`.
- **The Dreamina CLI** is new: where the pack looks
  ([01-decisions.md](01-decisions.md#the-cli-on-the-persons-computer)),
  `DREAMINA_CANVAS_INSTALL_DIR`, **Install** and **Update**
  ([05-foundation.md](05-foundation.md#step-18-the-installer)), the CLI
  page's one-line commands for a terminal, as the README's **Install** gives
  them ([research/cli.md](research/cli.md#release-and-install)), and the
  version gate, checked once and again after an install or update, since
  `validate_cli` keys a passed check by the binary's path and modification
  time. The dialog shows no command.
- **Settings** copies [05-foundation.md](05-foundation.md#step-3-settings-constants)'s
  defaults and ranges: the upload maximum is 210 MB, the first whole number
  of decimal megabytes above `seedance_2.5`'s 209,715,200-byte reference
  video. The labels are
  [16-frontend.md](16-frontend.md)'s. The screenshot's alt text is 19's, with
  16's sentence-case labels and the parts 16 shows.
- **Models** copies the starting values of
  [01-decisions.md](01-decisions.md#choosing-a-model) and the mode rule of
  [01-decisions.md](01-decisions.md#how-the-mode-is-chosen), including that
  `"mode": "m2v"` makes one or two images references, as one bullet per
  node, with `src/dreamina/modes.py`'s rule that a model with one mode uses
  it. Audio's bullet says `voice-name` fits text reading only, as the
  `arguments` tooltip does. The claim that `ratio`, `resolution`, and
  `duration` have no default on Dreamina is dropped: no run checked it, and
  a required setting left out is a refusal under **When a node stops**,
  where the checks are listed once.
- **Credit ceiling** is new, from [01-decisions.md](01-decisions.md#credits)
  and [02-dreamina-contract.md](02-dreamina-contract.md#credit-approval): the
  approval Dreamina requires, why every run carries it, a ceiling below the
  price stopping with nothing billed, the draft left on the canvas, and
  `--count 1`, said as "one output". It names no number, and says the
  starting ceiling covers the starting model, since `DEFAULT_CEILINGS` rounds
  each quote up to the next 10. If run C-5 or a
  Part 0 finding in [21-test-runs.md](21-test-runs.md) changes how a ceiling
  of 0 or a missing price behaves, this section follows.
- **References and uploads** takes the place of F's **Files and uploads**,
  from [01-decisions.md](01-decisions.md#media-references-and-placeholders)
  and [07-media.md](07-media.md#step-8-references-and-placeholders). It says
  one connection reaches each `references` input, which is why
  video-02 sends its product through `images`.
- **Caching and reruns** keeps F's five bullets: `run_number`, the account
  in place of the key, sent once, uploads per run, and Dreamina's missing
  cancel ([02-dreamina-contract.md](02-dreamina-contract.md#waiting-and-recovery)).
- **Recover a generation** is F's paragraph with Dreamina's facts: a record
  per accepted run, no cancel, a record deleted when Dreamina no longer has
  the run, and the pack's own 30 days, after which a collect deletes the
  record with `GENERATION_EXPIRED` (`RECORD_RETENTION_SECONDS`;
  [14-node-download.md](14-node-download.md#decisions)). How long Dreamina
  itself keeps a submission is still open
  ([research/cli.md](research/cli.md#open-questions), question 10).
- **The canvas** is new, from [01-decisions.md](01-decisions.md#the-canvas):
  one canvas, its link in each `result` (the dialog has none), `--project-id`
  on every call said in plain words, and a deleted canvas replaced by the
  next run: a run that finds it gone stops with `CANVAS_MISSING` and asks
  for another run, so "made again before anything is billed" is not said.
- **Limits** keeps F's paragraph, with the file limits Model: Info reports
  ([research/catalog.md](research/catalog.md#file-limits)), the CLI's 30 MB
  image limit (`UPLOAD_INVALID`), and the plan sentence in place of fal's
  concurrency link.
- **When a node stops** lists the checks the code makes, shared checks said
  once: 06's model, mode, and argument refusals, 07's reference and
  placeholder refusals and upload limit, and the free nodes' checks in 12,
  13, 14, and 15. It names no message text. When a plan adds or removes a
  refusal, this list changes in the same commit.
- **Use from another extension** is F's section re-valued from
  [23-live-shopping-provider.md](23-live-shopping-provider.md), which owns
  the contract: media as lists, `references` as returned, `credit_ceiling` on
  every call, and the error `code`.
- **Update or remove** adds the CLI, the skill folder its installer writes,
  and sign-out ([research/cli.md](research/cli.md#release-and-install)).
- **Development** and **Package and publish** are F's word for word, with
  names changed ([20-release.md](20-release.md) follows this), except that
  **Test a change** runs the smallest sizes and shortest durations, the
  owner's test rule. **Function
  names** also lists the verbs of `quality/config/repository/functions.json`,
  so a reader sees them without opening the rules. **Images** is
  [19-brand-assets.md](19-brand-assets.md#text-for-advanced)'s text word for
  word.
- **Troubleshooting** has nine entries. `MODEL_LIST_UNREADABLE`'s entry is
  dropped: its message already says everything the entry did. Each heading is the first
  sentence of a message the code shows, without its placeholders, copied
  from its owning plan:

  | Heading | Constant and plan |
  | ------- | ----------------- |
  | ComfyUI could not find the Dreamina CLI | `CLI_MISSING`, [08-runs.md](08-runs.md) |
  | The Dreamina installer finished, but the Dreamina CLI does not answer | `INSTALL_NO_ANSWER`, [05-foundation.md](05-foundation.md#step-16-installer-and-sign-in-messages) |
  | Dreamina no longer accepts this version of the Dreamina CLI | `UPGRADE_REQUIRED`, [08-runs.md](08-runs.md); the entry also covers `CLI_OUTDATED` and `CLI_CHANGED` |
  | You are not signed in to Dreamina | `SIGN_IN_REQUIRED`, [08-runs.md](08-runs.md) |
  | Open Dreamina Settings from a browser on the ComfyUI computer, at a localhost address | `LOCAL_CONNECTION_REQUIRED`, [05-foundation.md](05-foundation.md#step-7-foundation-messages) |
  | The model is not in your Dreamina model list | `MODEL_UNKNOWN`, [06-model-check.md](06-model-check.md) |
  | Your Dreamina model list holds no models of this kind | `MODEL_LIST_EMPTY`, 06, its `{made}` written as "of this kind" |
  | The Dreamina settings file has an unknown setting | `SETTING_UNKNOWN`, 05 |
  | A Dreamina state file is larger than expected | `STATE_FILE_SIZE`, 05 |

  Each heading is the first sentence of its message constant. A heading
  follows its message when the message changes. When a test run captures the
  fields of a failure that has no message yet (too few credits, a plan that
  cannot use a model, the safety check) and its fix needs more than the
  message can hold, its entry replaces the least needed entry above. No entry
  gives a price or a number of credits.
- Length: 544 lines, within F's 546.

## Step 4: Help pages

One page per node, `web/docs/<node ID>.md`, written in the node's milestone
with the node, because `comfy:nodes:check` refuses a node without a page, a
page without a registered node, and a table row that names a socket the node
lacks. The node plans own each page's content; this plan owns the shared
format.

| Page                             | Node                 | Content written in                                             | Milestone           | Reference page (lines)          | Last line                                                     |
| -------------------------------- | -------------------- | -------------------------------------------------------------- | ------------------- | ------------------------------- | ------------------------------------------------------------- |
| `DreaminaImageGenerate.md`       | Image: Generate      | [09-node-image.md](09-node-image.md#step-4-help-page)           | Image               | `FalImageGenerate.md` (44)      | `[Dreamina](https://dreamina.capcut.com/ai-tool/home)`         |
| `DreaminaImageUpscale.md`        | Image: Upscale       | [12-node-upscale.md](12-node-upscale.md#step-6-help-page)       | Upscale             | `FalImageGenerate.md` (44)      | `[Dreamina](https://dreamina.capcut.com/ai-tool/home)`         |
| `DreaminaVideoGenerate.md`       | Video: Generate      | [10-node-video.md](10-node-video.md)                            | Video and downloads | `FalVideoGenerate.md` (50)      | `[Dreamina](https://dreamina.capcut.com/ai-tool/home)`         |
| `DreaminaAudioGenerate.md`       | Audio: Generate      | [11-node-audio.md](11-node-audio.md)                            | Audio               | `FalAudioGenerate.md` (46)      | `[Dreamina](https://dreamina.capcut.com/ai-tool/home)`         |
| `DreaminaElementAdd.md`          | Element: Add         | [13-node-element.md](13-node-element.md#step-6-help-page)       | Elements            | `FalFileAdd.md` (35)            | `[Dreamina Canvas CLI](https://dreamina.capcut.com/canvas-cli)` |
| `DreaminaGenerationDownload.md`  | Generation: Download | [14-node-download.md](14-node-download.md#step-5-help-page)     | Video and downloads | `FalRequestDownload.md` (37)    | `[Dreamina Canvas CLI](https://dreamina.capcut.com/canvas-cli)` |
| `DreaminaModelInfo.md`           | Model: Info          | [15-node-model-info.md](15-node-model-info.md#step-6-help-page) | Audio               | `FalModelInfo.md` (65)          | `[Dreamina Canvas CLI](https://dreamina.capcut.com/canvas-cli)` |

Dreamina publishes no documentation page per feature, as fal does. So a
paid node's page links Dreamina's app, where its models are, and a free
node's page links the Dreamina Canvas CLI page, because it works through the
CLI's canvas, records, or model list. These are the links 09 to 15 write;
`repo:links:external` checks each on push.

The shared format, F's shipped pages' (`F/web/docs/FalImageGenerate.md` is
the model):

1. `# <Display name>`, then one short paragraph: what the node does, naming
   Dreamina, and what it outputs for other nodes.
1. `## Inputs`: a `| Input | What it takes |` table in node order. The first
   cell is the backticked input ID, which `scripts/nodes/check.py` checks
   with ``^\| `([a-z_.]+)` \|``. A generation node's table lists its inputs
   in node order: `images`, then `videos` and `audio` where the node has
   them, `references`, `model`, `credit_ceiling`, `run_number`, `prompt`,
   and `arguments`. A model's own settings go in `arguments`, so no page has
   a row for one, such as `ratio`.
1. One optional paragraph after the table: where model names and settings
   come from (**Model: Info**), the check before paying, and the mode rule.
1. `## Outputs`: a `| Output | What it carries |` table, saying when an output
   is empty and its nodes skipped.
1. Optional extra tables, such as Model: Info's keys. Their first cells are
   not backticked, because the check reads every backticked first cell as a
   socket name.
1. `## Use`: a numbered list of two to five steps ending with **Run**, then a
   closing paragraph where the node needs one, such as what a cancel does,
   then "Example: **<slug>**." or "Examples: **<slug>** and **<slug>**." with
   17's slugs.
1. The last line, from the table above.

Every page is wrapped at 80 columns, and a JSON block is in Prettier's form.
Rows that most pages share use the same words, as 09's page writes them:

| Input            | What it takes                                                                                              |
| ---------------- | ---------------------------------------------------------------------------------------------------------- |
| `images`         | Images to edit or combine, uploaded with the run.                                                          |
| `references`     | Images from other Dreamina nodes, and Elements, sent with no upload.                                       |
| `model`          | The model's Dreamina name, such as `<example>`. The default is `<starting model>`.                          |
| `credit_ceiling` | The most credits the run may cost. A run that costs more stops, and nothing is billed.                     |
| `run_number`     | Change it to send the same run again.                                                                      |
| `prompt`         | What to make or change. `{{image1}}` or `{{reference1}}` points at an input.                               |
| `arguments`      | The model's settings as JSON, under Dreamina's flag names, such as `{"ratio": "1:1", "resolution": "2K"}`. |
| `references`     | (output) What the run made, on your Dreamina canvas, for the next Dreamina node.                           |
| `result`         | (output) Dreamina's record of the run as JSON, with a link to your canvas.                                 |

Each page is no longer than its reference page in the table above, in lines
and about as long in table cells
([research/owner-rules.md](research/owner-rules.md#readme-advanced-and-help-pages)).
No page shows a price, a number of credits, or a sign-in step.

The examples each page names, from
[17-scripts-and-workflows.md](17-scripts-and-workflows.md#summary):

| Page                 | Examples                                                                                                         |
| -------------------- | ---------------------------------------------------------------------------------------------------------------- |
| Image: Generate      | image-01-design-a-host, image-02-edit-a-product-photo, image-03-upscale-a-poster                                 |
| Image: Upscale       | image-03-upscale-a-poster                                                                                        |
| Video: Generate      | video-01-animate-a-host, video-02-film-a-product-ad, video-03-keep-a-host-across-shots, video-04-recover-a-video |
| Audio: Generate      | audio-01-voice-a-script, audio-02-give-a-host-a-voice                                                            |
| Element: Add         | video-03-keep-a-host-across-shots                                                                                |
| Generation: Download | video-04-recover-a-video                                                                                         |
| Model: Info          | audio-01-voice-a-script                                                                                          |

A page whose example is built in a later milestone gets that example in that
milestone, as in F: Image: Generate's page names image-01 and image-02 from
the Image milestone and image-03 from the Upscale milestone, and Video:
Generate's names video-03 from the Elements milestone. A page's cancel
paragraph names **Generation: Download** only from the Video and downloads
milestone, when that node ships, as 09, 12, and 14 say.

## Step 5: Screenshots

Three screenshots, taken in the Documentation and brand milestone with the
owner's approval to start ComfyUI with the finished nodes. Their files,
sizes, views, and the capture procedure are in
[19-brand-assets.md](19-brand-assets.md#step-4-screenshots): F's method, full
color at a device scale of 1, in an 1,800 by 1,200 viewport, cropped to the
element, compressed with `oxipng`, and each under 100 KB, reduced to 256
colors without dithering only when a crop stays over 100 KB. The same session
re-measures the page as
[17-scripts-and-workflows.md](17-scripts-and-workflows.md#re-measure-the-page-on-frontend-1527)
says.

| File                                   | Where it appears           | Alt text                                                       |
| -------------------------------------- | -------------------------- | -------------------------------------------------------------- |
| `screenshots/settings-dialog.png`      | ADVANCED **Settings**      | The text in [Step 3](#step-3-advanced-guide)                   |
| `screenshots/video-generate-node.png`  | README **Models**          | The text in [Step 2](#step-2-readme-text)                      |
| `screenshots/video-02-workflow.png`    | README **Example workflows** | The text in [Step 2](#step-2-readme-text)                    |

After the captures:

1. Correct each alt text in the README and ADVANCED to what the capture
   shows, with the inputs in node order and the labels as the dialog writes
   them, and give 19 the same text.
1. The settings dialog shows no personal data: its account part shows only
   "Signed in to Dreamina." and the plan, so nothing is replaced.
1. The node screenshot shows the starting model the catalog gives,
   `seedance_2.0_mini`, with its starting `arguments`.
1. The workflow screenshot's alt text names only the groups the crop shows,
   with 17's group names, in 19's form.

Retake `video-generate-node.png` when Video: Generate's own inputs change,
`settings-dialog.png` when the dialog changes, and the workflow image when
video-02's notes or groups change; correct the alt text with each.

## When each part is added

The milestones are [README.md](README.md#build-order)'s. Rows go in the order
of the tables above: `NODE_TYPES` order for nodes and slug order for
workflows.

| Milestone                                        | Documentation change                                                                                                                                                 |
| ------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Tooling                                          | [Step 1](#step-1-readme-start), with the banner and badges of [19-brand-assets.md](19-brand-assets.md#step-1-badges-and-banner): the banner, badges, purpose, **Contents**, **Requirements**, **Install**, and **License** |
| Foundation                                       | None                                                                                                                                                                 |
| Frontend                                         | README: **Requirements** loses its CLI line, and **Install** ends with the CLI paragraph that names **Dreamina Settings** and gives the one-line commands             |
| Free reads and contract checks; Model check; Media and runs | None                                                                                                                       |
| Model: Info                                      | None: the node is committed unregistered, and its help page and README row wait for the Audio milestone ([15-node-model-info.md](15-node-model-info.md#milestones)) |
| Image                                            | README: **Example workflows** with the image-01 and image-02 rows and the paragraph under the table; **Nodes** with its sentence and the Image: Generate row; both in **Contents**. Image: Generate's help page |
| Upscale                                          | README: the image-03 row; the Image: Upscale row. Its help page; image-03 on Image: Generate's page                                                                  |
| Audio                                            | README: the audio rows; the Audio: Generate and Model: Info rows. Their help pages                                                                                   |
| Video and downloads                              | README: the video-01, video-02, and video-04 rows; the Video: Generate and Generation: Download rows. Their help pages; the **Generation: Download** sentence on the Image: Generate, Image: Upscale, and Audio: Generate pages |
| Elements                                         | README: the video-03 row, between video-02 and video-04; the Element: Add row. Its help page; video-03 on Video: Generate's page                                      |
| Documentation and brand                          | README: **First run**, **Models**, **How a run works**, **Development**, **Common problems**, the node map, the two screenshots, the update link in **Install**, the full **Contents**. `ADVANCED.md` whole. The screenshots ([Step 5](#step-5-screenshots)) |

Every milestone's push passes the hooks: each node milestone registers its
nodes with their help pages, README rows, and examples together, and Model:
Info joins `NODE_TYPES` only with audio-01, the example that places it.
