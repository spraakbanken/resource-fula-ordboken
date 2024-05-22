"""Use cases."""

import csv
import shutil
from pathlib import Path
from zipfile import ZipFile

from chardet import UniversalDetector
from chardet.resultdict import ResultDict
from simple_archive.use_cases import CreateSimpleArchiveFromCSVWriteToPath, create_unique_path

from resource_fula_ordboken import text


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

        change_encoding_to_utf8(path)

        unescape_file(path)
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


def detect_encoding(path: Path) -> ResultDict:
    """Detect encoding of file by reading as little as possible.

    Args:
        path (Path): the file to scan

    Returns:
        dict: the result
    """
    detector = UniversalDetector()
    for line in path.open("rb"):
        detector.feed(line)
        if detector.done:
            break
    return detector.close()


def unescape_file(src_path: Path) -> None:
    """Unescape the contents of given path.

    Writes a temporary file that is moved to replace the original file.

    Args:
        src_path (Path): path to file
    """
    dst_path = src_path.with_suffix(f"{src_path.suffix}.swp")
    with dst_path.open("w", encoding="utf-8") as unescaped_file:
        for line in src_path.open(encoding="utf-8"):
            unescaped_file.write(text.unescape_str(line))

    dst_path.replace(src_path)


def change_encoding_to_utf8(src_path: Path, encoding: str | None = None) -> None:
    """Change encoding of the file from 'src_encoding' to 'utf-8'.

    Writes a temporary file that is moved to replace the src_path.

    Args:
        src_path (Path): path to the file
        encoding (str): encoding of the file
    """
    dst_path = src_path.with_suffix(f"{src_path.suffix}.swp")

    src_encoding = encoding or detect_encoding(src_path)["encoding"]
    if src_encoding in {"ascii", "utf-8"}:
        return
    with (
        src_path.open(encoding=src_encoding) as src_file,
        dst_path.open("w", encoding="utf-8") as dst_file,
    ):
        for line in src_file:
            dst_file.write(line)

    dst_path.replace(src_path)
