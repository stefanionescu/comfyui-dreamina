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
