"""CLI for preparing fula-ordboken."""

from pathlib import Path
from typing import Optional

import json_arrays
import typer

# from sb_karp.utility import text
from resource_fula_ordboken import find_updates, use_cases
from resource_fula_ordboken.shared import files

subapp = typer.Typer()


@subapp.command()
def package_raw(path: Path, output: Optional[Path] = None) -> None:  # noqa: UP007
    """Package raw file as SimpleArchive for Metadata Repo."""
    date_issued = path.stem.split(" ")[-1]
    if not output:
        output = Path("data/data_raw")
        output_name = files.normalize_file_name(path.stem)
        output /= f"{output_name}.raw.saf.zip"
    use_cases.package_file_as_simple_archive(
        file=path, title=path.stem, date_issued=date_issued, output_path=output
    )


@subapp.command()
def raw2clean(path: Path, output: Optional[Path] = None) -> None:  # noqa: UP007
    """Clean the raw data and packages the cleaned data."""
    date_issued = path.stem.split(" ")[-1]
    if not output:
        output = Path("data/data_clean")
        output_name = files.normalize_file_name(path.stem)
        output /= f"{output_name}.clean.saf.zip"
    use_cases.clean_data_and_package(
        file=path, title=f"{path.stem} (cleaned)", date_issued=date_issued, output_path=output
    )


@subapp.command()
def clean2karp(
    path: Path,
    output: Optional[Path] = typer.Option(None, help="file to write to"),  # noqa: UP007
) -> None:
    """Convert FulaOrd entries from clean data."""
    date_issued = path.stem.split("_")[-1]
    if not output:
        output = Path("data/data_processed")
        output_name = files.normalize_file_name(path.stem)
        json_output = output / f"{output_name}.jsonl.gz"
        saf_output = output / f"{output_name}.processed.saf.zip"

    use_cases.convert_and_package(
        file=path,
        title=f"{path.stem} (processed)",
        date_issued=date_issued,
        json_output=json_output,
        saf_output=saf_output,
    )


@subapp.command(name="find_update")
def find_updates_cmd(
    path: Path,
    baseline: Path = typer.Option(...),
    from_export: bool = typer.Option(
        True, help="The baseline is exported from karp and has entity_ids"
    ),
) -> None:
    """Compute updates for converted entries and a given baseline.

    This command computes and separates entries to add, update and delete.
    """
    typer.echo(f"Using '{baseline}' as baseline", err=True)

    if from_export:
        adds, updates, removes = find_updates.find_updates_from_export(path, baseline)
    else:
        adds, updates, removes = find_updates.find_updates_old_format(path, baseline)

    output = Path(f"{path}.adds.jsonl")
    typer.echo(f"Writing adds to {output} ...", err=True)
    json_arrays.dump_to_file(adds, output)

    output = Path(f"{path}.removes.jsonl")
    typer.echo(f"Writing removes to {output} ...", err=True)
    json_arrays.dump_to_file(removes, output)

    output = Path(f"{path}.updates.jsonl")
    typer.echo(f"Writing updates to {output} ...", err=True)
    json_arrays.dump_to_file(updates, output)


if __name__ == "__main__":
    subapp()
