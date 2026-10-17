# Model Catalog

This report holds the models the owner's Dreamina account could call through
the CLI on 2026-10-16. Captured right after the owner signed in, with free
calls only.

**The pack never reads this file and keeps no copy of it.** The person types
any model name. Each run reads the person's live list from the CLI and checks
the name and settings against it before paying
([../06-model-check.md](../06-model-check.md)). A model Dreamina adds later
works the same day; a model it removes is refused before paying. The plans
read this file for three things only:

- the starting value of each node's `model` box;
- the models the examples use;
- the video models the test sweep runs.

## Contents

- [Account](#account)
- [What the lists show](#what-the-lists-show)
- [Image models](#image-models)
- [Video models](#video-models)
- [Audio models](#audio-models)
- [Voices](#voices)
- [File limits](#file-limits)
- [Defaults](#defaults)
- [Prices](#prices)

## Account

| Fact                         | Value                                                     | Source |
| ---------------------------- | --------------------------------------------------------- | ------ |
| CLI release                  | 1.0.3 (`244064d`, 2026-10-14 build)                        | `captures/version.json` |
| Signed in                    | Yes; credentials in the OS keyring; expire 2026-12-15     | `captures/auth-status.json` |
| `isVip`, `vipLevel`          | `true`, `standard`                                         | `captures/auth-account.json` (`userId` removed) |
| Plan gate                    | **Passed.** `model list` works on the Standard plan, though the CLI page says "Advanced subscribers only" | `captures/model-list-*.json` |
| Canvases                     | None yet                                                   | `canvas ls`, not kept |
| Models                       | 12 image, 5 video, 2 audio                                 | `captures/model-list-*.json` |

## What the lists show

These facts settle the format questions in
[../02-dreamina-contract.md](../02-dreamina-contract.md#model-discovery):

1. **Flag names start with two dashes**, such as `--ratio` and
   `--voice-name`. The pack strips them, so `arguments` keys are `ratio`,
   `resolution`, `duration`, `count`, `voice-name`, and `scenario`.
1. **`--prompt` is listed as a flag in every mode.** The node's `prompt` box
   fills it.
1. **`--model`, `--mode`, and `--ref` are never listed.** The pack sets them
   from the node.
1. **`ratio`, `resolution`, and `duration` are required, and the list gives
   no defaults.** A run without them is refused. So each node's `arguments`
   box starts with values that work for its default model
   ([Defaults](#defaults)).
1. **One mode can appear twice with different reference limits.** Every video
   model lists `first_last_frame` twice: once with exactly two images (first
   and last frame), once with exactly one image (first frame only). The pack
   picks the entry whose limits fit what is connected.
1. **`mediaType` values are `image`, `video`, and `audio`.** No list names an
   Element type. How an Element reference counts is run C-15.
1. **Membership fields.**
   - `vipRequired` is `false` for every mode.
   - `vipResolutions` names the resolutions that need membership, such as
     `4K` for Seedream and every resolution for Seedance 2.5.
   - The owner's Standard membership covers them. Part 0's price sweep shows
     whether any is refused.
1. **Reference rules seen.**
   - `requireAnyOfTypes`: `["image", "video"]` for Seedance 2.0 multimodal;
     `["image", "video", "audio"]` for Seedance 2.5 multimodal.
   - `mutuallyExclusiveTypes`: `["image", "audio"]` for `seed_audio_v1`
     omni dubbing.
1. **No music model is listed.** The `music` mode stays supported by the code
   (it is the CLI's own mode), but no example uses it.
1. **The CLI renames some flags for the service.** `model <canonical>` shows
   the underlying names: `aspect_ratio` for `--ratio`, `duration_ms`
   (milliseconds) for `--duration` (seconds). The pack uses only the CLI's
   names.

## Image models

Every image model has modes `t2i` and `i2i`. The flags are the same for both
modes; `--prompt` is required in `t2i` and optional in `i2i`.

| Model                              | Aliases       | `ratio` values                                   | `resolution` values | `count` | `i2i` images | `t2i` images | Membership resolutions |
| ---------------------------------- | ------------- | ------------------------------------------------ | ------------------- | ------- | ------------ | ------------ | ---------------------- |
| `dreamina_gpt_image_2_5_flare`     | None           | 21:9, 16:9, 3:2, 4:3, 1:1, 3:4, 2:3, 9:16 (required) | 1K, 2K, 4K (required) | 1 to 1 | 1 to 16 | none | 1K, 2K, 4K |
| `dreamina_gpt_image_2_5_sunburst`  | None           | same (required)                                  | 1K, 2K, 4K (required) | 1 to 1 | 1 to 16      | none         | 1K, 2K, 4K |
| `gemini_3_image_pro`               | `nano_banana` | same (required)                                  | 1K, 2K, 4K (required) | 1 to 4 | 1 to 6       | none         | 1K, 2K, 4K |
| `gpt_image_2`                      | None           | same (required)                                  | 1K, 2K, 4K (required) | 1 to 4 | 1 to 6       | none         | 1K, 2K, 4K |
| `jm_image_model_gg_bp_21`          | None           | 1:1, 2:3, 3:2, 3:4, 4:3, 9:16, 16:9, 21:9 (required) | 1K, 2K, 4K (required) | 1 to 4 | 1 to 14 | none | 1K, 2K, 4K |
| `seedream_4.0`                     | `4.0`         | 21:9 … 9:16 (required)                           | 2K, 4K (required)   | 1 to 8  | 1 to 6       | none         | 4K |
| `seedream_4.1`                     | `4.1`         | same (required)                                  | 2K, 4K (required)   | 1 to 8  | 1 to 6       | none         | 4K |
| `seedream_4.5`                     | `4.5`         | same (required)                                  | 2K, 4K (required)   | 1 to 8  | 1 to 6       | none         | 4K |
| `seedream_4.6`                     | `4.6`         | same (required)                                  | 2K, 4K (required)   | 1 to 8  | 1 to 6       | 0 to 14      | 4K |
| `seedream_4.7`                     | `4.7`         | same (required)                                  | 2K, 4K (required)   | 1 to 8  | 1 to 6       | 0 to 14      | 4K |
| `seedream_5.0_lite`                | `5.0lite`     | same (required)                                  | 2K, 4K (required)   | 1 to 8  | 1 to 6       | none         | 4K |
| `seedream_5.0_pro`                 | `5.0pro`      | same (**optional**)                              | 1.5K, 2K, 4K (required) | 1 to 4 | 1 to 10  | none         | 1K, 2K, 4K |

- `--prompt` takes 1 to 4,000 characters in `t2i`, and 0 to 4,000 in `i2i`.
- `seedream_4.6` and `4.7` let `t2i` take up to 14 images. The pack still
  chooses `i2i` when images are connected, unless `arguments` sets `"mode":
  "t2i"`.
- `dreamina_gpt_image_2_5_sunburst` is GPT Image 2.5 Sunburst, the model
  live-shopping uses through fal today.

## Video models

| Model               | Aliases            | Modes and references                                                                                               | `ratio` (required)            | `resolution` (required) | `duration` seconds (required) | `count` | Membership resolutions |
| ------------------- | ------------------ | ------------------------------------------------------------------------------------------------------------------ | ----------------------------- | ----------------------- | ----------------------------- | ------- | ---------------------- |
| `seedance_2.5`      | `seedance2.5`      | `t2v` none; `first_last_frame` 2 images or 1 image; `m2v` 1 to 50: images 0 to 30, videos 0 to 10, audio 0 to 10, any of image, video, audio | 21:9, 16:9, 4:3, 1:1, 3:4, 9:16 | 480p, 720p, 1080p | 4 to 30, step 1 | 1 to 4 | 480p, 720p, 1080p, 4k |
| `seedance_2.0`      | `seedance2.0`      | `t2v` none; `first_last_frame` 2 or 1 image; `m2v` 1 to 12: images 0 to 9, videos 0 to 3, audio 0 to 3, any of image or video | same | 720p, 1080p, 4K | 4 to 15, step 1 | 1 to 4 | 720p, 1080p, 4k |
| `seedance_2.0_fast` | `seedance2.0fast`  | as `seedance_2.0`                                                                                                  | same                          | 720p                    | 4 to 15, step 1               | 1 to 4  | 720p |
| `seedance_2.0_mini` | `seedance2.0mini`  | as `seedance_2.0`                                                                                                  | same                          | 720p                    | 4 to 15, step 1               | 1 to 4  | 720p |
| `seedance_pro_fast` | `seedance1.0fast`  | `t2v` none; `first_last_frame` 1 image only; no `m2v`                                                               | same                          | 720p, 1080p             | 5 to 10, step 1               | 1 to 4  | 1080p |

- `--prompt` is required in `t2v` and optional elsewhere. It takes up to
  15,000 characters on `seedance_2.5` and 4,000 on the others.
- Resolution spelling is mixed in the lists (`720p`, `4K`, `4k`). The pack
  checks the value exactly as the flag's `values` list writes it.

## Audio models

| Model           | Mode and scenario       | Flags                                                   | References                                                                 |
| --------------- | ----------------------- | ------------------------------------------------------- | -------------------------------------------------------------------------- |
| `seed_audio_v1` | `tts`, `omni-dubbing`   | `--scenario` required (`omni-dubbing`), `--prompt` required, 1 to 3,000 | 0 to 3: image 0 to 1, audio 0 to 3; image and audio not together |
| `seed_audio_v1` | `tts`, `text-reading`   | `--scenario` required (`text-reading`), `--voice-name` required, `--prompt` required, 1 to 3,000 | 0 to 1 audio                                  |

- **`seed_audio_v1` is the speech model.** A voice applies to text reading.
  The CLI also accepted `--voice-name` for omni dubbing in a free check,
  though the list does not show it there. The pack follows the list.
- The list also names one older speech model that CLI 1.0.3 cannot run by
  name. The pack ignores it, like any name it is never given.

## Voices

`voice list --model <m> --count 100`, one page each
(`captures/voices-<model>-page-0.json`):

| Model           | Count | Voice names                                                                                                   |
| --------------- | ----- | ------------------------------------------------------------------------------------------------------------- |
| `seed_audio_v1` | 13    | Good Guy, Fussy male, Jessie, Queen, Wacky, Santa II, Chill Girl, Valley Girl, Trickster, Old Style Advertising Male, Elfy, Cute Boy, Adorable Girl |

## File limits

`model <canonical>` (`captures/models/<model>.json`) adds the limits that
`model list` leaves out:

- per media type: file size, pixel size, duration;
- `maxBatchGenCount`;
- `vipConfigs`.

Model: Info reports them
([../15-node-model-info.md](../15-node-model-info.md)). The model check does
not refuse on them: the server refuses an oversized file at save time, before
any charge, and the owner's rule forbids a local copy of a check the service
makes for free.

| Models                                   | Images                                  | Videos                                                         | Audio                                         |
| ---------------------------------------- | --------------------------------------- | -------------------------------------------------------------- | --------------------------------------------- |
| Every image model, `seedance_2.0*` and `seedance_pro_fast` frames | 50 MB, up to 8,192 px per side | None                                                     | None                                          |
| `seedance_2.0`, `_fast`, `_mini` `m2v`   | 50 MB, up to 8,192 px                   | 52,428,800 bytes, 2.0 to 15.4 s, 200 to 2,160 px per side       | 15,728,640 bytes, 2.0 to 15.0 s               |
| `seedance_2.5` `m2v`                     | 50 MB, 300 to 8,192 px                  | 209,715,200 bytes, 1.8 to 30.2 s, 300 to 6,000 px per side      | 15,728,640 bytes, 1.8 to 30.2 s               |
| `seed_audio_v1`                          | 10 MB, up to 8,192 px (omni dubbing)    | None                                                            | 10 MB, 3 to 30 s                              |

The largest single file any model takes is 200 MB (a `seedance_2.5`
reference video, 209,715,200 bytes). So `max_upload_megabytes` defaults to
210 decimal megabytes, the first whole number above it, with a range of 1 to
210 ([../05-foundation.md](../05-foundation.md)).

## Defaults

The starting value of each node's `model` and `arguments` boxes. The person
replaces them freely. Each starting value meets these rules
([../01-decisions.md](../01-decisions.md#choosing-a-model)):

- the model is in the owner's live list;
- it is current, and among the least expensive of its kind;
- the starting `arguments` fill every required flag, so a fresh node runs
  with only a prompt.

| Node            | `model`             | `arguments` starting value                                   | Why                                                                                         |
| --------------- | ------------------- | ------------------------------------------------------------ | ------------------------------------------------------------------------------------------- |
| Image: Generate | `seedream_5.0_lite` | `{"ratio": "1:1", "resolution": "2K"}`                       | Current Seedream; 2K is its smallest size and needs no membership                           |
| Video: Generate | `seedance_2.0_mini` | `{"ratio": "16:9", "resolution": "720p", "duration": 4}`     | The least expensive video model at its smallest settings: 16 credits against 24 for `seedance_2.0_fast` |
| Audio: Generate | `seed_audio_v1`     | `{"voice-name": "Jessie"}`                                   | The current speech model. Text reading needs a voice; with nothing connected the node chooses text reading |
| Image: Upscale  | (no model)          | `{"resolution": "2K"}`                                       | The CLI's default mode `pro` needs a resolution; 2K is the smallest                         |

Part 0's price sweep on 2026-10-17 checked each choice and switched the video
model from `seedance_2.0_fast` to `seedance_2.0_mini`. Each node's
`credit_ceiling` default is its starting values' quote, rounded up to the next
multiple of 10:

| Node            | Quote of the starting values | `credit_ceiling` default |
| --------------- | ---------------------------- | ------------------------ |
| Image: Generate | 6                            | 10                       |
| Video: Generate | 16                           | 20                       |
| Audio: Generate | 12                           | 20                       |
| Image: Upscale  | 2                            | 10                       |

## Prices

Part 0's price sweep on 2026-10-17. Each price is Dreamina's
`minimumCreditCeiling` from a run sent with `--credit-ceiling 0` at the
lowest resolution and shortest duration the model allows, which bills
nothing. A model priced at 0 ran, for free. A model's price is the same in
every mode at the same settings.

| Model | Mode | Settings | Credits |
| ----- | ---- | -------- | ------- |
| `dreamina_gpt_image_2_5_flare` | i2i, 1 reference | ratio 1:1, resolution 1K, count 1 | 5 |
| `dreamina_gpt_image_2_5_flare` | t2i | ratio 1:1, resolution 1K, count 1 | 5 |
| `dreamina_gpt_image_2_5_sunburst` | i2i, 1 reference | ratio 1:1, resolution 1K, count 1 | 5 |
| `dreamina_gpt_image_2_5_sunburst` | t2i | ratio 1:1, resolution 1K, count 1 | 5 |
| `gemini_3_image_pro` | i2i, 1 reference | ratio 1:1, resolution 1K, count 1 | 31 |
| `gemini_3_image_pro` | t2i | ratio 1:1, resolution 1K, count 1 | 31 |
| `gpt_image_2` | i2i, 1 reference | ratio 1:1, resolution 1K, count 1 | 14 |
| `gpt_image_2` | t2i | ratio 1:1, resolution 1K, count 1 | 14 |
| `jm_image_model_gg_bp_21` | i2i, 1 reference | ratio 1:1, resolution 1K, count 1 | 9 |
| `jm_image_model_gg_bp_21` | t2i | ratio 1:1, resolution 1K, count 1 | 9 |
| `seedream_4.0` | i2i, 1 reference | ratio 1:1, resolution 2K, count 1 | 0 (ran free) |
| `seedream_4.0` | t2i | ratio 1:1, resolution 2K, count 1 | 0 (ran free) |
| `seedream_4.1` | i2i, 1 reference | ratio 1:1, resolution 2K, count 1 | 2 |
| `seedream_4.1` | t2i | ratio 1:1, resolution 2K, count 1 | 2 |
| `seedream_4.5` | i2i, 1 reference | ratio 1:1, resolution 2K, count 1 | 6 |
| `seedream_4.5` | t2i | ratio 1:1, resolution 2K, count 1 | 6 |
| `seedream_4.6` | i2i, 1 reference | ratio 1:1, resolution 2K, count 1 | 2 |
| `seedream_4.6` | t2i | ratio 1:1, resolution 2K, count 1 | 2 |
| `seedream_4.7` | i2i, 1 reference | ratio 1:1, resolution 2K, count 1 | 2 |
| `seedream_4.7` | t2i | ratio 1:1, resolution 2K, count 1 | 2 |
| `seedream_5.0_lite` | i2i, 1 reference | ratio 1:1, resolution 2K, count 1 | 6 |
| `seedream_5.0_lite` | t2i | ratio 1:1, resolution 2K, count 1 | 6 |
| `seedream_5.0_pro` | i2i, 1 reference | ratio 1:1, resolution 1.5K, count 1 | 6 |
| `seedream_5.0_pro` | t2i | ratio 1:1, resolution 1.5K, count 1 | 6 |
| `seedance_2.0` | first_last_frame, 2 references | ratio 16:9, resolution 720p, duration 4, count 1 | 52 |
| `seedance_2.0` | first_last_frame, 1 reference | ratio 16:9, resolution 720p, duration 4, count 1 | 52 |
| `seedance_2.0` | m2v, 1 reference | ratio 16:9, resolution 720p, duration 4, count 1 | 52 |
| `seedance_2.0` | t2v | ratio 16:9, resolution 720p, duration 4, count 1 | 52 |
| `seedance_2.0_fast` | first_last_frame, 2 references | ratio 16:9, resolution 720p, duration 4, count 1 | 24 |
| `seedance_2.0_fast` | first_last_frame, 1 reference | ratio 16:9, resolution 720p, duration 4, count 1 | 24 |
| `seedance_2.0_fast` | m2v, 1 reference | ratio 16:9, resolution 720p, duration 4, count 1 | 24 |
| `seedance_2.0_fast` | t2v | ratio 16:9, resolution 720p, duration 4, count 1 | 24 |
| `seedance_2.0_mini` | first_last_frame, 2 references | ratio 16:9, resolution 720p, duration 4, count 1 | 16 |
| `seedance_2.0_mini` | first_last_frame, 1 reference | ratio 16:9, resolution 720p, duration 4, count 1 | 16 |
| `seedance_2.0_mini` | m2v, 1 reference | ratio 16:9, resolution 720p, duration 4, count 1 | 16 |
| `seedance_2.0_mini` | t2v | ratio 16:9, resolution 720p, duration 4, count 1 | 16 |
| `seedance_2.5` | first_last_frame, 2 references | ratio 16:9, resolution 480p, duration 4, count 1 | 48 |
| `seedance_2.5` | first_last_frame, 1 reference | ratio 16:9, resolution 480p, duration 4, count 1 | 48 |
| `seedance_2.5` | m2v, 1 reference | ratio 16:9, resolution 480p, duration 4, count 1 | 48 |
| `seedance_2.5` | t2v | ratio 16:9, resolution 480p, duration 4, count 1 | 48 |
| `seedance_pro_fast` | first_last_frame, 1 reference | ratio 16:9, resolution 720p, duration 5, count 1 | 20 |
| `seedance_pro_fast` | t2v | ratio 16:9, resolution 720p, duration 5, count 1 | 20 |
| `seed_audio_v1` | tts omni-dubbing |  | 12 |
| `seed_audio_v1` | tts text-reading | voice-name Jessie | 12 |
| Image: Upscale | `normal` (2x) | from a 1280×720 image | 0 (ran free; 2560×1440 PNG) |
| Image: Upscale | `pro` | resolution 2K | 2 |
| Image: Upscale | `pro` | resolution 4K | 4 |
| Image: Upscale | `pro` | resolution 8K | 8 |
