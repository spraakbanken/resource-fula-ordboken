"""Utility functions for working with text."""

import html
from typing import Any

unescape_str = html.unescape


def unescape_any(s: Any) -> Any:
    """Unescape str or list[str] or dict[Any,str] recursively.

    Anythning else is passed through.

    Args:
        s (Any): the object to unescape

    Returns:
        Any: the unescaped input or the input
    """
    if isinstance(s, dict):
        return {k: unescape_any(v) for k, v in s.items()}
    if isinstance(s, list):
        return [unescape_any(v) for v in s]
    return html.unescape(s) if isinstance(s, str) else s
