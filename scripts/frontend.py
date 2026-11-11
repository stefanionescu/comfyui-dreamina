"""Build the browser bundle, or check the shipped one."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING
import asyncio
import argparse

from scripts.paths import REPO_ROOT, WEB_FOLDER, FRONTEND_CHECK_FOLDER

if TYPE_CHECKING:
    from pathlib import Path

BUNDLE = 'extension.js'
STYLES = 'extension.css'


async def _build_bundle(destination: Path, *, is_quiet: bool = False) -> None:
    """Run the build script of package.json into the given folder.

    Args:
        destination: The folder that receives the bundle.
        is_quiet: Whether Bun and esbuild print only warnings and errors, so a check that passes prints nothing.

    Raises:
        RuntimeError: When the build script exits with an error.

    """
    process = await asyncio.create_subprocess_exec(
        'bun',
        'run',
        *(('--silent',) if is_quiet else ()),
        'build',
        f'--outfile={destination / BUNDLE}',
        *(('--log-level=warning',) if is_quiet else ()),
        cwd=REPO_ROOT,
    )
    if await process.wait() != 0:
        message = 'esbuild failed.'
        raise RuntimeError(message)


def main() -> int:
    """Build the bundle into web/, or report when the shipped bundle differs.

    Returns:
        The exit code, which is 1 when `--check` finds a shipped file that differs from its build, else 0.

    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    arguments = parser.parse_args()
    if not arguments.check:
        asyncio.run(_build_bundle(WEB_FOLDER))
        return 0
    scratch = FRONTEND_CHECK_FOLDER
    scratch.mkdir(parents=True, exist_ok=True)
    asyncio.run(_build_bundle(scratch, is_quiet=True))
    problems = [
        f'Rebuild {name} with mise run comfy:frontend:build.'
        for name in (BUNDLE, STYLES)
        if not (built := WEB_FOLDER / name).is_file() or built.read_bytes() != (scratch / name).read_bytes()
    ]
    sys.stderr.writelines(f'{problem}\n' for problem in problems)
    return int(bool(problems))


if __name__ == '__main__':
    raise SystemExit(main())
