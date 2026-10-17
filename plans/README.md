# Build Plans

These plans describe everything needed to build the repository
`comfyui-dreamina`.

It is a ComfyUI node pack, published and installed as `dreamina` and called
**Dreamina** inside ComfyUI. It runs Dreamina's models on the person's own
Dreamina account and credits:

- images: generation, editing, and upscaling;
- video: text to video, first and last frames, and multimodal references;
- audio: speech with a voice, and dubbing that matches a picture or a voice
  sample.

It has one node per kind of output. As in the fal, BytePlus, and OpenRouter
packs:

- the person types a model name;
- the node takes the model's settings as JSON, under Dreamina's own flag
  names;
- before paying, it checks them against the person's live model list;
- it keeps no list of Dreamina's models.

It talks to Dreamina only through ByteDance's official **Dreamina Canvas
CLI**, which the person installs and signs in to from the pack's settings
dialog.

The pack's structure, logic, tooling, and documentation follow the fal pack
(`F=/Users/dr_stone/Documents/work/comfyui-fal`, commit `cef8b6e`). F itself
follows the BytePlus pack (`B=/Users/dr_stone/Documents/work/comfyui-byteplus`,
commit `472cf10`) and the OpenRouter pack
(`O=/Users/dr_stone/Documents/work/comfyui-openrouter`, commit `c076f37`).

Readers:

- the engineer or agent who builds the pack, step by step;
- the owner, who decides the open questions and approves every paid run.

Nothing in these plans has been implemented. They were written on 2026-10-16
from these sources:

- the installed Dreamina Canvas CLI 1.0.3: its `schema` and free calls,
  including the owner's live model and voice lists after sign-in (captured in
  `research/captures/`);
- its skill (mirrored in `research/docs/dreamina-canvas-cli/`, without the
  parts it marks confidential);
- Dreamina's site and terms;
- the code and plans of F, B, and O;
- ComfyUI 0.37.2 and its frontend 1.52.7.

## Contents

