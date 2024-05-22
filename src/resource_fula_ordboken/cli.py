"""CLI for preparing fula-ordboken."""

from pathlib import Path
from typing import Optional

import typer

# from sb_karp.utility import text
from resource_fula_ordboken import use_cases
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
        output_name = files.normalize_file_name(files.real_stem(path.stem))
        json_output = output / f"{output_name}.jsonl.gz"
        saf_output = output / f"{output_name}.processed.saf.zip"

    use_cases.convert_and_package(
        file=path,
        title=f"{path.stem} (processed)",
        date_issued=date_issued,
        json_output=json_output,
        saf_output=saf_output,
    )


@subapp.command()
def karp_as_batch(
    path: Path,
    baseline: Path = typer.Option(...),
    output: Optional[Path] = typer.Option(None, help="file to write to"),  # noqa: UP007
) -> None:
    """Compute updates for converted entries and a given baseline.

    This command computes and creates a batch of commands for updating fula ordboken in .
    """
    msg = files.real_stem(path.stem)
    date_issued = msg.split("_")[-1]
    if not output:
        output = Path("data/data_processed")
        output_path = output / f"fula-ordboken-batch-{date_issued}.jsonl.gz"
    use_cases.create_karp_batch_from_export(
        path, baseline=baseline, output_path=output_path, msg=msg
    )


if __name__ == "__main__":
    subapp()
