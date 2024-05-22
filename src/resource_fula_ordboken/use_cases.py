"""Use cases."""

import csv
import shutil
from pathlib import Path
from zipfile import ZipFile

import json_arrays
from simple_archive.use_cases import CreateSimpleArchiveFromCSVWriteToPath, create_unique_path

from resource_fula_ordboken.fula_ord_converter import FulaOrdTxt2JsonConverter
from resource_fula_ordboken.shared import files


def package_file_as_simple_archive(
    file: Path,
    *,
    title: str,
    date_issued: str,
    output_path: Path,
    workdir: Path | None = None,
) -> None:
    """Create Simple Archive Format for given file.

    Args:
        file (Path): the file to add to archive
        title (str): title to used
        date_issued (str): date issued
        output_path (Path): where to write the simple_archive,
        workdir (Path | None, optional): specify where the temporary files should be stored. Defaults to None.
    """  # noqa: E501
    working_dir = workdir or Path("tmp")

    working_dir = create_unique_path(working_dir, file.stem)

    working_dir.mkdir(parents=True)

    local_file = working_dir / file.name
    shutil.copy(file, local_file)

    csv_path = working_dir / "metadata.csv"

    with csv_path.open("w", encoding="utf-8") as fp:
        csv_writer = csv.DictWriter(fp, fieldnames=("files", "dc.title", "dc.date.issued"))
        csv_writer.writeheader()
        csv_writer.writerow(
            {"files": local_file.name, "dc.title": title, "dc.date.issued": date_issued}
        )

    create_simplearchive = CreateSimpleArchiveFromCSVWriteToPath()

    create_simplearchive.execute(csv_path, output_path=output_path, create_zip=True)


def clean_data_and_package(
    file: Path, *, title: str, date_issued: str, output_path: Path, workdir: Path | None = None
) -> None:
    """Clean data and package as Simple Archive Format.

    Args:
        file (Path): the Fula Ordboken export
        title (str): title to use
        date_issued (str): date issued
        output_path (Path): where to write the simple archive
        workdir (Path | None, optional): specify where the temporary files should be stored. Defaults to None.
    """  # noqa: E501
    working_dir = workdir or Path("tmp")

    working_dir = create_unique_path(working_dir, file.stem)

    working_dir.mkdir(parents=True)

    with ZipFile(file) as zipf:
        zipf.extractall(path=working_dir)

    file_names = []
    for path in working_dir.iterdir():
        if path.is_dir():
            continue

        files.change_encoding_to_utf8(path)

        files.unescape_file(path)
        file_names.append(path.name)

    csv_path = working_dir / "metadata.csv"
    with csv_path.open("w", encoding="utf-8") as fp:
        csv_writer = csv.DictWriter(fp, fieldnames=("files", "dc.title", "dc.date.issued"))
        csv_writer.writeheader()
        csv_writer.writerow(
            {"files": "||".join(file_names), "dc.title": title, "dc.date.issued": date_issued}
        )

    create_simplearchive = CreateSimpleArchiveFromCSVWriteToPath()

    create_simplearchive.execute(csv_path, output_path=output_path, create_zip=True)


def convert_and_package(
    file: Path,
    *,
    title: str,
    date_issued: str,
    json_output: Path,
    saf_output: Path,
    workdir: Path | None = None,
) -> None:
    """Convert Fula Ordboken txt to karp7 jsonl.

    Args:
        file (Path): file with cleaned data
        title (str): title the use
        date_issued (str): date issued
        json_output (Path): path where to write karp json
        saf_output (Path): path to create the Simple Archive
        workdir (Path | None, optional): workdir. Defaults to None.

    Raises:
        ValueError: If the extension of file is unknown.
    """
    working_dir = workdir or Path("tmp")

    working_dir = create_unique_path(working_dir, file.stem)

    working_dir.mkdir(parents=True)

    converter = FulaOrdTxt2JsonConverter()

    json_output.parent.mkdir(parents=True)
    if file.suffix == "txt":
        with file.open(encoding="utf-8") as fp:
            fulaord = list(converter.convert_entry(fp))
            json_arrays.dump_to_file(converter.update_jfr(fulaord), json_output)
    elif file.suffix == "zip":
        with ZipFile(file) as zipf:
            for file_name in zipf.namelist:
                if file_name.endswith(".txt"):
                    with zipf.open(file_name) as fp:
                        fulaord = list(converter.convert_entry(fp))
                        json_arrays.dump_to_file(converter.update_jfr(fulaord), json_output)
    else:
        raise ValueError(f"unknown file extension ('{file.suffix}')")

    local_file = working_dir / json_output.name
    shutil.copy(json_output, local_file)

    csv_path = working_dir / "metadata.csv"

    with csv_path.open("w", encoding="utf-8") as fp:
        csv_writer = csv.DictWriter(fp, fieldnames=("files", "dc.title", "dc.date.issued"))
        csv_writer.writeheader()
        csv_writer.writerow(
            {"files": local_file.name, "dc.title": title, "dc.date.issued": date_issued}
        )

    create_simplearchive = CreateSimpleArchiveFromCSVWriteToPath()

    create_simplearchive.execute(csv_path, output_path=saf_output, create_zip=True)
