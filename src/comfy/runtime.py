"""Create the shared stores when ComfyUI loads the extension."""

from ..state.errors import ErrorCode, DreaminaError
from ..storage.files import choose_state_directory
from ..config.storage import FILE_NAMES, GENERATION_FOLDER
from ..settings.store import ConfigurationStore
from ..storage.canvas import CanvasStore
from ..dreamina.account import SignInState
from ..config.messages.settings import RUNTIME_NOT_READY
from ..dreamina.generations.records import GenerationStore


class Runtime:
    """State shared by this extension's nodes and routes across event loops.

    Attributes:
        configuration: Private settings and the account cache token.
        sign_in: The pending Dreamina sign-in, kept in memory.
        canvas: The pack's saved Dreamina canvas.
        generations: Recorded generations, one per submit ID.

    """

    __slots__ = ('canvas', 'configuration', 'generations', 'sign_in')

    configuration: ConfigurationStore
    sign_in: SignInState
    canvas: CanvasStore
    generations: GenerationStore

    def __init__(self) -> None:
        """Create the shared stores and place their state under one private directory."""
        self.configuration = ConfigurationStore(choose_state_directory())
        self.sign_in = SignInState(self.configuration.reset_account_token)
        self.canvas = CanvasStore(self.configuration.directory / FILE_NAMES['CANVAS'])
        self.generations = GenerationStore(self.configuration.directory / GENERATION_FOLDER)


_runtime: Runtime | None = None


def create_runtime() -> None:
    """Initialize once through the host's extension lifecycle, without network calls."""
    global _runtime  # noqa: PLW0603 # reason: ComfyUI initializes one shared runtime during loading.
    if _runtime is None:
        _runtime = Runtime()


def get_runtime() -> Runtime:
    """Reject execution before the host has loaded the extension."""
    if _runtime is None:
        raise DreaminaError(ErrorCode.CONFIGURATION, RUNTIME_NOT_READY)
    return _runtime


__all__ = ['Runtime', 'create_runtime', 'get_runtime']
