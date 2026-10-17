"""What the pack reads about Dreamina's models from the CLI's model list."""

from . import Kind, Reply
from pydantic import Field
from ..config.models import FLAG_PREFIX
from ..config.messages.models import MODE_LABEL


class ModelFlag(Reply):
    """One flag of a mode entry.

    Attributes:
        name: The flag as the list writes it, with its two leading dashes, such as --ratio.
        required: Whether the run is refused without it.
        values: The allowed values, exactly as listed; None when any text is allowed.
        minimum: The smallest number allowed.
        maximum: The largest number allowed.
        step: The step from the minimum, or from 0 when there is no minimum.
        min_length: The shortest text allowed, in characters.
        max_length: The longest text allowed, in characters.

    """

    name: str = Field(alias="flag")
    required: bool
    values: tuple[str, ...] | None = None
    minimum: float | None = Field(default=None, alias="min")
    maximum: float | None = Field(default=None, alias="max")
    step: float | None = None
    min_length: int | None = Field(default=None, alias="minLength")
    max_length: int | None = Field(default=None, alias="maxLength")


class ReferenceLimit(Reply):
    """How many references of one media type a mode entry takes.

    Attributes:
        media_type: image, video, or audio.
        minimum: The fewest of that type.
        maximum: The most of that type.

    """

    media_type: str = Field(alias="mediaType")
    minimum: int = Field(alias="min")
    maximum: int = Field(alias="max")


class ModelReferences(Reply):
    """The references a mode entry takes.

    Attributes:
        minimum: The fewest references in all.
        maximum: The most references in all.
        limits: The media types the entry enables; an empty tuple enables none.
        required_types: At least one of these types must be connected; empty when there is no such rule.
        exclusive_types: These types may not be connected together; empty when there is no such rule.

    """

    minimum: int = Field(alias="min")
    maximum: int = Field(alias="max")
    limits: tuple[ReferenceLimit, ...] = Field(alias="types")
    required_types: tuple[str, ...] = Field(default=(), alias="requireAnyOfTypes")
    exclusive_types: tuple[str, ...] = Field(default=(), alias="mutuallyExclusiveTypes")


class ModelMode(Reply):
    """One mode entry of a model; one mode name can have several entries.

    Attributes:
        name: The mode, such as first_last_frame, sent as --mode.
        scenario: The speech scenario, sent as --scenario; None for every other mode.
        flags: The flags this entry accepts, in list order.
        references: The entry's reference limits; None when the list leaves them out, which means the entry takes none.
        vip_required: Whether the entry needs a paid plan, for Model: Info only.
        vip_sizes: The sizes a paid plan unlocks, for Model: Info only.

    """

    name: str
    scenario: str | None = None
    flags: tuple[ModelFlag, ...] = ()
    references: ModelReferences | None = None
    vip_required: bool | None = Field(default=None, alias="vipRequired")
    vip_sizes: tuple[str, ...] | None = Field(default=None, alias="vipResolutions")

    @property
    def label(self) -> str:
        """Name the mode as refusals do: its name, with its scenario when it has one."""
        return MODE_LABEL.format(name=self.name, scenario=self.scenario) if self.scenario else self.name

    @property
    def named_flags(self) -> dict[str, ModelFlag]:
        """The entry's flags in list order, keyed by name without the leading dashes, the one place they are removed."""
        return {flag.name.removeprefix(FLAG_PREFIX): flag for flag in self.flags}


class ListedModel(Reply):
    """One model of the person's live model list.

    Attributes:
        kind: The list's type, which is the kind the list was read for.
        name: The canonical name, sent as --model.
        aliases: Other names that match; never sent.
        modes: The mode entries in list order.

    """

    kind: Kind = Field(alias="type")
    name: str = Field(alias="model")
    aliases: tuple[str, ...] = ()
    modes: tuple[ModelMode, ...]


class ModelListReply(Reply):
    """The reply of model list for one kind.

    Attributes:
        items: The models of that kind.

    """

    items: tuple[ListedModel, ...]


__all__ = ["ListedModel", "ModelFlag", "ModelListReply", "ModelMode", "ModelReferences", "ReferenceLimit"]
