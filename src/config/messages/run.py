"""Messages for the failures the Dreamina CLI reports.

{reason} is the CLI's cleaned reason, ending as a sentence, and page placeholders are filled from DREAMINA_URLS.
"""

CANVAS_MISSING = (
    "The Dreamina canvas this extension uses was deleted, so this step did not run. Run again: the next run creates a "
    "new ComfyUI canvas."
)

CEILING_TOO_LOW = (
    "This run needs {minimum} credits, more than its credit_ceiling of {ceiling}. Nothing was billed. Raise "
    "credit_ceiling to {minimum} or more to run it."
)

CLI_FAILED = (
    "The Dreamina CLI stopped with an error: {reason} Try again. If it happens again, select Update in Dreamina "
    "Settings."
)

CREDENTIALS_DENIED = (
    "The Dreamina CLI may not open this computer's sign-in store. Run ComfyUI as the user who signed in to Dreamina, "
    "then try again."
)

CREDENTIALS_UNREADABLE = (
    "The Dreamina CLI could not read this computer's sign-in store: {reason} Check that ComfyUI runs as the user who "
    "signed in. If it does, contact Dreamina support before you sign in again."
)

DNS_FAILED = (
    "The Dreamina CLI could not look up Dreamina's servers. Check this computer's internet connection and DNS "
    "settings, then try again."
)

FREE_TIMEOUT = (
    "{node} did not finish within the request timeout of {seconds} seconds in Dreamina Settings. It bills nothing. "
    "Select Run to try again."
)

FLAG_REFUSED = (
    "The Dreamina CLI refused a flag or a value, so nothing was sent: {reason} Check arguments against the model's "
    "flags in Model: Info."
)

LOCAL_STATE_FAILED = (
    "The Dreamina CLI could not save its own records on this computer: {reason} Check that the user running ComfyUI "
    "can write to its home folder, then try again."
)

MODE_REQUIRED = (
    'The Dreamina CLI needs a mode for this run, so nothing was sent. Set "mode" in arguments to one of the model\'s '
    "modes in Model: Info."
)

NETWORK_DENIED = (
    "This computer stopped the Dreamina CLI from reaching the internet. Allow dreamina-canvas in your firewall or "
    "security software, then try again."
)

NETWORK_TIMEOUT = "The connection to Dreamina timed out. Check the internet connection, then try again."

NO_REASON = "no reason given."

OPERATION_INCOMPLETE = "Dreamina did not finish this step before the Dreamina CLI stopped waiting for it. Try again."

PRICE_UNKNOWN = (
    "Dreamina could not work out the price of this run, so it stopped before running. Nothing was billed. Try again "
    "in a few minutes."
)

REFERENCE_REFUSED = (
    "The Dreamina CLI refused a reference, so nothing was sent: {reason} Connect references only from Dreamina nodes."
)

REFERENCE_UNAVAILABLE = (
    "A reference or an uploaded file is not available on the ComfyUI canvas: {reason} Connect a current output, or "
    "run the node that made it again."
)

REGION_UNAVAILABLE = (
    "The Dreamina CLI is not available for this account's region: {reason} See {cli_page} for who can use it."
)

RUN_REFUSED = (
    "Dreamina refused this run, so it did not start and nothing was billed: {reason} Change the prompt, the connected "
    "inputs, or arguments, then run again."
)

SIGN_IN_LIMITED = (
    "Dreamina is limiting sign-in requests from this computer: {reason} Wait a few minutes, then try again."
)

SIGN_IN_REQUIRED = "You are not signed in to Dreamina. In Dreamina Settings, select Sign in, then try again."

TITLE_REQUIRED = (
    "Dreamina needs words in the prompt to name this run, so nothing was sent. Describe the result in prompt, then "
    "run again."
)

UPSCALE_PARTLY_REFUSED = (
    "Dreamina refused to upscale image {number}: {reason} The other images are being upscaled and billed. Collect "
    "them with Generation: Download."
)

UPSCALE_REFUSED = "Dreamina refused to upscale image {number}: {reason}"

UPGRADE_REQUIRED = (
    "Dreamina no longer accepts this version of the Dreamina CLI. Select Update in Dreamina Settings, then try again."
)

__all__ = [
    "CANVAS_MISSING",
    "CEILING_TOO_LOW",
    "CLI_FAILED",
    "CREDENTIALS_DENIED",
    "CREDENTIALS_UNREADABLE",
    "DNS_FAILED",
    "FLAG_REFUSED",
    "FREE_TIMEOUT",
    "LOCAL_STATE_FAILED",
    "MODE_REQUIRED",
    "NETWORK_DENIED",
    "NETWORK_TIMEOUT",
    "NO_REASON",
    "OPERATION_INCOMPLETE",
    "PRICE_UNKNOWN",
    "REFERENCE_REFUSED",
    "REFERENCE_UNAVAILABLE",
    "REGION_UNAVAILABLE",
    "RUN_REFUSED",
    "SIGN_IN_LIMITED",
    "SIGN_IN_REQUIRED",
    "TITLE_REQUIRED",
    "UPGRADE_REQUIRED",
    "UPSCALE_PARTLY_REFUSED",
    "UPSCALE_REFUSED",
]
