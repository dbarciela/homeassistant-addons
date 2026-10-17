"""JavaScript Client Scripts Loader for Antigravity Addon.

Loads client scripts from core/ui/static/js/app.js, maintaining 100%
backwards-compatibility with modules expecting JS_SCRIPTS string.
"""

import os

STATIC_JS_FILE = os.path.join(os.path.dirname(__file__), "static", "js", "app.js")

_CACHED_JS: str = ""


def get_js() -> str:
    """Retrieve JavaScript scripts, cached in memory after first load."""
    global _CACHED_JS
    if _CACHED_JS:
        return _CACHED_JS
    if os.path.exists(STATIC_JS_FILE):
        try:
            with open(STATIC_JS_FILE, "r", encoding="utf-8") as f:
                _CACHED_JS = f.read()
                return _CACHED_JS
        except Exception:
            pass
    return ""


# Backwards compatibility export
JS_SCRIPTS = get_js()
