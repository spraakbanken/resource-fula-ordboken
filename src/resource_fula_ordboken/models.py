"""Data models for Fula Ordboken."""

import karp_lex_types
import pydantic


class FulaOrd(pydantic.BaseModel):
    """Data model for a Fula Ordboken entry."""

    baseform: str
    id: str
    wordforms: list[str]
    text: str
    jfr: list[str] | None = None

    model_config = pydantic.ConfigDict(extra="forbid")


FulaOrdEntry = karp_lex_types.GenericEntryDto[FulaOrd]

AddFulaOrdEntry = karp_lex_types.commands.GenericAddEntry[FulaOrd]
UpdateFulaOrdEntry = karp_lex_types.commands.GenericUpdateEntry[FulaOrd]
DeleteFulaOrdEntry = karp_lex_types.commands.DeleteEntry

FulaOrdEntryCmd = AddFulaOrdEntry | DeleteFulaOrdEntry | UpdateFulaOrdEntry
