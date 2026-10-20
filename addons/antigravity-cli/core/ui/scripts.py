"""JavaScript Client Scripts Loader for Antigravity Addon.

Loads client scripts from core/ui/static/js/, maintaining 100%
backwards-compatibility with modules expecting JS_SCRIPTS string.
"""

import os

STATIC_JS_DIR = os.path.join(os.path.dirname(__file__), "static", "js")
STATIC_JS_FILE = os.path.join(STATIC_JS_DIR, "app.js")

_CACHED_JS: str = ""


def get_js() -> str:
    """Retrieve JavaScript scripts, cached in memory after first load."""
    global _CACHED_JS
    if _CACHED_JS:
        return _CACHED_JS

    scripts = []
    # Order of dependencies
    script_files = [
        "vendor_diff.js",
        "markdown_parser.js",
        "voice_input.js",
        "entity_cards.js",
        "app.js",
    ]

    for fname in script_files:
        fpath = os.path.join(STATIC_JS_DIR, fname)
        if os.path.exists(fpath):
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    scripts.append(f.read())
            except Exception:
                pass

    if scripts:
        _CACHED_JS = "\n\n".join(scripts)
        return _CACHED_JS

    # Fallback to single app.js if list failed
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
