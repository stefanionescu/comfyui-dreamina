"""The group notes and subgraph descriptions of the shipped workflows, in plain language."""

SIGN_IN_STEP = "1. Sign in to Dreamina in **ComfyUI menu → Extensions → Dreamina → Dreamina Settings**.\n"
CANCEL_NOTE = "A cancel does not stop a video Dreamina has accepted. It keeps running and is billed."
RECOVER_NOTE = CANCEL_NOTE + " Collect it with **Generation: Download** in **video-04-recover-a-video**."
UPSCALE_RECOVER_NOTE = (
    "A cancel does not stop an upscale Dreamina has accepted. It keeps running and is billed. Collect it with "
    "**Generation: Download**."
)

WORKFLOW_TEXTS = {
    "image-01-design-a-host": {
        "input": SIGN_IN_STEP
        + "2. Describe your host in **Host**: how they look, what they wear, and the background.\n"
        "3. Press **Run**. The image is saved under `image/dreamina`.",
        "design": "Seedream 5.0 Lite, the image node's starting model, draws the host from the waist up. `arguments` "
        "holds the model's own settings, written by the names Dreamina gives them: `ratio` `3:4` and `resolution` "
        "`2K`, its smallest size. To draw with another model, open **Design** and type another `model`, the model's "
        "name on Dreamina.\n\n`credit_ceiling` is the most credits one run may cost. A run that would cost more "
        "stops before anything is billed.",
        "design_description": "Draws the host and saves the image.",
    },
    "image-02-edit-a-product-photo": {
        "input": SIGN_IN_STEP + "2. In **Photo**, upload a photo of one product, such as a bottle or a shoe.\n"
        "3. In **Change**, say where to put it. `{{image1}}` stands for your photo.\n"
        "4. Press **Run**. The edited photo is saved under `image/dreamina`.",
        "edit": "The pack uploads your photo to your Dreamina canvas, the project named ComfyUI that holds every run, "
        "so the model can read it. Seedream 5.0 Lite then redraws it as **Change** asks, at `1:1` and `2K`, its "
        "smallest size. `{{image1}}` in the prompt marks where your photo goes.\n\nTo combine several products, give "
        "**Edit** a list of up to 6 photos, and name them `{{image1}}`, `{{image2}}`, and so on.",
        "edit_description": "Edits the product photo and saves it.",
    },
    "image-03-upscale-a-poster": {
        "input": SIGN_IN_STEP + "2. Describe the poster in **Brief**. Put any words it must show in quotation marks.\n"
        "3. Press **Run**. The poster and its upscaled version are saved under `image/dreamina`.",
        "poster": "Seedream 5.0 Lite draws the poster at `2K`, its smallest size, in a `3:4` frame. `references`, what "
        "an earlier Dreamina step made, passes the poster on to **Enlarge** with no download or upload.",
        "poster_description": "Draws the poster and saves it.",
        "enlarge": "**Image: Upscale** redraws the poster at `2K` in its `pro` mode, which adds fine detail. For a "
        "larger print, set `resolution` in `arguments` to `4K` or `8K`. `detail`, from 1 to 100, sets how much detail "
        "it adds. For a plain enlargement to twice the size, set `mode` to `normal` and leave out `resolution`.\n\n"
        + UPSCALE_RECOVER_NOTE,
        "enlarge_description": "Upscales the poster and saves it.",
    },
    "image-04-redraw-a-saved-host": {
        "input": SIGN_IN_STEP + "2. In **Host**, upload `example_workflows/assets/dreamina/host.webp` from this "
        "pack's folder: the host **image-01-design-a-host** made. Or upload a picture of your own host.\n"
        "3. In **Pose**, say how to redraw them. `{{image1}}` stands for the picture.\n"
        "4. Press **Run**. The new picture is saved under `image/dreamina`.",
        "redraw": "Seedream 5.0 Lite redraws the host from **Host** full body, at `9:16` and `2K`, its smallest "
        "size. A model given a picture keeps the person in it, and **Pose** says what to keep and what to change.\n\n"
        "This workflow made `example_workflows/assets/dreamina/host-full-body.webp`, which "
        "**image-05-place-a-host-in-a-scene** and **video-06-cast-a-saved-host** start from.",
        "redraw_description": "Redraws the host full body and saves the picture.",
    },
    "image-05-place-a-host-in-a-scene": {
        "input": SIGN_IN_STEP + "2. Upload three pictures from `example_workflows/assets/` in this pack's folder: "
        "`dreamina/host-full-body.webp` in **Host**, `live-shopping/kitchen-counter.webp` in **Place**, and "
        "`live-shopping/burger.webp` in **Product**.\n"
        "3. In **Change**, say what happens. `{{image1}}`, `{{image2}}`, and `{{image3}}` stand for the pictures in "
        "the order **Pictures** lists them.\n"
        "4. Press **Run**. The picture is saved under `image/dreamina`.",
        "combine": "**Pictures**, ComfyUI's **Create List**, joins the three pictures in order, and **Combine** "
        "uploads them. Seedream 5.0 Lite puts the host in the kitchen with the burger, at `9:16` and `2K`. It "
        "takes up to 6 pictures.\n\nThis workflow made `example_workflows/assets/dreamina/host-in-kitchen.webp`, "
        "which **video-05-animate-a-saved-image** starts from.",
        "combine_description": "Puts the host in the place with the product and saves the picture.",
    },
    "audio-01-voice-a-script": {
        "input": SIGN_IN_STEP
        + "2. In **Script**, write what the host says.\n3. Press **Run**. The voice is saved under `audio/dreamina`.",
        "voices": "**Model: Info** shows what a Dreamina model takes: its modes, its settings with their choices and "
        "limits, and a speech model's voices. It is free. **Info** shows Seed Audio, the audio node's starting model, "
        "with its 13 voices.\n\nTo change the voice, copy a name from **Info**, open **Voice**, and put it in "
        "`arguments` as `voice-name`.",
        "voice": "Seed Audio reads **Script** aloud in the voice that `voice-name` names: here `Good Guy`. `arguments` "
        "holds the model's own settings, written by the names Dreamina gives them. With nothing connected, the node "
        "uses text reading, Seed Audio's way to read a script in a chosen voice.\n\nConnect a picture instead, and "
        "Seed Audio makes a voice that suits it, as **audio-02-give-a-host-a-voice** does.",
        "voice_description": "Reads the script aloud and saves the voice.",
    },
    "audio-02-give-a-host-a-voice": {
        "input": SIGN_IN_STEP + "2. Describe the host in **Host**.\n3. In **Line**, write what the host says.\n"
        "4. Press **Run**. The voice is saved under `audio/dreamina`.",
        "cast": "Seedream 5.0 Lite draws the host from the waist up. `references`, what an earlier Dreamina step made, "
        "passes the portrait on to **Speak** with no download or upload.",
        "cast_description": "Draws the host.",
        "speak": "Seed Audio looks at the portrait and speaks **Line** in a voice that suits the host. A picture in "
        "`references` makes the node use omni dubbing, Seed Audio's way to voice a picture. Omni dubbing takes no "
        "`voice-name`, so `arguments` is empty (`{}`).\n\nTo choose the voice yourself, leave the portrait out and set "
        "`voice-name`, as **audio-01-voice-a-script** does.",
        "speak_description": "Speaks the line in a voice that suits the host and saves it.",
    },
    "video-01-animate-a-host": {
        "input": SIGN_IN_STEP + "2. Describe your host in **Host**, and what they do in **Scene**.\n"
        "3. Press **Run**. The video is saved under `video/dreamina`.",
        "portrait": "Seedream 5.0 Lite draws the host in a `9:16` frame. This picture becomes the video's first frame. "
        "`references`, what an earlier Dreamina step made, passes it on to **Animate** with no download or upload.",
        "portrait_description": "Draws the host.",
        "animate": "Seedance 2.0 Mini, the video node's starting model, starts on the host and makes a four-second "
        "`720p` video. With one picture connected, the node uses `first_last_frame`, the mode that starts the video on "
        "that picture. A second picture would set the last frame. Raise `duration` in `arguments` for up to 15 "
        "seconds.\n\n" + RECOVER_NOTE,
        "animate_description": "Turns the host into a video and saves it.",
    },
    "video-02-film-a-product-ad": {
        "input": SIGN_IN_STEP + "2. Describe the host in **Host** and the product in **Product**.\n"
        "3. In **Scene**, say what happens. `{{reference1}}` stands for the host and `{{image1}}` for the product.\n"
        "4. Press **Run**. The video is saved under `video/dreamina`.",
        "cast": "Seedream 5.0 Lite draws the host from the waist up. `references`, what an earlier Dreamina step made, "
        "passes the portrait on to **Film** with no download or upload.",
        "packshot": "Seedream 5.0 Lite draws the product on a plain background. **Film** takes it from `images`, and "
        "the pack uploads it to your Dreamina canvas again, because `references` takes one connection.",
        "packshot_description": "Draws the product.",
        "film": "Seedance 2.5 films the host holding the product, four seconds at `480p`, its smallest size, in a "
        "`9:16` frame. `model`, the model's name on Dreamina, is `seedance_2.5`. Two pictures alone would become the "
        "first and last frames, so `arguments` sets `mode` to `m2v`, the mode that uses them as references. **Scene** "
        "names them `{{reference1}}` and `{{image1}}`.\n\n" + RECOVER_NOTE,
        "film_description": "Films the host with the product and saves the video.",
    },
    "video-04-recover-a-video": {
        "collect": "Use this after you cancel a video Dreamina has already accepted, after a run times out, or after "
        "ComfyUI restarts while a video is being made. Dreamina keeps making it and bills it, and the pack keeps a "
        "record of it.\n\n" + SIGN_IN_STEP + "2. In **Collect**, choose the video in `generation`. Each entry shows "
        "the start of its ID, its model, and when it started, in UTC. Press R to list videos started after the page "
        "loaded.\n3. Press **Run**. The video is saved under `video/dreamina`.\n\nA video leaves the list once it is "
        "saved. If Dreamina no longer has its record, the node says so, and you can look for the video on your "
        "Dreamina canvas.",
        "shot": "Seedance 2.0 Mini makes a four-second `720p` clip from the prompt inside **Shot**. **Shot** ships "
        "turned off, so a run here makes nothing new and bills nothing. To make a video to recover, select **Shot**, "
        "press Ctrl+B to turn it on, press **Run**, and cancel once **Shot** has started. Then turn it off again, "
        "choose the video in **Collect**, and run.\n\n" + CANCEL_NOTE + " **Collect** downloads it.",
        "shot_description": "Makes a four-second clip and saves it.",
    },
    "video-05-animate-a-saved-image": {
        "input": SIGN_IN_STEP + "2. In **Frame**, upload `example_workflows/assets/dreamina/host-in-kitchen.webp` "
        "from this pack's folder, or any picture.\n3. In **Scene**, say what happens.\n"
        "4. Press **Run**. The video is saved under `video/dreamina`.",
        "move": "Seedance 2.0 Mini starts on **Frame** and makes a four-second `720p` video in a `9:16` frame. With "
        "one picture connected, the node uses `first_last_frame`, the mode that starts the video on that picture.\n\n"
        + RECOVER_NOTE,
        "move_description": "Turns the picture into a video and saves it.",
    },
    "video-06-cast-a-saved-host": {
        "input": SIGN_IN_STEP + "2. Upload three pictures from `example_workflows/assets/` in this pack's folder: "
        "`dreamina/host.webp` in **Host**, `dreamina/host-full-body.webp` in **Full Body**, and "
        "`live-shopping/kitchen-counter.webp` in **Place**.\n"
        "3. In **Scene**, say what happens. `{{reference1}}` stands for the host and `{{image1}}` for the place.\n"
        "4. Press **Run**. The video is saved under `video/dreamina`.",
        "keep": "**Element: Add** uploads both host pictures and saves them as an Element named **Host**, with "
        "**Host** as its main picture and **Full Body** as another angle. Making an Element is free.",
        "take": "Seedance 2.0 Mini films **Scene** with the host from **Keep** in the place from **Place**, four "
        "seconds at `720p` in a `9:16` frame. With an Element connected, the node uses `m2v`, the mode that takes "
        "references.\n\n" + RECOVER_NOTE,
        "take_description": "Films the kept host in the place and saves the video.",
    },
    "video-03-keep-a-host-across-shots": {
        "input": SIGN_IN_STEP + "2. Describe the host in **Host**.\n3. Say what happens in the first shot in "
        "**Opening**, and in the second in **Closing**.\n4. Press **Run**. Both shots are saved under "
        "`video/dreamina`.",
        "cast": "Seedream 5.0 Lite draws the host from the waist up. `references`, what an earlier Dreamina step made, "
        "passes the portrait on to **Keep**.",
        "keep": "**Element: Add** saves the portrait as an Element named **Host**, a character Dreamina keeps so it "
        "looks the same in every video. Making an Element is free. Its `references` output gives both shots the same "
        "host.\n\nTo keep more angles of the host, connect them to `auxiliary`. A voice clip goes in `voice`.",
        "shot_1": "Seedance 2.0 Mini films **Opening** with the host from **Keep**, four seconds at `720p` in a `9:16` "
        "frame. With an Element connected, the node uses `m2v`, the mode that takes references, and `{{reference1}}` "
        "in the prompt marks the host.\n\n" + RECOVER_NOTE,
        "shot_1_description": "Films the first shot with the kept host and saves it.",
        "shot_2": "Seedance 2.0 Mini films **Closing** with the same Element, so the host matches **Shot 1**. Each "
        "shot is its own run and is billed.\n\n" + RECOVER_NOTE,
        "shot_2_description": "Films the second shot with the kept host and saves it.",
    },
}

__all__ = ["WORKFLOW_TEXTS"]
