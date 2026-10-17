# Tooling Port Sheet for Dreamina

This report gives, for every tooling value the fal pack re-valued when it was
set up from the BytePlus pack, the fal value and the Dreamina value. It is the
evidence behind [../03-repository-setup.md](../03-repository-setup.md), which
holds the steps. It was written on 2026-10-16 for the engineer or agent who
follows that plan, and for the owner, who decides the items marked
**Owner**. Nothing is built yet.

Sources, all read only:

- `F=/Users/dr_stone/Documents/work/comfyui-fal`, commit `cef8b6e` (newest),
  and its first commit `c1dd344` ("build(quality): bring in the repository
  tooling"), which is F's tooling-time state. F's own sheet,
  `F/plans/research/tooling.md`, describes B's tooling file by file; this
  report does not repeat it.
- `B=/Users/dr_stone/Documents/work/comfyui-byteplus`, commit `472cf10`, and
  `O=/Users/dr_stone/Documents/work/comfyui-openrouter`, commit `c076f37`.
- The Dreamina repository, `/Users/dr_stone/Documents/work/comfyui-dreamina`:
  branch `main`, no commits, only the untracked `plans/` folder.
- The ComfyUI installation `/Users/dr_stone/ComfyUI-Installs/ComfyUI/ComfyUI`.

How the sources are cited:

- `F/<path>:N` is line N of that file at `cef8b6e`.
- `c1dd344:<path>:N` is line N of the file in F's first commit; read it with
  `git -C "$F" show c1dd344:<path>`.
- "F row N" is line N of `F/plans/README.md`, a row of its changes table.

## Contents

- [1. Headline findings](#1-headline-findings)
- [2. Names: the fal value and the Dreamina value](#2-names-the-fal-value-and-the-dreamina-value)
- [3. What F holds](#3-what-f-holds)
- [4. Root files](#4-root-files)
- [5. Files copied unchanged](#5-files-copied-unchanged)
- [6. quality/: every fal value and its Dreamina value](#6-quality-every-fal-value-and-its-dreamina-value)
- [7. Secret rules](#7-secret-rules)
- [8. Naming and function policies](#8-naming-and-function-policies)
- [9. Banned words the Dreamina CLI hits](#9-banned-words-the-dreamina-cli-hits)
- [10. scripts/: every fal value and its Dreamina value](#10-scripts-every-fal-value-and-its-dreamina-value)
- [11. Release configuration](#11-release-configuration)
- [12. Procedure](#12-procedure)
- [13. Decisions for the owner](#13-decisions-for-the-owner)

## 1. Headline findings

1. **Copy from F, not B.** F's tooling is B's tooling with fal values, plus
   F's own fixes (F rows 220 to 233). Since F's first commit, F changed only
   these tooling files (`git -C "$F" diff --stat c1dd344 cef8b6e`):
   `quality/config/naming/policy.json`,
   `quality/config/repository/directories.js`, `functions.json`, and
   `functions.py`, `quality/config/security/semgrep/markers.yml`,
   `scripts/workflows/build.py`, `pyproject.toml`, `package.json`, and
   `bun.lock`, plus the workflow descriptions, which Dreamina does not copy.
   The rest of `quality/`, `.mise/`, `.githooks/`, `rules/`, the root
   configuration, and `scripts/` is byte-identical to `c1dd344`.
2. **F's later-milestone values go back to F's tooling-time values.** Each
   of those changed files holds a value that names a module, method, or file
   that exists only after a later milestone. Dreamina's Tooling commit takes
   the `c1dd344` value for each, and the owning plan adds the later value in
   the change that creates its target
   ([../03-repository-setup.md](../03-repository-setup.md#tooling-that-later-milestones-add)).
   The one exception is the `ModelInfo` naming rule, which is kept
   ([8.1](#81-naming-policy-policyjson)).
3. **No API key exists.** The Dreamina CLI owns sign-in
   ([../01-decisions.md](../01-decisions.md#sign-in-and-privacy)). So the
   gitleaks configuration keeps gitleaks' default rules only, the Semgrep
   secrets file keeps only its HuggingFace rule, and the JavaScript naming
   policy drops F's `api_key` rule and its `credential_limit` wire name
   ([section 7](#7-secret-rules), [8.2](#82-javascript-naming-policy-javascriptjson)).
4. **`dreamina` hits no banned word.** `Dreamina`, `DreaminaError`,
   `X-Dreamina-Comfy`, `DREAMINA_REFERENCES`, `DREAMINA_COMFY_STATE_DIRECTORY`,
   and `src/dreamina` need no naming exception beyond the header's case
   exception F also has. typos 1.43.5 accepts every Dreamina name in the
   plans, including `Seedance`, `Seedream`, `Jimeng`, `CapCut`, `t2v`, `m2v`,
   and the CLI's camelCase fields (checked on 2026-10-16 on a scratch file
   with `~/.local/share/mise/installs/typos/1.43.5/typos`).
5. **The CLI's own words do hit banned terms**: `data`, `service`, `bind`,
   `resolution`, and others ([section 9](#9-banned-words-the-dreamina-cli-hits)).
   Pydantic aliases avoid them, as
   [../01-decisions.md](../01-decisions.md#banned-words-that-shape-names)
   says.
6. **Every function name in 04 passes the function policy.** The policy
   refuses a function in `src/`, `scripts/`, or `__init__.py` whose first
   word is not one of the 26 verbs in `F/quality/config/repository/functions.json:5-32`
   (`F/quality/repository/functions/python.py:164-178`). The CLI calls are
   named with listed verbs, such as `send_command` and `validate_cli`, and
   no name uses the banned `ensure`
   ([8.3](#83-function-policy-functionsjson-and-functionspy)).
7. **`git grep -E '\b…\b'` matches nothing on this machine.** With
   git 2.55.0, `git -C "$F" grep -nIiE '\bfal\b'` prints nothing, while
   `git grep -nIiP '\bfal\b'` and `git grep -nIiw fal` print every line that
   names fal. The leftover-name search in 03 uses `-P` for that reason.
8. **The Registry ID `dreamina` is free.** `https://api.comfy.org/nodes/dreamina`
   answered 404 on 2026-10-16
   ([../01-decisions.md](../01-decisions.md#names-and-identifiers)).
9. **The ComfyUI on this machine is the one F was built against**:
   ComfyUI 0.37.2 (`comfyui_version.py`), frontend 1.52.7
   (`comfyui-frontend-package==1.52.7` in `requirements.txt`), interpreter
   `.venv/bin/python`. F's measured page sizes hold. No folder in
   `custom_nodes` and no package in its `.venv` is named after Dreamina,
   Jimeng, or CapCut, and `custom_nodes/dreamina` does not exist.
10. **F's local Semgrep packs match the pins.**
    `shasum -a 256 -c quality/config/security/semgrep/checksums.txt`, run in
    F on 2026-10-16, printed `OK` for all five packs in
    `F/.artifacts/security/semgrep/rules/`. They are the fallback if the
    Semgrep registry drifts, as it did for F (F row 220).
11. **Every pinned tool is installed** at the version `F/mise.toml:1-15`
    names (python 3.12.13, uv 0.11.21, bun 1.3.11, shellcheck 0.11.0, shfmt
    3.13.0, gitleaks 8.30.0, typos 1.43.5, codeql 2.26.4, Bearer 2.0.1, jq
    1.8.1, osv-scanner 2.3.3, semgrep 1.152.0, comfy-cli 1.20.0), read from
    `~/.local/share/mise/installs/` without running mise.
12. **ComfyUI core names BytePlus models `dreamina-seedance-…`.**
    `comfy_api_nodes/nodes_bytedance.py` and `comfy_api_nodes/apis/bytedance.py`
    hold model IDs such as `dreamina-seedance-2-5-260628`. They are model
    IDs, not node IDs; no core node ID starts with `Dreamina`.

## 2. Names: the fal value and the Dreamina value

The Dreamina values come from
[../01-decisions.md](../01-decisions.md#names-and-identifiers). Labels write
"Dreamina", as Dreamina writes its own name.

| Item                                | fal value (where)                                                                 | Dreamina value                                                     |
| ----------------------------------- | --------------------------------------------------------------------------------- | ------------------------------------------------------------------ |
| Repository                          | `comfyui-fal`                                                                     | `comfyui-dreamina`                                                 |
| `[project].name`, Registry ID       | `fal-ai` (`F/pyproject.toml:2`)                                                   | `dreamina`                                                         |
| Install folder                      | `custom_nodes/fal-ai`                                                             | `custom_nodes/dreamina`                                            |
| `package.json` name                 | `comfyui-fal` (`F/package.json:2`)                                                | `comfyui-dreamina`                                                 |
| `quality/package.json` name         | `comfyui-fal-quality` (`F/quality/package.json:2`)                                | `comfyui-dreamina-quality`                                         |
| `bun.lock` workspace name           | `comfyui-fal` (`F/bun.lock:6`)                                                    | `comfyui-dreamina`                                                 |
| `uv.lock` root package              | `fal-ai` (`F/uv.lock:441`)                                                        | `dreamina`                                                         |
| GitHub repository                   | `stefanionescu/comfyui-fal`                                                       | `stefanionescu/comfyui-dreamina` (the local `origin`; its existence was not checked) |
| Registry display name, menu root    | `fal` (`F/pyproject.toml:158`, `F/src/config/namespace.py:9`)                     | `Dreamina`                                                         |
| Node ID prefix `NODE_PREFIX`        | `Fal` (`F/src/config/namespace.py:4`)                                             | `Dreamina`; node IDs such as `DreaminaVideoGenerate`               |
| Menus                               | `fal/Image`, `fal/Video`, `fal/Audio`, `fal/Text`, `fal/3D` (`F/src/config/namespace.py:10-14`) | `Dreamina/Image`, `Dreamina/Video`, `Dreamina/Audio` |
| Socket types                        | `FAL_FILES`, `FAL_OPTIONS` (`F/src/config/namespace.py:18-21`)                    | `DREAMINA_REFERENCES`                                              |
| Help pages                          | `web/docs/Fal<Node>.md`                                                           | `web/docs/Dreamina<Class>.md`                                      |
| Model: Info node ID                 | `FalModelInfo` (`F/quality/config/naming/policy.json:130`)                         | `DreaminaModelInfo`                                                |
| Runtime package for the vendor      | `src/fal/`                                                                        | `src/dreamina/`                                                    |
| Vendor config module                | `src/config/fal.py`                                                               | `src/config/dreamina.py`                                           |
| Error type                          | `FalError`                                                                        | `DreaminaError`                                                    |
| Browser extension name              | `'fal'` (`F/web/scripts/extension.ts:8`)                                          | `'dreamina'`                                                       |
| Settings command and menu           | `fal.OpenSettings` (`F/web/scripts/extension.ts:21`); **Extensions → fal → fal Settings** | `dreamina.OpenSettings`; **Extensions → Dreamina → Dreamina Settings** |
| Local routes                        | `/fal/v1/status`, `/settings`, `/credential` (`F/src/config/security.py:4-7`)     | `/dreamina/v1/status`, `/settings`, `/session`, `/cli`             |
| Write-request header                | `X-Fal-Comfy` (`F/src/config/security.py:29`)                                     | `X-Dreamina-Comfy`                                                 |
| CSS class prefix                    | `fal-ai-` (`c1dd344:web/styles/interface.css`)                                    | `dreamina-`                                                        |
| API key variable                    | `FAL_KEY` (`F/src/config/storage.py:6`)                                           | None: no API key exists                                            |
| State folder override variable      | `FAL_COMFY_STATE_DIRECTORY` (`F/src/config/storage.py:7`)                         | `DREAMINA_COMFY_STATE_DIRECTORY`                                   |
| State folder names                  | `FalComfyUI`, `fal-comfy` (`F/src/config/storage.py:11-14`)                       | `DreaminaComfyUI`, `dreamina-comfy`                                |
| Temporary file prefix               | `.fal-` (`F/src/config/storage.py:20`)                                            | `.dreamina-`                                                       |
| Secret rule IDs                     | `fal-api-key`, `fal-api-key-assignment`, `fal-secrets-hf-token-literal`, `fal-api-key-literal`, `fal-api-key-assignment-literal` | `dreamina-secrets-hf-token-literal` only |
| Semgrep rule ID prefix              | `fal-`                                                                            | `dreamina-`                                                        |
| CodeQL frontend configuration name  | `fal JavaScript and TypeScript`                                                   | `Dreamina JavaScript and TypeScript`                               |
| Temporary folders of the checks     | `comfyui-fal-types-`, `-links-`, `-secret-scan-`, `-schema-`                      | `comfyui-dreamina-types-`, `comfyui-dreamina-links-`, `comfyui-dreamina-secret-scan-`, `comfyui-dreamina-schema-` |
| Link alias                          | `[['web/', 'extensions/fal-ai']]`                                                 | `[['web/', 'extensions/dreamina']]`                                |
| Ruff checkout folder name           | `comfyui-fal` (`F/pyproject.toml:112`)                                            | `comfyui-dreamina`                                                 |
| Save prefixes in examples           | `image/fal/…`, `video/fal/…`, `audio/fal/…`, `text/fal/…`, `3d/fal/…`             | `image/dreamina/…`, `video/dreamina/…`, `audio/dreamina/…`         |
| First step of **Start Here**        | `1. Set your key in **ComfyUI menu → Extensions → fal → fal Settings**.` (`F/scripts/workflows/descriptions/notes.py:3`) | `1. Sign in to Dreamina in **ComfyUI menu → Extensions → Dreamina → Dreamina Settings**.` |
| Menu check message                  | `Put {node_id} in a fal menu.` (`F/scripts/nodes/check.py:86`)                     | `Put {node_id} in a Dreamina menu.`                                |
| Workflow UUID namespace             | `72ee9f58-7bbd-418b-af1f-7f48a5f198bf` (`F/scripts/workflows/page/graph.py:15`)   | `05f62da6-1302-4067-b6d8-e83cf4a52f83`                             |
| Registry icon                       | `…/comfyui-fal/main/docs/images/brand/logo.png` (`F/pyproject.toml:159`)          | `https://raw.githubusercontent.com/stefanionescu/comfyui-dreamina/main/docs/images/brand/logo.png` |
| Commit scopes                       | `nodes`, `frontend`, `workflows`, `docs`, `hooks`, `quality`, `root`, `deps`      | The same; they name no project                                     |

The new namespace is a version 4 UUID (RFC 4122 variant). It differs from
F's, B's (`9f1fd800-824d-4961-b2dd-4595d8c1ad6a`,
`B/scripts/workflows/page/graph.py:15`), and O's
(`6f1c0c7e-3b2a-4f7e-9d3a-2f0b4e6a8c10`,
`c076f37:scripts/workflows/page/graph.py:15`), so no Dreamina workflow,
subgraph, or blueprint ID can equal one of theirs.

## 3. What F holds

F tracks 463 files at `cef8b6e`; its first commit held 335.

| Area                  | Files | For Dreamina                                                                                           |
| --------------------- | ----: | ------------------------------------------------------------------------------------------------------ |
| `quality/`            |   220 | Copy; re-value 18 files ([section 6](#6-quality-every-fal-value-and-its-dreamina-value))                |
| `.mise/tasks/`        |    35 | Copy unchanged                                                                                         |
| `.githooks/`          |     3 | Copy unchanged                                                                                         |
| `rules/`              |     8 | Copy unchanged (protected)                                                                             |
| `scripts/`            |    29 | Copy 20 (the engine and the checks); write `texts.py` and `notes.py`; leave out F's seven family and node description modules |
| Root files            |    23 | Copy 20 ([section 4](#4-root-files)); write `README.md`, `ADVANCED.md`, and `requirements.txt` new     |
| `src/`, `web/`, `docs/images/`, `example_workflows/`, `subgraphs/` |   145 | fal runtime (74), browser code and help pages (23), artwork (10), and generated files (38); not copied |

Executable files (mode 755): the 3 hooks, the 35 task files, and the scanner
entry points under `quality/security/` and
`quality/repository/licenses/check.sh`. `git archive` keeps both modes and
leaves out the untracked `.venv/`, `node_modules/`, `.artifacts/`,
`.ruff_cache/`, `__pycache__/`, and `.import_linter_cache/`.

## 4. Root files

| File                       | fal value (where)                                                                                             | Dreamina value                                                                                       |
| -------------------------- | ------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| `__init__.py`              | `"""Load the fal nodes and their local routes through ComfyUI's extension entry point."""` (`F/__init__.py:1`) | `"""Load the Dreamina nodes and their local routes through ComfyUI's extension entry point."""`        |
| `pyproject.toml`           | [4.1](#41-pyprojecttoml)                                                                                      | [4.1](#41-pyprojecttoml)                                                                             |
| `package.json`             | `"name": "comfyui-fal"` (`:2`); `"dependencies": { "valibot": "1.5.0" }` (`:6-8`), added back in F's Frontend milestone (F row 233) | `"name": "comfyui-dreamina"`; `valibot` removed until the settings code imports it, then added back, as in F |
| `bun.lock`                 | `"name": "comfyui-fal",` (`:6`); the braces override at its full commit hash (F row 227)                       | `"name": "comfyui-dreamina",` by hand; the full braces hash kept after every `bun add` or `bun remove` |
| `uv.lock`                  | root `name = "fal-ai"` (`:441`)                                                                                | `dreamina`, written by `uv lock`                                                                     |
| `requirements.txt`         | `# Generated from pyproject.toml by mise run repo:deps:export.` and `pydantic>=2.10,<3`                       | The same, regenerated by `repo:deps:export`                                                          |
| `.mise.local.toml`         | Untracked: `COMFYUI_PATH` and `COMFYUI_PYTHON` (`F/.mise.local.toml:1-3`)                                     | The same two values: `/Users/dr_stone/ComfyUI-Installs/ComfyUI/ComfyUI` and `/Users/dr_stone/ComfyUI-Installs/ComfyUI/ComfyUI/.venv/bin/python` |
| `.gitignore`               | `/plans/` (`:2`), caches, `.artifacts/`, `node.zip`, `.env`, `.env.*`, `.mise.local.toml`                     | Unchanged                                                                                            |
| `.comfyignore`             | Keeps every development file out of the Registry archive; `/plans/` among them                                | Unchanged                                                                                            |
| `.markdownlint-cli2.yaml`  | Ignores `plans/**` (`:14`)                                                                                    | Unchanged. The entry keeps the skill mirror in `plans/research/docs/dreamina-canvas-cli/` out of the lint |
| `.typos.toml`              | Words `certifi`; identifiers `python_embeded`, `IIFEs` (`:10-17`)                                             | Unchanged; no Dreamina word is needed (finding 4)                                                    |
| The other root files       | `mise.toml`, `bunfig.toml`, `tsconfig.json`, `pyrightconfig.json`, `.prettierrc.json`, `.prettierignore`, `.stylelintrc.json`, `.gitattributes`, `AGENTS.md`, `CLAUDE.md`, `LICENSE.md` name no project | Unchanged                                                          |

### 4.1 pyproject.toml

| Key (F line)                                          | fal value                                                                                       | Dreamina value                                                                                                                      |
| ----------------------------------------------------- | ----------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| `[project] name` (`:2`)                               | `"fal-ai"`                                                                                      | `"dreamina"`. It is the Registry ID and must equal `PROJECT_PACKAGE_NAME`                                                           |
| `version` (`:3`)                                      | `"0.1.0"`                                                                                       | `"0.1.0"`                                                                                                                           |
| `description` (`:4`)                                  | `"Use any fal model in ComfyUI with your own API key: images, video, audio, text, and 3D models."` (94 characters; the line is 110) | `"Use Dreamina's image, video, and audio models in ComfyUI with your own Dreamina account."` (88 characters; the line is 104, so `pyproject-fmt` keeps a plain string) |
| `readme` to `dependencies` (`:5-12`)                  | `README.md`, `MIT`, `LICENSE.md`, Stefan Ionescu, `>=3.12`, `pydantic>=2.10,<3`                  | Unchanged. No CLI wrapper or other package is declared                                                                             |
| `[dependency-groups] dev` (`:14-35`)                  | Host libraries and check tools                                                                  | Unchanged                                                                                                                           |
| `lint.pep8-naming.extend-ignore-names` (`:111-112`)   | `[ "comfyui-fal" ]`, with the comment "ComfyUI loads the repository as a package even when its folder name has hyphens." | `[ "comfyui-dreamina" ]`, comment kept: it names the local checkout folder, not the install folder              |
| `[tool.interrogate]` (`:121-125`)                     | No `ignore-overloaded-functions`                                                                | Unchanged                                                                                                                           |
| `per_rule_ignores.DEP003` (`:142-143`)                | `[ "yarl" ]` with its comment, added for F's signed output downloads                           | Not copied: Dreamina's downloads go through the CLI, and the installer download uses a fixed address                               |
| `[tool.comfy]` (`:157-160`)                           | `DisplayName = "fal"`, `Icon = "…/comfyui-fal/…/logo.png"`, `requires-comfyui = ">=0.37.2"`     | `DisplayName = "Dreamina"` and `requires-comfyui = ">=0.37.2"` at Tooling; the `Icon` line arrives with the logo ([../19-brand-assets.md](../19-brand-assets.md)); `PublisherId` at release ([../20-release.md](../20-release.md#one-time-setup)) |
| Contract "The packages stack in one order" (`:185`)   | `"src.fal \| src.settings"`                                                                      | `"src.dreamina \| src.settings"`                                                                                                     |
| Contract "Only the host packages import ComfyUI's modules" (`:198`) | `"src.fal"` in `source_modules`                                                     | `"src.dreamina"`                                                                                                                    |
| Contract "Records must not import operations" (`:222`) | `"src.fal"` in `forbidden_modules`                                                             | `"src.dreamina"`                                                                                                                    |
| Contract "Config must not import runtime code or tooling" (`:231`) | `"src.fal"` in `forbidden_modules`                                                  | `"src.dreamina"`                                                                                                                    |

import-linter refuses a contract that names a module that does not exist, so
the skeleton creates all seven packages, `src/dreamina/` among them.

## 5. Files copied unchanged

- `rules/` (8 files), `AGENTS.md`, and `CLAUDE.md`. F's equal B's and O's;
  they are protected, and only the owner changes them.
- `.mise/tasks/` (35 files: 7 `comfy:*`, 28 `repo:*`) and `.githooks/`
  (3 files). No task or hook names fal: the leftover-name search of
  [12. Procedure](#12-procedure), run on F's tree, prints no line from them.
- In `quality/`: `terms.json` (101 banned terms), the verbs in
  `functions.json`, `commitlint.json`, `scopes.js`, `paths.py`,
  `folders.py`, `integrity.py`, `quality/config/python/rules.py`,
  `quality/config/shell.py`, the ESLint, knip, and madge settings (they name
  `web/scripts/extension.ts`, `text.ts`, `http.ts`, and `host.d.ts`,
  `F/quality/config/eslint/index.js:147`,
  `F/quality/config/imports/knip.json:5-6`,
  `F/quality/config/imports/madge.cjs:7-8`, which keep their names in
  [../04-architecture.md](../04-architecture.md#webscripts)), the license
  policies, `semgrep/packs.json` with `checksums.txt`, `hooks.yml`, the
  gitleaks `baseline.json` (`[]`) and `reasons.json` (`{}`), and the CodeQL
  Python, Bearer, and OSV settings.
- In `scripts/`: `__init__.py`, `paths.py`, `types.py`, `dependencies.py`,
  `frontend.py`, `nodes/__init__.py`, `nodes/host.py`, `workflows/__init__.py`,
  every file in `workflows/page/` except `graph.py`, and
  `workflows/descriptions/__init__.py`.

`scripts/nodes/host.py` lists the 14 host nodes F's examples place
(`F/scripts/nodes/host.py:9-22`), and `scripts/workflows/page/config.py`
holds their sizes measured on frontend 1.52.7 (`DOM_SIZES`,
`F/scripts/workflows/page/config.py:62-72`). Every member exists in
ComfyUI 0.37.2, so the node export runs with the copied list until
[../17-scripts-and-workflows.md](../17-scripts-and-workflows.md) sets the
list to the nodes Dreamina's examples place.

## 6. quality/: every fal value and its Dreamina value

| File:line (F)                                                 | fal value                                                                                         | Dreamina value at Tooling                                                                  |
| ------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| `quality/package.json:2`                                      | `"comfyui-fal-quality"`                                                                           | `"comfyui-dreamina-quality"`                                                               |
| `quality/config/repository/dependencies.py:5`                 | `PROJECT_PACKAGE_NAME = "fal-ai"`                                                                 | `PROJECT_PACKAGE_NAME = "dreamina"`                                                        |
| `quality/config/repository/links.js:1`                        | `[['web/', 'extensions/fal-ai']]`                                                                 | `[['web/', 'extensions/dreamina']]`                                                        |
| `quality/config/repository/functions.json:35-56`              | Four `allowlist` entries; three name F's runtime                                                  | Only the `__init__.py` entry ([8.3](#83-function-policy-functionsjson-and-functionspy))     |
| `quality/config/repository/functions.py:6-7`                  | A comment naming EndpointNode; a three-entry `HOST_NODE_BASES`                                    | F's tooling-time comment and two-entry value ([8.3](#83-function-policy-functionsjson-and-functionspy)) |
| `quality/config/repository/directories.js:3`                  | `SINGLE_FILE_FOLDER_PATTERNS = [];`                                                               | `SINGLE_FILE_FOLDER_PATTERNS = ['web/scripts/*.ts'];` (`c1dd344:…:3`)                      |
| `quality/config/naming/policy.json:130`                       | The `ModelInfo` reason names `FalModelInfo`                                                       | The reason names `DreaminaModelInfo` ([8.1](#81-naming-policy-policyjson))                 |
| `quality/config/naming/javascript.json:397`                   | `["credential_limit", "setting_ranges", "mutation_allowed"]`                                      | `["setting_ranges", "mutation_allowed"]`                                                   |
| `quality/config/naming/javascript.json:411`                   | `"X-Fal-Comfy"`, `["case"]`                                                                       | `"X-Dreamina-Comfy"`, `["case"]`                                                           |
| `quality/config/naming/javascript.json:422-428`               | The `api_key` rule for `web/scripts/settings/dialog.ts`                                           | Deleted                                                                                    |
| `quality/config/security/gitleaks/config.toml:1-16`           | Title and the rules `fal-api-key` (key shape) and `fal-api-key-assignment` (`FAL_KEY`)            | Title and gitleaks' default rules only ([section 7](#7-secret-rules))                      |
| `quality/config/security/semgrep/secrets.yml:1-19`            | `fal-secrets-hf-token-literal`, `fal-api-key-literal`, `fal-api-key-assignment-literal`           | `dreamina-secrets-hf-token-literal` only ([section 7](#7-secret-rules))                    |
| `quality/config/security/semgrep/python.yml:2,32,48,54,62,70` | `fal-` IDs; `include: ['/src/**', '/__init__.py']` at `:7` and `:37`                              | `dreamina-` IDs; the includes unchanged                                                    |
| `quality/config/security/semgrep/frontend.yml:2,15,30,44,62`  | `fal-` IDs                                                                                        | `dreamina-` IDs                                                                            |
| `quality/config/security/semgrep/markers.yml:1-29`            | Two rules: `fal-python-no-obsolete-markers` and `fal-python-no-deprecated-marker`, the second excluding `/src/types/models.py` (F row 232) | One rule, `dreamina-python-no-obsolete-markers`, with all five words, as `c1dd344:quality/config/security/semgrep/markers.yml:1-13` |
| `quality/config/security/codeql/frontend/scan.yml:1`          | `name: fal JavaScript and TypeScript`                                                             | `name: Dreamina JavaScript and TypeScript`                                                 |
| `quality/python/typecheck.py:41`                              | `prefix="comfyui-fal-types-"`                                                                     | `prefix="comfyui-dreamina-types-"`                                                         |
| `quality/repository/links.mjs:63`                             | `'comfyui-fal-links-'`                                                                            | `'comfyui-dreamina-links-'`                                                                |
| `quality/security/worktree.py:31`                             | `prefix="comfyui-fal-secret-scan-"`                                                               | `prefix="comfyui-dreamina-secret-scan-"`                                                   |

The Semgrep IDs after the edit:

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
`ensurepip` commands (`F/quality/config/security/semgrep/python.yml:8-47`),
so the CLI calls and the installer run that Dreamina's code makes with
`asyncio.create_subprocess_exec` do not match them. No pinned Semgrep pack
has a rule on `asyncio.create_subprocess_exec` outside its AWS Lambda rules,
which need a Lambda `event` source (read from `F/.artifacts/security/semgrep/rules/`
on 2026-10-16).

`markers.yml` refuses `legacy`, `deprecated`, `workaround`, backward
compatibility, and `compatibility` in Python files. The CLI's own texts use "legacy"
("follow the legacy `upgradeUrl` guidance",
`docs/dreamina-canvas-cli/references/authentication.md:56`), so no comment or
docstring quotes them. `model list` carries no model status word
([cli.md](cli.md#model-discovery)), so no split like F's is expected.

## 7. Secret rules

There is no Dreamina API key to find. The CLI keeps the sign-in in the OS
credential store, bound to the device
([cli.md](cli.md#sign-in)), and the pack keeps no token
([owner-rules.md](owner-rules.md#rules-added-for-dreamina)). Both of F's
gitleaks rules and both of F's Semgrep key rules describe fal's key and its
`FAL_KEY` variable, so none of them carries over.

`quality/config/security/gitleaks/config.toml` for Dreamina, the whole file:

```toml
title = "Dreamina node secret rules"

[extend]
useDefault = true
```

gitleaks' default rules still run on every staged file, the worktree, the
history, and the release archive. No check in `quality/` requires a custom
rule: `quality/repository/integrity/gitleaks.py` reads only `baseline.json`
and `reasons.json`.

`quality/config/security/semgrep/secrets.yml` for Dreamina, the whole file:

```yaml
rules:
    - id: dreamina-secrets-hf-token-literal
      message: Do not commit HuggingFace token literals.
      severity: ERROR
      languages:
          - generic
      pattern-regex: 'hf_[A-Za-z0-9]{20,}'
```

What remains is F's HuggingFace rule (`F/quality/config/security/semgrep/secrets.yml:2-7`)
under the Dreamina prefix. The pinned `secrets` pack (52 rules) still runs
beside it.

## 8. Naming and function policies

### 8.1 Naming policy: policy.json

`F/quality/config/naming/policy.json` `name_rules` holds ten rules:

| Lines     | Rule                                                                                                      | For Dreamina |
| --------- | --------------------------------------------------------------------------------------------------------- | ------------ |
| `35-41`   | `.githooks` and `.mise` folder names excluded                                                             | Keep         |
| `42-59`   | AST visitor methods excluded                                                                              | Keep         |
| `60-69`   | Two CodeQL variables in `codeql/python/scan.sh` excluded                                                  | Keep         |
| `70-83`   | The name `_` excluded                                                                                     | Keep         |
| `84-96`   | Leading underscores are a structural prefix                                                               | Keep         |
| `97-101`  | `i`, `j`, `k`, `x`, `y` excluded                                                                          | Keep         |
| `102-108` | `__init__`, `__main__` file names excluded                                                                | Keep         |
| `109-115` | `generic_visit` in the Python extractor excluded                                                          | Keep         |
| `116-123` | `on_load` in `__init__.py` may hold `load` ("ComfyUI calls this extension hook by name.")                 | Keep         |
| `124-131` | Class `ModelInfo` in `^src/nodes/model\.py$` may hold `info`; the reason names `FalModelInfo`             | Keep, with the reason "Other extensions call Model: Info by its node ID, DreaminaModelInfo, which ComfyUI builds from this class name." |

F has no other vendor-name exception, so nothing else is dropped. F added
the `ModelInfo` rule with its node (F row 245); Dreamina keeps it from the
first commit because the owner authorized it for F and
[../01-decisions.md](../01-decisions.md#banned-words-that-shape-names) keeps
it. A rule for a path that does not exist yet fails no check: B's first
commit held O's `ModelInfo` rule before the file existed (`F/plans/research/tooling.md:397-401`).

### 8.2 JavaScript naming policy: javascript.json

The five web rules of `F/quality/config/naming/javascript.json`:

| Lines     | File                              | Names                                                     | Allowed                 | For Dreamina                                               |
| --------- | --------------------------------- | --------------------------------------------------------- | ----------------------- | ---------------------------------------------------------- |
| `394-400` | `web/scripts/settings/schema.ts`  | `credential_limit`, `setting_ranges`, `mutation_allowed`  | snake case (wire names) | `setting_ranges`, `mutation_allowed`; `credential_limit` is F's key length limit (`F/src/settings/store.py:99`) and has no Dreamina counterpart |
| `401-407` | `web/scripts/settings/api.ts`     | `Content-Type`                                            | case                    | Keep                                                       |
| `408-414` | `web/scripts/settings/api.ts`     | `X-Fal-Comfy`                                             | case                    | `X-Dreamina-Comfy`, `["case"]`: it splits into `x`, `dreamina`, and `comfy`, none banned |
| `415-421` | `web/scripts/settings/dialog.ts`  | `once`                                                    | banned-term             | Keep                                                       |
| `422-428` | `web/scripts/settings/dialog.ts`  | `api_key`                                                 | case                    | Delete: F's key route field (`F/src/settings/routes.py:43`); Dreamina has no key route |

[../16-frontend.md](../16-frontend.md) adds any snake case wire name of the
account and CLI status reply to the `settings/schema.ts` rule in the change
that reads it.

### 8.3 Function policy: functions.json and functions.py

`F/quality/config/repository/functions.json` `allowlist` (`:35-56`):

| Lines   | Path and names                                                                    | Reason in F                                                         | At Dreamina's Tooling |
| ------- | --------------------------------------------------------------------------------- | ------------------------------------------------------------------- | --------------------- |
| `36-40` | `__init__.py`: `comfy_entrypoint`, `Extension.on_load`, `Extension.get_node_list` | "ComfyUI calls these extension hooks itself."                       | Keep: the only entry  |
| `41-45` | `src/types/credentials.py`: `Credential.reveal`                                   | "Revealing the key is an explicit call at the fal boundary, …"      | Never: no credential  |
| `46-50` | `src/settings/routes.py`: `ConfigurationRoutes.read_status`                       | "aiohttp calls this route handler itself."                          | Only in the same shape: Dreamina's status route moves to `AccountRoutes` in `src/comfy/account.py` ([../04-architecture.md](../04-architecture.md#srcsettings)) |
| `51-55` | `src/fal/queue/operation.py`: `QueueOperation.validate`, `CollectOperation.validate` | "The run wrapper calls it through the Operation protocol."       | Only in the same shape, at `src/dreamina/generations/operation.py` and `src/dreamina/upscale.py` |

`repo:lint:policy` refuses an entry whose file or function does not exist,
so the first commit holds only the `__init__.py` entry, exactly as
`c1dd344:quality/config/repository/functions.json:35-41`.

`HOST_NODE_BASES` lists the classes whose `define_schema`, `execute`,
`fingerprint_inputs`, and `validate_inputs` ComfyUI calls itself. The policy
matches class bases by name (`F/quality/repository/functions/python.py:272-277`).

| State             | Lines 6 and 7 of `quality/config/repository/functions.py`                                                                     |
| ----------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| F at `cef8b6e`    | `# The paid nodes reach ComfyNode through PaidNode, and the kind nodes through EndpointNode.` and `HOST_NODE_BASES = ("comfy_api.latest.io.ComfyNode", "src.nodes.base.PaidNode", "src.nodes.endpoint.EndpointNode")` |
| F at `c1dd344`    | `# The paid nodes reach ComfyNode through the extension's shared base class.` and `HOST_NODE_BASES = ("comfy_api.latest.io.ComfyNode", "src.nodes.base.PaidNode")` |
| Dreamina at Tooling | F's `c1dd344` lines, unchanged                                                                                              |
| Dreamina from [../08-runs.md](../08-runs.md) | `# The paid nodes reach ComfyNode through PaidNode, and the kind nodes through GenerateNode.` and `HOST_NODE_BASES = ("comfy_api.latest.io.ComfyNode", "src.nodes.base.PaidNode", "src.nodes.generate.GenerateNode")`, in the change that fills `GenerateNode`. The tuple line keeps F's length, 113 characters |

The policy refuses a function in `src/`, `scripts/`, or `__init__.py` whose
first word, after leading underscores, is not one of these verbs or the
predicates `is` and `has` (`F/quality/config/repository/functions.json:5-33`):

```text
read, save, send, parse, build, create, choose, list, find, plan, rank, validate, describe,
format, get, set, reset, decode, encode, sanitize, wait, register, delete, download, measure, place
```

The CLI calls in [../04-architecture.md](../04-architecture.md#srcdreamina)
use listed verbs, so none needs a new verb or a naming exception:

| Name in 04                          | Verb       | Module                       | Instead of                    |
| ----------------------------------- | ---------- | ---------------------------- | ----------------------------- |
| `send_command`                      | `send`     | `src/dreamina/cli.py`        | `run` (not a listed verb)     |
| `validate_cli`                      | `validate` | `src/dreamina/contract.py`   | `check`                       |
| `download_installer`, `save_cli`    | `download`, `save` | `src/dreamina/installer.py` | `install`              |
| `create_sign_in`, `delete_sign_in`  | `create`, `delete` | `src/dreamina/account.py` | `start`, `sign`        |
| `plan_references`, `format_prompt`  | `plan`, `format` | `src/dreamina/references.py` | `order`, `rewrite`      |
| `send_media`                        | `send`     | `src/dreamina/uploads.py`    | `upload`                      |
| `find_canvas`, `create_canvas`      | `find`, `create` | `src/dreamina/canvas.py` | `ensure`, which is also a banned term in `terms.json` |

A new verb would need both `functions.json` and the protected
`rules/NAMING.md`, so it would need the owner. F's plans used the listed
verbs the same way, such as `send` for an upload and `wait` for a queue wait
(`F/plans/03-repository-setup.md:1067-1070`).

## 9. Banned words the Dreamina CLI hits

A name is split into words at case and separator boundaries, and no word may
be one of the 101 terms in `quality/config/naming/terms.json`. A CLI field
read as a string key passes; a Python attribute, parameter, or constant with
the same name fails. The CLI's fields come from [cli.md](cli.md).

| CLI name                                   | Banned word  | Where the CLI uses it                                               | Local name                                                       |
| ------------------------------------------ | ------------ | ------------------------------------------------------------------- | ---------------------------------------------------------------- |
| `data` (the envelope), `partialData`       | `data`       | Every success reply; the exit 10 failure ([cli.md](cli.md#the-json-envelope)) | `payload` and `partial`, each with `Field(alias=…)`     |
| `serviceCode`                              | `service`    | `operation wait` `resources[]` and `submissionError` ([cli.md](cli.md#operations-and-recovery)) | `status_code`, with an alias                 |
| `subjectBindings`                          | `bind`       | A saved node's reference slots ([../01-decisions.md](../01-decisions.md#banned-words-that-shape-names)) | `subjects`, with an alias                  |
| `--resolution`, `vipResolutions`           | `resolution` | Video, image, and upscale flags; `model list` membership fields ([cli.md](cli.md#model-discovery)) | A key inside `arguments` only; `vipResolutions` through an alias, under a name without the banned word |
| "model catalog"                            | `catalog`    | The skill's prose                                                   | `models`, `listing`, or `model_list`                             |
| Model: Info                                | `info`       | The node name                                                       | `ModelInfo` with its exception; helpers and messages say "report" (F row 239) |
| "fetch" a download                         | `fetch`      | Prose                                                               | `download_…`                                                     |
| "smart upscale" (`pro`)                    | `smart`      | The upscale's `--mode pro` ([cli.md](cli.md#image-upscale))         | Help text only                                                   |
| "latest draft", "latest specification"     | `latest`     | The skill's prose ([cli.md](cli.md#credits))                        | Never part of a name                                             |
| "transient errors"                         | `transient`  | The skill's recovery prose ([cli.md](cli.md#operations-and-recovery)) | `retryable`, the CLI's field                                   |

Fields that pass: `submitId`, `projectId`, `nodeId`, `resourceId`,
`operationRef`, `requiredAction`, `retryable`, `minimumCreditCeiling`,
`creditsAmount`, `localStorage`, `requireAnyOfTypes`,
`mutuallyExclusiveTypes`, `vipRequired`, `isVip`, `vipLevel`, `userCode`,
`verificationUri`, `expiresAt`, `voiceName`, `hasMore`, `nextOffset`, and
`webUrl`. The Python keyword `class` becomes `failure_class`
([../04-architecture.md](../04-architecture.md#srctypes)).

## 10. scripts/: every fal value and its Dreamina value

| File:line (F)                                  | fal value                                                                                                     | Dreamina value                                                                                   |
| ---------------------------------------------- | ------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| `scripts/nodes/schema.py:31-34`                | The File: Add multi-typed widget test: a comment naming File: Add, `is_typed_widget`, `is_plain_widget`, and `is_widget` from both (F row 223) | B's one-line test, `B/scripts/nodes/schema.py:29`: no Dreamina node has a multi-typed widget input |
| `scripts/nodes/schema.py:104-105`              | "…so Request: Download lists no requests and the export is the same / on every machine."                     | "…so Generation: Download lists no generations and the export is / the same on every machine."  |
| `scripts/nodes/schema.py:108`                  | `prefix="comfyui-fal-schema-"`                                                                                | `prefix="comfyui-dreamina-schema-"`                                                              |
| `scripts/nodes/check.py:86`                    | `f"Put {node_id} in a fal menu."`                                                                             | `f"Put {node_id} in a Dreamina menu."`                                                           |
| `scripts/workflows/page/graph.py:15`           | `NAMESPACE = uuid.UUID("72ee9f58-7bbd-418b-af1f-7f48a5f198bf")`                                               | `NAMESPACE = uuid.UUID("05f62da6-1302-4067-b6d8-e83cf4a52f83")`                                  |
| `scripts/workflows/build.py:9`                 | `from src.config.namespace import MENUS`                                                                      | Deleted until the first family                                                                   |
| `scripts/workflows/build.py:16-17`, `:19-22`   | Six family imports: `MESH_WORKFLOWS`, `TEXT_WORKFLOWS`, `AUDIO_WORKFLOWS`, `IMAGE_WORKFLOWS`, `VIDEO_WORKFLOWS`, `VOICE_WORKFLOWS`; `:18` imports `measure` and `measure_note` | Deleted; `:18` stays                                    |
| `scripts/workflows/build.py:39-48`             | `FAMILIES` with six entries, then `WORKFLOWS`                                                                 | F's tooling-time form, `c1dd344:scripts/workflows/build.py:32-35`: `FAMILIES = cast("tuple[tuple[tuple[Workflow, ...], str], ...]", ())` with its two comments (F row 222) |
| `scripts/workflows/descriptions/texts.py`      | F's titles                                                                                                    | New: the three titles of `c1dd344:scripts/workflows/descriptions/texts.py`                       |
| `scripts/workflows/descriptions/notes.py`      | F's notes                                                                                                     | New: docstring only, as `c1dd344:scripts/workflows/descriptions/notes.py`                        |
| `scripts/workflows/descriptions/{audio,image,mesh,nodes,text,video,voices}.py` | F's examples and node IDs                                             | Not copied; [../17-scripts-and-workflows.md](../17-scripts-and-workflows.md) writes Dreamina's   |

The copied scripts import seven runtime names, which the skeleton supplies:
`MENUS` (`F/scripts/nodes/check.py:11`), `NODE_TYPES`, `PaidNode`,
`INPUT_NAMES`, `create_runtime`, and `ENVIRONMENT_VARIABLES`
(`F/scripts/nodes/schema.py:18-23`), and the root `__init__.py` imports
`register_routes` (`F/__init__.py:16`).

## 11. Release configuration

| Item                     | F                                                                                                                       | Dreamina                                                                                                                  |
| ------------------------ | ----------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| `[tool.comfy]`           | `DisplayName = "fal"`, `Icon` (the logo's raw GitHub address), `requires-comfyui = ">=0.37.2"`; no `PublisherId` (`F/pyproject.toml:157-160`) | `DisplayName = "Dreamina"`, `Icon` with the logo, `requires-comfyui = ">=0.37.2"`; no `PublisherId` until the owner publishes |
| At first publish         | `urls.Issues` and `urls.Repository` after `dependencies`; `PublisherId` in `[tool.comfy]` (`F/plans/20-release.md:84-114`) | The same with `stefanionescu/comfyui-dreamina`                                                                         |
| comfy-cli                | `"pipx:comfy-cli" = "1.20.0"` (`F/mise.toml:15`); the release tasks run through `mise run`                              | The same                                                                                                                  |
| Tasks                    | `comfy:release:package`, `comfy:release:publish`                                                                        | The same                                                                                                                  |
| Archive contents         | `__init__.py`, `src/`, `web/extension.js`, `web/extension.css`, `web/docs/`, `example_workflows/`, `subgraphs/`, `docs/images/`, `pyproject.toml`, `requirements.txt`, `README.md`, `ADVANCED.md`, `LICENSE.md` (`F/plans/20-release.md:300-306`) | The same list. No Dreamina binary or skill, which the repository never tracks; `.comfyignore` lists `/plans/`, which holds the skill mirror |
| The archive's secret scan | gitleaks with F's two key rules and the default rules                                                                  | gitleaks' default rules                                                                                                   |
| Registry ID check        | `https://api.comfy.org/nodes/fal-ai` answered 404 on 2026-10-15                                                          | `https://api.comfy.org/nodes/dreamina` answered 404 on 2026-10-16                                                         |
| Packs to search for clashes | The other fal packs on the Registry                                                                                  | Packs a Registry search for `dreamina`, `jimeng`, or `seedance` finds; on 2026-10-16, none named "dreamina", the Jimeng packs `ComfyUI-Jimeng-API` and `ComfyUI-WBLESS`, and 21 Seedance packs, none with a `Dreamina` prefix ([../01-decisions.md](../01-decisions.md#node-id-clashes)) |

## 12. Procedure

[../03-repository-setup.md](../03-repository-setup.md) holds the steps.
In short:

1. Copy F's tooling at `cef8b6e` with `git archive`.
2. Re-value the root files, `pyproject.toml`, and `package.json`
   ([section 4](#4-root-files)).
3. Create `.mise.local.toml`.
4. Re-value `quality/` ([section 6](#6-quality-every-fal-value-and-its-dreamina-value)),
   taking F's tooling-time value for each later-milestone value.
5. Re-value `scripts/` ([section 10](#10-scripts-every-fal-value-and-its-dreamina-value)).
6. Create the skeleton: seven runtime packages and the stubs the copied
   checks need.
7. Lock and install. If `repo:security:rules` refuses a downloaded pack,
   copy `F/.artifacts/security/semgrep/rules/` (finding 10).
8. Search the staged files for F's, B's, and O's names, then commit
   `build(quality): bring in the repository tooling`.

The leftover-name search, run on F's tree at `cef8b6e` over the files
Dreamina copies, printed exactly the 56 lines that steps 2 to 5 change and
nothing from `rules/`, `.mise/`, or `.githooks/`:

```sh
git grep -nIP '(?i:\bfal\b|fal-ai|comfyui-fal|byteplus|modelark|ark_api_key|hyper3d|hitem3d|openrouter|sk-or-v1)|\bFal[A-Z]|FAL_|X-Fal-|EndpointNode|Request: Download|File: Add|Request Options|api_key|credential_limit' -- . ':!uv.lock' ':!bun.lock' ':!plans/'
```

The case-insensitive group catches fal's, B's, and O's names in any case,
with word boundaries so `fallback` and `false` do not match. `\bFal[A-Z]`
(`FalError`, `FalModelInfo`), `FAL_`, and `X-Fal-` are case-sensitive for the
same reason. `EndpointNode`, F's node names, `api_key`, and
`credential_limit` catch F's runtime names. The pattern names no Dreamina
model family, so `Seedance`, `Seedream`, and `dreamina-seedance` never match.

## 13. Decisions for the owner

| Decision                                  | Options and what each changes                                                                                                                                                                         |
| ----------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `ModelInfo` naming rule at Tooling        | Kept from F's file (recommended, [8.1](#81-naming-policy-policyjson)), or added with Model: Info in [../15-node-model-info.md](../15-node-model-info.md), as F did                                     |
| A local Semgrep rule against `--yes`      | Not added: the tooling is copied with the smallest diff to F ([owner-rules.md](owner-rules.md#process-and-plans)). The code review of [../08-runs.md](../08-runs.md) holds the rule instead             |
| Registry publisher                        | `stefanionescu` existed on 2026-10-15 (`F/plans/20-release.md:47`); confirm it is the owner's before the first publish                                                                                |
