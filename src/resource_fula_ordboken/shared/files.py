"""Common file related utilities."""


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
