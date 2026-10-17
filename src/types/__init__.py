"""Records shared by the runtime: dataclasses for in-process values, pydantic models for JSON."""

from typing import Literal
from pydantic import BaseModel, ConfigDict

type Json = bool | int | float | str | list[Json] | dict[str, Json] | None
# What a paid generation node's models make: one node per kind, as model list groups models by type.
type Kind = Literal["image", "video", "audio"]
# What a reference carries: a kind's media, or a Dreamina Element.
type MediaKind = Literal["image", "video", "audio", "element"]


class Value(BaseModel):
    """A frozen record that refuses unknown fields, for files this extension writes."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class Reply(BaseModel):
    """A frozen record that ignores unknown fields, for the JSON the Dreamina CLI prints."""

    # The CLI adds fields over time; a new field must not break a paid run that already succeeded.
    model_config = ConfigDict(extra="ignore", frozen=True)


# Type aliases are imported by name; __all__ lists runtime names.
__all__ = ["Reply", "Value"]
