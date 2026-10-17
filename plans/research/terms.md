# Terms, Permission, and Rejected Routes

This report records:

- what Dreamina's terms say about calling the service from software;
- what ByteDance's own CLI pages say;
- why the pack calls the Dreamina Canvas CLI and nothing else;
- the routes that were looked at and rejected.

It was written on 2026-10-16 from these sources:

- the global Dreamina terms
  (`https://www.capcut.com/clause/dreamina-terms-of-service?region=GB&lang=en`,
  last updated 2026-01-22);
- the CapCut terms (`https://www.capcut.com/clause/terms-of-service`, last
  updated 2026-04-15);
- the CLI pages `https://dreamina.capcut.com/canvas-cli` and
  `https://dreamina.capcut.com/tools/dreamina-cli`, rendered in a browser on
  2026-10-16;
- the installed skill ([docs/dreamina-canvas-cli/](docs/dreamina-canvas-cli/SKILL.md)).

It is not legal advice.

## Contents

- [1. The terms](#1-the-terms)
- [2. What ByteDance publishes for software](#2-what-bytedance-publishes-for-software)
- [3. How the pack stays inside the published route](#3-how-the-pack-stays-inside-the-published-route)
- [4. Rejected routes](#4-rejected-routes)
- [5. Trademark](#5-trademark)
- [6. Open questions for the owner](#6-open-questions-for-the-owner)

## 1. The terms

Dreamina's global terms:

- §1: "Our Services are generally provided for private, non-commercial use."
- §2: "...certain content for commercial purposes (if permitted). Such
  additional terms and policies shall be made available to you as and when
  relevant..."
- §5: Dreamina may suspend or end an account "with or without notice at any
  time for any or no reason".
- §6, "You may not", includes:
  - "copy, decipher, modify, adapt, translate, reverse engineer, disassemble,
    decompile, or create any derivative works based on, the Services ... or
    determine or attempt to determine any source code, algorithms, methods or
    techniques embodied by the Services";
  - "use the Services or any derivative works thereof in a manner which is not
    authorised by us";
  - "circumvent or bypass any measures we may use to prevent or restrict
    access to the Services";
  - "incorporate the Services into any other program or product ... except as
    expressly permitted under these Terms";
  - "use automated scripts or other technologies to collect information from
    or otherwise interact with the Services".
- §7: "...or access or use the Services or any content therein for any
  commercial or unauthorized purposes."
- §8: "if you comply with these Terms, you own the Inputs you upload, and the
  Outputs generated in response". In return the user grants Dreamina a broad
  license to use those assets.

US users fall under separate US terms with TikTok USDS Joint Venture LLC
(`https://dreamina.capcut.com/clause/dreamina-terms-of-service`).

The CapCut terms repeat the reverse-engineering clause, the "automated
scripts" clause, and the "incorporate ... into any other program or product"
clause.

The pricing FAQ (`https://dreamina.capcut.com/pricing/dreamina-price`) says
"Commercial-use eligibility depends on the applicable Dreamina terms, the
content you create...". Paid plans remove the watermark.

## 2. What ByteDance publishes for software

The Canvas CLI page (`/canvas-cli`) says:

- "Connect Dreamina to Your Agent";
- "Private beta · Advanced subscribers only";
- that the agent installs the CLI and then follows "the CLI Skill" to sign in
  and authorize access.

The Dreamina CLI page (`/tools/dreamina-cli`) says:

- "Bring Dreamina CLI generation into scripts with agent workflows and
  automated production pipelines to reduce repetitive creative work."
- That it "creates videos, and combines different generation tasks to
  efficiently produce visual assets for campaigns, experiments, and content
  workflows."

The installed skill
([SKILL.md](docs/dreamina-canvas-cli/SKILL.md#hard-boundaries)) sets the
boundary for any caller:

- "Do not call undocumented endpoints or synthesize raw HTTP requests."
- "Do not expose or persist undocumented storage/provider identifiers or
  access material."

The CLI also refuses cookie sign-in: the binary contains the error code
`cli.cookie_auth_forbidden`.

So ByteDance publishes the CLI for exactly this use: software that runs
Dreamina generations for the signed-in user, from scripts and pipelines. The
terms' "automated scripts" and "other program" clauses carve out what is
"expressly permitted" and "authorised by us". The published CLI and its skill
are the only route that authorization covers.

## 3. How the pack stays inside the published route

- **Only the installed `dreamina-canvas` binary talks to Dreamina.** The pack
  runs it as a subprocess with `--format json --non-interactive`, and sends no
  HTTP request to any Dreamina or CapCut host itself.
- **The pack never sees the person's credentials.** The CLI keeps them in the
  OS credential store
  ([authentication.md](docs/dreamina-canvas-cli/references/authentication.md#authentication)).
- **The pack uses only commands, flags, and fields** that `schema`, `model
  list`, and `voice list` return for the installed release.
- **The pack does not bundle or redistribute the binary.** It does not
  reverse-engineer or patch it. The person installs it with ByteDance's own
  installer.
- **Every paid run passes the CLI's credit approval.** The approval is
  `--credit-ceiling`, typed by the person on the node, never `--yes`.
- **The pack keeps only durable public IDs.** It never keeps tokens, signed
  links, or credit tokens, as the skill's state rules ask
  ([SKILL.md](docs/dreamina-canvas-cli/SKILL.md#persist-minimal-job-state)).

What the pack cannot settle: whether a particular commercial use is allowed.
That depends on the person's plan and Dreamina's terms. The README leaves
account conditions to Dreamina's own pages, as the owner's rule says (B
`61e08d8`).

## 4. Rejected routes

| Route                                                                 | Why rejected                                                                                                     |
| --------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| Unofficial web APIs driven by the person's browser cookies            | Forbidden by §6 and by the skill's "no raw HTTP". They break whenever request signing changes, and users report "unusual activity" blocks. |
| useapi.net and similar relays                                         | Need the person's Dreamina password on a third party's servers; same §6 problem                                   |
| Browser extensions that click the website (such as SeedFlow)          | §6 "automated scripts"; fragile                                                                                  |
| The Jimeng `dreamina` CLI (`jimeng.jianying.com/cli`)                 | Mainland China accounts only. It does not sign in an international account.                                       |
| CapCut desktop drafts                                                  | No API. Drafts are a reverse-engineered format, export needs the desktop app, and CapCut 10.x reportedly refuses drafts written by tools. Clips are joined in ComfyUI instead. |
| The BytePlus ModelArk API                                              | Official and keyed, and it serves the same Seedance and Seedream models. It is the owner's `comfyui-byteplus` pack, billed to BytePlus, not to Dreamina credits. |
| ComfyUI's ByteDance partner nodes                                     | Billed to the Comfy account through Comfy's proxy, not to Dreamina credits                                       |
| Bundling the CLI binary in the pack                                   | No license to redistribute; about 25 MB per platform. The server refuses old clients (`requiredAction=upgrade`), so a bundled copy would go stale. |

## 5. Trademark

The terms grant no right to Dreamina's or CapCut's marks. The pack's banner
and logo use a redrawn star in the pack's own palette, with the family socket,
instead of Dreamina's artwork ([brand.md](brand.md#7-trademark)). Text names
Dreamina plainly, as a product the pack works with.

## 6. Open questions for the owner

- **Eligibility.** The CLI page says "Advanced subscribers only".
  `auth account` returns `isVip` and `vipLevel`. Whether the owner's
  discounted plan passes the gate is settled by the first free discovery
  call; see [cli.md](cli.md#account-and-plan-gate).
- **Publishing.** Publishing the pack on the Comfy Registry makes the
  integration public. The owner decides when, as for the other packs
  ([../20-release.md](../20-release.md)).
