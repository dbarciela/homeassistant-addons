"""Modular GFM Markdown Parser Engine powered by bundled marked.js.
Supports GFM tables, nested lists, headers, code blocks with copy buttons,
and GitHub/Terminal style callouts.
"""

import os

STATIC_MARKDOWN_FILE = os.path.join(os.path.dirname(__file__), "ui", "static", "js", "markdown_parser.js")

_CACHED_MD: str = ""


def get_markdown_js() -> str:
    """Retrieve markdown parser JS module, cached after first load."""
    global _CACHED_MD
    if _CACHED_MD:
        return _CACHED_MD
    if os.path.exists(STATIC_MARKDOWN_FILE):
        try:
            with open(STATIC_MARKDOWN_FILE, "r", encoding="utf-8") as f:
                _CACHED_MD = f.read()
                return _CACHED_MD
        except Exception:
            pass
    return ""


# Backwards compatibility export
MARKDOWN_JS_MODULE = get_markdown_js()
