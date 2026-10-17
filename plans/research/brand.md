# Brand Research

This report holds what the image plan
([../19-brand-assets.md](../19-brand-assets.md)) is written from:

- Dreamina's own mark and colors;
- the palettes of the owner's other packs;
- the rules the owner set for images;
- the palette and mark this pack uses.

It was written on 2026-10-16. Sources:

- Dreamina's colors were sampled from the logo on
  `https://dreamina.capcut.com/ai-tool/home`, read in an isolated browser
  context (no sign-in).
- The other packs' images were read from their repositories:
  `F=/Users/dr_stone/Documents/work/comfyui-fal` at `cef8b6e`,
  `B=/Users/dr_stone/Documents/work/comfyui-byteplus` at `472cf10`,
  `O=/Users/dr_stone/Documents/work/comfyui-openrouter` at `c076f37`, and
  `R=/Users/dr_stone/Documents/work/comfyui-reactor-connector` at `b3af7ca`.

## Contents

- [1. Dreamina's mark](#1-dreaminas-mark)
- [2. The owner's image rules](#2-the-owners-image-rules)
- [3. The family design](#3-the-family-design)
- [4. The other packs' palettes](#4-the-other-packs-palettes)
- [5. This pack's palette](#5-this-packs-palette)
- [6. This pack's mark](#6-this-packs-mark)
- [7. Trademark](#7-trademark)

## 1. Dreamina's mark

The homepage header shows the mark next to the word "Dreamina":

- The mark is a 161 × 161 PNG, inlined as a data URI in the
  `button.logo-…` element whose `aria-label` is "Go to homepage".
- The word is an SVG path drawn in `currentColor`.
- The favicon is
  `https://sf16-web-tos-buz.capcutstatic.com/obj/capcut-web-buz-sg/common/images/dreamina-v3.ico`.

The mark is a four-pointed star with concave sides. Its geometry:

- It is tilted so its top point leans left and its right point sits higher
  than its left point.
- A curved diagonal gap cuts the star from the lower left side to the right
  point.
- The gap leaves a large upper piece and a small lower piece, which holds the
  bottom point.

The upper piece is a gradient. It is orange at the top point, turns yellow,
then aqua at the middle and toward the left point, then sky blue and azure
toward the right point. The lower piece is blue to deep blue.

Colors read from the PNG's opaque pixels, row by row from the top point
down (PNG coordinates, 161 × 161):

| Row | Where             | Color     | Name used in these plans |
| --- | ----------------- | --------- | ------------------------ |
| 32  | Top point         | `#E57B21` | tip orange               |
| 40  | Below the point   | `#E1AB0F` | amber                    |
| 48  | Turn to yellow    | `#D4D615` | lime yellow              |
| 56  | Upper body        | `#60D5E6` | aqua                     |
| 112 | Left point        | `#69E0EF` | light aqua               |
| 80  | Middle            | `#2BB4EC` | sky                      |
| 88  | Middle, right     | `#149FF0` | blue                     |
| 104 | Right edge        | `#028DF7` | azure                    |
| 120 | Lower piece       | `#1271FC` | deep blue                |
| 128 | Bottom point      | `#1964FF` | ultramarine              |

The most common opaque colors, quantized to steps of 24, are cyan to blue:
`#30C0F0`, `#60D8F0`, `#48C0F0`, `#18A8F0`, `#0090F0`, and `#0078F0`. The
warm colors cover a few dozen pixels at the top point only.

Dreamina's site chrome is near-black (`#111` and darker panels) with white
text. The site has no single brand color: the star's gradient is the brand.

## 2. The owner's image rules

These rules come from `F/plans/research/owner-rules.md` (section "Images"),
F's changes table (rows 263 and 264), and `rules/DOCUMENTATION.md`.

- The image set is fixed:
  - four badges;
  - the banner;
  - the logo, which is also the Registry icon;
  - the node map;
  - three screenshots.

  There is no other icon and no social preview.
- Images live in `docs/images/badges/`, `brand/`, `diagrams/`, and
  `screenshots/`, with plain kebab-case names.
- Every image is under 100 KB and has alt text. An SVG's `aria-label` and
  `<title>` equal the README's alt text.
- Badges are neutral pills under the banner. There are no colored tags and no
  result collage.
- Screenshots are real ComfyUI captures:
  - Classic node design, 100% zoom, link midpoint markers off;
  - cropped to the element;
  - compressed with `oxipng`.
- The owner rejected a flat, purple-field design for fal (row 263). They asked
  for "the family design the BytePlus, OpenRouter, and Reactor connector packs
  share, stylized for fal, without BytePlus's icon" (row 264).
- fal's rule "No image shows fal's logo" comes from fal's terms. For this pack
  the owner asked for Dreamina's star in the banner. Section 7 records the
  trademark question, and section 6 the mark that answers it.

## 3. The family design

These parts are shared, from F's and B's `docs/images/brand/banner.svg`:

| Part        | Shared value                                                                                                      |
| ----------- | ----------------------------------------------------------------------------------------------------------------- |
| Frame       | 1200 × 260, `rx="24"`, clipped, with a 1px hairline border inset by 0.5                                            |
| Background  | The ink color, then a radial glow at (1010, 130), `r="330"`, `gradientUnits="userSpaceOnUse"`, fading to 0          |
| Rails       | Two rows of small shapes on the right half, near y = 17 to 21 and y = 235 to 239, opacity rising from about 0.06 to 0.45 toward the right |
| Hairlines   | Two 1px gradient lines at y = 40 and y = 219, from x = 640, 560 wide, opacity 0.25                                 |
| Mark        | Drawn in a 200-unit box at about `translate(915 32) scale(0.98)`                                                  |
| Eyebrow     | At (64, 78): `COMFYUI EXTENSION · COMFYUI-<NAME>`, 13px SF Mono stack, letter spacing 2.34, accent color         |
| Rule        | A 40 × 2 gradient bar at (64, 94)                                                                                 |
| Title       | At (62, 158): the vendor's product name, 64px bold Helvetica Neue stack, letter spacing −1.6, gradient fill       |
| Subtitle    | At (64, 200): "<kinds> models, inside ComfyUI.", 21px, letter spacing 0.1, muted color                           |
| Gradients   | Linear, `x1="0" y1="0" x2="1" y2="1"`                                                                             |

Badges are 22px pills:

- the outer rectangle at (0.5, 0.5), `rx="10.5"`, ink fill, hairline stroke;
- the label in monospace capitals at x = 12, y = 15, 10px, letter spacing
  1.4, muted;
- a value pill filled with the gradient at
  `x = 12 + 7 × label characters + 13`, y = 3, height 16, `rx="8"`, width
  `7 × value characters + 21`;
- the value text at pill x + 10, in ink.

The node map is 992 wide, `rx="20"`:

- an eyebrow `NODE MAP` at (32, 46), and a title "<N> nodes, grouped by kind"
  at (32, 82);
- cards 296 wide at x = 32, 348, and 664, with `rx="14"`. A card is 122 high
  for one row and 168 for two;
- a paid marker: a 10 × 10 `rx="2"` square filled with the gradient;
- a free marker: an 8.5 × 8.5 hollow square with a 1.5 accent stroke;
- a dashed `4 5` legend card.

## 4. The other packs' palettes

| Token               | BytePlus (B)              | fal (F)                    | Reactor (R)               | OpenRouter (O, older look)          |
| ------------------- | ------------------------- | -------------------------- | ------------------------- | ----------------------------------- |
| Ink                 | `#06080D`                 | `#0D0C10`                  | `#070809`                 | `#211927` (ComfyUI ink)             |
| Surface             | `#10141B`                 | `#19171C`                  | `#111214`                 | `#312C34`                           |
| Hairline            | `#232A35`                 | `#27262B`                  | `#272727`                 | `#413B45`                           |
| Light text          | `#EEF3FF`                 | `#F5F3F8`                  | `#F2EEDC`                 | `#C2BFB9`                           |
| Muted text          | `#8A93A3`                 | `#A19FA4`                  | `#8F8A7C`                 | None                                 |
| Accent              | `#5C9DFF`                 | `#A284FF`                  | `#C7C099`                 | Electric yellow `#F0FF41`           |
| Title gradient      | `#9CC4FF` → `#2F80FF`     | `#C0B1FF` → `#8553FF`      | `#ECE5BD` → `#C7C099`     | Flat yellow and indigo `#6366F1`    |
| Mark gradient       | `#8DBBFF` → `#0066FC`     | `#A284FF` → `#762FF8`      | Embedded PNG              | None                                 |
| Glow                | `#0066FC` at 0.32         | `#5718C0` at 0.5           | `#C7C099` at 0.28         | None                                 |
| Second accent       | `#2F80FF` socket          | Lime `#ADFF00` socket and one rail pixel | None          | Indigo `#6366F1`                    |
| Rail shape          | Circles, r 4.5, step 38   | 8 × 8 squares, `rx` 1.5, step 34 | 22 × 14 film perforations, step 38 | None                |
| Mark                | Node tile with a plus cut out and a socket | Lowercase f with four pixels cut out and a lime socket | Drawn R with a film frame and a plug | None |

## 5. This pack's palette

The owner asked for colors that combine BytePlus's and OpenRouter's with
Dreamina's. Each token below comes from one of the three sources, and the mix
is unlike any other pack's:

- B's are blue on blue-black;
- F's are violet with lime;
- R's are gold;
- O's are yellow on purple ink.

| Token          | Value                               | From                                                     |
| -------------- | ----------------------------------- | -------------------------------------------------------- |
| Ink            | `#080A12`                           | B's blue-black, nudged toward O's indigo                 |
| Surface        | `#121522`                           | Same family, one step up                                 |
| Hairline       | `#252A3A`                           | Same family                                              |
| Light text     | `#EEF3FF`                           | B                                                        |
| Muted text     | `#8C93A8`                           | B's gray, nudged toward indigo                           |
| Accent         | `#60D5E6`                           | Dreamina aqua (eyebrow, card labels, hollow marker)      |
| Accent gradient | `#7FE3F0` → `#2F80FF` → `#6366F1`  | Dreamina light aqua, B blue, O indigo (title, rule, rails, hairlines, badge pills, paid markers) |
| Mark gradient  | `#E57B21` 0, `#E1AB0F` 0.12, `#D4D615` 0.2, `#60D5E6` 0.42, `#149FF0` 0.7, `#1964FF` 1 | Dreamina's star |
| Lower piece    | `#149FF0` → `#1964FF`               | Dreamina's star                                          |
| Glow           | `#1964FF` at 0.34                   | Dreamina ultramarine                                     |
| Second accent  | `#F0FF41`                           | O's electric yellow, which also echoes the star's yellow (socket, one rail pair) |
| Rail shape     | Four-point sparkles, 9 units across, step 34 | New: the star's own shape, small                |

Contrast checks (WCAG relative luminance):

- light text `#EEF3FF` on ink `#080A12` is 17.8:1;
- muted `#8C93A8` on ink is 6.5:1;
- the accent `#60D5E6` on ink is 11.4:1;
- the socket yellow `#F0FF41` on ink is 18.0:1;
- ink text on the gradient's stops is 13.3:1 at `#7FE3F0`, 5.3:1 at
  `#2F80FF`, and 4.4:1 at `#6366F1`. Badge values therefore use ink on the
  gradient, as B's do. The pill's text sits over its light and middle part.

## 6. This pack's mark

The mark is a redrawn four-point star, not Dreamina's PNG:

- It is drawn as SVG paths in a 200-unit box, with concave sides, tilted as
  Dreamina's is.
- A curved gap cuts it from the lower left side to the right point.
- The large piece takes the six-stop mark gradient, warm at the top point.
- The small lower piece takes the deep blue gradient.
- As every mark in the family has a socket (B's blue socket, F's lime socket,
  R's plug), this one has an O-yellow `#F0FF41` socket circle at the end of the
  right point. It reads as a ComfyUI output wired from the star.

The star alone is recognizable as Dreamina's; the socket and the redrawn
geometry make it this pack's own. The exact path data is in
[../19-brand-assets.md](../19-brand-assets.md#step-2-the-mark-and-logo).

## 7. Trademark

- Dreamina belongs to ByteDance's CapCut business. Its terms
  ([terms.md](terms.md)) license the service for personal use and say nothing
  that permits using its marks.
- fal's packs avoided fal's logo because fal's terms forbid it.
- A redrawn star in the pack's own colors, with the family socket, refers to
  Dreamina without copying its artwork.
- The owner decides between this and the exact PNG
  ([../01-decisions.md](../01-decisions.md#decisions-the-owner-should-confirm)).
  The recommendation is the redraw.
