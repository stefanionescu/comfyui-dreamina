# Repository Setup

This plan brings the fal pack's tooling into the empty repository: the rules,
the quality checks, the mise tasks, the Git hooks, the root configuration,
and the scripts that are not about fal. It ends with a repository whose
tooling is complete, whose runtime packages exist as small stubs that later
plans fill, and whose first commit passes every hook.

The tooling is copied, not rewritten. The fal pack
(`F=/Users/dr_stone/Documents/work/comfyui-fal`, commit `cef8b6e`) is the only
source. F's tooling is the BytePlus pack's tooling
(`B=/Users/dr_stone/Documents/work/comfyui-byteplus`, commit `472cf10`) with
fal values, plus every fix F made while it was built. `.mise/`, `.githooks/`,
and `rules/` are byte-identical in F and B. F's first commit, `c1dd344`, is
F's tooling-time state: where F's current file holds a value that a later
milestone added, this plan takes the `c1dd344` value
([research/tooling.md](research/tooling.md#1-headline-findings)). F's code and
tooling are the reference, not F's `plans/03-repository-setup.md`, which
copied from B. The only edits here are project values: names, the import
contracts, the naming rules, the secret rules, the temporary folder prefixes,
and the workflow namespace. Every Tooling row of F's **Changes made while
building** table (F rows 220 to 224, 227, and 233) is applied up front, so
none of F's surprises repeats.

Readers: the engineer or agent who builds the pack, and the owner, who
decides the items [research/tooling.md](research/tooling.md#13-decisions-for-the-owner)
lists. "F row N" is line N of `F/plans/README.md`. `F/<path>:N` is line N of
that file at `cef8b6e`, and `c1dd344:<path>` is the file in F's first commit.

Do not hand-write a tooling file that F has; copy it and change the values.

## Contents

- [Decisions this plan makes](#decisions-this-plan-makes)
- [Before you start](#before-you-start)
- [Step 1: Copy the fal pack's files](#step-1-copy-the-fal-packs-files)
- [Step 2: Edit the root configuration](#step-2-edit-the-root-configuration)
- [Step 3: Create the local settings](#step-3-create-the-local-settings)
- [Step 4: Edit pyproject.toml](#step-4-edit-pyprojecttoml)
- [Step 5: Edit package.json](#step-5-edit-packagejson)
- [Step 6: Re-value the quality configuration](#step-6-re-value-the-quality-configuration)
- [Naming exceptions](#naming-exceptions)
- [Step 7: Re-value the scripts](#step-7-re-value-the-scripts)
- [Step 8: Create the skeleton](#step-8-create-the-skeleton)
- [Step 9: Lock and install](#step-9-lock-and-install)
- [Step 10: First commit](#step-10-first-commit)
- [Step 11: Link the pack into ComfyUI](#step-11-link-the-pack-into-comfyui)
- [Tooling that later milestones add](#tooling-that-later-milestones-add)
- [Names this plan uses from other plans](#names-this-plan-uses-from-other-plans)

## Decisions this plan makes

| Question                                                         | Decision                                                                                                   | Why                                                                                                                         |
| ---------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| Which pack is the source?                                        | F at `cef8b6e`                                                                                             | F is B re-valued plus F's fixes; [01-decisions.md](01-decisions.md#what-is-copied-from-fal) copies F's code                 |
| What happens to F's values from later milestones?                | `functions.json`, `functions.py`, `directories.js`, `markers.yml`, and `build.py` come from `c1dd344`; `pyproject.toml` drops `Icon` and the `yarl` ignore; `valibot` leaves `package.json` in [16-frontend.md](16-frontend.md#step-1-entry-files) | Each names a file, class, or method that does not exist at Tooling, and the copied checks refuse such an entry, or it is dead configuration |
| Is F's `ModelInfo` naming rule kept?                             | Yes, with the reason naming `DreaminaModelInfo`                                                            | The owner authorized it for F (F row 245), [01-decisions.md](01-decisions.md#banned-words-that-shape-names) keeps it, and a rule for a missing path fails no check |
| What does gitleaks check?                                        | gitleaks' default rules only                                                                               | No API key exists; the CLI owns sign-in ([01-decisions.md](01-decisions.md#tooling))                                        |
| What stays in the Semgrep secrets file?                          | The HuggingFace rule only                                                                                  | Both of F's key rules describe fal's key and `FAL_KEY`                                                                      |
| What happens to F's `api_key` and `credential_limit` naming entries? | Deleted                                                                                                | They are F's key route field and key length; Dreamina has neither                                                           |
| Does `scripts/nodes/schema.py` keep F's multi-typed widget test? | No: B's one-line test                                                                                      | F added it for File: Add (F row 223); no Dreamina node has a multi-typed widget input                                       |
| Which workflow namespace?                                        | `05f62da6-1302-4067-b6d8-e83cf4a52f83`, a new version 4 UUID                                               | Workflow, subgraph, and blueprint IDs are `uuid5` of this namespace; a new one keeps them apart from F's, B's, and O's       |
| How is the leftover-name search written?                         | `git grep -P` with word boundaries, excluding `uv.lock`, `bun.lock`, and `plans/`                          | `git grep -E '\b…\b'` matches nothing with git 2.55.0, and Dreamina's own model names (Seedance, Seedream) must not match   |
| What if the Semgrep registry drifts?                             | Copy F's local packs, which match the pins                                                                 | F row 220; checked with `shasum -a 256 -c` on 2026-10-16                                                                    |

## Before you start

- `/Users/dr_stone/Documents/work/comfyui-dreamina` is a Git repository on
  branch `main` with no commits. Its only content is the untracked `plans/`
  folder, which already holds `plans/research/docs/dreamina-canvas-cli/` (the
  skill mirror) and `plans/research/captures/` (the CLI's JSON replies). Its
  `origin` remote is `https://github.com/stefanionescu/comfyui-dreamina.git`.
  Whether that GitHub repository exists was not checked when this plan was
  written; [Step 10](#step-10-first-commit) asks the owner before the first
  push.
- mise is installed and active in the shell, as for F. Every tool in
  `F/mise.toml:1-15` is already installed at the same versions
  ([research/tooling.md](research/tooling.md#1-headline-findings), finding 11).
- `F` is at `cef8b6e`. Every copy names that commit or `c1dd344`, so a later
  F commit never leaks in.
- The ComfyUI used for type checks, node exports, and example measurements is
  `/Users/dr_stone/ComfyUI-Installs/ComfyUI/ComfyUI`: ComfyUI 0.37.2 with
  frontend 1.52.7 and its interpreter at `.venv/bin/python`, the same
  installation F was built against, so F's measured page sizes hold. If it is
  running, do not restart or stop it;
  [Step 11](#step-11-link-the-pack-into-comfyui) says what to tell the owner.
- comfy-cli 1.20.0 is pinned in `mise.toml` as `pipx:comfy-cli`, which the
  release tasks use.
- The Dreamina CLI is not needed for any step here.
- The names come from [01-decisions.md](01-decisions.md#names-and-identifiers):
  repository `comfyui-dreamina`; Python project, Registry ID, and install
  folder `dreamina`; display name and menu root `Dreamina`; browser extension
  name `dreamina`; node prefix `Dreamina`; error type `DreaminaError`; routes
  `/dreamina/v1`; local header `X-Dreamina-Comfy`; state override
  `DREAMINA_COMFY_STATE_DIRECTORY`; CSS class prefix `dreamina-`. No API key
  variable exists.

Every copy uses `git archive` or `git show`, so untracked caches (`.venv`,
`node_modules`, `.artifacts`, `.ruff_cache`, `__pycache__`,
`.import_linter_cache`) never come along and file modes survive: the 3 hooks,
the 35 task files, and the scanner entry points stay executable, and the
sourced `environment.sh` files stay plain.

## Step 1: Copy the fal pack's files

Run from the repository root:

```sh
F=/Users/dr_stone/Documents/work/comfyui-fal
git -C "$F" archive cef8b6e -- \
  AGENTS.md CLAUDE.md LICENSE.md rules \
  mise.toml bunfig.toml tsconfig.json pyrightconfig.json \
  .markdownlint-cli2.yaml .prettierrc.json .prettierignore .stylelintrc.json .typos.toml \
  .gitignore .gitattributes .comfyignore \
  package.json pyproject.toml uv.lock bun.lock __init__.py \
  .githooks .mise/tasks quality \
  scripts/__init__.py scripts/paths.py scripts/types.py scripts/dependencies.py scripts/frontend.py \
  scripts/nodes scripts/workflows/__init__.py scripts/workflows/build.py scripts/workflows/page \
  scripts/workflows/descriptions/__init__.py \
  | tar -x -C .
for path in \
  quality/config/repository/functions.json \
  quality/config/repository/functions.py \
  quality/config/repository/directories.js \
  quality/config/security/semgrep/markers.yml \
  scripts/workflows/build.py; do
  git -C "$F" show "c1dd344:$path" > "$path"
done
```

The loop replaces five copied files with their state in F's first commit.
Each differs from `cef8b6e` only by values later F milestones added
(`git -C "$F" diff c1dd344 cef8b6e` on these paths): three allowlist entries,
the `EndpointNode` base, the empty single-file list, the split `deprecated`
rule, and six workflow families. The files already exist, so `>` keeps their
mode.

Then edit `.gitignore`. In this repository the plans are tracked: the owner
asked on 2026-10-17 for them to be committed, and they were, before this
milestone. Replace F's first two lines (`# Build plans stay local` and
`/plans/`) with these three, before any `git add`:

```gitignore
# The plans are tracked; the copy of ByteDance's skill and the account captures stay local
/plans/research/docs/
/plans/research/captures/
```

The skill copy is ByteDance's text, not the owner's to publish, and the
captures hold IDs from the owner's account.

What arrives:

| Copied                                                                                                       | What it is                                                                                                | Edited in                          |
| ------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------- | ---------------------------------- |
| `AGENTS.md`, `CLAUDE.md`, `rules/` (8 files)                                                                  | The engineering rules. Protected: no plan edits them. The verb table in `rules/NAMING.md` matches `functions.json` | Never                       |
| `LICENSE.md`                                                                                                  | MIT, copyright 2026 Stefan Ionescu                                                                        | Never                              |
| `mise.toml`, `bunfig.toml`, `tsconfig.json`, `pyrightconfig.json`, `.prettierrc.json`, `.prettierignore`, `.stylelintrc.json`, `.markdownlint-cli2.yaml`, `.typos.toml`, `.gitignore`, `.gitattributes`, `.comfyignore` | Settings that name no project                                    | Never at Tooling                   |
| `__init__.py`                                                                                                 | The extension entry point                                                                                 | Step 2                             |
| `pyproject.toml`                                                                                              | Project metadata, tool settings, import contracts                                                         | Step 4                             |
| `package.json`                                                                                                | Browser and check dependencies                                                                            | Step 5                             |
| `uv.lock`, `bun.lock`                                                                                         | F's resolved versions                                                                                     | Step 9 relocks them                |
| `.githooks/` (3 files), `.mise/tasks/` (35 files)                                                             | The hooks and the `comfy:*` and `repo:*` tasks; no file names fal                                        | Never                              |
| `quality/` (220 files)                                                                                        | Every check the tasks run                                                                                 | Step 5 (`quality/package.json`), Step 6 |
| `scripts/` (20 files)                                                                                         | Frontend build, requirements export, node export and check, the workflow engine                          | Step 7                             |

The lock files come along so the first install resolves exactly the versions
F's checks passed with on 2026-10-15, including the five security overrides
and the braces override at its full commit hash (F row 227). The license
exemptions in `quality/config/repository/licenses/policy.json` name installed
versions (colorama 0.4.6, fastjsonschema 2.22.2, grimp 3.17, import-linter
2.15, `F/quality/config/repository/licenses/policy.json:18-33`), and a fresh
resolve could move them.

Not copied:

| F path                                                                                     | Why                                                                     | Written by                                                                                   |
| ------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| `src/`                                                                                     | fal runtime, including `src/storage/credentials.py`, `src/types/credentials.py`, `src/fal/schema.py`, and the Request Options, text, and 3D nodes, which have no Dreamina counterpart ([04-architecture.md](04-architecture.md#port-map)) | [Step 8](#step-8-create-the-skeleton) stubs, then plans 05 to 15 |
| `web/`                                                                                     | Settings code with the API key section, the built bundle, help pages    | [16-frontend.md](16-frontend.md#step-1-entry-files) Step 1 copies `host.d.ts` and `interface.css` from F; 16 and [18-documentation.md](18-documentation.md) write the rest |
| `scripts/workflows/descriptions/{texts,notes,nodes,image,audio,video,voices,text,mesh}.py` | fal workflows, notes, node IDs, model IDs, save prefixes                | [Step 7](#step-7-re-value-the-scripts) writes `texts.py`, [Step 8](#step-8-create-the-skeleton) stubs `notes.py`, then [17-scripts-and-workflows.md](17-scripts-and-workflows.md) |
| `example_workflows/`, `subgraphs/`                                                         | Generated from those descriptions                                       | `mise run comfy:workflows:build`, from [17-scripts-and-workflows.md](17-scripts-and-workflows.md) |
| `README.md`, `ADVANCED.md`, `docs/images/`                                                 | fal documentation and artwork                                           | [18-documentation.md](18-documentation.md), [19-brand-assets.md](19-brand-assets.md)          |
| `requirements.txt`                                                                         | Generated                                                               | [Step 9](#step-9-lock-and-install)                                                           |

Two copied scripts still describe F's examples and are kept as they are here:

- `scripts/nodes/host.py` lists the 14 ComfyUI nodes F's examples place
  (`F/scripts/nodes/host.py:9-22`), and `scripts/workflows/page/config.py`
  (`DOM_SIZES`, `F/scripts/workflows/page/config.py:62-72`) holds their sizes
  measured on frontend 1.52.7. Every member exists in ComfyUI 0.37.2, so the
  node export runs with the copied list.
  [17-scripts-and-workflows.md](17-scripts-and-workflows.md#step-1-scripts-the-hooks-need)
  sets the list to the nodes Dreamina's examples place and measures any node
  F never measured.
- `scripts/workflows/build.py`, taken from `c1dd344`, imports no family
  module and builds from an empty family list
  ([Step 7](#step-7-re-value-the-scripts)).

## Step 2: Edit the root configuration

`__init__.py`: replace only the module docstring (`F/__init__.py:1`):

```python
"""Load the Dreamina nodes and their local routes through ComfyUI's extension entry point."""
```

The rest is the extension class
[04-architecture.md](04-architecture.md#root) describes: `on_load` imports
`register_routes` and `create_runtime` lazily (each with its `# noqa: PLC0415
-- reason:` comment) and runs `create_runtime` off the event loop through
`asyncio.to_thread`, and `get_node_list` returns `NODE_TYPES`.
[Step 8](#step-8-create-the-skeleton) supplies those three names;
[05-foundation.md](05-foundation.md) owns the file afterwards.

The other root files stay as copied:

- `mise.toml` keeps `"pipx:comfy-cli" = "1.20.0"` (`F/mise.toml:15`). The
  release tasks run through `mise run`, which puts mise's tools first on
  `PATH`, so they always use the pinned comfy-cli. Bun 1.3.11 must equal
  `packageManager` in `package.json`;
  `quality/repository/package-json/dependencies.js` checks it.
- `.gitignore` lists `/plans/research/docs/` and `/plans/research/captures/`
  (above), `.mise.local.toml`, `.venv/`, `node_modules/`, `.artifacts/`,
  `node.zip`, `.env`, and `.env.*`.
- `.comfyignore` keeps every development file out of the Registry archive,
  `/plans/` among them, and ships `docs/`, `subgraphs/`, `example_workflows/`,
  and `web/docs/`. The pack ships no model list and no CLI binary: each node
  reads the person's live model list through the installed CLI
  ([06-model-check.md](06-model-check.md)), so no data file needs an entry.
- `.markdownlint-cli2.yaml` already ignores `plans/**`
  (`F/.markdownlint-cli2.yaml:14`). That entry matters here:
  `markdownlint-cli2` does not read `.gitignore`, and
  `plans/research/docs/dreamina-canvas-cli/` holds the skill's own Markdown,
  whose heading styles would fail the hook.
- `.typos.toml` holds F's words (`certifi`, `python_embeded`, `IIFEs`), and
  `"plans"` joins `[files] extend-exclude`: typos skips only what Git ignores,
  and the plans are tracked here, with CLI flags, IDs, and quoted vendor text
  it should not judge. No Dreamina word is added: typos 1.43.5 accepts every Dreamina name in the
  plans ([research/tooling.md](research/tooling.md#1-headline-findings),
  finding 4). A plan that writes text typos reports adds the word under
  `[default.extend-words]` with a comment, as `certifi` is.
- `.prettierignore` gains one line, `plans/`, at the end. Prettier 3 skips
  only what `.gitignore` lists, and the plans are tracked here; the hook must
  not reformat them.
- `quality/config/repository/links.js`: `LINK_EXCLUDED_PREFIXES` becomes
  `['.artifacts/', 'plans/']`. The link check copies every file Git shows,
  and the plans link into the ignored skill copy and captures, which the copy
  leaves out.

`repo:lint:policy`'s folder check walks the `plans/` folder too
(F row 221). Its folders, `research`, `captures`, `docs`,
`dreamina-canvas-cli`, and `references`, hold none of the banned folder names
(`F/quality/config/repository/folders.py:7-18`), so nothing there is renamed.

## Step 3: Create the local settings

Create `.mise.local.toml`. `.gitignore` lists it, and the link check skips it.
The content equals `F/.mise.local.toml:1-3`:

```toml
[env]
COMFYUI_PATH = "/Users/dr_stone/ComfyUI-Installs/ComfyUI/ComfyUI"
COMFYUI_PYTHON = "/Users/dr_stone/ComfyUI-Installs/ComfyUI/ComfyUI/.venv/bin/python"
```

`quality/lib/comfy.py` and `quality/python/typecheck.py` read both values to
type-check against ComfyUI's own packages, and `scripts/nodes/check.py` runs
the node export with that interpreter. Without the file, the pre-commit type
check and the pre-push node and workflow checks stop with "Set COMFYUI_PATH to
the ComfyUI folder that holds main.py." Another development machine writes its
own paths.

## Step 4: Edit pyproject.toml

Change only what is listed; every other table stays as copied.

`[project]` (`F/pyproject.toml:2` and `:4`). The description fits on one line
of at most 120 characters (the line is 104), so `pyproject-fmt` keeps it as a
plain string, and `repo:format:check` passes:

```toml
[project]
name = "dreamina"
version = "0.1.0"
description = "Use Dreamina's image, video, and audio models in ComfyUI with your own Dreamina account."
readme = "README.md"
license = "MIT"
license-files = [ "LICENSE.md" ]
authors = [ { name = "Stefan Ionescu" } ]
requires-python = ">=3.12"
dependencies = [
  "pydantic>=2.10,<3",
]
```

`name` is the Comfy Registry ID and must equal `PROJECT_PACKAGE_NAME`
([Step 6](#step-6-re-value-the-quality-configuration)). It was free on the
Registry on 2026-10-16 ([01-decisions.md](01-decisions.md#names-and-identifiers)).
The repository keeps the name `comfyui-dreamina`, as O's project `openrouter`
lives in `comfyui-openrouter` and F's `fal-ai` in `comfyui-fal`. Only the
Registry-facing names change: `pyproject.toml`, `uv.lock`,
`PROJECT_PACKAGE_NAME`, `LINK_ALIASES`, and the install folder say
`dreamina`, while `package.json`, `bun.lock`, `quality/package.json`, the
temporary folder prefixes, and Ruff's checkout-folder name keep the
repository's name. `pydantic` is the only runtime dependency, as in F:
ComfyUI supplies aiohttp, PyAV, NumPy, Pillow, and torch, and declaring them
would let ComfyUI Manager change the host environment. The Dreamina CLI is a
program the person installs, not a package
([01-decisions.md](01-decisions.md#the-cli-on-the-persons-computer)). The
project addresses are added only at release
([20-release.md](20-release.md#one-time-setup)).

`[dependency-groups] dev` stays. Its host ranges contain the versions
ComfyUI 0.37.2 ships, so the checks see the same library APIs ComfyUI runs.

`[tool.ruff]`: one value, with its comment kept (`F/pyproject.toml:111-112`).
It names the local checkout folder, which is the repository's name, not the
install folder:

```toml
# ComfyUI loads the repository as a package even when its folder name has hyphens.
lint.pep8-naming.extend-ignore-names = [ "comfyui-dreamina" ]
```

`[tool.deptry]`: delete these two lines (`F/pyproject.toml:142-143`), which F
added for its signed output downloads:

```toml
# yarl comes with ComfyUI's aiohttp. Output downloads pass a yarl URL so aiohttp sends a signed address unchanged.
per_rule_ignores.DEP003 = [ "yarl" ]
```

Dreamina's outputs are downloaded by the CLI, and the installer download uses
one fixed address, so no code imports `yarl`. A setting no code needs is dead
configuration (B commit `673862b`). The rest of `[tool.deptry]`,
`[tool.interrogate]` (it has no overload setting in F), `[tool.vulture]`, and
`[tool.bandit]` stays.

`[tool.comfy]`, with no `Icon` yet (delete `F/pyproject.toml:159`):

```toml
[tool.comfy]
DisplayName = "Dreamina"
requires-comfyui = ">=0.37.2"
```

`DisplayName` is the name ComfyUI Manager shows. `requires-comfyui` is the
installation every check and measurement runs on. The `Icon` line comes with
the logo, in [19-brand-assets.md](19-brand-assets.md); `PublisherId` comes at
release ([20-release.md](20-release.md#one-time-setup)).

`[tool.importlinter]`: `root_packages`, `include_external_packages`, and the
first two contracts stay. In the other four, `src.fal` becomes
`src.dreamina` (`F/pyproject.toml:185`, `:198`, `:222`, `:231`), as
[04-architecture.md](04-architecture.md#import-linter-contracts) lists. They
read:

```toml
[[tool.importlinter.contracts]]
# Nothing here may import a package above it, which is what keeps the packages free of cycles.
name = "The packages stack in one order"
type = "layers"
layers = [
  "src.nodes",
  "src.comfy",
  "src.dreamina | src.settings",
  "src.storage",
  "src.types",
  "src.config",
]

[[tool.importlinter.contracts]]
name = "Only the host packages import ComfyUI's modules"
type = "forbidden"
allow_indirect_imports = true
# The node classes and the comfy package are the host boundary: ComfyUI calls them and they speak its types.
source_modules = [
  "src.config",
  "src.dreamina",
  "src.settings",
  "src.storage",
  "src.types",
]
forbidden_modules = [
  "comfy",
  "comfy_api",
  "comfy_api_nodes",
  "comfy_execution",
  "comfy_extras",
  "folder_paths",
  "node_helpers",
  "nodes",
  "server",
]

[[tool.importlinter.contracts]]
name = "Records must not import operations"
type = "forbidden"
source_modules = [ "src.types" ]
forbidden_modules = [
  "src.comfy",
  "src.nodes",
  "src.dreamina",
  "src.settings",
  "src.storage",
]

[[tool.importlinter.contracts]]
name = "Config must not import runtime code or tooling"
type = "forbidden"
source_modules = [ "src.config" ]
forbidden_modules = [ "src.nodes", "src.comfy", "src.dreamina", "src.types", "scripts", "quality" ]
```

import-linter refuses a contract that names a module that does not exist, so
[Step 8](#step-8-create-the-skeleton) creates all seven packages. The
runtime package `src/dreamina/` is reached only through relative imports
inside the pack; no package in ComfyUI's environment is named `dreamina`
([research/tooling.md](research/tooling.md#1-headline-findings), finding 9).

## Step 5: Edit package.json

`package.json:2`: set `"name": "comfyui-dreamina"`, the repository's name.
Everything else stays, in F's key order (`name`, `private`, `type`,
`packageManager`, `dependencies`, `devDependencies`, `imports`,
`overrides`):

- `"dependencies": { "valibot": "1.5.0" }` (`F/package.json:6-8`). Nothing
  imports it until the settings code, and knip's default check refuses an
  unused dependency, so [16-frontend.md](16-frontend.md#step-1-entry-files)
  Step 1 removes it before the first commit and a later 16 step adds it back,
  as in F.
- The exact devDependencies, including `@comfyorg/comfyui-frontend-types`
  1.48.3 (type declarations only; its license exemption names the package).
- `"packageManager": "bun@1.3.11"`, which must equal the Bun version in
  `mise.toml`.
- `"imports"` with `#web/*` and `#styles/*`, and the five security
  `"overrides"` (braces at a full Git commit, katex 0.18.11, js-yaml 5.4.1,
  markdown-it 14.3.1, smol-toml 1.9.1).

`quality/package.json:2`: set `"name": "comfyui-dreamina-quality"`.

## Step 6: Re-value the quality configuration

Every fal value in `quality/`, and its Dreamina value
([research/tooling.md](research/tooling.md#6-quality-every-fal-value-and-its-dreamina-value)):

| File                                                  | F value at `cef8b6e`                                                                       | Dreamina value                                                                             |
| ----------------------------------------------------- | ------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------ |
| `quality/config/repository/dependencies.py:5`         | `PROJECT_PACKAGE_NAME = "fal-ai"`                                                          | `PROJECT_PACKAGE_NAME = "dreamina"`, the `[project]` name `uv.lock` holds                  |
| `quality/config/repository/links.js:1`                | `LINK_ALIASES = [['web/', 'extensions/fal-ai']]`                                           | `LINK_ALIASES = [['web/', 'extensions/dreamina']]`; ComfyUI serves `web/` at `/extensions/<install folder>/` |
| `quality/config/repository/functions.json:35-56`      | Four `allowlist` entries; three name F's runtime                                           | From Step 1: only the `__init__.py` entry, below                                           |
| `quality/config/repository/functions.py:6-7`          | A comment naming EndpointNode; a three-entry `HOST_NODE_BASES`                             | From Step 1: F's tooling-time comment and two-entry value, below                           |
| `quality/config/repository/directories.js:3`          | `SINGLE_FILE_FOLDER_PATTERNS = [];`                                                        | From Step 1: `SINGLE_FILE_FOLDER_PATTERNS = ['web/scripts/*.ts'];`, below                  |
| `quality/config/naming/policy.json:130`               | The `ModelInfo` reason names `FalModelInfo`                                                | The reason names `DreaminaModelInfo` ([Naming exceptions](#naming-exceptions))              |
| `quality/config/naming/javascript.json:397`, `:411`, `:421-428` | `credential_limit` among the wire names; header `X-Fal-Comfy`; the `api_key` rule | No `credential_limit`; `X-Dreamina-Comfy`; no `api_key` rule ([Naming exceptions](#naming-exceptions)) |
| `quality/config/security/gitleaks/config.toml`        | Title and the rules `fal-api-key` and `fal-api-key-assignment`                             | The whole file below                                                                       |
| `quality/config/security/semgrep/secrets.yml`         | `fal-secrets-hf-token-literal`, `fal-api-key-literal`, `fal-api-key-assignment-literal`    | The whole file below                                                                       |
| `quality/config/security/semgrep/python.yml`          | Six IDs starting `fal-` (`:2`, `:32`, `:48`, `:54`, `:62`, `:70`)                          | The same IDs starting `dreamina-`; the includes at `:7` and `:37` stay `['/src/**', '/__init__.py']` |
| `quality/config/security/semgrep/frontend.yml`        | Five IDs starting `fal-` (`:2`, `:15`, `:30`, `:44`, `:62`)                                | The same IDs starting `dreamina-`                                                          |
| `quality/config/security/semgrep/markers.yml`         | From Step 1: one rule, `fal-python-no-obsolete-markers`                                    | The whole file below                                                                       |
| `quality/config/security/codeql/frontend/scan.yml:1`  | `name: fal JavaScript and TypeScript`                                                      | `name: Dreamina JavaScript and TypeScript`                                                 |
| `quality/python/typecheck.py:41`                      | `prefix="comfyui-fal-types-"`                                                              | `prefix="comfyui-dreamina-types-"`                                                         |
| `quality/repository/links.mjs:63`                     | `'comfyui-fal-links-'`                                                                     | `'comfyui-dreamina-links-'`                                                                |
| `quality/security/worktree.py:31`                     | `prefix="comfyui-fal-secret-scan-"`                                                        | `prefix="comfyui-dreamina-secret-scan-"`                                                   |

The Semgrep rule bodies stay; only the IDs change. After the edit the IDs
are:

- `python.yml`: `dreamina-no-runtime-package-install`,
  `dreamina-no-async-package-install`, `dreamina-torch-no-jit-script`,
  `dreamina-torch-no-load`, `dreamina-torch-no-lstm-cell`,
  `dreamina-python-no-diskcache-direct-use`.
- `frontend.yml`: `dreamina-no-eval`, `dreamina-no-child-process-exec`,
  `dreamina-no-dynamic-require-or-import`, `dreamina-no-secret-env-log`,
  `dreamina-no-dom-html-sinks`.
- `markers.yml`: `dreamina-python-no-obsolete-markers`.
- `secrets.yml`: `dreamina-secrets-hf-token-literal`.
- `hooks.yml` keeps `hooks-no-curl-pipe-shell` and `hooks-no-eval`.

The two package-install rules match only `pip`, `uv pip`, `uv sync`, and
`ensurepip` commands, so the CLI calls and the installer run in later plans
do not match them
([research/tooling.md](research/tooling.md#6-quality-every-fal-value-and-its-dreamina-value)).

Unchanged on purpose: `quality/config/naming/terms.json` (the 101 banned
words; see [01-decisions.md](01-decisions.md#banned-words-that-shape-names)),
the verbs in `functions.json`, `commitlint.json` (its scopes are the ones in
[README.md](README.md#how-to-use-these-plans)), `scopes.js`, `paths.py`,
`folders.py`, `integrity.py`, `quality/config/python/rules.py`,
`quality/config/shell.py`, the ESLint, knip, and madge settings (they name
`web/scripts/extension.ts`, `text.ts`, `http.ts`, and `host.d.ts`, which keep
their names in [04-architecture.md](04-architecture.md#webscripts)), the
license policies, `semgrep/packs.json` with `checksums.txt`, the gitleaks
`baseline.json` (`[]`) and `reasons.json` (`{}`), and the CodeQL Python,
Bearer, and OSV settings.

`quality/config/repository/functions.json` `allowlist`, the whole array, as
Step 1 leaves it (`c1dd344:quality/config/repository/functions.json`, lines
35 to 41):

```json
"allowlist": [
    {
        "path": "__init__.py",
        "names": ["comfy_entrypoint", "Extension.on_load", "Extension.get_node_list"],
        "reason": "ComfyUI calls these extension hooks itself."
    }
]
```

`repo:lint:policy` refuses an entry whose file or function does not exist, so
the first commit keeps only the `__init__.py` entry. The others arrive with
the method they name
([Tooling that later milestones add](#tooling-that-later-milestones-add)).

`quality/config/repository/functions.py`, lines 6 and 7, as Step 1 leaves
them:

```python
# The paid nodes reach ComfyNode through the extension's shared base class.
HOST_NODE_BASES = ("comfy_api.latest.io.ComfyNode", "src.nodes.base.PaidNode")
```

`src.nodes.base.PaidNode` exists from [Step 8](#step-8-create-the-skeleton).
[08-runs.md](08-runs.md) adds `"src.nodes.generate.GenerateNode"` to the
tuple in the change that fills `GenerateNode`, because each kind node's short
`define_schema` would otherwise fail the trivial-function check.

`quality/config/repository/directories.js`, line 3, as Step 1 leaves it:

```js
export const SINGLE_FILE_FOLDER_PATTERNS = ['web/scripts/*.ts'];
```

At Tooling, `web/scripts/` holds only `extension.ts` and `host.d.ts`, and
ESLint's `local/no-single-file-folders` does not count `host.d.ts`, so
without this entry `repo:lint:frontend` fails. This list is the check's own
exemption, and `allowlists.js` reports the entry if the folder disappears.
[16-frontend.md](16-frontend.md) sets it back to `[]` in the step that adds
the second TypeScript module.

`quality/config/security/gitleaks/config.toml`, the whole file:

```toml
title = "Dreamina node secret rules"

[extend]
useDefault = true
```

There is no Dreamina API key to look for: the CLI keeps the sign-in in the
OS credential store, and the pack keeps no token
([research/owner-rules.md](research/owner-rules.md#rules-added-for-dreamina)).
F's shape rule and `FAL_KEY` rule describe fal's key, so neither carries
over. gitleaks' default rules still run on the staged files, the worktree,
the history, and the release archive. No check requires a custom rule:
`quality/repository/integrity/gitleaks.py` reads only `baseline.json` and
`reasons.json`.

`quality/config/security/semgrep/secrets.yml`, the whole file:

```yaml
rules:
    - id: dreamina-secrets-hf-token-literal
      message: Do not commit HuggingFace token literals.
      severity: ERROR
      languages:
          - generic
      pattern-regex: 'hf_[A-Za-z0-9]{20,}'
```

F's two key rules, `fal-api-key-literal` and `fal-api-key-assignment-literal`
(`F/quality/config/security/semgrep/secrets.yml:8-19`), both name `FAL_KEY`
and are dropped. The pinned `secrets` pack still runs beside this rule.

`quality/config/security/semgrep/markers.yml`, the whole file:

```yaml
rules:
    - id: dreamina-python-no-obsolete-markers
      message: Do not use obsolete marker wording in Python source.
      severity: ERROR
      languages:
          - generic
      paths:
          include:
              - /src/**/*.py
              - /scripts/**/*.py
              - /__init__.py
              - /quality/**/*.py
      pattern-regex: '(?i)\b(?:legacy|deprecated|workaround|backward(?:\s|-)?compat(?:ible|ibility)|compatibility)\b'
```

One rule with all five words, as F's first commit had. Dreamina's `model
list` carries no model status word, so no split like F's (F row 232) is
expected. The CLI's own texts use "legacy" (its `upgradeUrl`), so Python
comments and docstrings describe that field without the word.

## Naming exceptions

`quality/config/naming/terms.json` stays unchanged. `Dreamina`,
`DreaminaError`, `X-Dreamina-Comfy`, `DREAMINA_COMFY_STATE_DIRECTORY`,
`DREAMINA_REFERENCES`, and `src/dreamina` hold no banned word, so the pack
needs no vendor-name exception beyond the two F already has.

`quality/config/naming/policy.json` `name_rules` keeps all ten of F's rules
(`F/quality/config/naming/policy.json:35-131`): the `.githooks` and `.mise`
folder names, the AST visitor methods, the two CodeQL variables, `_`, leading
underscores, the loop letters, `__init__` and `__main__`, `generic_visit`,
`on_load` in the root `__init__.py`, and `ModelInfo` in
`^src/nodes/model\.py$`. F holds no other vendor exception, so nothing is
dropped. Only the `ModelInfo` reason changes, at line 130:

```json
"reason": "Other extensions call Model: Info by its node ID, DreaminaModelInfo, which ComfyUI builds from this class name."
```

F added this rule with its Model: Info node (F row 245). It is kept from the
first commit because the owner authorized it for F and
[01-decisions.md](01-decisions.md#banned-words-that-shape-names) keeps it. A
rule for a path that does not exist yet fails no check. The plans keep
Dreamina's own banned words (`data`, `service`, `bind`, `resolution`, and the
rest) out of every declared name with Pydantic aliases, so no other exception
is expected.

In `quality/config/naming/javascript.json` `nameRules`, keep F's other web
rules: `Content-Type` and the dialog's `once` option. Make three edits:

1. Line 397, the `settings/schema.ts` wire names: drop `credential_limit`,
   F's key length limit (`F/src/settings/store.py:99`):

   ```json
   "names": ["setting_ranges", "mutation_allowed"],
   ```

1. Line 411, the header rule: replace the name, so the rule (lines 408 to
   414) reads:

   ```json
   {
       "pathRegexes": ["^web/scripts/settings/api\\.ts$"],
       "categories": ["properties", "functions"],
       "names": ["X-Dreamina-Comfy"],
       "allowedViolations": ["case"],
       "reason": "Local extension requests use this header name."
   }
   ```

1. Delete the `api_key` rule (lines 422 to 428), F's key route field
   (`F/src/settings/routes.py:43`), and change line 421 from `},` to `}`, so
   the array still ends with a valid object.

`X-Dreamina-Comfy` splits into `x`, `dreamina`, and `comfy`, none banned, so
only the case exception stays. [16-frontend.md](16-frontend.md) adds any snake
case wire name of the account and CLI status reply to the
`settings/schema.ts` rule in the change that reads it.

## Step 7: Re-value the scripts

| File                                         | Edit                                                                                                                          |
| -------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| `scripts/nodes/schema.py:31-34`              | F's multi-typed widget test becomes B's one-line test, below                                                                  |
| `scripts/nodes/schema.py:104-105`            | The `main` docstring's second paragraph, below                                                                                |
| `scripts/nodes/schema.py:108`                | `tempfile.TemporaryDirectory(prefix="comfyui-dreamina-schema-")`                                                              |
| `scripts/nodes/check.py:86`                  | `f"Put {node_id} in a Dreamina menu."`                                                                                        |
| `scripts/workflows/page/graph.py:15`         | `NAMESPACE = uuid.UUID("05f62da6-1302-4067-b6d8-e83cf4a52f83")`                                                               |
| `scripts/workflows/build.py`                 | None: Step 1 took F's first-commit file, with an empty family list, below                                                     |
| `scripts/workflows/descriptions/texts.py`    | New: the three titles the engine reads, below                                                                                 |

`scripts/nodes/schema.py`, `_build_node_schema`: replace lines 31 to 34 (the
comment naming File: Add, `is_typed_widget`, `is_plain_widget`, and the
`is_widget` that joins them) with B's one line,
`B/scripts/nodes/schema.py:29`. The loop then reads:

```python
    for item in schema.inputs:
        fields = cast("dict[str, object]", item.as_dict())
        is_widget = isinstance(item, io.WidgetInput | io.DynamicCombo.Input) and not fields.get("forceInput")
        inputs.append({"name": item.id, "type": item.get_io_type(), "widget": is_widget, **fields})
```

F added the multi-typed test for File: Add's `file` input (F row 223). No
Dreamina node in [01-decisions.md](01-decisions.md#the-nodes) has a
multi-typed widget input, and a branch nothing reaches is dead code. If
[13-node-element.md](13-node-element.md) or a later plan gives a node such an
input, that plan brings back `F/scripts/nodes/schema.py:31-34` in the same
change. The imports stay: `io` and `cast` are still used.

`scripts/nodes/schema.py`, the `main` docstring:

```python
    """Print the node descriptions of this extension and of the host nodes the workflows use.

    The extension's state folder is a new empty one, so Generation: Download lists no generations and the export is
    the same on every machine.
    """
```

The longer line is 115 characters, under Ruff's 120.

The namespace is a new random UUID, made once on 2026-10-16 with
`python3 -c "import uuid;print(uuid.uuid4())"`. Every workflow ID is
`uuid5(NAMESPACE, slug)`, every subgraph ID `uuid5(NAMESPACE, "<slug>/<name>")`,
and every blueprint ID `uuid5(NAMESPACE, "blueprint.<name>")`. With F's
namespace, a Dreamina example whose slug and step name matched an F one would
get F's ID, and ComfyUI identifies workflows and subgraphs by ID. The value
differs from F's, B's, and O's
([research/tooling.md](research/tooling.md#2-names-the-fal-value-and-the-dreamina-value))
and never changes after the first example ships, because changing it changes
every ID.

`scripts/workflows/build.py`, as Step 1 leaves it, imports no family module
and no `MENUS`. Its family list (`c1dd344:scripts/workflows/build.py`, lines
32 to 35) reads:

```python
# Each family's workflows, with the node menu their subgraph blueprints are listed in.
# The cast keeps the empty tuple from narrowing to no type until the first family is added.
FAMILIES = cast("tuple[tuple[tuple[Workflow, ...], str], ...]", ())
WORKFLOWS = tuple(workflow for workflows, _menu in FAMILIES for workflow in workflows)
```

basedpyright narrows an annotated empty tuple to `tuple[()]`, so the
`WORKFLOWS` generator would iterate `Never`; the `cast` keeps the declared
type (F row 222). F's first commit passed every hook with this form. Each node
milestone adds its family's import and its `FAMILIES` entry; with the first
one, `FAMILIES` becomes a plain tuple, its second comment and the `cast` go,
and the `MENUS` import returns
([17-scripts-and-workflows.md](17-scripts-and-workflows.md)).

`scripts/workflows/descriptions/texts.py`, the content of
`c1dd344:scripts/workflows/descriptions/texts.py`:

```python
"""The titles of the shipped workflows' groups, subgraphs, notes and nodes."""

SHARED_TEXTS = {
    "start": "Start Here",
    "note": "Note",
    "input": "Input",
}

__all__ = ["SHARED_TEXTS"]
```

`build.py` titles the first group's note `SHARED_TEXTS["start"]` and every
later note `SHARED_TEXTS["note"]`; `"input"` is the inputs group's title.
[17-scripts-and-workflows.md](17-scripts-and-workflows.md) adds the Dreamina
titles, `notes.py`'s texts, `nodes.py`, and the family modules.

With `FAMILIES` empty and no nodes registered, `comfy:workflows:build` writes
nothing, `comfy:workflows:check` reports nothing once `README.md` exists, and
`comfy:nodes:check` finds no node to check.

Unchanged: `scripts/__init__.py` (its docstring names no provider),
`paths.py`, `types.py`, `dependencies.py`, `frontend.py` (it bundles
`web/scripts/extension.ts` and keeps ComfyUI's `app.js` and `api.js`
external), `nodes/host.py`, and the rest of `page/`. `schema.py` already
imports `INPUT_NAMES` from `src.config.inputs` and exports each input's type
with `item.get_io_type()`.

## Step 8: Create the skeleton

The import contracts need every runtime package, and the scripts and the root
`__init__.py` import seven runtime names: `MENUS`, `NODE_TYPES`, `PaidNode`,
`create_runtime`, `register_routes`, `INPUT_NAMES`, and
`ENVIRONMENT_VARIABLES` (`F/scripts/nodes/check.py:11`,
`F/scripts/nodes/schema.py:18-23`, `F/__init__.py:16-17`). This step creates
the packages and those names as stubs that later plans fill, plus
`NODE_PREFIX`, which
[17-scripts-and-workflows.md](17-scripts-and-workflows.md)'s workflow
descriptions import, and the entries the copied checks need. Each stub follows
F's first commit, with Dreamina's names.

| Path                                       | Content                                                                                                           | Filled by                                                       |
| ------------------------------------------ | ----------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------- |
| `src/__init__.py`                          | Docstring: `"""Node logic for Dreamina, independent of the ComfyUI loader."""`                                    | Stays                                                           |
| `src/config/__init__.py`                   | Docstring: `"""Fixed settings shared by the runtime and the build tools."""`                                      | Stays                                                           |
| `src/config/namespace.py`                  | `NODE_PREFIX` and `MENUS` with the shared menu, below                                                             | [05](05-foundation.md): the kind menus and `SOCKET_TYPES`       |
| `src/config/storage.py`                    | `ENVIRONMENT_VARIABLES` with `STATE_DIRECTORY`, below                                                             | [05](05-foundation.md): `DREAMINA_CANVAS_INSTALL_DIR`, the state folder names, and the file names |
| `src/config/inputs.py`                     | `INPUT_NAMES` with `RUN_NUMBER`, below                                                                            | [06](06-model-check.md): the other shared inputs and their tooltips |
| `src/types/__init__.py`                    | The `Value` and `Reply` pydantic bases, below                                                                     | [05](05-foundation.md): the `Json`, `Kind`, and `MediaKind` aliases |
| `src/storage/__init__.py`                  | Docstring: `"""Private files outside ComfyUI: the settings, the canvas, and the generation records."""`           | Stays                                                           |
| `src/settings/__init__.py`                 | Docstring: `"""The private settings, their local route, and the snapshot each run reads."""`                      | Stays                                                           |
| `src/dreamina/__init__.py`                 | Docstring: `"""Every call to the Dreamina CLI: sign-in, model reads, uploads, generations, and downloads."""`      | Stays                                                           |
| `src/comfy/__init__.py`                    | Docstring: `"""Connect Dreamina runs and local routes to the ComfyUI host."""`                                    | Stays                                                           |
| `src/comfy/runtime.py`                     | `create_runtime` with an empty body, below                                                                        | [05](05-foundation.md): `Runtime`, `get_runtime`                |
| `src/comfy/routes.py`                      | `register_routes` with an empty body, below                                                                       | [05](05-foundation.md)                                          |
| `src/nodes/__init__.py`                    | `NODE_TYPES` as an empty tuple, below                                                                             | Each node plan adds its class                                   |
| `src/nodes/base.py`                        | `PaidNode` with its `send` entry point, below                                                                     | [08](08-runs.md)                                                |
| `src/nodes/generate.py`                    | Docstring only: `"""The shared generation node the image, video, and audio nodes subclass."""`                    | [08](08-runs.md): `GenerateNode`                                |
| `scripts/workflows/descriptions/notes.py`  | Docstring only: `"""The group notes and subgraph descriptions of the shipped workflows, in plain language."""`    | [17](17-scripts-and-workflows.md)                               |
| `web/scripts/extension.ts`, `web/scripts/host.d.ts`, `web/styles/interface.css` | Created by [16-frontend.md](16-frontend.md#step-1-entry-files) Step 1               | [16](16-frontend.md)                                            |
| `README.md`                                | Created by [18-documentation.md](18-documentation.md#step-1-readme-start) Step 1                                  | [18](18-documentation.md)                                       |

Why three entries exist only for the copied checks:

- `src/nodes/generate.py` and `scripts/workflows/descriptions/notes.py` exist
  because the `python.single-file-package` rule refuses a package that holds
  exactly one module and no subpackage. Without them `src/nodes/` would hold
  only `base.py`, and `descriptions/` only `texts.py`. `src/nodes/generate.py`
  is the module [04-architecture.md](04-architecture.md#srcnodes) already
  plans, so the stub is not a throwaway. `src/config/` holds three modules
  and `src/comfy/` two, so they need no stub; `src/dreamina/`,
  `src/settings/`, `src/storage/`, and `src/types/` hold only their
  `__init__.py`, which the rule does not count, as in F's first commit.
- `src/types/__init__.py` holds the pydantic bases now because deptry reports
  a declared dependency that nothing imports (`DEP002`), and `pydantic` is the
  pack's one runtime dependency.

No stub is a module with only an `__all__`: outside `__init__.py`, the
`exports.only` rule refuses a module whose only statements are imports and
`__all__`. A docstring-only module passes. Each stub carries the docstring its
owning plan keeps.

`src/config/namespace.py`:

```python
"""The names this extension uses in spaces shared with other packs."""

# Every node identifier is this prefix and the class name.
NODE_PREFIX = "Dreamina"

# The menu headings the nodes are grouped under.
MENUS = {
    "SHARED": "Dreamina",
}

__all__ = [
    "MENUS",
    "NODE_PREFIX",
]
```

`src/config/storage.py`:

```python
"""The private state folder, its files and their size limits, and the environment variables that move them."""

# An absolute folder that replaces the platform's own state folder.
ENVIRONMENT_VARIABLES = {
    "STATE_DIRECTORY": "DREAMINA_COMFY_STATE_DIRECTORY",
}

__all__ = ["ENVIRONMENT_VARIABLES"]
```

`src/config/inputs.py`:

```python
"""Names of the inputs every paid node shares."""

# The inputs every paid node shares.
INPUT_NAMES = {
    "RUN_NUMBER": "run_number",
}

__all__ = ["INPUT_NAMES"]
```

`src/types/__init__.py`:

```python
"""Records shared by the runtime: dataclasses for in-process values, pydantic models for JSON."""

from pydantic import BaseModel, ConfigDict


class Value(BaseModel):
    """A frozen record that refuses unknown fields, for files this extension writes."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class Reply(BaseModel):
    """A frozen record that ignores unknown fields, for the JSON the Dreamina CLI prints."""

    # The CLI adds fields in new releases; a new field must not break a paid run that already succeeded.
    model_config = ConfigDict(extra="ignore", frozen=True)


__all__ = ["Reply", "Value"]
```

`src/comfy/runtime.py`:

```python
"""Create the shared stores when ComfyUI loads the extension."""


def create_runtime() -> None:
    """Initialize once through the host's extension lifecycle, without network calls."""


__all__ = ["create_runtime"]
```

`src/comfy/routes.py`:

```python
"""Register the extension's local routes with ComfyUI."""


def register_routes() -> None:
    """Reject public state locations before enabling writes, then register every local route."""


__all__ = ["register_routes"]
```

`src/nodes/__init__.py`:

```python
"""Register the extension's nodes in menu order."""

from comfy_api.latest import io

NODE_TYPES: tuple[type[io.ComfyNode], ...] = ()

__all__ = ["NODE_TYPES"]
```

`src/nodes/base.py`. `scripts/nodes/schema.py` reads `PaidNode.send`'s
parameters, so the class declares it:

```python
"""Share the cache key and the run-number input across the paid nodes."""

from typing import ClassVar
from comfy_api.latest import io
from collections.abc import Callable, Awaitable


class PaidNode(io.ComfyNode):
    """Own the run-number input every paid node shares.

    Attributes:
        send: Typed entry point that receives every saved input except the run number.

    """

    send: ClassVar[Callable[..., Awaitable[io.NodeOutput]]]


__all__ = ["PaidNode"]
```

Imports are ordered by line length, as the copied `import.order` rule
requires. A function whose body is only its docstring has no statement, so the
function policy does not report it as trivial. Every stub above equals its
file in F's first commit except for the Dreamina names in docstrings and
values.

## Step 9: Lock and install

```sh
mise trust mise.toml
mise trust .mise.local.toml
mise install
uv lock
bun install
mise run repo:setup
mise run repo:deps:export
```

- `mise install` installs the tools in `mise.toml`. All of them are already
  installed for F at the same versions, so it only links them.
- `uv lock` renames the root package in `uv.lock` from `fal-ai`
  (`F/uv.lock:441`) to `dreamina`. Every other version stays, because uv
  keeps locked versions that still satisfy the unchanged dependency lists.
- `bun install` does not rename the root package in `bun.lock`: Bun 1.3.11
  keeps the workspace `"name"` it finds (line 6), even after a later
  `bun remove`. Edit that one line to `"name": "comfyui-dreamina",` by hand,
  the `package.json` name; `bun install --frozen-lockfile` accepts the result,
  and every resolved version stays.
- `repo:setup` runs `mise install`, then `repo:deps` (the dev group into
  `.venv`, the Bun packages into `node_modules`, both from the locks), then
  `repo:security:rules`, which downloads the pinned Semgrep packs into
  `.artifacts/security/semgrep/rules` and needs the network, then sets
  `core.hooksPath` to `.githooks`. From here on the hooks run on every commit
  and push.
- `repo:deps:export` writes `requirements.txt`:

```text
# Generated from pyproject.toml by mise run repo:deps:export.
pydantic>=2.10,<3
```

Then confirm the two lock names: `grep -c 'fal-ai' uv.lock` and
`grep -c 'comfyui-fal' bun.lock` each print `0`, and `sed -n 6p bun.lock`
prints `"name": "comfyui-dreamina",` with its indent. The leftover-name search
in [Step 10](#step-10-first-commit) skips both locks, because their integrity
hashes hold random letters.

If `repo:security:rules` stops because the Semgrep registry serves different
content for a pinned rule (F row 220), copy F's local packs, which match the
same pins, check them, and finish the setup by hand. Change no pin:

```sh
mkdir -p .artifacts/security/semgrep
cp -R /Users/dr_stone/Documents/work/comfyui-fal/.artifacts/security/semgrep/rules .artifacts/security/semgrep/
shasum -a 256 -c quality/config/security/semgrep/checksums.txt
uv run --no-sync python -m quality.repository.hooks.setup
```

`shasum` must print `OK` for all five packs; it did in F on 2026-10-16. The
last command is the step `repo:setup` runs after `repo:security:rules`
(`F/.mise/tasks/repo/setup`). Record the fallback in the changes table.

Commit both locks and `requirements.txt` in Step 10. `repo:deps:verify` (in
the pre-push check) refuses a hand edit of `requirements.txt`.

The license policies need no edit: the locks hold the versions their
exemptions cite. If a later lock change makes `repo:licenses` or
`repo:audit:frontend` (both in the pre-push check) report a package, edit only
the license policy with a reason naming the installed version, or add an exact
override as B's `6d7af22` did, in a `build(deps)` commit.

After this step the tooling is installed, but `web/` and `README.md` do not
exist yet, so the frontend checks and the workflow check cannot pass. The
steps in Step 10's list create them.

## Step 10: First commit

The hooks check files that other plans create. Do these first, in this order,
as [README.md](README.md#build-order) lists for the Tooling milestone:

1. [19-brand-assets.md](19-brand-assets.md#step-1-badges-and-banner) Step 1:
   the four badges and `banner.svg`, which the README start links.
1. [18-documentation.md](18-documentation.md#step-1-readme-start) Step 1: the
   start of `README.md`. The workflow check reads it, and the Markdown and
   local link checks lint it and every image it links, so it links only
   images that exist in the commit.
1. [16-frontend.md](16-frontend.md#step-1-entry-files) Step 1: the browser
   entry files. It removes `valibot` with `bun remove valibot`, puts
   `package.json`'s keys back in F's order without `dependencies`, and
   restores the braces override's full commit hash in `bun.lock`, which
   `bun remove` shortens and OSV then refuses (F row 227):
   `grep -c 'braces#d0d575e55e74a4e0218e5248fafb79efc3e54ebb' bun.lock` prints
   `2`. It copies `web/scripts/host.d.ts` and `web/styles/interface.css` from
   F at `cef8b6e` (both unchanged since `c1dd344`), replacing every `fal-ai-` class with `dreamina-`, and
   writes `web/scripts/extension.ts`, registered as `dreamina`, which imports
   `#styles/interface.css` so esbuild writes `extension.css`. TypeScript needs
   one source file, knip starts from `extension.ts`, and madge reads
   `host.d.ts`.
1. [17-scripts-and-workflows.md](17-scripts-and-workflows.md#step-1-scripts-the-hooks-need)
   Step 1: the scripts the hooks need.
1. The step of [16-frontend.md](16-frontend.md) that builds the bundle:
   `mise run comfy:frontend:build` writes `web/extension.js` and
   `web/extension.css`, which `comfy:frontend:check` compares byte for byte at
   every commit.

Then stage everything, confirm the plans stayed out, and search the staged
files for the names of F, B, and O:

```sh
git add -A
git status --short -- plans/research/docs plans/research/captures | grep -c .
git grep -nIP '(?i:\bfal\b|fal-ai|comfyui-fal|byteplus|modelark|ark_api_key|hyper3d|hitem3d|openrouter|sk-or-v1)|\bFal[A-Z]|FAL_|X-Fal-|EndpointNode|Request: Download|File: Add|Request Options|api_key|credential_limit' -- . ':!uv.lock' ':!bun.lock' ':!plans/'
```

The first count must print `0`: the plans themselves are already committed,
and their ignored folders stay out. `git grep` searches only tracked files, so
it runs after `git add`; it must print nothing. A line it prints is a value
Steps 2 to 8 or the steps listed above missed. `.gitignore` keeps the plans' skill copy and captures,
`.mise.local.toml`, `.venv/`, `node_modules/`, and `.artifacts/` out of the
index.

How the search is built:

- `-P` (Perl regular expressions), because `git grep -E` with `\b` matches
  nothing with this machine's git 2.55.0
  ([research/tooling.md](research/tooling.md#1-headline-findings), finding 7).
- The `(?i:…)` group ignores case: fal's names with word boundaries, so
  `fallback` and `false` never match, and B's and O's names (`byteplus`,
  `modelark`, `ark_api_key`, `hyper3d`, `hitem3d`, `openrouter`, `sk-or-v1`).
- The rest is case-sensitive: `\bFal[A-Z]` (`FalError`, `FalModelInfo`),
  `FAL_` (`FAL_KEY`), `X-Fal-`, and F's runtime names (`EndpointNode`,
  **Request: Download**, **File: Add**, **Request Options**, `api_key`,
  `credential_limit`).
- No Dreamina model family is in the pattern. `seedance`, `seedream`, and
  `dreamina` are Dreamina's own names, so they never count as leftovers.

Run over F's own files at `cef8b6e`, the same pattern printed exactly the 56
lines Steps 1 to 7 change and nothing from `rules/`, `.mise/`, or
`.githooks/` ([research/tooling.md](research/tooling.md#12-procedure)).

Commit on `main`. It is the repository's first commit:

```sh
git commit -m "build(quality): bring in the repository tooling"
```

The pre-commit hook scans the staged files for secrets, then runs
`repo:lint`, `repo:format:check`, `repo:type:python`, `repo:type:frontend`,
and `comfy:frontend:check`; the commit-msg hook checks the message against
`commitlint.json`. A failure means a step above was missed; fix it and commit
again.

Then push. During F's build the owner asked for every commit to be pushed at
once (F row 226), and
[research/owner-rules.md](research/owner-rules.md#commits-and-git) carries
the rule. Before this first push, confirm with the owner that
`stefanionescu/comfyui-dreamina` exists on GitHub and that pushing now is
wanted; until then, leave the commit unpushed:

```sh
git push -u origin main
```

The pre-push hook runs `mise run repo:check`: every local check, the node and
workflow checks, the security scans, and the external link check. Any failure
stops the push.

## Step 11: Link the pack into ComfyUI

ComfyUI loads a pack from its `custom_nodes` folder. The development
installation gets a symbolic link to the working copy, so every later change
is what ComfyUI loads, as the owner's other packs are linked
(`custom_nodes/fal-ai`, `custom_nodes/byteplus`, `custom_nodes/openrouter`).
The link name is the install folder from
[01-decisions.md](01-decisions.md#names-and-identifiers), `dreamina`, which is
also the folder `LINK_ALIASES` names. ComfyUI names the template group and
the node badges after this folder.

```sh
C=/Users/dr_stone/ComfyUI-Installs/ComfyUI/ComfyUI
test ! -e "$C/custom_nodes/dreamina"
ln -s /Users/dr_stone/Documents/work/comfyui-dreamina "$C/custom_nodes/dreamina"
```

The `test` must succeed: a file or folder already at that path is not this
pack's and is left alone. On 2026-10-16 nothing was there, and no folder in
`custom_nodes` was named after Dreamina, Jimeng, Seedance, or ByteDance. The
link changes nothing in the repository, so nothing is committed.

ComfyUI reads `custom_nodes` only when it starts, and a running ComfyUI holds
the owner's work, so do not restart it. Tell the owner the link exists;
ComfyUI loads the pack at its next start, which the owner chooses. Loading the
skeleton is harmless: `on_load` runs the two empty stubs, and `NODE_TYPES` is
empty. No ID, route, socket type, or extension name of this pack matches one
of the owner's other packs or ComfyUI core's
([04-architecture.md](04-architecture.md#ids-other-packs-use)). None of the
checks need the link: `scripts/nodes/schema.py` loads the pack from the
working copy with ComfyUI's interpreter.

## Tooling that later milestones add

These tooling edits belong to later milestones, because each names a file,
method, or folder that does not exist at Tooling, and the copied checks refuse
an entry whose target is missing. The owning plan makes each edit in the
change that creates its target; this table is the list to check against.

| Milestone and plan                                           | Edit                                                                                                                       | Why it waits                                                    |
| ------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------- |
| Foundation, [05](05-foundation.md)                           | `functions.json` `allowlist`: each route handler aiohttp calls whose body is two statements or fewer gets an entry with the reason "aiohttp calls this route handler itself.", as F's `ConfigurationRoutes.read_status` did (`F/quality/config/repository/functions.json:46-50`); Dreamina's status handler is in `AccountRoutes` in `src/comfy/account.py` ([04-architecture.md](04-architecture.md#srccomfy)) | `repo:lint:policy` refuses an entry whose method is missing     |
| Runs, [08](08-runs.md)                                       | `functions.py` `HOST_NODE_BASES` gains `"src.nodes.generate.GenerateNode"`, with the comment "The paid nodes reach ComfyNode through PaidNode, and the kind nodes through GenerateNode.", in the change that fills `GenerateNode`; `functions.json` entries for `GenerationOperation.validate` and `CollectOperation.validate` in `src/dreamina/generations/operation.py`, with F's reason "The run wrapper calls it through the Operation protocol.", if they only hand the check on, as F's do; an exact temporary entry for each public function no other module calls yet, removed with its first call (F rows 225, 228) | The class and methods do not exist yet                          |
| Image: Upscale, [12](12-node-upscale.md)                     | `functions.json`: `UpscaleOperation.validate` in `src/dreamina/upscale.py`, with the same reason, if it has the same shape  | The method does not exist yet                                   |
| Frontend, [16](16-frontend.md)                               | `directories.js` `SINGLE_FILE_FOLDER_PATTERNS` back to `[]`; `bun add --exact valibot@1.5.0`, then `dependencies` moved back after `packageManager` and the braces hash restored to its full form (F row 233); snake case wire names of the status reply added to the `settings/schema.ts` naming rule | Each follows a frontend module that does not exist yet           |
| Any milestone                                                | `[tool.interrogate]` `ignore-overloaded-functions = true` with its comment, in the change that adds the first `@overload`; a split of `markers.yml`, as F's (F row 232), only if a module must hold one of its five words as the CLI writes it | Dead configuration until then                                    |
| Scripts and workflows, [17](17-scripts-and-workflows.md)     | `scripts/nodes/host.py` and `scripts/workflows/page/config.py` `DOM_SIZES` for the host nodes Dreamina's examples place, each new one measured on frontend 1.52.7; each family's import and `FAMILIES` entry in `build.py`, with the plain tuple and the `MENUS` import from the first one | The examples are written there                                   |
| Documentation and brand, [19](19-brand-assets.md)            | `[tool.comfy]` `Icon = "https://raw.githubusercontent.com/stefanionescu/comfyui-dreamina/main/docs/images/brand/logo.png"`, after `DisplayName` | The logo does not exist yet                                      |
| Release, [20](20-release.md)                                 | `[project]` `urls.Issues` and `urls.Repository`; `[tool.comfy]` `PublisherId`                                              | The owner decides when to publish                                |

The `ModelInfo` naming rule is not in this table: it is already in
`policy.json` from [Step 6](#naming-exceptions).

A new function verb, such as `run`, `check`, `install`, or `upload`, would
need both `functions.json` and the protected `rules/NAMING.md`, so it needs
the owner. The policy checks every function and method in `src/`,
`scripts/`, and `__init__.py`
(`F/quality/repository/functions/python.py:164-178`). The plans use the
listed verbs instead: `send_command` for a CLI call, `validate_cli` for the
version gate, `download_installer` and `save_cli` for the install,
`create_sign_in` and `delete_sign_in`, `send_media` for an upload,
`plan_references`, `format_prompt`, and `find_canvas` and `create_canvas`
([04-architecture.md](04-architecture.md#srcdreamina),
[research/tooling.md](research/tooling.md#83-function-policy-functionsjson-and-functionspy)).
A temporary `functions.json` entry for one of them, while no other module
calls it yet, names it exactly as 04 does.

## Names this plan uses from other plans

| Name                                                                                  | Owner                                                                    |
| ------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| Repository `comfyui-dreamina`; project, Registry ID, and install folder `dreamina`; display name and menu root `Dreamina`; `NODE_PREFIX` `Dreamina`; extension name `dreamina`; `X-Dreamina-Comfy`; `DREAMINA_COMFY_STATE_DIRECTORY`; CSS prefix `dreamina-` | [01-decisions.md](01-decisions.md#names-and-identifiers) |
| The seven runtime packages, the import layers, and the four re-valued contracts       | [04-architecture.md](04-architecture.md#import-linter-contracts)        |
| `src/nodes/generate.py` and `GenerateNode`; `src/nodes/base.py` and `PaidNode`; `src/config/inputs.py` and `INPUT_NAMES`; `src/config/storage.py` and `ENVIRONMENT_VARIABLES`; `src/config/namespace.py`, `NODE_PREFIX`, and `MENUS`; `create_runtime`, `register_routes`, `NODE_TYPES`; `AccountRoutes` in `src/comfy/account.py`; `GenerationOperation`, `CollectOperation`, `UpscaleOperation` | [04-architecture.md](04-architecture.md#module-inventory) |
| `ModelInfo` in `src/nodes/model.py`, node ID `DreaminaModelInfo`                      | [15-node-model-info.md](15-node-model-info.md)                           |
| The banned words and their local names                                                | [01-decisions.md](01-decisions.md#banned-words-that-shape-names)         |
| Step 1 "Entry files" (`bun remove valibot`, `host.d.ts`, `interface.css`, `extension.ts`) and the bundle step | [16-frontend.md](16-frontend.md#step-1-entry-files)          |
| Step 1 "Scripts the hooks need"                                                       | [17-scripts-and-workflows.md](17-scripts-and-workflows.md#step-1-scripts-the-hooks-need) |
| Step 1 "README start"                                                                 | [18-documentation.md](18-documentation.md#step-1-readme-start)          |
| Step 1 "Badges and banner"                                                            | [19-brand-assets.md](19-brand-assets.md#step-1-badges-and-banner)       |
| The Tooling milestone and its commit subject                                          | [README.md](README.md#build-order)                                       |
| The one-time setup, `urls.*`, and `PublisherId`                                       | [20-release.md](20-release.md#one-time-setup)                            |
