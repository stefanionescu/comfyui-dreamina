"""Register the extension's local routes with ComfyUI."""

from pathlib import Path

from server import PromptServer
import folder_paths
from comfy.cli_args import args

from .runtime import get_runtime
from .settings import SettingsRoutes
from ..state.errors import ErrorCode, DreaminaError
from ..config.messages.settings import PRIVATE_STATE_LOCATION

# The installed extension, which the private state must stay out of.
EXTENSION_ROOT = Path(__file__).resolve().parents[2]


def register_routes() -> None:
    """Reject public state locations before enabling changes, then register every local route."""
    runtime = get_runtime()
    directory = runtime.configuration.directory.resolve()
    public_roots = (
        folder_paths.base_path,
        folder_paths.get_input_directory(),
        folder_paths.get_output_directory(),
        folder_paths.get_temp_directory(),
        folder_paths.get_user_directory(),
        str(EXTENSION_ROOT),
    )
    if any(directory.is_relative_to(Path(root).resolve()) for root in public_roots):
        raise DreaminaError(ErrorCode.CONFIGURATION, PRIVATE_STATE_LOCATION)
    routes = SettingsRoutes(runtime.configuration, runtime.sign_in, is_multi_user=args.multi_user)
    routes.register(PromptServer.instance.routes)


__all__ = ['register_routes']
