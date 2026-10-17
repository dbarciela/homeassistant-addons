# Google Antigravity CLI - Home Assistant Add-on

[![Current Version](https://img.shields.io/badge/version-1.4.0-blue.svg)](config.yaml)

![Google Antigravity Smart Home Web UI](web_ui_preview.png)

This add-on runs the **Google Antigravity CLI (`agy`)** directly inside Home Assistant, fully integrating it so AI agents can natively monitor and control all Home Assistant devices and states.

*   **Web-based Dual Interface**: Directly supports both a web terminal (`ttyd`/`tmux`) and an intuitive, responsive Web UI within the Home Assistant Ingress dashboard.
*   **Complete MCP Integration**: Runs the official `ha-mcp` via `stdio`, providing over 88 Home Assistant-specific tools (lighting control, sensor reading, automation management, etc.) out-of-the-box.
*   **Granular 3-Stage Operating Modes (`chat_mode`)**:
    *   `full`: Fast smart home control combined with complete deep CLI reasoning.
    *   `fast_only`: Ultra-fast (0.05s) device control and conversation history browsing without spawning the `agy` CLI subprocess, completely eliminating 200–300MB RAM spikes on memory-constrained systems.
    *   `monitoring`: Lightweight system monitoring and daemon telemetry dashboard.
*   **Mobile 2×2 Responsive View & Real-time Usage Graphs**: Status card grid optimized for smartphones with high-resolution, real-time CPU/RAM sparkline charts.
*   **Remote Daemon Control (`agy remote-control serve`)**: Integrates with the official Google remote web dashboard (`antigravity.google.com`) with safe busy-lock protections.
*   **Persistent Background Sessions**: Work continues in background `tmux` sessions even when you close the browser tab.
*   **Persistent Storage**: Configuration, authentication credentials, and custom skills are safely preserved in `/config/.gemini` across add-on restarts and rebuilds.

📖 **[Fast Control Mode Guide](https://dbarciela.github.io/homeassistant-addons/fast-control-guide/)** — Comprehensive reference of natural language commands and usage patterns  
📖 **[CLI Reasoning Mode Guide](https://dbarciela.github.io/homeassistant-addons/cli-reasoning-guide/)** — Guide for login, model/agent selection, file attachments, and MCP integration with the deep agy agent

### 🧩 Built-in Components

The following components are automatically set up on installation (and preserved during updates). See the **Documentation** tab for details:

*   **MCP**: Official `ha-mcp` (88+ tools for device control, sensor queries, automation management, with automatic token injection) — Source: [homeassistant-ai/ha-mcp](https://github.com/homeassistant-ai/ha-mcp)
*   **Agent Skills**: `home-assistant-best-practices` (automatically consulted when writing automations, helpers, and dashboards) — Source: [homeassistant-ai/skills](https://github.com/homeassistant-ai/skills/tree/main/skills/home-assistant-best-practices)
*   **5 Custom Agents** (switchable in CLI mode): Orchestrator (default), Automation Engineer, Dashboard Designer, Diagnostics Operator, Smart Controller
*   **Hooks**: `ha-file-guard` — Unconditionally blocks deletion or destructive overwriting of critical HA files (`.storage`, `secrets.yaml`, `configuration.yaml`, etc.)
*   **Harness Rules**: `ha-guidelines` (prioritizes `ha-mcp` tools), `ha-file-safety` (mandatory explicit approval before file deletion/overwrite + hard denial on core data even if approved)

### 📦 Bundled Open-Source Libraries

*   **[jsdiff](https://github.com/kpdecker/jsdiff)** (`diff` 9.0.0, BSD-3-Clause) — Used in the diff viewer to show line-by-line file modifications during CLI reasoning mode. Vendored directly inside the add-on without requiring external network requests.

### 🤝 Credits & Acknowledgements

Special thanks and full credit to **[dugurs](https://github.com/dugurs)**, the original creator and lead author responsible for the core architecture, implementation, and features of this Home Assistant add-on. Maintained and enhanced by [dbarciela](https://github.com/dbarciela).

For detailed installation instructions, usage guidelines, and troubleshooting, please refer to the **Documentation** tab.
