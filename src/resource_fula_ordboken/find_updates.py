"""Find updates."""

from pathlib import Path

import json_arrays
from tqdm import tqdm

import resource_fula_ordboken
from resource_fula_ordboken.models import (
    AddFulaOrdEntry,
    DeleteFulaOrdEntry,
    FulaOrdEntry,
    FulaOrdEntryCmd,
    UpdateFulaOrdEntry,
)


def find_updates_from_export(path: Path, baseline: Path, *, msg: str) -> list[FulaOrdEntryCmd]:
    """Find updates from Karp export.

    Args:
        path (Path): new entries
        baseline (Path): the last used entries
        msg (str): The message to use

    Returns:
        tuple[list, list, list[str]]: entries to add, update, delete
    """
    base = {
        obj["entry"]["id"]: FulaOrdEntry(**obj)
        for obj in tqdm(
            json_arrays.load_from_file(baseline),
            desc="Loading baseline",
            unit=" entries",
        )
    }

    curr = {
        obj["id"]: obj
        for obj in tqdm(
            json_arrays.load_from_file(path), desc="Loading current", unit=" entries"
        )
    }

    batch: list[FulaOrdEntryCmd] = [
        DeleteFulaOrdEntry(
            user=resource_fula_ordboken.user_agent(),
            message=msg,
            resourceId="fulaord",
            id=base[key].id,
            version=base[key].version,
        )
        for key in tqdm(base, desc="Finding entries to remove", unit=" entries")
        if key not in curr
    ]

    # find updated entries
    for key, curr_entry in tqdm(
        curr.items(), desc="Finding entries to add or update", unit=" entries"
    ):
        if key in base:
            if curr_entry != base[key].entry:
                batch.append(
                    UpdateFulaOrdEntry(
                        resourceId=base[key].resource,
                        id=base[key].id,
                        version=base[key].version,
                        entry=curr_entry,
                        user=resource_fula_ordboken.user_agent(),
                        message=msg,
                    )
                )
        else:
            batch.append(
                AddFulaOrdEntry(
                    resourceId="fulaord",
                    entry=curr_entry,
                    user=resource_fula_ordboken.user_agent(),
                    message=msg,
                )
            )

    return batch
