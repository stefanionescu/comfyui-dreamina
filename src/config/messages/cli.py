"""Messages for a Dreamina CLI that is missing, too old, changed, or unreadable, and for its installer."""

CLI_CHANGED = (
    'The Dreamina CLI does not offer {command}, which this extension uses. Update the Dreamina extension in ComfyUI to '
    'its latest release.'
)

CLI_MISSING = 'ComfyUI could not find the Dreamina CLI. Select Install in Dreamina Settings.'

CLI_NOT_STARTED = (
    'The Dreamina CLI is installed but could not start on this computer. Select Update in Dreamina Settings to install '
    'it again.'
)

CLI_OUTDATED = (
    'The Dreamina CLI is version {version}, and this extension needs version {minimum} or later. Select Update in '
    'Dreamina Settings.'
)

CLI_REPLY_INVALID = (
    'The Dreamina CLI gave a reply this extension cannot read. Try again. If it happens again, select Update in '
    'Dreamina Settings.'
)

CLI_TIMEOUT = (
    'The Dreamina CLI did not answer within {seconds} seconds, so ComfyUI stopped it. Check the internet connection, '
    'then try again.'
)

CLI_VERSION_UNREADABLE = (
    'The Dreamina CLI did not report its version and commands in a form this extension reads. Select Update in '
    'Dreamina Settings.'
)

INSTALL_DOWNLOAD_FAILED = (
    'The Dreamina installer could not be downloaded from dreamina.capcut.com. Check the internet connection, or run '
    "the install command from the extension's README in a terminal."
)

INSTALL_FAILED = (
    "The Dreamina installer stopped with an error: {reason} Run the install command from the extension's README in a "
    'terminal to see all of its output.'
)

INSTALL_NO_ANSWER = (
    'The Dreamina installer finished, but the Dreamina CLI does not answer. Run dreamina-canvas version in a terminal '
    'to see why.'
)

INSTALL_SHELL_MISSING = (
    'The Dreamina installer needs {program}, which the ComfyUI computer does not have. Install {program}, then select '
    'Install in Dreamina Settings again.'
)

INSTALL_TIMEOUT = (
    "The Dreamina installer did not finish within {minutes} minutes. Run the install command from the extension's "
    'README in a terminal.'
)

__all__ = [
    'CLI_CHANGED',
    'CLI_MISSING',
    'CLI_NOT_STARTED',
    'CLI_OUTDATED',
    'CLI_REPLY_INVALID',
    'CLI_TIMEOUT',
    'CLI_VERSION_UNREADABLE',
    'INSTALL_DOWNLOAD_FAILED',
    'INSTALL_FAILED',
    'INSTALL_NO_ANSWER',
    'INSTALL_SHELL_MISSING',
    'INSTALL_TIMEOUT',
]
