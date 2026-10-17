"""ByteDance's official Dreamina CLI installer: where it is, how it runs, and how long it may take."""

# The installer for each system: a shell script on macOS and Linux, a PowerShell script on Windows. The address
# redirects to the current release on ByteDance's CDN, as the CLI page's own curl -L command follows it.
INSTALLER_URLS = {
    "POSIX": "https://dreamina.capcut.com/canvas-cli/install.sh",
    "WINDOWS": "https://dreamina.capcut.com/canvas-cli/install.ps1",
}

# The installer is read only over HTTPS from a host under one of these CapCut domains, after at most
# INSTALLER_REDIRECTS redirects.
INSTALLER_DOMAINS = (".capcut.com", ".capcutstatic.com")
INSTALLER_REDIRECTS = 3

# The program and options that run a downloaded installer; the installer file goes last.
INSTALLER_SHELLS = {
    "POSIX": ("bash",),
    "WINDOWS": ("powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File"),
}

# How long the installer script's download may take, in seconds.
INSTALLER_DOWNLOAD_SECONDS = 30

# How long the installer may run, in seconds.
INSTALL_TIMEOUT_SECONDS = 300

# The largest installer script read, and how much of the installer's output is kept for an error message.
INSTALLER_BYTES = {
    "SCRIPT": 1_000_000,
    "OUTPUT": 65_536,
}

# How many of the installer's last output lines an error message quotes.
INSTALLER_REASON_LINES = 3

__all__ = [
    "INSTALLER_BYTES",
    "INSTALLER_DOMAINS",
    "INSTALLER_DOWNLOAD_SECONDS",
    "INSTALLER_REASON_LINES",
    "INSTALLER_REDIRECTS",
    "INSTALLER_SHELLS",
    "INSTALLER_URLS",
    "INSTALL_TIMEOUT_SECONDS",
]
