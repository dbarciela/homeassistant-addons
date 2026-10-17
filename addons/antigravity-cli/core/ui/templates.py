"""HTML Body Templates Loader for Antigravity Addon.

Loads HTML layout from core/ui/static/templates/body.html, maintaining 100%
backwards-compatibility with modules expecting HTML_BODY string.
"""

import os

STATIC_BODY_FILE = os.path.join(os.path.dirname(__file__), "static", "templates", "body.html")

_CACHED_BODY: str = ""


def get_html_body() -> str:
    """Retrieve HTML body template, cached in memory after first load."""
    global _CACHED_BODY
    if _CACHED_BODY:
        return _CACHED_BODY
    if os.path.exists(STATIC_BODY_FILE):
        try:
            with open(STATIC_BODY_FILE, "r", encoding="utf-8") as f:
                _CACHED_BODY = f.read()
                return _CACHED_BODY
        except Exception:
            pass
    return ""


# Backwards compatibility export
HTML_BODY = get_html_body()
