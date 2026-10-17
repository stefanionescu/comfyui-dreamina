# Test Runs

This plan lists every live run the build makes against Dreamina, in order:

- Part 0: the free reads and a free price check of every model and mode;
- Part 1: the contract checks that settle what the CLI's schema and skill
  leave open;
- Part 2: the first run of each node milestone, through ComfyUI;
- Part 3: the video model sweep the owner asked for;
- Part 4: one run of every example workflow.

Each run gives its exact command or graph, what it confirms, what to expect,
its credits, and where its result is recorded. Every call goes through the
installed `dreamina-canvas` binary, as the pack's do
([01-decisions.md](01-decisions.md#why-the-cli)).

**Credits.** Every figure is in Dreamina credits and comes from Dreamina's own
quote: the `minimumCreditCeiling` of a run sent with `--credit-ceiling 0`,
which stops before the run and bills nothing
([02-dreamina-contract.md](02-dreamina-contract.md#credit-approval)). Part
0's price sweep ran on 2026-10-17. The credit columns below name a price from
[Prices the later tables use](#step-8-prices-the-later-tables-use), with its
number next to it. Credits appear only in these plans, never in the pack
([01-decisions.md](01-decisions.md#credits)).

**Lowest settings.** Every test run uses the lowest resolution and the
shortest duration each model allows, and `count` 1, as the owner asked on
2026-10-17. A row that exists to test something else, such as a `9:16` ratio
or `count` 2, still runs at the lowest resolution and the shortest duration.
The upscale tests use the lowest too: `normal` (free) and `pro` at `2K`. The
examples Part 4 runs use the same lowest settings
([17-scripts-and-workflows.md](17-scripts-and-workflows.md#example-workflows)).

## Contents

- [Totals](#totals)
- [Approval](#approval)
- [How to run and record](#how-to-run-and-record)
- [Part 0: Free reads and the price sweep](#part-0-free-reads-and-the-price-sweep)
- [Part 1: Contract checks](#part-1-contract-checks)
- [Part 2: First run of each node milestone](#part-2-first-run-of-each-node-milestone)
- [Part 3: Video model sweep](#part-3-video-model-sweep)
- [Part 4: Run every example once](#part-4-run-every-example-once)
- [What the runs change](#what-the-runs-change)
- [Names this plan uses from other plans](#names-this-plan-uses-from-other-plans)

## Totals

| Stage | When ([README build order](README.md#build-order)) | Runs | Cap | Credits, filled by Part 0 Step 8 |
| ----- | -------------------------------------------------- | ---- | --- | -------------------------------- |
| [Part 0](#part-0-free-reads-and-the-price-sweep) | Lists read on 2026-10-16; Steps 1 to 8 done on 2026-10-17 | 27 reads, 4 uploads, 1 import, 45 price checks, and 4 upscale quotes, all done; the owner's balance reading left | 0 | 0 |
| [Part 1](#part-1-contract-checks) | Milestone 4, after Part 0 | C-1 to C-17 (C-0 done; C-7 and C-8 settled by Part 0); 6 runs at most, C-10 and C-13 free, C-14's counted in Part 3 | ≤ 60 | I2I (0) + AUD-D (12) + C-11b's quote (12) + UP (0) + C-17's quote (2) = 26 |
| [Part 2](#part-2-first-run-of-each-node-milestone) | Milestones 8 to 12, each before its examples | 14 rows (3 free), 12 paid runs | ≤ 150 | IMG-D (6) + 3 × IMG-DE (18) + UP-D (2) + AUD-D (12) + DUB (12) + 2 × VID-D (32) + VID-F (16) + M2V (16) + M2V-E = 114 + M2V-E (C-15 fills) |
| [Part 3](#part-3-video-model-sweep) | Milestone 14 | 18 lowest-settings rows, 3 of them filled earlier, then round 2's 4 rows | ≤ 750 | 680: round 1's 600 (C-14's T2V of 16 included), less S-9 and S-18 (16 each, counted in Part 2), plus round 2's 112 |
| [Part 4](#part-4-run-every-example-once) | Milestone 14, after Part 3 | 9 | ≤ 250 | 169, from Part 0's prices; Step 1's quotes confirm it |
| Reserve | | | ≥ 90 | |
| **Total** | | | **≤ 1,300** | |

The caps are the README's
([Before the first paid run](README.md#before-the-first-paid-run)). The
owner's balance showed about 1,300 credits on 2026-10-16
([22-owner-setup.md](22-owner-setup.md#your-account-today)).

How the caps hold:

1. **C-14's video counts in Part 3.** It is the cheapest video model's
   cheapest run, made early because 08 and 14 are written against it. Its
   result fills S-4, `seedance_2.0_mini`'s `t2v` row, which is not run again.
1. **V-1, V-2, V-3, and E-1 run at the cheapest settings,** so each fills its
   row in Part 3 too. They count in Part 2.
1. **A Part whose filled total passes its cap** is shown to the owner with
   both numbers. The owner either moves credits from the reserve, keeping it
   at 90 or more, or drops runs in this order:
   - Part 1: C-17's paid step, then C-11b.
   - Part 2: V-3 (E-1 covers `m2v`, and S-22 covers a video reference), then
     I-3's second run.
   - Part 3 stops at its cap by its own rule.
   - Part 4: the owner chooses.
1. **A balance below 1,300 at the start of Part 1** shrinks Part 3's cap by
   the difference. The reserve stays at 90 or more.

## Approval

1. **What the owner approved.** The owner bought a discounted Dreamina plan
   (1.19 British pounds) that showed about 1,300 credits, and pre-approved
   spending them on these tests: "test as many models as possible for the
   video model … you have plenty of leeway to run a bunch of tests". The
   approval covers the runs in this plan, within each Part's cap. Anything
   outside this plan needs a new approval.
1. **Each stage is still shown first.** Before the first run of a Part, show
   the owner that Part's table: each run, what it confirms, its credits from
   Part 0, the Part's total and cap, and the balance the owner last read.
   Start when the owner says go.
1. **Part 0's price sweep had its own go.** It is free. It ran on
   2026-10-17: it created the "ComfyUI tests" canvas, uploaded four small
   files, and left about 50 draft nodes on that canvas
   ([Part 0](#part-0-free-reads-and-the-price-sweep)).
1. **C-17 needs the owner present,** to read the balance just before and just
   after its one run.
1. **Each run's ceiling is its exact quote.** A paid run passes
   `--credit-ceiling`, or sets `credit_ceiling`, to the quote Part 0 recorded
   for exactly those values, never more. A run whose values differ from every
   Part 0 price check is quoted first with `--credit-ceiling 0`, for free. If
   Dreamina's quote has risen, the run stops at exit 10 with nothing billed,
   and the new price goes to the owner before it runs.
1. **What no run ever does:**
   - buy credits, turn on top-ups, change the plan, or change any account
     setting;
   - pass `--yes`, `--credit-token`, `--force`, `--use`, or `--profile`;
   - delete or edit a canvas node, or delete a canvas (the owner deletes
     drafts in Firefox, as [22-owner-setup.md](22-owner-setup.md#step-6-delete-drafts-left-by-refusals)
     says);
   - sign out, or sign in another account, to provoke an error
     ([research/owner-rules.md](research/owner-rules.md#paid-requests-and-live-checks)).
1. **A run the owner drops** is recorded as dropped in
   [Changes made while building](README.md#changes-made-while-building), with
   the reason. Any plan that depended on it says what is still unconfirmed.
1. **Stop and report** when a balance reading falls by more than the sum of
   the quotes since the last reading, or when a run stopped at a ceiling below
   its quote is billed.

## How to run and record

**Where run files go.** Every CLI call runs from a fresh folder in the
agent's scratchpad, never in the repository: `dreamina-runs/part-0` to
`dreamina-runs/part-4`, with `helpers.sh` in `dreamina-runs`. Run files hold
node, submit, and resource IDs and the outputs; they never hold credentials.
They are deleted once their results are recorded, and never committed.

**Every block** below starts in its Part's folder with the helpers loaded:

```sh
cd "$RUNS/part-1" && . "$RUNS/helpers.sh"
```

`RUNS` is the absolute path of `dreamina-runs` in the session's scratchpad.
Type it out in each call: the agent's shell keeps no variables between calls.
The blocks leave this line out.

**The base command.** Every call is
`B=~/.local/bin/dreamina-canvas; $B --format json --non-interactive …`, the
pack's own shape ([02-dreamina-contract.md](02-dreamina-contract.md#how-the-pack-calls-the-cli)).
The helper `dr` makes it, saves stdout in `NAME.json` (a success), stderr in
`NAME.err.json` (a failure), and the exit code in `NAME.exit`.

**The helpers.** Write this file once per session. It is Bash 3.2-safe, as
F's Bash rules ask, though it runs in the scratchpad, not in the repository.

```sh
mkdir -p "$RUNS/part-0" "$RUNS/part-1" "$RUNS/part-2" "$RUNS/part-3" "$RUNS/part-4"
cat > "$RUNS/helpers.sh" <<'EOF'
# Sourced at the start of every block of plans/21-test-runs.md. Bash 3.2 or later, on macOS.
B="$HOME/.local/bin/dreamina-canvas"
CAP=/Users/dr_stone/Documents/work/comfyui-dreamina/plans/research/captures
T=bc7dfe2a-ecf1-4d6c-b651-eff1748acf51       # the "ComfyUI tests" canvas
PNG=d89a2753-fc16-4ef6-85db-bca5b983b793     # apple.png
PNG2=a50d5a26-c1ea-4db2-a63b-4a1006e0a78f    # apple-left.png
WAV=dc6591ba-2601-448b-90a9-df83244dfc4a     # tone.wav
MP4=bcda0f62-d06b-4235-bf17-cade1cb0c58a     # clip.mp4
MP3=248cf326-9f1c-48b1-835e-82cf097f4eda     # tone.mp3
TINY=f0c400ca-fffd-43a4-8fa7-8ab448cec28e    # tiny.png
SHORT=ba695f38-9e6d-4223-a7a5-f38d9688abfc   # short.wav
IMPORT=1045c3e6-6bf1-4f86-975f-ea44a3f8843d  # the submit ID of apple.png's import
COMFY=/Users/dr_stone/ComfyUI-Installs/ComfyUI/ComfyUI
API=http://127.0.0.1:8188
STATE="$HOME/Library/Application Support/DreaminaComfyUI"

# new_id: a new lowercase UUID, the one spelling the CLI accepts.
new_id() { uuidgen | tr '[:upper:]' '[:lower:]'; }

# dr NAME ARGUMENTS...: one CLI call. NAME.json gets stdout, NAME.err.json stderr, NAME.exit the exit code.
dr() {
  local name="$1"
  shift
  "$B" --format json --non-interactive "$@" < /dev/null > "$name.json" 2> "$name.err.json"
  local code=$?
  printf '%s\n' "$code" > "$name.exit"
  printf '%s\t%s\n' "$name" "$code" >> exits.tsv
  printf '%s: exit %s\n' "$name" "$code"
}

# clean FILE: the reply without the account ID, the sign-in codes, or a credit token.
clean() {
  jq 'walk(if type == "object" then del(.userId, .deviceCode, .userCode, .verificationUriComplete, .creditConfirmationToken, .creditToken) else . end)' "$1"
}

# job MODEL MODE [SCENARIO] [REFERENCES]: the name of a Part 0 price check.
job() {
  awk -F '\t' -v mo="$1" -v m="$2" -v sc="${3:-}" -v r="${4:-}" \
    '$3 == mo && $4 == m && $5 == sc && (r == "" || $6 == r) { print $1 }' "$CAP/price-sweep.tsv" | head -n 1
}

# cheapest MODE [SCENARIO] [REFERENCES]: the price check of MODE with the lowest quote.
cheapest() {
  awk -F '\t' -v m="$1" -v sc="${2:-}" -v r="${3:-}" \
    '$4 == m && $5 == sc && (r == "" || $6 == r) && $8 ~ /^[0-9]+$/ { print $8 "\t" $1 }' "$CAP/price-sweep.tsv" \
    | sort -n | head -n 1 | cut -f 2
}

# cheapest_priced MODE [SCENARIO] [REFERENCES]: as cheapest, among the checks quoted above 0, so a ceiling of 0 stops it.
cheapest_priced() {
  awk -F '\t' -v m="$1" -v sc="${2:-}" -v r="${3:-}" \
    '$4 == m && $5 == sc && (r == "" || $6 == r) && $8 ~ /^[0-9]+$/ && $8 > 0 { print $8 "\t" $1 }' "$CAP/price-sweep.tsv" \
    | sort -n | head -n 1 | cut -f 2
}

# price JOB: the quote Part 0 recorded for a price check.
price() { awk -F '\t' -v j="$1" '$1 == j { print $8 }' "$CAP/price-sweep.tsv"; }

# flag_of JOB FLAG: the value a price check sends for one flag, such as --resolution.
flag_of() {
  jq -r --arg j "$1" --arg f "$2" 'select(.name == $j) | .args | (index($f)) as $i | if $i then .[$i + 1] else empty end' "$CAP/price-sweep-jobs.jsonl"
}

# arguments_of JOB: a price check's flags as a node's arguments JSON, numbers as numbers.
arguments_of() {
  jq -c --arg j "$1" 'select(.name == $j) | .args[3:] | [range(0; length; 2) as $i | {key: (.[$i] | ltrimstr("--")), value: .[$i + 1]}]
    | map(select(.key | IN("project-id", "model", "prompt", "ref") | not) | .value |= (if test("^[0-9]+$") then tonumber else . end))
    | from_entries' "$CAP/price-sweep-jobs.jsonl"
}

# run_job NAME JOB CEILING [PROMPT [MORE ARGUMENTS...]]: a run with a price check's flags, a new submit ID
# (saved first in NAME.submit), and the given ceiling. PROMPT, when not empty, replaces the prompt.
run_job() {
  local name="$1" job_name="$2" ceiling="$3" prompt="${4:-}" a
  shift 3
  [ "$#" -gt 0 ] && shift
  local -a args
  args=()
  while IFS= read -r -d '' a; do args+=("$a"); done < <(jq -j --arg j "$job_name" --arg p "$prompt" \
    'select(.name == $j) | .args | (if $p != "" then .[index("--prompt") + 1] = $p else . end) | .[] | (., "\u0000")' \
    "$CAP/price-sweep-jobs.jsonl")
  if [ "${#args[@]}" -eq 0 ]; then
    printf 'No price check named %s\n' "$job_name"
    return 1
  fi
  new_id > "$name.submit"
  dr "$name" "${args[@]}" "$@" --run --credit-ceiling "$ceiling" --submit-id "$(cat "$name.submit")"
}

# wait_for NAME SUBMIT CANVAS: operation status, then a 15-second operation wait, until the wait stops answering exit 20.
wait_for() {
  local name="$1" submit="$2" canvas="$3" n=0 start
  start=$(date +%s)
  while [ "$n" -lt 240 ]; do
    n=$((n + 1))
    dr "$name-status-$n" operation status "$submit" --project-id "$canvas"
    dr "$name-wait-$n" operation wait "$submit" --project-id "$canvas" --timeout 15s
    [ "$(cat "$name-wait-$n.exit")" = 20 ] || break
  done
  cp "$name-wait-$n.json" "$name-terminal.json"
  printf '%s\t%s\n' "$name" "$(( $(date +%s) - start ))" | tee -a seconds.tsv
}

# download_outputs NAME NODE SUBMIT CANVAS EXTENSION: node show, then each resource of that submit ID, with its size and SHA256 checked.
download_outputs() {
  local name="$1" node="$2" submit="$3" canvas="$4" extension="$5" i=0 resource
  dr "$name-show" node show --project-id "$canvas" --node-id "$node"
  jq -r --arg s "$submit" '.data.nodes[0].node.resources[] | select(.submitId == $s) | .resourceId' "$name-show.json" > "$name-resources.txt"
  while IFS= read -r resource; do
    i=$((i + 1))
    dr "$name-get-$i" resource get "$resource" --project-id "$canvas"
    dr "$name-download-$i" resource download "$resource" --project-id "$canvas" --output "$PWD/$name-$i.$extension"
    printf 'reply: %s bytes, %s\nfile:  %s bytes, %s\n' \
      "$(jq -r .data.size "$name-download-$i.json")" "$(jq -r .data.sha256 "$name-download-$i.json")" \
      "$(stat -f %z "$name-$i.$extension")" "$(shasum -a 256 "$name-$i.$extension" | cut -d ' ' -f 1)"
  done < "$name-resources.txt"
}

# probe FILE: each stream's kind, codec, size, frame rate, and sample rate, and the duration.
probe() {
  ffprobe -v error -show_entries stream=codec_type,codec_name,width,height,r_frame_rate,sample_rate,channels \
    -show_entries format=duration -of compact "$1"
}

# pack_canvas: the ID of the pack's own "ComfyUI" canvas.
pack_canvas() { "$B" --format json --non-interactive canvas ls --limit 100 | jq -r '.data.items[] | select(.name == "ComfyUI") | .projectId'; }

# comfy_queue: how many prompts the local ComfyUI is running and holding.
comfy_queue() { curl -sS "$API/queue" | jq -c '{running: (.queue_running | length), pending: (.queue_pending | length)}'; }

# comfy_send FILE: queue one API-format workflow in the local ComfyUI; print its prompt ID, or the refusal.
comfy_send() {
  curl -sS -X POST "$API/prompt" -H "Content-Type: application/json" -d "{\"prompt\": $(cat "$1")}" \
    | jq -r 'if .prompt_id then .prompt_id else "refused: \(.error.message // "") \(.node_errors // {} | tostring)" end'
}

# comfy_history ID: one prompt's ComfyUI history entry: status, seconds from start to end, and outputs.
comfy_history() {
  curl -sS "$API/history/$1" | jq --arg id "$1" '.[$id] | {status: .status.status_str,
    seconds: ((.status.messages | map({(.[0]): .[1].timestamp}) | add) as $t | (($t.execution_success // $t.execution_error) - $t.execution_start) / 1000),
    outputs}'
}

# set_inputs FILE CLASS JSON: the workflow with JSON merged into the inputs of every node of CLASS.
set_inputs() { jq --arg c "$2" --argjson v "$3" 'with_entries(if .value.class_type == $c then .value.inputs += $v else . end)' "$1"; }
EOF
```

**The test canvas.** Every CLI run in this plan goes to a separate canvas,
"ComfyUI tests", created once with the fixed client-made ID `T`. The pack's
own `ComfyUI` canvas holds only what ComfyUI runs make, so the two never mix.
The IDs in the helpers are fixed on purpose: a later session that uploads or
imports again with the same ID gets the same resource or node, as the CLI
documents for retries ([research/cli.md](research/cli.md#resources-upload-and-download)).
They are public IDs on the owner's account, kept only in these local plans.

**Through ComfyUI** (Parts 2 to 4):

- **A shared ComfyUI.** Another Claude session, the live-shopping work,
  restarts this same ComfyUI when its queue empties. A restart can cut a run
  off or erase its history entry, as it did during F's A-2. So:
  - Before each send, `comfy_queue` must show nothing running or pending.
  - After each paid run, check it on the Dreamina canvas, not only in
    ComfyUI's history: its node, status, and resources, with
    `node find --project-id "$(pack_canvas)" --limit 50`.
  - A run cut off after Dreamina accepted it keeps its generation record in
    `$STATE/generations/`. **Generation: Download** collects it for free.
    Never send it again.
- **Restarts.** Restart ComfyUI only with its queue empty and the owner's yes.
  F restarted through ComfyUI Manager's `/v2/manager/reboot`, which Comfy
  Desktop relaunched with its own arguments.
- **Test files in ComfyUI.** Copy Part 0's files into ComfyUI's input folder
  once, under names that clash with nothing:

  ```sh
  for f in apple.png apple-left.png tone.wav clip.mp4; do cp "../part-0/$f" "$COMFY/input/dreamina-test-$f"; done
  ```

**The balance.** The CLI shows none
([02-dreamina-contract.md](02-dreamina-contract.md#the-account)). The owner
reads it on dreamina.capcut.com, in Firefox, before and after each Part, and
for C-17 just before and after its run
([22-owner-setup.md](22-owner-setup.md#step-4-watch-the-credits)). Dreamina
may add credits by itself, such as a plan renewal, so compare readings taken
the same day, each with its time.

**Recording.** After each run:

1. Compare the result with **Expect**. Record it in 02's
   [Results of the contract runs](02-dreamina-contract.md#results-of-the-contract-runs)
   (Parts 0 and 1), and in
   [research/catalog.md](research/catalog.md) (prices, and each model's
   outputs from Part 3).
1. When it differs, the CLI or Dreamina differs from the plans: correct 02 and
   the plans **Record in** names before building further.
1. Add a row to [Changes made while building](README.md#changes-made-while-building)
   for each Part or milestone batch, as F's rows 236, 248, 253, 258, and 261
   do: what ran, what each run found, the plans changed, the credits spent,
   and the running total.
1. Save each reply worth keeping through `clean`, which removes `userId`,
   sign-in codes, and any credit token, and copy it into
   `plans/research/captures/` under the name **Record in** gives. `plans/research/captures/` is
   ignored by Git, so captures stay local.
1. Each fix a run calls for is its own commit, as B's and F's were.
1. Keep run records private: they go to no issue, chat, or third party.

## Part 0: Free reads and the price sweep

Part 0 reads the account and the lists, then checks the price of every model
and mode for free. It needs no pack code. The reads were done on 2026-10-16,
and Steps 1 to 8 on 2026-10-17. Step 9's balance reading is the owner's, when
convenient; nothing waits for it.

### Done on 2026-10-16

The owner signed in on 2026-10-16. These reads are done, and their captures
are in `research/captures/`:

| Read | Result | Capture |
| ---- | ------ | ------- |
| Sign-in (`auth login`, `auth wait`) | Two links expired unapproved; the third was approved. `auth wait` exit 0, `status` `logged_in` | Recorded in 02's results; the codes were not kept |
| `auth status` | Signed in; credentials in the keyring until 2026-12-15 | `auth-status.json` |
| `auth account` (C-0) | `isVip` `true`, `vipLevel` `standard`: the plan gate passed on Standard | `auth-account.json`, without `userId` |
| `model list --type image`, `video`, `audio` (C-0) | 12 image, 5 video, and 2 audio models; flags written `--ratio`; no music model | `model-list-image.json`, `model-list-video.json`, `model-list-audio.json` |
| `model <canonical> --type <kind>`, for each model | The file limits `model list` leaves out | `models/<model>.json`, 19 files |
| `voice list --model seed_audio_v1 --offset 0 --count 100` | 13 voices, one page | `voices-seed_audio_v1-page-0.json` |
| `canvas ls --limit 100` | No canvases | Not kept |

[research/catalog.md](research/catalog.md) is written from them. To read them
again, after a CLI update or a plan change, run this in `part-0`:

```sh
dr auth-status auth status
dr auth-account auth account
for kind in image video audio; do dr "model-list-$kind" model list --type "$kind"; done
for kind in image video audio; do
  jq -r '.data.items[].model' "model-list-$kind.json" | while IFS= read -r m; do dr "model-$m" model "$m" --type "$kind"; done
done
jq -r '.data.items[] | select(any(.modes[]; .name == "tts")) | .model' model-list-audio.json | while IFS= read -r m; do
  offset=0
  page=0
  while :; do
    dr "voices-$m-page-$page" voice list --model "$m" --offset "$offset" --count 100
    [ "$(jq -r --arg m "$m" '.data.models[$m].hasMore' "voices-$m-page-$page.json")" = true ] || break
    offset=$(jq -r --arg m "$m" '.data.models[$m].nextOffset' "voices-$m-page-$page.json")
    page=$((page + 1))
  done
done
dr canvas-ls canvas ls --limit 100
```

### Steps 1 to 8: done on 2026-10-17

The owner said go, and Steps 1 to 8 ran on 2026-10-17. The steps below stay
as the record, and to run again after a CLI update. The results:

- **Canvas.** "ComfyUI tests" was created with the ID `T` (Step 2).
- **Uploads.** All four were accepted, the WAV and the MP4 included (Step 3).
- **Import.** The import needs a `--title`. Without one it is refused with
  `cli.invalid_node_input`, `fieldPath` `title`. Step 4's command passes one.
- **Price checks.** 45 checks: 42 priced, 2 ran free (`seedream_4.0`, quote
  0), and 1 was refused locally, for free: one listed speech model cannot be
  run by name. That check is the one exit 2 in `price-sweep.tsv`; nothing to
  fix.
- **The exit 10 reply** for a ceiling below the quote: `error.code`
  `cli.generation_credit_ceiling_too_low`, `class` `confirmation_required`,
  `creditConfirmation.reason` `ceiling_too_low`.
- **Upscale.** The imported node is an eligible source. `normal` is free and
  ran at its quote of 0: 1280×720 became a 2560×1440 PNG. `pro` costs 2 at
  `2K`, 4 at `4K`, and 8 at `8K`.
- **C-7 and C-8 settled.** The two free `seedream_4.0` runs and the free
  `normal` upscale showed `submission.state` `accepted` on the run reply;
  operation `state` `succeeded`, `submission.state` `completed`, and
  resource `state` `succeeded` at the end; and `node show` resource `status`
  `success`. The images are JPEG, 2048×2048 at `2K` `1:1`; the upscale is
  PNG. Each download's size and SHA256 matched the file.
- **Prices**, at the lowest resolution and the shortest duration. Images:
  `seedream_4.0` 0; `seedream_4.1`, `4.6`, and `4.7` 2; GPT Image 2.5 Flare
  and Sunburst 5 (`1K`); `seedream_4.5`, `5.0_lite`, and `5.0_pro` 6;
  `jm_image_model_gg_bp_21` 9; `gpt_image_2` 14; `gemini_3_image_pro` 31.
  Video at 4 seconds (5 for `seedance_pro_fast`), the same in every mode:
  `seedance_2.0_mini` 16, `seedance_pro_fast` 20, `seedance_2.0_fast` 24, and
  `seedance_2.0` 52, all at `720p`; `seedance_2.5` 48 at `480p`. Speech:
  `seed_audio_v1` 12, in both scenarios.
- **Defaults** (Step 7). The video starting model is now
  `seedance_2.0_mini`: 16 credits, against 24 for `seedance_2.0_fast` at the
  same settings. The starting `credit_ceiling` values: image 10, video 20,
  audio 20, upscale 10.

### Step 1: Make the test files

With Homebrew's `ffmpeg`, in `part-0`. The files are the same each time on
this Mac, so a later session makes them again with the same commands.

```sh
disc() {  # disc CENTER_X FILE: a red disc on white, 1280x720 (16:9)
  ffmpeg -v error -y -f lavfi -i "color=c=white:s=1280x720:d=1,format=rgb24" \
    -vf "geq=r='if(lt(hypot(X-$1,Y-380),200),210,255)':g='if(lt(hypot(X-$1,Y-380),200),30,255)':b='if(lt(hypot(X-$1,Y-380),200),40,255)'" \
    -frames:v 1 "$2"
}
disc 640 apple.png
disc 380 apple-left.png
ffmpeg -v error -y -f lavfi -i "color=c=red:s=16x16:d=1" -frames:v 1 tiny.png
ffmpeg -v error -y -f lavfi -i "sine=frequency=440:duration=5" -ar 44100 -ac 1 -c:a pcm_s16le tone.wav
ffmpeg -v error -y -f lavfi -i "sine=frequency=440:duration=2" -ar 44100 -ac 1 -c:a pcm_s16le short.wav
ffmpeg -v error -y -f lavfi -i "sine=frequency=440:duration=5" -ar 44100 -ac 1 -c:a libmp3lame -b:a 128k tone.mp3
ffmpeg -v error -y -f lavfi -i "testsrc2=s=1280x720:r=24:d=5" -f lavfi -i "sine=frequency=440:duration=5" \
  -c:v libx264 -pix_fmt yuv420p -c:a aac -shortest clip.mp4
```

| File | What | Why this shape |
| ---- | ---- | -------------- |
| `apple.png` | A red disc on white, 1280×720, about 6 KB | 16:9, so `first_last_frame` at `--ratio 16:9` matches it; above `seedance_2.5`'s 300-pixel minimum |
| `apple-left.png` | The same disc moved left | The last frame of a two-image `first_last_frame`, with the same ratio |
| `tiny.png` | A red 16×16 square | C-17's run likely to fail, and C-17's refusal at save |
| `tone.wav`, `tone.mp3` | A 440 Hz tone, 5 seconds, mono | `seed_audio_v1` refuses audio under 3 seconds (`minDurationMs` 3000); 5 seconds stays clear of that edge and inside every model's audio range |
| `short.wav` | The same tone, 2 seconds | C-12's refusal of audio under 3 seconds |
| `clip.mp4` | A test pattern with the tone, 1280×720, 24 fps, 5 seconds, H.264 and AAC | Inside both Seedance video ranges (2.0 to 15.4 seconds, 200 to 2,160 pixels; 1.8 to 30.2 seconds, 300 to 6,000 pixels) |

### Step 2: Create the test canvas (C-1)

```sh
dr c01-create canvas create "ComfyUI tests" --project-id "$T"
dr c01-retry canvas create "ComfyUI tests" --project-id "$T"
dr c01-ls canvas ls --limit 100
jq '.data' c01-create.json
jq '.data, .error' c01-retry.json c01-retry.err.json
jq -c '.data.items[] | select(.name == "ComfyUI tests")' c01-ls.json
```

Give the owner the canvas's `webUrl`, so the drafts can be watched in
Firefox. C-1 below says what this settles.

### Step 3: Upload the test files

```sh
dr upload-apple resource upload --project-id "$T" --file "$PWD/apple.png" --type image --resource-id "$PNG"
dr upload-apple-left resource upload --project-id "$T" --file "$PWD/apple-left.png" --type image --resource-id "$PNG2"
dr upload-tone resource upload --project-id "$T" --file "$PWD/tone.wav" --type audio --resource-id "$WAV"
dr upload-clip resource upload --project-id "$T" --file "$PWD/clip.mp4" --type video --resource-id "$MP4"
jq -c '.data' upload-*.json
```

Expect exit 0 and `resourceId` equal to the ID sent. Uploads are free. C-2 to
C-4 read these replies.

### Step 4: Import apple.png as an image node

The source for the upscale prices and C-13. Free: "this is the only case where
`--submit-id` works without `--run`".

```sh
dr import-apple node create image --project-id "$T" --resource-id "$PNG" --import-kind local_upload \
  --title "Image: Upscale source" --submit-id "$IMPORT"
jq '.data.node | {nodeId, type, status, resources}' import-apple.json
clean import-apple.json > "$CAP/node-create-import.json"
```

### Step 5: The price sweep

One price check for every listed model and every mode entry it lists: 45 on
the 2026-10-16 lists. Each is a run sent with `--credit-ceiling 0`, which
stops at exit 10 with `creditConfirmation.minimumCreditCeiling` and bills
nothing. Each leaves one unrun draft on the test canvas.

The values are the cheapest the list allows:

- `--resolution`: the lowest value (`480p` below `720p`, `1K` below `1.5K`
  below `2K`);
- `--duration`: the lowest value, or the minimum;
- `--count 1`;
- `--ratio`: `1:1` for images and `16:9` for video, the starting values;
- `--voice-name`: `Jessie` where the model has it, the Audio starting value;
- any other required flag: its first value, or its minimum;
- references: the fewest the mode needs, from Step 3's uploads, by
  `mediaType`;
- the prompt: "A red apple on a white table." for images and video, "Hello
  from Dreamina." for speech.

Write the builder:

```sh
cat > jobs.jq <<'EOF'
# Builds Part 0's price checks from the three model-list captures, read with --slurp.
# $T: the test canvas. $ids: the uploads by media type, in order. $voices[0]: one voice per speech model.
def level: ascii_downcase | capture("^(?<n>[0-9.]+) *(?<u>[pk])$") | (.n | tonumber) * (if .u == "k" then 1000 else 1 end);
def lowest: min_by(try level catch 1e9);
def text($mode): if $mode == "tts" then "Hello from Dreamina." elif $mode == "music" then "Calm solo piano." else "A red apple on a white table." end;
def pick($kind; $voice):
  (.flag | ltrimstr("--")) as $f
  | (if $kind == "image" then "1:1" else "16:9" end) as $ratio
  | if $f == "prompt" or $f == "scenario" then null
    elif $f == "count" then "1"
    elif $f == "voice-name" then ($voice // error("no voice captured"))
    elif $f == "ratio" and ((.values // []) | index($ratio)) then $ratio
    elif $f == "resolution" and .values then (.values | lowest)
    elif $f == "duration" and .values then (.values | min_by(tonumber))
    elif $f == "duration" and .min != null then (.min | tostring)
    elif .required and .values then .values[0]
    elif .required and .min != null then (.min | tostring)
    elif .required then error("no value for the required flag " + $f)
    else null end;
def refs:
  if .references == null then []
  else .references as $r
    | [$r.types[] | select(.min > 0) | {t: .mediaType, n: .min}] as $need
    | if ($need | length) > 0 then $need
      elif (($r.requireAnyOfTypes // []) | length) > 0 then [{t: $r.requireAnyOfTypes[0], n: 1}]
      elif $r.min > 0 then [{t: $r.types[0].mediaType, n: $r.min}]
      else [] end
  end;
.[].data.items[] as $m
| $m.modes[] as $mode
| ($mode | refs) as $need
| ([$need[].n] | add // 0) as $count
| { name: ([$m.model, $mode.name, ($mode.scenario // empty), (if $count > 0 then "\($count)ref" else empty end)] | join("+")),
    kind: $m.type, model: $m.model, mode: $mode.name, scenario: ($mode.scenario // ""), refs: $count }
| . + (try {
      args: (["node", "create", $m.type, "--project-id", $T, "--mode", $mode.name]
        + (if $mode.scenario then ["--scenario", $mode.scenario] else [] end)
        + ["--model", $m.model, "--prompt", text($mode.name)]
        + [($mode.flags // [])[] | {f: .flag, v: pick($m.type; $voices[0][$m.model])} | select(.v != null) | .f, .v]
        + [$need[] | . as $x | ($ids[$x.t] // []) as $list
            | if ($list | length) < $x.n then error("no upload for \($x.n) \($x.t) references") else $list[0:$x.n][] | "--ref", "res:" + . end])
    } catch { skip: . })
EOF
```

Build the list of checks. The flags keep their two dashes, as the list writes
them:

```sh
jq -s 'map(.data.models | to_entries[] | {key, value: ([.value.items[].voiceName] | if index("Jessie") then "Jessie" else .[0] end)}) | from_entries' \
  "$CAP"/voices-*-page-0.json > voices.json
IDS=$(jq -n --arg a "$PNG" --arg b "$PNG2" --arg v "$MP4" --arg w "$WAV" '{image: [$a, $b], video: [$v], audio: [$w]}')
jq -c -s --arg T "$T" --argjson ids "$IDS" --slurpfile voices voices.json -f jobs.jq \
  "$CAP/model-list-image.json" "$CAP/model-list-video.json" "$CAP/model-list-audio.json" > price-sweep-jobs.jsonl
wc -l < price-sweep-jobs.jsonl
jq -r '[.name, (.skip // "")] | @tsv' price-sweep-jobs.jsonl
```

Expect 45 lines and no `skip`. Each name is the model, the mode, the scenario,
and the number of references, joined with `+`, such as
`seedance_2.5+first_last_frame+2ref`; the two `first_last_frame` entries of a
video model differ by it.

Send the checks:

```sh
: > price-sweep.tsv
while IFS= read -r line; do
  name=$(printf '%s' "$line" | jq -r .name)
  fields=$(printf '%s' "$line" | jq -r '[.name, .kind, .model, .mode, .scenario, .refs] | @tsv')
  if printf '%s' "$line" | jq -e 'has("skip")' > /dev/null; then
    printf '%s\tskipped\t\t%s\n' "$fields" "$(printf '%s' "$line" | jq -r .skip)" >> price-sweep.tsv
    continue
  fi
  args=()
  while IFS= read -r -d '' a; do args+=("$a"); done < <(printf '%s' "$line" | jq -j '.args[] | (., "\u0000")')
  dr "$name" "${args[@]}" --run --credit-ceiling 0 --submit-id "$(new_id)"
  if [ "$(cat "$name.exit")" = 0 ]; then
    printf '%s\t0\t%s\tran at ceiling 0\n' "$fields" "$(jq -r '.data.quote.maxCredits // "unknown"' "$name.json")" >> price-sweep.tsv
  else
    printf '%s\t%s\t%s\n' "$fields" "$(cat "$name.exit")" \
      "$(jq -r '[(.creditConfirmation.minimumCreditCeiling // "none"), (.error.code // "")] | @tsv' "$name.err.json")" >> price-sweep.tsv
  fi
done < price-sweep-jobs.jsonl
cp price-sweep-jobs.jsonl price-sweep.tsv "$CAP/"
column -t -s "$(printf '\t')" price-sweep.tsv
```

`price-sweep.tsv` has one line per check: the name, kind, model, mode,
scenario, references, exit code, credits, and error code. The later Parts
read it and the jobs file from `research/captures/`, so they work in any
session.

How to read each line:

| Exit | Credits | Means | Next |
| ---- | ------- | ----- | ---- |
| 10 | a number | The price, nothing billed | Recorded |
| 10 | `none` | Dreamina could not price it (`occupancy_unknown`), nothing billed | Recorded "no price"; that model and mode run nowhere in this plan |
| 0 | `maxCredits` | The quote was 0, so a ceiling of 0 let it run; it bills 0 | Wait for it and download it as C-8 does, and record it in [What the runs change](#what-the-runs-change) |
| 2 | empty | The CLI refused the values locally, nothing sent | Fix the builder's choice for that flag and send that one check again |
| other | empty | Refused by Dreamina at save or quote, such as a membership limit on a listed resolution | Record the `error` fields; a refusal at save bills nothing |

Save one exit-10 reply as the capture C-5 reads:

```sh
clean "$(jq -r 'select(.mode == "t2i") | .name' price-sweep-jobs.jsonl | head -n 1).err.json" > "$CAP/error-confirmation-required.json"
```

### Step 6: Upscale prices

Four quotes on Step 4's imported node. `node upscale image` has no `--run`
and starts on submission, so the ceiling of 0 is passed explicitly: "Explicit
ceilings remain binding below the threshold."

```sh
N=$(jq -r .data.node.nodeId "$CAP/node-create-import.json")
dr upscale+normal node upscale image --project-id "$T" --node-id "$N" --submit-id "$(new_id)" --mode normal --credit-ceiling 0
for r in 2K 4K 8K; do
  dr "upscale+pro+$r" node upscale image --project-id "$T" --node-id "$N" --submit-id "$(new_id)" --mode pro --resolution "$r" --credit-ceiling 0
done
for name in upscale+normal upscale+pro+2K upscale+pro+4K upscale+pro+8K; do
  printf '%s\tupscale\t\t%s\t\t\t%s\t%s\n' "$name" "$(printf '%s' "$name" | cut -d + -f 2-)" "$(cat "$name.exit")" \
    "$(jq -r '[(.creditConfirmation.minimumCreditCeiling // "none"), (.error.code // "")] | @tsv' "$name.err.json")" >> "$CAP/price-sweep.tsv"
done
jq '{error, creditConfirmation, partialData}' upscale+pro+2K.err.json
clean upscale+pro+2K.err.json > "$CAP/node-upscale-quote.json"
```

Expect exit 10 with a price and `partialData.items[].sourceNodeId` and
`submitId`, and no output node. If Dreamina refuses the imported node as a
source, record the `error` fields: C-13 then quotes the upscale on C-8's
generated image instead, and 12 changes ([What the runs change](#what-the-runs-change)).

### Step 7: Check the starting values and the ceiling defaults

The starting values in [research/catalog.md](research/catalog.md#defaults)
match Step 5's cheapest values, so their prices are already in the sweep:

| Node | Starting values | Price check |
| ---- | --------------- | ----------- |
| Image: Generate | `seedream_5.0_lite`, `{"ratio": "1:1", "resolution": "2K"}` | `seedream_5.0_lite+t2i` |
| Video: Generate | `seedance_2.0_mini`, `{"ratio": "16:9", "resolution": "720p", "duration": 4}` | `seedance_2.0_mini+t2v` |
| Audio: Generate | `seed_audio_v1`, `{"voice-name": "Jessie"}` | `seed_audio_v1+tts+text-reading` |
| Image: Upscale | `{"resolution": "2K"}` | `upscale+pro+2K` |

```sh
for j in seedream_5.0_lite+t2i seedance_2.0_mini+t2v seed_audio_v1+tts+text-reading upscale+pro+2K; do
  p=$(price "$j")
  printf '%s: %s credits, credit_ceiling default %s\n' "$j" "$p" "$(( (p + 9) / 10 * 10 ))"
done
grep -E '\+t2v' "$CAP/price-sweep.tsv" | sort -t "$(printf '\t')" -k8,8n | cut -f 1,8
```

1. Apply the catalog's rule: when another model of the same kind is cheaper
   at the same settings and equally current, such as `seedance_2.0_mini`
   against `seedance_2.0_fast`, switch the starting model.
1. Each node's `credit_ceiling` default is its starting values' quote,
   rounded up to the next multiple of 10
   ([01-decisions.md](01-decisions.md#credits)). Write it into
   [09-node-image.md](09-node-image.md), [10-node-video.md](10-node-video.md),
   [11-node-audio.md](11-node-audio.md), and
   [12-node-upscale.md](12-node-upscale.md).
1. Record any switch and the four defaults in the changes table, and in the
   catalog's Defaults section.

### Step 8: Prices the later tables use

The **Credits** column is filled from `price-sweep.tsv` and Step 6's upscale
quotes, on 2026-10-17. M2V-E is filled later, by C-15's free quote.

| Name | The quote of | Command | Credits | Used by |
| ---- | ------------ | ------- | ------- | ------- |
| IMG-D | Image: Generate's starting values | `price seedream_5.0_lite+t2i` | 6 | I-1 |
| IMG-DE | The same model in `i2i` with one image | `price seedream_5.0_lite+i2i+1ref` | 6 | I-2, I-3 |
| VID-D | Video: Generate's starting values | `price seedance_2.0_mini+t2v` | 16 | V-1, V-4 |
| VID-F | The same model, `first_last_frame`, one image | `price seedance_2.0_mini+first_last_frame+1ref` | 16 | V-2 |
| AUD-D | Audio: Generate's starting values | `price seed_audio_v1+tts+text-reading` | 12 | C-11a, A-1 |
| DUB | `seed_audio_v1` omni dubbing | `price seed_audio_v1+tts+omni-dubbing`; C-12a quotes it again with one image | 12 | A-2 |
| UP-D | Image: Upscale's starting values | `price upscale+pro+2K` | 2 | U-1 |
| UP | The lowest of the four upscale quotes | `grep '^upscale' "$CAP/price-sweep.tsv" \| sort -t "$(printf '\t')" -k8,8n \| head -n 1` | 0 (`normal`) | C-13 |
| T2I | The lowest `t2i` quote | `price "$(cheapest t2i)"` | 0 (`seedream_4.0`) | C-7, settled by Part 0 |
| I2I | The lowest `i2i` quote | `price "$(cheapest i2i)"` | 0 (`seedream_4.0`) | C-10 |
| T2V | The lowest `t2v` quote | `price "$(cheapest t2v)"` | 16 (`seedance_2.0_mini`) | C-14 |
| M2V | The lowest `m2v` quote with one image | `price "$(cheapest m2v "" 1)"` | 16 (`seedance_2.0_mini`) | V-3 |
| M2V-E | `m2v` with C-15's Element | C-15b's quote | C-15 fills | E-1 |

Then:

1. Each number is written next to its name in the credit columns of Parts 1
   to 4, as "T2I (0)", and each Part 3 row's `price` is in its Credits cell.
1. The Totals table's last column holds each Part's sum.
1. Write the catalog's [Prices](research/catalog.md#prices) table: one row per
   check, from the captures:

   ```sh
   jq -r --rawfile p "$CAP/price-sweep.tsv" '
     ($p | split("\n") | map(select(length > 0) | split("\t") | {key: .[0], value: .}) | from_entries) as $prices
     | ($prices[.name] // []) as $row
     | (.args // [])[3:] as $a
     | [range(0; $a | length; 2) as $i | select(($a[$i] | IN("--project-id", "--model", "--prompt", "--ref", "--mode", "--scenario")) | not)
         | "\($a[$i] | ltrimstr("--")) \($a[$i + 1])"] as $settings
     | "| `\(.model)` | \(.mode)\(if .scenario != "" then " " + .scenario else "" end)\(if .refs > 0 then ", \(.refs) reference" + (if .refs > 1 then "s" else "" end) else "" end) | \(if .skip then "not checked: " + .skip else ($settings | join(", ")) end) | \($row[7] // "") |"' \
     "$CAP/price-sweep-jobs.jsonl"
   ```

   Add the four upscale rows by hand from `price-sweep.tsv`.

### Step 9: Record Part 0

1. The owner reads the balance when convenient; nothing waits for it. It
   should equal the reading before Part 0, since Part 0 billed nothing. A
   drop is reported, as [Approval](#approval)'s last rule says
   ([22-owner-setup.md](22-owner-setup.md#step-4-watch-the-credits)).
1. Add a row to 02's results ("Part 0 price sweep") and a row to the changes
   table: the canvas, the uploads, how many checks priced, refused, or ran,
   the cheapest model of each mode, the defaults, and the drafts left (one
   per check, on "ComfyUI tests").
1. Captures written in Steps 2 to 6: `canvas-create.json` and
   `canvas-create-retry.json` (C-1), `resource-upload-image.json`,
   `resource-upload-audio.json`, and `resource-upload-video.json` (C-2 to
   C-4), `node-create-import.json`, `error-confirmation-required.json`,
   `node-upscale-quote.json`, `price-sweep.tsv`, and
   `price-sweep-jobs.jsonl`.

## Part 1: Contract checks

Runs C-0 to C-17 are the facts in 02's
[Facts to confirm by test runs](02-dreamina-contract.md#facts-to-confirm-by-test-runs),
in its numbering. They are sent with the CLI outside ComfyUI, on the test
canvas, at milestone 4, because 06, 07, and 08 are written against them.
Every block runs in `part-1`; C-14's resume runs there in a new Bash call.

C-12 differs from 02's list: no music model is listed
([research/catalog.md](research/catalog.md#audio-models)), so C-12 checks the
omni dubbing references instead, which 11 needs.

| Run | Confirms | Credits |
| --- | -------- | ------- |
| C-0 | The plan gate and the list format. Done on 2026-10-16 | Free |
| C-1 | The `canvas create` reply, and a retry with the same ID | Free |
| C-2 | The PNG upload reply; the upload size limit; an upload downloaded back | Free |
| C-3 | The MP4 upload; whether `resource download` returns a video | Free |
| C-4 | WAV and MP3 uploads; whether `resource download` returns audio | Free |
| C-5 | The exit 10 reply; `node quote` agrees; a ceiling one credit low stops | Free |
| C-6 | `{{res:<uuid>}}` in a prompt binds an upload | Free |
| C-7 | The run reply on acceptance, without `--wait`. Settled by Part 0 on 2026-10-17 | T2I (0), run in Part 0 |
| C-8 | `operation wait` states and `resources[]`; `node show`; an image download. Settled by Part 0 on 2026-10-17 | C-7's run |
| C-9 | Values the server refuses: exit code, `error.validation` | Free |
| C-10 | `i2i` with an uploaded image and its placeholder | I2I (0) |
| C-11 | Speech with a voice; text reading's audio reference; audio downloads | AUD-D (12) + C-11b's quote (12) |
| C-12 | Omni dubbing references at save: one image, image and audio together, audio under 3 seconds | Free |
| C-13 | An imported upload upscaled; the upscale reply | UP (0) |
| C-14 | A video run whose wait is killed, then resumed from a new process; a video download | T2V (16), counted in Part 3 |
| C-15 | An Element from an upload; an `m2v` quote with it; a canvas that does not exist | Free |
| C-16 | `operation status` of an unknown submit ID; every exit code met | Free |
| C-17 | Whether a failed generation is billed | 2 (the cheapest priced `i2i`), only if its save passes |
| | **Total** | **I2I (0) + AUD-D (12) + C-11b's quote (12) + UP (0) + C-17's quote (2) = 26** |

### C-0: the plan gate

Done on 2026-10-16 ([Part 0](#done-on-2026-10-16)).

- **Confirms:** the account can use the CLI; `isVip` and `vipLevel`; how
  `model list` writes `flags[].flag`; which flags each mode lists.
- **Result:** `isVip` `true`, `vipLevel` `standard`; 12 image, 5 video, and 2
  audio models; flags written with two dashes; `ratio`, `resolution`, and
  `duration` required with no defaults; `first_last_frame` listed twice;
  `mediaType` values `image`, `video`, and `audio`.
- **Record in:** done in 02's results, the catalog's Account section, and 22.

### C-1: canvas create

Part 0 Step 2's calls.

- **Confirms:** the reply's fields (`project.projectId`, `name`, `createdAt`,
  `updatedAt`, `webUrl`, `draftVersion`, `current`, and any
  `localStorageWarning`); what a second create with the same `--project-id`
  answers.
- **Expect:** exit 0 and `projectId` equal to `T`; the retry answers the same
  canvas, or a failure whose `error.code` says it exists; `canvas ls` shows
  one "ComfyUI tests".
- **Record in:** 02's Canvases; 08's `create_canvas`, whose retry after a lost
  reply depends on it. Captures `canvas-create.json` and
  `canvas-create-retry.json`.

### C-2: PNG upload and its size limit

Step 3 uploaded `apple.png`. Make three incompressible PNGs of about 5, 20,
and 60 MB with F's standard-library generator, upload them, and download
`apple.png` back:

```sh
/usr/bin/python3 -I -c '
import os, struct, zlib
for name, side in (("5m", 1300), ("20m", 2590), ("60m", 4480)):
    rows = b"".join(b"\x00" + os.urandom(side * 3) for _ in range(side))
    def chunk(kind, body): return struct.pack(">I", len(body)) + kind + body + struct.pack(">I", zlib.crc32(kind + body))
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", side, side, 8, 2, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(rows, 0)) + chunk(b"IEND", b"")
    open(f"noise-{name}.png", "wb").write(png)
'
for size in 5m 20m 60m; do
  dr "c02-upload-$size" resource upload --project-id "$T" --file "$PWD/noise-$size.png" --type image --resource-id "$(new_id)"
done
jq '.data' ../part-0/upload-apple.json
dr c02-get resource get "$PNG" --project-id "$T"
dr c02-download resource download "$PNG" --project-id "$T" --output "$PWD/c02-apple.png"
jq '.data' c02-get.json c02-download.json
shasum -a 256 ../part-0/apple.png c02-apple.png
```

- **Confirms:** the upload reply (`resourceId`, `mediaType`); the largest
  accepted image and the refusal past it; that an upload downloads back,
  byte for byte or transcoded.
- **Expect:** `apple.png` and the 5 MB file accepted. The models take images
  up to 50 MB ([research/catalog.md](research/catalog.md#file-limits)), so the
  60 MB file may be refused; the refusal's exit code and `error` fields are
  the result. The download's `sha256` equals the local file's, or the
  difference shows Dreamina re-encodes uploads.
- **Record in:** 02's Uploads; 07's upload step and its encode-size message;
  05's `max_upload_megabytes` range. Captures `resource-upload-image.json` and
  `resource-get.json`, and the refusal as `error-<code>.json`.

### C-3: MP4 upload and video download

```sh
jq '.data' ../part-0/upload-clip.json
dr c03-get resource get "$MP4" --project-id "$T"
dr c03-download resource download "$MP4" --project-id "$T" --output "$PWD/c03-clip.mp4"
jq '.data, .error' c03-download.json c03-download.err.json
probe c03-clip.mp4
shasum -a 256 ../part-0/clip.mp4 c03-clip.mp4
```

- **Confirms:** an MP4 uploads; whether `resource download`, whose summary
  says "Safely download a successful image resource", returns a video.
- **Expect:** the upload accepted with `mediaType` `video`. The download is the
  open question. A refusal here is not final: the pack downloads generated
  videos, not uploads, and C-14 settles that.
- **Record in:** 02's Downloads; 07's download step; 10 and 14. Capture
  `resource-upload-video.json`, and `resource-download-video.json` or the
  refusal.

### C-4: WAV and MP3 uploads, and audio download

```sh
jq '.data' ../part-0/upload-tone.json
dr c04-upload-mp3 resource upload --project-id "$T" --file "$PWD/../part-0/tone.mp3" --type audio --resource-id "$MP3"
dr c04-upload-short resource upload --project-id "$T" --file "$PWD/../part-0/short.wav" --type audio --resource-id "$SHORT"
for id in "$WAV" "$MP3"; do
  dr "c04-download-$id" resource download "$id" --project-id "$T" --output "$PWD/c04-$id.audio"
  probe "c04-$id.audio"
done
```

- **Confirms:** Dreamina accepts 16-bit WAV, the pack's upload format, and MP3,
  its fallback ([01-decisions.md](01-decisions.md#media-formats)); whether
  audio downloads back. `short.wav` is uploaded here for C-12.
- **Expect:** both accepted with `mediaType` `audio`; the downloads are the
  open question, settled for generated audio by C-11.
- **Record in:** 02's Uploads and Downloads; 07 (WAV, or MP3 through PyAV if
  WAV is refused); 11. Capture `resource-upload-audio.json`.

### C-5: the exit 10 reply

Free. Part 0's price checks are C-5's main evidence; these calls add a
read-only quote and a ceiling one credit below the price, on the cheapest
model quoted above 0 (`seedream_4.0` is free):

```sh
J=$(cheapest_priced t2i)
P=$(price "$J")
jq . "$CAP/error-confirmation-required.json"
run_job c05-low "$J" "$((P - 1))"
jq '{error, creditConfirmation, partialData}' c05-low.err.json
N=$(jq -r '.partialData.items[0].nodeId' c05-low.err.json)
dr c05-quote node quote --project-id "$T" --node-id "$N"
dr c05-show node show --project-id "$T" --node-id "$N"
jq '.data' c05-quote.json
jq '.data.nodes[0].node | {status, resources, generation: .generation.mode}' c05-show.json
cat c05-low.submit
jq -r '.partialData.items[0].submitId' c05-low.err.json
```

- **Confirms:** exit 10 with `error.code` `cli.generation_credit_ceiling_too_low`,
  `class` `confirmation_required`, `requiredAction` `confirm`,
  `creditConfirmation.reason` `ceiling_too_low` and `minimumCreditCeiling`, and `partialData.items[].nodeId` and `submitId`;
  that `partialData`'s submit ID is the one sent; that `node quote`'s
  `maxCredits` equals `minimumCreditCeiling`; that a ceiling one credit below
  the quote stops the run; that the draft has no resources.
- **Expect:** all of the above, nothing billed. If the run with `P - 1` is
  accepted instead, stop every paid run and tell the owner: the ceiling does
  not hold.
- **Record in:** 02's Credit approval; 08's failure map and `CliReply`.
  Capture `node-quote.json`.

### C-6: a placeholder for an upload

Free: both saves stop at the ceiling of 0, and `node show` reads the drafts.

```sh
J=$(cheapest_priced i2i)
M=$(flag_of "$J" --model)
R=$(flag_of "$J" --resolution)
run_job c06a "$J" 0 "Make {{res:$PNG}} green."
dr c06b node create image --project-id "$T" --mode i2i --model "$M" --prompt "Make {{res:$PNG}} green." \
  --ratio 1:1 --resolution "$R" --count 1 --run --credit-ceiling 0 --submit-id "$(new_id)"
for n in c06a c06b; do
  printf '%s exit %s\n' "$n" "$(cat "$n.exit")"
  N=$(jq -r '.partialData.items[0].nodeId // empty' "$n.err.json")
  if [ -n "$N" ]; then
    dr "$n-show" node show --project-id "$T" --node-id "$N"
    jq '.data.nodes[0].node.generation | {prompt, references, promptParts}' "$n-show.json"
  else
    jq -c .error "$n.err.json"
  fi
done
```

- **Confirms:** C-6a, a placeholder with the same resource in `--ref`: the
  saved `generation.prompt` keeps `{{res:<uuid>}}`, `references[]` holds one
  slot, and `promptParts[]` has a reference part whose `referenceIndex` points
  at it. C-6b, the placeholder alone: whether it adds the reference by itself.
- **Expect:** C-6a binds and merges into one slot. C-6b is the open question.
- **Record in:** 01's Placeholders, 07's `format_prompt`, and 23. If
  C-6a does not bind, placeholders are limited to `references` (node IDs), as
  01 says. Capture `node-show-placeholder.json`.

### C-7: the run reply on acceptance

Settled by Part 0 on 2026-10-17
([Part 0](#steps-1-to-8-done-on-2026-10-17)): the free `seedream_4.0` runs
gave this reply, with `submission.state` `accepted`. The block below is not
run again. It was planned as the first paid run: the cheapest image at its
cheapest settings, without `--wait`.

```sh
J=$(cheapest t2i)
run_job c07 "$J" "$(price "$J")"
jq '.data | {node: .node.nodeId, status: .node.status, mutation, quote, approval, submission}' c07.json
clean c07.json > "$CAP/run-accepted.json"
```

- **Confirms:** the reply returns as soon as Dreamina accepts the run; its
  fields. The schema shows `node`, `mutation`, `quote` (`maxCredits`,
  `draftVersion`, `confirmable`, `confirmationRequired`), `approval`
  (`creditCeiling`), and `submission` (`submitId`, `state`, `resources`,
  `error`). 02 expects run items (`items[].nodeId`, `submitId`, `state`), as
  `node run` returns them.
- **Expect:** exit 0 in a few seconds; `submission.submitId` equal to
  `c07.submit`; `submission.state` an accepted value; `quote.maxCredits` equal
  to T2I.
- **Record in:** 02's Generation runs; 08's `RunReply` and the record step,
  which need only the node ID and the state. Credits: T2I (0).

### C-8: the wait, node show, and the download

Settled by Part 0 on 2026-10-17
([Part 0](#steps-1-to-8-done-on-2026-10-17)): operation `state` `succeeded`,
`submission.state` `completed`, resource `state` `succeeded`, `node show`
resource `status` `success`, a JPEG of 2048×2048 at `2K` `1:1`, and a
download whose size and SHA256 matched. C-14's longer video run captures the
running states and a wait that runs out (exit 20). The block below is not run
again. It continues C-7:

```sh
S=$(cat c07.submit)
N=$(jq -r .data.node.nodeId c07.json)
wait_for c07 "$S" "$T"
jq -c '.data | {state, resources: [.resources[]? | {state, width, height, format}]}' c07-status-*.json
jq '.error' c07-wait-1.err.json
jq '.data' c07-terminal.json
download_outputs c07 "$N" "$S" "$T" "$(jq -r '.data.resources[0].format // "image"' c07-terminal.json)"
jq '.data.nodes[0].node | {status, resources, generation}' c07-show.json
probe c07-1.*
```

- **Confirms:** the state values of `operation status` while running and of
  `operation wait` at the end, on both axes (the operation `state` and each
  resource's `state`); the exit 20 reply of a wait that runs out; the terminal
  reply (`operationRef`, `state`, `resources[]` with `width`, `height`,
  `format`, `submission`); `node show`'s resources with `submitId` and
  `creditsAmount`; that `resource download` returns the image, with `size` and
  `sha256` that match the file.
- **Expect:** one or more running reads, then a terminal success with one
  resource; the downloaded image is square, with the size the resolution
  sent sets.
- **Record in:** 02's Waiting and recovery and Reading a finished node; 08's
  `OPERATION_STATES` (in `src/config/generations.py`), the wait loop, and the
  download checks. Captures `operation-status-running.json`,
  `operation-wait-incomplete.json` (an exit 20 reply),
  `operation-wait-terminal.json`, `node-show.json`, and
  `resource-download.json`.

### C-9: values the server refuses

Free: every call carries a ceiling of 0, so a value the server accepts stops
at the quote.

```sh
J=$(cheapest_priced t2i)
M=$(flag_of "$J" --model)
R=$(flag_of "$J" --resolution)
dr c09a node create image --project-id "$T" --mode t2i --model "$M" --prompt "A red apple on a white table." \
  --ratio 5:4 --resolution "$R" --count 1 --run --credit-ceiling 0 --submit-id "$(new_id)"
dr c09b node create image --project-id "$T" --mode t2i --model "$M" --prompt "A red apple on a white table." \
  --ratio 1:1 --resolution "$R" --count 99 --run --credit-ceiling 0 --submit-id "$(new_id)"
dr c09c node create video --project-id "$T" --mode t2v --model seedance_2.0_fast --prompt "Waves on a beach at sunset." \
  --ratio 16:9 --resolution 720p --duration 2 --count 1 --run --credit-ceiling 0 --submit-id "$(new_id)"
dr c09d node create video --project-id "$T" --mode t2v --model seedance_2.0_fast --prompt "Waves on a beach at sunset." \
  --ratio 16:9 --resolution 1080p --duration 4 --count 1 --run --credit-ceiling 0 --submit-id "$(new_id)"
dr c09e node create video --project-id "$T" --mode t2v --model seedance_2.0_fast --prompt "Waves on a beach at sunset." \
  --resolution 720p --duration 4 --count 1 --run --credit-ceiling 0 --submit-id "$(new_id)"
for n in c09a c09b c09c c09d c09e; do printf '%s exit %s ' "$n" "$(cat "$n.exit")"; jq -c '{error, creditConfirmation}' "$n.err.json"; done
```

The values: a ratio not in the list (`5:4`), a count above the maximum (99),
a duration below the minimum (2, minimum 4), a resolution the model does not
list (`1080p`), and a required flag left out (`--ratio`). The pack refuses
all five before paying ([01-decisions.md](01-decisions.md#checking-a-model-before-paying));
these calls skip the pack to see what the CLI and the server do.

- **Confirms:** for each value, whether the CLI refuses it locally (exit 2),
  the server refuses it at save (which exit, `error.class`, `error.code`,
  `error.validation.reasonCode`, `fieldPath`, and `detail`), or Dreamina
  quotes it anyway (exit 10).
- **Expect:** refusals with `class` `invalid_input`. A refusal after the save
  leaves a draft.
- **Record in:** 02's Exit codes and failure fields; 08's failure map. The
  pack keeps its own checks either way, because a refusal after the save
  leaves a draft. Captures `error-<code>.json` for each new code.

### C-10: i2i with an uploaded image

The run of C-6a's values:

```sh
J=$(cheapest i2i)
run_job c10 "$J" "$(price "$J")" "Make {{res:$PNG}} green."
S=$(cat c10.submit)
N=$(jq -r .data.node.nodeId c10.json)
wait_for c10 "$S" "$T"
download_outputs c10 "$N" "$S" "$T" "$(jq -r '.data.resources[0].format // "image"' c10-terminal.json)"
jq '.data.nodes[0].node | {upstreamNodeIds, generation: {prompt: .generation.prompt, references: .generation.references}}' c10-show.json
```

- **Confirms:** an upload works as an `i2i` reference, with its placeholder,
  end to end.
- **Expect:** the disc turns green, on white, 1:1. Look at the file.
- **Record in:** 09's live checks. Credits: I2I (0).

### C-11: speech, voices, and audio downloads

Two parts, in order. C-11a: text reading with a voice.

```sh
J=$(job seed_audio_v1 tts text-reading)
run_job c11a "$J" "$(price "$J")" "Hello from Dreamina. This is a short test of speech."
wait_for c11a "$(cat c11a.submit)" "$T"
download_outputs c11a "$(jq -r .data.node.nodeId c11a.json)" "$(cat c11a.submit)" "$T" "$(jq -r '.data.resources[0].format // "audio"' c11a-terminal.json)"
probe c11a-1.*
```

C-11b: text reading in another voice, Good Guy, with C-11a's speech in
Jessie's voice as its one audio reference. Quote it free, then run it at that
quote:

```sh
A11=$(jq -r .data.node.nodeId c11a.json)
set -- --mode tts --scenario text-reading --model seed_audio_v1 --voice-name "Good Guy" \
  --prompt "Hello from Dreamina. Whose voice is this?" --ref "node:$A11"
dr c11b-quote node create audio --project-id "$T" "$@" --run --credit-ceiling 0 --submit-id "$(new_id)"
P=$(jq -r .creditConfirmation.minimumCreditCeiling c11b-quote.err.json)
new_id > c11b.submit
dr c11b node create audio --project-id "$T" "$@" --run --credit-ceiling "$P" --submit-id "$(cat c11b.submit)"
wait_for c11b "$(cat c11b.submit)" "$T"
download_outputs c11b "$(jq -r .data.node.nodeId c11b.json)" "$(cat c11b.submit)" "$T" "$(jq -r '.data.resources[0].format // "audio"' c11b-terminal.json)"
probe c11b-1.*
```

- **Confirms:** speech with a voice works and its audio downloads (format,
  sample rate, channels, duration); whether text reading's one audio
  reference acts as a voice sample (C-11b sounds like Jessie, not Good Guy).
- **Expect:** C-11a downloads as a playable file of about 3 seconds. C-11b is
  the open question, so listen to it.
- **Record in:** 02's Voices and Downloads; 11's live checks and help page;
  15's voice list; the catalog's Audio models notes. Credits: AUD-D (12) +
  C-11b's quote (12).

### C-12: omni dubbing references

Free: every save stops at the ceiling of 0, or is refused before the quote.

```sh
dr c12a node create audio --project-id "$T" --mode tts --model seed_audio_v1 --scenario omni-dubbing \
  --prompt "Hello from Dreamina." --ref "res:$PNG" --run --credit-ceiling 0 --submit-id "$(new_id)"
dr c12b node create audio --project-id "$T" --mode tts --model seed_audio_v1 --scenario omni-dubbing \
  --prompt "Hello from Dreamina." --ref "res:$PNG" --ref "res:$WAV" --run --credit-ceiling 0 --submit-id "$(new_id)"
dr c12c node create audio --project-id "$T" --mode tts --model seed_audio_v1 --scenario omni-dubbing \
  --prompt "Hello from Dreamina." --ref "res:$WAV" --run --credit-ceiling 0 --submit-id "$(new_id)"
dr c12d node create audio --project-id "$T" --mode tts --model seed_audio_v1 --scenario omni-dubbing \
  --prompt "Hello from Dreamina." --ref "res:$SHORT" --run --credit-ceiling 0 --submit-id "$(new_id)"
dr c12e node create audio --project-id "$T" --mode tts --model seed_audio_v1 --scenario text-reading --voice-name Jessie \
  --prompt "Hello from Dreamina." --ref "res:$SHORT" --run --credit-ceiling 0 --submit-id "$(new_id)"
for n in c12a c12b c12c c12d c12e; do printf '%s exit %s ' "$n" "$(cat "$n.exit")"; jq -c '{error, creditConfirmation}' "$n.err.json"; done
```

| Call | References | Expect |
| ---- | ---------- | ------ |
| c12a | One image | Exit 10 with a price: DUB (12) |
| c12b | One image and one audio | Refused (`mutuallyExclusiveTypes` `["image", "audio"]`) |
| c12c | One 5-second audio | Exit 10 with a price |
| c12d | One 2-second audio | Refused at save: under `minDurationMs` 3000 |
| c12e | Text reading with a 2-second audio | Refused at save, the same limit |

- **Confirms:** the price of omni dubbing with an image; where each refusal
  happens (the CLI locally, exit 2, which release 1.0.3's notes suggest with
  "preflight references against model specifications", or the server at
  save) and its `error` fields; that the server enforces the audio length
  limit at save, before any charge, as the catalog's
  [File limits](research/catalog.md#file-limits) assumes.
- **Record in:** 02's Generation runs (omni dubbing) and What is billed; 06's
  reference checks; 11; the catalog. C-12a confirms DUB in
  [Step 8's table](#step-8-prices-the-later-tables-use). Captures
  `error-<code>.json` for each new code.

### C-13: upscale an imported image

Part 0 Step 6 quoted all four variants, found the imported node an eligible
source, and found `normal` the cheapest, at 0. Run `normal`, at a ceiling of
0:

```sh
N=$(jq -r .data.node.nodeId "$CAP/node-create-import.json")
new_id > c13.submit
dr c13 node upscale image --project-id "$T" --node-id "$N" --submit-id "$(cat c13.submit)" --mode normal --credit-ceiling 0
jq '.data' c13.json
O=$(jq -r '.data.items[0].nodeId' c13.json)
wait_for c13 "$(cat c13.submit)" "$T"
download_outputs c13 "$O" "$(cat c13.submit)" "$T" "$(jq -r '.data.resources[0].format // "image"' c13-terminal.json)"
probe c13-1.*
```

- **Confirms:** an imported upload is an "eligible successful image"; the
  reply's `items[]` (`sourceNodeId`, `submitId`, `nodeId`, `resourceIds`,
  `state`, `authorizedCredits`), `totalMaxCredits`, and `creditsApproved`;
  that `operation wait` follows an upscale's submit ID; the output's size.
- **Expect:** exit 0, a new node, and a 2560×1440 PNG, twice the source's
  size, as Part 0 Step 6's free `normal` run gave.
- **Record in:** 02's Image upscale; 12's import path and `UpscaleOperation`;
  04's upscale flow. Capture `node-upscale-run.json`. Credits: UP (0).

### C-14: a killed wait, resumed from a new process

The cheapest video at its lowest settings: `seedance_2.0_mini` `t2v`, `720p`,
4 seconds. Its credits count in Part 3, where it fills S-4.

```sh
J=$(cheapest t2v)
run_job c14 "$J" "$(price "$J")"
S=$(cat c14.submit)
"$B" --format json --non-interactive operation wait "$S" --project-id "$T" --timeout 10m < /dev/null > c14-killed.json 2> c14-killed.err.json &
W=$!
dr c14-status-0 operation status "$S" --project-id "$T"
kill -KILL "$W"
wait "$W"
printf 'killed wait: exit %s\n' "$?"
date +%s > c14.killed
```

The pack kills a CLI process the same way on a ComfyUI cancel
([04-architecture.md](04-architecture.md#threads-event-loops-and-subprocesses)).
Then, in a new Bash call, which is a new process with nothing in memory:

```sh
S=$(cat c14.submit)
N=$(jq -r .data.node.nodeId c14.json)
dr c14-journal operation status "$S"
wait_for c14 "$S" "$T"
download_outputs c14 "$N" "$S" "$T" mp4
probe c14-1.mp4
```

- **Confirms:** a killed wait leaves the run going and the CLI's journal
  readable; `operation status` without `--project-id` finds the run through
  the journal; a new `operation wait` from another process follows it to the
  end; `resource download` returns a generated video; the video's state
  values, `width`, `height`, and `format`; how long a cheapest video takes.
- **Expect:** the kill ends the wait at once; the resumed wait ends in success
  with one resource; the MP4 plays, with the size and duration the settings
  ask for.
- **Record in:** 02's Waiting and recovery and Downloads; 08's wait loop,
  cancel step, and `CollectOperation`, which 14 calls; 10. If the video cannot be downloaded,
  [What the runs change](#what-the-runs-change) applies before the Video
  milestone. Credits: T2V (16), in Part 3's total.

### C-15: an Element, and a canvas that does not exist

Free. Elements generate nothing, the quote stops at 0, and a canvas that does
not exist fails before any quote.

```sh
dr c15-element node create element --project-id "$T" --main "$PNG" --title "Test ball" --description "A red ball on white."
dr c15-element-voice node create element --project-id "$T" --main "$PNG" --voice "$WAV" --auxiliary "$PNG2" --title "Test ball with a voice"
E=$(jq -r .data.node.nodeId c15-element.json)
dr c15-element-show node show --project-id "$T" --node-id "$E"
jq '.data.nodes[0].node | {type, status, title, subjectBindings}' c15-element-show.json
jq -c '{error}' c15-element-voice.err.json
J=$(cheapest m2v "" 1)
M=$(flag_of "$J" --model)
R=$(flag_of "$J" --resolution)
D=$(flag_of "$J" --duration)
dr c15b node create video --project-id "$T" --mode m2v --model "$M" --prompt "{{node:$E}} rolls slowly across a wooden table." \
  --ref "node:$E" --ratio 16:9 --resolution "$R" --duration "$D" --count 1 --run --credit-ceiling 0 --submit-id "$(new_id)"
jq -c '{error, creditConfirmation}' c15b.err.json
```

If `c15b` is refused because an Element alone does not meet `m2v`'s
`requireAnyOfTypes` (image or video), send it again with `--ref "res:$PNG"`
added after the Element, as `c15c`, and record both.

Then a canvas that does not exist, a new random ID:

```sh
GONE=$(new_id)
dr c15-gone-upload resource upload --project-id "$GONE" --file "$PWD/../part-0/apple.png" --type image --resource-id "$(new_id)"
dr c15-gone-run node create image --project-id "$GONE" --mode t2i --model seedream_5.0_lite --prompt "A red apple on a white table." \
  --ratio 1:1 --resolution 2K --count 1 --run --credit-ceiling 0 --submit-id "$(new_id)"
dr c15-gone-element node create element --project-id "$GONE" --main "$PNG"
for n in c15-gone-upload c15-gone-run c15-gone-element; do printf '%s exit %s ' "$n" "$(cat "$n.exit")"; jq -c .error "$n.err.json"; done
```

- **Confirms:** an Element binds an upload as `--main` (bare resource ID),
  with `subjectBindings` in the reply; whether a tone is accepted as
  `--voice`; how an Element counts in `m2v`'s reference limits, and its price
  (M2V-E); the error a missing canvas gives for an upload, a run, and an
  Element. The skill says a missing, forbidden, or unlinked ID all return "the
  **same** error", so the code is read for the canvas target only.
- **Expect:** the Element saved for free; the `m2v` quote at exit 10; one
  error code, the same for all three calls on the missing canvas, before any
  quote.
- **Record in:** 02's Elements and Canvases; 13; 06's reference counting for
  Elements; 08's message for a canvas deleted during a run, which fails that
  run with nothing sent again. `find_canvas` does not rely on this code: it
  checks `canvas ls` before each run, and `create_canvas` makes a new canvas
  before any upload. M2V-E in
  [Step 8's table](#step-8-prices-the-later-tables-use). Captures
  `node-create-element.json` and `error-<code>.json`.

### C-16: an unknown submit ID, and the exit codes met

Free:

```sh
U=$(new_id)
dr c16-status operation status "$U" --project-id "$T"
dr c16-status-journal operation status "$U"
dr c16-wait operation wait "$U" --project-id "$T" --timeout 0
for n in c16-status c16-status-journal c16-wait; do printf '%s exit %s ' "$n" "$(cat "$n.exit")"; jq -c '.data // .error' "$n.json" "$n.err.json" 2> /dev/null; done
for f in "$RUNS"/part-0/*.err.json "$RUNS"/part-1/*.err.json; do
  [ -s "$f" ] && jq -r --arg f "${f##*/}" --arg x "$(cat "${f%.err.json}.exit")" \
    '[$x, .error.code, .error.class, .error.requiredAction, (.error.retryable | tostring), $f] | @tsv' "$f"
done | sort -t "$(printf '\t')" -u -k1,4 > c16-exit-codes.tsv
column -t -s "$(printf '\t')" c16-exit-codes.tsv
```

- **Confirms:** what Dreamina answers for a submit ID it never saw: an error,
  or `submission.state` `absent`; every exit code met in Parts 0 and 1 with
  its `error.code`, `class`, `requiredAction`, and `retryable`, including any
  of the undocumented 1, 12, 13, 21, and 22.
- **Expect:** an unknown submission reads as `absent` or a not-found error,
  never as success.
- **Record in:** 02's Exit codes table; 08's failure map; 14's message for a
  record Dreamina no longer has. Run the roll-up again after Part 4 with
  every Part's folder.

### C-17: whether a failed generation is billed

There is no safe way to make a generation fail on purpose that is sure to
work. A prompt written to trip the safety check is not used: it could count
against the owner's account. Instead, C-17 tries an input that is legal at
save but may fail in the run, and records what happens.

```sh
dr c17-upload resource upload --project-id "$T" --file "$PWD/../part-0/tiny.png" --type image --resource-id "$TINY"
J=$(cheapest_priced i2i)
M=$(flag_of "$J" --model)
R=$(flag_of "$J" --resolution)
dr c17-quote node create image --project-id "$T" --mode i2i --model "$M" --prompt "Make the red square blue." \
  --ratio 1:1 --resolution "$R" --count 1 --ref "res:$TINY" --run --credit-ceiling 0 --submit-id "$(new_id)"
dr c17-limit node create video --project-id "$T" --mode m2v --model seedance_2.5 --prompt "The square spins." \
  --ref "res:$TINY" --ratio 16:9 --resolution 480p --duration 4 --count 1 --run --credit-ceiling 0 --submit-id "$(new_id)"
for n in c17-quote c17-limit; do printf '%s exit %s ' "$n" "$(cat "$n.exit")"; jq -c '{error, creditConfirmation}' "$n.err.json"; done
```

`c17-limit` is free in every case: a 16-pixel image is below `seedance_2.5`'s
300-pixel minimum for `m2v` images, so it checks that the server refuses an
undersized file at save.

When `c17-quote` stops at exit 10 with a price:

1. The owner reads the balance, and no other run happens until the second
   reading.
1. Run it at that quote:

   ```sh
   P=$(jq -r .creditConfirmation.minimumCreditCeiling c17-quote.err.json)
   new_id > c17.submit
   dr c17 node create image --project-id "$T" --mode i2i --model "$M" --prompt "Make the red square blue." \
     --ratio 1:1 --resolution "$R" --count 1 --ref "res:$TINY" --run --credit-ceiling "$P" --submit-id "$(cat c17.submit)"
   wait_for c17 "$(cat c17.submit)" "$T"
   jq '.data | {state, resources, submissionError}' c17-terminal.json
   ```

1. Ten minutes after the run ends, the owner reads the balance again.

- **Confirms:** whether a failed generation is billed: the balance before and
  after, and `creditsAmount` on the failed resource.
- **Expect:** the run either succeeds (an upscaled square: record "no failure
  reached", and C-17 stays open) or fails with `submissionError` or a failed
  resource. Any generation that fails in Parts 2 to 4 is checked the same way,
  with the balance read before and after, and settles C-17 if this one does
  not.
- **Record in:** 02's What is billed when something fails; the failure
  messages in 08 and 01's Errors; 18's ADVANCED sentence on failed runs; 22's
  question on refunds. Credits: 2, only when `c17-quote` priced it. C-17
  uses the cheapest `i2i` quoted above 0, because a free model would show no
  charge either way.

## Part 2: First run of each node milestone

Each node milestone's first runs go through ComfyUI, after the milestone's
commit and before its example runs, so a fault shows on the smallest run.
Each node plan's live checks step defines its runs, with what each settles and
what to fix when it differs; this table runs them in milestone order and adds
the model check and the refusals. A run's values are the node plan's; where
the node plan and this table differ, the node plan wins and this table is
corrected.

**How to send a run.**

1. Restart ComfyUI with the milestone's nodes, as
   [How to run and record](#how-to-run-and-record) says.
1. Build the graph in the ComfyUI page from the table, and press **Run**. Or
   save it once with **Workflow → Export (API)** into `part-2` as
   `<run>.api.json`, and send it with `comfy_send <run>.api.json`. The comfy-mcp
   `run_workflow` tool on the saved UI file works too.
1. Set `credit_ceiling` to the run's quote, except where the table says the
   default: those runs check that the node's default ceiling covers its
   starting values.

**What to check after each run.**

- The outputs: the saved files in `$COMFY/output/image/dreamina/`,
  `video/dreamina/`, or `audio/dreamina/`, and `result`, read through a
  **Preview Any** node: the node view and the canvas link.
- The generation record: `ls "$STATE/generations"` shows `<submitId>.json`
  while the run waits, and nothing after the outputs are saved.
- The canvas node: `node find --project-id "$(pack_canvas)" --limit 50` lists
  it with its status; its resources carry the run's submit ID.
- ComfyUI's history, `comfy_history <prompt ID>`, for the time. If the entry
  is gone after a restart, the canvas decides.

| # | Milestone | Run | Defined in | Credits |
| - | --------- | --- | ---------- | ------- |
| K-1 | Image | The model check and the refusals, all free ([below](#k-1-the-model-check-and-the-refusals)) | [06-model-check.md](06-model-check.md) | Free |
| I-1 | Image | **Image: Generate** with its starting `model` and `arguments`, `prompt` "A red apple on a white table.", the default `credit_ceiling` → **Save Image** `image/dreamina/i1` | [09-node-image.md](09-node-image.md) | IMG-D (6) |
| I-2 | Image | **Image: Generate**, `references` ← I-1's `references`, `prompt` "Make {{reference1}} green.", starting `arguments`: `i2i` chosen, the reference sent as a node | [09-node-image.md](09-node-image.md) | IMG-DE (6) |
| I-3 | Image | **Image: Generate**, `images` ← **Load Image** `dreamina-test-apple.png`, `prompt` "Make {{image1}} blue."; run again with a new `run_number` | [09-node-image.md](09-node-image.md) | 2 × IMG-DE (12) |
| U-1 | Upscale | **Image: Upscale**, `images` ← **Load Image** `dreamina-test-apple.png` (the import path), starting `arguments` `{"resolution": "2K"}`, the default `credit_ceiling` | [12-node-upscale.md](12-node-upscale.md) | UP-D (2) |
| M-1 | Audio (Model: Info registered) | **Model: Info** for `seedream_5.0_lite`, `seedance_2.5`, `seed_audio_v1`, `nano_banana`, and `no_such_model` | [15-node-model-info.md](15-node-model-info.md) | Free |
| A-1 | Audio | First, free: **Audio: Generate** with `model` `seedance_2.0_fast` is refused, naming **Video: Generate**. Then the starting `model` and `arguments`, `prompt` "Hello from Dreamina.", the default `credit_ceiling` → **Save Audio (Advanced)** `audio/dreamina/a1` | [11-node-audio.md](11-node-audio.md) | AUD-D (12) |
| A-2 | Audio | Omni dubbing: **Audio: Generate**, `references` ← I-1's `references`, `prompt` "A cheerful voice says: hello from Dreamina." First with the starting `arguments` (refused for free: omni dubbing has no `voice-name`), then with `arguments` `{}` | [11-node-audio.md](11-node-audio.md) | DUB (12) |
| D-1 | Video and downloads | **Generation: Download** with no records: the empty-list message. After V-4: collects V-4's run | [14-node-download.md](14-node-download.md) | Free |
| V-1 | Video and downloads | **Video: Generate** with its starting `model` and `arguments`, `prompt` "Waves on a beach at sunset.", sent first with `credit_ceiling` 0 (free: the refusal with Dreamina's quote), then with the default → **Save Video** `video/dreamina/v1` | [10-node-video.md](10-node-video.md) | VID-D (16) |
| V-2 | Video and downloads | **Video: Generate**, `references` ← I-1's `references` (one image, nothing else): the one-image `first_last_frame` entry chosen; `arguments` `{"ratio": "1:1", "resolution": "720p", "duration": 4}`, `prompt` "The apple rolls slowly off the table." | [10-node-video.md](10-node-video.md) | VID-F (16), quoted again at 1:1 |
| V-3 | Video and downloads | **Video: Generate**, `images` ← **Load Image** `dreamina-test-apple.png`, `videos` ← **Load Video** `dreamina-test-clip.mp4`: `m2v` chosen; `model` M2V's model, its cheapest `arguments`, `prompt` "{{image1}} bounces in time with {{video1}}." | [10-node-video.md](10-node-video.md) | M2V (16), quoted again with the video |
| V-4 | Video and downloads | V-1's graph with a new `run_number`; cancel once the record appears in `$STATE/generations`; then D-1 collects it | [10-node-video.md](10-node-video.md), [14](14-node-download.md) | VID-D (16) |
| E-1 | Elements | **Element: Add**, `main` ← **Load Image** `dreamina-test-apple.png`, `title` `Apple`, then **Video: Generate**, `references` ← its `references`: `m2v` chosen; `model` M2V-E's model, its cheapest `arguments`, `prompt` "{{reference1}} rolls across a wooden table." | [13-node-element.md](13-node-element.md) | M2V-E (C-15 fills) |
| | | | **Total** | **IMG-D (6) + 3 × IMG-DE (18) + UP-D (2) + AUD-D (12) + DUB (12) + 2 × VID-D (32) + VID-F (16) + M2V (16) + M2V-E = 114 + M2V-E** |

A run "quoted again" has values no Part 0 check priced exactly. Quote them
first on the test canvas with the CLI and a ceiling of 0, and use that quote
as the run's `credit_ceiling`. For V-2:

```sh
dr v2-quote node create video --project-id "$T" --mode first_last_frame --model seedance_2.0_mini --prompt "The apple rolls slowly off the table." \
  --ref "res:$PNG" --ratio 1:1 --resolution 720p --duration 4 --count 1 --run --credit-ceiling 0 --submit-id "$(new_id)"
jq .creditConfirmation v2-quote.err.json
```

V-3 is the same with `--mode m2v`, M2V's model and flags, and `--ref
"res:$PNG" --ref "res:$MP4"`.

Notes on single runs:

- **I-1** creates the pack's `ComfyUI` canvas, unless K-1's step 6 already
  did: `canvas ls` shows one `ComfyUI`, and `$STATE/canvas.json` holds its ID.
- **I-2** checks that a node reference goes with no download or upload: the
  canvas shows an edge from I-1's node, and `generation.references[]` holds
  `kind` `node`.
- **I-3** checks the upload path and the `{{image1}}` rewrite. The second run
  makes a second upload, with a new resource ID, because the pack keeps no
  upload memory ([01-decisions.md](01-decisions.md#local-media)). With the
  same `run_number`, ComfyUI's cache returns the same outputs and nothing is
  sent.
- **U-1** uses the import path, which only Image: Upscale has. If C-13 showed
  that an imported image cannot be upscaled, U-1 takes `references` ← I-1's
  `references` instead, and 12 is corrected first.
- **M-1** checks that Model: Info shows: both `first_last_frame` entries of
  `seedance_2.5` with their limits; the 13 voices of `seed_audio_v1`; the
  file limits; the alias
  `nano_banana` reported as `gemini_3_image_pro`; and the refusal of
  `no_such_model` with the closest names.
- **A-2** also checks a gap in the starting values: the Audio starting
  `arguments` `{"voice-name": "Jessie"}` fits text reading only. With an image
  connected, the pack refuses it before paying. The refusal message must name
  the mode's flags; 11 and 17 say how the person clears it.
- **V-4** checks the cancel. Cancel with the queue panel's stop button, or
  `curl -sS -X POST "$API/interrupt"`, once `ls "$STATE/generations"` shows the
  record. The node stops at once with the message that the generation keeps
  running and is billed, and names **Generation: Download**; the record stays.
  D-1 then lists it as "<short submit ID> · seedance_2.0_mini · <UTC minute>",
  collects the video, and deletes the record. If V-4's run ends before the
  cancel lands, the node collects it and deletes the record itself; then run
  V-4 again, canceled sooner, and add VID-D to the record.
- **E-1** checks that an Element travels as a node reference and that `m2v`
  is chosen for it. C-15 decides whether it also needs an image.

### K-1: the model check and the refusals

Free: every step is refused before anything is uploaded or paid, except step
6, which Dreamina stops at the quote. Run it right after the Image
milestone's commit, with ComfyUI restarted, so the process starts with no
model list in memory. Count the nodes on the `ComfyUI` canvas before and
after with `node find`, once the canvas exists.

Each step is one **Image: Generate** node with the starting values unless it
says otherwise:

1. **A model not in the list.** `model` `no_such_model`, run twice with
   different `run_number` values. Expect the refusal with the closest
   canonical names, at queue time, both times after a fresh list read: a name
   not found causes one new read of the kind.
1. **A model of another kind.** `model` `seedance_2.0_fast`. Expect the
   refusal naming **Video: Generate**.
1. **A flag the mode does not list.** `arguments` `{"ratio": "1:1",
   "resolution": "2K", "duration": 4}`. Expect the refusal naming
   `duration` and the model's flags.
1. **A value out of range.** `arguments` `{"ratio": "5:4", "resolution":
   "2K"}`, then `{"ratio": "1:1", "resolution": "2K", "count": 9}`. Expect
   refusals naming the allowed ratios, then the count's range (1 to 8).
1. **A required flag left out.** `arguments` `{"resolution": "2K"}`. Expect
   the refusal naming `ratio`.
1. **The ceiling.** The starting values with `credit_ceiling` set to IMG-D
   minus 1. Dreamina stops the run at the quote. Expect 01's message with the
   two numbers: "This run needs (IMG-D) credits, more than its
   credit_ceiling of (IMG-D minus 1). Nothing was billed. Raise
   credit_ceiling to (IMG-D) or more to run it."; a draft on the `ComfyUI`
   canvas; no generation record. This step creates the canvas if it does not
   exist.

Steps 1 to 5 leave nothing on the canvas. The second run of a refused model
in step 1 is not taken from memory, while steps 2 to 5, after the first read,
answer at once from the process's list.

- **Confirms:** 06's read, match, and checks refuse before paying; the cache
  per process; the ceiling refusal's message and its draft.
- **Record in:** [06-model-check.md](06-model-check.md); 08's ceiling message.
  A step that sends anything is a fault, fixed before the first paid run.

## Part 3: Video model sweep

The owner asked to test as many video models as possible. The account lists
five, all Seedance ([research/catalog.md](research/catalog.md#video-models)):

| Model | Resolutions | Durations | Modes |
| ----- | ----------- | --------- | ----- |
| `seedance_2.5` | 480p, 720p, 1080p | 4 to 30 seconds | `t2v`, `first_last_frame` (2 or 1 image), `m2v` |
| `seedance_2.0` | 720p, 1080p, 4K | 4 to 15 | `t2v`, `first_last_frame` (2 or 1), `m2v` |
| `seedance_2.0_fast` | 720p | 4 to 15 | `t2v`, `first_last_frame` (2 or 1), `m2v` |
| `seedance_2.0_mini` | 720p | 4 to 15 | `t2v`, `first_last_frame` (2 or 1), `m2v` |
| `seedance_pro_fast` | 720p, 1080p | 5 to 10 | `t2v`, `first_last_frame` (1 image only); no `m2v` |

The sweep runs at milestone 14, through **Video: Generate** in ComfyUI, so the
node path is tested on every model. When ComfyUI is busy with the other
session's work, a row runs through the CLI on the test canvas instead.

Every row runs at the lowest resolution and the shortest duration its model
allows, and `count` 1. A round 2 row changes one other thing, and keeps the
lowest resolution and the shortest duration. No row tests a higher
resolution or a longer video.

### Round 1: every model and mode at its cheapest settings

Eighteen rows, one per Part 0 price check of a video model, at 16:9, the
lowest resolution, the shortest duration, and `count` 1. Run them in this
order: the `t2v` rows, then the one-image `first_last_frame` rows, then the
two-image rows, then the `m2v` rows; within each group, in rising price.
Rows an earlier run filled are not run again.

| Row | Price check | Filled earlier by | Credits |
| --- | ----------- | ----------------- | ------- |
| S-1 | `seedance_2.5+t2v` | | 48 |
| S-2 | `seedance_2.0+t2v` | | 52 |
| S-3 | `seedance_2.0_fast+t2v` | | 24 |
| S-4 | `seedance_2.0_mini+t2v` | V-1; C-14 (the cheapest `t2v`) | 16 |
| S-5 | `seedance_pro_fast+t2v` | | 20 |
| S-6 | `seedance_2.5+first_last_frame+1ref` | | 48 |
| S-7 | `seedance_2.0+first_last_frame+1ref` | | 52 |
| S-8 | `seedance_2.0_fast+first_last_frame+1ref` | | 24 |
| S-9 | `seedance_2.0_mini+first_last_frame+1ref` | V-2 | 16 |
| S-10 | `seedance_pro_fast+first_last_frame+1ref` | | 20 |
| S-11 | `seedance_2.5+first_last_frame+2ref` | | 48 |
| S-12 | `seedance_2.0+first_last_frame+2ref` | | 52 |
| S-13 | `seedance_2.0_fast+first_last_frame+2ref` | | 24 |
| S-14 | `seedance_2.0_mini+first_last_frame+2ref` | | 16 |
| S-15 | `seedance_2.5+m2v+1ref` | | 48 |
| S-16 | `seedance_2.0+m2v+1ref` | | 52 |
| S-17 | `seedance_2.0_fast+m2v+1ref` | | 24 |
| S-18 | `seedance_2.0_mini+m2v+1ref` | V-3 (M2V's model) | 16 |

C-14 fills S-4, the cheapest `t2v`. Round 1 costs 600 in all; S-9 and S-18
count in Part 2.

### Round 2: settings round 1 leaves untested

Once round 1 is done, quote these for free on the test canvas, and run them
in rising price while the cap allows. Show the owner the list with its quotes
first; the owner may add or drop rows. Each row is at the lowest resolution
and the shortest duration. The credits are from Part 0's prices; `count` 2
doubles the price.

| Row | What | Why | Credits |
| --- | ---- | --- | ------- |
| S-19 | The cheapest `t2v` at 9:16 | The vertical shape live-shopping uses | 16 |
| S-20 | The cheapest `t2v` with `count` 2 | Two outputs: two resources, and `references` holding each as `res:` ([01-decisions.md](01-decisions.md#references)) | 32 |
| S-21 | `seedance_2.5` `m2v` at 480p with an image and A-1's speech | An audio reference: does the video speak the line? | 48 |
| S-22 | The cheapest `m2v` with `clip.mp4` only | A video reference alone | 16 |
| | **Total** | | **112** |

The quotes:

```sh
q() {  # q ROW FLAGS...: a free quote of one round 2 row
  local row="$1"
  shift
  dr "$row-quote" node create video --project-id "$T" --prompt "A red apple on a white table." "$@" --run --credit-ceiling 0 --submit-id "$(new_id)"
  printf '%s\t%s\n' "$row" "$(jq -r '.creditConfirmation.minimumCreditCeiling // .error.code' "$row-quote.err.json")" | tee -a round-2.tsv
}
J=$(cheapest t2v)
M=$(flag_of "$J" --model)
R=$(flag_of "$J" --resolution)
D=$(flag_of "$J" --duration)
JM=$(cheapest m2v "" 1)
ffmpeg -v error -y -i "$(ls "$COMFY"/output/audio/dreamina/a1_* | head -n 1)" -ar 44100 -ac 1 a1.wav
dr upload-a1 resource upload --project-id "$T" --file "$PWD/a1.wav" --type audio --resource-id "$(new_id)"
A1=$(jq -r .data.resourceId upload-a1.json)
q S-19 --mode t2v --model "$M" --ratio 9:16 --resolution "$R" --duration "$D" --count 1
q S-20 --mode t2v --model "$M" --ratio 16:9 --resolution "$R" --duration "$D" --count 2
q S-21 --mode m2v --model seedance_2.5 --ref "res:$PNG" --ref "res:$A1" --ratio 16:9 --resolution 480p --duration 4 --count 1
q S-22 --mode m2v --model "$(flag_of "$JM" --model)" --ref "res:$MP4" --ratio 16:9 --resolution "$(flag_of "$JM" --resolution)" --duration "$(flag_of "$JM" --duration)" --count 1
```

S-21's prompt in the run is "The apple says the line in the audio." S-22's
is "A red apple, in the style of the video."

### The cap

The cap is 750 credits, less C-14's T2V. Before each row, add its quote to
the credits spent so far in Part 3. When the sum would pass the cap, stop: the
rest of the rows are recorded "quoted only", with their quotes.

### How to run a row through ComfyUI

Build four one-node workflows once in the ComfyUI page, and export each with
**Workflow → Export (API)** into `part-3`:

| File | Graph |
| ---- | ----- |
| `sweep-t2v.api.json` | **Video: Generate** → **Save Video**; its `result` → **Preview Any** |
| `sweep-frames-1.api.json` | The same, with `images` ← **Load Image** `dreamina-test-apple.png` |
| `sweep-frames-2.api.json` | The same, with `images` ← both test images, `dreamina-test-apple.png` first, connected as [10-node-video.md](10-node-video.md) says several images connect |
| `sweep-m2v.api.json` | As `sweep-frames-1`, for one-image `m2v` rows; `arguments` carries `"mode": "m2v"` |

For each row, write its values into a copy and send it:

```sh
ROW=S-2
J=seedance_2.0+t2v
FILE=sweep-t2v.api.json
P=$(price "$J")
comfy_queue
set_inputs "$FILE" DreaminaVideoGenerate "$(jq -n --arg m "$(flag_of "$J" --model)" --arg a "$(arguments_of "$J")" \
  --arg p "A red apple rolls across a white table." --argjson c "$P" --argjson r "${ROW#S-}" \
  '{model: $m, arguments: $a, prompt: $p, credit_ceiling: $c, run_number: $r}')" \
  | set_inputs /dev/stdin SaveVideo "{\"filename_prefix\": \"video/dreamina/$ROW\"}" > "$ROW.api.json"
comfy_send "$ROW.api.json" | tee "$ROW.prompt"
```

`arguments_of` includes `"mode"`, so the `first_last_frame` entry and `m2v`
are chosen as the row says. Wait with the comfy-mcp `job` tool (`action`
`wait`) on the prompt ID, or read `comfy_history "$(cat "$ROW.prompt")"` until
`status` is `success` or `error`. Then:

```sh
comfy_history "$(cat "$ROW.prompt")" | jq '{status, seconds}'
F=$(ls -t "$COMFY"/output/video/dreamina/"$ROW"_* | head -n 1)
probe "$F"
ls "$STATE/generations"
```

### How to run a row through the CLI

When ComfyUI is busy, on the test canvas:

```sh
ROW=S-2
J=seedance_2.0+t2v
run_job "$ROW" "$J" "$(price "$J")"
wait_for "$ROW" "$(cat "$ROW.submit")" "$T"
download_outputs "$ROW" "$(jq -r .data.node.nodeId "$ROW.json")" "$(cat "$ROW.submit")" "$T" mp4
probe "$ROW-1.mp4"
```

### Between rows

1. Read the row's result and look at the video. Check its node on the canvas
   (the `result` link, or `node find`), not only ComfyUI's history.
1. Check `comfy_queue` is empty before the next row.
1. After every five rows, or every 150 credits, the owner reads the balance.
   If it fell by more than the quotes since the last reading, stop and report.
1. A row that fails or is refused is recorded and not retried. A failed row
   is a C-17 case: note the balance before and after.

### Results

Fill one row per run in the catalog's Video models notes and in the changes
table's Part 3 row, in this shape:

| Row | Model | Mode | Settings sent | Route | Quote | `creditsAmount` | Balance change | Seconds to finish | Width × height | Duration (s) | fps | Sound | Result | Notes |
| --- | ----- | ---- | ------------- | ----- | ----- | --------------- | -------------- | ----------------- | -------------- | ------------ | --- | ----- | ------ | ----- |
| S-4 | `seedance_2.0_mini` | `t2v` | 16:9, 720p, 4 s, count 1 | CLI (C-14) | 16 | from `node show` | when read | from `seconds.tsv` | from `probe` | from `probe` | from `probe` | an audio stream in `probe` or none | pass, fail, or refused | any `error.code`, what the video shows |

- **Quote** is Part 0's or round 2's. **`creditsAmount`** is Dreamina's own
  figure on the resource, from `node show` or `result`. **Balance change** is
  filled when the owner's readings isolate the row; otherwise it is the
  change over the rows between two readings, noted as such.
- **Seconds to finish** is from acceptance to the terminal state: ComfyUI's
  history time, or `seconds.tsv` for a CLI row.
- **Result** is "pass" when the video plays, matches the settings, and shows
  the prompt; "fail" for a failed generation; "refused" for a refusal; or
  "quoted only".

## Part 4: Run every example once

Each example runs once on the final code, after the Documentation milestone,
with the owner's approval. The runs are not part of the Documentation commit;
each fix a run needs is its own commit. The examples, their shipped prompts,
settings, and save names are in
[17-scripts-and-workflows.md](17-scripts-and-workflows.md); where this table
and 17 differ, 17 wins and this table is corrected.

### Step 1: Quote each example

Free. The Credits column below is filled from Part 0's prices for each
example's settings in 17, all at the lowest settings. An example's credits
are the sum of its nodes' quotes. Before the runs, confirm each one: send
each paid node's exact values from 17 with the CLI on the test canvas and
`--credit-ceiling 0`, as Part 0 Step 5 does. A quote that differs replaces
the figure. Show the owner the table.

### Before the runs

1. Restart ComfyUI with the finished pack, with its queue empty.
1. Check **Dreamina Settings** shows the CLI and the signed-in account.
1. Copy the files each **Start Here** note asks for into ComfyUI's input
   folder. image-02 takes a product photo: use `dreamina-test-apple.png`.
1. Run each example start to finish before opening the next. ComfyUI keeps
   only the last run's results, so a multi-stage example run in pieces mixes
   two runs' outputs; B's video-04 had to run twice for this reason.

**How to run.** Open the example from **Browse Templates → dreamina**, set what
its **Start Here** note asks, and press **Run**. An agent may instead run
`example_workflows/<slug>.json` through the comfy-mcp `run_workflow` tool,
which expands subgraphs, or build the prompt with ComfyUI's own
`app.graphToPrompt()` in a headless page and queue it through `/prompt`, as F
did, so subgraphs expand as **Run** expands them. The owner approves each run
either way.

| Order | Example | How | Check | Credits |
| ----- | ------- | --- | ----- | ------- |
| 1 | image-01-design-a-host | Run | The host image saved under `image/dreamina/`; `result` names the model and mode; the nodes on the `ComfyUI` canvas | 6 |
| 2 | image-02-edit-a-product-photo | Load the photo; Run | The edited photo keeps the product; `i2i` ran with one upload | 5 |
| 3 | image-03-upscale-a-poster | Run | The poster, then its `pro` `2K` upscale; the upscale's source is the poster's node | 6 + 2 = 8 |
| 4 | audio-01-voice-a-script | Run | The speech says the script in the chosen voice; its length fits the script | 12 |
| 5 | audio-02-give-a-host-a-voice | Run | Omni dubbing from the host image: a voice that fits the host, with no `voice-name` sent | 6 + 12 = 18 |
| 6 | video-01-animate-a-host | Run; once the generation record appears, press **Cancel** | The run stops with the "keeps running" message; the record stays; **Generation: Download** lists it | 6 + 16 = 22 |
| 7 | video-04-recover-a-video | Choose video-01's record; Run | The video is saved; the record is deleted; the list empties | 0 (collects video-01's run) |
| 8 | video-02-film-a-product-ad | Run | The host and the product in one video; the canvas shows the reference slots in the order 17 sets | 6 + 6 + 48 = 60 |
| 9 | video-03-keep-a-host-across-shots | Run | One Element, then each shot shows the same host | 6 + 16 + 16 = 38 (Element: Add is free) |
| | **Total** | | | **169, at most 250** |

If video-01's run finishes before the cancel lands, it is collected and its
record deleted by the run itself; then run video-04 after a second video-01
run, canceled sooner, and add its credits to the record.

### After the runs

1. The owner reads the balance and compares the change with the table's
   total.
1. The agent lists the `ComfyUI` canvas with `node find` and checks that every
   example's nodes are there with status success, apart from video-01's,
   which video-04 collected.
1. `ls "$STATE/generations"` is empty: every run was collected.
1. Run C-16's exit-code roll-up over every Part's folder.
1. Record anything that differs from the plans, and every fix, in
   [Changes made while building](README.md#changes-made-while-building), with
   the run's order number, the credits, and the running total.

## What the runs change

| Finding | Plans to correct |
| ------- | ---------------- |
| A price check with a quote of 0 ran at a ceiling of 0 | 02's Credit approval; 01's Credits; 18's ADVANCED sentence on the ceiling |
| A run sent with a ceiling below its quote was accepted or billed | Stop every paid run and tell the owner; 01's Credits and 02 |
| A listed resolution or model is refused on the Standard plan | The catalog's membership notes; 08's plan message; 22; 06 keeps not refusing on membership fields |
| Part 0 finds a cheaper, equally current starting model | The catalog's Defaults; 01's Choosing a model; 06's `DEFAULT_MODELS`; the starting values and `credit_ceiling` defaults in 09 to 12 |
| A second `canvas create` with the same ID fails instead of answering the same canvas | 08's `create_canvas` retry |
| An upload format or size is refused | 07's encoding (MP3 through PyAV when WAV is refused); 05's `max_upload_megabytes`; the catalog's File limits |
| `resource download` refuses a generated video or audio | 02's Downloads; 07; 10; 11; 14. The pack would have no file to decode; the owner decides before the Video milestone |
| The run reply carries `submission`, as the schema shows, not run items | 02's Generation runs; 08's `RunReply`; 04's `src/types/replies.py` row |
| The state values of `operation status` and `operation wait` | 02's Waiting and recovery; 08's `OPERATION_STATES` |
| `{{res:<uuid>}}` does not bind an upload | 01's Placeholders; 07's `format_prompt`; the help pages of 09 to 11; 23 |
| The CLI refuses a bad value locally, or the server quotes it | 02's Exit codes; 08's failure map. 06's checks stay either way |
| Text reading's audio reference acts as a voice sample | 11's help page; 17's audio examples |
| Omni dubbing refusals happen in the CLI or at save | 06's reference checks; the catalog's File limits; 11 |
| An imported image cannot be upscaled | 12's import path; 04's upscale flow; U-1 and image-03 use references |
| A killed wait cannot be resumed from a new process | 08's cancel step; 14; the owner decides |
| An Element alone does not meet `m2v`'s `requireAnyOfTypes` | 06's reference counting; 10's mode table; 13's help page |
| The error code of a canvas that does not exist | 02's Canvases; 08's message for a canvas deleted during a run |
| How an unknown submit ID reads | 02; 14's message for an expired record |
| Exit codes 1, 12, 13, 21, or 22 met | 02's Exit codes table; 08's failure map |
| A failed generation is billed, or not | 02's What is billed; 01's Errors; 08's messages; 18's ADVANCED; 22 |
| The Audio starting `arguments` block omni dubbing | 11's starting values or refusal message; 17's audio-02 sets `arguments` to `{}` |
| Each video model's real output: size, frame rate, duration, sound, time | The catalog's Video models; 10's help page; 17's example settings |
| `count` 2 returns two resources on one node | 01's Outputs and References; 08's `build_node_outputs` |
| A charge above the quote | Stop and tell the owner; 01's Credits |

## Names this plan uses from other plans

| Name | Owner | Used for |
| ---- | ----- | -------- |
| The call shape, exit codes, Facts to confirm, and Results of the contract runs | [02-dreamina-contract.md](02-dreamina-contract.md) | Every CLI call; where Parts 0 and 1 record |
| `credit_ceiling`, `run_number`, the mode table, placeholders, the canvas name, the state folder | [01-decisions.md](01-decisions.md) | The node runs and their checks |
| The starting values, the File limits, the Prices table | [research/catalog.md](research/catalog.md) | Part 0, defaults, and Part 3's model list |
| `OPERATION_STATES` in `src/config/generations.py`; the run flow; subprocess kill on cancel | [04-architecture.md](04-architecture.md), [08-runs.md](08-runs.md) | C-8, C-14, V-4 |
| `max_upload_megabytes` | [05-foundation.md](05-foundation.md) | C-2 |
| The model check and `DEFAULT_MODELS` | [06-model-check.md](06-model-check.md) | K-1, Step 7 |
| Uploads, `format_prompt`, downloads | [07-media.md](07-media.md) | C-2 to C-6 |
| `find_canvas`, `create_canvas`, `CanvasStore`, `GenerationRecord`, the failure map, `RunReply`, `build_node_outputs` | [08-runs.md](08-runs.md) | C-1, C-7, C-15, Part 2 |
| **Image: Generate**, **Video: Generate**, **Audio: Generate**, **Image: Upscale**, **Element: Add**, **Generation: Download**, **Model: Info**, and each one's live checks step | [09-node-image.md](09-node-image.md) to [15-node-model-info.md](15-node-model-info.md) | Part 2 |
| **Dreamina Settings** | [16-frontend.md](16-frontend.md) | Part 4 |
| The example workflows, their slugs and **Start Here** notes | [17-scripts-and-workflows.md](17-scripts-and-workflows.md) | Part 4 |
| ADVANCED | [18-documentation.md](18-documentation.md) | Findings on billing and the ceiling |
| Reading the balance; deleting drafts | [22-owner-setup.md](22-owner-setup.md) | Every Part; C-17 |
| The owner's rules for paid requests and live checks | [research/owner-rules.md](research/owner-rules.md) | Approval and recording |
| Build order, Before the first paid run, Changes made while building | [README.md](README.md) | When each Part runs; where results go |
