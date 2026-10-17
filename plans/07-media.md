# Media, References, and Downloads

This plan builds everything between ComfyUI's media and Dreamina's
resources:

- the constants and messages for encoding, uploads, references, and
  downloads;
- the `Reference` record the `DREAMINA_REFERENCES` socket carries, and the
  `LocalMedia` record of a connected item waiting for its upload;
- the encoders that write ComfyUI images, video, and audio to files, and the
  decoders that turn downloaded files back into ComfyUI values;
- the uploads (`resource upload`);
- the reference checks, the `--ref` order, and the prompt placeholders;
- the downloads (`resource download`) and their checks.

It ports F's media code (`F=/Users/dr_stone/Documents/work/comfyui-fal`,
commit `cef8b6e`): `F/src/comfy/media.py`, `F/src/fal/uploads.py`,
`F/src/fal/outputs.py`, `F/src/types/files.py`, `F/src/config/media.py`,
`F/src/config/messages/media.py`, and the decoding half of
`F/src/nodes/outputs.py`. It follows F's code as built, with the rows of F's
changes table that touch 07: the upload memory was dropped
(`F/plans/README.md:262`), the encoders are private `_encode_*` functions
and the file kind is `FileKind` (`F/plans/README.md:238`), and 07 was
committed with temporary allowlist entries (`F/plans/README.md:237`). Each
step names what changes from F. `C` is ComfyUI 0.37.2 at
`/Users/dr_stone/ComfyUI-Installs/ComfyUI/ComfyUI`, as F's research names
it.

Readers:

- the engineer who writes `src/config/media.py`,
  `src/config/messages/media.py`, `src/types/references.py`,
  `src/comfy/media.py`, and `src/dreamina/{uploads,references,downloads}.py`;
- the writers of [08-runs.md](08-runs.md) and the node plans, who call these
  functions.

