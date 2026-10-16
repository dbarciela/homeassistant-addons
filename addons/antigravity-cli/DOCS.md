# Google Antigravity CLI - Home Assistant Add-on

[![Current Version](https://img.shields.io/badge/version-1.3.1--beta.1-blue.svg)](config.yaml)

This add-on runs the **Google Antigravity CLI (`agy`)** directly inside Home Assistant, fully integrating it so AI agents can natively monitor and control all Home Assistant devices and states.

## ✨ Features

*   **Web-based Terminal:** Access the Antigravity CLI directly inside your Home Assistant Ingress dashboard.
*   **Complete Model Context Protocol (MCP) Integration:**
    *   Runs the official **`ha-mcp`** as a **`stdio` process** using the ultra-fast Python package manager `uv`, providing over 88 Home Assistant-specific tools (lighting control, sensor queries, automation management, etc.) directly to the AI agent.
    *   Utilizes the officially supported `stdio` transport of Antigravity CLI, preventing `Method Not Allowed` errors and ensuring a rock-solid connection.
*   **Persistent Background Sessions (Tmux):** Tasks and chat sessions remain active in the background via `tmux` even if you close the browser window.
*   **Persistent Storage:** AI settings, authentication credentials, and user-defined skills are safely preserved in Home Assistant's `/config/.gemini` folder across add-on restarts and updates.

## 📖 Related Documentation

*   **[Fast Control Mode Guide](https://dugurs.github.io/homeassistant-addons/fast-control-guide/)** — Comprehensive reference of natural language commands and usage patterns
*   **[CLI Reasoning Mode Guide](https://dugurs.github.io/homeassistant-addons/cli-reasoning-guide/)** — Guide for login, model/agent selection, file attachments, and MCP integration with the deep agy agent

## 🚀 Installation & Setup

You can easily add this add-on repository to Home Assistant using the button below:

[![Open your Home Assistant instance and show the add add-on repository dialog with a specific repository URL pre-filled.](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fdbarciela%2Fhomeassistant-addons)

1.  After adding the repository, go to **Settings > Add-ons > Add-on Store**.
2.  Click the three dots menu (⋮) in the top right, select **Repositories**, and add this custom repository URL.
3.  Refresh the store, locate the **"Google Antigravity CLI"** add-on, and click **Install**.
4.  Click **"Start"** to launch the add-on.
5.  Click **"Open Web UI"** to open the terminal in your browser.
6.  When `agy` starts for the first time, `ha-mcp` will download automatically (**one-time only**, takes about 10–20 seconds).
7.  Once downloaded, verify the MCP connection status by entering the following command at the agy prompt (`>`):
    ```
    /mcp
    ```
    If the `home-assistant` server is shown as **✓ connected**, installation was successful.

## 🛠 Usage

Once the terminal is open, interact naturally with the agent by typing commands at the prompt (`>`):

**Example Prompts:**
> *"What is the living room temperature?"*
> *"Turn off all lights currently on in the house."*
> *"Plot a graph of refrigerator power consumption over the last hour."*

### 💡 Terminal (Tmux) Scrolling & Keyboard Shortcuts

This add-on uses `tmux` under the hood to maintain persistent background sessions. Use the following shortcuts to navigate and scroll terminal history:

*   **Enter Scroll Mode**: Press `Ctrl + B` then `[` (or scroll up with the mouse wheel).
*   **Scroll Navigation**: Use the arrow keys (Up/Down) or `Page Up` / `Page Down` to review past conversation history.
*   **Exit Scroll Mode**: Press `Esc` or `q` to return to the live prompt.

### ⚙️ Configuration Options

By default, the add-on automatically detects Home Assistant's `SUPERVISOR_TOKEN` and configures all permissions automatically. You do not need to manually configure IP addresses or API tokens.

| Option | Type | Default | Description |
|---|---|---|---|
| `auto_start_remote_control` | bool | `false` | Automatically starts the `agy remote-control serve` daemon in the background on boot. Recommended when using web dashboards or remote sessions. |
| `enable_terminal` | bool | `true` | Enables the Ingress web terminal (`ttyd` and `tmux`). Can be disabled after initial login to save RAM if only using remote control or chat. |
| `chat_mode` | string (enum) | `"full"` | Web UI operating mode: `"full"` (fast smart home control + full CLI reasoning), `"fast_only"` (0.05s fast device control and conversation history browsing only; saves RAM by avoiding 200–300MB agy process memory spikes), `"monitoring"` (lightweight telemetry and daemon monitoring dashboard). |
| `dangerous_mode` | bool | `true` | Passes `--dangerously-skip-permissions` to chat (CLI reasoning mode) and remote daemon. Recommended (`true`) to prevent headless agy from hanging indefinitely on approval prompts. |
| `api_port` | port | `8000` | Port number for the add-on's REST/SSE and status API. |
| `api_key` | string | `""` (empty) | Authentication token for external client access. When left empty, allows unauthenticated access from the local network. |
| `print_timeout` | string | `"5m"` | Maximum timeout duration for headless CLI execution. |
| `ha_sse_url` | string | `""` (empty) | Specify an external Streamable HTTP/SSE MCP URL (e.g., HACS component). Leave empty to use default local stdio (`uvx ha-mcp@latest`). |
| `enable_sandbox` | bool | `false` | Whether to apply sandbox container isolation during CLI execution. |

## 📝 Troubleshooting

*   **What if the AI asks for permission when trying to control a device?**
    On first run, the agent asks for tool access permissions. Choose **"Yes, and always allow... (Persist to settings.json)"** so it controls devices automatically without prompting again.

*   **How to allow all ha-mcp permissions in CLI at once?**
    Enter the following in the chat prompt:
    ```
    Please add "mcp(home-assistant/*)" to permissions.allow in the ~/.gemini/antigravity-cli/settings.json file
    ```

*   **Why is the first run of `ha-mcp` slow?**
    On initial run, `uvx` downloads the `ha-mcp@latest` package (~10–20 seconds). Subsequent runs use the local cache and start instantly.

*   **What if the MCP server throws a `Method Not Allowed` error?** (when upgrading from v1.0.2 or below)
    Starting from v1.0.3, the legacy SSE HTTP server method was removed in favor of `stdio`, which is the officially supported transport for Antigravity CLI. Update the add-on to the latest version and restart.

## 🧩 Built-in Components (MCP, Skills, Agents, Hooks, Rules)

The add-on automatically configures the following components on boot. Configured via 3-way merge deployment, user customizations are preserved across add-on updates:

*   **MCP Server — `ha-mcp`**
    Automatically connects the official Home Assistant MCP server via `stdio` using `uvx ha-mcp@latest`. Provides **88+ tools** for device control, sensor queries, automation/script/scene editing, and backup management with automatic `SUPERVISOR_TOKEN` injection.
    Source: [homeassistant-ai/ha-mcp](https://github.com/homeassistant-ai/ha-mcp) (MIT License, PyPI `ha-mcp` package)

*   **Agent Skill — `home-assistant-best-practices`**
    Collection of best practices automatically consulted when creating automations, helpers, scripts, dashboards, and blueprints. Helps the CLI mode choose between Jinja2 templates vs. native options, helper selection, and card documentation.
    Source: [homeassistant-ai/skills](https://github.com/homeassistant-ai/skills/tree/main/skills/home-assistant-best-practices)

*   **Custom Agents (switchable via "Select Agent" in CLI mode)**

    | Agent | Specialty |
    |---|---|
    | HA Antigravity Orchestrator (Default) | General orchestrator that classifies and handles automation, dashboard, diagnostics, and real-time control requests. |
    | HA Automation Engineer | Designs automations, scripts, and scenes; validates YAML syntax; debugs execution traces. |
    | HA Dashboard Designer | Designs Lovelace dashboard views and cards, registers resources, optimizes responsive layouts. |
    | HA Diagnostics Operator | Analyzes HA and add-on logs, detects offline/unavailable devices, conducts system health checks. |
    | HA Smart Controller | Real-time control of lights, switches, and climate; batch mode switching; status briefings. |

*   **Hook — `ha-file-guard`**
    PreToolUse hook that intercepts file deletion and overwrite tools. Hard-blocks attempts to run `rm`, `mv`, or overwrite critical Home Assistant data (`/homeassistant/.storage`, `secrets.yaml`, `configuration.yaml`, `automations.yaml`, `home-assistant_v2.db`, `/backup`, etc.) at the script level. Always active regardless of `--dangerously-skip-permissions`.

*   **`permissions.deny` List (`bundled/hooks/deny_rules.json`)**
    Registered in `settings.json` `permissions.deny` for additional protection when running in interactive terminal mode without `--dangerously-skip-permissions`.

*   **Harness Rules (Always-on Rules)**
    *   `ha-guidelines` — Instructs the agent to prioritize `ha-mcp` tools over raw `curl` for device queries and control.
    *   `ha-file-safety` — Requires explicit user approval before deleting or overwriting any file, and hard-rejects any modification to core HA data even if approved.

*   **Web UI Open-Source Library — `jsdiff`**
    Used by the diff viewer to show line-by-line file changes during CLI reasoning mode. Vendored directly in `core/ui/vendor_diff.py` without external network dependencies.
    Source: [kpdecker/jsdiff](https://github.com/kpdecker/jsdiff) (`diff` 9.0.0, BSD-3-Clause)

*   **Git-Backed Configuration Snapshots — `ha-git-backup`**
    Integrated CLI utility to track, diff, and snapshot Home Assistant configurations using Git with a secure `.gitignore` (safeguarding `secrets.yaml`, `.storage/auth`, databases, SSL certs, and logs).
    Usage inside the terminal:
    *   `ha-git-backup init` — Initialise git tracking in `/homeassistant` with secure rules.
    *   `ha-git-backup commit "message"` (or alias `habackup "message"`) — Snapshot modified YAMLs and automations.
    *   `ha-git-backup status` (or alias `hasync status`) — Show modified files.
    *   `ha-git-backup diff` — Inspect recent YAML changes.
    *   `ha-git-backup push [remote]` — Push snapshots to a remote private git repository.

*   **Custom MCP Servers — `custom_mcp_servers`**
    Configure additional Model Context Protocol servers directly in the add-on Configuration UI (`config.yaml`). Accepts a JSON object mapping server names to command/args or URL configurations, merged seamlessly with the default `ha-mcp` server into `mcp_config.json`.

*   **Multi-Arch Container Builds (GHCR)**
    Prebuilt container images for `amd64` and `aarch64` are automatically built via GitHub Actions (`.github/workflows/build.yaml`) using the official Home Assistant builder and published to the GitHub Container Registry (`ghcr.io/dbarciela/{arch}-addon-antigravity-cli`).

*   **ESPHome & Hardware Flashing Tools**
    Full ESPHome suite (`esphome`, `esptool`, `build-essential`, `udev`) pre-installed with host `uart`, `usb`, and `udev` access. Allows Antigravity to validate, compile, and flash ESP32/ESP8266 firmwares directly from `/homeassistant/esphome/` via OTA or USB-to-serial.
    *   `cdesp` — Quick navigate to the ESPHome configuration directory.
    *   `esphome config <device.yaml>` (or `esphome-check <device.yaml>`) — Validate configuration syntax.
    *   `esphome compile <device.yaml>` — Compile firmware locally.
    *   `esphome upload <device.yaml>` / `esphome run <device.yaml>` — Flash device via WiFi OTA or connected USB.
    *   `esptool.py` — Low-level serial diagnostic and flashing tool.

## 🏗 Architecture & Internal Structure

*   **ttyd + tmux**: Bridges browser and terminal sessions.
*   **uvx + ha-mcp (stdio)**: Launches `uvx ha-mcp@latest` as a child process when `agy` requests MCP tools.
*   **SUPERVISOR_TOKEN Auto-Injection**: Reads token from container environment and forwards it to `ha-mcp`.
*   **ha-git-backup**: Provides fast git snapshots of `/homeassistant` before making major changes.
*   **Bash Wrapper Script**: Ensures cross-architecture binary compatibility across x86_64 and ARM environments.
