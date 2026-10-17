"""CSS Styles Loader for Antigravity Addon.

Loads stylesheet cleanly from core/ui/static/css/app.css, maintaining 100%
backwards-compatibility with modules expecting CSS_STYLES string.
"""

import os

STATIC_CSS_FILE = os.path.join(os.path.dirname(__file__), "static", "css", "app.css")

_CACHED_CSS: str = ""


def get_css() -> str:
    """Retrieve CSS styles, cached in memory after first load."""
    global _CACHED_CSS
    if _CACHED_CSS:
        return _CACHED_CSS
    if os.path.exists(STATIC_CSS_FILE):
        try:
            with open(STATIC_CSS_FILE, "r", encoding="utf-8") as f:
                _CACHED_CSS = f.read()
                return _CACHED_CSS
        except Exception:
            pass
    return ""


# Backwards compatibility export
CSS_STYLES = get_css()
