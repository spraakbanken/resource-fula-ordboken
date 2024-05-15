from pathlib import Path

import json_arrays
from karp_lex_types import EntryDto
from tqdm import tqdm


def find_updates_from_export(path: Path, baseline: Path) -> tuple[list, list, list[str]]:
    base = {
        obj["entry"]["id"]: EntryDto(**obj)
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

    removes = [
        key
        for key in tqdm(base, desc="Finding entries to remove", unit=" entries")
        if key not in curr
    ]

    updates = []
    adds = []
    # find updated entries
    for key, curr_entry in tqdm(
        curr.items(), desc="Finding entries to add or update", unit=" entries"
    ):
        if key in base:
            if curr_entry != base[key].entry:
                updates.append(
                    {
                        "entity_id": base[key].entity_id,
                        "version": base[key].version,
                        "entry": curr_entry,
                    }
                )
        else:
            adds.append(curr_entry)

    return adds, updates, removes


def find_updates_old_format(path: Path, baseline: Path) -> tuple[list, list, list[str]]:
    base = {
        obj["id"]: obj
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

    removes = [
        key
        for key in tqdm(base, desc="Finding entries to remove", unit=" entries")
        if key not in curr
    ]

    updates = []
    adds = []
    # find updated entries
    for key, value in tqdm(
        curr.items(), desc="Finding entries to add or update", unit=" entries"
    ):
        if key in base:
            if value != base[key]:
                updates.append({"entry_id": key, "entry": value})
        else:
            adds.append(value)

    return adds, updates, removes