- [How to use these plans](#how-to-use-these-plans)
- [The plans](#the-plans)
- [What the research found](#what-the-research-found)
- [Build order](#build-order)
- [Before the first paid run](#before-the-first-paid-run)
- [Changes made while building](#changes-made-while-building)
- [Research sources](#research-sources)
- [Glossary](#glossary)

## How to use these plans

1. **Read the core plans first.** Read [01-decisions.md](01-decisions.md),
   [02-dreamina-contract.md](02-dreamina-contract.md), and
   [04-architecture.md](04-architecture.md) before any other plan. They fix
   the names, the CLI facts, and the file map every other plan uses. Then
   read [research/owner-rules.md](research/owner-rules.md): it lists every
   rule the owner set while building O, B, and F, and every plan follows it.
1. **Build in the [build order](#build-order).** Within a plan, do the steps
   in their numbered order; a step never depends on a later one.
1. **Follow the copied `rules/`** for every file: naming, Python, TypeScript,
   Bash, documentation, writing, and planning. When a plan and a rule
   disagree, the rule wins, and the plan is corrected in
   [Changes made while building](#changes-made-while-building).
1. **Copy before writing.** When a plan names an F file, port that file and
   apply the plan's edits instead of writing new code. F's code, not its
   plans, is the reference.
1. **Write no automated tests.** The rules forbid them. Run checks only when
   the owner asks. The Git hooks run their checks on every commit and push; a
   failing hook means a plan step was missed.
1. **Commit at each milestone** with a message in the commit rules:
   `type(scope): lowercase subject`. The scope is one of `nodes`, `frontend`,
   `workflows`, `docs`, `hooks`, `quality`, `root`, or `deps`.
1. **Make no paid run without the owner's approval,** and state its credits
   first ([21-test-runs.md](21-test-runs.md)).
1. **For an example workflow,
   [17-scripts-and-workflows.md](17-scripts-and-workflows.md) holds** the
   shipped prompts, settings, and save names. When it and a node plan differ,
   17 wins and the node plan is corrected.
1. **Never call Dreamina except through the installed CLI.** Never pass
   `--yes`, and never delete a node on the person's canvas
   ([research/terms.md](research/terms.md#3-how-the-pack-stays-inside-the-published-route)).

The plans are tracked in Git, at the owner's request (2026-10-17). Two
folders stay local: `research/docs/` (ByteDance's skill text) and
`research/captures/` (IDs from the owner's account). `.comfyignore` keeps all
of `plans/` out of the released package.

## The plans

| Plan                                                         | Builds or fixes                                                                                     |
| ------------------------------------------------------------ | --------------------------------------------------------------------------------------------------- |
| [01-decisions.md](01-decisions.md)                           | Every design decision: names, the nodes, the model check, modes, references, the CLI, sign-in, the canvas, credits, scope |
| [02-dreamina-contract.md](02-dreamina-contract.md)           | The CLI's calls, replies, exit codes, sign-in, models, runs, credits, waits, uploads, downloads, with the facts still to test |
| [03-repository-setup.md](03-repository-setup.md)             | Rules, quality tooling, mise tasks, hooks, and root configuration copied from F                     |
| [04-architecture.md](04-architecture.md)                     | The file tree, module inventory, import layers, run flows, and other packs' node IDs                |
| [05-foundation.md](05-foundation.md)                         | Constants, records, errors, storage, settings, the status, sign-in, and install routes, loading      |
| [06-model-check.md](06-model-check.md)                       | Reading the live model list, matching a typed name, choosing the mode, checking `arguments`          |
| [07-media.md](07-media.md)                                   | Encoding ComfyUI media, uploads, references and placeholders, downloads, decoding                   |
| [08-runs.md](08-runs.md)                                     | The CLI runner, the failure map, the version gate, the canvas, generation records, the run, the wait, the paid node base |
| [09-node-image.md](09-node-image.md)                         | Image: Generate                                                                                     |
| [10-node-video.md](10-node-video.md)                         | Video: Generate                                                                                     |
| [11-node-audio.md](11-node-audio.md)                         | Audio: Generate                                                                                     |
| [12-node-upscale.md](12-node-upscale.md)                     | Image: Upscale                                                                                      |
| [13-node-element.md](13-node-element.md)                     | Element: Add                                                                                        |
| [14-node-download.md](14-node-download.md)                   | Generation: Download                                                                                |
| [15-node-model-info.md](15-node-model-info.md)               | Model: Info                                                                                         |
| [16-frontend.md](16-frontend.md)                             | The Dreamina Settings dialog (CLI, account, request limits) and the bundle                          |
| [17-scripts-and-workflows.md](17-scripts-and-workflows.md)   | Build and check scripts, the example workflows, and how notes are written                           |
| [18-documentation.md](18-documentation.md)                   | README, advanced guide, node help pages                                                             |
| [19-brand-assets.md](19-brand-assets.md)                     | The palette, banner, mark and logo, badges, node map, and screenshots                               |
| [20-release.md](20-release.md)                               | Packaging and publishing to the Comfy Registry                                                      |
| [21-test-runs.md](21-test-runs.md)                           | Every free and paid live run: free reads and the price sweep, contract checks, each milestone's first runs, the video model sweep, every example once |
| [22-owner-setup.md](22-owner-setup.md)                       | The owner's Dreamina account: the CLI, sign-in, the plan gate, credits, the canvas                  |
| [23-live-shopping-provider.md](23-live-shopping-provider.md) | Adding Dreamina to `comfyui-live-shopping` as an optional provider, later                           |

## What the research found

The owner asked several questions. The short answers, with where the evidence
is:

| Question                                                             | Answer                                                                                                     |
| -------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| Can a ComfyUI pack use the owner's own Dreamina account and credits? | Yes, through the official Dreamina Canvas CLI. It signs the person in with a device code and runs generations on their credits ([02](02-dreamina-contract.md)). |
| Is there an API key or an HTTP API?                                  | No. The CLI is the only published route for international accounts. Its skill forbids undocumented endpoints and raw HTTP, and the binary refuses cookie sign-in ([research/terms.md](research/terms.md)). |
| Does the pack ship the CLI?                                          | No. There is no license to redistribute it, it is about 25 MB per platform, and the server refuses old clients. Dreamina Settings runs ByteDance's own installer ([01](01-decisions.md#the-cli-on-the-persons-computer)). |
| How does the person sign in?                                         | **Sign in** in Dreamina Settings shows a link and code. The person approves on dreamina.capcut.com. The credentials stay in the OS credential store, and the pack never sees them ([01](01-decisions.md#sign-in-and-privacy)). |
| Can the nodes take any model name, with no list in the pack?         | Yes. `model list` returns each model's modes, flags, allowed values, ranges, and reference limits live. The node checks the typed name and settings against it before paying ([01](01-decisions.md#checking-a-model-before-paying)). |
| How is spending controlled?                                          | Dreamina's own approval: each run carries `--credit-ceiling`. A quote above it stops the run with nothing charged and shows the price ([01](01-decisions.md#credits)). |
| What happens on a cancel?                                            | Dreamina has no cancel for a run it accepted. The run keeps going and is billed. **Generation: Download** collects it ([02](02-dreamina-contract.md#waiting-and-recovery)). |
| Which models can the owner use?                                      | Any model on the person's live list, typed by name; the pack holds no list. On 2026-10-16 the owner's Standard account listed 12 image models (Seedream 4.0 to 5.0 Pro, GPT Image 2 and 2.5, Gemini 3 Image Pro, and more), 5 Seedance video models, and 2 speech models, and no music model ([research/catalog.md](research/catalog.md)). The CLI page says Advanced only, but Standard worked. |
| What are Dreamina's colors?                                          | Its star mark runs from orange `#E57B21` through yellow and aqua `#60D5E6` to blue `#1964FF`. The pack's palette mixes it with BytePlus blue and OpenRouter indigo and yellow ([research/brand.md](research/brand.md)). |

## Build order

Each milestone ends with a commit. The Git hooks check help pages, example
workflows, README links, and the browser bundle, so each node milestone adds
its help page, its examples, and its README rows together with the node.

1. **Tooling.**
   - [03-repository-setup.md](03-repository-setup.md), all steps, with the
     steps it names in 16, 17, and 18 for the files the hooks need.
   - [19-brand-assets.md](19-brand-assets.md#step-1-badges-and-banner)
     Step 1: the badges and banner the first README links.

   Commit: `build(quality): bring in the repository tooling`.
1. **Foundation.** [05-foundation.md](05-foundation.md) Part A (Steps 1 to
   14), then [08-runs.md](08-runs.md) Part A (the CLI constants, the reply
   records, the runner, the failure map, the version gate), then
   [05-foundation.md](05-foundation.md) Part B (Steps 15 to 22: sign-in,
   install, status, and settings routes, and loading). The routes call the
   CLI, so its runner comes first. Free; no paid run. Commit:
   `feat(nodes): add the settings, sign-in routes and extension loading`.
1. **Frontend.** [16-frontend.md](16-frontend.md): the settings dialog with
   install, sign-in, and the request limits. Every example's
   **Start Here** note sends the person to this dialog. Commit:
   `feat(frontend): add the settings dialog`.
1. **Free reads and contract checks.**
   - With the owner signed in (through the dialog or with `dreamina-canvas
     auth login` in a terminal; both set the same CLI sign-in), run Part 0
     and Part 1 of
     [21-test-runs.md](21-test-runs.md), with the CLI outside ComfyUI.
   - Part 0 is free: the captures and the price sweep.
   - Part 1 needs the owner's approval of its credits.
   - Record every result in the changes table and in
     [02-dreamina-contract.md](02-dreamina-contract.md#results-of-the-contract-runs),
     and correct the plans it names before building further.

   No commit unless a plan's code changes.
1. **Model check.** [06-model-check.md](06-model-check.md): the live list,
   its cache, the match, the modes, and the arguments. Free; no paid run.
   Commit: `feat(nodes): add the live model check`.
1. **Media and runs.** [07-media.md](07-media.md) and
   [08-runs.md](08-runs.md) Part B, interleaved as 08's "When each part is
   built" lists: 07's constants, messages, placeholder pattern, and records
   first, then 08's queue constants and reply records that 07's uploads and
   downloads read, then the rest of 07, then the rest of 08. Commit:
   `feat(nodes): add uploads, runs and downloads`.
1. **Model: Info.** [15-node-model-info.md](15-node-model-info.md): the node
   class and its reads, committed unregistered, as F did. Its help page,
   README row, and registration arrive with the Audio milestone, which ships
   its example. The push hooks refuse a registered node no example places,
   and a help page for an unregistered node. Commit: `feat(nodes): add model
   info`.
1. **Image.** [09-node-image.md](09-node-image.md), with its examples, help
   page, and README rows; `mise run comfy:workflows:build`. Commit:
   `feat(nodes): add the image node`.
1. **Upscale.** [12-node-upscale.md](12-node-upscale.md), the same way. It
   comes after Image because image-03 upscales an image Image: Generate made.
   Commit: `feat(nodes): add the upscale node`.
1. **Audio.** [11-node-audio.md](11-node-audio.md), the same way, with
   Model: Info registered, its help page, its README row, and its example. It comes before Video because a
   video example voices its host. Commit: `feat(nodes): add the audio node`.
1. **Video and downloads.**
   [14-node-download.md](14-node-download.md), then
   [10-node-video.md](10-node-video.md), the same way. They ship together
   because Generation: Download's example collects a video run. Commit:
   `feat(nodes): add the video node and generation downloads`.
1. **Elements.** [13-node-element.md](13-node-element.md), the same way.
   Commit: `feat(nodes): add the element node`.
1. **Documentation and brand.** [19-brand-assets.md](19-brand-assets.md),
   then [18-documentation.md](18-documentation.md), the remaining steps.
   Commit: `docs(docs): complete the readme, the advanced guide and the images`.
1. **Video model sweep and example runs.** The video model sweep and "Run
   every example once" in [21-test-runs.md](21-test-runs.md), with the
   owner's approval. Each fix is its own commit.
1. **Release.** [20-release.md](20-release.md), when the owner decides to
   publish.
1. **Live-shopping.** [23-live-shopping-provider.md](23-live-shopping-provider.md),
   in the live-shopping repository, when the owner asks for it.

## Before the first paid run

- **Milestones 1 to 3 spend nothing.** Part 0 of milestone 4 spends nothing
  either: model lists, voices, uploads, Elements, and price checks with
  `--credit-ceiling 0` are free. Part 0 is done: the lists on 2026-10-16,
  the price sweep on 2026-10-17 ([research/catalog.md](research/catalog.md#prices)).
- **Every test runs at the lowest resolution and shortest duration** each
  model allows, upscales included.
- **From Part 1 of milestone 4, runs spend the owner's Dreamina credits.**
  Ask the owner before the first one and state its credits.
- **The owner's account** had about 1,300 credits on a discounted plan on
  2026-10-16. The owner pre-approved spending them on tests, with the most on
  video models.
- **Where the details are.** [21-test-runs.md](21-test-runs.md) holds every
  run with its call, what it confirms, and its credits. Part 0 fills in every
  credit figure, from Dreamina's own quotes.

| Stage                                       | What it confirms                                                                                     | Credits                         |
| ------------------------------------------- | ---------------------------------------------------------------------------------------------------- | ------------------------------- |
| Part 0: free reads and price sweep          | The live lists, voices, the plan gate, every model's price at its cheapest settings                  | 0                               |
| Part 1: contract checks (C-1 to C-17)       | Upload formats, downloads, the run reply, waits, recovery, placeholders, upscale, Elements, billing on failure | ≤ 60                  |
| Part 2: node first runs                     | One cheap run per node through ComfyUI; a cancel and Generation: Download; Model: Info                | ≤ 150                           |
| Part 3: video model sweep                   | Every video model on the account once, at its cheapest settings, then frames and multimodal modes     | ≤ 750                           |
| Part 4: every example once                  | Each example end to end, as shipped                                                                  | ≤ 250                           |
| Reserve                                     |                                                                                                      | ≥ 90                            |

If a run behaves differently from the contract plan, the CLI or Dreamina has
changed. Update [02-dreamina-contract.md](02-dreamina-contract.md) and the
step it names before building further, and record it in the table below.

## Changes made while building

Record here every change to a plan made during the build, with the plan
number and the reason, as F's, B's, and O's plans do.

| Plan | Change | Why |
| ---- | ------ | --- |
| 03 | `[tool.ruff] exclude` lists `plans`. | Ruff formats Python blocks inside the tracked Markdown plans, so the first commit's format check refused two plans. |
| 03 | `quality/repository/links.mjs` skips every prefix in `LINK_EXCLUDED_PREFIXES`, with `some((prefix) => relative.startsWith(prefix))`. F's `some(relative.startsWith.bind(relative))` passed each prefix's index as the start position, so only the first prefix worked, and the tracked `plans/` was link-checked. | Found by the first commit's hook. |
| 03 | `repo:security:rules` refused the pinned rule `python.boto3.security.hardcoded-token.hardcoded-token` (registry drift, as F row 220). F's local packs were copied and `shasum -a 256 -c` printed OK for all five; the hooks were set up by hand. No pin changed. | Upstream drift. |
| 01, 04, 05, 08, 16, 18, 19, 22 | The Dreamina Settings dialog has three parts: the CLI (Install or Update), the account (Sign in or Sign out), and the request limits. No canvas link, no Check again, no command to copy; the install commands are in the README. | Owner's instruction, 2026-10-17. |
| README, 03, research | The plans are tracked in Git; `plans/research/docs/` and `plans/research/captures/` stay ignored. | Owner's instruction, 2026-10-17. |
| 02, 21, catalog | Part 0 ran on 2026-10-17, free: the test canvas, four uploads, an imported image node, 45 price checks, and four upscale quotes. Results are in 02's results table and the catalog's Prices. | The owner allowed canvases and drafts to be created freely. |
| 01, 06, 09 to 12, 14, 17 to 19, 21, catalog | Video starting model switched from `seedance_2.0_fast` to `seedance_2.0_mini` (16 credits against 24 at 720p and 4 seconds). Starting `credit_ceiling`: image 10, video 20, audio 20, upscale 10. | Part 0's quotes and the catalog's rule for defaults. |
| 01, 19, research | The banner title is "Dreamina"; the mark is the redrawn star. | Owner's choice, 2026-10-17. |
| 11, 21, catalog | The one listed speech model the CLI cannot run by name is dropped from the plans; `seed_audio_v1` is the speech model. Every test runs at the lowest resolution and shortest duration; upscale tests use `normal` and `pro` 2K. | Owner's instruction: keep it simple and test at the lowest settings. |
| 08 | The exit 10 code for a ceiling below the quote is `cli.generation_credit_ceiling_too_low` (class `confirmation_required`), not only `cli.generation_confirmation_required`. The failure map reads exit 10 and `requiredAction` `confirm`, so both map to `CEILING_TOO_LOW`. | Part 0. |
| 12 | An import needs `--title`; the pack sends the node's display name. | Part 0: refused without it. |
| 03, 08 | `quality/config/repository/folders.py` `SINGLE_FILE_PACKAGE_ALLOWLIST` holds `src/storage` from Foundation until the Media and runs milestone, whose `canvas.py` joins `files.py`; that milestone removes the entry. | `python.single-file-package` refused `src/storage` with only `files.py`, and the canvas store arrives with its first reader. |
| 04, 05, 03, 08, 16 | F's `src/settings/routes.py` is not ported. Every route, the settings save among them, is in `SettingsRoutes` in `src/comfy/settings.py` (was `AccountRoutes` in `src/comfy/account.py`). | With one route left, a settings-only `register` had two statements, which `python.trivial-function` refuses. |
| 04, 05, 08, 12 | `reset_cli_validation` is gone: `validate_cli` keys a passed check by the binary's path and modification time, so an install is checked again. `is_current_version` takes `None` for a CLI not found. `save_cli` returns nothing. | `python.trivial-function` refused a one-statement reset and a two-statement version test. |
| 02, 04, 05 | The installer download follows at most three redirects and keeps the script only from a final HTTPS address under `.capcut.com` or `.capcutstatic.com` (`INSTALLER_DOMAINS`, `INSTALLER_REDIRECTS`). `INSTALLER_HOST` is gone and the addresses are literals. | Live, 2026-10-17: `install.sh` answers 301 to `/canvas-cli/install/install.sh`, then 302 to ByteDance's CDN, so "no redirect" refused the official installer. `repo:lint` refuses f-strings in `src/config/`. The Install route then ran the installer in 14 seconds. |
| 05, 08 | `CLI_TOO_OLD` is `CLI_OUTDATED`. `LocalStorage.reason` is not declared. `RUN_REFUSED` arrives in Part B with the run call. `REASON_PATTERNS["TOKEN"]` is `["IDENTIFIER"]`, and `INSTALL_SHELL_MISSING` names `{program}`, not `{shell}`. | `old` is a banned term; nothing reads the reason; a message arrives with its first reader. Bandit read the `TOKEN` key as a password (B105) and `format(shell=…)` as `shell=True` (B604). |
| 16 | The sign-in poll redraws only the CLI and account parts; `CliActions` has no `report`; the account part's line container is `lines`, and the file-local action and status types are not exported. | Redrawing the limits every 2 seconds would wipe values typed while a sign-in waits. `details` is a banned term, and knip refuses unused exported types. |
| 16, 21 | Frontend browser checks ran on 2026-10-17 in headless Chrome through Playwright: 22 of 22 passed (menu command, three parts and footer, no command or canvas link, "Dreamina CLI 1.0.3 is installed.", **Update** dismissed sends nothing, **Update** accepted reinstalls in about 14 seconds with the parts disabled, **Reload settings**, limits saved then unchanged then restored, one dialog at a time, focus). The sign-in flow ran against mocked status replies: code, link, one new tab, a read every 2 seconds, "Signed in." on approval, then no more reads. **Sign out** and a real approval wait for the owner, so the account stays signed in. | The owner is away; signing out would need their approval in Firefox to undo. |
| 04, 06, 07 | `describe_mode` and `_list_flags` are the properties `ModelMode.label` and `ModelMode.named_flags`; `ANY_KIND` holds "images, videos, or audio". | `python.trivial-function` refuses one-line functions; properties are exempt. |
| 07, 08, 04, 12 to 15 | Media and runs, as built: `CanvasStore` has `read` and `save` only, and `find_canvas` returns `None` for a canvas `canvas ls` no longer lists without deleting the record, since the next `create_canvas` replaces it. `GenerationRecord.label` replaces `_build_label` and `list_generation_labels`. A new `RunCall` record in `src/types/generations.py` holds the run call and writes its `arguments`. `ACCEPTED_PHASE` (`after_submit`) is a constant in `src/config/dreamina.py`. `wait_for_run` and `wait_for_thread` are private until 13, 14, or 15 calls `wait_for_run`. Downloads land in the private folder as `output-<n>`, not under a name from a reply. `src/storage` left the single-file allowlist. | `python.trivial-function`, `python.module-only-public`, and Pylint's ten locals per function; no file name comes from a reply. |
| 08, 21 | The run path ran end to end on 2026-10-17 outside ComfyUI, free: `seedream_4.0` `t2i` at `2K` with `credit_ceiling` 0 checked, created the pack's `ComfyUI` canvas, ran, recorded, waited, read the node, downloaded a 1.7 MB PNG, and deleted the record (19 seconds). `seedream_4.1` with `credit_ceiling` 0 stopped at the quote: "This run needs 2 credits, more than its credit_ceiling of 0. Nothing was billed." The canvas record was copied into ComfyUI's state folder, so ComfyUI reuses that canvas. Credits: 0. | Checks the milestone before a node exists. |
| 02, 07, 08, 21 | Part 1 ran on 2026-10-17 (results in 02). Fixes: an unknown submission is exit 20 with `cli.operation_submission_absent`, so `OPERATION_STATES["ABSENT"]` is gone; the wait raises `SubmissionAbsentError` on that code, which deletes the record with `GENERATION_ABSENT`, and `validate_lost_run` reads it as `RUN_UNCERTAIN`. The wait reports `RUNNING` on each still-running answer. The failure map gains `service.20009` (`CANVAS_MISSING`) and `cli.invalid_upload_file` (`UPLOAD_INVALID`, naming the 30 MiB image limit). No other change: text reading already refuses a connected item through its one voice slot, the pack's checks already refuse the values the server would substitute, and outputs are decoded from their bytes. C-17 waits for the owner. Credits: 28; total 28. | Part 1's replies. |
| 15, 08 | Model: Info, as built: `src/dreamina/report.py` has one public `read_report(name, deadline)`, which checks the CLI, finds the model, reads its specification and a speech model's voices, and builds the report; the node only bounds it by the request timeout and writes the JSON. `describe_model` and `_describe_flag` are gone (one statement each), and `read_specifications` is private. `VoiceCatalog` is `ModelVoices`, and the report keys `max_total_video_duration_ms` and `max_total_audio_duration_ms` are `max_total_video_ms` and `max_total_audio_ms`. `wait_for_run` is public again. | `catalog` is a banned term, names have at most four words, and `python.trivial-function`. |
| 17, 18 | `scripts/nodes/schema.py` checks that every required `send` parameter is an input and every input a parameter, instead of equal sets, because the shared `GenerateNode.send` also takes the media sockets a kind node does not show. The README's CLI paragraph and the removal of the CLI requirement line, due in the Frontend milestone, ship with the Image milestone. | The image node shows only `images`; the README change was missed at Frontend. |
| 09, 21 | Image runs through ComfyUI, 2026-10-17. K-1: every refusal word for word as the plan writes it; steps 1 to 3 at queue time (ComfyUI repeats the validator's text under `model`, `prompt`, and `arguments`), steps 4 and 5 at run time, step 6 stopped at Dreamina's quote of 6, free. I-1 (starting values) was accepted and made, but an outside ComfyUI Manager reboot during the run call killed ComfyUI; the CLI child finished the submit, so the image is on the canvas, billed, and unrecorded, since the reply never arrived. I-1 then ran again on the free `seedream_4.0` and fed I-2: `i2i`, `--ref node:…`, `{{reference1}}` saved as `{{node:…}}`, the canvas edge drawn. I-3 on the free `seedream_4.0`: the upload saved as `{{res:…}}`, and a new `run_number` uploaded again under a new resource ID. The same prompt queued again came from ComfyUI's cache with no call. Credits: 12; total 40. | Another session restarts the shared ComfyUI; paid runs check the queue first, and a restart during a run call can lose its record, which no code can prevent. |
| 12, 08 | Upscale, as built: `validate_cli` returns the schema's flags of every command it checked, so the upscale reads its rules from the one check; there is no `read_command_flags` (two statements). `SchemaFlag.default` is any JSON value, since `detail`'s default is the integer 50. `parse_upscale_arguments` returns the values to send by flag name. `UPSCALE_DEFAULTS` is `UPSCALE_CEILING` and `UPSCALE_ARGUMENTS`, and `UPSCALE_COMMAND` names the command. `UpscaleRequest` carries the node's title for the imports, and an `UpscaleCall` record writes the call. A lost upscale reply is `RUN_UNCERTAIN`, as 12 says. | `python.trivial-function`, the ten-locals limit, and typed constants. |

## Research sources

The research behind these plans is kept in `plans/research/`, so it outlives
the session that made it. Read it when a plan's fact needs checking.

| File                                   | What it holds                                                                                              |
| -------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `research/cli.md`                      | Every CLI fact with its source: install, flags, replies, exit codes, sign-in, models, runs, credits, waits, uploads, downloads, upscale, Elements, open questions |
| `research/catalog.md`                  | The owner's live model lists by kind, with modes, flags, references, and membership fields; the default model per node |
| `research/captures/`                   | The CLI's replies on 2026-10-16: `schema.json`, `version.json`, the sign-in and error replies, and the model and voice lists |
| `research/docs/dreamina-canvas-cli/`   | The installed skill and its protocol references, without the parts it marks confidential                  |
| `research/owner-rules.md`              | Every rule the owner set while building O, B, and F, with Dreamina notes                                   |
| `research/tooling.md`                  | F's tooling file by file, with the Dreamina value for each                                                 |
| `research/brand.md`                    | Dreamina's mark and colors, the other packs' palettes, this pack's palette and mark                        |
| `research/terms.md`                    | Dreamina's terms, what ByteDance publishes for software, how the pack stays inside it, rejected routes      |

## Glossary

| Term                 | Meaning                                                                                                       |
| -------------------- | ------------------------------------------------------------------------------------------------------------- |
| Dreamina             | ByteDance's creative app at `dreamina.capcut.com`, part of CapCut                                             |
| CLI                  | The Dreamina Canvas CLI, `dreamina-canvas`, which the person installs; the only way the pack talks to Dreamina |
| Canvas               | A Dreamina project that holds nodes; the pack uses one named `ComfyUI`                                        |
| Canvas node          | A node on the Dreamina canvas, such as an image, a video, or an Element, named by its node ID (`node_…`)       |
| Resource             | One concrete image, video, or audio file on Dreamina, named by its resource ID (a lowercase UUID)              |
| Model name           | Dreamina's canonical model name, such as `seedance_2.5`, typed into `model`                                    |
| Alias                | Another name `model list` gives for a model; matched, never sent                                              |
| Mode                 | What a run does: `t2i`, `i2i`, `t2v`, `first_last_frame`, `m2v`, `tts`, or `music`                            |
| Flag                 | One setting of a mode, such as `duration`, set in `arguments` and sent as `--duration`                        |
| Arguments            | The `arguments` input: a JSON object of a model's flags and values                                            |
| Reference            | An input a run uses: a canvas node (`node:`) or a resource (`res:`), carried by `DREAMINA_REFERENCES`          |
| Element              | A Dreamina canvas node that holds one recurring character, product, or place for later runs                   |
| Credits              | Dreamina's unit of spending                                                                                   |
| Credit ceiling       | The `credit_ceiling` input, sent as `--credit-ceiling`: the most a run may cost                               |
| Quote                | Dreamina's price for a saved run, checked against the ceiling                                                 |
| Submit ID            | The UUID that names one run; reusing it never charges twice; `operation wait` follows it                      |
| Generation record    | A file in the state folder for a run Dreamina accepted, kept until its outputs are downloaded                 |
| Paid node            | A node that sends a billed run; it subclasses `PaidNode`                                                       |
| Run number           | The `run_number` input; changing it sends the same run again                                                  |
| State folder         | The private folder outside ComfyUI that holds the settings, the canvas, and the generation records            |
