"""The group notes and subgraph descriptions of the shipped workflows, in plain language."""

SIGN_IN_STEP = "1. Sign in to Dreamina in **ComfyUI menu → Extensions → Dreamina → Dreamina Settings**.\n"

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
}

__all__ = ["WORKFLOW_TEXTS"]
