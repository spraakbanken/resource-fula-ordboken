"""CLI for preparing fula-ordboken."""

from pathlib import Path
from typing import Optional

import json_arrays
import typer

# from sb_karp.utility import text
from resource_fula_ordboken import find_updates, use_cases
from resource_fula_ordboken.fula_ord_converter import FulaOrdTxt2JsonConverter
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
        file=path, title=path.stem, date_issued=date_issued, output_path=output
    )


@subapp.command()
def convert(
    path: Path,
    output: Optional[Path] = typer.Option(None, help="file to write to"),  # noqa: UP007
) -> None:
    """Convert FulaOrd entries."""
    typer.echo(f"reading '{path}' ...", err=True)
    if not output:
        output = Path(f"{path}.jsonl")
    typer.echo(f"writing output to '{output}' ...", err=True)
    converter = FulaOrdTxt2JsonConverter()
    with path.open(encoding="utf-8") as fp:
        typer.echo("converting entries ...", err=True)
        fulaord = list(converter.convert_entry(fp))
        typer.echo(f"updating 'jfr' and writing to '{output}' ...", err=True)
        json_arrays.dump_to_file(converter.update_jfr(fulaord), output)
        # for length, entry in enumerate(convert_entry(fp), 1):
        #     pass
        # print(f"number of words: {length}")


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
