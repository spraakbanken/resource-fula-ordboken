import html
from typing import Any


unescape_str = html.unescape


def unescape_any(s: Any) -> Any:
    if isinstance(s, dict):
        return {k: unescape_any(v) for k, v in s.items()}
    elif isinstance(s, list):
        return [unescape_any(v) for v in s]
    elif isinstance(s, str):
        return html.unescape(s)
    else:
        return s
