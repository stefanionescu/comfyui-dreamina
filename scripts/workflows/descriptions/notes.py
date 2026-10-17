"""The group notes and subgraph descriptions of the shipped workflows, in plain language."""

SIGN_IN_STEP = "1. Sign in to Dreamina in **ComfyUI menu → Extensions → Dreamina → Dreamina Settings**.\n"
UPSCALE_RECOVER_NOTE = "A cancel does not stop an upscale Dreamina has accepted. It keeps running and is billed."

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
        "so the model can read it. GPT Image 2.5 Sunburst then redraws it as **Change** asks, at `1:1` and `1K`, its "
        "smallest size. `{{image1}}` in the prompt marks where your photo goes.\n\nTo combine several products, give "
        "**Edit** a list of up to 16 photos, and name them `{{image1}}`, `{{image2}}`, and so on.",
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
}

__all__ = ["WORKFLOW_TEXTS"]
