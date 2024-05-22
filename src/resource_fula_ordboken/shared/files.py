"""Common file related utilities."""

from pathlib import Path

from chardet import UniversalDetector
from chardet.resultdict import ResultDict

from resource_fula_ordboken import text


def normalize_file_name(name: str) -> str:
    """Create a normalized file name.

    Args:
        name (str): the file name to normalize

    Returns:
        str: the normalized name
    """
    normalized_name = name.lower()
    normalized_name = normalized_name.replace(" - ", "-")
    return normalized_name.replace(" ", "_")


def real_stem(possible_stem: str) -> str:
    """Extract the real stem of a file name.

    Removes all suffixes.

    >>> real_stem('file')
    'file'
    >>> real_stem('file.ext')
    'file'
    >>> real_stem('file.ext1.ext2')
    'file'
    >>> real_stem('file.ext1.ext2.ext3')
    'file'

    Args:
        possible_stem (str): strips all extensions from this file name

    Returns:
        str: stem
    """
    path = Path(possible_stem)
    while True:
        if not path.suffix:
            return path.stem
        path = Path(path.stem)


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
