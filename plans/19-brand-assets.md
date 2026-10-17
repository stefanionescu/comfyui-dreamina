# Brand Assets

This plan makes every image the README and the advanced guide show:

- four badges;
- the banner;
- the logo, which is also the Registry icon;
- the node map;
- three screenshots.

They live in `docs/images/badges/`, `brand/`, `diagrams/`, and
`screenshots/`. There is no other icon and no social preview
([research/brand.md](research/brand.md#2-the-owners-image-rules)).

The layout is the family design the owner asked the fal pack to return to.
This plan copies what the other packs ship, not their plans:

- **F**, the fal pack (`F=/Users/dr_stone/Documents/work/comfyui-fal`, commit
  `cef8b6e`). Its shipped `docs/images/brand/banner.svg`,
  `docs/images/badges/*.svg`, and `docs/images/diagrams/node-map.svg`, and
  the "Images" section of `F/ADVANCED.md`, are the template. F's own
  `plans/19-brand-assets.md` is partly outdated: it describes B's look made
  with `sed` replacements, which rows 263 and 264 of `F/plans/README.md`
  replaced.
- **B**, the BytePlus pack (`B=/Users/dr_stone/Documents/work/comfyui-byteplus`,
  commit `472cf10`). Its node map gives the arrow and the legend's third row.
- **R**, the Reactor connector pack
  (`R=/Users/dr_stone/Documents/work/comfyui-reactor-connector`, commit
  `b3af7ca`). Its banner embeds a PNG mark, which only Step 5 uses.

The colors are this pack's own. They combine B's blue, O's indigo and
electric yellow, and Dreamina's star
([research/brand.md](research/brand.md#5-this-packs-palette), which is
authoritative for colors).

This plan is for:

- the agent who builds Step 1 in the **Tooling** milestone and Steps 2 to 4
  in the **Documentation and brand** milestone
  ([README.md](README.md#build-order));
- the owner, who confirms the decisions at the end.

This plan owns the palette, every image file, and every alt text.
[18-documentation.md](18-documentation.md) places the images and copies
their alt text from this plan word for word.

Every SVG below was rendered with `rsvg-convert` 2.63.2 on 2026-10-16 and
looked at. The star reads as a tilted four-point star with a curved gap and a
socket, and every text ends inside its card or its half of the banner. The
drafts are not kept in the repository.

## Contents

- [Decisions this plan makes](#decisions-this-plan-makes)
- [Palette](#palette)
- [Step 1: Badges and banner](#step-1-badges-and-banner)
- [Step 2: The mark and logo](#step-2-the-mark-and-logo)
- [Step 3: Node map](#step-3-node-map)
- [Step 4: Screenshots](#step-4-screenshots)
- [Step 5: Dreamina's own PNG, only if the owner chooses it](#step-5-dreaminas-own-png-only-if-the-owner-chooses-it)
- [Names this plan uses from other plans](#names-this-plan-uses-from-other-plans)
- [Decisions the owner should confirm](#decisions-the-owner-should-confirm)

## Decisions this plan makes

| Question                                   | Decision                                                                                                                                                                       | Why                                                                                                                                                                                   |
| ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| What is the template?                      | F's shipped images: frame, glow, rails, hairlines, mark box, eyebrow, rule, title, subtitle, pill badges, and node-map cards, at F's positions                                 | The owner asked for the family design ([research/brand.md](research/brand.md#3-the-family-design)); F's plan 19 no longer describes F's files.                                        |
| How are the files written?                 | Hand-written SVG text, given whole in this plan. One element per line, with a final newline.                                                                                   | F's files are one line. The rendering is the same, and a change shows as one changed line. No generator script exists in any of the packs.                                            |
| What is the mark?                          | A redrawn concave four-point star, tilted as Dreamina's is, cut by a curved gap into two pieces, with a yellow socket at its right point ([Step 2](#step-2-the-mark-and-logo)) | The owner asked for Dreamina's star in the banner. A redraw in the pack's colors refers to Dreamina without copying its artwork ([research/brand.md](research/brand.md#7-trademark)). |
| How is the mark's gradient placed?         | `gradientUnits="userSpaceOnUse"`, along a fixed axis from the top point down to the right                                                                                      | The family's `x1="0" y1="0" x2="1" y2="1"` would put the orange stops in the empty top-left corner of the star's box. Dreamina's star is orange at its top point only.                |
| What are the rails?                        | Small four-point sparkles, 9 units across, on F's centers (every 34 units). The 13th pair is socket yellow at 0.7 opacity.                                                     | The star's own shape, small. F's lime pixel sits at the same place with the same opacity.                                                                                             |
| What do the badges say to a screen reader? | `aria-label` and `<title>` equal the README's alt text: "ComfyUI 0.37.2 or later", "Frontend 1.52.7 or later", "Python 3.12 or later", and "MIT license"                       | The owner's rule: an SVG's `aria-label` and `<title>` equal the README's alt text. F's files say "ComfyUI: 0.37.2+" while F's README says "ComfyUI 0.37.2 or later".                  |
| What fills a badge's value pill?           | The accent gradient, with the value in ink                                                                                                                                     | Ink on the gradient is at least 4.6 to 1 under every character, as B's ink on blue is ([Palette](#palette)).                                                                          |
| How is the node map laid out?              | Three kind cards 168 high, then a `SHARED` card 612 × 150 beside a dashed legend card 296 × 150                                                                                | B's bottom row has the same two cards. Image needs two rows, so the three kind cards share its height, as B's one-node cards do.                                                      |
| Which arrows does the node map draw?       | One: Image: Generate to Image: Upscale, inside the IMAGE card, with B's legend row "Output feeds the next node"                                                                | `references` flows from Element: Add and every paid node into every paid node. Drawn as arrows, that would cross every card. The alt text and the README say it in words.             |
| What does the paid marker mean?            | "Starts a paid run"                                                                                                                                                            | [01-decisions.md](01-decisions.md#paid-runs) calls every paid node's call a paid run, Image: Upscale's too. F's "Sends a paid request" names fal's requests.                          |
| What does Model: Info's subtitle say?      | "What a model takes"                                                                                                                                                           | F's ", for free" does not fit a third of the `SHARED` card. The hollow square already says it bills nothing.                                                                          |
| Where is the logo's source?                | `.artifacts/brand/logo.svg`, which Git ignores, as F keeps it                                                                                                                  | B tracks no source for its logo; F keeps one so the logo can be rendered again.                                                                                                       |
| How are the screenshots made?              | F's three roles and F's method: full-color crops at device scale 1, compressed with `oxipng`, in a 1,800 × 1,200 viewport                                                      | F's shipped screenshots (row 264 of `F/plans/README.md`). The Dreamina dialog has three parts, so the viewport is taller than F's 1,000 pixels.                                       |
| What personal data may a screenshot show?  | None. Any account name, email, or ID is replaced before the capture. The dialog shows no canvas address.                                                                       | [rules/DOCUMENTATION.md](../rules/DOCUMENTATION.md) asks for realistic but fictional data, with personal information removed.                                                         |

## Palette

From [research/brand.md](research/brand.md#5-this-packs-palette). Each token
comes from B, O, or Dreamina, and the mix is unlike any other pack's.

| Token             | Value                                                                                  | From                                                | Used for                                                                                  |
| ----------------- | -------------------------------------------------------------------------------------- | --------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| `ink`             | `#080A12`                                                                              | B's blue-black, nudged toward O's indigo            | Backgrounds of the banner, node map, and badges; badge values; the legend's hollow square |
| `surface`         | `#121522`                                                                              | One step up from `ink`                              | Node-map cards; the hollow square inside a card                                           |
| `hairline`        | `#252A3A`                                                                              | Same family                                         | Borders, card strokes, dividers, the dashed legend                                        |
| `text`            | `#EEF3FF`                                                                              | B                                                   | Node-map title, node names, legend lines                                                  |
| `muted`           | `#8C93A8`                                                                              | B's gray, nudged toward indigo                      | Banner subtitle, badge labels, node subtitles, the `LEGEND` label                         |
| `accent`          | `#60D5E6`                                                                              | Dreamina aqua                                       | Eyebrows, card labels, hollow-square strokes, arrows                                      |
| `accent` gradient | `#7FE3F0` 0, `#2F80FF` 0.5, `#6366F1` 1                                                | Dreamina light aqua, B blue, O indigo               | Banner title, eyebrow rule, rails, hairlines, badge value pills, paid squares             |
| `mark` gradient   | `#E57B21` 0, `#E1AB0F` 0.12, `#D4D615` 0.2, `#60D5E6` 0.42, `#149FF0` 0.7, `#1964FF` 1 | Dreamina's star                                     | The mark's large upper piece                                                              |
| `lower` gradient  | `#149FF0` 0, `#1964FF` 1                                                               | Dreamina's star                                     | The mark's small lower piece                                                              |
| `glow`            | `#1964FF`, opacity 0.34 to 0                                                           | Dreamina ultramarine                                | The radial glow behind the mark                                                           |
| `socket`          | `#F0FF41`                                                                              | O's electric yellow, which echoes the star's yellow | The mark's socket; one pair of rail sparkles                                              |

The `accent` gradient keeps the family's geometry: linear,
`x1="0" y1="0" x2="1" y2="1"`. The two mark gradients use fixed axes
([Step 2](#step-2-the-mark-and-logo)). The glow keeps the family's radial at
(1010, 130), radius 330, `gradientUnits="userSpaceOnUse"`.

Contrast, as WCAG ratios. Every image except the logo carries its own dark
background, so its inner contrast is the same on GitHub's light and dark
pages.

| Pair                                  | Ratio       | Meets                                                                  |
| ------------------------------------- | ----------- | ---------------------------------------------------------------------- |
| `text` on `ink`                       | 17.8        | AA for any text                                                        |
| `muted` on `ink`                      | 6.5         | AA for small text                                                      |
| `accent` on `ink`                     | 11.4        | AA for small text                                                      |
| `socket` on `ink`                     | 18.0        | A strong dot in the banner                                             |
| `accent` gradient on `ink`            | 13.3 to 4.4 | The 64-pixel bold title needs 3 to 1                                   |
| `ink` on the badge's value pill       | 13.3 to 4.6 | AA for the 10-pixel value under every character                        |
| `socket` on white                     | 1.1         | The logo's socket is faint on a light page (see the owner's decisions) |
| `hairline` on GitHub dark (`#0D1117`) | 1.3         | Card edges are faint on GitHub dark, as F's and B's are                |

Fonts, as F's, because a README SVG cannot load web fonts:

- Headings and body: `'Helvetica Neue', Helvetica, Arial, sans-serif`, bold
  for titles, with tight letter spacing (-1.6 at 64 pixels, -0.5 at 26,
  -0.2 at 14.5).
- Labels: a monospace stack in capitals with wide letter spacing:
  `'SF Mono', SFMono-Regular, Menlo, Consolas, 'DejaVu Sans Mono', monospace`.

## Step 1: Badges and banner

Built in the **Tooling** milestone, before the first commit. The README's
first lines link these files, and the link check reads every linked file
([18-documentation.md](18-documentation.md)).

### Badges

| Output                            | Size     | Bytes | Alt text in the README, `aria-label`, and `<title>` |
| --------------------------------- | -------- | ----- | --------------------------------------------------- |
| `docs/images/badges/comfyui.svg`  | 148 × 22 | 977   | ComfyUI 0.37.2 or later                             |
| `docs/images/badges/frontend.svg` | 155 × 22 | 980   | Frontend 1.52.7 or later                            |
| `docs/images/badges/python.svg`   | 126 × 22 | 968   | Python 3.12 or later                                |
| `docs/images/badges/license.svg`  | 118 × 22 | 949   | MIT license                                         |

The minimums are F's: ComfyUI 0.37.2, frontend 1.52.7, Python 3.12, and the
MIT license ([03-repository-setup.md](03-repository-setup.md)). The geometry
is F's:

- the outer pill at (0.5, 0.5), the full width less 1, 21 high, `rx="10.5"`,
  `ink` fill, `hairline` stroke;
- the label in capitals at (12, 15), 10-pixel monospace, letter spacing 1.4,
  `muted`;
- the value pill at x = 12 + 7 × (label characters) + 13, y = 3, 16 high,
  `rx="8"`, filled with the `accent` gradient. Its width is F's: 71 for a
  seven-character value, 56 for five, and 41 for three;
- the value text at the pill's x + 10, in `ink`;
- the full width = pill x + pill width + 3, set as `width` and in `viewBox`.

When a minimum changes, edit the version in the `aria-label`, the `<title>`,
the README's alt text, and the second `<text>` together. If the value's
length changes, the new pill width is 7 × (value characters) + 21, and the
full width follows.

`docs/images/badges/comfyui.svg`:

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="148" height="22" viewBox="0 0 148 22" role="img" aria-label="ComfyUI 0.37.2 or later">
<title>ComfyUI 0.37.2 or later</title>
<defs><linearGradient id="accent" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#7FE3F0"/><stop offset="0.5" stop-color="#2F80FF"/><stop offset="1" stop-color="#6366F1"/></linearGradient></defs>
<rect x="0.5" y="0.5" width="147" height="21" rx="10.5" fill="#080A12" stroke="#252A3A"/>
<rect x="74" y="3" width="71" height="16" rx="8" fill="url(#accent)"/>
<text x="12" y="15" font-family="'SF Mono', SFMono-Regular, Menlo, Consolas, 'DejaVu Sans Mono', monospace" font-size="10" font-weight="normal" letter-spacing="1.4" fill="#8C93A8" text-anchor="start">COMFYUI</text>
<text x="84" y="15" font-family="'SF Mono', SFMono-Regular, Menlo, Consolas, 'DejaVu Sans Mono', monospace" font-size="10" font-weight="normal" letter-spacing="1.4" fill="#080A12" text-anchor="start">0.37.2+</text>
</svg>
```

`docs/images/badges/frontend.svg`:

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="155" height="22" viewBox="0 0 155 22" role="img" aria-label="Frontend 1.52.7 or later">
<title>Frontend 1.52.7 or later</title>
<defs><linearGradient id="accent" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#7FE3F0"/><stop offset="0.5" stop-color="#2F80FF"/><stop offset="1" stop-color="#6366F1"/></linearGradient></defs>
<rect x="0.5" y="0.5" width="154" height="21" rx="10.5" fill="#080A12" stroke="#252A3A"/>
<rect x="81" y="3" width="71" height="16" rx="8" fill="url(#accent)"/>
<text x="12" y="15" font-family="'SF Mono', SFMono-Regular, Menlo, Consolas, 'DejaVu Sans Mono', monospace" font-size="10" font-weight="normal" letter-spacing="1.4" fill="#8C93A8" text-anchor="start">FRONTEND</text>
<text x="91" y="15" font-family="'SF Mono', SFMono-Regular, Menlo, Consolas, 'DejaVu Sans Mono', monospace" font-size="10" font-weight="normal" letter-spacing="1.4" fill="#080A12" text-anchor="start">1.52.7+</text>
</svg>
```

`docs/images/badges/python.svg`:

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="126" height="22" viewBox="0 0 126 22" role="img" aria-label="Python 3.12 or later">
<title>Python 3.12 or later</title>
<defs><linearGradient id="accent" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#7FE3F0"/><stop offset="0.5" stop-color="#2F80FF"/><stop offset="1" stop-color="#6366F1"/></linearGradient></defs>
<rect x="0.5" y="0.5" width="125" height="21" rx="10.5" fill="#080A12" stroke="#252A3A"/>
<rect x="67" y="3" width="56" height="16" rx="8" fill="url(#accent)"/>
<text x="12" y="15" font-family="'SF Mono', SFMono-Regular, Menlo, Consolas, 'DejaVu Sans Mono', monospace" font-size="10" font-weight="normal" letter-spacing="1.4" fill="#8C93A8" text-anchor="start">PYTHON</text>
<text x="77" y="15" font-family="'SF Mono', SFMono-Regular, Menlo, Consolas, 'DejaVu Sans Mono', monospace" font-size="10" font-weight="normal" letter-spacing="1.4" fill="#080A12" text-anchor="start">3.12+</text>
</svg>
```

`docs/images/badges/license.svg`:

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="118" height="22" viewBox="0 0 118 22" role="img" aria-label="MIT license">
<title>MIT license</title>
<defs><linearGradient id="accent" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#7FE3F0"/><stop offset="0.5" stop-color="#2F80FF"/><stop offset="1" stop-color="#6366F1"/></linearGradient></defs>
<rect x="0.5" y="0.5" width="117" height="21" rx="10.5" fill="#080A12" stroke="#252A3A"/>
<rect x="74" y="3" width="41" height="16" rx="8" fill="url(#accent)"/>
<text x="12" y="15" font-family="'SF Mono', SFMono-Regular, Menlo, Consolas, 'DejaVu Sans Mono', monospace" font-size="10" font-weight="normal" letter-spacing="1.4" fill="#8C93A8" text-anchor="start">LICENSE</text>
<text x="84" y="15" font-family="'SF Mono', SFMono-Regular, Menlo, Consolas, 'DejaVu Sans Mono', monospace" font-size="10" font-weight="normal" letter-spacing="1.4" fill="#080A12" text-anchor="start">MIT</text>
</svg>
```

### Banner

`docs/images/brand/banner.svg`, 1200 × 260, 6,733 bytes. Its alt text, in the
README's H1, the `aria-label`, and the `<title>`, is "comfyui-dreamina: a
ComfyUI extension that runs Dreamina models".

| Part      | Value                                                                                                                                                                                 | F's value                                                   |
| --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| Frame     | 1200 × 260, clipped to `rx="24"`, `ink` fill, a `hairline` border inset by 0.5                                                                                                        | Same, in F's colors                                         |
| Glow      | Radial at (1010, 130), `r="330"`, `userSpaceOnUse`, `#1964FF` at 0.34 to 0                                                                                                            | `#5718C0` at 0.5                                            |
| Rails     | 16 sparkles per rail, centered at x = 660 + 34 × n for n = 0 to 15, at y = 21 and y = 239. Opacity 0.06 + 0.026 × n, from 0.06 to 0.45. At n = 12 (x = 1068), `socket` yellow at 0.7. | 8 × 8 squares on the same centers, lime at n = 12           |
| Sparkle   | `M<x> <y − 4.5>`, then four relative quadratic curves from tip to tip, each with its control point 0.7 units from the center, so the sides curve inward. 9 units across.              | A square                                                    |
| Hairlines | Two 1-pixel `accent` gradient lines at y = 40 and y = 219, from x = 640, 560 wide, opacity 0.25                                                                                       | Same                                                        |
| Mark      | [Step 2](#step-2-the-mark-and-logo)'s mark at `translate(915 32) scale(0.98)`: x 931 to 1095, y 51 to 209, centered on the glow                                                       | F's f at the same transform                                 |
| Eyebrow   | `COMFYUI EXTENSION · COMFYUI-DREAMINA` at (64, 78), 13-pixel monospace, letter spacing 2.34, `accent`                                                                                 | `COMFYUI EXTENSION · COMFYUI-FAL`                           |
| Rule      | A 40 × 2 `accent` gradient bar at (64, 94)                                                                                                                                            | Same                                                        |
| Title     | "Dreamina" at (62, 158), 64-pixel bold, letter spacing -1.6, `accent` gradient                                                                                                        | "fal Model APIs"                                            |
| Subtitle  | "Image, video, and audio models, inside ComfyUI." at (64, 200), 21 pixels, letter spacing 0.1, `muted`                                                                                | "Image, video, audio, text, and 3D models, inside ComfyUI." |

The left texts end well before the hairlines start at x = 640. Measured in
Helvetica Neue: the eyebrow is 364 pixels wide and ends at x = 428, the title
510 and ends at x = 576, and the subtitle 464 and ends at x = 529.

Write `docs/images/brand/banner.svg` exactly:

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="260" viewBox="0 0 1200 260" role="img" aria-label="comfyui-dreamina: a ComfyUI extension that runs Dreamina models">
<title>comfyui-dreamina: a ComfyUI extension that runs Dreamina models</title>
<defs>
<linearGradient id="accent" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#7FE3F0"/><stop offset="0.5" stop-color="#2F80FF"/><stop offset="1" stop-color="#6366F1"/></linearGradient>
<linearGradient id="mark" gradientUnits="userSpaceOnUse" x1="73.8" y1="19.3" x2="138.8" y2="106"><stop offset="0" stop-color="#E57B21"/><stop offset="0.12" stop-color="#E1AB0F"/><stop offset="0.2" stop-color="#D4D615"/><stop offset="0.42" stop-color="#60D5E6"/><stop offset="0.7" stop-color="#149FF0"/><stop offset="1" stop-color="#1964FF"/></linearGradient>
<linearGradient id="lower" gradientUnits="userSpaceOnUse" x1="115.5" y1="103.4" x2="120.2" y2="180.7"><stop offset="0" stop-color="#149FF0"/><stop offset="1" stop-color="#1964FF"/></linearGradient>
<mask id="cut"><rect width="200" height="200" fill="#fff"/><circle cx="172" cy="78.5" r="19" fill="#000"/></mask>
<radialGradient id="glow" cx="1010" cy="130" r="330" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#1964FF" stop-opacity="0.34"/><stop offset="1" stop-color="#1964FF" stop-opacity="0"/></radialGradient>
<clipPath id="frame"><rect width="1200" height="260" rx="24"/></clipPath>
</defs>
<g clip-path="url(#frame)">
<rect width="1200" height="260" fill="#080A12"/>
<rect width="1200" height="260" fill="url(#glow)"/>
<path d="M660 16.5q.7 3.8 4.5 4.5q-3.8.7-4.5 4.5q-.7-3.8-4.5-4.5q3.8-.7 4.5-4.5z" fill="url(#accent)" opacity="0.06"/>
<path d="M660 234.5q.7 3.8 4.5 4.5q-3.8.7-4.5 4.5q-.7-3.8-4.5-4.5q3.8-.7 4.5-4.5z" fill="url(#accent)" opacity="0.06"/>
<path d="M694 16.5q.7 3.8 4.5 4.5q-3.8.7-4.5 4.5q-.7-3.8-4.5-4.5q3.8-.7 4.5-4.5z" fill="url(#accent)" opacity="0.086"/>
<path d="M694 234.5q.7 3.8 4.5 4.5q-3.8.7-4.5 4.5q-.7-3.8-4.5-4.5q3.8-.7 4.5-4.5z" fill="url(#accent)" opacity="0.086"/>
<path d="M728 16.5q.7 3.8 4.5 4.5q-3.8.7-4.5 4.5q-.7-3.8-4.5-4.5q3.8-.7 4.5-4.5z" fill="url(#accent)" opacity="0.112"/>
<path d="M728 234.5q.7 3.8 4.5 4.5q-3.8.7-4.5 4.5q-.7-3.8-4.5-4.5q3.8-.7 4.5-4.5z" fill="url(#accent)" opacity="0.112"/>
<path d="M762 16.5q.7 3.8 4.5 4.5q-3.8.7-4.5 4.5q-.7-3.8-4.5-4.5q3.8-.7 4.5-4.5z" fill="url(#accent)" opacity="0.138"/>
<path d="M762 234.5q.7 3.8 4.5 4.5q-3.8.7-4.5 4.5q-.7-3.8-4.5-4.5q3.8-.7 4.5-4.5z" fill="url(#accent)" opacity="0.138"/>
<path d="M796 16.5q.7 3.8 4.5 4.5q-3.8.7-4.5 4.5q-.7-3.8-4.5-4.5q3.8-.7 4.5-4.5z" fill="url(#accent)" opacity="0.164"/>
<path d="M796 234.5q.7 3.8 4.5 4.5q-3.8.7-4.5 4.5q-.7-3.8-4.5-4.5q3.8-.7 4.5-4.5z" fill="url(#accent)" opacity="0.164"/>
<path d="M830 16.5q.7 3.8 4.5 4.5q-3.8.7-4.5 4.5q-.7-3.8-4.5-4.5q3.8-.7 4.5-4.5z" fill="url(#accent)" opacity="0.19"/>
<path d="M830 234.5q.7 3.8 4.5 4.5q-3.8.7-4.5 4.5q-.7-3.8-4.5-4.5q3.8-.7 4.5-4.5z" fill="url(#accent)" opacity="0.19"/>
<path d="M864 16.5q.7 3.8 4.5 4.5q-3.8.7-4.5 4.5q-.7-3.8-4.5-4.5q3.8-.7 4.5-4.5z" fill="url(#accent)" opacity="0.216"/>
<path d="M864 234.5q.7 3.8 4.5 4.5q-3.8.7-4.5 4.5q-.7-3.8-4.5-4.5q3.8-.7 4.5-4.5z" fill="url(#accent)" opacity="0.216"/>
<path d="M898 16.5q.7 3.8 4.5 4.5q-3.8.7-4.5 4.5q-.7-3.8-4.5-4.5q3.8-.7 4.5-4.5z" fill="url(#accent)" opacity="0.242"/>
<path d="M898 234.5q.7 3.8 4.5 4.5q-3.8.7-4.5 4.5q-.7-3.8-4.5-4.5q3.8-.7 4.5-4.5z" fill="url(#accent)" opacity="0.242"/>
<path d="M932 16.5q.7 3.8 4.5 4.5q-3.8.7-4.5 4.5q-.7-3.8-4.5-4.5q3.8-.7 4.5-4.5z" fill="url(#accent)" opacity="0.268"/>
<path d="M932 234.5q.7 3.8 4.5 4.5q-3.8.7-4.5 4.5q-.7-3.8-4.5-4.5q3.8-.7 4.5-4.5z" fill="url(#accent)" opacity="0.268"/>
<path d="M966 16.5q.7 3.8 4.5 4.5q-3.8.7-4.5 4.5q-.7-3.8-4.5-4.5q3.8-.7 4.5-4.5z" fill="url(#accent)" opacity="0.294"/>
<path d="M966 234.5q.7 3.8 4.5 4.5q-3.8.7-4.5 4.5q-.7-3.8-4.5-4.5q3.8-.7 4.5-4.5z" fill="url(#accent)" opacity="0.294"/>
<path d="M1000 16.5q.7 3.8 4.5 4.5q-3.8.7-4.5 4.5q-.7-3.8-4.5-4.5q3.8-.7 4.5-4.5z" fill="url(#accent)" opacity="0.32"/>
<path d="M1000 234.5q.7 3.8 4.5 4.5q-3.8.7-4.5 4.5q-.7-3.8-4.5-4.5q3.8-.7 4.5-4.5z" fill="url(#accent)" opacity="0.32"/>
<path d="M1034 16.5q.7 3.8 4.5 4.5q-3.8.7-4.5 4.5q-.7-3.8-4.5-4.5q3.8-.7 4.5-4.5z" fill="url(#accent)" opacity="0.346"/>
<path d="M1034 234.5q.7 3.8 4.5 4.5q-3.8.7-4.5 4.5q-.7-3.8-4.5-4.5q3.8-.7 4.5-4.5z" fill="url(#accent)" opacity="0.346"/>
<path d="M1068 16.5q.7 3.8 4.5 4.5q-3.8.7-4.5 4.5q-.7-3.8-4.5-4.5q3.8-.7 4.5-4.5z" fill="#F0FF41" opacity="0.7"/>
<path d="M1068 234.5q.7 3.8 4.5 4.5q-3.8.7-4.5 4.5q-.7-3.8-4.5-4.5q3.8-.7 4.5-4.5z" fill="#F0FF41" opacity="0.7"/>
<path d="M1102 16.5q.7 3.8 4.5 4.5q-3.8.7-4.5 4.5q-.7-3.8-4.5-4.5q3.8-.7 4.5-4.5z" fill="url(#accent)" opacity="0.398"/>
<path d="M1102 234.5q.7 3.8 4.5 4.5q-3.8.7-4.5 4.5q-.7-3.8-4.5-4.5q3.8-.7 4.5-4.5z" fill="url(#accent)" opacity="0.398"/>
<path d="M1136 16.5q.7 3.8 4.5 4.5q-3.8.7-4.5 4.5q-.7-3.8-4.5-4.5q3.8-.7 4.5-4.5z" fill="url(#accent)" opacity="0.424"/>
<path d="M1136 234.5q.7 3.8 4.5 4.5q-3.8.7-4.5 4.5q-.7-3.8-4.5-4.5q3.8-.7 4.5-4.5z" fill="url(#accent)" opacity="0.424"/>
<path d="M1170 16.5q.7 3.8 4.5 4.5q-3.8.7-4.5 4.5q-.7-3.8-4.5-4.5q3.8-.7 4.5-4.5z" fill="url(#accent)" opacity="0.45"/>
<path d="M1170 234.5q.7 3.8 4.5 4.5q-3.8.7-4.5 4.5q-.7-3.8-4.5-4.5q3.8-.7 4.5-4.5z" fill="url(#accent)" opacity="0.45"/>
<rect x="640" y="40" width="560" height="1" fill="url(#accent)" opacity="0.25"/>
<rect x="640" y="219" width="560" height="1" fill="url(#accent)" opacity="0.25"/>
<g transform="translate(915 32) scale(0.98)">
<g mask="url(#cut)">
<path d="M80.1 130.5C64.1 121.7 44.2 120 16.3 123.2C67 99 80.2 75.1 73.8 19.3C98 70 121.9 83.2 177.7 76.8C130 87 100 104.4 80.1 130.5Z" fill="url(#mark)"/>
<path d="M177.7 76.8C127 101 113.8 124.9 120.2 180.7C110.5 160.4 100.9 146.1 89.2 136.7C108.8 110.6 136.7 92.1 177.7 76.8Z" fill="url(#lower)"/>
</g>
<circle cx="172" cy="78.5" r="11.5" fill="#F0FF41"/>
</g>
</g>
<rect x="0.5" y="0.5" width="1199" height="259" rx="24" fill="none" stroke="#252A3A"/>
<text x="64" y="78" font-family="'SF Mono', SFMono-Regular, Menlo, Consolas, 'DejaVu Sans Mono', monospace" font-size="13" letter-spacing="2.34" fill="#60D5E6">COMFYUI EXTENSION · COMFYUI-DREAMINA</text>
<rect x="64" y="94" width="40" height="2" fill="url(#accent)"/>
<text x="62" y="158" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="64" font-weight="bold" letter-spacing="-1.6" fill="url(#accent)">Dreamina</text>
<text x="64" y="200" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="21" letter-spacing="0.1" fill="#8C93A8">Image, video, and audio models, inside ComfyUI.</text>
</svg>
```

Then render it once and look:

```sh
mkdir -p .artifacts/brand
rsvg-convert -w 1200 docs/images/brand/banner.svg -o .artifacts/brand/banner-check.png
stat -f%z docs/images/brand/banner.svg
```

The star, its socket, the eyebrow, the title, and the subtitle are each
inside their half, and `stat` prints less than 100000.

## Step 2: The mark and logo

Built in the **Documentation and brand** milestone. Step 1's banner already
holds the mark; this step adds the logo.

### The mark

The mark is a redrawn concave four-point star in a 200-unit box:

- **Tilted as Dreamina's is.** The top point leans left, and the right point
  sits higher than the left point.
- **Concave sides.** Each side is one cubic curve from tip to tip that bows
  in toward the center.
- **A curved gap.** A swoosh-shaped gap runs from the lower-left side to the
  right point. It is 11 units wide where it starts and narrows to about 4
  where the socket's ring begins. The ring covers the rest, where the two
  edges meet at the right point.
- **Two pieces.** The large upper piece holds the top and left points and the
  upper half of the right point. It takes the `mark` gradient. The small
  lower piece holds the bottom point and the lower half of the right point.
  It takes the `lower` gradient.
- **The family socket.** A `socket` yellow circle sits at the end of the
  right point, inside a ring cut out of the star, as F's lime socket sits at
  the end of its crossbar. It reads as a ComfyUI output wired from the star.

| Point           | Coordinates                           | Note                                           |
| --------------- | ------------------------------------- | ---------------------------------------------- |
| Top point       | (73.8, 19.3)                          | The `mark` gradient's 0, orange                |
| Right point     | (177.7, 76.8)                         | Under the socket's ring                        |
| Bottom point    | (120.2, 180.7)                        | The `lower` gradient's 1, ultramarine          |
| Left point      | (16.3, 123.2)                         | Falls at 0.45 of the `mark` gradient, aqua     |
| Gap, upper edge | From (80.1, 130.5) to the right point | On the lower-left side                         |
| Gap, lower edge | From (89.2, 136.7) to the right point | On the lower-left side, 11 units farther along |
| Socket          | Center (172, 78.5), `r="11.5"`        | 6 units in from the right point along the arm  |
| Ring cut        | Center (172, 78.5), `r="19"`          | A mask, as F's `fcut` and B's `mcut` are       |

How the shape was made, for anyone who redraws it: an upright star centered
at (97, 100), with its points 84 units from the center. Each side is a cubic
whose control points sit 0.11 × 84 units off the axis and 0.34 × 84 units
from the center, toward each of the side's two points. The whole star is then
turned 16° counterclockwise about (97, 100). The gap's two edges are cubics
from the lower-left side, at 0.50 and 0.40 of its length from the bottom
point, to the right point. The path data below is the source; these numbers
only explain it.

The gradients:

- `mark`: from the top point (73.8, 19.3) to (138.8, 106). On this axis the
  left point falls at 0.45 (aqua), the center at 0.72 (blue), and the right
  point at 1 (ultramarine). Only the top point is warm, as on Dreamina's star.
- `lower`: from (115.5, 103.4), near the gap, to the bottom point
  (120.2, 180.7).

The mark fills its box with 16 to 19 units of padding on every side: x from
16.3 to 183.5 with the socket, y from 19.3 to 180.7.

### Logo

`docs/images/brand/logo.png`, 400 × 400, 8-bit RGBA on a transparent
background: the banner's mark alone, at twice its 200-unit box.

1. Write `.artifacts/brand/logo.svg` (Git ignores `.artifacts/`). It holds
   the banner's mark defs and drawing, without the banner's transform:

    ```xml
    <svg xmlns="http://www.w3.org/2000/svg" width="400" height="400" viewBox="0 0 200 200">
    <defs>
    <linearGradient id="mark" gradientUnits="userSpaceOnUse" x1="73.8" y1="19.3" x2="138.8" y2="106"><stop offset="0" stop-color="#E57B21"/><stop offset="0.12" stop-color="#E1AB0F"/><stop offset="0.2" stop-color="#D4D615"/><stop offset="0.42" stop-color="#60D5E6"/><stop offset="0.7" stop-color="#149FF0"/><stop offset="1" stop-color="#1964FF"/></linearGradient>
    <linearGradient id="lower" gradientUnits="userSpaceOnUse" x1="115.5" y1="103.4" x2="120.2" y2="180.7"><stop offset="0" stop-color="#149FF0"/><stop offset="1" stop-color="#1964FF"/></linearGradient>
    <mask id="cut"><rect width="200" height="200" fill="#fff"/><circle cx="172" cy="78.5" r="19" fill="#000"/></mask>
    </defs>
    <g mask="url(#cut)">
    <path d="M80.1 130.5C64.1 121.7 44.2 120 16.3 123.2C67 99 80.2 75.1 73.8 19.3C98 70 121.9 83.2 177.7 76.8C130 87 100 104.4 80.1 130.5Z" fill="url(#mark)"/>
    <path d="M177.7 76.8C127 101 113.8 124.9 120.2 180.7C110.5 160.4 100.9 146.1 89.2 136.7C108.8 110.6 136.7 92.1 177.7 76.8Z" fill="url(#lower)"/>
    </g>
    <circle cx="172" cy="78.5" r="11.5" fill="#F0FF41"/>
    </svg>
    ```

1. Render and compress it (rsvg-convert 2.63.2 and oxipng 10.2.1 from
   Homebrew):

    ```sh
    mkdir -p docs/images/brand
    rsvg-convert -w 400 -h 400 .artifacts/brand/logo.svg -o docs/images/brand/logo.png
    oxipng -o 4 --strip safe docs/images/brand/logo.png
    stat -f%z docs/images/brand/logo.png
    ```

    A scratch render on 2026-10-16 gave 400 × 400 and 11,901 bytes. The
    target is under 100 KB: `stat` prints less than 100000.

1. In `pyproject.toml`, under `[tool.comfy]`, name the logo as the Registry
   icon, as F's `pyproject.toml` does:

    ```toml
    Icon = "https://raw.githubusercontent.com/stefanionescu/comfyui-dreamina/main/docs/images/brand/logo.png"
    ```

    [20-release.md](20-release.md) relies on this line and does not add it
    again. The link resolves once the commit is pushed to `main`.

The logo is not shown in the README or the advanced guide, as F's is not, so
it needs no alt text there. Where a page shows it, its alt text is "The
comfyui-dreamina mark: a tilted four-point star in Dreamina's colors with a
yellow socket."

## Step 3: Node map

Built in the **Documentation and brand** milestone.
`docs/images/diagrams/node-map.svg`, 992 × 482, 8,084 bytes.

Frame and title, as F's: `rx="20"`, `ink` fill with a `hairline` border;
the eyebrow `NODE MAP` at (32, 46), 12-pixel monospace, letter spacing 2.4,
`accent`; the title "Seven nodes, grouped by kind" at (32, 82), 26-pixel
bold, letter spacing -0.5, `text`.

Cards, as F's: `rx="14"`, `surface` fill, `hairline` stroke, on columns
x = 32, 348, and 664, 296 wide, with 20-pixel gaps. Inside a card at (x, y):

- the label at (x + 20, y + 30), 11-pixel monospace, letter spacing 2.2,
  `accent`, and a divider from (x + 20, y + 40) to (x + width − 20, y + 40);
- a node's marker at x + 21 and y + 60 (the second row at y + 106);
- its name at x + 42 and y + 70 (y + 116), 14.5-pixel bold, letter spacing
  -0.2, `text`, and its subtitle 17 pixels lower, 12 pixels, `muted`;
- a paid marker: a 10 × 10 square, `rx="2"`, filled with the `accent`
  gradient;
- a free marker: an 8.5 × 8.5 square 0.75 in from the paid square's corner,
  `rx="2"`, `surface` fill, a 1.5 `accent` stroke;
- B's arrow: a 1.5 `accent` line at x + 26 from y + 71 to y + 99, with the
  head `M<x + 26> <y + 104> l-4 -6 h8 z`.

| Card              | Position and size     | Nodes (name, subtitle, marker)                                                                                                                                                                                                                                                                                                                                        |
| ----------------- | --------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `IMAGE`           | (32, 112), 296 × 168  | Generate, "From a prompt, images, or references", paid; an arrow; Upscale, "Enlarges an image or a reference", paid                                                                                                                                                                                                                                                   |
| `VIDEO`           | (348, 112), 296 × 168 | Generate, "From a prompt, frames, or references", paid                                                                                                                                                                                                                                                                                                                |
| `AUDIO`           | (664, 112), 296 × 168 | Generate, "Speech, dubbing, or music", paid                                                                                                                                                                                                                                                                                                                           |
| `SHARED`          | (32, 300), 612 × 150  | Three columns, markers at x + 21, x + 226, and x + 431: Element: Add, "A character, product, or place"; Generation: Download, "Collects a run left running"; Model: Info, "What a model takes"; all free                                                                                                                                                              |
| `LEGEND` (dashed) | (664, 300), 296 × 150 | B's legend card: no fill, `hairline` stroke with `stroke-dasharray="4 5"`, label in `muted`. "Starts a paid run" at y + 70 with a paid square, "Bills nothing" at y + 100 with a hollow square filled `ink`, and "Output feeds the next node" at y + 130 with B's legend arrow (a line from y + 117 to y + 129, head `l-4.5 -7 h9 z` at y + 133), all 13-pixel `text` |

Height = 300 + 150 + 32 = 482, set as `height` and in `viewBox`.

The alt text, in the README, the `aria-label`, and the `<title>`, word for
word. It follows F's node-map pattern and, like F's, is longer than 155
characters, because a diagram's alt text names every node:

> Node map: one card for each kind of node. Image: Generate, Video: Generate,
> and Audio: Generate each run any Dreamina model of their kind, and Image:
> Generate feeds Image: Upscale. The references output of Element: Add and of
> every paid node feeds any paid node. Generation: Download collects runs left
> running, and Model: Info shows what a model takes. A blue square marks a
> node that starts a paid run, and a hollow square one that bills nothing.

Write `docs/images/diagrams/node-map.svg` exactly:

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="992" height="482" viewBox="0 0 992 482" role="img" aria-label="Node map: one card for each kind of node. Image: Generate, Video: Generate, and Audio: Generate each run any Dreamina model of their kind, and Image: Generate feeds Image: Upscale. The references output of Element: Add and of every paid node feeds any paid node. Generation: Download collects runs left running, and Model: Info shows what a model takes. A blue square marks a node that starts a paid run, and a hollow square one that bills nothing.">
<title>Node map: one card for each kind of node. Image: Generate, Video: Generate, and Audio: Generate each run any Dreamina model of their kind, and Image: Generate feeds Image: Upscale. The references output of Element: Add and of every paid node feeds any paid node. Generation: Download collects runs left running, and Model: Info shows what a model takes. A blue square marks a node that starts a paid run, and a hollow square one that bills nothing.</title>
<defs><linearGradient id="accent" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#7FE3F0"/><stop offset="0.5" stop-color="#2F80FF"/><stop offset="1" stop-color="#6366F1"/></linearGradient></defs>
<rect width="992" height="482" rx="20" fill="#080A12"/>
<rect x="0.5" y="0.5" width="991" height="481" rx="20" fill="none" stroke="#252A3A"/>
<text x="32" y="46" font-family="'SF Mono', SFMono-Regular, Menlo, Consolas, 'DejaVu Sans Mono', monospace" font-size="12" font-weight="normal" letter-spacing="2.4" fill="#60D5E6" text-anchor="start">NODE MAP</text>
<text x="32" y="82" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="26" font-weight="bold" letter-spacing="-0.5" fill="#EEF3FF" text-anchor="start">Seven nodes, grouped by kind</text>
<rect x="32" y="112" width="296" height="168" rx="14" fill="#121522" stroke="#252A3A"/>
<text x="52" y="142" font-family="'SF Mono', SFMono-Regular, Menlo, Consolas, 'DejaVu Sans Mono', monospace" font-size="11" font-weight="normal" letter-spacing="2.2" fill="#60D5E6" text-anchor="start">IMAGE</text>
<line x1="52" y1="152" x2="308" y2="152" stroke="#252A3A"/>
<rect x="53" y="172" width="10" height="10" rx="2" fill="url(#accent)"/>
<text x="74" y="182" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="14.5" font-weight="bold" letter-spacing="-0.2" fill="#EEF3FF" text-anchor="start">Generate</text>
<text x="74" y="199" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="12" font-weight="normal" letter-spacing="0" fill="#8C93A8" text-anchor="start">From a prompt, images, or references</text>
<line x1="58" y1="183" x2="58" y2="211" stroke="#60D5E6" stroke-width="1.5"/>
<path d="M58 216 l-4 -6 h8 z" fill="#60D5E6"/>
<rect x="53" y="218" width="10" height="10" rx="2" fill="url(#accent)"/>
<text x="74" y="228" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="14.5" font-weight="bold" letter-spacing="-0.2" fill="#EEF3FF" text-anchor="start">Upscale</text>
<text x="74" y="245" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="12" font-weight="normal" letter-spacing="0" fill="#8C93A8" text-anchor="start">Enlarges an image or a reference</text>
<rect x="348" y="112" width="296" height="168" rx="14" fill="#121522" stroke="#252A3A"/>
<text x="368" y="142" font-family="'SF Mono', SFMono-Regular, Menlo, Consolas, 'DejaVu Sans Mono', monospace" font-size="11" font-weight="normal" letter-spacing="2.2" fill="#60D5E6" text-anchor="start">VIDEO</text>
<line x1="368" y1="152" x2="624" y2="152" stroke="#252A3A"/>
<rect x="369" y="172" width="10" height="10" rx="2" fill="url(#accent)"/>
<text x="390" y="182" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="14.5" font-weight="bold" letter-spacing="-0.2" fill="#EEF3FF" text-anchor="start">Generate</text>
<text x="390" y="199" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="12" font-weight="normal" letter-spacing="0" fill="#8C93A8" text-anchor="start">From a prompt, frames, or references</text>
<rect x="664" y="112" width="296" height="168" rx="14" fill="#121522" stroke="#252A3A"/>
<text x="684" y="142" font-family="'SF Mono', SFMono-Regular, Menlo, Consolas, 'DejaVu Sans Mono', monospace" font-size="11" font-weight="normal" letter-spacing="2.2" fill="#60D5E6" text-anchor="start">AUDIO</text>
<line x1="684" y1="152" x2="940" y2="152" stroke="#252A3A"/>
<rect x="685" y="172" width="10" height="10" rx="2" fill="url(#accent)"/>
<text x="706" y="182" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="14.5" font-weight="bold" letter-spacing="-0.2" fill="#EEF3FF" text-anchor="start">Generate</text>
<text x="706" y="199" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="12" font-weight="normal" letter-spacing="0" fill="#8C93A8" text-anchor="start">Speech, dubbing, or music</text>
<rect x="32" y="300" width="612" height="150" rx="14" fill="#121522" stroke="#252A3A"/>
<text x="52" y="330" font-family="'SF Mono', SFMono-Regular, Menlo, Consolas, 'DejaVu Sans Mono', monospace" font-size="11" font-weight="normal" letter-spacing="2.2" fill="#60D5E6" text-anchor="start">SHARED</text>
<line x1="52" y1="340" x2="624" y2="340" stroke="#252A3A"/>
<rect x="53.75" y="360.75" width="8.5" height="8.5" rx="2" fill="#121522" stroke="#60D5E6" stroke-width="1.5"/>
<text x="74" y="370" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="14.5" font-weight="bold" letter-spacing="-0.2" fill="#EEF3FF" text-anchor="start">Element: Add</text>
<text x="74" y="387" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="12" font-weight="normal" letter-spacing="0" fill="#8C93A8" text-anchor="start">A character, product, or place</text>
<rect x="258.75" y="360.75" width="8.5" height="8.5" rx="2" fill="#121522" stroke="#60D5E6" stroke-width="1.5"/>
<text x="279" y="370" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="14.5" font-weight="bold" letter-spacing="-0.2" fill="#EEF3FF" text-anchor="start">Generation: Download</text>
<text x="279" y="387" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="12" font-weight="normal" letter-spacing="0" fill="#8C93A8" text-anchor="start">Collects a run left running</text>
<rect x="463.75" y="360.75" width="8.5" height="8.5" rx="2" fill="#121522" stroke="#60D5E6" stroke-width="1.5"/>
<text x="484" y="370" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="14.5" font-weight="bold" letter-spacing="-0.2" fill="#EEF3FF" text-anchor="start">Model: Info</text>
<text x="484" y="387" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="12" font-weight="normal" letter-spacing="0" fill="#8C93A8" text-anchor="start">What a model takes</text>
<rect x="664" y="300" width="296" height="150" rx="14" fill="none" stroke="#252A3A" stroke-dasharray="4 5"/>
<text x="684" y="330" font-family="'SF Mono', SFMono-Regular, Menlo, Consolas, 'DejaVu Sans Mono', monospace" font-size="11" font-weight="normal" letter-spacing="2.2" fill="#8C93A8" text-anchor="start">LEGEND</text>
<rect x="685" y="360" width="10" height="10" rx="2" fill="url(#accent)"/>
<text x="706" y="370" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="13" font-weight="normal" letter-spacing="0" fill="#EEF3FF" text-anchor="start">Starts a paid run</text>
<rect x="685.75" y="390.75" width="8.5" height="8.5" rx="2" fill="#080A12" stroke="#60D5E6" stroke-width="1.5"/>
<text x="706" y="400" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="13" font-weight="normal" letter-spacing="0" fill="#EEF3FF" text-anchor="start">Bills nothing</text>
<line x1="690" y1="417" x2="690" y2="429" stroke="#60D5E6" stroke-width="1.5"/>
<path d="M690 433 l-4.5 -7 h9 z" fill="#60D5E6"/>
<text x="706" y="430" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="13" font-weight="normal" letter-spacing="0" fill="#EEF3FF" text-anchor="start">Output feeds the next node</text>
</svg>
```

Every text fits. The estimate is 8 pixels per character at 14.5-pixel bold,
so "Generation: Download" needs about 160 of its 172 pixels. The widths below
were measured in Helvetica Neue with `rsvg-convert`. Arial, the Windows
fallback, has the same widths as Helvetica. Room runs from the text's x to
the card's inner edge (card x + width − 20), or to 12 pixels before the next
column's marker.

| Text                                 | Font      | Width (px) | Room (px) |
| ------------------------------------ | --------- | ---------- | --------- |
| Seven nodes, grouped by kind         | 26 bold   | 359        | 928       |
| Generate, Upscale                    | 14.5 bold | 62, 55     | 234       |
| From a prompt, images, or references | 12        | 202        | 234       |
| Enlarges an image or a reference     | 12        | 176        | 234       |
| From a prompt, frames, or references | 12        | 200        | 234       |
| Speech, dubbing, or music            | 12        | 145        | 234       |
| Element: Add                         | 14.5 bold | 89         | 172       |
| A character, product, or place       | 12        | 160        | 172       |
| Generation: Download                 | 14.5 bold | 150        | 172       |
| Collects a run left running          | 12        | 137        | 172       |
| Model: Info                          | 14.5 bold | 75         | 140       |
| What a model takes                   | 12        | 107        | 140       |
| Starts a paid run                    | 13        | 96         | 234       |
| Output feeds the next node           | 13        | 160        | 234       |

After writing the file, render it and look:

```sh
rsvg-convert -w 992 docs/images/diagrams/node-map.svg -o .artifacts/brand/node-map-check.png
stat -f%z docs/images/diagrams/node-map.svg
```

Every name and subtitle ends before its card's edge or the next column. If
one does not, shorten its words, keep the card size, and change the alt text
with it. When a node is added, renamed, or changes from free to paid, change
the card, the title's count, and the alt text together.

## Step 4: Screenshots

Taken in the **Documentation and brand** milestone, when every node exists,
with the owner's approval to start ComfyUI (owner rule: do not restart or use
ComfyUI during the build unless the owner says).

| Output                                            | Shows                                                                                                                | Expected size                                      | Used in                      |
| ------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------- | ---------------------------- |
| `docs/images/screenshots/settings-dialog.png`     | The **Dreamina Settings** dialog, signed in, with default request limits: all three parts and the footer, nothing else | About 608 wide, the dialog's height; F's was 36 KB | ADVANCED **Settings**        |
| `docs/images/screenshots/video-generate-node.png` | A new **Video: Generate** node, 420 pixels wide, with a model, a prompt, and `arguments` typed in; nothing connected | 452 wide, the node's height; F's was 12 KB         | README **Models**            |
| `docs/images/screenshots/video-02-workflow.png`   | video-02 at 100% zoom: the **Start Here** note and the groups that fit the viewport                                  | Up to 1,800 wide; F's was 62 KB, B's 63 KB         | README **Example workflows** |

Why these three: they are F's three roles (the dialog, the main paid node,
one example). Each shows what only this pack does: a dialog that installs the
CLI and signs in, a model typed by its Dreamina name with its settings in
`arguments` under Dreamina's flag names, and an example whose media moves
between nodes as `references`. If
[17-scripts-and-workflows.md](17-scripts-and-workflows.md) gives that
example another slug, the file takes its slug.

### Set up

1. Start ComfyUI with this pack linked into `custom_nodes/dreamina`, the
   Dreamina CLI installed, the owner signed in through **Dreamina Settings**,
   and the default request limits.
1. Open `http://127.0.0.1:8188` in Chrome with the chrome-devtools tools, and
   `resize_page` to 1,800 by 1,200 at a device scale factor of 1, so a
   capture is at 100% browser zoom. When no Chrome can be attached, use
   headless Chrome through Playwright with a 1,800 × 1,200 viewport and
   `deviceScaleFactor: 1`, as F did. Where this step says `evaluate_script`,
   Playwright's `page.evaluate` does the same.
1. In ComfyUI's settings: the default dark theme, the Classic node design,
   100% canvas zoom, and link midpoint markers off (**Settings → Lite Graph →
   Link midpoint markers**: None). For the node and the workflow, turn on
   focus mode, so no side panel shows.

### Each view

- **Settings dialog.** Open **ComfyUI menu → Extensions → Dreamina →
  Dreamina Settings**. The dialog must not scroll; if it does, make the
  viewport taller. Then remove personal data with `evaluate_script`: set the
  text of any element that shows the account's name, email, or user ID to
  `Dreamina account`. [16-frontend.md](16-frontend.md) names those elements'
  classes.
- **Video: Generate node.** Add a new **Video: Generate** node and set its
  width to 420 with `evaluate_script`
  (`node.setSize([420, node.size[1]])`, then `app.canvas.setDirty(true, true)`).
  Set its inputs:
    - `model`: `seedance_2.0_mini`, the Video: Generate starting value in
      [research/catalog.md](research/catalog.md#defaults), which a new node
      already shows. If Part 0 of [21-test-runs.md](21-test-runs.md)
      switches the starting model, the node shows that name, and the alt
      text names it.
    - `prompt`: `A host holds up a green bottle and smiles at the camera.`
    - `arguments`: the starting `{"ratio": "16:9", "resolution": "720p",
      "duration": 4}`, which a new node already shows. The alt text names
      these values.

    Connect nothing. `credit_ceiling` and `run_number` keep their defaults.

- **Workflow.** Open video-02 from **Browse Templates → dreamina**, and pan
  so the **Start Here** note is at the top left.

### Capture, crop, and compress

1. Capture the viewport with `take_screenshot` (or Playwright's
   `page.screenshot`) to `.artifacts/shots/<name>.png`.
1. Read the element's rectangle with `evaluate_script`:
    - the dialog: `document.querySelector("dialog.dreamina-dialog").getBoundingClientRect()`,
      with no margin;
    - the node: Classic nodes are drawn on the canvas, so compute the
      rectangle from LiteGraph, with a 16-pixel margin on every side:

        ```js
        () => {
            const pad = 16;
            const box = app.canvas.canvas.getBoundingClientRect();
            const { offset, scale } = app.canvas.ds;
            const title = LiteGraph.NODE_TITLE_HEIGHT;
            const node = app.graph.nodes.find((item) => item.type === 'DreaminaVideoGenerate');
            return {
                x: Math.round(box.left + (node.pos[0] + offset[0]) * scale - pad),
                y: Math.round(box.top + (node.pos[1] - title + offset[1]) * scale - pad),
                width: Math.round(node.size[0] * scale + 2 * pad),
                height: Math.round((node.size[1] + title) * scale + 2 * pad),
            };
        };
        ```

        At 100% zoom the width is 420 + 32 = 452, as F's is.

    - the workflow: the same computation over the **Start Here** note and
      every group (`group.pos`, `group.size`) whose right edge fits in the
      viewport, joined into one rectangle, with the same 16-pixel margin.

1. Crop and compress, from the repository root:

    ```sh
    magick .artifacts/shots/<name>.png -crop <width>x<height>+<x>+<y> +repage -strip docs/images/screenshots/<name>.png
    oxipng -o 4 --strip safe docs/images/screenshots/<name>.png
    stat -f%z docs/images/screenshots/<name>.png
    ```

1. `stat` must print less than 100000. If it does not, crop closer and
   repeat. If the workflow is still too large, reduce it to 256 colors
   without dithering, as B's plan did, then run `oxipng` again:

    ```sh
    magick docs/images/screenshots/video-02-workflow.png +dither -colors 256 PNG8:docs/images/screenshots/video-02-workflow.png
    ```

1. Correct each alt text below to what the capture shows, with the inputs in
   node order, and give the README or ADVANCED the same text.

Retake `settings-dialog.png` when the dialog changes,
`video-generate-node.png` when Video: Generate's inputs change, and
`video-02-workflow.png` when video-02's notes or groups change.

### Alt text

The labels come from [16-frontend.md](16-frontend.md) and
[10-node-video.md](10-node-video.md). The inputs follow
[01-decisions.md](01-decisions.md#the-inputs-of-a-paid-node)'s order:
sockets, then widgets, then text boxes.

| Image                     | Alt text                                                                                                                                                                                                                                                                                                                                 |
| ------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `settings-dialog.png`     | The Dreamina Settings dialog, signed in: Dreamina CLI with the installed version and Update; Account with the plan and Sign out; Request limits with Request timeout (seconds), Maximum upload size (MB), Maximum download size (MB), and Save limits; and Reload settings at the bottom.                                              |
| `video-generate-node.png` | Video: Generate on the canvas: the images, videos, audio, and references inputs; model set to seedance_2.0_mini; credit_ceiling; run_number; a prompt about a host holding up a green bottle; and arguments holding ratio 16:9, resolution 720p, and duration 4.                                                                         |
| `video-02-workflow.png`   | Written from the capture in F's form: "Screenshot of video-02: the Start Here note and the &lt;name&gt; note sit above &lt;count&gt; groups. &lt;Group&gt; holds &lt;its nodes or prompts&gt;, and &lt;Group&gt; holds &lt;its nodes or prompts&gt;." It names only the groups the crop shows, with 17's group names.                    |

### Text for ADVANCED

[18-documentation.md](18-documentation.md) takes this text for the
"Images" section of `ADVANCED.md`, in F's form:

> The README's and this guide's images are in `docs/images/`:
>
> - `brand/banner.svg`, `diagrams/node-map.svg`, and the four `badges/*.svg`
>   files are SVG files; edit them as text. They follow the owner's other
>   packs' layout in this pack's colors: near-black `#080A12`, surfaces
>   `#121522`, hairlines `#252A3A`, light text `#EEF3FF`, muted text
>   `#8C93A8`, aqua `#60D5E6`, the gradient `#7FE3F0` to `#2F80FF` to
>   `#6366F1`, and yellow `#F0FF41` for the mark's socket and one sparkle in
>   each rail. Headings use Helvetica Neue with tight spacing; labels use a
>   monospace font in wide-spaced capitals.
> - `brand/logo.png` is the extension's mark: a tilted four-point star,
>   orange at its top point through aqua to blue, cut by a curved gap, with a
>   yellow socket at the end of its right point, at 400 × 400 pixels on a
>   transparent background. Its source is `.artifacts/brand/logo.svg`, which
>   Git ignores; render it with `rsvg-convert` and compress it with `oxipng`.
>   The banner draws the same mark between two rails of small sparkles, and
>   `pyproject.toml` names `brand/logo.png` as the Registry icon.
> - The node map has one card for each kind of node. A blue square marks a
>   node that starts a paid run, a hollow square one that bills nothing, and
>   an arrow an output that feeds the next node.
> - The badges under the banner name the ComfyUI, frontend, and Python
>   versions and the license, as near-black pills with a blue value; update
>   them when those change.
> - `screenshots/video-02-workflow.png` is video-02 at 100% zoom, with link
>   midpoint markers off.
> - `screenshots/video-generate-node.png` is a new **Video: Generate** node,
>   420 pixels wide, at 100% zoom, with a model, a prompt, and `arguments`
>   typed in.
> - `screenshots/settings-dialog.png` is the **Dreamina Settings** dialog,
>   signed in, with default request limits.
>
> The star is this extension's own drawing, not Dreamina's logo. Keep each
> image under 100 KB, and give it alt text.

## Step 5: Dreamina's own PNG, only if the owner chooses it

This step is not part of the build. It runs only if the owner chooses
Dreamina's exact mark in
[Decisions the owner should confirm](#decisions-the-owner-should-confirm).

What it would use: the 161 × 161 PNG in the header of
`https://dreamina.capcut.com/ai-tool/home`, inlined as a data URI in the
`button` whose `aria-label` is "Go to homepage"
([research/brand.md](research/brand.md#1-dreaminas-mark)).

Why it is not recommended:

1. **No license.** Dreamina belongs to ByteDance's CapCut business. Its terms
   license the service for personal use and grant no right to its marks
   ([research/brand.md](research/brand.md#7-trademark),
   [research/terms.md](research/terms.md#5-trademark)).
1. **It reads as Dreamina's own product.** The README's purpose sentence and
   the install folder are chosen so nothing reads as Dreamina's own product
   ([01-decisions.md](01-decisions.md#names-and-identifiers)). Dreamina's
   exact logo as the Registry icon would undo that.
1. **It is too small.** The logo is 400 × 400. A 161-pixel PNG enlarged
   2.5 times is soft at the edges.
1. **It breaks the family.** Every mark in the family has a socket (B's blue
   socket, F's lime socket, R's plug). Dreamina's PNG has none.

If the owner chooses it anyway, with Dreamina's written permission first:

1. In a browser on that page, copy the PNG's data URI from the `button`
   (its `img` `src` or its CSS `background-image`), then save it, from the
   repository root:

    ```sh
    pbpaste | sed 's|^data:image/png;base64,||' | base64 -D > .artifacts/brand/dreamina-mark.png
    magick identify .artifacts/brand/dreamina-mark.png
    ```

    `identify` must print `PNG 161x161`.

1. In `docs/images/brand/banner.svg`, delete the `mark` and `lower`
   gradients and the `cut` mask from `<defs>`, and replace the
   `<g transform="translate(915 32) scale(0.98)">` group, with everything in
   it, by one element, as R's banner embeds its mark:

    ```xml
    <image x="917" y="37" width="186" height="186" href="data:image/png;base64,<the base64 text saved above>"/>
    ```

    `base64 -i .artifacts/brand/dreamina-mark.png` prints the text. The
    banner then grows by about four thirds of the PNG's size and stays under
    100 KB.

1. Make the logo from the PNG:

    ```sh
    magick .artifacts/brand/dreamina-mark.png -filter Lanczos -resize 400x400 docs/images/brand/logo.png
    oxipng -o 4 --strip safe docs/images/brand/logo.png
    ```

1. Change ADVANCED's "Images" text to say the mark is Dreamina's logo, used
   with permission. The alt texts do not change.

## Names this plan uses from other plans

| Name                                                                                                                                                                                     | Owner                                                                                             | Used for                                               |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- | ------------------------------------------------------ |
| The seven nodes, their display names, paid or free, `NODE_TYPES` order                                                                                                                   | [01-decisions.md](01-decisions.md#the-nodes)                                                      | The node map's cards, markers, title, and alt text     |
| The inputs of a paid node, in order                                                                                                                                                      | [01-decisions.md](01-decisions.md#the-inputs-of-a-paid-node)                                      | The node screenshot's alt text                         |
| Repository `stefanionescu/comfyui-dreamina`, install folder `dreamina`, node ID `DreaminaVideoGenerate`, CSS prefix `dreamina-`, menu path **Extensions → Dreamina → Dreamina Settings** | [01-decisions.md](01-decisions.md#names-and-identifiers)                                          | The eyebrow, the `Icon` link, and the screenshot steps |
| The banner title and subtitle, the redrawn mark                                                                                                                                          | [01-decisions.md](01-decisions.md#brand-and-images)                                               | Step 1 and Step 2                                      |
| The palette, Dreamina's mark, the family design, the owner's image rules                                                                                                                 | [research/brand.md](research/brand.md)                                                            | Every image                                            |
| The minimum ComfyUI, frontend, and Python versions, and the license                                                                                                                      | [03-repository-setup.md](03-repository-setup.md)                                                  | The badges                                             |
| The settings dialog's parts, labels, and element classes                                                                                                                                 | [16-frontend.md](16-frontend.md)                                                                  | `settings-dialog.png` and its alt text                 |
| Video: Generate's inputs and their labels                                                                                                                                                | [10-node-video.md](10-node-video.md)                                                              | `video-generate-node.png` and its alt text             |
| The video starting model and `arguments`, `seedance_2.0_mini` with `{"ratio": "16:9", "resolution": "720p", "duration": 4}`                                                              | [research/catalog.md](research/catalog.md#defaults), Part 0 of [21-test-runs.md](21-test-runs.md) | `video-generate-node.png`                              |
| video-02, its notes, and its groups                                                                                                                                                      | [17-scripts-and-workflows.md](17-scripts-and-workflows.md)                                        | `video-02-workflow.png` and its alt text               |
| Where each image appears in the README and ADVANCED                                                                                                                                      | [18-documentation.md](18-documentation.md)                                                        | Copies this plan's alt texts and its ADVANCED text     |
| The `Icon` line under `[tool.comfy]`                                                                                                                                                     | [20-release.md](20-release.md)                                                                    | Relies on Step 2                                       |
| The milestones                                                                                                                                                                           | [README.md](README.md#build-order)                                                                | When each step is built                                |

## Decisions the owner should confirm

The owner decided the mark (the redrawn star) and the banner title
("Dreamina") on 2026-10-17. The rest are decided as recommended. Each is easy to change before the
**Documentation and brand** milestone.

| Decision                        | Recommended                                                              | Alternative                                                                                                           |
| ------------------------------- | ------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------- |
| The socket on light pages       | `#F0FF41` everywhere, one mark in the banner and the logo                | In `logo.svg` only, a 2-unit `#080A12` stroke around the socket, so it shows on a light Registry page                 |
| The node map's arrows           | One arrow, Image: Generate to Image: Upscale, and the legend row         | No arrow and a two-row legend, as F's map has; or arrows from Element: Add to every paid card                         |
| The rail shape                  | Small four-point sparkles                                                | F's square pixels or B's dots, in this palette                                                                        |
| The workflow screenshot         | video-02, the example whose media moves between nodes as `references`    | Another example that 17 builds                                                                                        |
