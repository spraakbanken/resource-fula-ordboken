"""This package prepares fula-ordboken for Karp."""

__version__ = "0.1.0"


def get_version() -> str:
    """Get version.

    >>> get_version()
    '0.1.0'
    """
    return __version__


def user_agent() -> str:
    """User agent."""
    return f"resource-fula-ordboken/{__version__}"
