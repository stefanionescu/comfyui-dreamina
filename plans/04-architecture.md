# Architecture

This plan fixes:

- the repository tree;
- the runtime packages and their import order;
- every module and what it owns;
- how each run flows.

Every other plan uses these paths and names. It follows F's current code
(`F=/Users/dr_stone/Documents/work/comfyui-fal`, commit `cef8b6e`), which was
ported from B (`B=/Users/dr_stone/Documents/work/comfyui-byteplus`, commit
`472cf10`). Where F and B differ, F wins.

## Contents

- [Repository tree](#repository-tree)
- [Runtime packages](#runtime-packages)
- [Import layers](#import-layers)
- [Import-linter contracts](#import-linter-contracts)
- [Module inventory](#module-inventory)
- [Port map](#port-map)
- [How a paid run flows](#how-a-paid-run-flows)
- [How a model is read](#how-a-model-is-read)
- [How an upscale flows](#how-an-upscale-flows)
- [How a recorded generation is collected](#how-a-recorded-generation-is-collected)
- [How the person signs in](#how-the-person-signs-in)
- [How the CLI is installed](#how-the-cli-is-installed)
- [Threads, event loops, and subprocesses](#threads-event-loops-and-subprocesses)
- [Where data lives](#where-data-lives)
- [IDs other packs use](#ids-other-packs-use)

## Repository tree

The repository is `comfyui-dreamina`. It installs as `custom_nodes/dreamina`
([01-decisions.md](01-decisions.md#names-and-identifiers)).

```text
comfyui-dreamina/
├── __init__.py                 Extension class, WEB_DIRECTORY, comfy_entrypoint
├── pyproject.toml              Project dreamina, tools, import contracts, [tool.comfy]
├── requirements.txt            Generated: pydantic>=2.10,<3
├── README.md, ADVANCED.md, LICENSE.md, AGENTS.md, CLAUDE.md
├── mise.toml, .mise.local.toml (ignored), package.json, bun.lock, uv.lock, bunfig.toml
├── tsconfig.json, pyrightconfig.json, .prettierrc.json, .prettierignore,
│   .markdownlint-cli2.yaml, .stylelintrc.json, .typos.toml,
│   .gitignore, .gitattributes, .comfyignore
├── .githooks/                  commit-msg, pre-commit, pre-push
├── .mise/tasks/                comfy:* and repo:* tasks
├── rules/                      Engineering rules (protected)
├── quality/                    Every check the tasks run
├── plans/                      These plans (tracked; their skill copy and captures are ignored)
├── scripts/                    Frontend build, node checks, workflow generator
├── src/                        Runtime packages (below)
├── web/
│   ├── extension.js, extension.css   Built bundle (committed)
│   ├── docs/                   One help page per node: Dreamina<Class>.md
│   ├── scripts/                TypeScript sources (not shipped)
│   └── styles/                 CSS source (not shipped)
├── example_workflows/          Generated workflow JSON files
├── subgraphs/                  Generated blueprints, one per example step
└── docs/images/                badges/, brand/, diagrams/, screenshots/
```

The pack ships no list of Dreamina's models and no CLI binary.

## Runtime packages

`src/` holds only packages, as in F.

| Package         | Holds                                                                                                         |
| --------------- | ------------------------------------------------------------------------------------------------------------- |
| `src.nodes`     | Node classes, the shared generation node, and the output builder                                              |
| `src.comfy`     | ComfyUI glue: running with progress and cancel, media encoding and decoding, routes, the runtime, the account and CLI routes |
| `src.dreamina`  | Every CLI call: finding and running the binary, the installer, the failure map, sign-in, model reads, modes, arguments, references, uploads, the canvas, generations, upscales, Elements, voices, downloads, and Model: Info's report |
| `src.settings`  | Private settings, their local route, and the checks that keep routes local                                   |
| `src.storage`   | Private files: settings, the canvas, generation records                                                       |
| `src.types`     | Records, type aliases, JSON parsing, and `DreaminaError`                                                      |
| `src.config`    | Constants and messages, with no code                                                                          |

## Import layers

Each package imports only the packages below it, as in F:

```text
src.nodes
src.comfy
src.dreamina | src.settings
src.storage
src.types
src.config
```

- **ComfyUI is imported only in `src/nodes/`, `src/comfy/`, and the root
  `__init__.py`.**
- **`src/dreamina/cli.py` is the one module that starts the CLI.**
  `src/dreamina/installer.py` is the one module that downloads and runs the
  installer.
- **`src.dreamina` and `src.settings` are siblings and do not import each
  other.** So the routes of Dreamina Settings live in `src/comfy/settings.py`,
  which imports both. `src.settings` keeps F's local-route guard and body
  reader, which `src/comfy/settings.py` reuses.

## Import-linter contracts

`pyproject.toml` keeps F's six contracts, with `src.fal` replaced by
`src.dreamina` in contracts 3 to 6
([03-repository-setup.md](03-repository-setup.md)):

1. Scripts must not import the quality tooling.
1. Runtime must not import scripts or quality tooling.
1. The packages stack in one order (the layers above).
1. Only the host packages import ComfyUI's modules. `src.config`,
   `src.dreamina`, `src.settings`, `src.storage`, and `src.types` may not
   import `comfy`, `comfy_api`, `comfy_api_nodes`, `comfy_execution`,
   `comfy_extras`, `folder_paths`, `node_helpers`, `nodes`, or `server`.
1. Records must not import operations. `src.types` may not import
   `src.comfy`, `src.nodes`, `src.dreamina`, `src.settings`, or
   `src.storage`.
1. Config must not import runtime code or tooling. `src.config` may not
   import `src.nodes`, `src.comfy`, `src.dreamina`, `src.types`, `scripts`,
   or `quality`.

## Module inventory

Rules every module follows:

- Every module ends with `__all__`.
- Every function starts with a verb from `rules/NAMING.md` or is an
  `is_`/`has_` predicate.
- Public names listed here are the contract between plans. The owning plan
  (last column) fixes the private helpers.
- A module that would pass 300 lines is split as its plan says.

### Root

| Path          | Owns                                                                                                         | Plan |
| ------------- | ------------------------------------------------------------------------------------------------------------ | ---- |
| `__init__.py` | `Extension(ComfyExtension)`: `on_load` creates the runtime off the loop and registers routes; `get_node_list` returns `NODE_TYPES`; `comfy_entrypoint` | 05 |

### `src/config/`

| Module                     | Owns                                                                                                                          | Plan |
| -------------------------- | ----------------------------------------------------------------------------------------------------------------------------- | ---- |
| `namespace.py`             | `NODE_PREFIX` (`"Dreamina"`), `MENUS` (`SHARED` `Dreamina`, `IMAGE` `Dreamina/Image`, `VIDEO` `Dreamina/Video`, `AUDIO` `Dreamina/Audio`), `SOCKET_TYPES` (`REFERENCES`) | 05 |
| `dreamina.py`              | The CLI's names and limits: `BINARY_NAMES`, `INSTALL_FOLDERS`, `GLOBAL_ARGUMENTS` (`--format json --non-interactive`), `MINIMUM_VERSION` (`1.0.3`), `REPLY_SCHEMA_VERSION`, `REQUIRED_COMMANDS`, `EXIT_CODES`, `CALL_SECONDS`, `REPLY_BYTES`, `MAX_REPLY_DEPTH`, `MAX_REASON_CHARACTERS`, `REASON_ENDINGS`, `DREAMINA_URLS`; 08 Part B adds `WAIT_SLICE` (`15s`), `CANVAS_NAME` (`ComfyUI`), `CANVAS_PAGE_SIZE`; 05 adds `ACCOUNT_TIMEOUTS`, `SIGN_IN_FAILURES`, `SIGN_IN_SECONDS`; 13 adds `TITLE_MAX_UNITS` | 08, 05, 13 |
| `installer.py`             | `INSTALLER_URLS` (by OS), `INSTALLER_DOMAINS`, `INSTALLER_REDIRECTS`, `INSTALLER_SHELLS`, `INSTALLER_DOWNLOAD_SECONDS`, `INSTALL_TIMEOUT_SECONDS`, `INSTALLER_BYTES`, `INSTALLER_REASON_LINES` | 05 |
| `patterns.py`              | Regular expression text, each added by its first user: `REVISION_PATTERN` (05), `VERSION_PATTERN` and `REASON_PATTERNS` (token shapes, links, paths; 08 Part A), `PLACEHOLDER_PATTERN` (07), `SCHEMA_RANGE_PATTERN` (12). 05 fixes every value but the last | 05, 07, 08, 12 |
| `security.py`              | F's local route rules with `/dreamina/v1` and `X-Dreamina-Comfy`; `ROUTES` (`STATUS`, `SETTINGS`, `SESSION`, `CLI`), `CHANGE_HEADER`, `ACCOUNT_TOKEN_BYTES` | 05   |
| `settings.py`              | `SETTING_RANGES` (`max_upload_megabytes` default 210, range 1 to 210), `SETTINGS_BODY`                                       | 05   |
| `storage.py`               | `ENVIRONMENT_VARIABLES` (`DREAMINA_COMFY_STATE_DIRECTORY`; 08 adds `DREAMINA_CANVAS_INSTALL_DIR`), `STATE_FOLDER_NAMES`, `PRIVATE_FOLDER_MODE`, `TEMPORARY_PREFIX` (`.dreamina-`), `FILE_NAMES` (`settings.json`; 08 adds `canvas.json`), `MAX_FILE_BYTES`; 08 adds `GENERATION_FOLDER` (`generations`) and `GENERATION_SUFFIX` | 05, 08 |
| `units.py`                 | `SECONDS_PER_MINUTE` (05); `BYTES_PER_MEGABYTE` (07, with 05's value)                                                         | 05, 07 |
| `execution.py`             | `PROGRESS_STEPS` (`CHECKED`, `UPLOADED`, `ACCEPTED`, `RUNNING`, `DOWNLOADED`, `TOTAL`), `CANCELLATION_POLL_SECONDS`; 05 fixes the values, and 08 Part B creates the file with its reader | 05, 08 |
| `media.py`                 | `MEDIA_TYPES` (06 creates the module with it, a milestone before 07); 07 adds the encoding constants: PNG and WAV forms, the upload extension and `--type` per media kind, `IMAGE_TENSOR`, `FREE_ATTEMPTS`, `REFERENCE_TYPES`, `PLACEHOLDERS`, `FRAME_MODES`, `VOICE_REFERENCE`, `RESOURCE_KINDS`, `RESOURCE_SUCCESS` | 06, 07 |
| `models.py`                | `KINDS` (`image`, `video`, `audio`), `KIND_NODES`, `DEFAULT_MODELS`, `DEFAULT_ARGUMENTS`, `MODES` by kind, `SCENARIOS`, `SELECTION_KEYS` (`mode`, `scenario`), `PROMPT_FLAG`, `COUNT_FLAG`, `COUNT_VALUE`, `FLAG_PREFIX`, `FRAME_IMAGES` (2), `SUGGESTION_COUNT`, `LIST_COMMAND`, `LIST_TIMEOUT_SECONDS`; 15 adds `VOICE_PAGE_COUNT` | 06, 15 |
| `inputs.py`                | `INPUT_NAMES` (`IMAGES`, `VIDEOS`, `AUDIO`, `REFERENCES`, `MODEL`, `CREDIT_CEILING`, `RUN_NUMBER`, `PROMPT`, `ARGUMENTS`), in F's dict form, which `scripts/nodes/schema.py` reads; `RUN_NUMBER`, `CREDIT_CEILING_RANGE`, `TOOLTIPS` (the tooltips the paid nodes share), `ARGUMENTS_TOOLTIPS` by kind; `DEFAULT_CEILINGS` by kind, one key added by each of 09, 11, and 10 | 06 |
| `generations.py`           | `RECORD_VERSION`, `RECORD_RETENTION_SECONDS`, `LABEL_SEPARATOR`, `LABEL_CHARACTERS`, `OPERATION_STATES` (`SUCCEEDED`, `ABSENT`, from the contract runs), `WAIT_REREAD_SECONDS`; 12 adds `UPSCALE_FLAGS`, `UPSCALE_MODES`, `UPSCALE_MODEL`, `UPSCALE_IMPORT_KIND`, `SCHEMA_CONSTRAINTS`, `UPSCALE_DEFAULTS` | 08, 12 |
| `messages/inputs.py`       | Refusals of `prompt`, `arguments`, placeholders, and connected inputs; `SINGLE_VALUE`; the upscale refusals (12) and the Element refusals (13) | 06, 07, 12, 13 |
| `messages/models.py`       | A model not in the list, a model of another kind, an ambiguous name, a mode the model lacks, a flag or value it refuses; the reference limits (07) | 06, 07 |
| `messages/media.py`        | Encoding, upload, and download refusals                                                                                       | 07   |
| `messages/cli.py`          | CLI missing, too old, changed, failed to start; installer outcomes                                                            | 05, 08 |
| `messages/run.py`          | The CLI failure messages: sign-in, credits, ceiling, plan, safety, input, network; `FREE_TIMEOUT` (15); the upscale refusals (12) | 08, 12, 15 |
| `messages/generations.py`  | Run outcomes: timeout, cancel, recorded, collected, expired, gone, uncertain; Generation: Download's empty list (14)           | 08, 14 |
| `messages/requests.py`     | F's local HTTP body refusals                                                                                                  | 05   |
| `messages/settings.py`     | Settings and state refusals; sign-in route outcomes                                                                           | 05   |

### `src/types/`

| Module            | Owns                                                                                                                         | Plan |
| ----------------- | ---------------------------------------------------------------------------------------------------------------------------- | ---- |
| `__init__.py`     | `Json`, `Kind` (`image`, `video`, `audio`), `MediaKind` (`image`, `video`, `audio`, `element`); `Value`, `Reply` Pydantic bases | 05 |
| `errors.py`       | `ErrorCode`, `DreaminaError`                                                                                                 | 05   |
| `parsing.py`      | `parse_json` (F's)                                                                                                           | 05   |
| `settings.py`     | `Settings`, `Configuration`                                                                                                  | 05   |
| `cli.py`          | `CliFailure` (`code`, `failure_class` aliased from `class`, `message`, `reason`, `retryable`, `required_action`, `validation`, `local_storage`), `Validation`, `LocalStorage`, `CreditConfirmation`, `PartialItem`, `PartialRun`, `CliMeta`, `CliReply` (`ok`, `payload` aliased from `data`, `error`, `credit_confirmation`, `partial`, `meta`), `CliResult` (`exit_code` and `reply`; the success JSON is `result.reply.payload`) | 08 |
| `models.py`       | `ModelFlag`, `ReferenceLimit`, `ModelReferences`, `ModelMode`, `ListedModel` (`name` aliased from `model`, `kind` from `type`), `ModelListReply` | 06 |
| `references.py`   | `Reference` (`origin` `node` or `resource`, `value`, `media`, `title`, `typed_value`), `LocalMedia` (a ComfyUI value waiting for upload); 13 adds `ElementRequest` | 07, 13 |
| `replies.py`      | The CLI's success payloads read with `Reply`. Part A: `VersionReply`, `SchemaFlag`, `SchemaCommand`, `SchemaReply`, `AuthState`, `AuthChallenge`, `AuthReply`, `AccountReply`. Part B: `CanvasProject`, `CanvasReply`, `CanvasListReply`, `NodeResource`, `NodeView`, `RunSubmission`, `RunReply` (`node`, `submission`), `OperationResource`, `Submission`, `SubmissionError`, `OperationReply`, `NodeShowItem`, `NodeShowReply`, `UploadReply`, `DownloadReply`. Later: `ElementReply`, `UpscaleError`, `UpscaleItem`, `UpscaleReply`, and `SchemaFlag`'s rule fields (12); `NodeView.subjects` (13); `Voice`, `VoiceCatalog`, `VoicePage` (15) | 08, 12, 13, 15 |
| `generations.py`  | `CanvasRecord`, `GenerationRecord` (`Value`), `GenerationPlan`, `GenerationResult`, `OutputFile`; 12 adds `UpscaleRequest`   | 08, 12 |
| `specifications.py` | `CountRange`, `MaterialLimits`, `MaterialType`, `MaterialSet`, `SizeMembership`, `ModeSpecification`, `SpecificationMatch`, `SpecificationReply`: one model's full specification, as `model <canonical>` returns it | 15 |

### `src/storage/`

| Module      | Owns                                                                        | Plan |
| ----------- | --------------------------------------------------------------------------- | ---- |
| `files.py`  | `choose_state_directory`, `save_file`, `read_file` (F's)                     | 05   |
| `canvas.py` | `CanvasStore`: read, save, and delete `canvas.json`                          | 08   |

### `src/settings/`

F's five modules, re-valued:

- `schema.py`;
- `store.py` (`ConfigurationStore`);
- `access.py` (`build_local_route`);
- `body.py` (`read_body`).

The store keeps the settings and the account cache token. F's `routes.py` is
not ported: every route, the settings save among them, is in
`src/comfy/settings.py`, because the status reports the CLI and the account
([05-foundation.md](05-foundation.md)).

### `src/dreamina/`

| Module                     | Owns                                                                                                                                           | Plan |
| -------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- | ---- |
| `cli.py`                   | `find_binary()`, `send_command(arguments, timeout_seconds)` → `CliResult`: the only subprocess start, with byte caps and kill on cancel; `parse_reply(payload, record)`, which reads every success payload | 08 |
| `failures.py`              | `build_failure(result, context, *, credit_ceiling=None)` → `DreaminaError`: the map from exit code and `error` fields to messages; `sanitize_reason(text)`; `build_generation_failure(reply)` for a failed generation | 08 |
| `contract.py`              | `validate_cli()`: `version` and `schema` once per process; the version gate and the required commands and flags; `is_current_version(version)`, `None` being not current; a passed check is kept per binary path and modification time, so an install is checked again. 12 adds `read_command_flags(path)`, the schema's flags of one command | 08, 12 |
| `installer.py`             | `read_cli_version()`; `download_installer()`: the OS's official installer from its fixed address and ByteDance's CDN, into a private temporary file; `save_cli(installer_path)`: run it, which saves the CLI to disk | 05 |
| `account.py`               | `is_signed_in()`, `read_account()`, `delete_sign_in()`, `SignInState`, whose `create_challenge` runs the private `_create_sign_in` (`auth login`) and `_wait_for_sign_in` (`auth wait`) | 05 |
| `models.py`                | `find_model(name, kind)`, which Model: Info calls with `kind=None`; the private `_read_model_list(kind)`, with F's per-process cache and shared reads per event loop | 06 |
| `modes.py`                 | `choose_mode(model, kind, connected, arguments)` → the mode entry, with its scenario; `describe_mode(mode)`, the mode as refusals name it | 06 |
| `arguments.py`             | `parse_arguments(text)`; `validate_argument_names(model, arguments)`, also run at queue time; `choose_prompt(prompt, arguments)` → the one prompt; `build_flags(mode, prompt, arguments)` → the `--mode` and `--flag value` list | 06 |
| `references.py`            | `validate_references(mode, items, arguments)`; `plan_references(references, local, uploaded)` → the `--ref` order and the placeholder table; `format_prompt(prompt, placed)` | 07 |
| `uploads.py`               | `send_media(project_id, items, encode, settings, deadline)` → `tuple[Reference, ...]`                                                         | 07   |
| `downloads.py`             | `download_resources(project_id, node, submit_id, settings, deadline)` → `OutputFile`s, with the byte-count and SHA256 checks                    | 07   |
| `canvas.py`                | `find_canvas(store)` → the saved canvas while `canvas ls` lists it, else `None`, clearing a canvas the person deleted; `create_canvas(store)` → a new `ComfyUI` canvas, saved | 08 |
| `operation.py`             | `Operation[Result]` protocol (F's), `Progress`; `wait_until_settled(task)`, which the run call and the upscale call share | 08 |
| `generations/records.py`   | `GenerationStore`, `list_generation_labels`                                                                                                    | 08   |
| `generations/operation.py` | `GenerationOperation` (check, upload, run, record, wait, show, download), `CollectOperation` (Generation: Download)                             | 08   |
| `generations/waiting.py`   | `wait_for_operation(submit_id, project_id, deadline, progress)`: the `operation wait` loop; `validate_lost_run(submit_id, project_id)`: the read-only check of a lost run reply. Kept apart so `operation.py` stays under 300 lines | 08 |
| `upscale.py`               | `parse_upscale_arguments(text, flags)`; `UpscaleOperation`: import, `node upscale image`, record, wait, download                               | 12   |
| `elements.py`              | `create_element(project_id, request, deadline)` → the Element's `Reference`                                                                    | 13   |
| `voices.py`                | `read_voices(model, deadline)`: every page of `voice list --model`                                                                             | 15   |
| `report.py`                | `read_specifications(model, kind, deadline)`: one `model <canonical>` read; `describe_model(model, specifications, voices)`: Model: Info's report | 15 |

### `src/comfy/`

| Module          | Owns                                                                                                                       | Plan |
| --------------- | -------------------------------------------------------------------------------------------------------------------------- | ---- |
| `runtime.py`    | `Runtime` (configuration store, generation store, canvas store, sign-in state), `create_runtime`, `get_runtime`             | 05   |
| `routes.py`     | `register_routes`: F's state folder check, then `SettingsRoutes`                                                           | 05   |
| `settings.py`   | `SettingsRoutes`: `GET status`, `PATCH settings`, `POST` and `DELETE session`, `POST cli`                                  | 05   |
| `execution.py`  | `send_run`, `wait_for_run`, `wait_for_thread` (F's `send_request`, `wait_for_request`, `wait_for_thread`, renamed to the vendor's word) | 08 |
| `media.py`      | `list_local_media` (splits connected image and audio batches into items); `encode_local_file` (IMAGE to PNG, VIDEO to MP4, AUDIO to WAV, in a temporary folder); `decode_images`, `decode_video`, `decode_audio` | 07 |

### `src/nodes/`

| Module         | Owns                                                                                                              | Plan |
| -------------- | ----------------------------------------------------------------------------------------------------------------- | ---- |
| `__init__.py`  | `NODE_TYPES` in menu order                                                                                         | 05   |
| `base.py`      | `PaidNode` (F's), with the account cache token                                                                     | 08   |
| `outputs.py`   | `build_node_outputs`: downloaded files and the node view into a node's outputs, shared by every paid node and Generation: Download; `build_result_document`, the `result` JSON | 08 |
| `generate.py`  | `GenerateNode`: the shared generation node the three kind nodes subclass, each setting `kind`, `display_name`, `default_ceiling`, `list_inputs`, and `outputs`; a docstring-only stub from the Tooling milestone ([03](03-repository-setup.md)) | 08 |
| `image.py`     | `ImageGenerate`                                                                                                    | 09   |
| `video.py`     | `VideoGenerate`                                                                                                    | 10   |
| `audio.py`     | `AudioGenerate`                                                                                                    | 11   |
| `upscale.py`   | `ImageUpscale`                                                                                                     | 12   |
| `element.py`   | `ElementAdd`                                                                                                       | 13   |
| `download.py`  | `GenerationDownload`                                                                                               | 14   |
| `model.py`     | `ModelInfo`                                                                                                        | 15   |

`NODE_TYPES` order: ImageGenerate, ImageUpscale, VideoGenerate, AudioGenerate,
ElementAdd, GenerationDownload, ModelInfo.

### `scripts/`

F's `scripts/` (frontend build, node schema export and checks, workflow
generator), re-valued
([17-scripts-and-workflows.md](17-scripts-and-workflows.md)).

### `web/scripts/`

F's files with the same names, re-valued:

- `extension.ts`, `routes.ts`, `schema.ts`, `text.ts`, `http.ts`,
  `browser.ts`, `dom.ts`, `host.d.ts`;
- `settings/api.ts`, `settings/dialog.ts`, `settings/schema.ts`;
- `web/styles/interface.css`.

Two new modules keep `dialog.ts` under 300 lines:

- `settings/account.ts`: the sign-in poll and the account section;
- `settings/cli.ts`: the CLI section, its state line and its one
  **Install** or **Update** button.

([16-frontend.md](16-frontend.md))

## Port map

Copy before writing. These modules are ported from F, and then changed as
their plan says.

| Source file                                                     | Dreamina file                                | Change size |
| --------------------------------------------------------------- | -------------------------------------------- | ----------- |
| `F/__init__.py`                                                 | same                                         | Names |
| `F/src/comfy/{runtime,routes,execution}.py`                     | same                                         | Names; the runtime holds the generation, canvas, and sign-in state; `execution.py` renames request to run |
| `F/src/settings/{access,body}.py`                               | same                                         | Names |
| `F/src/settings/{schema,store}.py`                              | same                                         | Names, setting ranges; no credential; the store's token follows the account |
| `F/src/settings/routes.py`                                      | not ported                                   | Its settings save joins every other route in `src/comfy/settings.py` |
| `F/src/storage/files.py`                                        | same                                         | Names |
| `F/src/storage/credentials.py`                                  | not ported                                   | The CLI keeps the credentials |
| `F/src/types/{__init__,errors,parsing,settings}.py`             | same                                         | `Kind` values, `DreaminaError` |
| `F/src/types/credentials.py`                                    | not ported                                   | No credential |
| `F/src/fal/operation.py`                                        | `src/dreamina/operation.py`                  | Names |
| `F/src/fal/transport.py`, `streams.py`                          | `src/dreamina/cli.py`                        | Rewritten: one subprocess call instead of HTTP |
| `F/src/fal/failures.py`                                         | `src/dreamina/failures.py`                   | Rewritten map, same shape: structured fields to messages, reasons cleaned |
| `F/src/fal/models.py`                                           | `src/dreamina/models.py`                     | Same cache and shared reads; reads `model list --type` instead of fal's listing |
| `F/src/fal/schema.py`                                           | not ported                                   | The CLI's list is already parsed; Pydantic records read it |
| `F/src/fal/arguments.py`                                        | `src/dreamina/arguments.py`                  | Same parse; checks flags and values instead of OpenAPI fields |
| `F/src/fal/uploads.py`                                          | `src/dreamina/uploads.py`                    | `resource upload` instead of fal storage |
| `F/src/fal/outputs.py`                                          | `src/dreamina/downloads.py`                  | `node show` resources and `resource download` instead of a result walk |
| `F/src/fal/options.py`, `F/src/nodes/options.py`, `F/src/types/options.py`, `F/src/config/options.py` | not ported | No Request Options |
| `F/src/fal/queue/records.py`                                    | `src/dreamina/generations/records.py`        | Submit IDs and canvas IDs instead of fal URLs |
| `F/src/fal/queue/operation.py`                                  | `src/dreamina/generations/operation.py`, `waiting.py` | The run call, the record, the wait loop, `node show`, downloads; no cancel |
| `F/src/nodes/base.py`                                           | same                                         | Names; the account token |
| `F/src/nodes/endpoint.py`                                       | `src/nodes/generate.py`                      | Media sockets, `references`, `credit_ceiling` instead of `files` and `options` |
| `F/src/nodes/outputs.py`                                        | same                                         | Images, video, audio, references, result |
| `F/src/nodes/{image,video,audio}.py`                            | same                                         | Kind values and sockets |
| `F/src/nodes/files.py`                                          | `src/nodes/element.py`                       | Rewritten on its skeleton: an Element instead of a file list |
| `F/src/nodes/download.py`                                       | same                                         | Generation records |
| `F/src/nodes/model.py`                                          | same                                         | The CLI's model and voices |
| `F/src/nodes/text.py`, `mesh.py`                                | not ported                                   | Dreamina has no text or 3D models in the CLI |
| `F/web/scripts/*`, `F/web/styles/interface.css`                 | same                                         | Names and text; the key section becomes the CLI and account sections |

New modules with no source to port:

- `src/dreamina/{contract,installer,account,modes,references,canvas,upscale,elements,voices,report}.py`;
- `src/dreamina/generations/waiting.py`;
- `src/types/specifications.py`;
- `src/comfy/settings.py`;
- `src/storage/canvas.py`;
- `src/nodes/upscale.py`.

## How a paid run flows

1. **Queue time.** ComfyUI calls `GenerateNode.validate_inputs(model,
   prompt, arguments)` when the workflow is queued. `credit_ceiling` is left
   out so ComfyUI keeps its own range check for it. It runs
   `validate_cli`, `parse_arguments`, `find_model`, `validate_argument_names`,
   and `choose_prompt`. A refusal blocks the queue, for free. Linked inputs
   arrive as `None` and are checked at run time.
1. **Run time.** ComfyUI calls `PaidNode.execute`, which drops `run_number`.
   `GenerateNode.send` reads the inputs.
1. `send_run` reads the configuration snapshot, runs
   `operation.validate(settings)`, and sets progress 0.
1. **Before paying.** `GenerationOperation.send`:
   1. runs `validate_cli`;
   1. reads `arguments` with `parse_arguments`;
   1. matches the model with `find_model` ([How a model is read](#how-a-model-is-read));
   1. checks the `arguments` keys with `validate_argument_names`;
   1. chooses the mode entry with `choose_mode`;
   1. takes the one prompt with `choose_prompt`;
   1. builds the flag list with `build_flags`, which refuses a flag the
      chosen entry does not list;
   1. checks the references against the entry's limits with
      `validate_references`.

   Every refusal of
   [01-decisions.md](01-decisions.md#checking-a-model-before-paying) happens
   here, before anything is uploaded or paid. Progress: `CHECKED`.
1. **The canvas.** `find_canvas` looks for the saved canvas in `canvas ls`.
   When none is saved, or the person deleted it, the saved ID is cleared and
   `create_canvas` creates `ComfyUI`, before any upload. A canvas deleted
   during a run fails that run, and nothing is sent again.
1. **Uploads.** In a worker thread, each connected image, video, and audio is
   encoded to a temporary file. `send_media` uploads each with `resource
   upload`. `plan_references` puts every reference in order, and
   `format_prompt` writes the prompt's placeholders in the CLI's form.
   Progress: `UPLOADED`.
1. **The run.** A new submit ID (`uuid4`). Then one `node create <kind> --run`
   call with every flag and `--credit-ceiling`. The call is shielded: a
   cancel waits for it to return.
1. **The answers.**
   - Exit 0: the run was accepted. The pack saves a `GenerationRecord` from
     the reply's `node.nodeId` and its `submission`, before the first wait.
     Progress: `ACCEPTED`.
   - Exit 10: the run stopped at the ceiling, and the node is refused with
     Dreamina's quote, nothing billed.
   - Exit 20, or a local store failure `after_submit`: accepted, and
     recorded from `partialData`.
   - Any other failure: mapped by `build_failure`.
   - A lost reply: `validate_lost_run` checks it read-only with `operation
     status`. Nothing is recorded or sent again.
1. **The wait.** `wait_for_operation` calls `operation wait <submitId>
   --project-id <canvas> --timeout 15s` until the state is terminal or the
   request timeout passes. Exit 20 means the run is still going, and the loop
   goes on. Between calls the loop checks ComfyUI's cancel. Progress:
   `RUNNING`.
1. **A cancel** after acceptance stops the loop. The record stays, and the
   node raises `DreaminaError` with `INTERRUPTED` and
   `GENERATION_KEEPS_RUNNING`: the generation keeps running and is billed,
   and Generation: Download collects it. A cancel before acceptance shows as
   ComfyUI's `InterruptProcessingException`, with nothing billed.
1. **A failed generation** (a terminal state with `submissionError` or failed
   resources) deletes the record and is mapped by
   `build_generation_failure`.
1. **The outputs.**
   1. `node show` reads the node.
   1. `download_resources` downloads each resource into a temporary folder
      and checks its byte count and SHA256.
   1. The record is deleted. Progress: `DOWNLOADED`.
   1. `build_node_outputs` decodes the files in a worker thread. An empty
      output becomes `ExecutionBlocker(None)`. Progress: `TOTAL`.

## How a model is read

`find_model(name, kind)` is the one public way to the model lists. Every
generation node calls it with its kind, and Model: Info with `kind=None`,
which searches every kind. It reads each list through the private
`_read_model_list(kind)`:

1. A kind's list already read in this ComfyUI process is returned from memory.
1. Otherwise one `model list --type <kind>` call through `send_command`. Two
   callers on one event loop that need the same kind share one read, each
   awaiting it through `asyncio.shield`, as in F.
1. The reply is read into `ModelListReply`. A failed read is not kept.

`find_model` matches the name against the list
([01-decisions.md](01-decisions.md#checking-a-model-before-paying)):

1. It looks for an exact canonical or alias match.
1. On a miss, it reads the kind again once.
1. On a second miss, it looks in the other kinds' lists to name the right
   node.
1. Otherwise it refuses with the closest names.

## How an upscale flows

`UpscaleOperation` ([12-node-upscale.md](12-node-upscale.md)) follows the run
flow with these differences:

- **The sources.** Each `references` item of media `image` is used as is. Each
  local image is uploaded, then imported as an image node with `node create
  image --resource-id <uuid> --import-kind local_upload --submit-id <uuid>`
  (free).
- **The arguments.** `parse_upscale_arguments` checks them against the
  flags `read_command_flags` takes from the schema the version gate read.
- **The call.** One `node upscale image --node-id … --submit-id …
  --credit-ceiling <n>` call covers up to 20 sources, with one submit ID per
  source. It is shielded with `wait_until_settled`, as the run call is.
- **The rest.** Each source's submit ID is recorded, waited on, and collected
  like a generation.

## How a recorded generation is collected

1. Generation: Download lists the records as labels: the short submit ID,
   the model, and the UTC minute.
1. For the chosen record, `CollectOperation` runs the same wait, `node show`,
   and downloads as above, fills every output that has something, and deletes
   the record.
1. A cancel during collection only stops the wait, and the record stays.
1. A record older than `RECORD_RETENTION_SECONDS`, or whose submission
   Dreamina reports `absent`, is deleted with its own message.

## How the person signs in

1. The dialog sends `POST /dreamina/v1/session` with `X-Dreamina-Comfy: 1`.
1. The local route guard checks the connection.
1. `SignInState.create_challenge` runs `auth login` through the private
   `_create_sign_in`, keeps the challenge in memory, and starts a task that
   `SignInState` owns. The task runs `auth wait --device-code … --timeout
   <until the challenge expires>` through the private `_wait_for_sign_in`.
1. The reply holds the user code, the verification link, and the expiry. The
   device code stays on the server.
1. The dialog opens the link and polls `GET /dreamina/v1/status` every two
   seconds until the status reports signed in or the challenge expires.
1. When the wait succeeds, the store clears the account cache, so the next
   paid run reads the new account's token.
1. `DELETE /dreamina/v1/session` runs `auth logout` with `delete_sign_in`.

## How the CLI is installed

1. The dialog sends `POST /dreamina/v1/cli` with `X-Dreamina-Comfy: 1`, after
   the person confirms.
1. `download_installer` downloads the installer for the server's OS from
   `INSTALLER_URLS`, following at most three redirects to ByteDance's CDN.
   Only a final HTTPS address on a CapCut domain is accepted, with a byte cap. The installer is saved to a private
   temporary file.
1. `save_cli` runs the installer:
   - macOS and Linux: `bash <file>`;
   - Windows: `powershell.exe -NoProfile -ExecutionPolicy Bypass -File
     <file>`.

   The server's environment is passed, and the run is bounded by
   `INSTALL_TIMEOUT_SECONDS`.
1. It reads `version` again with `read_cli_version`. The next run checks the
   new binary, because `validate_cli` keys a passed check by the binary's
   path and modification time.
1. The reply holds the new version, or the installer's last lines of error
   output, cut to 300 characters, when it fails.

## Threads, event loops, and subprocesses

F's rules:

- Routes run on the server loop, and nodes on ComfyUI's executor loop. Shared
  stores (`ConfigurationStore`, `GenerationStore`, `CanvasStore`) use
  `threading.Lock`. `SignInState` lives on the server loop only, so it uses
  an `asyncio.Lock`, which can be held across an await.
- Blocking work runs in `wait_for_thread`.
- Every created task has an owner that cancels and awaits it.
- `src/dreamina/models.py`'s shared reads are kept per event loop, as F keeps
  them.

Subprocesses:

- `send_command` uses `asyncio.create_subprocess_exec` on the calling loop.
- On cancel it kills the process and awaits its exit, so no child outlives
  its node. The run call is the one exception: it is shielded, so it always
  finishes and its acceptance is recorded.
- The sign-in wait runs on the server loop, owned by `SignInState`. It is
  canceled when a new sign-in starts or the person signs out. When ComfyUI
  stops, the `auth wait` child ends by itself when the challenge expires.

## Where data lives

| Data                  | Where                                              | Written by             |
| --------------------- | -------------------------------------------------- | ---------------------- |
| Settings              | `<state>/settings.json`                            | Settings route         |
| The canvas            | `<state>/canvas.json`                              | `create_canvas`        |
| Generation records    | `<state>/generations/<submit id>.json`             | `GenerationOperation`, `UpscaleOperation` |
| Model lists           | Memory only, for the life of the process           | `find_model`           |
| The account token     | Memory only, renewed on sign-in and sign-out       | `ConfigurationStore`   |
| A pending sign-in     | Memory only, until it ends or expires              | `SignInState`          |
| Encoded uploads       | A temporary folder, deleted when the uploads end   | `encode_local_file`    |
| Downloads             | A temporary folder, read into memory, then deleted | `download_resources`   |
| Credentials           | The OS credential store, owned by the CLI          | `dreamina-canvas`      |
| The CLI's journal     | The CLI's own state folder                         | `dreamina-canvas`      |

`<state>` is the private state folder in
[01-decisions.md](01-decisions.md#names-and-identifiers).

## IDs other packs use

Checked on 2026-10-16
([01-decisions.md](01-decisions.md#node-id-clashes)). A new node ID must match
none of these:

- **ComfyUI core 0.37.2:** `ByteDance2FirstLastFrameNode`,
  `ByteDance2ReferenceNode`, `ByteDance2ReferenceNodeV2`,
  `ByteDance2TextToVideoNode`, `ByteDanceCreateImageAsset`,
  `ByteDanceCreateVideoAsset`, `ByteDanceFirstLastFrameNode`,
  `ByteDanceImageToVideoNode`, `ByteDanceSeedAudio`, `ByteDanceSeedNode`,
  `ByteDanceSeedreamLayerSeparationNode`, `ByteDanceSeedreamNode`,
  `ByteDanceSeedreamNodeV2`, `ByteDanceSeedreamNodeV3`,
  `ByteDanceTextToVideoNode`, `ByteDanceVideoEnhanceNode`.
- **The owner's packs:** `BytePlus*`, `Fal*`, `OpenRouter*`, and live-shopping's
  node IDs.

None of these matches:

- this pack's `Dreamina<Family><Action>` node IDs;
- `DREAMINA_REFERENCES`;
- `/dreamina/v1/*`;
- the frontend extension `dreamina` and `dreamina.OpenSettings`;
- the install folder `dreamina`.