Nothing in this plan is implemented. It was written on 2026-10-16 from
[01-decisions.md](01-decisions.md#media-references-and-placeholders),
[02-dreamina-contract.md](02-dreamina-contract.md),
[04-architecture.md](04-architecture.md#module-inventory),
[research/cli.md](research/cli.md), [research/catalog.md](research/catalog.md),
the owner's captures in `research/captures/`, F's code, and C's source.

This plan is built in the **Media and runs** milestone, interleaved with
[08-runs.md](08-runs.md) Part B, because each reads the other's records
([08-runs.md](08-runs.md#when-each-part-is-built)):

1. this plan's Steps 1 to 5;
1. 08's Steps 7 to 9, which add the reply records this plan reads
   (`UploadReply`, `DownloadReply`, `NodeView`) and `OutputFile`;
1. this plan's Steps 6 to 10;
1. 08's Steps 10 to 19.

Both ship in one commit, `feat(nodes): add uploads, runs and downloads`. It
calls what is built earlier:

- 08 Part A (Foundation milestone): `send_command`, `build_failure`, and the
  CLI records;
- [06-model-check.md](06-model-check.md) (Model check milestone): the model
  list records, the chosen mode, `describe_mode`, and `src/config/media.py`
  with `MEDIA_TYPES`;
- [05-foundation.md](05-foundation.md): settings, errors, and the shared
  constants.

The contract runs C-2 to C-15 come before this milestone (milestone 4 of the
build order). Read their results before Step 1
([Live checks](#live-checks)).

Media reaches a paid node in two ways
([01-decisions.md](01-decisions.md#the-inputs-of-a-paid-node)):

- **Local media** through the `images`, `videos`, and `audio` list sockets.
  Each item is uploaded with the run and sent as `--ref res:<uuid>`.
- **References** through the `references` socket: canvas nodes and resources
  that other Dreamina nodes made, sent as `--ref node:<id>` or
  `--ref res:<uuid>` with no upload.

ComfyUI's formats, confirmed in 0.37.2
([F/plans/research/comfy.md](../../comfyui-fal/plans/research/comfy.md#6-media-helpers)):

| Type    | Python value                                                                          |
| ------- | ------------------------------------------------------------------------------------- |
| `IMAGE` | `torch.float32` tensor `[B, H, W, C]`, values 0 to 1, C is 3 (sometimes 4)            |
| `AUDIO` | `{"waveform": tensor [B, C, T] float32 in -1 to 1, "sample_rate": int}`               |
| `VIDEO` | An `Input.Video`: `InputImpl.VideoFromFile`, `VideoFromComponents`, or `VideoFromList` |

## Contents

- [Decisions this plan makes](#decisions-this-plan-makes)
- [Step 1: Media constants](#step-1-media-constants)
- [Step 2: Media messages](#step-2-media-messages)
- [Step 3: Reference and placeholder messages](#step-3-reference-and-placeholder-messages)
- [Step 4: Placeholder pattern](#step-4-placeholder-pattern)
- [Step 5: Reference records](#step-5-reference-records)
- [Step 6: Conversions](#step-6-conversions)
- [Step 7: Uploads](#step-7-uploads)
- [Step 8: References and placeholders](#step-8-references-and-placeholders)
- [Step 9: Downloads](#step-9-downloads)
- [Step 10: Temporary allowlist entries](#step-10-temporary-allowlist-entries)
- [What other plans do with these](#what-other-plans-do-with-these)
- [Live checks](#live-checks)
- [Names this plan uses from other plans](#names-this-plan-uses-from-other-plans)

## Decisions this plan makes

| Question | Decision | Why |
| -------- | -------- | --- |
| What is uploaded for each kind? | Each image frame as a PNG at its own size, keeping a fourth channel; each audio clip as 16-bit WAV; each video as MP4 through ComfyUI's `save_to`, which copies an MP4 source's streams. | [01-decisions.md](01-decisions.md#media-formats). PNG is lossless. WAV keeps every sample; AAC in MP4, ComfyUI's default, padded 44,100 samples to 45,056 in F's research. C-2 to C-4 confirm each format. |
| What is one upload? | One file per item: each frame of an IMAGE batch, each VIDEO, and each clip of an AUDIO batch. `list_local_media` splits the inputs and numbers each kind from 1. | A placeholder and a `--ref` each name one item, and `resource upload` takes one file (schema: `resource upload` `--file`). F's File: Add split batches the same way. |
| Where do encoded files live? | In one private temporary folder per `send_media` call, made with `tempfile.TemporaryDirectory(prefix=".dreamina-")`, named `<kind>-<position>.<extension>`, and deleted as soon as that call's uploads finish. | The CLI takes a path. The file name becomes the resource's name on the canvas (schema: `resource upload` `--name`, "omit to use the file name"). No encoded file outlives its upload, so none remains after the run ([01-decisions.md](01-decisions.md#local-media)). |
| Is anything remembered between runs? | No. Each run uploads its own media. Within one call, items with the same bytes (the full SHA-256) are uploaded once and share one `Reference`. | F's owner dropped the upload memory (`F/plans/README.md:262`); F's per-request map (`F/src/fal/uploads.py:65-71`) is kept. |
| When is an upload or a download sent a second time? | Once at most (`FREE_ATTEMPTS`), and only when its outcome is unknown: a reply the CLI runner could not read, `error.retryable` true, or for an upload `error.code` `cli.upload_state_unknown`; for a download also a file that fails the length or SHA-256 check. An upload's second try reuses its `--resource-id`. | Uploads and downloads are free and "are tried again within the request timeout" ([01-decisions.md](01-decisions.md#paid-runs)). The client-made resource ID is "reused for retries across processes" (schema: `resource upload`), so a second try never makes a second resource. One more try covers a lost reply without a retry loop. |
| How is an upload reply checked? | Its `resourceId` must equal the ID sent. `mediaType` is not checked. | The schema says the ID is "always echoed as resourceId". Dreamina checks the type itself, for free, when the run saves. |
| Which file limits are checked locally? | Only the person's own `max_upload_megabytes` (default 210, range 1 to 210, [05-foundation.md](05-foundation.md)). Each model's file size, pixel, and duration limits are not checked. | `model <canonical>` gives per-model limits ([research/catalog.md](research/catalog.md#file-limits)), but the server refuses an oversized file at save, before any charge, and the owner forbids a local copy of a free check. The largest file any listed model takes is 209,715,200 bytes. |
| The `--ref` order | `references` in socket order, then images, videos, and audio, each by position. | [01-decisions.md](01-decisions.md#order). |
| Placeholders | `{{image1}}`, `{{video1}}`, `{{audio1}}`, and `{{reference1}}` count from 1 within their input, and become `{{res:<uuid>}}` or `{{node:<id>}}`. A placeholder for an item that is not connected is refused. Any other `{{…}}` is sent unchanged. A `{{` after a backslash is never touched. | [01-decisions.md](01-decisions.md#placeholders); `\{{` is the CLI's literal `{{` (schema: `node create video` `--prompt`). |
| What is checked before uploading? | Every count and type against the mode entry 06's `choose_mode` picked: `min`, `max`, `types[]`, `requireAnyOfTypes`, and `mutuallyExclusiveTypes`; an omitted `references` means none. Two CLI rules the list cannot express are added: a `voice-name` in speech fills one audio slot, and an Element never fills a frame. | [01-decisions.md](01-decisions.md#checking-a-model-before-paying): each check reads a field the list returned. The skill states both added rules ([Step 8](#step-8-references-and-placeholders)). One mode can appear twice with different limits ([research/catalog.md](research/catalog.md#what-the-lists-show)), so the entry matters. |
| How does an Element count? | As `MediaKind` `element`, mapped by `MEDIA_TYPES` to the list's `image`. Run C-15 settles the mapping. | No list names an Element type; the lists use only `image`, `video`, and `audio` ([research/catalog.md](research/catalog.md#what-the-lists-show)). The skill accepts an Element where `i2i` needs an image. |
| Image outputs | Three channels, `[1, H, W, 3]`, read with `mode="RGB"`. A fourth channel is dropped, and there is no mask output. | Dreamina's image modes (`t2i`, `i2i`, upscale) make opaque pictures, and [01-decisions.md](01-decisions.md#outputs) has no mask socket. F's masks paired with fal's cut-out models, which this pack does not run. |
| How is a download checked? | `size` above 0 and within `max_download_megabytes`, the file's length equal to `size`, and its SHA-256 equal to `sha256`. Each file is read into memory and deleted at once. | The skill's download checks: "a zero-byte or clearly implausible file is not a valid delivery", and "record the SHA256 returned by the CLI" (`skill: references/completion-and-validation.md#download-checks`). |
| An output of an unknown type | Stops before any download, with `RESOURCE_TYPE`. The generation record stays. | A type outside image, video, and audio means the CLI changed. Generation: Download collects the run after an update. |
| If video or audio cannot be downloaded | Stop the Video or Audio milestone and record it. Never download through an address taken from a reply or found elsewhere. | The schema's summary reads "Safely download a successful image resource" (run C-3). The skill forbids undocumented endpoints and raw HTTP ([01-decisions.md](01-decisions.md#why-the-cli)). |
| Where the encoder runs | `encode_local_file` is synchronous. `send_media` runs it with `asyncio.to_thread`, as F's queue operation ran its encoder (`F/src/fal/queue/operation.py:306-310`). | `src.dreamina` may not import `src.comfy`, where `wait_for_thread` lives ([04-architecture.md](04-architecture.md#import-layers)). |

## Step 1: Media constants

[06-model-check.md](06-model-check.md#srcconfigmediapy) creates
`src/config/media.py` one milestone earlier, holding only `MEDIA_TYPES`,
because 06's `choose_mode` reads it. That module already has this plan's
docstring, "How local media is written for upload, how references reach the
CLI, and how outputs are sorted.", and `MEDIA_TYPES` with the comment and
value below. Add the other 11 constants to it, ported from
`F/src/config/media.py`, so the module reads:

```python
# A ComfyUI IMAGE tensor: batch, height, width, and three or four channels. Each connected frame reaches the encoder
# alone, as [1, H, W, C], and a decoded image is [1, H, W, 3].
IMAGE_TENSOR = {
    "DIMENSIONS": 4,
    "RGB_CHANNELS": 3,
    "RGBA_CHANNELS": 4,
}

# What each kind of local media is written as before its upload, and the --type resource upload takes for it: PNG at
# the image's own size, 16-bit WAV, and MP4.
UPLOAD_FORMATS = {
    "image": {"EXTENSION": "png", "TYPE": "image"},
    "video": {"EXTENSION": "mp4", "TYPE": "video"},
    "audio": {"EXTENSION": "wav", "TYPE": "audio"},
}

# The WAV container and codec PyAV writes audio with.
WAV = {
    "FORMAT": "wav",
    "CODEC": "pcm_s16le",
}

# An upload or a download bills nothing, so one whose outcome is unknown is sent a second time, and never a third.
FREE_ATTEMPTS = 2

# The CLI's code for an upload whose outcome it could not learn; the same resource ID makes the second try safe.
UPLOAD_STATE_UNKNOWN = "cli.upload_state_unknown"

# The word the CLI writes before a node ID or a resource ID, in --ref and in a prompt placeholder.
REFERENCE_TYPES = {
    "node": "node",
    "resource": "res",
}

# Each placeholder word a prompt may use, with the input whose items it counts from 1, in --ref order.
PLACEHOLDERS = {
    "reference": "references",
    "image": "images",
    "video": "videos",
    "audio": "audio",
}

# The mediaType the live model list counts each kind of reference as. The lists name no Element type, and an Element
# is expected to count as an image (run C-15).
MEDIA_TYPES = {
    "image": "image",
    "video": "video",
    "audio": "audio",
    "element": "image",
}

# The modes whose frames take images only: an Element counts as an image in the list's limits, but never fills a frame.
FRAME_MODES = ("first_last_frame",)

# In speech, a voice set with this flag fills one audio reference slot, as a connected audio clip does.
VOICE_REFERENCE = {
    "FLAG": "voice-name",
    "MODE": "tts",
}

# The kind of an output resource by the type node show gives it.
RESOURCE_KINDS = {
    "image": "image",
    "video": "video",
    "audio": "audio",
}

# The status node show gives a resource that finished and can be downloaded.
RESOURCE_SUCCESS = "success"
```

`MEDIA_TYPES` is unchanged from 06. The module ends with `__all__` listing
the 12 names in ASCII order: `FRAME_MODES`, `FREE_ATTEMPTS`, `IMAGE_TENSOR`,
`MEDIA_TYPES`, `PLACEHOLDERS`, `REFERENCE_TYPES`, `RESOURCE_KINDS`,
`RESOURCE_SUCCESS`, `UPLOAD_FORMATS`, `UPLOAD_STATE_UNKNOWN`,
`VOICE_REFERENCE`, `WAV`.

In the same step, add `BYTES_PER_MEGABYTE = 1_000_000` to
`src/config/units.py`, with 05's comment "A megabyte is 1,000,000 bytes, as
the settings count them.", and to its `__all__`. The upload and download
limits of this plan are its first readers
([05-foundation.md](05-foundation.md#step-15-installer-constants-account-limits-and-units)).

Why these values:

- **`UPLOAD_FORMATS`.** F's `ENCODED_FORMATS` (`F/src/config/media.py:17-22`)
  without `mask` and without `CONTENT_TYPE`: the CLI takes a file and a
  `--type`, never a content type. `TYPE` is the CLI's own word for
  `--type` (schema: `resource upload`, "image|video|audio; overrides file
  extension"). It is passed every time, so Dreamina never guesses the kind
  from the extension.
- **`FREE_ATTEMPTS` and `UPLOAD_STATE_UNKNOWN`.** The binary holds the code
  `cli.upload_state_unknown` (research/cli.md, "Media and resources", from
  strings). It names exactly the case the resource ID exists for.
- **`REFERENCE_TYPES`.** "Generation flags and prompt placeholders use
  `type:value` / `{{type:value}}`", with `node:node_xxx` and
  `res:<canonical lowercase UUID>`
  (`skill: references/identity-and-references.md#public-identity-model`).
- **`MEDIA_TYPES`.** The captures `model-list-image.json`,
  `model-list-video.json`, and `model-list-audio.json` use only `image`,
  `video`, and `audio` ([research/catalog.md](research/catalog.md#what-the-lists-show),
  item 6). `element` maps to `image` until run C-15 shows how an Element
  counts.
- **`FRAME_MODES`.** "An Element must not occupy a `first_last_frame` slot"
  ([research/cli.md](research/cli.md#elements)). Since an Element counts as
  an image, the list's image limits alone would let one through.
- **`VOICE_REFERENCE`.** "A voice counts as an audio reference and shares the
  selected model and scenario's `references.max` and audio type limit with
  ordinary audio"
  (`skill: references/identity-and-references.md#audio-model-and-voice-selection`).
  It explains the live list: `seed_audio_v1` text reading requires
  `voice-name` and takes 0 to 1 audio, so the voice fills the one slot, as
  the skill's "references are not supported" for text reading says.
- **`RESOURCE_KINDS` and `RESOURCE_SUCCESS`.** `node show` gives each
  resource a `type` and a `status` (schema: `node show`). `resource get`
  names the states "running/success/failed/canceled" (schema:
  `resource get` summary). Run C-8 confirms both spellings on `node show`.
  `RESOURCE_SUCCESS` is a field of `node show`, not the `state` that
  `operation wait` gives, whose values are 08's `OPERATION_STATES`.

F's `MASK_TENSOR`, `ENCODED_FORMATS`, `DIGEST_CHARACTERS`, `OUTPUT_KINDS`,
`MESH_FORMATS`, `OUTPUT_ID_KINDS`, `INLINE_PREFIX`, `LINK_SCHEME`, and
`MAX_LINK_CHARACTERS` are not ported. There are no masks, links, 3D files, or
inline files. An output's kind comes from its resource `type`. Files are
named by kind and position, and the in-call map keys on the full digest.

## Step 2: Media messages

Create `src/config/messages/media.py`, ported from
`F/src/config/messages/media.py`, with the docstring "Messages for media
that cannot be encoded, uploaded, downloaded, or read." and the second
paragraph "{reason} is the CLI's cleaned reason, ending as a sentence."
Constants in ASCII order:

| Constant            | Code               | Text |
| ------------------- | ------------------ | ---- |
| `AUDIO_EMPTY`       | `INVALID_INPUT`    | `The connected audio has no samples.` |
| `AUDIO_UNREADABLE`  | `MEDIA`            | `An audio file Dreamina returned could not be decoded. It is still on the ComfyUI canvas at dreamina.capcut.com.` |
| `AUDIO_UNWRITABLE`  | `MEDIA`            | `The connected audio could not be written as WAV. Use mono or stereo audio.` |
| `DOWNLOAD_EMPTY`    | `MEDIA`            | `Dreamina returned an empty file for an output. The run stays recorded, so Generation: Download can collect it again later.` |
| `DOWNLOAD_FAILED`   | from 08's map      | `An output could not be downloaded from Dreamina: {reason} The run stays recorded, so Generation: Download can collect it again.` |
| `DOWNLOAD_LIMIT`    | `MEDIA`            | `An output from Dreamina is {size} MB, above the maximum download size of {maximum} MB in Dreamina Settings. Raise it, then collect the run with Generation: Download.` |
| `DOWNLOAD_MISMATCH` | `MEDIA`            | `A downloaded output did not match the size and checksum Dreamina reported, so it was not used. The run stays recorded, so Generation: Download can collect it again.` |
| `IMAGE_CHANNELS`    | `INVALID_INPUT`    | `Connect a ComfyUI image with three or four color channels.` |
| `IMAGE_PIXELS`      | `INVALID_INPUT`    | `The connected image holds values that are not numbers. Check the node that made it.` |
| `IMAGE_UNREADABLE`  | `MEDIA`            | `An image Dreamina returned could not be decoded. It is still on the ComfyUI canvas at dreamina.capcut.com.` |
| `OUTPUTS_MISSING`   | `MEDIA`            | `Dreamina reports the run finished, but its canvas node holds no finished output from it yet. The run stays recorded, so Generation: Download can collect it later.` |
| `RESOURCE_TYPE`     | `MEDIA`            | `Dreamina returned an output of a type this extension cannot read: {type}. Update the extension, then collect the run with Generation: Download.` |
| `UPLOAD_LIMIT`      | `INVALID_INPUT`    | `A connected {kind} is {size} MB, above the maximum upload size of {maximum} MB in Dreamina Settings. Connect a smaller {kind}, or raise the limit there.` |
| `UPLOAD_REFUSED`    | from 08's map      | `Dreamina refused a connected file: {reason} Nothing was billed. Check that the media opens in ComfyUI, then run again.` |
| `UPLOAD_UNREADABLE` | `TRANSPORT`        | `Dreamina's answer to an upload could not be read. Nothing was billed. Run again.` |
| `VIDEO_UNREADABLE`  | `MEDIA`            | `A video Dreamina returned could not be read. It is still on the ComfyUI canvas at dreamina.capcut.com.` |
| `VIDEO_UNWRITABLE`  | `MEDIA`            | `The connected video could not be written as MP4.` |

- **Sizes** are decimal megabytes (`BYTES_PER_MEGABYTE`), rounded up to
  0.1 MB, as F shows them (`F/src/fal/operation.py:31-37`). `{kind}` is
  `image`, `video`, or `audio`. `{maximum}` is the setting's value.
- **`UPLOAD_REFUSED` and `DOWNLOAD_FAILED`** are the `context` this plan
  passes to 08's `build_failure(result, context)`: the message 08's map uses,
  filled with the cleaned `validation.detail` or `error.message`, when the
  failure has no fixed-fix message of its own (sign-in, upgrade, network).
  08's map picks their `ErrorCode`.
- **"The run stays recorded"** is true for every download message: 08 deletes
  a generation record only after `download_resources` returns
  ([04-architecture.md](04-architecture.md#how-a-paid-run-flows)). The
  `*_UNREADABLE` decoder messages come after that deletion, so they point to
  the canvas instead.
- **What changes from F.** `IMAGE_PIXELS` drops "or mask". The decoder
  messages name Dreamina and the canvas. `UPLOAD_LIMIT` names Dreamina
  Settings and drops F's sentence about fal's 100 MB and File: Add. F's
  `MASK_SHAPE` and `INLINE_UNREADABLE` are not ported. The download and upload
  messages are new: F's `DOWNLOAD_LIMIT`, `UPLOAD_FAILED`, and
  `UPLOAD_UNREADABLE` lived in its transport's messages, and here the
  modules of this plan raise them.

The module ends with `__all__` listing the 17 names in ASCII order.

## Step 3: Reference and placeholder messages

[04-architecture.md](04-architecture.md#srcconfig) puts reference-limit
messages in `src/config/messages/models.py` and placeholder refusals in
`src/config/messages/inputs.py`. Both modules exist from 06. Their first
raiser is this plan's `src/dreamina/references.py`, so this step adds them
(the owner's rule: a message arrives with the first milestone that needs
it). 06 does not define them. Each constant is inserted in ASCII order among
06's constants and added to the module's `__all__`.

Add to `src/config/messages/models.py`, all raised with `INVALID_INPUT`:

| Constant                    | Text |
| --------------------------- | ---- |
| `REFERENCES_ANY_OF`         | `Mode {mode} of this model needs at least one reference of these kinds: {media}. Connect one.` |
| `REFERENCES_ELEMENT_FRAME`  | `Mode {mode} takes only images as frames, and an Element cannot be one. Disconnect the Element, or set another mode in arguments.` |
| `REFERENCES_EXCLUSIVE`      | `Mode {mode} of this model cannot take {media} references together. Keep one kind and disconnect the others.` |
| `REFERENCES_NONE`           | `Mode {mode} of this model takes no images, videos, audio, or references, but the run has {count}. Disconnect them, or set another mode in arguments.` |
| `REFERENCES_TOTAL`          | `Mode {mode} of this model takes at least {minimum} and at most {maximum} references in all, but the run has {count}.` |
| `REFERENCE_KIND_COUNT`      | `Mode {mode} of this model takes at least {minimum} and at most {maximum} {media} references, but the run has {count}.` |
| `REFERENCE_KIND_REFUSED`    | `Mode {mode} of this model takes no {media} references, but the run has {count}. Disconnect them, or set another mode in arguments.` |
| `VOICE_COUNTED`             | `The voice-name in arguments counts as one audio reference.` |

- `{mode}` is 06's `describe_mode(mode)`: the mode's name, followed by its
  scenario in parentheses when it has one, such as `tts (omni-dubbing)`
  ([06-model-check.md](06-model-check.md#step-4-choose-the-mode)). 06's own
  refusals fill `{mode}` the same way.
- `{media}` is the pack's kind word (`image`, `video`, `audio`, or `element`)
  for a type the pack knows, or the list's `mediaType` as written for any
  other. `REFERENCES_ANY_OF` joins the words with ", ", and
  `REFERENCES_EXCLUSIVE` with " and ".
- `VOICE_COUNTED` is a sentence of its own, added after the message, with a
  space, only when a voice was counted.
- "set another mode in arguments" is how a person overrides the chosen mode
  ([01-decisions.md](01-decisions.md#how-the-mode-is-chosen)).

Add to `src/config/messages/inputs.py`, raised with `INVALID_INPUT`:

| Constant                  | Text |
| ------------------------- | ---- |
| `PLACEHOLDER_UNCONNECTED` | `The prompt uses {placeholder}, but {input} has {count} connected. Placeholders count from 1 within each input.` |

`{placeholder}` is the text as typed, such as `{{image3}}`. `{input}` is the
input name from `PLACEHOLDERS`.

## Step 4: Placeholder pattern

Add to `src/config/patterns.py`, which 05 creates, in ASCII order and in
`__all__`:

```python
# A placeholder of this pack in a prompt, such as {{image1}}: one of its four words and a number from 1, in double
# braces, not after the backslash the CLI uses for a literal {{.
PLACEHOLDER_PATTERN = r"(?<!\\)\{\{(image|video|audio|reference)([1-9][0-9]*)\}\}"
```

- The text is the one [05-foundation.md](05-foundation.md#step-5-patterns)
  fixes. Its four words are the keys of `PLACEHOLDERS`.
- Only this pack's placeholders match. `{{scene1}}`, `{{image0}}`, and
  `{{image01}}` do not, so they reach the CLI as typed, and the CLI refuses
  them for free ([01-decisions.md](01-decisions.md#placeholders)).
- The CLI's own forms never match: `{{node:node_abc}}` and `{{res:…}}` hold
  a colon after the word.
- `\{{image1}}` never matches. At the first brace, the look-behind finds the
  backslash. At the second, the next character is not a brace.
- [04-architecture.md](04-architecture.md#srcconfig) lists
  `PLACEHOLDER_PATTERN` among the patterns whose text 05 fixes. Its first
  user is this plan, so it arrives here, and 05 does not add it.

## Step 5: Reference records

Create `src/types/references.py`, with the docstring "Dreamina canvas nodes
and resources a run references, and ComfyUI media waiting for its upload."
It holds records only and imports nothing from ComfyUI (import contract 4),
so local media is typed `object`. F's `src/types/files.py` is not ported:
`FalFile`, `EncodedFile`, `FileKind`, `FileOrigin`, `FieldValue`,
`FileItem`, and `ArgumentValue` describe fal links and request fields, which
this pack does not have.

```python
type ReferenceOrigin = Literal["node", "resource"]


@dataclass(frozen=True, slots=True)
class Reference:
    """One Dreamina canvas node or resource a run can use, with no upload.

    Attributes:
        origin: node for a canvas node, which keeps the edge to it; resource for one concrete file.
        value: The node ID (node_…) or the resource ID (a lowercase UUID), as the CLI writes it.
        media: image, video, audio, or element.
        title: The canvas node's title when Dreamina gives one; None otherwise.

    """

    origin: ReferenceOrigin
    value: str
    media: MediaKind
    title: str | None

    @property
    def typed_value(self) -> str:
        """Write the reference as --ref and a prompt placeholder take it: node:<node ID> or res:<resource ID>."""
        return f"{REFERENCE_TYPES[self.origin]}:{self.value}"


@dataclass(frozen=True, slots=True)
class LocalMedia:
    """One connected ComfyUI image frame, video, or audio clip, uploaded when its run starts.

    Attributes:
        media: image, video, or audio.
        value: The ComfyUI value: an IMAGE frame [1, H, W, C], a VIDEO, or an AUDIO clip whose waveform is [1, C, T].
        position: Its place among the connected items of its kind, from 1, which its placeholder names.

    """

    media: Kind
    value: object
    position: int
```

Imports: `Kind` and `MediaKind` from `src/types/__init__.py` (05),
`REFERENCE_TYPES` from `src/config/media.py`. The module ends with
`__all__ = ["LocalMedia", "Reference"]`. `ReferenceOrigin` stays out of
`__all__` and is imported by name, as F does with its aliases.

How a reference is written to the CLI:

| Where                                        | Written as                         | Example                         | Plan |
| -------------------------------------------- | ---------------------------------- | ------------------------------- | ---- |
| `--ref`, one per reference, in order         | `reference.typed_value`            | `--ref node:node_ab12`, `--ref res:3f6c…` | 08 |
| A prompt placeholder                         | `{{` + `typed_value` + `}}`        | `{{res:3f6c…}}`                 | 07 ([Step 8](#step-8-references-and-placeholders)) |
| Element bindings `--main`, `--voice`, `--auxiliary` | `reference.value`, bare     | `--main node_ab12`              | [13-node-element.md](13-node-element.md) |

- Element bindings "keep their existing bare Node ID / Resource ID
  contracts" (`skill: references/identity-and-references.md#public-identity-model`;
  [02-dreamina-contract.md](02-dreamina-contract.md#elements)).
- `typed_value` is a property, so the function policy's decorator exemption
  covers it, as it covers F's `Settings.revision`.
- Every `value` comes from a CLI reply: an upload's echoed `resourceId`, or
  08's and 13's reading of `node show` and `node create element`. The
  resource ID the pack sends is `str(uuid.uuid4())`, which is already the one
  accepted spelling, "canonical lowercase UUID".
- `LocalMedia.position` is unique per kind within one `send_media` call.
  `list_local_media` numbers each kind from 1
  ([Step 6](#step-6-conversions)).

## Step 6: Conversions

Create `src/comfy/media.py`, ported from `F/src/comfy/media.py`, with the
docstring "Check ComfyUI media and convert it with ComfyUI's own helpers, to
files for upload and back from downloaded files." and the second paragraph
"Encoding and decoding block, so callers run these functions in a worker
thread." Each helper call sits in one `except Exception` that raises the
listed message with `ErrorCode.MEDIA`, `from None`, carrying F's
`# noqa: BLE001 -- reason: ComfyUI's helper raises unrelated exception types; one reviewed message replaces them.`
F's two `pyright: ignore` comments stay, on the `audio_bytes_to_audio_input`
import and on the `save_to` call (`F/src/comfy/media.py:33`, `:112`).

### Which ComfyUI helpers to use

Only the conversion helpers, as in F. Only this module imports
`comfy_api_nodes`, so a change in ComfyUI touches one file.

| Helper | From | Used by | Call it with |
| ------ | ---- | ------- | ------------ |
| `tensor_to_bytesio(image, *, total_pixels, mime_type)` | `comfy_api_nodes.util.conversions` (`C/comfy_api_nodes/util/conversions.py:71`) | `_encode_image` | `total_pixels=None`, `mime_type="image/png"`. The default `2048 * 2048` shrinks every larger image to about 4 MP (`conversions.py:96-106`). |
| `audio_tensor_to_contiguous_ndarray(waveform)` | same (`conversions.py:294`) | `_encode_audio` | One clip, `[1, C, T]`; any other shape raises. |
| `audio_ndarray_to_bytesio(audio_data_np, sample_rate, container_format, codec_name)` | same (`conversions.py:263`) | `_encode_audio` | `container_format=WAV["FORMAT"]`, `codec_name=WAV["CODEC"]`. It writes a stereo layout for more than one channel. |
| `bytesio_to_image_tensor(image_bytesio, mode)` | same (`conversions.py:19`) | `decode_images` | `mode="RGB"`, so every image comes back with three channels, whatever PIL mode it had. |
| `audio_bytes_to_audio_input(audio_bytes)` | same (`conversions.py:604`) | `decode_audio` | The downloaded bytes. PyAV reads any common container and returns `{"waveform": [1, C, T], "sample_rate": …}`. |
| `Input.Video.save_to(path, format, codec)` | `comfy_api.latest` (`C/comfy_api/latest/_input_impl/video_types.py:623`) | `_encode_video` | `str(path)` (the parameter is `str \| io.BytesIO`), `format=Types.VideoContainer.MP4`, `codec=Types.VideoCodec.AUTO`. |
| `InputImpl.VideoFromFile(file)` | `comfy_api.latest` (`video_types.py:236`) | `decode_video` | A `BytesIO` over the downloaded bytes. |

`VideoFromFile.save_to` copies the source's streams unchanged when the
source is already an MP4 container, untrimmed and uncropped, and the codec
is `AUTO`. Otherwise it re-encodes (`video_types.py:643-667`). So a video
loaded from an MP4 file is uploaded with its original streams, and any other
video is encoded by ComfyUI's own code. The pack reads no private attribute
to find the original file.

Not used, with F's reasons re-valued:

| Helper | Why it is not used |
| ------ | ------------------ |
| `sync_op`, `sync_op_raw`, `poll_op`, `poll_op_raw` (`util/client.py`) | They call Comfy's proxy with the person's Comfy sign-in and retry. The pack talks to Dreamina only through the CLI ([01-decisions.md](01-decisions.md#why-the-cli)). |
| `upload_image_to_comfyapi`, `upload_images_to_comfyapi`, and every other `upload_*_to_comfyapi` | They send media to Comfy.org storage, shrink images to about 4 MP, and keep only the first 8 images. The CLI uploads to the person's canvas ([Step 7](#step-7-uploads)). |
| `download_url_to_bytesio`, `download_url_to_image_tensor`, `download_url_to_video_output`, `download_url_as_bytesio` | They fetch addresses, retry up to five times, and have no size cap. The CLI downloads outputs ([Step 9](#step-9-downloads)). |
| `tensor_to_data_uri`, `tensor_to_base64_string`, `audio_to_base64_string`, `video_to_base64_string` | The CLI takes a file path, never inline media. |
| `util/validation_utils.py` | Its checks pass silently when a file's metadata cannot be read, and Dreamina checks its own limits for free. |
| `is_api_node=True` on a schema | It adds hidden Comfy sign-in inputs and partner-node styling. |

torchaudio is not used. ComfyUI's helpers encode and decode with PyAV.

### Splitting and encoding

| Function | Does | Message on failure |
| -------- | ---- | ------------------ |
| `list_local_media(images: Sequence[torch.Tensor], videos: Sequence[Input.Video], audio: Sequence[Input.Audio]) -> tuple[LocalMedia, ...]` | Returns one `LocalMedia` per frame of each IMAGE batch, `frame.unsqueeze(0)`, then one per VIDEO, then one per clip of each AUDIO batch, `{"waveform": waveform[index : index + 1], "sample_rate": sample_rate}`. Each kind is numbered from 1, in socket order and then batch order. | none |
| `encode_local_file(media: LocalMedia, folder: Path) -> Path` | Writes the item to `folder / f"{media.media}-{media.position}.{UPLOAD_FORMATS[media.media]['EXTENSION']}"` and returns the path. An image or audio item is encoded to bytes, then written with `path.write_bytes`. A video is written by `save_to` straight to the path. | from the private encoder |
| `_encode_image(image: torch.Tensor) -> bytes` | Checks first (`INVALID_INPUT`): rank 4 with 3 or 4 channels (`IMAGE_CHANNELS`), then finite values (`IMAGE_PIXELS`). Then `tensor_to_bytesio(image.clamp(0, 1), total_pixels=None, mime_type="image/png").getvalue()`. | `IMAGE_CHANNELS` |
| `_encode_audio(audio: Input.Audio) -> bytes` | Checks `waveform.shape[-1] > 0` first (`AUDIO_EMPTY`, `INVALID_INPUT`). Then `audio_ndarray_to_bytesio(audio_tensor_to_contiguous_ndarray(audio["waveform"]), audio["sample_rate"], container_format=WAV["FORMAT"], codec_name=WAV["CODEC"]).getvalue()`. | `AUDIO_UNWRITABLE` |
| `_encode_video(video: Input.Video, path: Path) -> None` | `video.save_to(str(path), format=Types.VideoContainer.MP4, codec=Types.VideoCodec.AUTO)` | `VIDEO_UNWRITABLE` |

What changes from F:

- **`list_local_media` is new.** F's File: Add split batches into one
  `FalFile` per frame or clip. Here the paid nodes, Image: Upscale, and
  Element: Add all take list sockets, so the split lives with the encoders.
  Its count of frames and clips is what `validate_references` counts, before
  anything is encoded.
- **Each encoder takes one item.** F's `_encode_image` and `_encode_audio`
  took a batch and returned a tuple of `EncodedFile` records
  (`F/src/comfy/media.py:52-105`). Here each takes the one frame or clip that
  `list_local_media` made, and returns bytes.
- **`_encode_video` writes to the file.** F wrote into a `BytesIO`
  (`F/src/comfy/media.py:108-115`). The CLI needs a file, and writing straight
  to it keeps a long video out of memory.
- **`encode_local_file` writes a file and returns its path.** F returned an
  `EncodedFile` with the content and its digest
  (`F/src/comfy/media.py:118-127`). `send_media` computes the digest from the
  file ([Step 7](#step-7-uploads)).
- **Not ported:** `_build_encoded`, `_encode_mask`, and `decode_mesh`. There
  is no mask input and no 3D output.
- **A four-channel image stays RGBA in the PNG**, as in F, so a cut-out keeps
  its transparency on the way to Dreamina.
- **Images are never resized.** A ComfyUI image above a model's pixel limit
  (8,192 pixels per side for every listed image model,
  [research/catalog.md](research/catalog.md#file-limits)) is refused by
  Dreamina at save, for free.

`encode_local_file` is the one encoder other modules call.
[08-runs.md](08-runs.md)'s `GenerateNode` hands it to `GenerationOperation`,
because `src/dreamina/` may not import `src/comfy/`
([04-architecture.md](04-architecture.md#import-layers)), as F's
`EndpointNode` handed it to `QueueOperation`.

### Decoding

| Function | Does | Message on failure |
| -------- | ---- | ------------------ |
| `decode_images(contents: Sequence[bytes]) -> tuple[torch.Tensor, ...]` | For each file, `bytesio_to_image_tensor(io.BytesIO(content), mode="RGB")`: one `[1, H, W, 3]` tensor each, in the order given. | `IMAGE_UNREADABLE` |
| `decode_video(content: bytes) -> Input.Video` | `InputImpl.VideoFromFile(io.BytesIO(content))`, then `get_dimensions()` once, so an unreadable file fails here with a message and not later in **Save Video**. | `VIDEO_UNREADABLE` |
| `decode_audio(content: bytes) -> Input.Audio` | `audio_bytes_to_audio_input(content)`. | `AUDIO_UNREADABLE` |

What changes from F:

- **`decode_images` returns the pixels only.** F returned pixels and masks,
  with the mask `1 - alpha` (`F/src/comfy/media.py:130-148`). Dreamina's
  images are opaque generations, and the nodes have no mask output
  ([Decisions this plan makes](#decisions-this-plan-makes)). `mode="RGB"`
  converts any PIL mode, such as palette or grayscale, to three channels; an
  alpha channel is dropped, not blended.
- **`decode_video` and `decode_audio`** are F's, unchanged
  (`F/src/comfy/media.py:151-167`). The video stays in memory: `VideoFromFile`
  reads the `BytesIO`, and **Save Video** copies its streams.

The module ends with
`__all__ = ["decode_audio", "decode_images", "decode_video", "encode_local_file", "list_local_media"]`.

## Step 7: Uploads

Create `src/dreamina/uploads.py`, ported from `F/src/fal/uploads.py`, with
the docstring "Upload a run's local media to the pack's canvas through the
CLI, each distinct file once." and the second paragraph "Nothing is kept
between runs. The encoded files live in a private temporary folder until
their uploads finish."

```python
async def send_media(
    project_id: str,
    items: Sequence[LocalMedia],
    encode: Callable[[LocalMedia, Path], Path],
    settings: Settings,
    deadline: float,
) -> tuple[Reference, ...]:
```

Docstring: "Upload every item to the canvas and return one resource reference
per item, in item order." with the second paragraph "Every item is encoded
and checked against the maximum upload size before the first upload. Items
with the same bytes are uploaded once and share one reference."

`deadline` is the `time.monotonic()` value at which the run's request
timeout ends, as 08's `GenerationOperation` sets it. It bounds the run "from
the first upload to the last download"
([01-decisions.md](01-decisions.md#paid-runs)). Each CLI call gets
`deadline - time.monotonic()` seconds.

What it does, in order:

1. **No items:** returns `()` and makes no folder.
1. **The folder.** `tempfile.TemporaryDirectory(prefix=TEMPORARY_PREFIX,
   ignore_cleanup_errors=True)`, with `TEMPORARY_PREFIX` (`.dreamina-`) from
   `src/config/storage.py` (05). The standard library makes the folder
   readable by its owner only. `ignore_cleanup_errors` keeps a cancel during
   encoding from being replaced by a cleanup error.
1. **Encoding.** One `asyncio.to_thread` call runs a private
   `_encode_files(items, encode, folder)`. For each item in order it calls
   `encode(item, folder)`, then reads the file's size and its SHA-256 with
   `hashlib.file_digest`. It returns the path, size, and digest of each item.
1. **The size check.** The first item whose size is above
   `settings.max_upload_megabytes * BYTES_PER_MEGABYTE` raises `UPLOAD_LIMIT`
   with `INVALID_INPUT`, before anything is uploaded. F's
   `validate_upload_size` (`F/src/fal/operation.py:31-37`) moves here, as a
   private `_validate_upload_size`.
1. **The uploads**, one after another, in item order. An item whose digest
   was already uploaded in this call takes that upload's reference. Each new
   file gets a new `resource_id = str(uuid.uuid4())` and goes through the
   private `_send_upload` below.
1. **The result.** One `Reference(origin="resource", value=resource_id,
   media=item.media, title=None)` per item, in item order. The folder is
   deleted when the `with` block ends, before the run call.

The upload call, through 08's `send_command`:

```text
resource upload --project-id <canvas> --file <path> --type <UPLOAD_FORMATS[kind]["TYPE"]> --resource-id <uuid>
```

- `--project-id` is always passed: "Always pass `--project-id` to
  `resource upload`, even with `--resource-id`"
  (`skill: references/identity-and-references.md#upload-material-identity`).
- `--name` is not passed, so the resource takes the file name, such as
  `image-1.png` (schema: `resource upload`).
- `--import-kind` is not passed. Its default is `local_upload`.

`_send_upload(project_id, path, media_type, resource_id, deadline) -> None`
makes at most `FREE_ATTEMPTS` calls:

- **Success:** exit 0. The payload is read as 08's `UploadReply`. A reply
  that does not validate, or whose `resourceId` differs from `resource_id`,
  raises `UPLOAD_UNREADABLE` with `TRANSPORT`.
- **Sent a second time**, with the same file and the same `--resource-id`,
  only when the first outcome is unknown:
  - `send_command` could not read the CLI's reply and raised `DreaminaError`
    with `ErrorCode.TRANSPORT` (02: an invalid reply is `TRANSPORT` for every
    call but the run call);
  - the failure's `error.retryable` is true;
  - the failure's `error.code` is `UPLOAD_STATE_UNKNOWN`.
- **Not sent again:** every other failure. It has a definite answer, such as
  exit 2 (refused before anything was sent), exit 11 (sign-in), a
  `requiredAction` of `upgrade`, or an `error.validation` refusal. It raises
  `build_failure(result, UPLOAD_REFUSED)` at once. A cancel is never
  repeated: `send_command` kills the process, and the cancel goes on.
- **A second failure** is final: `build_failure(result, UPLOAD_REFUSED)`, or
  `send_command`'s own `TRANSPORT` error.

Details:

- **Uploads run one after another**, as in F. The pack adds no parallel cap
  or fan-out of its own, and the order makes a failure name the first file
  that failed.
- **Nothing is billed by an upload or its failure.** "Uploads, Elements,
  imports, reads" bill nothing
  ([02-dreamina-contract.md](02-dreamina-contract.md#what-is-billed-when-something-fails)).
  A refused or cut-off upload may leave a resource on the canvas, which the
  person can see and delete.
- **Each model's file limits are not checked here.** `model <canonical>`
  gives them ([research/catalog.md](research/catalog.md#file-limits)), and
  the server refuses an oversized file at save, before any charge. On
  2026-10-16:
  - images: 50 MB and up to 8,192 pixels per side for every image model and
    for frames;
  - `seedance_2.0`, `_fast`, and `_mini` `m2v` video: 52,428,800 bytes, 2.0
    to 15.4 seconds, 200 to 2,160 pixels per side;
  - `seedance_2.5` `m2v` video: 209,715,200 bytes, 1.8 to 30.2 seconds, 300
    to 6,000 pixels per side;
  - audio: 15,728,640 bytes for Seedance, and 10 MB and 3 to 30 seconds for
    `seed_audio_v1`.

  The largest is the 209,715,200-byte reference video, so
  `max_upload_megabytes` defaults to 210 with a range of 1 to 210
  ([05-foundation.md](05-foundation.md)). The binary also holds a
  `MaximumUploadBytes` check per media type (strings), so the CLI may refuse
  an oversized file itself, before sending it. Either refusal is free.
- **A deleted canvas.** 08's `find_canvas` checks the saved canvas in
  `canvas ls` before each run. When it is gone, the saved ID is cleared, and
  `create_canvas` makes a new canvas before any upload. A canvas deleted
  during the run fails the upload with the message 08's map gives its error
  (run C-15). The error goes up unchanged, the run stops, and nothing is sent
  again ([01-decisions.md](01-decisions.md#the-canvas)).
- **The encoder is synchronous** and runs through `asyncio.to_thread`, as
  F's `QueueOperation._build_body` ran it
  (`F/src/fal/queue/operation.py:306-310`).

What changes from F:

- **`UploadStore` is not ported.** It kept a fal storage token behind a
  `threading.Lock` (`F/src/fal/uploads.py:27-51`). There is no token: the CLI
  signs every call. So there is no class and nothing is added to `Runtime`.
- **The per-request map stays**, as a local `dict[str, Reference]` keyed on
  the full SHA-256, like `links` in F's `send_files`
  (`F/src/fal/uploads.py:73-86`).
- **One second try with the same resource ID is new.** F sent each upload
  once, and the next run uploaded again. Here the resource ID makes the
  second try safe, and 01 asks for it.

The module ends with `__all__ = ["send_media"]`.

## Step 8: References and placeholders

Create `src/dreamina/references.py`, new, with the docstring "Check a run's
references against its mode, order them for --ref, and write its
placeholders in the CLI's form." It compiles `PLACEHOLDER_PATTERN` once, as
a private module constant.

### `validate_references`

```python
def validate_references(
    mode: ModelMode,
    items: Sequence[Reference | LocalMedia],
    arguments: Mapping[str, Json],
) -> None:
```

Docstring: "Refuse references the chosen mode entry would refuse, before
anything is uploaded."

- `mode` is the entry 06's `choose_mode` picked. One mode can appear twice in
  a model's list with different limits: every video model lists
  `first_last_frame` once with exactly two images and once with exactly one
  ([research/catalog.md](research/catalog.md#what-the-lists-show), item 5).
  This function checks only the entry it is given.
- For video, 06's rule is
  [01-decisions.md](01-decisions.md#how-the-mode-is-chosen)'s. One or two
  images and nothing else give `first_last_frame`, and the count chooses its
  one-image or two-image entry. Anything else gives `m2v`. `"mode": "m2v"` in
  `arguments` sends one or two images as references instead. Every video
  mode requires `ratio`, so a ratio never changes the mode.
- `items` is every reference and every connected local item, before upload:
  `(*references, *local)`. Both records carry `media`.
- `arguments` is the parsed `arguments` mapping from 06's `parse_arguments`.

How items are counted:

1. Each item counts once, under `MEDIA_TYPES[item.media]`. So an Element
   counts as `image`.
1. In a mode named `VOICE_REFERENCE["MODE"]` (`tts`), a
   `VOICE_REFERENCE["FLAG"]` key (`voice-name`) in `arguments` adds one
   `audio`. 06 has already refused the key for an entry that lists no such
   flag: `validate_argument_names` for a model with none, and `build_flags`
   for an entry without it, such as `seed_audio_v1` omni dubbing.
1. The total is the sum of every count.

The checks, in this order. The first that fails raises its message with
`INVALID_INPUT`, followed by `VOICE_COUNTED` when a voice was counted:

| # | Check | Message |
| - | ----- | ------- |
| 1 | The mode is in `FRAME_MODES` and an item's `media` is `element` | `REFERENCES_ELEMENT_FRAME` |
| 2 | The entry has no `references`, or its `max` is 0, and the total is above 0 | `REFERENCES_NONE` with `count` |
| 3 | The total is below `references.min` or above `references.max` | `REFERENCES_TOTAL` with `minimum`, `maximum`, `count` |
| 4 | A counted `mediaType` is not the `mediaType` of any `types[]` entry (an empty `types` enables none) | `REFERENCE_KIND_REFUSED` with `media`, `count` |
| 5 | A `types[]` entry's count is below its `min` or above its `max` (a type nothing fills counts 0) | `REFERENCE_KIND_COUNT` with `media`, `minimum`, `maximum`, `count` |
| 6 | `requireAnyOfTypes` is present and none of its types has a count | `REFERENCES_ANY_OF` with `media` |
| 7 | `mutuallyExclusiveTypes` is present and two or more of its types have a count | `REFERENCES_EXCLUSIVE` with the counted ones as `media` |

The fields come from 06's `ModelReferences` and `ReferenceLimit`, which read
`min`, `max`, `types[].mediaType`, `types[].min`, `types[].max`,
`requireAnyOfTypes`, and `mutuallyExclusiveTypes`. "An omitted `references`
means the upstream specification supplied no materials; `types: []` means
the specification explicitly enabled no material type"
(`skill: SKILL.md#model-and-voice-discovery`). Both enable nothing here, with
different messages. Private helpers keep each function within Ruff's
complexity of 8 and four returns: one builds the counts, one runs checks 1
and 2, and one runs checks 3 to 7.

How the CLI's mode rules are kept:

| CLI rule ([research/cli.md](research/cli.md#generation-nodes)) | Where it is enforced |
| ------------------------------------------------------------ | -------------------- |
| `t2v` takes no reference | Every video model lists `t2v` with `{"min": 0, "max": 0, "types": []}`: check 2. |
| `t2i` takes only Text references, which the pack never sends | Most image models list `t2i` with no references: check 2. `seedream_4.6` and `seedream_4.7` list `t2i` with 0 to 14 images, so a person who sets `"mode": "t2i"` may connect images there ([research/catalog.md](research/catalog.md#image-models)). The live list is followed, not a fixed rule. |
| `i2i` needs at least one image, Element, or image resource | Every image model lists `i2i` with images 1 and up, and an Element counts as an image: checks 3 and 5. |
| `first_last_frame` takes one or two images, first then last, and no Element | The two list entries fix one or two images: checks 3 to 5. The Element rule is check 1, the one fixed rule, because the list's image limits would count an Element as a frame. |
| Text reading takes no references | `seed_audio_v1` lists text reading with 0 to 1 audio and requires `voice-name`. The voice fills that slot, so any connected item makes check 3 fail. |
| A voice counts as an audio reference | The counting rule above. With `seed_audio_v1` omni dubbing, an image and a voice fail check 7, as the skill says: "When image and audio are mutually exclusive, an image and a voice cannot be combined." |

What is left to Dreamina: whether two frame images share their aspect ratio,
each file's limits, and whether a reference's node or resource exists and is
ready. The server refuses those at save, before the quote, for free.

### `plan_references`

```python
def plan_references(
    references: Sequence[Reference],
    local: Sequence[LocalMedia],
    uploaded: Sequence[Reference],
) -> tuple[tuple[Reference, ...], dict[str, Reference]]:
```

Docstring: "Put every reference in --ref order, and name each one for its
placeholder."

- `uploaded` is `send_media`'s result for `local`, so the two pair by index.
- **The order.** `references` in socket order, then the uploaded items sorted
  by their kind's place in `PLACEHOLDERS` (image, video, audio) and then by
  `position`. The sort makes the order hold whatever order the caller listed
  the local items in.
- **The names.** `reference1`, `reference2`, … for `references`, and
  `f"{item.media}{item.position}"` for each uploaded item, such as `image1`.
- Two items with the same bytes share one resource, and each keeps its own
  place in `--ref`. A first and last frame made from one image are sent as
  two references, as connected.

### `format_prompt`

```python
def format_prompt(prompt: str, placed: Mapping[str, Reference]) -> str:
```

Docstring: "Write each placeholder of this pack in the CLI's form, and leave
every other part of the prompt as typed."

For each match of `PLACEHOLDER_PATTERN`, a private
`_format_placeholder(match, placed)` decides:

1. The key is the word and the number as typed, such as `image1`. The
   pattern takes no leading zero, so each item has one key.
1. A key in `placed` becomes `"{{" + reference.typed_value + "}}"`, such as
   `{{res:3f6c…}}`.
1. A key not in `placed`, such as `{{image3}}` with two images:
   `PLACEHOLDER_UNCONNECTED`, with the placeholder as typed, the input from
   `PLACEHOLDERS[word]`, and the count of keys placed for that word.

Text the pattern does not match, such as `{{scene1}}` or `{{image0}}`,
reaches the CLI unchanged, and the CLI refuses it for free
([01-decisions.md](01-decisions.md#placeholders)).

Details:

- **The reference stays in `--ref`.** "If the same node appears in both a
  prompt placeholder and `--ref`, it is merged into one reference slot"
  (`skill: references/identity-and-references.md#prompt-references`).
- **The escape.** `\{{` is never matched, and the pack never adds or removes
  it ([02-dreamina-contract.md](02-dreamina-contract.md#how-the-pack-calls-the-cli)).
- **Which prompt.** 08 calls `format_prompt` on the text it sends as
  `--prompt`, whether it came from the `prompt` box or from `prompt` in
  `arguments`. An empty prompt sends nothing, and `format_prompt` is not
  called.
- **`{{res:<uuid>}}` for an upload** is unconfirmed until run C-6
  ([Live checks](#live-checks)).

The module ends with
`__all__ = ["format_prompt", "plan_references", "validate_references"]`.

## Step 9: Downloads

`OutputFile` lives in `src/types/generations.py`, which
[08-runs.md](08-runs.md#step-9-generation-records) creates in its Step 9,
before this step by the interleaved order. This step builds the record as
`OutputFile(resource_id, kind, content)`: the resource ID, its `Kind`, and
its downloaded bytes.

Create `src/dreamina/downloads.py`, ported in role from
`F/src/fal/outputs.py`, with the docstring "Download a finished node's
outputs through the CLI, checking each file's size and SHA-256 before
reading it."

```python
async def download_resources(
    project_id: str,
    node: NodeView,
    submit_id: str,
    settings: Settings,
    deadline: float,
) -> tuple[OutputFile, ...]:
```

Docstring: "Download the finished resources of one submit ID, in the node's
order, and return their bytes." `node` is the `node` of 08's `node show`
reply, read as `NodeView`. `deadline` is as in [Step 7](#step-7-uploads).

What it does, in order:

1. **Which resources.** The items of `node.resources[]` whose `submitId`
   equals `submit_id` and whose `status` equals `RESOURCE_SUCCESS`, in the
   node's order ([02-dreamina-contract.md](02-dreamina-contract.md#reading-a-finished-node)).
   None: `OUTPUTS_MISSING`.
1. **Their kinds.** Each resource's `type` is looked up in `RESOURCE_KINDS`
   before the first download. A type not listed raises `RESOURCE_TYPE` with
   the type as written.
1. **The folder.** One `tempfile.TemporaryDirectory(prefix=TEMPORARY_PREFIX,
   ignore_cleanup_errors=True)` for the call, deleted when it returns.
1. **Each download**, one after another, through the private
   `_download_file` below, to `folder / resource_id`. The file is read into
   memory and deleted at once, so at most one output file is on disk at a
   time.
1. **The result.** One `OutputFile(resource_id, kind, content)` per resource,
   in the node's order.

The download call, through 08's `send_command`:

```text
resource download <resource-id> --project-id <canvas> --output <folder>/<resource-id>
```

The CLI uses `--output` "verbatim; no transcoding" (schema:
`resource download`). The path is new, so the CLI never overwrites a file.

`_download_file(project_id, resource_id, path, settings, deadline) -> bytes`
makes at most `FREE_ATTEMPTS` calls. For each:

1. **The reply** is read as 08's `DownloadReply` (`resourceId`, `path`,
   `size`, `sha256`).
1. **`size` is 0:** `DOWNLOAD_EMPTY`, final.
1. **`size` is above `settings.max_download_megabytes *
   BYTES_PER_MEGABYTE`:** `DOWNLOAD_LIMIT` with the size in MB, rounded up to
   0.1, final. The file is never read into memory.
1. **The file.** In `asyncio.to_thread`, the private `_read_download(path,
   size, sha256) -> bytes | None` reads at most `size + 1` bytes from the
   pack's own path, never from the reply's `path`. It returns the bytes when
   their length equals `size` and their SHA-256, in lowercase hexadecimal,
   equals `sha256` lowercased. Otherwise, or when the file is missing, it
   returns `None`. The file is deleted either way.
1. **Sent a second time** only when the outcome is unknown: `send_command`
   raised `TRANSPORT`, the failure's `error.retryable` is true, the reply did
   not validate, its `resourceId` differs, or `_read_download` returned
   `None`.
1. **Final failures:** a CLI failure with a definite answer raises
   `build_failure(result, DOWNLOAD_FAILED)`. A second unknown outcome raises
   `DOWNLOAD_MISMATCH`, or `send_command`'s own `TRANSPORT` error.

Details:

- **Every failure here keeps the generation record.** 08 deletes it only after
  `download_resources` returns, so Generation: Download can try again.
- **Why both length and SHA-256.** The skill asks to "inspect the byte count
  returned by the CLI" and "record the SHA256 returned by the CLI"
  (`skill: references/completion-and-validation.md#download-checks`). The
  pack compares the file it reads with both, so a cut-off or replaced file
  is never decoded.
- **Video and audio downloads** are unconfirmed. The schema's summary reads
  "Safely download a successful image resource"
  ([02-dreamina-contract.md](02-dreamina-contract.md#downloads)). Runs C-3
  and C-4 settle them before this plan is built
  ([Live checks](#live-checks)).
- **The CLI may refuse a large file itself.** The binary holds
  `cli.download_too_large` (strings). 08's map gives it `DOWNLOAD_FAILED`
  with the CLI's reason.
- **No address is ever fetched.** The pack opens no network connection. The
  CLI downloads.

What changes from F: `list_output_files`, `choose_output_text`, and
`decode_inline_file` (`F/src/fal/outputs.py:75-118`) are not ported. A fal
result held files at any depth, as links or inline. A Dreamina node lists its
resources by ID and type, and the whole node goes into `result` (08).

The module ends with `__all__ = ["download_resources"]`.

## Step 10: Temporary allowlist entries

No module names this plan's public functions until 08 Part B. The function
policy (`python.module-only-public`) refuses a public function that no other
module names, so each module gets an exact entry in
`quality/config/repository/functions.json`, in the step that creates it, as
F did (`F/plans/README.md:237`). Add to `python.allowlist`:

```json
{
    "path": "src/comfy/media.py",
    "names": ["decode_audio", "decode_images", "decode_video", "encode_local_file", "list_local_media"],
    "reason": "The paid nodes list, encode, and decode their media with these from the Media and runs milestone."
},
{
    "path": "src/dreamina/uploads.py",
    "names": ["send_media"],
    "reason": "The generation operation uploads local media with it from the Media and runs milestone."
},
{
    "path": "src/dreamina/references.py",
    "names": ["format_prompt", "plan_references", "validate_references"],
    "reason": "The generation operation checks, orders, and places references with these from the Media and runs milestone."
},
{
    "path": "src/dreamina/downloads.py",
    "names": ["download_resources"],
    "reason": "The generation operation downloads a finished node's outputs with it from the Media and runs milestone."
}
```

- `Reference.typed_value` needs no entry: it is a property.
- 08 Part B removes each name in the step that adds its first caller:
  `GenerateNode` (`list_local_media`, `encode_local_file`),
  `build_node_outputs` (`decode_images`, `decode_video`, `decode_audio`), and
  `GenerationOperation` (`send_media`, `validate_references`,
  `plan_references`, `format_prompt`, `download_resources`). An entry goes
  when its list is empty.
- The expected state: after this plan's steps, the four entries exist and
  nothing calls these functions. The commit comes after 08 Part B, so it
  holds none of the four entries. The Git hooks run only at the commit.

## What other plans do with these

| Plan | Uses |
| ---- | ---- |
| [06-model-check.md](06-model-check.md) | `choose_mode` picks the mode entry, including which `first_last_frame` entry, from what is connected. It counts items the same way, an Element as an image. `validate_references` then checks every count against that entry. `build_flags` refuses a `voice-name` the chosen entry does not list, before it can be counted as a voice. `describe_mode` writes `{mode}` in this plan's messages. |
| [08-runs.md](08-runs.md) | `GenerateNode` calls `list_local_media(images, videos, audio)` and passes `encode_local_file` to `GenerationOperation`. `GenerationOperation.send` calls `validate_references(mode, (*references, *local), values)` after 06's `choose_mode`, `choose_prompt`, and `build_flags`, and before `find_canvas`; `send_media` after the canvas; `plan_references`; `format_prompt` on the text 06's `choose_prompt` returned, sent as `--prompt`; one `("--ref", reference.typed_value)` pair per ordered reference; and `download_resources` after `node show`. `CollectOperation` calls `download_resources` too. |
| [08-runs.md](08-runs.md), `build_node_outputs` | Runs through `wait_for_thread`, as F's does (`F/src/comfy/execution.py:35-41`). It passes the contents of the `OutputFile`s of kind `image`, in order, to `decode_images` for `images`, each of kind `video` to `decode_video` for `video`, and each of kind `audio` to `decode_audio` for `audio`. It decodes only the outputs the node shows, as F's does (`F/src/nodes/outputs.py:24-43`). It builds `references` from `Reference`: `Reference(origin="node", value=<node ID>, media=<kind>, title=<node title>)` for one output, and one `Reference(origin="resource", …)` per resource for several ([01-decisions.md](01-decisions.md#outputs)). An empty list becomes `ExecutionBlocker(None)`. |
| [09-node-image.md](09-node-image.md) to [11-node-audio.md](11-node-audio.md) | Declare their outputs. Their help pages describe the placeholders, the `--ref` order, and three-channel images. 11's page says a `voice-name` counts as one audio reference. |
| [12-node-upscale.md](12-node-upscale.md) | `list_local_media(images, (), ())` and `send_media` for local images before each import. Uses each image reference's `value` for `--node-id`, and decides what to do with a resource reference. |
| [13-node-element.md](13-node-element.md) | `list_local_media` and `send_media` for the main image, the other angles, and the voice. Writes `reference.value`, bare, to `--main`, `--auxiliary`, and `--voice`. Its output is one `Reference(origin="node", value=<Element node ID>, media="element", title=<title>)`. |
| [14-node-download.md](14-node-download.md) | Through `CollectOperation` and `build_node_outputs`. |
| [15-node-model-info.md](15-node-model-info.md) | Shows each mode's `references` with the list's `mediaType` words, and the file limits from `model <canonical>`. It uses nothing from this plan. |

## Live checks

These runs are in Part 1 of [21-test-runs.md](21-test-runs.md#part-1-contract-checks),
made with the CLI outside ComfyUI in milestone 4, before this plan is built.
Before Step 1, read each result in
[02-dreamina-contract.md](02-dreamina-contract.md#results-of-the-contract-runs)
and in the README's changes table, and apply the change named here. Each
change to this plan is recorded in that table.

| Run | What it settles here | If it differs |
| --- | -------------------- | ------------- |
| C-2 | A PNG written by `_encode_image` uploads with `--type image`. The reply echoes `resourceId` and gives `mediaType`. The largest image Dreamina takes, and whether the CLI refuses a large file itself. | A refused PNG: record the error fields, and set `UPLOAD_FORMATS["image"]` to a format the run shows accepted. An upload cap below 200 MB for images is recorded; it changes nothing here, since the server's refusal is free. |
| C-3 | An MP4 written by `_encode_video` uploads with `--type video`, and `resource download` returns a video resource with `size` and `sha256`. | A refused video download: stop the Video milestone ([10-node-video.md](10-node-video.md) and [14-node-download.md](14-node-download.md)), and record it in 02 and the README. No download through another address. |
| C-4 | A WAV written by `_encode_audio` uploads with `--type audio`. An MP3 does too. `resource download` returns an audio resource. | WAV refused and MP3 accepted: `_encode_audio` returns `audio_input_to_mp3(audio).getvalue()` (`C/comfy_api_nodes/util/conversions.py:318`), `UPLOAD_FORMATS["audio"]` becomes `{"EXTENSION": "mp3", "TYPE": "audio"}`, `WAV` is deleted, and `AUDIO_UNWRITABLE` says MP3 ([01-decisions.md](01-decisions.md#media-formats)). A refused audio download: stop the Audio milestone ([11-node-audio.md](11-node-audio.md)) and record it. |
| C-6 | A prompt with `{{res:<uuid>}}` of an upload saves with a `promptParts[]` part whose `referenceIndex` points at that resource in `generation.references[]`. | Not bound: `format_prompt` refuses `{{imageN}}`, `{{videoN}}`, `{{audioN}}`, and a `{{referenceN}}` whose reference has origin `resource`, with a new `PLACEHOLDER_RESOURCE` in `src/config/messages/inputs.py`: `{placeholder} names an uploaded file, and Dreamina binds only canvas nodes to a place in the prompt. Remove it. The item still goes to the model as a reference.` 01's placeholder section and 09 to 11's help pages are corrected. |
| C-8 | `node show` after an image run: each resource's `type` and `status` spelling, and `submitId` on each. The image download reply's fields. | `RESOURCE_KINDS` and `RESOURCE_SUCCESS` take the spellings the run records. Other reply field names change 08's `NodeView` or `DownloadReply`, not this plan. |
| C-11 | What `seed_audio_v1` text reading's one audio reference is for ([research/catalog.md](research/catalog.md#audio-models)). | If a connected audio clip works together with the required `voice-name`, the voice does not fill that slot: `VOICE_REFERENCE` takes a `SCENARIOS` entry, `("omni-dubbing",)`, and the counting rule applies only there. |
| C-15 | How an Element reference counts against a mode's `references`, from an `m2v` quote that references an Element. | If an Element does not count as `image`, `MEDIA_TYPES["element"]` takes the type the run shows, or the Element is left out of the counts when it counts as nothing. `FRAME_MODES` stays. |

The node first runs in Part 2 exercise these functions through ComfyUI:
`i2i` with an uploaded image (C-10, [09-node-image.md](09-node-image.md))
and an Element from an upload ([13-node-element.md](13-node-element.md)).

## Names this plan uses from other plans

| Name | Owner | Used for |
| ---- | ----- | -------- |
| `Settings` (`max_upload_megabytes`, `max_download_megabytes`) | [05-foundation.md](05-foundation.md) | The upload and download size limits |
| `DreaminaError`, `ErrorCode` | [05-foundation.md](05-foundation.md) | Every refusal |
| `Json`, `Kind`, `MediaKind` (`src/types/__init__.py`) | [05-foundation.md](05-foundation.md) | Record fields and `arguments` |
| `TEMPORARY_PREFIX` (`src/config/storage.py`) | [05-foundation.md](05-foundation.md) | The temporary folders' `.dreamina-` prefix |
| `BYTES_PER_MEGABYTE` (`src/config/units.py`) | [05-foundation.md](05-foundation.md) fixes it; Step 1 adds it | Sizes in decimal megabytes |
| `src/config/patterns.py`, the text of `PLACEHOLDER_PATTERN` | [05-foundation.md](05-foundation.md) | The module and the pattern Step 4 adds |
| `ModelMode` (`name`, `scenario`, `references`), `ModelReferences`, `ReferenceLimit` | [06-model-check.md](06-model-check.md) | `validate_references` |
| `choose_mode`, `parse_arguments`, `describe_mode` | [06-model-check.md](06-model-check.md) | The mode entry, the `arguments` mapping `validate_references` takes, and `{mode}` in the messages |
| `src/config/media.py` with `MEDIA_TYPES` | [06-model-check.md](06-model-check.md) | The module Step 1 adds to |
| `src/config/messages/models.py`, `src/config/messages/inputs.py` | [06-model-check.md](06-model-check.md) | The modules Step 3 adds to |
| `send_command`, `CliResult` (exit code and reply), `CliFailure` (`code`, `retryable`) | [08-runs.md](08-runs.md) Part A | Every CLI call and the second-try decision |
| `build_failure(result, context)` | [08-runs.md](08-runs.md) Part A | Upload and download failures, with `UPLOAD_REFUSED` or `DOWNLOAD_FAILED` as the context |
| `UploadReply`, `DownloadReply`, `NodeView` | [08-runs.md](08-runs.md) Part B, Step 8, built before Step 6 | Reading the CLI's replies |
| `OutputFile` (`resource_id`, `kind`, `content`) | [08-runs.md](08-runs.md) Part B, Step 9, built before Step 6 | `download_resources`' result |
| `GenerationOperation`, `CollectOperation`, `GenerateNode`, `build_node_outputs`, `wait_for_thread`, `find_canvas`, `create_canvas` | [08-runs.md](08-runs.md) Part B | The callers, the deadline they pass, and the canvas every call names |
| `OPERATION_STATES` | [08-runs.md](08-runs.md) | Named only to tell it apart from `RESOURCE_SUCCESS` |
| `UpscaleOperation` | [12-node-upscale.md](12-node-upscale.md) | A caller of `list_local_media` and `send_media` |
| `create_element` | [13-node-element.md](13-node-element.md) | A caller that writes bare `value`s |
