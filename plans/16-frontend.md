# Frontend

This plan builds the browser side, and nothing else: the **Dreamina
Settings** dialog and the menu entry that opens it. The dialog has three
parts, top to bottom, and a footer:

- **Dreamina CLI**: one line that says whether the CLI is installed and its
  version, and one button: **Install** when it is missing, **Update** when it
  is installed;
- **Account**: sign in with Dreamina's device code, or sign out;
- **Request limits**: F's three settings;
- the footer: the status line and **Reload settings**.

The dialog reads the status each time it opens, and **Reload settings** reads
it again, so it has no button of its own to check the CLI. It shows no
install command and no canvas link: the one-line commands are in the README
and ADVANCED ([18-documentation.md](18-documentation.md)), and the canvas link
is in each run's `result` ([01-decisions.md](01-decisions.md#the-canvas)).

Nodes get no panels, badges, or status text. A paid node's inputs are plain
inputs that never change with a choice
([01-decisions.md](01-decisions.md#the-inputs-of-a-paid-node)). So F's
browser code has no value keeping to port, and neither does this plan. The
pack has no model list, so the browser listens for no server event.

Every file is a port of the fal pack's current browser code
(`F=/Users/dr_stone/Documents/work/comfyui-fal`, commit `cef8b6e`):
`web/scripts/**/*.ts` and `web/styles/interface.css`. This plan lists what
changes. TypeScript in `web/scripts/` is bundled by esbuild into the
committed `web/extension.js` and `web/extension.css`, which ComfyUI loads
from `WEB_DIRECTORY`. The routes the dialog calls, and the status document
they return, are [05-foundation.md](05-foundation.md#step-20-settings-routes-and-the-status-document)'s.

Readers: the engineer or agent who builds the Frontend milestone, and the
owner, who approves the browser checks that sign in and install.

Porting rules:

1. Replace fal names with the values in
   [01-decisions.md](01-decisions.md#names-and-identifiers): `fal-ai-` CSS
   classes become `dreamina-`, the extension name `fal` becomes `dreamina`,
   `fal.OpenSettings` becomes `dreamina.OpenSettings`, `/fal/v1` routes
   become `/dreamina/v1`, and the `X-Fal-Comfy` header becomes
   `X-Dreamina-Comfy`. Every visible string says "Dreamina". The install
   folder `dreamina` appears in no browser file: ComfyUI serves the bundle at
   `/extensions/dreamina/` by itself.
1. Keep every other function, name, comment, and `eslint-disable` reason as
   it is in the source file.
1. No TypeScript identifier contains a banned word
   ([01-decisions.md](01-decisions.md#banned-words-that-shape-names)): avoid
   `data`, `info`, `load`, `object`, `fetch`, `catalog`, `sync`, `and`,
   `or`, `with`, `tmp`, and `temp`. String values such as
   `'dreamina.OpenSettings'` are not checked.
1. Keep each file under ESLint's 300 lines and each function under 60
   (`quality/config/repository/limits.js`). F's `dialog.ts` is 264 lines.
   The CLI and account parts go into their own modules, so `dialog.ts`
   stays under 300 ([04-architecture.md](04-architecture.md#webscripts)).
1. Every function and method keeps a JSDoc block, as F's files do.

The plan's steps belong to two milestones of
[README.md](README.md#build-order):

| Step | Milestone |
| ---- | --------- |
| [Step 1: Entry files](#step-1-entry-files) | Tooling |
| [Step 2](#step-2-shared-modules) to [Step 7](#step-7-browser-checks) | Frontend, after Foundation, whose routes the dialog calls |
| [Step 8: Build the bundle](#step-8-build-the-bundle) | Tooling, then after every step that changes `web/scripts/` or `web/styles/` |

The step numbers 1 to 8 match F's, so other plans' links to Step 1 and
Step 8 land in the same place.

## Contents

- [Decisions this plan makes](#decisions-this-plan-makes)
- [Step 1: Entry files](#step-1-entry-files)
- [Step 2: Shared modules](#step-2-shared-modules)
- [Step 3: Browser text](#step-3-browser-text)
- [Step 4: Local replies and requests](#step-4-local-replies-and-requests)
- [Step 5: Settings dialog](#step-5-settings-dialog)
- [Step 6: Wire the extension](#step-6-wire-the-extension)
- [Step 7: Browser checks](#step-7-browser-checks)
- [Step 8: Build the bundle](#step-8-build-the-bundle)
- [Host behaviors this plan relies on](#host-behaviors-this-plan-relies-on)
- [Names this plan uses from other plans](#names-this-plan-uses-from-other-plans)

## Decisions this plan makes

| Question | Decision | Why |
| -------- | -------- | --- |
| How are buttons written? | In sentence case: **Install**, **Update**, **Sign in**, **Sign out**, **Save limits**, **Reload settings**. The title and menu entry stay **Dreamina Settings**. | `rules/DOCUMENTATION.md` "Use title case for document titles" asks for sentence case on buttons and title case on component names. F's "Save Limits" and "Reload Settings" would sit beside "Sign in". |
| Which parts does the dialog have? | Three: **Dreamina CLI**, **Account**, and **Request limits**, then the footer. No button that checks the CLI again, no install command to copy, and no canvas part. | The owner's decision on 2026-10-17. The dialog reads the status each time it opens, and **Reload settings** reads it again. The README and ADVANCED give the one-line commands for a terminal, and each `result` carries the canvas link. |
| How does **Install** ask first? | `window.confirm` with text that names ByteDance's official installer and dreamina.capcut.com, under a one-line `eslint-disable-next-line no-alert` with its reason. | The settings dialog is a modal `<dialog>`, which makes the rest of the page inert, ComfyUI's own confirm dialog included. A native confirm stays on top. `no-alert` is on for browser files (`quality/config/eslint/index.js:60`), and `rules/TYPESCRIPT.md` allows a disable with a specific reason. |
| How does the sign-in page open? | `window.open(url, '_blank', 'noopener,noreferrer')` right after the sign-in reply, and the link stays on the page as **Open the sign-in page**. | A browser can block a tab opened after an awaited reply, because the click's activation has passed. The link always works. |
| How is a pending sign-in followed? | A quiet `GET /dreamina/v1/status` every 2 seconds while `sign_in.state` is `waiting`. It stops when the account is signed in, when the state is `expired` or `failed`, on a read error, or when the dialog closes. | [04-architecture.md](04-architecture.md#how-the-person-signs-in). The server reports `expired` once `expires_at` passes, so the browser needs no clock rule of its own. |
| How do a poll and a button share the server? | Every request joins one promise chain, so no two overlap. A button's request disables the fieldsets and shows its working text. A poll's read changes nothing on the page until its reply. | F's rule: one request at a time. A poll every 2 seconds must not flash disabled buttons. |
| How long may a request take? | 60 seconds, and 390 seconds for an install. | The status takes up to 35 seconds and a sign-in start adds 15 ([05-foundation.md](05-foundation.md#step-15-installer-constants-account-limits-and-units)). An install takes up to 30 seconds of download, 300 of installer, and 10 for the version, then the status: 375 seconds. |
| What does the account part show? | "Signed in to Dreamina." and, when `vip_level` is present, "Plan: standard", as Dreamina writes it. `is_vip` is checked in the reply but not shown. | [02-dreamina-contract.md](02-dreamina-contract.md#the-account): the dialog shows `vipLevel` when present. |
| Which buttons stay enabled in multi-user mode? | **Reload settings**, which only reads. **Install**, **Update**, **Sign in**, **Sign out**, and **Save limits** are disabled, as F disables its changes. | Changes need multi-user mode off ([05-foundation.md](05-foundation.md#step-14-local-route-guard-request-body-and-settings-route)). |

## Step 1: Entry files

The pre-commit hook runs `repo:lint`, `repo:type:frontend`, and
`comfy:frontend:check`, so these files exist before the first commit
([03-repository-setup.md](03-repository-setup.md)). The hook needs:

- at least one `web/scripts/**/*.ts` file, or `tsc` fails with TS18003;
- an entry that imports a CSS file, or esbuild emits no `extension.css` and
  `scripts/frontend.py --check` fails reading it;
- no unused npm dependency, or knip fails: `repo:lint:frontend` runs knip
  with no flags, so its default dependency check applies.

[03-repository-setup.md](03-repository-setup.md) copies F's `package.json`,
which lists `"valibot": "1.5.0"`, and nothing imports it until
[Step 4](#step-4-local-replies-and-requests). Remove it before the first
commit, from the repository root, as F did:

```sh
bun remove valibot
```

This changes `package.json` and `bun.lock`, which the first commit takes as
they are. Step 4 adds the same version back.

Files:

1. `web/scripts/host.d.ts`: copy F's file unchanged. It types ComfyUI's
   `app.js` and `api.js` and lets TypeScript import CSS.
1. `web/styles/interface.css`: copy F's file and replace every `fal-ai-`
   with `dreamina-` (`.dreamina-dialog`, `.dreamina-actions`). The rules
   Step 5 needs are added there.
1. `web/scripts/extension.ts`: only the stylesheet import and the stylesheet
   code from F's `setup`:

```ts
import '#styles/interface.css';
import { app } from '../../scripts/app.js';

app.registerExtension({
  name: 'dreamina',
  setup: () => {
    const stylesheet = document.createElement('link');
    stylesheet.rel = 'stylesheet';
    stylesheet.href = new URL('./extension.css', import.meta.url).href;
    const stylesheets = new Set();
    for (const link of document.querySelectorAll('link[rel=stylesheet]')) {
      stylesheets.add(link.getAttribute('href'));
    }
    if (!stylesheets.has(stylesheet.href)) document.head.append(stylesheet);
  },
});
```

Then, after
[17-scripts-and-workflows.md](17-scripts-and-workflows.md#step-1-scripts-the-hooks-need)
Step 1, build the bundle as in [Step 8](#step-8-build-the-bundle), in the
order [03-repository-setup.md](03-repository-setup.md) lists.
`scripts/frontend.py` is F's, unchanged: it bundles `web/scripts/extension.ts`
and keeps ComfyUI's `app.js` and `api.js` external. The first bundle holds
this registration and the dialog styles. Nothing in ComfyUI changes yet.

## Step 2: Shared modules

In the same change, set `SINGLE_FILE_FOLDER_PATTERNS` in
`quality/config/repository/directories.js` back to `[]`, as in F. The Tooling
milestone sets it to `['web/scripts/*.ts']`, because ESLint's
`local/no-single-file-folders` refuses a folder with one code file, and
`host.d.ts` does not count. Once these modules exist, the exemption is not
needed.

Copy these from F into `web/scripts/`:

| File         | Change |
| ------------ | ------ |
| `http.ts`    | None |
| `schema.ts`  | None |
| `routes.ts`  | The four routes below |
| `browser.ts` | The limits below; the `revision` and `settingName` patterns stay |
| `dom.ts`     | Adds `externalLink` below |

`routes.ts`:

```ts
/** Local ComfyUI routes used by the browser interface. */
export const browserRoutes = {
  settings: {
    status: '/dreamina/v1/status',
    values: '/dreamina/v1/settings',
    session: '/dreamina/v1/session',
    cli: '/dreamina/v1/cli',
  },
} as const;
```

The paths equal `ROUTES` in `src/config/security.py`, which holds no other
route ([05-foundation.md](05-foundation.md#step-2-security-constants)).

`browser.ts`, replacing F's `browserLimits` (`F/web/scripts/browser.ts:2-5`):

```ts
/** Request deadlines, the sign-in poll, and response size limits for the interface. */
export const browserLimits = {
  requestTimeoutMilliseconds: 60_000,
  installTimeoutMilliseconds: 390_000,
  signInPollMilliseconds: 2_000,
  maxErrorCharacters: 1_024,
} as const;
```

`dom.ts` keeps F's `element` and `button` and adds one function, used by the
sign-in link:

```ts
/**
 * Create a link that opens a checked https address in a new tab, with no access back to this page.
 * @param text - The visible link text.
 * @param url - An https address the reply schema already checked.
 * @returns The new link.
 */
export function externalLink(text: string, url: string): HTMLAnchorElement {
  const node = element('a', text);
  node.href = url;
  node.target = '_blank';
  node.rel = 'noopener noreferrer';
  return node;
}
```

F's `nodes.ts`, `widgets.ts`, and `contracts.ts` do not exist at `cef8b6e`
and are not created: no node of this pack has a dynamic input.

## Step 3: Browser text

Port F's `web/scripts/text.ts` with its `TEXT` object, `MessageKey`,
`message`, `setText`, `LIMIT_LABELS`, and `selectedLocale` unchanged in
shape (`F/web/scripts/text.ts:4-95`). English only. Every dialog string is
below, in plain words: what happened and, where the person must act, what to
do.

`TEXT`:

```ts
/** The text the extension's dialogs show, addressed by dotted key. */
const TEXT = {
  close: 'Close',
  working: 'Working...',
  settings: {
    close: 'Close Dreamina Settings',
    invalidDefinition: 'ComfyUI returned an invalid Dreamina setting definition.',
    invalidLimit: 'ComfyUI returned an invalid Dreamina limit.',
    invalidResponse: 'ComfyUI returned an invalid Dreamina Settings response.',
    limits: 'Request limits',
    limitsSaved: 'Limits saved.',
    menu: 'Dreamina Settings',
    noLimitChanges: 'No limit changes to save.',
    readFailed: 'ComfyUI could not read Dreamina Settings.',
    readOnly: "Changes are disabled in this host's multi-user mode.",
    reading: 'Loading settings...',
    reload: 'Reload settings',
    reread: 'Settings loaded.',
    saveFailed: 'ComfyUI could not save the Dreamina settings.',
    saveLimits: 'Save limits',
    title: 'Dreamina Settings',
    unreachable: 'Cannot reach Dreamina Settings. Check that ComfyUI is running, then select Reload settings.',
    unreadableResponse: 'ComfyUI returned an unreadable Dreamina Settings response.',
    updateFailed: 'The Dreamina settings could not be saved.',
  },
  cli: {
    confirmInstall:
      "Install the Dreamina CLI on the ComfyUI computer?\n\nComfyUI downloads ByteDance's official installer from dreamina.capcut.com and runs it.",
    confirmUpdate:
      "Update the Dreamina CLI on the ComfyUI computer?\n\nComfyUI downloads ByteDance's official installer from dreamina.capcut.com and runs it.",
    current: 'Dreamina CLI {version} is installed.',
    install: 'Install',
    installFailed: 'ComfyUI could not install the Dreamina CLI.',
    installed: 'Dreamina CLI installed.',
    installing: 'Installing the Dreamina CLI. This can take a few minutes...',
    legend: 'Dreamina CLI',
    missing: 'The Dreamina CLI is not installed on the ComfyUI computer. Select Install.',
    outdated: 'Dreamina CLI {version} is installed, but the extension needs version {minimum} or later. Select Update.',
    update: 'Update',
  },
  account: {
    code: 'On the Dreamina sign-in page, check that it shows this code, then approve the sign-in:',
    expired: 'The sign-in link expired. Select Sign in to get a new one.',
    incomplete: 'The sign-in did not finish. Select Sign in to try again.',
    legend: 'Account',
    noCli: 'Install the Dreamina CLI, then sign in here.',
    notice:
      'Your sign-in stays in the Dreamina CLI on the ComfyUI computer. The extension never sees your password or sign-in tokens.',
    openPage: 'Open the sign-in page',
    plan: 'Plan: {level}',
    signIn: 'Sign in',
    signInDone: 'Signed in.',
    signInFailed: 'ComfyUI could not start the Dreamina sign-in.',
    signInStarted: 'Sign-in started. Approve it on the Dreamina page.',
    signOut: 'Sign out',
    signOutDone: 'Signed out.',
    signOutFailed: 'ComfyUI could not sign out of Dreamina.',
    signedIn: 'Signed in to Dreamina.',
    signedOut: 'Sign in with your Dreamina account to run the Dreamina nodes.',
    until: 'The link works until {time}.',
  },
} as const;
```

The keys are sorted inside each group, so a reader finds one fast. F's
credential texts (`clearKey`, `credentialLabel`, `credentials`,
`environmentKey`, `keyCleared`, `keyNotice`, `keySaved`, `removeFailed`,
`saveKey`, `savedKey`) are not ported.

`LIMIT_LABELS` keeps F's code labels and order
(`F/web/scripts/text.ts:42-46`). The defaults and ranges in the third column
are [05-foundation.md](05-foundation.md#step-3-settings-constants)'s, shown
here only so the dialog text can be checked against them. The dialog reads
them from the server:

| Setting name              | Label                       | Default and range |
| ------------------------- | --------------------------- | ----------------- |
| `request_timeout_seconds` | Request timeout (seconds)   | 1800; 10 to 3600  |
| `max_upload_megabytes`    | Maximum upload size (MB)    | 210; 1 to 210     |
| `max_download_megabytes`  | Maximum download size (MB)  | 512; 16 to 4096   |

Add one function after `message`, for the texts with `{name}` placeholders:

```ts
/**
 * Read one message and fill its named placeholders.
 * @param key - A dotted path into the extension's text.
 * @param values - The text for each placeholder name.
 * @returns The message with every known placeholder replaced.
 */
export function formatMessage(key: MessageKey, values: Readonly<Record<string, string>>): string {
  const replacements = new Map(Object.entries(values));
  return message(key).replaceAll(/\{(\w+)\}/g, (placeholder, name: string) => replacements.get(name) ?? placeholder);
}
```

The `Map` keeps the lookup clear of ESLint's `security/detect-object-injection`.

## Step 4: Local replies and requests

Add the validator, the one runtime dependency the bundle carries:

```sh
bun add --exact valibot@1.5.0
```

This updates `package.json` and `bun.lock`; both are committed with this
milestone. Bun 1.3.11 writes the new `dependencies` key last; move it back
after `packageManager`, where F has it, so `package.json` differs from F's
only in its name.

### `web/scripts/settings/schema.ts`

Port F's file (`F/web/scripts/settings/schema.ts`). `parseDefinitions` and
the checks of setting names, ranges with `minimum <= maximum`, and values
inside their ranges stay. The credential checks go: `credential`,
`credential_limit`, and `credentialLimitSchema`. The status document it
reads is owned by
[05-foundation.md](05-foundation.md#step-20-settings-routes-and-the-status-document).

The parsed shape:

```ts
export type CliStatus = {
  found: boolean;
  version: string | undefined;
  minimumVersion: string;
  isCurrent: boolean;
};

export type AccountStatus = { signedIn: boolean; vipLevel: string | undefined };

export type SignInStatus = {
  state: 'waiting' | 'expired' | 'failed';
  userCode: string;
  verificationUrl: string;
  expiresAt: number;
  message: string | undefined;
};

export type Configuration = {
  revision: string;
  mutationAllowed: boolean;
  definitions: Record<string, SettingDefinition>;
  settings: Record<string, number>;
  cli: CliStatus;
  account: AccountStatus;
  signIn: SignInStatus | undefined;
};
```

The valibot schemas for the new parts of the document. A JSON `null` becomes
`undefined` in the parsed shape, and `expires_at` becomes milliseconds with
`Date.parse`:

| Wire field | Schema |
| ---------- | ------ |
| `cli.found`, `cli.is_current` | `v.boolean()` |
| `cli.version` | `v.nullable(v.pipe(v.string(), v.minLength(1), v.maxLength(64)))` |
| `cli.minimum_version` | `v.pipe(v.string(), v.minLength(1), v.maxLength(64))` |
| `account.signed_in` | `v.boolean()` |
| `account.is_vip` | `v.nullable(v.boolean())`; checked, not kept |
| `account.vip_level` | `v.nullable(v.pipe(v.string(), v.minLength(1), v.maxLength(64)))` |
| `sign_in` | `v.nullable(v.object({…}))` with the five fields below |
| `sign_in.state` | `v.picklist(['waiting', 'expired', 'failed'])` |
| `sign_in.user_code` | `v.pipe(v.string(), v.minLength(1), v.maxLength(32))` |
| `sign_in.verification_url` | `v.pipe(v.string(), v.url(), v.startsWith('https://'))` |
| `sign_in.expires_at` | `v.pipe(v.string(), v.isoTimestamp())` |
| `sign_in.message` | `v.nullable(v.pipe(v.string(), v.minLength(1), v.maxLength(browserLimits.maxErrorCharacters)))` |

Only `https://` addresses pass, so no `javascript:` link reaches a page
element. Any other shape throws `settings.invalidResponse`, as F's parser
does.

In the same change, set the `^web/scripts/settings/schema\.ts$` rule in
`quality/config/naming/javascript.json` to these snake_case wire names, with
F's reason ("These fields are deserialized from the local settings API and
must keep their wire names."): `setting_ranges`, `mutation_allowed`,
`minimum_version`, `is_current`, `signed_in`, `is_vip`, `vip_level`,
`sign_in`, `user_code`, `verification_url`, and `expires_at`.
F's `credential_limit` leaves the list.

### `web/scripts/settings/api.ts`

Port F's `requestConfiguration` (`F/web/scripts/settings/api.ts:17-57`) with
the same options: `cache: 'no-store'`, `credentials: 'same-origin'`, the
caller's `AbortSignal` joined with a timeout, and the headers
`Content-Type: application/json` and `X-Dreamina-Comfy: 1`. The header value
is `'1'` and the name `'X-Dreamina-Comfy'`, which must equal 05's
`CHANGE_HEADER`. Two changes:

- **The timeout.** `browserLimits.installTimeoutMilliseconds` for `POST
  /dreamina/v1/cli`, and `browserLimits.requestTimeoutMilliseconds` for
  every other request.
- **The fallback messages**, used only when the server's error body is
  unreadable (`F/web/scripts/settings/api.ts:47-54`), are keyed by method
  and route:

| Request | Message key |
| ------- | ----------- |
| `GET /dreamina/v1/status` | `settings.readFailed` |
| `POST /dreamina/v1/session` | `account.signInFailed` |
| `DELETE /dreamina/v1/session` | `account.signOutFailed` |
| `POST /dreamina/v1/cli` | `cli.installFailed` |
| Any other, which is `PATCH /dreamina/v1/settings` | `settings.saveFailed` |

The server's own message, read by F's `parsePublicError`, comes first, as in
F. In the `^web/scripts/settings/api\.ts$` naming rule, the header name is
`X-Dreamina-Comfy` ([03-repository-setup.md](03-repository-setup.md)
re-values it at Tooling).

## Step 5: Settings dialog

Port F's `web/scripts/settings/dialog.ts` and add two modules beside it. The
layout, top to bottom:

1. **Header:** the H2 **Dreamina Settings** (`id="dreamina-settings-title"`)
   and **Close** (`aria-label` "Close Dreamina Settings").
1. **Dreamina CLI** form, from `settings/cli.ts`.
1. **Account** form, from `settings/account.ts`.
1. **Request limits** form: F's, with **Save limits**.
1. **Footer:** the polite `role="status"` line and **Reload settings**.

Changes to F's class names:

| F | This pack |
| - | --------- |
| `className = 'fal-ai-dialog'` | `className = 'dreamina-dialog'` |
| `'fal-ai-settings-title'` | `'dreamina-settings-title'` |
| `actions.className = 'fal-ai-actions'` | `actions.className = 'dreamina-actions'` |

### `web/scripts/settings/cli.ts`

`CliSection` builds the **Dreamina CLI** form. Its constructor takes
`CliActions`: `update(success, route, method, working)`, the dialog's
request for its button. The part reports nothing else, so it takes no
`report`.

| Part | Content |
| ---- | ------- |
| `fields` | A `<fieldset>` with the legend **Dreamina CLI**, the state sentence, and **Install** or **Update** (submit) |
| State sentence | `cli.missing` when `found` is false; `cli.current` with `{version}` when current; `cli.outdated` with `{version}` and `{minimum}` when not current |
| Button label | **Install** when `found` is false, else **Update** |

The button is the section's only control.

Behavior:

- **Install** or **Update** opens `window.confirm` with
  `message('cli.confirmInstall')` or `message('cli.confirmUpdate')`.
  The line above the call is `// eslint-disable-next-line no-alert -- The
  native prompt stays above this modal dialog, which makes the rest of the
  page, ComfyUI's dialogs included, inert.` A cancel sends nothing. An OK
  calls `update(message('cli.installed'), browserRoutes.settings.cli,
  'POST', message('cli.installing'))`.
- `display(cli)` sets the sentence and the button label.

### `web/scripts/settings/account.ts`

`AccountSection` builds the **Account** form and follows a pending sign-in.
Its constructor takes `AccountActions`: `update(success, route, method)`,
`poll()`, which returns `Promise<Configuration | undefined>`, and
`report(text)`.

What `display(configuration)` shows:

| State | Shown |
| ----- | ----- |
| CLI not found | `account.noCli`; no button |
| Signed in | `account.signedIn`; `account.plan` with `{level}` when `vipLevel` is set; **Sign out** |
| `signIn.state` is `waiting` | `account.code`; the user code in a `<p class="dreamina-code">`; **Open the sign-in page**, made with `externalLink`; `account.until` with `{time}` from `expiresAt`, written with `toLocaleTimeString(selectedLocale(), { hour: '2-digit', minute: '2-digit' })` |
| `signIn.state` is `expired` | `account.expired`; **Sign in** |
| `signIn.state` is `failed` | The server's `message`, else `account.incomplete`; **Sign in** |
| Signed out, no sign-in | `account.signedOut`; **Sign in** |

`account.notice` follows the form in every state, as F's key notice did.

Behavior:

- **Sign in** (submit) sets a private `isStarting` flag, then calls
  `update(message('account.signInStarted'), browserRoutes.settings.session,
  'POST')`.
- **Sign out** calls `update(message('account.signOutDone'),
  browserRoutes.settings.session, 'DELETE')`. It asks nothing first: signing
  in again undoes it.
- **Opening the page.** When `display` runs with `isStarting` set and
  `signIn.state` `waiting`, it calls `window.open(signIn.verificationUrl,
  '_blank', 'noopener,noreferrer')`. Every `display` then clears
  `isStarting`, so a reopened dialog or a poll never opens a tab.
- **The poll.** When `signIn.state` is `waiting` and no timer runs,
  `display` sets `setTimeout(tick, browserLimits.signInPollMilliseconds)`.
  When the state is anything else, it clears the timer. `tick` awaits
  `poll()`. An `undefined` reply ends the poll; the dialog has already shown
  the error. A reply whose `signIn.state` is no longer `waiting` reports the
  outcome:

| Reply | Status line |
| ----- | ----------- |
| `account.signedIn` true | `account.signInDone` |
| `signIn.state` `expired` | `account.expired` |
| `signIn.state` `failed` | The server's `message`, else `account.incomplete` |
| No `signIn` and signed out | `account.incomplete` |

- `dispose()` clears the timer. The dialog calls it when it closes.

Only `tick` reports outcomes, so a button's own success text, such as
"Signed out.", is never replaced by a sign-in outcome.

### The rest of `dialog.ts`

Changes to F's `SettingsDialog`:

- **Removed:** `credentials()`, the `key` input, `keyFields`, the key
  placeholder table, and the key clearing in `updateSettings` and `dispose`
  (`F/web/scripts/settings/dialog.ts:22-24`, `:65-97`, `:164-169`, `:189`,
  `:244`).
- **`display(configuration)`** keeps F's limit fields
  (`F/web/scripts/settings/dialog.ts:161-179`), then calls `cli.display` and
  `account.display`.
- **`updateSettings(success, route?, method?, body?, working?)`** is F's
  with one more argument: the working text, `message('working')` by default.
  It disables `cli.fields`, `account.fields`, `limitFields`, and `reload`,
  shows the working text, and queues `requestSettings` on the chain.
- **The chain.** A private `pending: Promise<void>` starts resolved. Each
  request is attached to it with `then`, and `pending` becomes the new
  promise with its rejection caught. So the next request starts only after
  the last one settles.
- **`requestSettings`** is F's (`F/web/scripts/settings/dialog.ts:204-233`).
  In `finally`, the three fieldsets get `disabled = !mutationAllowed`, and
  `reload` is enabled.
- **`pollStatus()`** queues a `GET` status on the chain without disabling
  anything or changing the status line. On success it calls `cli.display`
  and `account.display`, not `display`, so limits typed while a sign-in
  waits are kept and the revision stays the one the person read, and
  returns the configuration. On an error it shows the error on the status
  line and returns `undefined`. It is the account section's `poll`.
- **`dispose()`** also calls `account.dispose()`.

Kept from F, unchanged: when `mutation_allowed` is false, the fieldsets stay
disabled after each reply and the status line reads "Changes are disabled in
this host's multi-user mode."; one dialog at a time (`openSettings`
refocuses an open one, `F/web/scripts/settings/dialog.ts:257-264`); focus
returns to the opener on close; a closed dialog aborts its pending request.

Size: F's 264 lines, less about 50 for the credential form, plus about 30
for the sections and the chain, keeps `dialog.ts` near 245 lines. `cli.ts`
and `account.ts` stay under 200 each.

### `web/styles/interface.css`

Add these rules after F's, with the `dreamina-` prefix:

| Selector | Declarations | For |
| -------- | ------------ | --- |
| `.dreamina-dialog [hidden]` | `display: none` | Buttons and lines a state hides, which a later `display` rule would show |
| `.dreamina-dialog .dreamina-code` | `font-size: 1.4rem; font-weight: 600; letter-spacing: 0.12em` | The sign-in code |
| `.dreamina-dialog a` | `color: inherit; text-decoration: underline` | The sign-in link |

F's `.fal-ai-dialog > form button[type='submit']` rule
(`F/web/styles/interface.css:111-114`), renamed, colors **Install**,
**Update**, **Sign in**, and **Save limits**, the submit buttons of forms
placed directly in the dialog.

## Step 6: Wire the extension

Complete `web/scripts/extension.ts` from F's file
(`F/web/scripts/extension.ts:1-32`):

```ts
import '#styles/interface.css';
import { message } from '#web/text.ts';
import { app } from '../../scripts/app.js';
import { requestLocal } from '#web/http.ts';
import { openSettings } from '#web/settings/dialog.ts';

app.registerExtension({
  name: 'dreamina',
  setup: () => {
    const stylesheet = document.createElement('link');
    stylesheet.rel = 'stylesheet';
    stylesheet.href = new URL('./extension.css', import.meta.url).href;
    const stylesheets = new Set();
    for (const link of document.querySelectorAll('link[rel=stylesheet]')) {
      stylesheets.add(link.getAttribute('href'));
    }
    if (!stylesheets.has(stylesheet.href)) document.head.append(stylesheet);
  },
  commands: [
    {
      id: 'dreamina.OpenSettings',
      label: message('settings.menu'),
      function: openSettings.bind(null, requestLocal),
    },
  ],
  menuCommands: [
    {
      path: ['Extensions', 'Dreamina'],
      commands: ['dreamina.OpenSettings'],
    },
  ],
});
```

Imports keep the length order the copied `import.order` rule requires, as in
F. The menu path is **ComfyUI menu → Extensions → Dreamina → Dreamina
Settings**, the path every workflow note and document names
([01-decisions.md](01-decisions.md#documentation-notes-and-examples)). The
command ID and the extension name match no other pack's
([04-architecture.md](04-architecture.md#ids-other-packs-use)). Then build
the bundle ([Step 8](#step-8-build-the-bundle)).

### Generation: Download's list

**Generation: Download**'s record input is a plain dropdown of the recorded
generations, built when ComfyUI builds node definitions, as F's Request:
Download lists its requests ([14-node-download.md](14-node-download.md)).
ComfyUI re-runs `define_schema` on every `/object_info` read, so the host's
**Refresh Node Definitions** (the R key) lists a generation recorded later
and updates the dropdown of a node already on the canvas, because it is a
plain `COMBO`. The node's tooltip says so. No route or browser code is added
for it ([01-decisions.md](01-decisions.md#browser-code)).

## Step 7: Browser checks

None of these runs a paid generation. They need ComfyUI restarted with the
pack loaded, which the owner does when they choose
([03-repository-setup.md](03-repository-setup.md)), so they run after the
Frontend commit, with the Classic node design (**Settings → Nodes 2.0 →
Modern Node Design** off), as F's were. Run them in headless Chrome through
Playwright, or with the Chrome DevTools tools, at `http://127.0.0.1:8188`,
with the owner's approval, as F's dialog checks were run. Watch new tabs
with Playwright's `context.on('page')` and the requests in the network log.

Run them in this order. The owner starts signed in from
[22-owner-setup.md](22-owner-setup.md) and ends signed in.

| Check | Expected |
| ----- | -------- |
| Open **ComfyUI menu → Extensions → Dreamina → Dreamina Settings** | The dialog opens with focus in it. A second open refocuses the same dialog. It has three parts, **Dreamina CLI**, **Account**, and **Request limits**, then the footer, and no install command or canvas link. |
| Read the **Dreamina CLI** part | "Dreamina CLI 1.0.3 is installed."; one button, which reads **Update** |
| Select **Update** and dismiss the confirm | No request in the network log |
| With the owner's approval, select **Update** and accept the confirm | The confirm names ByteDance's official installer and dreamina.capcut.com. The status line reads "Installing the Dreamina CLI. This can take a few minutes...", and the buttons are disabled. Then "Dreamina CLI installed." and the version line. |
| Select **Reload settings** | "Settings loaded."; the version line again |
| Read the **Account** part | "Signed in to Dreamina." and "Plan: standard"; **Sign out** |
| Select **Sign out** | "Signed out."; **Sign in**; `dreamina-canvas --format json auth status` in a terminal reports `loggedIn` `false` |
| Select **Sign in** and do not approve | "Sign-in started. Approve it on the Dreamina page."; the code and **Open the sign-in page**; one new tab opens at the verification address; a status read every 2 seconds |
| Close the dialog, then reopen it | The code and link come back, the reads resume every 2 seconds, and no new tab opens |
| Wait until the link expires, about 10 minutes | "The sign-in link expired. Select Sign in to get a new one."; the reads stop |
| Select **Sign in**; the owner approves with the real code on dreamina.capcut.com | Within about 2 seconds of approval: "Signed in.", then "Signed in to Dreamina." and "Plan: standard"; the reads stop |
| Change one limit and select **Save limits**; select it again unchanged | "Limits saved.", then "No limit changes to save." |
| Add **Generation: Download** after a run was recorded, then press R | The dropdown lists the generation |

Optional, with the owner's approval: rename `~/.local/bin/dreamina-canvas`,
select **Reload settings**, and expect "The Dreamina CLI is not installed on
the ComfyUI computer. Select Install.", **Install**, and "Install the
Dreamina CLI, then sign in here."; rename it back and select **Reload
settings**.

The Generation: Download check runs with the Video and downloads milestone,
when it exists. The sign-in checks also settle
[02-dreamina-contract.md](02-dreamina-contract.md#sign-in)'s open fact about
what approval returns. Record each result in
[Changes made while building](README.md#changes-made-while-building).

## Step 8: Build the bundle

```sh
mise run comfy:frontend:build
```

It runs `scripts/frontend.py`, which runs esbuild on
`web/scripts/extension.ts` and writes `web/extension.js` and
`web/extension.css`: unminified ES modules with `../../scripts/app.js` and
`../../scripts/api.js` left external, and the CSS that `extension.ts`
imports. Commit both files with the source change that produced them.

`mise run comfy:frontend:check`, which the pre-commit hook runs, builds again
into `.artifacts/frontend` and compares both files byte for byte. A
difference fails the commit with "Rebuild extension.js with mise run
comfy:frontend:build." Rebuild after every change under `web/scripts/` or
`web/styles/`, and after `bun.lock` changes the bundled valibot. No node
milestone changes the browser code.

ComfyUI reads the bundle from `web/` at startup, so reload the browser tab
after a rebuild. Python changes need a ComfyUI restart instead.

The Frontend milestone commits with `feat(frontend): add the settings
dialog` ([README.md](README.md#build-order)).

State of the quality configuration at the end of this plan:

| File | State |
| ---- | ----- |
| `quality/config/repository/directories.js` | `SINGLE_FILE_FOLDER_PATTERNS` is `[]` |
| `quality/config/naming/javascript.json` | `settings/schema.ts`: the eleven wire names of Step 4. `settings/api.ts`: `Content-Type` and `X-Dreamina-Comfy`. `settings/dialog.ts`: `once`, for the dialog's close listener. No rule names `api_key`, because no file holds it. |

## Host behaviors this plan relies on

Each was read in frontend 1.52.7's shipped source, as F's research
describes, or is F's own shipped behavior. A frontend update means checking
this table again.

| Behavior | Source (frontend 1.52.7) | Used by |
| -------- | ------------------------ | ------- |
| `registerExtension`'s `commands` and `menuCommands` add a command under **Extensions** in the ComfyUI menu | F's shipped `extension.ts` (`F/web/scripts/extension.ts:19-31`) | Step 6 |
| `api.fetchApi` sends a route to the local server, which also serves every extension route under `/api` | F's shipped `requestLocal` (`F/web/scripts/http.ts:12-16`) | Every request |
| **Refresh Node Definitions** (the R key) re-reads `/object_info` and updates every plain `COMBO` widget on existing nodes | `src/scripts/app.ts:2384-2443`; `src/composables/useCoreCommands.ts:309-318` | Generation: Download's list |

These are browser behaviors, not host ones, and the checks of Step 7 confirm
them: a modal `<dialog>` makes the rest of the page inert; `window.confirm`
shows above it; and a tab opened after an awaited reply can be blocked.

## Names this plan uses from other plans

| Name | Owner | Used for |
| ---- | ----- | -------- |
| `ROUTES`, `CHANGE_HEADER` (`X-Dreamina-Comfy`) | [05-foundation.md](05-foundation.md#step-2-security-constants) | `routes.ts` and the request headers |
| The status document: `settings`, `setting_ranges`, `revision`, `cli`, `account`, `sign_in`, `mutation_allowed` | [05-foundation.md](05-foundation.md#step-20-settings-routes-and-the-status-document) | `schema.ts` and every part of the dialog |
| `SETTING_RANGES` | [05-foundation.md](05-foundation.md#step-3-settings-constants) | The limit fields, read from the reply |
| `BODY_NOT_ALLOWED`, `LOCAL_CONNECTION_REQUIRED` | [05-foundation.md](05-foundation.md#step-7-foundation-messages) | Server errors shown on the status line |
| The installer messages and `SIGN_IN_CODE_MISSING` | [05-foundation.md](05-foundation.md#step-16-installer-and-sign-in-messages) | Server errors shown on the status line |
| `INSTALLER_DOWNLOAD_SECONDS`, `INSTALL_TIMEOUT_SECONDS` | [05-foundation.md](05-foundation.md#step-15-installer-constants-account-limits-and-units) | The install timeout |
| Generation: Download's dropdown | [14-node-download.md](14-node-download.md) | Step 6's list note |
| The menu path in notes and pages | [17-scripts-and-workflows.md](17-scripts-and-workflows.md), [18-documentation.md](18-documentation.md) | Every **Start Here** note and the README |
| `scripts/frontend.py` | [17-scripts-and-workflows.md](17-scripts-and-workflows.md#step-1-scripts-the-hooks-need) | Step 8 |
| The owner's sign-in | [22-owner-setup.md](22-owner-setup.md) | The starting state of Step 7 |
