# Owner Setup

This plan is for the owner, not the builder. It lists what to do on
dreamina.capcut.com and on this Mac, in order, before and during the build:
check the CLI, sign in, find out whether the plan includes the CLI, watch the
credits, and look after the canvas the pack fills. Each step says where to go
and what it changes. Nothing here changes the pack's code, and Steps 1 to 4
do not need the pack.

It follows F's owner plan (`F=/Users/dr_stone/Documents/work/comfyui-fal`,
commit `cef8b6e`, `plans/22-owner-setup.md`). The facts come from the free
calls made on 2026-10-16, saved in `research/captures/` and cited by file
name, from the CLI's schema and skill ([research/cli.md](research/cli.md)),
and from Dreamina's pages ([research/terms.md](research/terms.md)).

The pack adds no spending caps or warnings of its own. `credit_ceiling` is the
approval Dreamina's own CLI asks for on every run, not a cap the pack invents
([01-decisions.md](01-decisions.md#credits)). No step buys credits, changes
the plan, or changes an account setting. The owner's rule is that a runtime
check never authorizes buying credits or changing account settings
([research/owner-rules.md](research/owner-rules.md#paid-requests-and-live-checks)).
Where a step finds something only a purchase would fix, it stops, and the
owner decides.

Steps 1 to 3 were done on 2026-10-16. Do Step 4 before Part 1 of
[21-test-runs.md](21-test-runs.md), the first stage that spends credits.
Steps 2 and 3 are done again whenever the sign-in ends. Steps 5 and 6 matter
once runs start. Step 7 is for later, if at all.

## Contents

- [Your account today](#your-account-today)
- [Step 1: Check the CLI](#step-1-check-the-cli)
- [Step 2: Sign in](#step-2-sign-in)
- [Step 3: Check the plan gate](#step-3-check-the-plan-gate)
- [Step 4: Watch the credits](#step-4-watch-the-credits)
- [Step 5: Know the ComfyUI canvas](#step-5-know-the-comfyui-canvas)
- [Step 6: Delete drafts left by refusals](#step-6-delete-drafts-left-by-refusals)
- [Step 7: Sign out or remove the CLI](#step-7-sign-out-or-remove-the-cli)
- [See what each run cost](#see-what-each-run-cost)
- [Questions only the website can answer](#questions-only-the-website-can-answer)
- [Names this plan uses from other plans](#names-this-plan-uses-from-other-plans)

## Your account today

| Item              | State on 2026-10-16                                                                                                                                  |
| ----------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| Computer          | macOS on Apple Silicon. ComfyUI runs in the Comfy Desktop app, as the owner's macOS user                                                             |
| Dreamina account  | Signed in to dreamina.capcut.com in Firefox, from the UK. A UK account is under Dreamina's global terms ([research/terms.md](research/terms.md#1-the-terms)) |
| Plan              | A heavily discounted Standard plan, bought for 1.19 British pounds. The CLI page, `https://dreamina.capcut.com/canvas-cli`, says "Private beta · Advanced subscribers only" |
| Credits           | About 1,300, as the website showed after the purchase. The CLI cannot read the balance ([research/cli.md](research/cli.md#open-questions), question 9) |
| The CLI           | Release 1.0.3 (commit `244064d`, built 2026-10-14) at `~/.local/bin/dreamina-canvas`, with its skill at `~/.agents/skills/dreamina-canvas-cli`, both from ByteDance's official installer (`version.json`) |
| CLI sign-in       | Signed in at the third attempt, kept in the Keychain (`credentialStorage` `keyring`) until `expiresAt` 2026-12-15 (`auth-status.json`). The first two links ran out before approval: one wait ended first (`error-login-wait-timeout.json`, `cli.login_wait_timeout`, exit 20), and one code expired (`error-login-expired.json`, `cli.login_expired`, exit 11) |
| Plan gate         | Passed on the Standard plan, although the CLI page names Advanced subscribers. `auth account` gives `isVip` `true` and `vipLevel` `standard` (`auth-account.json`), and the lists hold 12 image, 5 video, and 2 audio models, with no music model (`model-list-image.json`, `model-list-video.json`, `model-list-audio.json`; [research/catalog.md](research/catalog.md#account)) |
| Canvas            | None yet. The pack makes its `ComfyUI` canvas on its first run ([Step 5](#step-5-know-the-comfyui-canvas))                                           |
| Paid runs         | None                                                                                                                                                 |

## Step 1: Check the CLI

The CLI is installed. The pack needs release 1.0.3 or later, the release its
contract was read from
([01-decisions.md](01-decisions.md#the-cli-on-the-persons-computer)).

1. In Terminal, run:

   ```bash
   dreamina-canvas version
   ```

   It shows version `1.0.3` and commit `244064d`.
1. If the shell answers `command not found`, `~/.local/bin` is not on its
   `PATH`. Run `~/.local/bin/dreamina-canvas version` instead, and use the
   full path the same way in every command below. The pack is not affected:
   it looks in `~/.local/bin` itself, because Comfy Desktop may start ComfyUI
   without that folder on its `PATH`.

Nothing else is needed now. Update later in either of two ways:

- **Dreamina Settings → Dreamina CLI → Update**, once the Frontend milestone
  exists ([README.md](README.md#build-order)). It runs the same official
  installer.
- In Terminal, run the installer again:

  ```bash
  curl -fsSL https://dreamina.capcut.com/canvas-cli/install.sh | bash
  ```

  It replaces the binary and the skill in place and keeps the sign-in
  ([research/cli.md](research/cli.md#release-and-install)).

Update when a node says the CLI is too old. Dreamina's server refuses an old
release with `requiredAction` `upgrade`, and its reply may carry install
commands of its own. Run only the fixed installer above, never a command
taken from a reply
([02-dreamina-contract.md](02-dreamina-contract.md#install-upgrade-and-the-version-gate)).

For other people's computers, the README
([18-documentation.md](18-documentation.md)) needs only this:

| System               | Command                                                          | Installs to                             |
| -------------------- | ---------------------------------------------------------------- | --------------------------------------- |
| macOS, Linux         | `curl -fsSL https://dreamina.capcut.com/canvas-cli/install.sh \| bash` | `~/.local/bin/dreamina-canvas`    |
| Windows (PowerShell) | `irm https://dreamina.capcut.com/canvas-cli/install.ps1 \| iex`  | `%USERPROFILE%\bin\dreamina-canvas.exe` |

The Windows CLI runs only on AMD64 processors. Linux keeps the sign-in in
files under `~/.local/share/`, and Windows in the current user's registry,
encrypted for that user ([research/cli.md](research/cli.md#sign-in)).

## Step 2: Sign in

Done on 2026-10-16 with the CLI's own `auth login` and `auth wait`, as in
[From a terminal](#from-a-terminal): the third link was approved. Do it again
after a sign-out, when the sign-in ends, or on another computer.

The CLI signs in with Dreamina's device authorization. It shows a link and a
code, and you approve the code on dreamina.capcut.com. The code lasts about 10
minutes, in both captures. The CLI keeps the sign-in in the macOS Keychain,
and the pack never sees it
([01-decisions.md](01-decisions.md#sign-in-and-privacy)).

### From Dreamina Settings

Once the Frontend milestone exists:

1. Open **ComfyUI menu → Extensions → Dreamina → Dreamina Settings**, and
   select **Sign in** under **Account**.
1. The dialog shows the link and the code, and opens the link. If the link
   opens anywhere but Firefox, such as inside the Comfy Desktop window, copy
   it into Firefox, where the account is signed in.
1. Check that the page's address starts with
   `https://dreamina.capcut.com/ai-tool/cli-auth-os` and that it shows the
   same code. Then approve it.
1. The dialog shows the account as signed in. It checks every two seconds
   until the sign-in ends or the code expires
   ([04-architecture.md](04-architecture.md#how-the-person-signs-in)).

### From a terminal

Before the Frontend milestone, or whenever a terminal is easier. Both ways
make the same sign-in, and the dialog shows a terminal sign-in too.

1. Start a sign-in. `--format json` prints the fields named here, as in the
   captures:

   ```bash
   dreamina-canvas --format json auth login
   ```

   Its `challenge` holds the link (`verificationUriComplete`), the code
   (`userCode`), the `deviceCode`, and the expiry (`expiresAt`).
1. At once, start the wait that collects the approval, with the `deviceCode`
   from step 1. It waits up to 10 minutes:

   ```bash
   dreamina-canvas --format json auth wait --device-code <deviceCode>
   ```

   Keep the device code in the terminal. Do not paste it anywhere else.
1. While it waits, open the link in Firefox, check the page and the code as
   above, and approve.
1. The wait ends with `state.loggedIn` `true`. If it ends with
   `cli.login_wait_timeout` (exit 20), the code is still valid: run the same
   `auth wait` again. If it ends with `cli.login_expired` (exit 11), start
   again from step 1. Do not start a new sign-in while one is waiting, as the
   skill says.
1. Check the result:

   ```bash
   dreamina-canvas --format json auth status
   ```

   It shows `loggedIn` `true`, `credentialStorage`, and `expiresAt`. It reads
   this Mac's state only, with no network call.

### What the sign-in is bound to

- **This Mac and this macOS user.** The CLI signs every request with a key
  made for this device, and keeps the sign-in in the Keychain of the user who
  signed in ([research/cli.md](research/cli.md#sign-in)). ComfyUI must run as
  that same macOS user, which Comfy Desktop does. Another computer needs its
  own sign-in.
- **One profile, `default`.** The pack never passes `--profile`, so do not
  sign in with one.
- **Everything that runs the CLI as this user.** The pack, a terminal, and any
  agent session that loads the skill share the one sign-in.

When the sign-in ends, paid nodes and **Model: Info** stop with the sign-in
message, which names **Dreamina Settings**. Sign in again as above. Whether
the CLI renews the sign-in by itself before `expiresAt` is checked by the test
runs ([research/cli.md](research/cli.md#commands-the-pack-does-not-use)).

## Step 3: Check the plan gate

Done on 2026-10-16: the gate passed. Do it again after a plan change. It is
run C-0 in Part 0 of [21-test-runs.md](21-test-runs.md), and it is free.

1. Read the account:

   ```bash
   dreamina-canvas --format json auth account
   ```

   It returns `userId`, `isVip`, and `vipLevel`
   ([02-dreamina-contract.md](02-dreamina-contract.md#the-account)). Note
   `isVip` and `vipLevel`. Keep `userId` out of every plan and capture.
1. List the video models the account can call:

   ```bash
   dreamina-canvas --format json model list --type video
   ```

   Part 0 also lists `image` and `audio`, and saves all three replies.
1. Read the result:

   | Result                                       | Meaning                                         | Next                                                                                                                                                         |
   | -------------------------------------------- | ----------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
   | `items` lists models                         | The account can use the CLI                     | Go on with Step 4                                                                                                                                            |
   | The call is refused, or `items` is empty     | The plan does not include the CLI               | Stop before any paid stage. Which plan includes it is Dreamina's decision, shown on its pricing page, `https://dreamina.capcut.com/pricing/dreamina-price`. Nothing is bought or changed until the owner decides |

1. Record the result in [research/catalog.md](research/catalog.md#account):
   the date, the CLI release, `isVip`, `vipLevel`, and how many models each
   kind lists. For a refusal, record its `error.code`, `error.class`,
   `error.requiredAction`, and `meta.requestId`. Save the account reply as
   `research/captures/auth-account.json`, without `userId`.

The result on 2026-10-16, recorded there: `isVip` `true`, `vipLevel`
`standard`, and 12 image, 5 video, and 2 audio models. So the gate admitted
the Standard plan, although the CLI page names Advanced subscribers.

A listed model can still be refused when a run is saved or started. A mode's
`vipRequired` and `vipResolutions` describe the model, not the plan, and "the
server's final admission decision remains authoritative"
([research/cli.md](research/cli.md#model-discovery)). Where a plan limit
stops a run is question 8 in
[research/cli.md](research/cli.md#open-questions), settled by the test runs.

## Step 4: Watch the credits

The CLI shows no balance. `auth account` has none, and no command in 1.0.3
returns one ([02-dreamina-contract.md](02-dreamina-contract.md#the-account)).
So the owner reads it on the website.

1. Before each test stage in [21-test-runs.md](21-test-runs.md), read the
   balance on dreamina.capcut.com, signed in, where it showed about 1,300
   credits after the purchase. Write it in that stage's record.
1. After the stage, read it again and write the difference next to the
   stage's limit. The limits are in
   [README.md](README.md#before-the-first-paid-run): Part 0 spends nothing,
   and Parts 1 to 4 spend at most 60, 150, 750, and 250 credits. That is
   1,210 in all, with at least 90 kept in reserve.
1. If the balance changed during Part 0, stop the test runs and tell the
   owner. Part 0 only reads lists and checks prices with a ceiling of 0,
   which stops every run before it is billed
   ([02-dreamina-contract.md](02-dreamina-contract.md#credit-approval)).
1. For run C-17, read the balance just before and just after its one run. It
   shows whether a failed generation is billed
   ([02-dreamina-contract.md](02-dreamina-contract.md#what-is-billed-when-something-fails)).
1. On the website's plan page, check when the plan's credits expire and
   whether the plan renews by itself. Credits that come with a discounted plan
   may expire, so the test stages should finish before then.

A run the balance cannot pay for is refused, and the node says so
([01-decisions.md](01-decisions.md#errors)). Adding credits is the owner's
decision, made on the website. The owner pre-approved spending the 1,300
credits on these tests; any spending beyond the README's stages needs a new
approval.

## Step 5: Know the ComfyUI canvas

Every node the pack makes lives on one Dreamina canvas named `ComfyUI`
([01-decisions.md](01-decisions.md#the-canvas)).

- **The first run makes it.** The first node that saves anything to Dreamina
  (an upload, a run, or an Element) creates the canvas. The pack saves its ID
  and link in its state folder, in
  `~/Library/Application Support/DreaminaComfyUI/canvas.json`.
- **Where to see it.** The link is in each node's `result`, and the canvas
  is in the owner's Dreamina projects. Dreamina Settings has no canvas link.
  The canvas shows every image, video, audio file, upload, and Element the
  pack made, with its prompt, so it doubles as a history.
- **Renaming is safe.** The pack finds the canvas by its ID, not its name, so
  the owner may rename it on the website.
- **Deleting it starts a new one.** Before each run, the pack looks for its
  canvas in `canvas ls`. After a deletion, the next run finds it gone and
  creates a new `ComfyUI` canvas before anything is uploaded. A canvas
  deleted while a run is going fails that run, and nothing is sent again.
  First collect every run that **Generation: Download** lists, because each
  record names its canvas. Deleting the pack's state folder also makes the
  next run create a new canvas, and the old one stays on the account.
- **Other canvases are left alone.** The pack names its canvas in every call
  and never changes the CLI's current canvas, which a terminal or an agent
  session may use.

The prompts and the uploaded images, videos, and audio stay on the canvas
until the owner deletes them on dreamina.capcut.com. The pack keeps no copy
([01-decisions.md](01-decisions.md#sign-in-and-privacy)).

## Step 6: Delete drafts left by refusals

Optional. Drafts cost nothing to keep.

- **Where drafts come from.** A run whose quote is above its `credit_ceiling`
  stops before it runs, with nothing billed, and leaves its saved node on the
  canvas as a draft, with no output
  ([02-dreamina-contract.md](02-dreamina-contract.md#credit-approval)). A run
  that Dreamina refuses after saving it leaves one too
  ([01-decisions.md](01-decisions.md#checking-a-model-before-paying)).
- **The price sweep leaves many.** Part 0 of
  [21-test-runs.md](21-test-runs.md) checks each price with a ceiling of 0,
  so it leaves one draft for each price it checks.
- **The pack never deletes a node.** The CLI needs the person's explicit
  approval of each deletion
  ([research/cli.md](research/cli.md#commands-the-pack-does-not-use)). Delete
  drafts on the canvas in Firefox when they get in the way.
- **Delete only nodes with no output and no generation in progress.**
  Deleting a node does not cancel a generation Dreamina accepted and does not
  refund its credits ([research/cli.md](research/cli.md#operations-and-recovery)),
  and a deleted node can no longer be collected.

## Step 7: Sign out or remove the CLI

Not needed for the build.

To sign out, select **Dreamina Settings → Account → Sign out**, or run:

```bash
dreamina-canvas --format json auth logout
```

It clears the CLI's sign-in on this Mac and returns `loggedOut`
([02-dreamina-contract.md](02-dreamina-contract.md#sign-in)). It signs out
everything that runs the CLI as this user, and leaves the Firefox session
alone. Paid nodes then stop with the sign-in message.

To remove the CLI:

1. Sign out first.
1. Delete `~/.local/bin/dreamina-canvas` and the folder
   `~/.agents/skills/dreamina-canvas-cli`.
1. The Keychain may still hold an entry of ByteDance's auth client, which the
   CLI uses to keep its sign-in, with a lock folder in
   `~/Library/Caches/byted_auth_client/`
   ([research/cli.md](research/cli.md#sign-in)). The entry belongs to that
   client, not to the pack. Leave it, or delete it in Keychain Access.

The CLI's own records, its current canvas and its operation journal, stay in
its state folder, whose default place the skill does not name
([research/cli.md](research/cli.md#local-state-the-cli-keeps)). Removing the
pack and its state folder is in ADVANCED.md's "Update or remove"
([18-documentation.md](18-documentation.md)). Without the CLI, every Dreamina
node stops with the message that the CLI is missing, which names
**Dreamina Settings → Dreamina CLI → Install**.

## See what each run cost

The pack shows no prices. The only credit figure it shows is Dreamina's quote,
when a run stops at its `credit_ceiling`
([01-decisions.md](01-decisions.md#credits)). To see what a run cost:

1. **The run's `result`.** It holds the node as Dreamina's `node show`
   returns it, and each resource in it carries Dreamina's `creditsAmount`
   ([02-dreamina-contract.md](02-dreamina-contract.md#reading-a-finished-node)).
   Connect `result` to a text display node, such as ComfyUI's **Preview Any**,
   to read it.
1. **The canvas.** Each node shows there with its outputs.
1. **The website's credit history**, if it has one, is the authority. The
   skill warns that a figure taken before the charge settles is not proof of
   the final spend or of a refund
   ([research/cli.md](research/cli.md#credits)), so `creditsAmount` is
   Dreamina's figure for the resource, not a ledger entry. Without a history
   page, the balance before and after (Step 4) is the measure.

The test runs record each stage's credits from the balance, in
[21-test-runs.md](21-test-runs.md).

## Questions only the website can answer

| Question                                                                 | Where                                                                                                   |
| ------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------- |
| What is the credit balance?                                              | dreamina.capcut.com, signed in                                                                          |
| When do the plan's credits expire, and does the plan renew by itself?    | The plan or subscription page on dreamina.capcut.com                                                    |
| Which plans include the Canvas CLI?                                      | `https://dreamina.capcut.com/pricing/dreamina-price` and `https://dreamina.capcut.com/canvas-cli`       |
| Is a failed generation refunded?                                         | The balance, or the credit history, before and after run C-17                                           |
| What did a given run cost?                                               | The credit history, if the website has one; otherwise the balance before and after                      |
| May the outputs be used commercially under this plan?                    | Dreamina's terms (sections 1, 2, and 7) and the pricing page's FAQ ([research/terms.md](research/terms.md#1-the-terms)). It decides whether live-shopping may use them ([23-live-shopping-provider.md](23-live-shopping-provider.md#open-questions)) |

## Names this plan uses from other plans

| Name                                                                                       | Owner                                                                                                      | Used for                                    |
| ------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------- | ------------------------------------------- |
| **Dreamina Settings** and its **Dreamina CLI**, **Account**, and **Request limits** parts | [16-frontend.md](16-frontend.md)                                                                             | Updating, signing in and out                |
| `MINIMUM_VERSION` (`1.0.3`) and the version gate                                           | [08-runs.md](08-runs.md)                                                                                   | Which release the pack needs                |
| The state folder, `canvas.json`, and `CANVAS_NAME` (`ComfyUI`)                             | [01-decisions.md](01-decisions.md#names-and-identifiers), [05-foundation.md](05-foundation.md), [08-runs.md](08-runs.md) | Where the canvas is kept       |
| `credit_ceiling` and Dreamina's quote                                                      | [01-decisions.md](01-decisions.md#credits)                                                                 | Drafts and costs                            |
| **Generation: Download**                                                                   | [14-node-download.md](14-node-download.md)                                                                 | Collecting runs before deleting the canvas  |
| Parts 0 to 4 and runs C-0 and C-17                                                         | [21-test-runs.md](21-test-runs.md), [README.md](README.md#before-the-first-paid-run)                       | When to read the balance                    |
| The "Account" section                                                                      | [research/catalog.md](research/catalog.md#account)                                                         | Where the plan gate's result is kept        |
