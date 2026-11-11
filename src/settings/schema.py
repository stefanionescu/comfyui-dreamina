"""Validate private limits before the extension sends any request."""

from dataclasses import fields

from ..state import Json
from ..state.errors import ErrorCode, DreaminaError
from ..state.settings import Settings
from ..config.settings import SETTING_RANGES
from ..config.messages.settings import SETTINGS_RANGE, SETTING_UNKNOWN, SETTINGS_WHOLE_NUMBERS

# The configured default for every setting.
DEFAULT_SETTINGS = Settings(**{name: definition['default'] for name, definition in SETTING_RANGES.items()})


def _validate_settings(settings: Settings) -> None:
    """Keep every limit in its range.

    Args:
        settings: The settings to check.

    Raises:
        DreaminaError: When a limit is outside its range.

    """
    for name, definition in SETTING_RANGES.items():
        value: int = getattr(settings, name)
        if not definition['minimum'] <= value <= definition['maximum']:
            raise DreaminaError(ErrorCode.CONFIGURATION, SETTINGS_RANGE)


def parse_settings(document: dict[str, Json]) -> Settings:
    """Reject unknown settings instead of silently accepting misspelled limits.

    Args:
        document: The settings by name; a missing setting takes its default.

    Returns:
        The validated settings.

    Raises:
        DreaminaError: When a name is unknown or a value is not a whole number.

    """
    expected = {item.name for item in fields(Settings)}
    if document.keys() - expected:
        raise DreaminaError(ErrorCode.CONFIGURATION, SETTING_UNKNOWN)
    integers: dict[str, int] = {}
    for name in expected:
        value = document.get(name, getattr(DEFAULT_SETTINGS, name))
        if type(value) is not int:
            raise DreaminaError(ErrorCode.CONFIGURATION, SETTINGS_WHOLE_NUMBERS)
        integers[name] = value
    settings = Settings(**integers)
    _validate_settings(settings)
    return settings


__all__ = ['DEFAULT_SETTINGS', 'parse_settings']
