"""Vendored jsdiff JavaScript Library Loader for Antigravity Addon.

Loads jsdiff from core/ui/static/js/vendor_diff.js, maintaining 100%
backwards-compatibility with modules expecting JSDIFF_MIN_JS string.
"""

import os

STATIC_DIFF_FILE = os.path.join(os.path.dirname(__file__), "static", "js", "vendor_diff.js")

_CACHED_DIFF: str = ""


def get_jsdiff() -> str:
    """Retrieve jsdiff script, cached in memory after first load."""
    global _CACHED_DIFF
    if _CACHED_DIFF:
        return _CACHED_DIFF
    if os.path.exists(STATIC_DIFF_FILE):
        try:
            with open(STATIC_DIFF_FILE, "r", encoding="utf-8") as f:
                _CACHED_DIFF = f.read()
                return _CACHED_DIFF
        except Exception:
            pass
    return ""


# Backwards compatibility export
JSDIFF_MIN_JS = get_jsdiff()
