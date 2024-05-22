"""Data models for Fula Ordboken."""

import pydantic


class FulaOrd(pydantic.BaseModel):
    """Data model for a Fula Ordboken entry."""

    baseform: str
    id: str
    wordforms: list[str]
    text: str
    jfr: list[str] | None = None

    model_config = pydantic.ConfigDict(extra="forbid")
