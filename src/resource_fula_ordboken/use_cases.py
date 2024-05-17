"""Use cases."""

import csv
import shutil
from pathlib import Path

from simple_archive.use_cases import CreateSimpleArchiveFromCSVWriteToPath, create_unique_path


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
