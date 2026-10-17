# Owner Rules for the Dreamina Plans

This checklist holds every rule the owner set while building the OpenRouter
pack (`O=/Users/dr_stone/Documents/work/comfyui-openrouter`, commit `c076f37`),
the BytePlus pack (`B=/Users/dr_stone/Documents/work/comfyui-byteplus`, commit
`472cf10`), and the fal pack (`F=/Users/dr_stone/Documents/work/comfyui-fal`,
commit `cef8b6e`). It is for the person who writes and follows the
`comfyui-dreamina` plans. Each line is one rule in plain words, then its
sources, then, where the rule maps to something Dreamina names, a "For
Dreamina" note. [Rules added for Dreamina](#rules-added-for-dreamina) holds
the rules that come from Dreamina's own CLI and skill.

It was written on 2026-10-16 from F's checklist
(`F/plans/research/owner-rules.md`), F's changes table, the three Git
histories, and `rules/`. Nothing is built yet. Tooling details are in
[tooling.md](tooling.md); the CLI facts are in [cli.md](cli.md); the terms and
the rejected routes are in [terms.md](terms.md).

How the sources are cited:

- "Row N" is line N of `B/plans/README.md`, a row of **Changes made while
  building** (lines 218 to 312).
- "O row N" is line N of `O/plans/README.md`, a row of its changes table
  (lines 155 to 204).
- "F row N" is line N of `F/plans/README.md`, a row of its changes table
  (lines 220 to 264).
- "B abc1234", "O abc1234", or "F abc1234" is a commit; read its body with
  `git -C <repo> show abc1234`.
- `rules/<FILE>:N` is line N of that rules file. `B/rules/`, `O/rules/`, and
  `F/rules/` are identical (`diff -rq` found no difference on 2026-10-16).
- Dreamina facts cite the skill mirror under
  `plans/research/docs/dreamina-canvas-cli/`, shortened to `skill/`, by file
  and line, and [cli.md](cli.md) by section. Dreamina plans are linked by
  section.

## Contents

