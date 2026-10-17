"""Web UI Aggregator and Template Renderer for Antigravity Dual Ingress.

Supports:
- Clean modular static assets (served via ./static/* for browser caching and fast initial load)
- In-memory inlined fallback when required
- Dynamic configuration injection (ENABLE_CHAT_UI, CHAT_MODE)
"""

import os
from typing import Optional

from core.ui.scripts import get_js
from core.ui.styles import get_css
from core.ui.templates import get_html_body
from core.ui.vendor_diff import get_jsdiff

STATIC_INDEX_TEMPLATE = os.path.join(os.path.dirname(__file__), "ui", "static", "index.html")


def render_web_ui(chat_enabled: bool = True, chat_mode: str = "dual", inline: bool = False) -> str:
    """Render the full Web UI HTML page with configuration injected."""
    body_content = get_html_body()
    config_script = (
        f"<script>\n"
        f"  window.ENABLE_CHAT_UI = {'true' if chat_enabled else 'false'};\n"
        f"  window.CHAT_MODE = '{chat_mode}';\n"
        f"</script>"
    )

    if inline:
        # Build self-contained HTML with inlined assets (useful for offline/standalone rendering)
        from core.markdown_parser import MARKDOWN_JS_MODULE
        css_content = get_css()
        js_diff = get_jsdiff()
        js_app = get_js()

        return f"""<!DOCTYPE html>
<html lang="pt-PT" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>Google Antigravity Smart Home</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Pretendard:wght@400;500;600;700&family=Fira+Code:wght@400;500&display=swap" rel="stylesheet">
  <style>
{css_content}
  </style>
  {config_script}
</head>
<body>
{body_content}
  <script>
{js_diff}
  </script>
  <script>
{MARKDOWN_JS_MODULE}
  </script>
  <script>
{js_app}
  </script>
</body>
</html>
"""

    # Default: Use modular index.html with static asset links (fast, browser cached)
    if os.path.exists(STATIC_INDEX_TEMPLATE):
        with open(STATIC_INDEX_TEMPLATE, "r", encoding="utf-8") as f:
            template = f.read()
        html = template.replace("<!-- __HEAD_CONFIG__ -->", config_script)
        html = html.replace("<!-- __BODY_CONTENT__ -->", body_content)
        return html

    # Fallback to inlined if template missing
    return render_web_ui(chat_enabled, chat_mode, inline=True)


# Backwards compatibility export
HTML_INDEX = render_web_ui(chat_enabled=True, chat_mode="dual", inline=True)
