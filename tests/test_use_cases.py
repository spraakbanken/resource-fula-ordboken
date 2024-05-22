import tempfile
from pathlib import Path

from resource_fula_ordboken import use_cases


def test_package_as_simple_archive() -> None:
    fd, file_to_package = tempfile.mkstemp(suffix=".txt", text=True)
    with open(fd, "w", encoding="utf-8") as fp:  # noqa: PTH123, FURB103
        fp.write("text text")

    _output_dir_guard = tempfile.mkdtemp()
    output_dir = Path(_output_dir_guard)

    _work_dir_guard = tempfile.mkdtemp()
    workdir = Path(_output_dir_guard)

    output_path = output_dir / "test.saf.zip"
    use_cases.package_file_as_simple_archive(
        Path(file_to_package),
        title="test",
        date_issued="2024-05-22",
        output_path=output_path,
        workdir=workdir,
    )

    assert output_path.exists()