- [Process and plans](#process-and-plans)
- [Requests, inputs, and checks](#requests-inputs-and-checks)
- [Code shape and names](#code-shape-and-names)
- [Messages, comments, and docs text](#messages-comments-and-docs-text)
- [README, ADVANCED, and help pages](#readme-advanced-and-help-pages)
- [Example workflows and notes](#example-workflows-and-notes)
- [Images](#images)
- [Commits and Git](#commits-and-git)
- [Paid requests and live checks](#paid-requests-and-live-checks)
- [Out of scope and rejected](#out-of-scope-and-rejected)
- [Rules added for Dreamina](#rules-added-for-dreamina)
- [rules/ summaries](#rules-summaries)
- [Superseded rules](#superseded-rules)

## Process and plans

- [ ] Port from the reference packs' code, not their plans. Their plans
      describe older designs. (`B/plans/README.md:42-44`,
      `B/plans/01-decisions.md:78-80`, `O/plans/README.md:33-36`,
      `F/plans/README.md:53-56`) For Dreamina: the reference is F at
      `cef8b6e`, which was ported from B and carries every rule set for B and
      O. Name the F source file for every ported file and list the edits
      ([04-architecture.md](../04-architecture.md#port-map),
      [01-decisions.md](../01-decisions.md#what-is-copied-from-fal)).
- [ ] Read the decisions, the API contract, and the architecture plans before
      any other plan. They fix names, API facts, and the file map.
      (`B/plans/README.md:32-35`, `O/plans/README.md:24-27`,
      `F/plans/README.md:41-46`) For Dreamina: [01-decisions.md](../01-decisions.md),
      [02-dreamina-contract.md](../02-dreamina-contract.md), and
      [04-architecture.md](../04-architecture.md).
- [ ] When a plan and a rule disagree, the rule wins, the plan is corrected,
      and the change is recorded in **Changes made while building** with the
      columns Plan, Change, Why. (`B/plans/README.md:38-41`,
      `B/plans/README.md:211-216`, `O/plans/README.md:30-32`,
      `O/plans/README.md:150-151`, `F/plans/README.md:49-52`,
      `F/plans/README.md:213-216`)
- [ ] When two plans disagree, the plan that owns the module wins and the
      other plan is corrected. (Rows 226, 245; `F/plans/README.md:65-70`)
- [ ] Number the steps; a step never depends on a later one. Discovery before
      edits, contracts before callers, data shapes before consumers,
      generated output after its source, cleanup last.
      (`B/plans/README.md:36-37`, `F/plans/README.md:47-48`,
      `rules/PLANNING.md:42-59`)
- [ ] Name every file, declaration, key, command, and asset a step touches.
      No "update as needed" or "fix any errors". For a generated or binary
      file, give the source, output, operation, and size. (`rules/PLANNING.md:16-34`,
      `rules/PLANNING.md:79-95`)
- [ ] Plans contain no automated tests and no test commands. Checks run only
      when the owner asks; the Git hooks run theirs on every commit and push,
      and a failing hook means a missed plan step. (`rules/PLANNING.md:36-40`,
      `rules/GENERAL.md:210-218`, `B/plans/README.md:45-47`,
      `B/plans/01-decisions.md:582`, `F/plans/README.md:57-59`)
- [ ] Plans stay local: `.gitignore` lists `/plans/`, so they are never
      committed, released, or checked by the hooks. (`B/.gitignore:1-2`,
      `B/plans/README.md:52-53`, `O/plans/README.md:45-46`,
      `F/plans/README.md:72-73`) For Dreamina: the `.gitignore` copied from F
      keeps the entry (`F/.gitignore:2`), and `.comfyignore` lists `/plans/`
      too, so the skill mirror under `plans/research/docs/` can never be
      committed or packed.
      **Changed for Dreamina:** the owner asked on 2026-10-17 for the plans
      to be committed. Only `plans/research/docs/` and
      `plans/research/captures/` stay ignored ([../03-repository-setup.md](../03-repository-setup.md)).

- [ ] Keep research in `plans/research/` so it outlives the session. The
      folder check walks the untracked `plans/` folder too, so no research
      folder takes a banned folder name such as `javascript` or `python`.
      (`B/plans/README.md:314-317`, `F/plans/README.md:266-269`, F row 221)
      For Dreamina: the folders `research`, `captures`, `docs`,
      `dreamina-canvas-cli`, and `references` pass
      (`F/quality/config/repository/folders.py:7-18`).
- [ ] Each plan set states its readers, its date, its sources, and that
      nothing is built yet. (`B/plans/README.md:11-17`,
      `B/plans/01-decisions.md:3-6`, `F/plans/README.md:18-26`)
- [ ] The decisions plan ends with the decisions the owner should confirm,
      each with its alternative. (`B/plans/01-decisions.md:584-593`) For
      Dreamina: [01-decisions.md](../01-decisions.md#decisions-the-owner-should-confirm).
- [ ] Each node milestone ships the node, its help page, its example, and its
      README row in one commit; the hooks fail otherwise. Order milestones so
      every example's nodes exist. A node class may be committed
      unregistered and registered later with its example.
      (`B/plans/README.md:99-101`, `O/plans/README.md:74-76`,
      `B/plans/08-requests.md:639-642`, `B/scripts/workflows/build.py:61-71`,
      `F/plans/README.md:120-124`, F row 246)
- [ ] A constant or message arrives with the first milestone that needs it,
      by build order, and a later plan does not add it again. Milestone
      numbers and commit subjects in plans match the build order.
      (Rows 227, 228, 233, 246, 251, 255; F rows 229, 247)
- [ ] Every API fact comes from the vendor's docs, cited by page and line, or
      from a live check. When the brief and the docs disagree, the docs win.
      Check every table row against the docs. (Rows 239, 240, 296;
      `rules/DOCUMENTATION.md:1095-1121`; O row 185) For Dreamina: the
      installed binary is "the source of truth for commands, flags, models,
      and every other executable fact" (`skill/SKILL.md:32-34`), so the
      binary's `schema` wins over the skill ([cli.md](cli.md)).
- [ ] When a live check contradicts the docs, update the contract plan and
      the step it names before building further, and record it.
      (`B/plans/README.md:207-209`, `O/plans/README.md:144-145`, Row 218,
      `F/plans/README.md:209-211`, F rows 236, 258) For Dreamina:
      [02-dreamina-contract.md](../02-dreamina-contract.md) and the open
      questions in [cli.md](cli.md#open-questions).
- [ ] Do not restart or use ComfyUI during the build unless the owner says.
      Read host behavior from the shipped frontend code, mark it "Checked on
      frontend X", and confirm it in the browser with the live checks, in a
      commit of its own. (Rows 232, 261, 267, 286, 288; F rows 234, 248)
- [ ] A node milestone that adds a dynamic dropdown adds its entry to
      `web/scripts/nodes.ts` and rebuilds the bundle; at the Frontend
      milestone the map is empty. (Row 231; `B/plans/README.md:115-117`) For
      Dreamina: no node has a dynamic dropdown
      ([01-decisions.md](../01-decisions.md#browser-code)).
- [ ] Copy tooling with the smallest diff to its source: keep the source's
      key order in `package.json`, and hand-edit the lock's root name. If the
      Semgrep registry serves different content for a pinned pack, copy the
      packs from a sibling pack's local `.artifacts/` that matches the same
      pins, and change no pin. (Rows 223, 224, 230; F rows 220, 227, 233)
      For Dreamina: copy F's tooling at `cef8b6e`
      ([03-repository-setup.md](../03-repository-setup.md)).

## Requests, inputs, and checks

- [ ] An input that sets an API request field takes the field's exact name
      and the API's own values. Nothing is invented: no renamed fields, no
      stand-in values, no node-made schema names or strict modes. (Rows 295,
      296, 297, 298, 300, 301; Row 295 calls it "the owner's rule
      (2026-10-11)"; B c4d6fb5) For Dreamina: `arguments` keys are the flag
      names `model list` returns, each sent as `--<flag> <value>` with
      Dreamina's own value, such as `720P` for `resolution` and `16:9` for
      `ratio` ([cli.md](cli.md#generation-nodes),
      [01-decisions.md](../01-decisions.md#how-the-nodes-cover-every-model)).
- [ ] Use the API's own sentinel values, such as `-1` for "the model
      chooses", never an invented `0`. (Row 298)
- [ ] An input that sets no request field by name keeps its own name.
      (Row 299) For Dreamina: `run_number` sets no flag and keeps its name;
      `credit_ceiling` is the CLI's `--credit-ceiling` in the snake case
      inputs use.
- [ ] Empty sends nothing. A text input left empty, a dropdown at model
      default, and a number at 0 send no field. The only exceptions are the
      spending-safety fields the decisions plan names, which are always sent.
      (Rows 296, 300; O row 190; O 5ea7504;
      `B/plans/08-requests.md:602-605`; `B/src/nodes/video/generate.py:49`;
      `B/plans/01-decisions.md:411-425`) For Dreamina: the named exceptions
      are `--count 1`, sent when the mode has a `count` flag and `arguments`
      does not set it, because the skill asks for one output per node
      (`skill/SKILL.md:157`), and `--credit-ceiling`, without which the CLI
      runs nothing ([cli.md](cli.md#credits)). `--title` is sent only when
      the prompt is empty, because the CLI requires it for a run
      ([01-decisions.md](../01-decisions.md#what-a-run-sends)).
- [ ] The person writes the model's own prompt commands or templates; the
      node does not fill vendor templates with text it chose, and adds only
      what the node must (such as the output format). (Rows 300, 301) For
      Dreamina: the only change to the prompt rewrites the pack's own
      placeholders (`{{image1}}` and the like) to the CLI's `{{res:…}}` and
      `{{node:…}}` forms ([01-decisions.md](../01-decisions.md#placeholders)).
- [ ] No local copy of a check the API makes for free. Refuse locally only
      what the API would bill or silently ignore. (Row 305; B b0c86b1;
      B 6fa1c0d; O row 202; `B/plans/01-decisions.md:249-254`) For Dreamina:
      a refusal after the save leaves a saved draft on the canvas, and the
      live `model list` holds every constraint, so the pack checks flags,
      values, and reference limits by reading the fields the list returned,
      and copies no rule of its own
      ([01-decisions.md](../01-decisions.md#checking-a-model-before-paying)).
- [ ] No guards, fallbacks, retries, or defaults for states that cannot occur.
      (Rows 278, 283; `rules/GENERAL.md:68-79`)
- [ ] Send each request once: no retries, no fallbacks, no invented limits,
      no parallel cap of the pack's own. The run number is the only way to
      send the same request again. (O 2047b6b; O row 180;
      `B/plans/01-decisions.md:376-387`, `B/plans/01-decisions.md:496-497`;
      `B/plans/08-requests.md:638`) For Dreamina: the run call is never
      retried. A lost reply is checked read-only with the same submit ID,
      because the skill says "do not replay the run"
      (`skill/references/recovery-and-idempotency.md:30`). Status reads,
      uploads, and downloads are free and are tried again within the request
      timeout ([01-decisions.md](../01-decisions.md#paid-runs)).
- [ ] A person types any model ID. Check it before paying against the
      vendor's own listing where one exists; keep no copy of the vendor's
      list to maintain. (O row 190; O 5ea7504; Row 218; Row 263) For
      Dreamina: the person's own `model list --type <kind>`, read live, and
      matched on the canonical `model` or an alias; the skill says "never
      select the first item by default" (`skill/SKILL.md:58-62`,
      `skill/SKILL.md:90`).
- [ ] Seeds start **fixed**, so queueing a workflow again never sends a new
      paid request by itself. (`B/plans/01-decisions.md:383-387`)
- [ ] One request timeout for every node; no identical-request logic. Every
      run sends one new job; a Download node collects an earlier one.
      (O 6340e4a; O row 192) For Dreamina: one request timeout, from the
      first upload to the last download; **Generation: Download** collects a
      recorded generation ([01-decisions.md](../01-decisions.md#paid-runs)).
- [ ] Record a long job as soon as the vendor accepts it, before the first
      wait. A cancel cancels a queued job; a running one is collected later.
      (`B/plans/01-decisions.md:388-396`; Rows 272, 275; F row 253) For
      Dreamina: Dreamina has no cancel for an accepted generation, and
      deleting the node neither stops nor refunds it
      (`skill/references/node-deletion.md:15-16`). A ComfyUI cancel stops
      only the wait; the record stays, and **Generation: Download** collects
      the generation ([01-decisions.md](../01-decisions.md#paid-runs)).
- [ ] Each request uploads its own local files; nothing is remembered between
      requests. (F row 262) For Dreamina: each run uploads its media with
      `resource upload` and deletes the temporary files after the run
      ([01-decisions.md](../01-decisions.md#local-media)).
- [ ] Each media kind is one list socket, and everything connected goes in
      one request. No invented socket counts. (O row 201; O 8288141) For
      Dreamina: `images`, `videos`, `audio`, and `references`
      ([01-decisions.md](../01-decisions.md#the-inputs-of-a-paid-node)).
- [ ] Leave out a control that offers no choice. (O row 179; O 64648d7)
- [ ] Return what an input asks for; do not drop requested parts of a reply.
      (O row 182) For Dreamina: `result` returns every part of `node show`
      that has no socket ([01-decisions.md](../01-decisions.md#outputs)).
- [ ] A node's defaults make its default model work. (O row 193) For
      Dreamina: the default `credit_ceiling` is the default model's quote at
      its defaults, rounded up to the next multiple of 10
      ([01-decisions.md](../01-decisions.md#credits)).
- [ ] Map each documented vendor error to its own message; keep the vendor's
      reason for every other status. (O rows 185, 203;
      `B/plans/01-decisions.md:433-451`) For Dreamina: the map reads the exit
      code and `error.code`, `class`, `requiredAction`, `reason`,
      `retryable`, and `validation`, never message text: "Branch on
      structured fields and exit classes, never localized message text"
      (`skill/SKILL.md:324`).
- [ ] Handle failures at the user-input boundary with a reviewed message.
      (Row 264; `rules/GENERAL.md:74-75`)
- [ ] Count sizes in the vendor's units. (Row 309)
- [ ] Build every request body before the first paid request, so a refusal
      comes before anything is billed. (Row 279; `B/plans/08-requests.md:606-608`)
      For Dreamina: the model, mode, flags, and reference limits are checked
      before the first upload, and the one `node create … --run` call comes
      last ([04-architecture.md](../04-architecture.md#how-a-paid-run-flows)).
- [ ] Add no Python dependency and no vendor SDK; never use ComfyUI's
      API-node request helpers. (`B/plans/01-decisions.md:484-488`,
      `B/plans/01-decisions.md:503-505`) For Dreamina: the CLI is a program
      the person installs with ByteDance's installer, never a Python
      dependency and never bundled
      ([01-decisions.md](../01-decisions.md#the-cli-on-the-persons-computer)).

## Code shape and names

- [ ] One implementation per concept: no parallel paths, no forwarding
      wrappers, one record per reply shape, one transport per verb.
      (`rules/GENERAL.md:81-94`; Rows 241, 256, 263, 270, 277, 283, 306;
      B 8aaaa56; O rows 176, 177) For Dreamina: every CLI call goes through
      one function in `src/dreamina/cli.py`
      ([01-decisions.md](../01-decisions.md#subprocesses-and-concurrency)).
- [ ] Internal names use the vendor's vocabulary. (Row 307; B 79e056f) For
      Dreamina: one paid run is a **generation**, named by its **submit ID**;
      its state is read as an **operation** (`operation status` and
      `operation wait <submitId>`); the pack's work lives on a **canvas** as
      Dreamina **nodes**, whose outputs are **resources**; a recurring
      character, product, or place is an **Element**
      ([cli.md](cli.md#operations-and-recovery), [cli.md](cli.md#canvases),
      [cli.md](cli.md#resources-upload-and-download),
      [cli.md](cli.md#elements)). So records are generation records keyed by
      submit ID, not requests or jobs.
- [ ] Keep the vendor's exact spelling for its own names. A banned word in a
      vendor name gets a narrow naming exception, limited to that name and
      path, with a reason, and only with the owner's authorization. (Rows
      302, 307; `rules/NAMING.md:37-46`; `rules/NAMING.md:440`; O row 155: a
      rule's `path_regexes` must all match, so one exception per folder;
      F rows 232, 245) For Dreamina: the CLI uses the banned words `data`,
      `service`, `bind`, `resolution`, `catalog`, `info`, `fetch`, and
      `smart` ([01-decisions.md](../01-decisions.md#banned-words-that-shape-names)).
      `DreaminaError` and `X-Dreamina-Comfy` hold none, so the only expected
      exception is F's `ModelInfo` one.
- [ ] Avoid banned words in local names; give a banned wire field a Pydantic
      alias. (Rows 266, 306; O rows 173, 181; `B/plans/01-decisions.md:534-553`;
      F row 239) For Dreamina: `payload` for `data`, `status_code` for
      `serviceCode`, and `subjects` for `subjectBindings`, each with
      `Field(alias=…)`; Model: Info's helpers and messages say "report", as
      F's do ([01-decisions.md](../01-decisions.md#banned-words-that-shape-names)).
- [ ] Start every function with a verb from the table in `rules/NAMING.md`,
      used with its meaning, or `is_`/`has_`. A name never repeats a word.
      (`rules/NAMING.md:221-261`; O 97e4cc6; O 14fbdb1; O row 195; Row 257;
      F row 240) For Dreamina: the table has no `run`, `check`, `install`,
      or `upload`, and `ensure` is banned, so the CLI calls are
      `send_command`, `validate_cli`, `download_installer`, `save_cli`,
      `create_sign_in`, `delete_sign_in`, `send_media`, `plan_references`,
      `format_prompt`, `find_canvas`, and `create_canvas`
      ([04-architecture.md](../04-architecture.md#srcdreamina)). A new verb
      needs `functions.json` and the protected `rules/NAMING.md`, so it needs
      the owner.
- [ ] Private functions come first and are never exported; a function only
      its module uses is private. A public function no other module names yet
      gets an exact `functions.json` allowlist entry, removed with its first
      call. (O row 195; O 7f7d0b0; Rows 220, 225, 235, 243, 244, 252, 272,
      284; `B/plans/08-requests.md:645-659`; F rows 225, 228, 237, 238, 242)
- [ ] A function of one or two statements is inlined (`python.trivial-function`).
      (Rows 237, 257, 263, 271, 279, 284; O rows 157, 174; F rows 242, 245)
- [ ] Keep each function at Ruff complexity 8 or less, five arguments or
      fewer, and four returns or fewer; keep each module at 300 lines or
      less. (Rows 237, 243, 257, 273; F rows 239, 242)
- [ ] A package of one module is flattened (`python.single-file-package`); a
      docstring-only stub module may hold a package until its plan fills it.
      A check's own exemption list may hold a temporary entry.
      (Rows 221, 222, 234, 276; `rules/NAMING.md:388-390`) For Dreamina:
      `src/nodes/generate.py` and `scripts/workflows/descriptions/notes.py`
      start as docstring-only stubs
      ([03-repository-setup.md](../03-repository-setup.md#step-8-create-the-skeleton)).
- [ ] Internal constants take a leading underscore; module values are
      tuples, not lists; frozen records hold no `dict`. (Rows 243, 258, 270,
      273; `rules/PYTHON.md:462`)
- [ ] No public single-letter type variables; abstract collection types for
      arguments; narrow with `isinstance`, not casts; type aliases stay out of
      `__all__`. (Rows 238, 270; O rows 162, 163, 164)
- [ ] A docstring summary fits one 120-character line; a longer one is a
      summary line and a second paragraph. Every module has a docstring. A
      config exception carries a comment with its reason. (Rows 236, 242,
      247, 271; F rows 225, 238)
- [ ] Every fixed value lives in config. Related values are one dict with
      uppercase keys; wire names, headers, and setting names keep their
      spelling; each parameter has its comment directly above it. Patterns
      are compiled once from config. (O a17723e; O 67c32de; O row 194;
      `rules/PYTHON.md:1464-1465`; F row 229)
- [ ] Name no config key `TOKEN`: Bandit's hardcoded-password check flags
      such a key even when it holds an address. (F row 231) For Dreamina:
      the device code and the sign-in link are reply fields read at run
      time, never config keys.
- [ ] `src/` holds only packages; records and errors are one `types`
      package; the `Extension` class is in the package `__init__.py`.
      (O rows 191, 194; O f8691e5; O eed6510)
- [ ] Delete code, fields, and constants that nothing reads or that change
      nothing. (Rows 308, 312; O rows 158, 161, 175, 178, 186; B 1242144;
      B 673862b; B 6fa1c0d; `rules/GENERAL.md:347-361`; F row 247)
- [ ] Define each shared node ID and model ID once in the workflow
      descriptions. (Row 312; B fb25672; O row 196)
- [ ] Every output's label equals its ID, because examples and help pages
      name outputs that way. (Row 274; O row 167; `B/plans/08-requests.md:591-592`)
- [ ] Custom socket types carry the vendor prefix so they cannot collide with
      another pack. (O 179ec23; `B/plans/01-decisions.md:214-226`) For
      Dreamina: `DREAMINA_REFERENCES`
      ([01-decisions.md](../01-decisions.md#the-nodes)).
- [ ] Node IDs are the prefix plus the class name; display names are
      `Family: Action`, with no pack suffix and no `search_aliases`. Check new
      IDs against ComfyUI core and other packs; IDs never change after the
      first release. (`B/plans/01-decisions.md:135-161`) For Dreamina:
      `Dreamina<Class>`, checked on 2026-10-16 against core's 16
      `ByteDance*` IDs and the Registry's Jimeng and Seedance packs
      ([01-decisions.md](../01-decisions.md#node-id-clashes)).
- [ ] Inputs show their snake_case names, as ComfyUI's own nodes do, and
      every tooltip, message, help page, and note names them that way. Text
      boxes come last. A setting's key and label agree; setting labels use
      sentence case; the menu entry and dialog title read "<Vendor> Settings".
      (B 084ba64; O 179ec23; O rows 198, 200) For Dreamina: **Dreamina
      Settings**, at **Extensions → Dreamina → Dreamina Settings**
      ([01-decisions.md](../01-decisions.md#names-and-identifiers)).
- [ ] Keep host and framework names exact and follow the current ComfyUI;
      a Download node's `validate_inputs` takes `**inputs` so ComfyUI skips
      its list check. (O rows 165, 166, 170; O ab3fa59; O 1749aac;
      `rules/GENERAL.md:363-365`) For Dreamina: **Generation: Download**.
- [ ] Keep CodeQL clean by fixing code, and keep bundled third-party code out
      of the scan; host imports only in the files the ESLint rule allows.
      (O rows 156, 168)
- [ ] No logging, prints, warnings, or stack traces anywhere.
      (`rules/GENERAL.md:170-184`; `B/plans/01-decisions.md:451`;
      `B/plans/05-foundation.md:70`)
- [ ] The key is read from the vendor's environment variable first, then the
      private credential file; it is never a widget, in a workflow, in a
      message, or sent to the browser. (`B/plans/01-decisions.md:356-374`;
      `rules/GENERAL.md:162-168`) For Dreamina: no API key exists. The CLI
      owns sign-in: its device authorization keeps the credentials in the OS
      credential store, and the pack never reads, stores, or sends them. So
      the pack has no key widget, no credential file, and no key variable,
      and no credential reaches a workflow, a message, or the browser
      ([01-decisions.md](../01-decisions.md#sign-in-and-privacy),
      [cli.md](cli.md#sign-in)).
- [ ] No compatibility layers, aliases for renamed symbols, or dual paths.
      (`rules/GENERAL.md:347-365`)

## Messages, comments, and docs text

- [ ] All project text conforms to ISO 24495-1:2023 plain language: readers
      can get, find, understand, and use the information. This covers
      READMEs, help pages, comments, docstrings, tooltips, labels, errors,
      notes, and generated text. (`rules/WRITING.md:3-12`,
      `rules/DOCUMENTATION.md:39-47`)
- [ ] Short sentences, one idea each; split long comments, docstrings,
      tooltips, messages, and notes. (B 6fa1c0d; B 1242144; O 8dd4de3;
      `rules/WRITING.md:14-15`; `rules/DOCUMENTATION.md:745-753`)
- [ ] A message is a constant in `src/config/messages/`: a complete sentence,
      second person and imperative, starting with a capital letter, saying
      what to do and where. (`B/plans/01-decisions.md:438-439`;
      `B/plans/05-foundation.md:79-81`; Row 258; `rules/GENERAL.md:203-208`)
- [ ] Messages leak no internal names, IDs, paths, or stack traces.
      (`rules/GENERAL.md:186-201`)
- [ ] Comments and docs describe the present state only; no history.
      (`rules/GENERAL.md:232-239`)
- [ ] Comments say why, not what. Drop comments that restate the code; keep
      a docstring while true and rewrite it when the behavior differs.
      (O 140b79a; B 3ddcfdf; Row 229; `rules/GENERAL.md:264-283`)
- [ ] Tooltips and notes state what a thing does. (O 2c956bd; O 7a033f6)
- [ ] No em dashes or double hyphens as punctuation; serial comma; split a
      sentence instead of a semicolon. (`rules/GENERAL.md:250-257`,
      `rules/DOCUMENTATION.md:1001-1012`)
- [ ] US English. (Row 260; `rules/DOCUMENTATION.md:733-738`)
- [ ] Write the currency name on first use: "30 US dollars", not "USD 30".
      (Row 292; `rules/DOCUMENTATION.md:901-924`)
- [ ] Use the same name for the same thing, and use the vendor's own names
      for its products and pages. Two config names never share a name with
      two meanings. (`rules/WRITING.md:15`; Row 311; B 6fa1c0d; O cf306a1;
      `rules/DOCUMENTATION.md:979-992`; F row 241) For Dreamina: Dreamina
      writes its name "Dreamina", and the program is the **Dreamina Canvas
      CLI**, `dreamina-canvas`
      ([01-decisions.md](../01-decisions.md#why-the-cli)).
- [ ] Title case for H1 titles, workflow titles, and note titles; sentence
      case for H2 and lower, table headers, labels, tooltips, and note text.
      (`rules/DOCUMENTATION.md:926-964`)
- [ ] Spell out zero to nine; numerals from 10. No promotional words.
      (`rules/DOCUMENTATION.md:864-879`, `rules/DOCUMENTATION.md:661-694`)
- [ ] Do not invent commands, fields, environment variables, defaults, or
      timings. State an observation as one, not as a guarantee; drop a claim
      that was never measured. A message states only what the vendor
      documents. (`rules/DOCUMENTATION.md:1109-1132`; Row 285; F row 230)
      For Dreamina: commands and flags come from the installed release's
      `schema`; `DREAMINA_CLI_CALLER_AGENT` stays unset because the skill
      does not document it ([cli.md](cli.md#hosts-and-telemetry)).
- [ ] Say each thing once; list shared checks once. (Row 310; B 872e2ca;
      B 029e93f; O ba4304a; `rules/DOCUMENTATION.md:99-132`)
- [ ] Docs match the code: correct every fact against the code and the
      vendor's docs in the same change. (B 872e2ca; B 029e93f; O 8d973c7;
      Rows 292, 309, 310; `rules/DOCUMENTATION.md:72-73`,
      `rules/DOCUMENTATION.md:134-136`; F row 259)
- [ ] Cut what ComfyUI users already know, and drop lines about what the
      extension is not or does not do. (O 3527330; O ba4304a; Row 303)
- [ ] No prices, costs, or amounts of money in nodes, tooltips, notes, help
      pages, README, or ADVANCED. "Billed" may appear where the person needs
      it. (`B/plans/01-decisions.md:409-410`; O eae61f1; O 584eb10; O row 198;
      `B/plans/17-scripts-and-workflows.md:324-325`) For Dreamina: the word
      "credits" appears where the person needs it, as "billed" does; the only
      number of credits the pack shows is Dreamina's own quote
      (`minimumCreditCeiling`) in the over-ceiling refusal
      ([01-decisions.md](../01-decisions.md#credits)).
- [ ] Leave the vendor's account conditions to the vendor's docs; write
      requirements as plain sentences. (B 61e08d8) For Dreamina: the README
      says the account must be able to use the Dreamina Canvas CLI and leaves
      plan details to Dreamina's pages. The CLI page reads "Private beta ·
      Advanced subscribers only", yet the owner's Standard account passed the
      gate ([catalog.md](catalog.md#account),
      [01-decisions.md](../01-decisions.md#why-the-cli),
      [terms.md](terms.md#2-what-bytedance-publishes-for-software)).
- [ ] Keep private reasoning, acceptance status, run records, and machine
      paths out of public text. (`rules/WRITING.md:19-21`,
      `rules/DOCUMENTATION.md:3838-3843`)

## README, ADVANCED, and help pages

- [ ] README and ADVANCED take the reference packs' section shapes and
      lengths, with nothing beyond them. (Rows 291, 303, 310;
      `B/plans/01-decisions.md:517-519`) For Dreamina: F's `README.md`
      (203 lines) and `ADVANCED.md` (546 lines) at `cef8b6e` set the shapes
      and lengths ([01-decisions.md](../01-decisions.md#documentation-notes-and-examples)).
- [ ] Each help page is no longer than the matching reference page and has
      its shape. (Rows 254, 259, 265, 269, 280, 285) For Dreamina: F's pages
      in `F/web/docs/`, paired as [04-architecture.md](../04-architecture.md#port-map)
      pairs the nodes: `FalImageGenerate.md` (44 lines), `FalVideoGenerate.md`
      (50), `FalAudioGenerate.md` (46), `FalRequestDownload.md` (37),
      `FalModelInfo.md` (65), and `FalFileAdd.md` (35) for Element: Add.
      Image: Upscale has no F node and takes Image: Generate's page as its
      reference.
- [ ] The README opens with the banner as its H1, then the reference packs'
      one-sentence purpose. (Row 303; O row 199; O eae61f1; O f7ae905;
      O 413e310; O row 197) For Dreamina: the purpose sentence names the pack
      as a ComfyUI extension that runs Dreamina models
      ([01-decisions.md](../01-decisions.md#names-and-identifiers)).
- [ ] No bullet list above the README contents; the node table carries it.
      (B 084ba64; O 179ec23; replaces Row 253, which wrote the bullets once,
      complete, in the Documentation milestone)
- [ ] One example workflow table in the README; every example is linked
      from it. (O row 199; `B/scripts/workflows/build.py:61-67`)
- [ ] No bold labels as small headings. (Row 291;
      `rules/DOCUMENTATION.md:2155-2165`)
- [ ] No project layout or file map sections. (`rules/DOCUMENTATION.md:284-308`)
- [ ] One help page per node at `web/docs/<node id>.md`; inputs in node
      order; text wrapped at 80 columns; JSON blocks in Prettier's form.
      (`B/plans/08-requests.md:639-642`; O eae61f1; Row 252) For Dreamina:
      `web/docs/Dreamina<Class>.md`.
- [ ] A help page, note, or guide names only nodes and workflows already
      shipped; a page's "Example:" line arrives with its example. (Rows 250,
      259, 265)
- [ ] List each node's checks the way the code makes them. (B 029e93f;
      Row 310)
- [ ] `ADVANCED.md` is written in the Documentation milestone; no plan
      before it edits it. (Rows 251, 266)
- [ ] Docs follow the example plan when examples change. (O rows 171, 184)

## Example workflows and notes

- [ ] Examples are scenario workflows that solve a real task with the
      newest models for the job; every node appears in at least one.
      (O row 183; O 459bbd3; `B/scripts/workflows/build.py:61-71`)
- [ ] Name examples by family, two-digit number, and task, such as
      `image-01-design-a-character`. (`rules/NAMING.md:856-858`)
- [ ] Each step after the inputs is a subgraph with named inputs and
      outputs. (O row 188; O f59dc04)
- [ ] Every subgraph ships as a blueprint in `subgraphs/`, named after its
      step alone; the build refuses two different subgraphs with one name.
      (B 5bd4ada; O cdf0613; `B/scripts/workflows/build.py:161`)
- [ ] Each group's note sits above its frame, as wide as the frame.
      (B 20532df; O 48a6750)
- [ ] The first note is **Start Here**, in steps only: step 1 is the key
      step, the next steps say what to type or choose, the last is "Press
      **Run**." and where the result is saved. (Row 289;
      `B/plans/17-scripts-and-workflows.md:313-316`;
      `B/scripts/workflows/descriptions/notes.py:3`) For Dreamina: step 1 is
      the sign-in step: "1. Sign in to Dreamina in **ComfyUI menu →
      Extensions → Dreamina → Dreamina Settings**."
      ([01-decisions.md](../01-decisions.md#documentation-notes-and-examples)).
- [ ] Every other note says what the step does, which model does it, and
      what to change, in two short paragraphs at most. A subgraph
      description is one sentence starting with a verb.
      (`B/plans/17-scripts-and-workflows.md:319-321`)
- [ ] A note on a long job's step says what a cancel does, matched to the
      live run; a recover note turns off the steps that would bill again.
      (`B/plans/17-scripts-and-workflows.md:327-329`; Row 289; B 1242144;
      F row 253) For Dreamina: a cancel stops the wait, the generation keeps
      running and is billed, and **Generation: Download** collects it
      ([01-decisions.md](../01-decisions.md#paid-runs)).
- [ ] Name a model or product plainly, and introduce it once.
      (O 2b6efe3)
- [ ] Notes are sized to their text; no giant background notes.
      (`rules/DOCUMENTATION.md:3828-3831`; O 459bbd3)
- [ ] Settings come from the node plan; values are set only when they
      differ from the default; media inputs ship empty; save prefixes are
      `<kind>/<vendor>/<name>`. (Row 260;
      `B/plans/17-scripts-and-workflows.md:384-390`) For Dreamina:
      `image/dreamina/<name>`, `video/dreamina/<name>`, and
      `audio/dreamina/<name>`. Dreamina's default can be the expensive
      setting, so an example sets the cheaper value explicitly
      ([01-decisions.md](../01-decisions.md#choosing-a-model)).
- [ ] Use a format the host save node offers. (O row 170)
- [ ] Node sizes are measured in the page, not guessed. (O row 172;
      Rows 286, 288)
- [ ] When a model decides the image count from the prompt, the prompt says
      the number. (Rows 262, 304; B 69c2cd6; B 16e00fc) For Dreamina: the
      pack sends `--count 1` unless `arguments` sets `count`, so an example
      that wants several outputs sets `count` and says the number in the
      prompt.

## Images

- [ ] The image set is the reference packs': four badges, the banner, the
      node map, and three screenshots; no extra icon or social preview file.
      (Row 293) For Dreamina: F's set, with the logo as the Registry icon
      ([01-decisions.md](../01-decisions.md#brand-and-images)).
- [ ] The pack has its own look: a node-tile logo, a banner of sockets,
      badges as pills, and a node map with one card per kind of node and
      marks for paid and free nodes. The Registry icon is the logo.
      (B fc461b2; `B/pyproject.toml:164`)
- [ ] The images use the family design the BytePlus, OpenRouter, and Reactor
      packs share, styled in the vendor's colors, with a mark of the pack's
      own and no other pack's icon. The vendor's own logo is never used.
      (F rows 263, 264) For Dreamina: a redrawn four-point star in
      Dreamina's gradient with the family's yellow socket, and the banner
      title "Dreamina"
      ([01-decisions.md](../01-decisions.md#brand-and-images)).
- [ ] Images sit in `docs/images/badges/`, `brand/`, `diagrams/`, and
      `screenshots/`, with plain kebab-case names. (B 472cf10; O c076f37;
      `rules/DOCUMENTATION.md:2642-2646`)
- [ ] Badges are neutral and sit under the banner; no colored tags or
      result collage. (O row 204; O row 197; O 48bf922;
      `rules/DOCUMENTATION.md:3697-3708`)
- [ ] Screenshots are DevTools captures cropped to the element, in a window
      1,000 pixels tall, reduced to 256 colors without dithering, each under
      100 KB, with alt text. (Row 294; `B/plans/18-documentation.md:921`;
      `rules/DOCUMENTATION.md:2652-2656`; F row 259 took them in headless
      Chrome through Playwright when the DevTools browser tool had no Chrome
      to attach to)
- [ ] Retake a screenshot when a label it shows changes; alt text names the
      inputs in node order. (Rows 298, 310; B 084ba64;
      `B/plans/18-documentation.md:347`; `rules/DOCUMENTATION.md:3129-3143`)
- [ ] Node map arrows are all solid and consistent; card text must fit its
      card. (O row 204; Row 311)

## Commits and Git

- [ ] Commit messages are `type(scope): lowercase subject`. The scope is one
      of `nodes`, `frontend`, `workflows`, `docs`, `hooks`, `quality`,
      `root`, `deps`; the scope may not be empty; the header is at most 120
      characters, the subject 100. The `commit-msg` hook enforces it.
      (`B/quality/config/repository/commitlint.json:4-15`;
      `B/plans/README.md:48-50`; `B/.githooks/commit-msg:12`;
      `F/plans/README.md:60-62`)
- [ ] The body says what changed and why, in plain sentences, wrapped near
      72 columns. (B 5bd4ada, B 084ba64, B b0c86b1 as examples)
- [ ] Commit at each milestone with the subject the build order gives. A
      large milestone may be committed in parts, each passing the hooks.
      (`B/plans/README.md:99`; Row 228; F row 237) For Dreamina: the
      Tooling commit is `build(quality): bring in the repository tooling`
      ([03-repository-setup.md](../03-repository-setup.md#step-10-first-commit)).
- [ ] A live-check fix, a browser re-measurement, or an example-run fix is
      a commit of its own. (Rows 261, 267, 290; F row 260)
- [ ] Push every commit as soon as it is made, so every commit must pass the
      pre-push check; that is why each node arrives with its help page,
      example, and README row. (F rows 226, 246) This replaces "Do not push
      while the pre-push check would fail between milestones"
      ([Superseded rules](#superseded-rules)).
- [ ] Pin dependencies past audit advisories, with full commit hashes OSV
      can read. After any `bun add` or `bun remove`, restore the braces
      override's full commit hash in `bun.lock`. (O 1b95cd3; O b167219;
      B 6d7af22; F rows 227, 233)
- [ ] The owner decides when to publish and runs the publish step;
      `pyproject.toml` has no `PublisherId` until then. (O row 189;
      `B/plans/19-release.md:8-10`, `B/plans/19-release.md:28-30`,
      `B/plans/19-release.md:233-237`) For Dreamina: the Registry ID
      `dreamina` ([20-release.md](../20-release.md#one-time-setup)).
- [ ] Do not edit `AGENTS.md`, `CLAUDE.md`, or `rules/` unless asked.
      (`rules/GENERAL.md:329-332`; `B/AGENTS.md:6`)
- [ ] Do not revert or overwrite changes you did not make.
      (`rules/GENERAL.md:367-377`)
- [ ] No hosted Git workflows or deployment tooling; hooks never install
      packages. (`rules/GENERAL.md:217-218`; `rules/BASH.md:1701-1709`)

## Paid requests and live checks

- [ ] Send paid requests only within the scope the owner authorizes. Ask
      before the first one and state its cost. (`B/plans/README.md:165-168`;
      `O/plans/README.md:124-127`; `rules/PYTHON.md:2639-2641`;
      `F/plans/README.md:63-64`, `F/plans/README.md:190-198`; F row 250)
      For Dreamina: the cost is Dreamina credits, stated from Dreamina's
      quote. The skill also stops for the user when the server requires
      credit approval (`skill/SKILL.md:305-315`).
- [ ] A runtime check never authorizes buying credits, turning on top-ups,
      or changing account settings. (`rules/PYTHON.md:2639-2641`) For
      Dreamina: nor changing the plan, signing in another account, or
      approving with `--yes`.
- [ ] The plans README holds a table of first runs per milestone with costs;
      prices appear only in plans. (`B/plans/README.md:163-209`;
      `O/plans/README.md:122-145`; `F/plans/README.md:190-211`) For
      Dreamina: the costs are in credits.
- [ ] Record every live run's result in the changes table. (Rows 218, 262,
      268, 275, 281, 287, 304; F rows 236, 248, 253, 257, 258, 261)
- [ ] Before a node's first paid run, test its path outside ComfyUI with a
      request that bills nothing. (F row 243) For Dreamina: free reads, and
      a run that stops at its ceiling, which charges nothing and leaves a
      saved draft node on the canvas
      (`skill/references/credits-and-hitl.md:48-49`).
- [ ] Check every paid run in the vendor's own history, not only in
      ComfyUI's: another session can restart the shared ComfyUI and lose
      ComfyUI's record. (F row 254) For Dreamina: the `ComfyUI` canvas at
      dreamina.capcut.com, or a read-only `operation status <submitId>`
      ([01-decisions.md](../01-decisions.md#the-canvas)).
- [ ] Do not change the account to provoke one error message; the error map
      covers it. (Row 248)
- [ ] Build nodes before their live check only with the owner's approval.
      (Row 282)
- [ ] Run each example once, with the owner's approval and the costs stated,
      separately from the Documentation commit; then compare the vendor's
      usage page. (Rows 290, 304; `B/plans/17-scripts-and-workflows.md:1112-1148`;
      F row 261 queued each prompt through ComfyUI's own `app.graphToPrompt()`,
      so subgraphs expand as **Run** expands them) For Dreamina: compare
      each run with its node on the `ComfyUI` canvas.
- [ ] Keep run records private. (`rules/PYTHON.md:2641`;
      `rules/PYTHON.md:2646-2651`)

## Out of scope and rejected

- [ ] No spending caps, budget guards, usage limits, spending warnings, or
      key restrictions, in code or docs. (Row 249;
      `B/plans/01-decisions.md:426-428`) For Dreamina: `credit_ceiling` is
      not a pack-made spending cap. It is the CLI's own `--credit-ceiling`
      approval, which Dreamina requires before any run, under its own name
      ([01-decisions.md](../01-decisions.md#credits),
      [cli.md](cli.md#credits)). The pack adds no other cap, no spending
      warning, and no balance section.
- [ ] No prices or price estimates. (O row 169, later removed with the
      models dialog in O 682dea8; O eae61f1) For Dreamina: `node quote`
      stays unused ([cli.md](cli.md#commands-the-pack-does-not-use)).
- [ ] No bundled copy of the vendor's model list when a listing can be read.
      (O row 190; Row 218) For Dreamina: no bundled CLI either
      ([01-decisions.md](../01-decisions.md#the-cli-on-the-persons-computer)).
- [ ] No account management in the pack. (`B/plans/01-decisions.md:580-581`)
      For Dreamina: **Sign in** and **Sign out** run the CLI's own `auth
      login`, `auth wait`, and `auth logout`, as F's dialog saves and clears
      a key; the pack manages no account, plan, or credits
      ([01-decisions.md](../01-decisions.md#sign-in-and-privacy)).
- [ ] No automated tests and no logging. (`B/plans/01-decisions.md:582`;
      `rules/GENERAL.md:170-176`)
- [ ] No search or compare presets, instruction templates, or renamed
      model commands. (Rows 300, 301)
- [ ] No identical-request block, uncertain job records, or request hashing.
      (O 6340e4a)
- [ ] No code that changes nothing, such as relabeling widgets ComfyUI
      already labels. (Row 308)
- [ ] O row 159 (drop a bad price line alone) and O row 160 (`is_bundled`)
      belong to the bundled model list O later removed (O row 190); nothing
      carries over.

## Rules added for Dreamina

These rules come from Dreamina's CLI, its skill, and its terms. The owner's
rules above apply to them as to any vendor rule.

- [ ] Talk to Dreamina only through the person's installed `dreamina-canvas`
      binary, run as a subprocess with `--format json --non-interactive`.
      The pack sends no HTTP request to any Dreamina or CapCut host itself.
      ([01-decisions.md](../01-decisions.md#why-the-cli),
      [terms.md](terms.md#3-how-the-pack-stays-inside-the-published-route))
- [ ] Never call an undocumented endpoint or build a raw HTTP request. Use
      only the commands, flags, and fields that `schema`, `model list`, and
      `voice list` return for the installed release. ("Do not call
      undocumented endpoints or synthesize raw HTTP requests.",
      `skill/SKILL.md:364`; `skill/SKILL.md:353-355`;
      [terms.md](terms.md#3-how-the-pack-stays-inside-the-published-route))
- [ ] Never pass `--yes`, never answer a prompt, and always pass
      `--non-interactive`. `--yes` "Approves any amount"; every paid run
      takes the person's `credit_ceiling` instead. (`skill/SKILL.md:317-320`;
      `skill/references/credits-and-hitl.md:27-29`,
      `skill/references/credits-and-hitl.md:47`;
      [01-decisions.md](../01-decisions.md#the-cli-on-the-persons-computer))
- [ ] Never delete a canvas node. Deleting needs the person's explicit
      approval of each batch, so the person deletes on the canvas, and a
      draft left at the ceiling stays; ADVANCED says so.
      (`skill/references/node-deletion.md:40-43`,
      `skill/references/node-deletion.md:82-84`;
      [01-decisions.md](../01-decisions.md#credits))
- [ ] Always pass `--project-id` with the pack's own `ComfyUI` canvas. Never
      read or change the CLI's current canvas, and never pass `canvas create
      --use`. ("An explicit `--project-id` avoids reading the current-canvas
      record", `skill/references/authentication.md:7`;
      [cli.md](cli.md#canvases); [01-decisions.md](../01-decisions.md#the-canvas))
- [ ] Never keep a token or a device code. The pack keeps only public IDs:
      canvas, node, submit, and resource. It stores no access token, signed
      link, credit token, or device code, in a file, a log, or a message.
      ("Do not store access tokens, signed URLs, provider payloads, temporary
      download material, or credit-confirmation tokens.",
      `skill/SKILL.md:301-303`; `skill/SKILL.md:362-363`;
      [01-decisions.md](../01-decisions.md#records-and-state),
      [04-architecture.md](../04-architecture.md#how-the-person-signs-in))
- [ ] Never put the creative-skill contents of the Dreamina skill anywhere:
      not in code, prompts, notes, help pages, the README, ADVANCED, plans, or
      research. The skill marks its creative guidance confidential, and the
      research mirror leaves that section out (`skill/SKILL.md:131-133`).
- [ ] Never ship, patch, or redistribute the CLI binary or its skill. The
      person installs both with ByteDance's installer, and the release archive
      holds neither. ([terms.md](terms.md#4-rejected-routes);
      [01-decisions.md](../01-decisions.md#the-cli-on-the-persons-computer);
      [20-release.md](../20-release.md#step-6-package))

## rules/ summaries

`F/rules/` equals `B/rules/` and `O/rules/` byte for byte, so these line
numbers hold in all three.

| File | Lines | What shapes plans, names, docs, and notes |
| ---- | ----- | ----------------------------------------- |
| `GENERAL.md` | 377 | Do what was asked (62-66). No guards for states that cannot occur (68-79). One implementation (81-94). No hardcoded secrets (162-168). No logging (170-184). Messages: no internals, uppercase start, actionable (186-208). No tests; checks only when asked (210-218). Present state only (232-239). No em dashes (250-257). Contents section in long files (259-262). Comments say why (264-283). Protected `AGENTS.md` and `rules/` (329-332). No backward compatibility (347-365). |
| `NAMING.md` | 881 | Names follow the guide and the checks; provider names keep provider spelling with a recorded exception (25-46). Role, not type; same vocabulary everywhere (48-77). Banned vague words (142-169). Verb table (221-261). One concept per function name (284-302). Booleans `is_`, `has_`, `can_`, except checkbox widget IDs (323-343). Flatten one-module packages (388-390). Python, Bash, TypeScript cases (416-811). Help files match registered IDs (823-824). Provider IDs exact; examples named family-NN-task; units in names (840-862). |
| `PYTHON.md` | 2869 | Import-stable modules (93-110). Local tooling wins; no new ignores without a request (189-222). Relative imports in the package (170). `__all__` last. Internal names with one underscore (448-470). Comments and docstrings (759-990). Config owns defaults and limits (1459-1480). Small functions (1504-1548). Error message rules (2407-2453). Host boundaries, credentials, paid scope (2616-2644). Manual checks private (2646-2651). |
| `TYPESCRIPT.md` | 263 | Validate external input with the schema library (28-41, 206-218). Strict compiler flags (43-60). Named exports; barrels only in `index` (78-94). No enums (116-128). No `any`, casts, or non-null assertions (175-188). No logging; throw `Error` (220-236). Regenerate generated code (253-263). |
| `BASH.md` | 2044 | Bash only calls commands; logic lives in modules (40-124). Output and errors without logging (484-517). `# name - description` above every function (560-612). Tasks and hooks small, read-only, pinned, no installs (1701-1710). |
| `DOCUMENTATION.md` | 3843 | ISO 24495-1 review (39-47). Core standard: correct, concise, honest (54-97). One maintained explanation (99-136). README and ADVANCED split and contents (248-402). No layout sections (284-308). Essential information first (404-442). Voice, US English, numbers, dates, currency, casing (576-1012). Evidence; invent nothing (1095-1194). Bold labels (2155-2165). Images and screenshots (2580-2735). Keep docs current (3054-3175). Badges (3697-3708). Help, examples, and notes for components (3803-3843). |
| `WRITING.md` | 26 | All project text conforms to ISO 24495-1:2023 (3-5); short sentences, same name for same thing, exact API identifiers (14-17); no private reasoning in public text (19-21). |
| `PLANNING.md` | 95 | Concrete change descriptions (14-34). No tests or unrequested checks (36-40). Implementation order (42-75). Detail level and no placeholders (77-95). |

## Superseded rules

A plan writer follows the right-hand column.

| Earlier rule | Current rule | Sources |
| ------------ | ------------ | ------- |
| Input labels are short vendor names with spaces (`max tokens`), units in tooltips; later, lowercase phrases with units in parentheses | Inputs show their snake_case IDs, as ComfyUI does | O row 187, O 8d66919, `B/plans/08-requests.md:589-592` → O 179ec23, B 084ba64 |
| Input IDs follow their labels | Labels are the IDs; IDs are the API's field names | O row 198, O 644abe9 → B 084ba64, Rows 295-301 |
| Error type and header avoid the banned `plus` (`ByteplusError`, `X-Byteplus-Comfy`) | Vendor spelling with a narrow naming exception (`BytePlusError`, `X-BytePlus-Comfy`) | `B/plans/01-decisions.md:130-133`, `B/plans/05-foundation.md:60-63` → Row 307, B 79e056f |
| Two top notes per workflow, then a note per group as wide as the group and as tall as the tallest | A note above each group's frame, as wide as the frame | O 459bbd3, O row 188, O f59dc04 → B 20532df, O 48a6750 |
| Start Here ends with a line naming the models to activate | Start Here in steps only; the README requirements say to activate models | `B/plans/17-scripts-and-workflows.md:316-318` → Row 289, B 61e08d8 |
| Blueprints named step plus workflow, such as `Design (video-01)` | Blueprints named after the step alone; duplicate names refused | B 20532df, O 48a6750 → B 5bd4ada, O cdf0613 |
| Generated `banner.jpg`, `icon.png`, `social-preview.jpg` | The reference image set, then the pack's own look, in four folders | Row 219, B aea8641 → Row 293 → B fc461b2, B 472cf10 |
| No Registry icon | The Registry icon is the logo | Row 293 → B fc461b2, `B/pyproject.toml:164` |
| README with tags, badges, collage, group tags | No tags or collage; four neutral badges under the banner | O 6999991 → O f7ae905, O row 197 → O 48bf922, O row 204 |
| README feature bullets above the contents | The node table replaces the bullet list | Row 253 → B 084ba64, O 179ec23 |
| Install folder and Registry ID keep `comfyui-<vendor>` | Install as the vendor's short name, because ComfyUI names the template group and node badges after the folder: O as `openrouter`, F as `fal-ai`, and Dreamina as `dreamina`; B was not changed | O row 199, `B/plans/01-decisions.md:101-108` → O 783d103, `F/plans/20-release.md:50-53`, [01-decisions.md](../01-decisions.md#names-and-identifiers) |
| Settings menu "BytePlus settings" | "BytePlus Settings" | `B/plans/01-decisions.md:115`, `B/plans/17-scripts-and-workflows.md:308` → B 084ba64 |
| Separate video wait, check interval, identical-video block, uncertain records | One request timeout for every node; each run sends one new job | O e35ec5f, O row 180 → O 6340e4a |
| Bundled model list with dialog, routes, prices | Any model ID, checked live before paying | O rows 159, 160, 169 → O row 190, O 5ea7504, O 682dea8 |
| Model usage limits, spending sections, restricted key | None | `B/plans/20-owner-setup.md` Steps 3 to 5 → Row 249 |
| Search presets fill the vendor's templates | Plain instructions sent as written | Row 300 |
| Child-label code for dropdown fields | Deleted; ComfyUI labels them correctly | O 52d0871, O row 200 → Row 308, B 70d67fb |
| Text sizes in MiB | Decimal MB, as the vendor writes them | Row 309, B 3ddcfdf |
| Do not push while the pre-push check would fail between milestones | Push every commit at once; each node arrives with its help page, example, and README row | `B/plans/README.md:130-132` → F rows 226, 246 |
| A local file uploaded once is remembered and its link reused by later requests | Each request uploads its own local files | F's `UploadStore` → F row 262 |
| Images in BytePlus's art direction recolored for the vendor; then a flat field in the vendor's color | The family design, styled for the vendor, with a mark of the pack's own | F row 263 → F row 264 |
