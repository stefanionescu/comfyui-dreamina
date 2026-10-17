# Release

This plan publishes a version of the pack to the Comfy Registry, where ComfyUI
Manager finds it. It uses the `comfy:release:package` and
`comfy:release:publish` tasks, copied with the rest of `.mise/tasks/` in
[03-repository-setup.md](03-repository-setup.md#step-1-copy-the-fal-packs-files).
It follows the fal pack's release plan
(`F=/Users/dr_stone/Documents/work/comfyui-fal`, commit `cef8b6e`,
`plans/20-release.md`), with Dreamina's values. F's plan found the BytePlus
and OpenRouter packs unpublished on 2026-10-15 (`F/plans/20-release.md:9-11`).

Readers: the owner, who decides when to publish and runs the publish step,
and the engineer or agent who prepares the release.

Publishing is public and cannot be taken back: a published version stays
listed, and a fix is a new version. Release comes after the example runs in
[21-test-runs.md](21-test-runs.md), as [README.md](README.md#build-order)
orders it. Nothing in this plan spends credits: every Dreamina call here is a
free read.

## Contents

- [Decisions this plan makes](#decisions-this-plan-makes)
- [One-time setup](#one-time-setup)
- [What the Registry flags](#what-the-registry-flags)
- [Step 1: Check the CLI release and the models the release names](#step-1-check-the-cli-release-and-the-models-the-release-names)
- [Step 2: Re-check the node IDs](#step-2-re-check-the-node-ids)
- [Step 3: Refresh generated files](#step-3-refresh-generated-files)
- [Step 4: Set the version](#step-4-set-the-version)
- [Step 5: Commit](#step-5-commit)
- [Step 6: Package](#step-6-package)
- [Step 7: Publish](#step-7-publish)
- [Step 8: Tag and push](#step-8-tag-and-push)
- [Step 9: Verify in a clean ComfyUI](#step-9-verify-in-a-clean-comfyui)
- [Release checklist](#release-checklist)
- [Names this plan uses from other plans](#names-this-plan-uses-from-other-plans)

## Decisions this plan makes

| Question                                        | Decision                                                                                       | Why                                                                                                                  |
| ----------------------------------------------- | ---------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| Which Registry ID?                              | `dreamina`, the `[project].name` and install folder                                            | [01-decisions.md](01-decisions.md#names-and-identifiers); free on 2026-10-16. The owner confirms it before the first publish, because an ID never changes after it |
| Who publishes?                                  | The owner, typing the Registry key at a hidden prompt                                          | The owner's rule; no `PublisherId` until then ([research/owner-rules.md](research/owner-rules.md#commits-and-git))    |
| What ships?                                     | F's archive list, from F's `.comfyignore`, copied unchanged                                    | The pack's file set matches F's; `.comfyignore` already keeps `plans/` and every development file out                 |
| Can the archive hold the Dreamina CLI or skill? | No, and Step 6 checks it                                                                       | The pack never redistributes either ([research/owner-rules.md](research/owner-rules.md#rules-added-for-dreamina))     |
| How is the archive scanned for secrets?         | gitleaks' default rules                                                                        | No API key exists ([03-repository-setup.md](03-repository-setup.md#step-6-re-value-the-quality-configuration))        |
| What if the scanner flags the installer route?  | With the owner's decision, a patch version drops **Install** and **Update**; the README and ADVANCED keep the one-line commands ([01-decisions.md](01-decisions.md#decisions-the-owner-should-confirm) records the owner keeping the button) | Downloading and running an installer is the one scanner pattern the pack keeps on purpose                          |
| Where is the clean install checked?             | A separate ComfyUI 0.37.2 in `/Users/dr_stone/ComfyUI-Installs/release-check-dreamina`, on port 8189 | Kept apart from the development installation and from F's release check folder                                  |

## One-time setup

Nothing here blocks building or local use. As in F, `pyproject.toml` has no
`PublisherId` and no project addresses until the owner decides to publish.
[18-documentation.md](18-documentation.md) writes the **Package and publish**
part of `ADVANCED.md` with this pack's values.

What was known on 2026-10-16:

| Item                | State                                                                                                                                                                      |
| ------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GitHub repository   | The local `origin` remote points at `https://github.com/stefanionescu/comfyui-dreamina.git`. Whether the repository exists, and its description, were not read for this plan; [22-owner-setup.md](22-owner-setup.md) confirms them |
| Registry ID         | `dreamina`, the `[project].name`, also the install folder (`custom_nodes/dreamina`). `https://api.comfy.org/nodes/dreamina` answered 404, and a Registry search for "dreamina" found nothing ([01-decisions.md](01-decisions.md#names-and-identifiers)) |
| Registry publisher  | `https://api.comfy.org/publishers/stefanionescu` answered on 2026-10-15: display name "Stefan", created 2026-09-08, `PublisherStatusActive`, no nodes (`F/plans/20-release.md:47`). Whether it is the owner's is not confirmed |
| Related packs       | No Registry pack is named "dreamina". The Jimeng packs `ComfyUI-Jimeng-API` and `ComfyUI-WBLESS` and 21 Seedance packs exist; none uses a `Dreamina` node prefix ([01-decisions.md](01-decisions.md#node-id-clashes)) |

The name `dreamina` is Dreamina's own product name, and also the name of
ByteDance's mainland China CLI for Jimeng
([research/terms.md](research/terms.md#4-rejected-routes)), so a pack listed
as `dreamina` can read as ByteDance's own. The owner chose it knowingly, as O
installs as `openrouter` (O commit `783d103`) and F as `fal-ai`: ComfyUI names
the node badges and the **Browse Templates** group after the install folder.
[01-decisions.md](01-decisions.md#decisions-the-owner-should-confirm) keeps
`comfyui-dreamina` as the alternative until the first publish. The Registry and
ComfyUI Manager show the display name **Dreamina** and the description from
`[project]` ([03-repository-setup.md](03-repository-setup.md#step-4-edit-pyprojecttoml)):
"Use Dreamina's image, video, and audio models in ComfyUI with your own
Dreamina account." It says the person brings their own account and claims no
link with Dreamina, and it stays as written. The README names the pack as a
ComfyUI extension that runs Dreamina models, and the logo is a redrawn star,
not Dreamina's artwork, because the terms grant no right to Dreamina's marks
([research/terms.md](research/terms.md#5-trademark)). The repository keeps the
name `comfyui-dreamina`, so its addresses below say `comfyui-dreamina`.

The owner sets the GitHub settings, as for the other packs. They use the
description pattern "ComfyUI extension for … models" (F's is "ComfyUI
extension for fal.ai models", `F/plans/20-release.md:45`), no topics, and no
homepage. No social preview image is uploaded; the pack's image set has none
([01-decisions.md](01-decisions.md#brand-and-images)), so GitHub shows its own
card.

When the owner decides to publish, they do four things once.

First, make sure `main` is on GitHub. The owner asked during F's build for
every commit to be pushed at once (F row 226), and
this pack follows that rule, so `main` is usually there already. If it is not:

```sh
git push -u origin main
```

The pre-push hook runs `mise run repo:check`: every local check, the node and
workflow checks, the security scans, and the external link check. Any failure
stops the push. Pushing makes the source public if the repository is public.
The `Icon` address in `[tool.comfy]` points at `main` on GitHub, so the
Registry shows the logo only after `main` holds it.

Second, add the repository addresses to `[project]` in `pyproject.toml`,
directly after `dependencies`:

```toml
urls.Issues = "https://github.com/stefanionescu/comfyui-dreamina/issues"
urls.Repository = "https://github.com/stefanionescu/comfyui-dreamina"
```

`pyproject-fmt` rewrites a `[project.urls]` table into these dotted keys,
sorted by name, so writing them this way keeps `repo:format:check` passing.
TOML reads both forms the same, so comfy-cli sends the same addresses to the
Registry. The Registry reads `Issues`, not the `Bug Tracker` key some examples
use.

Third, choose the publisher. Sign in to `registry.comfy.org` with the owner's
account. If the publisher `stefanionescu` is listed as the owner's, use it.
Otherwise create a publisher; `stefanionescu` is taken, so the new
publisher's ID replaces `stefanionescu` in the `PublisherId` line below. A
publisher ID is public, committed, and cannot be renamed. Use the same
publisher as F's pack if F has been published by then. Add it to the existing
`[tool.comfy]` table, which by then holds `DisplayName` and
`requires-comfyui` from
[03-repository-setup.md](03-repository-setup.md#step-4-edit-pyprojecttoml)
and `Icon` from [19-brand-assets.md](19-brand-assets.md):

```toml
[tool.comfy]
PublisherId = "stefanionescu"
DisplayName = "Dreamina"
Icon = "https://raw.githubusercontent.com/stefanionescu/comfyui-dreamina/main/docs/images/brand/logo.png"
requires-comfyui = ">=0.37.2"
```

| Key                | Value and why                                                                                                                                  |
| ------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| `PublisherId`      | The owner's publisher                                                                                                                          |
| `DisplayName`      | `Dreamina`, as Dreamina writes its name ([01-decisions.md](01-decisions.md#names-and-identifiers)); the name ComfyUI Manager shows            |
| `Icon`             | The raw GitHub address of `docs/images/brand/logo.png`, the logo, which is also the Registry icon ([19-brand-assets.md](19-brand-assets.md))  |
| `requires-comfyui` | `>=0.37.2`, the installation every check, measurement, and example run used                                                                    |

No `Banner` key: the README banner is not a Registry image, as in F. No
`includes` key: comfy-cli's `includes` adds folders Git ignores, and every
file the pack ships is tracked.

Fourth, create a Registry publishing key on `registry.comfy.org` and keep it
out of the repository. `comfy node publish` asks for it at a hidden prompt.
Do not pass `--token`: the key would land in the shell history. The publishing
key has nothing to do with the Dreamina sign-in, which the CLI keeps.

The address and publisher edits are committed with the first release in
[Step 5](#step-5-commit).

## What the Registry flags

The Registry does not publish its scanner's rules. F's plan found the old fal
pack's newest version flagged with no reason given, and BytePlus's own pack
flagged in every version for "informational findings in API networking and
environment access" (`F/plans/20-release.md:137-140`). This pack avoids every
pattern found in those packs and the patterns scanners look for, except one,
which it keeps on purpose and names here:

| Pattern                                                | In this pack                                                                                                                                                  | Held by                                                                                                     |
| ------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| Subprocesses started from nodes and routes             | It starts the person's installed `dreamina-canvas` from the paid and free nodes and from the settings routes (status, sign-in, sign-out). Every start goes through the one CLI module, `src/dreamina/cli.py`, with a fixed program and an argument list built from constants and checked inputs, never through a shell. No route takes a command, a flag, or a path from the request | [04-architecture.md](04-architecture.md#threads-event-loops-and-subprocesses), [05-foundation.md](05-foundation.md), [08-runs.md](08-runs.md) |
| Downloading and running code at run time               | It never installs a Python package. **Install** and **Update** in **Dreamina Settings** download ByteDance's official installer from `https://dreamina.capcut.com` only, with no redirects and a byte cap, and run it after the person confirms. This is the pattern the pack keeps on purpose | [04-architecture.md](04-architecture.md#how-the-cli-is-installed), [05-foundation.md](05-foundation.md), [16-frontend.md](16-frontend.md); Semgrep `dreamina-no-runtime-package-install` and `dreamina-no-async-package-install` for Python packages |
| Files written inside the pack folder                   | Writes nothing inside the pack folder. The settings, the canvas record, and the generation records go to the private state folder                            | [04-architecture.md](04-architecture.md#where-data-lives), [05-foundation.md](05-foundation.md)             |
| Credentials written into ComfyUI's folders             | Writes no credential anywhere: the CLI keeps the sign-in in the OS credential store. `register_routes` refuses a state folder inside any ComfyUI folder or the pack | [01-decisions.md](01-decisions.md#sign-in-and-privacy), [05-foundation.md](05-foundation.md)                |
| Network at import or on load                           | Sends nothing and starts no process at import or in `on_load`, which only reads the settings from disk and registers the routes. The first CLI call comes from a node run or a dialog action the person starts | [05-foundation.md](05-foundation.md)                                                                        |
| Media sent to a third party with the person's identity | Uploads local media only to Dreamina, through the person's own CLI sign-in, onto the person's own `ComfyUI` canvas; never calls ComfyUI's API-node request or upload helpers, which use the Comfy sign-in | [01-decisions.md](01-decisions.md#local-media), [07-media.md](07-media.md)                                  |
| Unguarded state-changing routes                        | Every write route (settings, sign-in, sign-out, install) needs a local, same-origin, single-user connection and `X-Dreamina-Comfy: 1`                         | [01-decisions.md](01-decisions.md#sign-in-and-privacy), [05-foundation.md](05-foundation.md)                |
| A bundled third-party binary                           | Ships no CLI binary and no skill; the person installs both with ByteDance's installer                                                                         | [01-decisions.md](01-decisions.md#the-cli-on-the-persons-computer), [Step 6](#step-6-package)               |
| A node for the pack's own testing                      | Ships only the seven nodes in `NODE_TYPES`                                                                                                                    | [04-architecture.md](04-architecture.md#srcnodes)                                                           |

The pack reads two environment variables: `DREAMINA_COMFY_STATE_DIRECTORY`
and the installer's own `DREAMINA_CANVAS_INSTALL_DIR`. It passes the server's
environment to the CLI unchanged, so the CLI finds the person's sign-in, and
reads no credential from it
([01-decisions.md](01-decisions.md#subprocesses-and-concurrency)).

If the scanner flags a version and the reason points at the installer,
the fix, with the owner's decision, is a patch version without **Install**
and **Update**: the `POST /dreamina/v1/cli` route and
`src/dreamina/installer.py` are removed, and people install the CLI with the
one-line commands the README and ADVANCED already give. The owner kept the
button on 2026-10-17
([01-decisions.md](01-decisions.md#decisions-the-owner-should-confirm)).

`comfy node publish` also runs `ruff check --select S102,S307,E702 --exit-zero`
(`exec`, `eval`, and two statements on one line) and only warns. The pack has
none of them, and Bandit in `repo:check` reports `exec` and `eval`.

## Step 1: Check the CLI release and the models the release names

The pack ships no model list: a node checks the model a person types against
the person's live `model list` when it runs
([06-model-check.md](06-model-check.md)). So nothing is rebuilt, but Dreamina
adds and retires models, and the release names some: each paid generation
node's default `model` and each example's models. These reads are free and
need the owner signed in to the CLI. Space them a few seconds apart.

First, read the installed CLI release:

```sh
D="$HOME/.local/bin/dreamina-canvas"
"$D" --format json --non-interactive version | jq -r '.data.version'
```

If it prints a release newer than the one
[02-dreamina-contract.md](02-dreamina-contract.md) records (1.0.3 on
2026-10-16), run **Model: Info** once in ComfyUI: the version gate reads
`schema` on first use and refuses a missing command or flag with the message
that the CLI changed ([01-decisions.md](01-decisions.md#the-cli-on-the-persons-computer)).
A refusal there means the pack needs a fix before release; record it and
correct [02-dreamina-contract.md](02-dreamina-contract.md) and the plan it
names.

Then check each model by its canonical name:

```sh
"$D" --format json --non-interactive model find "<canonical model name>" --type <image|video|audio> | jq -r '.data.items[].model'
```

1. Each of the three default models in
   [research/catalog.md](research/catalog.md#defaults) prints its own
   canonical name. Replace one Dreamina no longer lists with the current model
   of the same family, in [research/catalog.md](research/catalog.md#defaults),
   the node's default in its plan, and its help page. A new default needs a
   new `credit_ceiling` default, measured as Part 0 of
   [21-test-runs.md](21-test-runs.md) measures it
   ([01-decisions.md](01-decisions.md#credits)).
1. Every model the examples name
   ([17-scripts-and-workflows.md](17-scripts-and-workflows.md)) prints its
   canonical name, and every flag an example's `arguments` sets is still a
   flag of the mode it runs, with its value allowed: run **Model: Info** on
   the model. A changed model or flag is fixed in the example's description,
   and the example is run again by [21-test-runs.md](21-test-runs.md)'s
   procedure, with the owner's approval.

The list holds only the models the signed-in account can call, so a check
against another account can differ.

## Step 2: Re-check the node IDs

Workflows save node IDs, so after the first release a node ID never changes
([01-decisions.md](01-decisions.md#node-id-clashes)). The `Dreamina` prefix,
the install folder, and the Registry ID `dreamina` come from
[01-decisions.md](01-decisions.md#names-and-identifiers). Until the first
publish claims the ID, check that it is still free:
`https://api.comfy.org/nodes/dreamina` answers 404.

Search the Registry for the packs whose IDs could clash, and read each
result's Registry ID:

```sh
for term in dreamina jimeng seedance; do
  curl -s "https://api.comfy.org/nodes/search?search=$term" | jq .
done
```

Put every Registry ID the three searches list into `ids`, then clone each
pack's current source from its Registry `repository` value and search it,
with ComfyUI core, for each node ID this release ships. Run this from the
repository root: `web/docs/` holds one help page per registered node, named
by its node ID, and `comfy:nodes:check` keeps the two in step. The clones are
only searched, never run or imported.

```sh
ids="<the Registry IDs the searches list, separated by spaces>"
scan=$(mktemp -d)
for id in $ids; do
  git clone --quiet --depth 1 "$(curl -s "https://api.comfy.org/nodes/$id" | jq -r .repository)" "$scan/$id"
done
C=/Users/dr_stone/ComfyUI-Installs/ComfyUI/ComfyUI
for id in $(ls web/docs | sed 's/\.md$//'); do
  grep -rlw --include='*.py' --include='*.js' "$id" "$scan" "$C/nodes.py" "$C/comfy_extras" "$C/comfy_api_nodes"
done
grep -rlF -e '/dreamina/v1' -e 'dreamina.OpenSettings' -e 'DREAMINA_REFERENCES' -e 'X-Dreamina-Comfy' "$scan"
```

Both searches must print nothing. A printed file uses one of this pack's node
IDs, its route prefix, its settings command, its socket type, or its header:

- Before the first release, rename the clashing node's class in the plan that
  owns it, and change its node ID everywhere 01 and 04 list it, its help page,
  and the examples.
- After the first release, the ID stays. Record the clash, with the date, in
  [04-architecture.md](04-architecture.md#ids-other-packs-use).

Then list every `Dreamina`-prefixed name the other packs and ComfyUI core
use, and bring the dated list in
[04-architecture.md](04-architecture.md#ids-other-packs-use) up to date:

```sh
grep -rhoE "[\"']Dreamina[A-Za-z0-9_]+[\"']" "$scan" "$C/comfy_api_nodes" | tr -d "\"'" | sort -u
rm -rf "$scan"
```

ComfyUI core's ByteDance nodes name BytePlus models such as
`dreamina-seedance-2-5-260628` (`comfy_api_nodes/nodes_bytedance.py`). They
are model IDs, written in lower case with hyphens, so neither search above
matches them, and none can equal a `Dreamina<Family><Action>` node ID.

## Step 3: Refresh generated files

```sh
mise run repo:deps:export
mise run comfy:frontend:build
mise run comfy:workflows:build
```

- `repo:deps:export` rewrites `requirements.txt` from `[project].dependencies`.
- `comfy:frontend:build` rebuilds `web/extension.js` and `web/extension.css`.
- `comfy:workflows:build` regenerates `example_workflows/` and `subgraphs/`
  from the current node schemas and descriptions, so a model or flag fixed in
  Step 1 reaches the examples and their blueprints.

## Step 4: Set the version

Set `[project].version` in `pyproject.toml`. The first release is `0.1.0`, the
value [03-repository-setup.md](03-repository-setup.md#step-4-edit-pyprojecttoml)
set. Raise the minor number for new nodes or settings, and the patch number
for fixes. These names never change between versions:

- a node ID;
- the socket type `DREAMINA_REFERENCES`;
- an input name the node plans fix, such as `images`, `videos`, `audio`,
  `references`, `model`, `credit_ceiling`, `run_number`, `prompt`, and
  `arguments`;
- an output name, such as `images`, `video`, `audio`, `references`, `result`,
  and `info`;
- a saved setting name.

Model names and their flags are Dreamina's. The pack ships only the three
default names, so Dreamina changes the rest without a release.

## Step 5: Commit

Commit the version, the generated files, any model fixed in Step 1, and, on
the first release, the address and publisher edits from the
[one-time setup](#one-time-setup):

```text
chore(root): release version 0.1.0
```

## Step 6: Package

```sh
mise run comfy:release:package
```

The task runs `mise run repo:check`, then `comfy node pack`, which zips the
Git-tracked files that `.comfyignore` does not exclude into `node.zip`. It then
lists the archive and scans it with gitleaks, using gitleaks' default rules
([03-repository-setup.md](03-repository-setup.md#step-6-re-value-the-quality-configuration)).
The archive holds exactly:

- `__init__.py`, `src/`
- `web/extension.js`, `web/extension.css`, `web/docs/`
- `example_workflows/`, `subgraphs/`, `docs/images/`
- `pyproject.toml`, `requirements.txt`
- `README.md`, `ADVANCED.md`, `LICENSE.md`

Anything else in the listing, such as `web/scripts/`, `scripts/`, `quality/`,
a lock file, or `rules/`, means `.comfyignore` needs an entry. Git ignores
`node.zip`, `.mise.local.toml`, and `plans/`, so none of them can be packed;
`plans/` holds the skill mirror, and `.comfyignore` lists it too.

Then confirm that no Dreamina binary or skill is in the archive. This prints
nothing:

```sh
unzip -l node.zip | grep -iE 'dreamina-canvas|skill\.tar\.gz|SKILL\.md'
```

The repository never tracks the CLI or its skill, so a printed line means a
file was added by mistake: remove it from Git, and package again.

## Step 7: Publish

The owner runs:

```sh
COMFY_NODE_CHANGELOG="First release." mise run comfy:release:publish
```

The task repeats the package task, then runs `comfy node publish`. It
validates `pyproject.toml`, asks for the publishing key, registers the
version, and uploads a new archive built from the checkout; it does not upload
the `node.zip` from Step 6. So nothing may change between Step 6 and Step 7:
not the source, the built files, the tracked paths, `.comfyignore`, or the
comfy-cli version. `COMFY_NODE_CHANGELOG` is the text the Registry shows under
**Updates** for this version; later releases name what changed, such as
"Generation: Download now …".

## Step 8: Tag and push

```sh
git tag -a v0.1.0 -m "Release 0.1.0"
git push origin main v0.1.0
```

One push sends the release commit and the tag, so the pre-push hook runs
`repo:check` once.

## Step 9: Verify in a clean ComfyUI

First, read the Registry's verdict on the version:

```sh
curl -s https://api.comfy.org/nodes/dreamina/versions | jq -r '.[] | "\(.version) \(.status) \(.supported_comfyui_version)"'
```

The expected line is `0.1.0 NodeVersionStatusActive >=0.37.2`. A version the
scanner has not finished may show another status first; read it again later.
`NodeVersionStatusFlagged` means the scanner found something: compare the
release with [What the Registry flags](#what-the-registry-flags), fix it, and
publish a patch version.

Then install the published version through ComfyUI Manager in a new ComfyUI
0.37.2, the declared minimum. It is kept apart from the development
installation, which links the working copy into its `custom_nodes`, and from
the folder F's release check uses. Run the commands from the repository root,
so `comfy` is the comfy-cli 1.20.0 that `mise.toml` pins:

```sh
cd /Users/dr_stone/Documents/work/comfyui-dreamina
R=/Users/dr_stone/ComfyUI-Installs/release-check-dreamina
uv venv --seed --python 3.12 "$R/venv"
source "$R/venv/bin/activate"
comfy --workspace "$R/ComfyUI" --skip-prompt install --version 0.37.2 --m-series
comfy --workspace "$R/ComfyUI" node install dreamina
grep '^version' "$R/ComfyUI/custom_nodes/dreamina/pyproject.toml"
comfy --workspace "$R/ComfyUI" launch -- --port 8189
```

- The pack needs Python 3.12 or later. comfy-cli installs into the active
  environment; without one, it builds an environment from the Python it runs
  on, which differs between comfy-cli installations.
- `comfy node install` installs from the Registry through ComfyUI Manager's
  command line, as the Manager's node list does. The `grep` prints
  `version = "0.1.0"`.
- `comfy launch` starts ComfyUI with the Manager turned on, and port 8189
  keeps the development ComfyUI's 8188 free. Starting this second ComfyUI does
  not touch the owner's running one.

Then check, in the terminal and at `http://127.0.0.1:8189`:

1. The custom node import times in the terminal list `dreamina` without
   `(IMPORT FAILED)`.
1. Searching ComfyUI Manager's node list for **Dreamina** shows **Dreamina**
   (`dreamina`) 0.1.0 as installed.
1. The node menu has the **Dreamina** root with **Image**, **Video**, and
   **Audio**, the seven nodes, and each node's help page opens.
1. **Image: Generate** shows `model` set to the image default in
   [research/catalog.md](research/catalog.md#defaults), `credit_ceiling` at its
   default, and `prompt` and `arguments` below them.
1. **Extensions → Dreamina → Dreamina Settings** opens. The CLI, its sign-in,
   and the state folder belong to the OS user, not to one ComfyUI, so the
   dialog shows the installed CLI's version, **Update**, and the account
   signed in during development.
1. **Browse Templates** lists the examples under **dreamina**, and each opens
   without a missing-node warning.
1. **Model: Info** runs on the image default. It reads the model list through
   the CLI, sends nothing paid, and costs nothing.

Last, check that nothing private or bundled landed in the new ComfyUI's
folders. Both commands print nothing:

```sh
find "$R/ComfyUI/custom_nodes/dreamina" \( -name .env -o -name 'dreamina-canvas*' -o -name SKILL.md -o -name settings.json -o -name canvas.json -o -name generations \) -print
find "$R/ComfyUI/user" \( -name canvas.json -o -name generations \) -print
```

Stop the server and run `deactivate`. `$R` can then be deleted; the state
folder and the CLI outside it stay.

## Release checklist

Each line points at the step that does it; tick them in order.

- [ ] Every example ran once on the release candidate, with the owner's
      approval ([21-test-runs.md](21-test-runs.md)).
- [ ] One-time setup done: `main` on GitHub, `urls.Issues` and
      `urls.Repository` added, publisher chosen and `PublisherId` added,
      publishing key created ([One-time setup](#one-time-setup)).
- [ ] The installed CLI release passes the version gate, and the default and
      example models are still listed with the flags the examples set
      ([Step 1](#step-1-check-the-cli-release-and-the-models-the-release-names)).
- [ ] Node IDs, routes, settings command, header, and socket type clash with
      no other pack ([Step 2](#step-2-re-check-the-node-ids)).
- [ ] `requirements.txt`, the bundle, the examples, and the blueprints
      rebuilt ([Step 3](#step-3-refresh-generated-files)).
- [ ] Version set ([Step 4](#step-4-set-the-version)) and committed as
      `chore(root): release version <version>` ([Step 5](#step-5-commit)).
- [ ] Archive listing matches the list, holds no Dreamina binary or skill,
      and its gitleaks scan is clean ([Step 6](#step-6-package)).
- [ ] Published by the owner, with the changelog text
      ([Step 7](#step-7-publish)).
- [ ] Tagged and pushed in one push ([Step 8](#step-8-tag-and-push)).
- [ ] Registry status `NodeVersionStatusActive`; clean install checked; no
      private or bundled file in the clean ComfyUI
      ([Step 9](#step-9-verify-in-a-clean-comfyui)).

## Names this plan uses from other plans

| Name                                                                                  | Owner                                                                    |
| ------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| Registry ID and install folder `dreamina`; display name `Dreamina`; `NODE_PREFIX`; `/dreamina/v1`; `dreamina.OpenSettings`; `X-Dreamina-Comfy`; `DREAMINA_REFERENCES`; `DREAMINA_COMFY_STATE_DIRECTORY` | [01-decisions.md](01-decisions.md#names-and-identifiers) |
| The installer alternative and the Registry ID alternative                             | [01-decisions.md](01-decisions.md#decisions-the-owner-should-confirm)    |
| `[project]` description, `[tool.comfy]` `DisplayName` and `requires-comfyui`, `version = "0.1.0"`, `.comfyignore`, the release tasks, the gitleaks configuration | [03-repository-setup.md](03-repository-setup.md) |
| `src/dreamina/cli.py`, `src/dreamina/installer.py`, `POST /dreamina/v1/cli`, `NODE_TYPES` and its seven nodes, the state folder files | [04-architecture.md](04-architecture.md) |
| The CLI release the contract was read from (1.0.3)                                    | [02-dreamina-contract.md](02-dreamina-contract.md)                       |
| The three default model names                                                         | [research/catalog.md](research/catalog.md#defaults)                      |
| The `Icon` line and `docs/images/brand/logo.png`                                      | [19-brand-assets.md](19-brand-assets.md)                                 |
| The **Package and publish** part of `ADVANCED.md`                                     | [18-documentation.md](18-documentation.md)                               |
| The examples, their models, and their flags                                           | [17-scripts-and-workflows.md](17-scripts-and-workflows.md)               |
| Part 0 and the example runs                                                           | [21-test-runs.md](21-test-runs.md)                                       |
| The GitHub repository check                                                           | [22-owner-setup.md](22-owner-setup.md)                                   |
