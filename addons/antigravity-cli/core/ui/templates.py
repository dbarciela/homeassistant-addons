"""Web UI HTML Templates."""

from core.ui import UI_BUILD_VERSION

_SVG = 'viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'

# Lucide-equivalent icons (the recovered React build used lucide-react
# throughout -- these are the same glyphs as inline SVG, stroke=currentColor
# so size/color are set by the .icon wrapper in CSS, not baked into the markup).
ICON_MENU = f'<svg {_SVG}><line x1="4" y1="6" x2="20" y2="6"/><line x1="4" y1="12" x2="20" y2="12"/><line x1="4" y1="18" x2="20" y2="18"/></svg>'
ICON_MOON = f'<svg {_SVG}><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>'
ICON_SUN = f'<svg {_SVG}><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/></svg>'
ICON_COINS = f'<svg {_SVG}><circle cx="8" cy="8" r="6"/><path d="M18.09 10.37A6 6 0 1 1 10.34 18"/><path d="M7 6h1v4"/><path d="M16.71 13.88l.7.71-2.82 2.82"/></svg>'
ICON_PLUS = f'<svg {_SVG}><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>'
ICON_MESSAGE = f'<svg {_SVG}><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>'
ICON_TERMINAL = f'<svg {_SVG}><polyline points="4 17 10 11 4 5"/><line x1="12" y1="19" x2="20" y2="19"/></svg>'
ICON_TRASH = f'<svg {_SVG}><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><line x1="10" y1="11" x2="10" y2="17"/><line x1="14" y1="11" x2="14" y2="17"/></svg>'
ICON_CHECK_SQUARE = f'<svg {_SVG}><polyline points="9 11 12 14 22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg>'
ICON_SQUARE = f'<svg {_SVG}><rect x="3" y="3" width="18" height="18" rx="2"/></svg>'
ICON_ARROW_UP = f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="19" x2="12" y2="5"/><polyline points="5 12 12 5 19 12"/></svg>'
ICON_MIC = f'<svg {_SVG}><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" y1="19" x2="12" y2="23"/><line x1="8" y1="23" x2="16" y2="23"/></svg>'
ICON_ZAP = f'<svg {_SVG}><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>'
ICON_BRAIN = f'<svg {_SVG}><path d="M9.5 2A2.5 2.5 0 0 0 7 4.5v.5A2.5 2.5 0 0 0 4.5 7.5 2.5 2.5 0 0 0 3 9.9 2.5 2.5 0 0 0 4.5 14a2.5 2.5 0 0 0 2.5 2.5V19a2.5 2.5 0 0 0 5 0V4.5A2.5 2.5 0 0 0 9.5 2z"/><path d="M14.5 2A2.5 2.5 0 0 1 17 4.5v.5a2.5 2.5 0 0 1 2.5 2.5A2.5 2.5 0 0 1 21 9.9 2.5 2.5 0 0 1 19.5 14a2.5 2.5 0 0 1-2.5 2.5V19a2.5 2.5 0 0 1-5 0V4.5A2.5 2.5 0 0 1 14.5 2z"/></svg>'
ICON_CHEVRON_DOWN = f'<svg {_SVG}><polyline points="6 9 12 15 18 9"/></svg>'
ICON_CHEVRON_UP = f'<svg {_SVG}><polyline points="18 15 12 9 6 15"/></svg>'
ICON_CHEVRON_RIGHT = f'<svg {_SVG}><polyline points="9 18 15 12 9 6"/></svg>'
ICON_CHECK = f'<svg {_SVG}><polyline points="20 6 9 17 4 12"/></svg>'
ICON_BAR_CHART = f'<svg {_SVG}><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>'
ICON_INFO = f'<svg {_SVG}><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>'
ICON_X = f'<svg {_SVG}><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>'
ICON_USER = f'<svg {_SVG}><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>'
ICON_EXTERNAL_LINK = f'<svg {_SVG}><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>'

ICON_DOWNLOAD = f'<svg {_SVG}><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>'

# Compact badge text ("b13") -- short like the reference's "v2.0", full version stays in the tooltip.
_UI_VERSION_SHORT = "b" + UI_BUILD_VERSION.rsplit(".", 1)[-1] if "beta." in UI_BUILD_VERSION else UI_BUILD_VERSION

HTML_BODY = f"""
<header>
    <div class="brand">
      <button class="icon-btn-lg" id="sidebar-toggle-btn" onclick="toggleSessionSidebar()" title="Toggle conversations sidebar"><span class="icon">{ICON_MENU}</span></button>
      <div class="brand-name">
        <span class="brand-emoji">🤖</span>
        <span>Antigravity CLI</span>
        <span class="brand-badge" id="build-badge" title="Build version (for update verification): {UI_BUILD_VERSION}">{_UI_VERSION_SHORT}</span>
      </div>
    </div>
    <div class="header-right">
      <button class="header-stat-pill" id="resource-badge" onclick="toggleResourcePanel()" title="Click to pin/unpin real-time resource graphs">
        <span class="stat-dot stat-dot-green"></span>
        <span id="header-cpu">0.0%</span>
        <span class="stat-sep">·</span>
        <span class="stat-dot stat-dot-blue"></span>
        <span id="header-ram">0MB</span>
      </button>
      <button class="icon-btn-lg" id="export-chat-btn" onclick="exportChatHistory()" title="Export conversation to Markdown"><span class="icon">{ICON_DOWNLOAD}</span></button>
      <button class="icon-btn-lg" id="theme-toggle-btn" onclick="toggleTheme()" title="Toggle Dark/Light theme"><span class="icon" id="theme-toggle-icon">{ICON_MOON}</span></button>
      <button class="icon-btn-lg" id="help-btn" onclick="toggleHelpPanel()" title="Help / Feedback"><span class="icon">{ICON_INFO}</span></button>
    </div>
  </header>

  <div class="image-lightbox-overlay" id="image-lightbox-overlay" onclick="closeImageLightbox()">
    <img id="image-lightbox-img" src="" alt="">
  </div>

  <div class="help-overlay" id="help-overlay" onclick="if(event.target===this) toggleHelpPanel()">
    <div class="help-box">
      <div class="help-box-top">
        <h3>Help &amp; Feedback</h3>
        <button class="help-box-close" onclick="toggleHelpPanel()"><span class="icon">{ICON_X}</span></button>
      </div>
      <div class="help-section">
        <h4>Execution Modes</h4>
        <ul>
          <li><strong>Fast Control Mode</strong> — Instantly controls devices and queries state; provides sensor-based environmental analysis for weather questions</li>
          <li><strong>CLI Reasoning Mode</strong> — Deep reasoning agent powered by Antigravity CLI (agy)</li>
        </ul>
      </div>
      <div class="help-section">
        <h4>Guides & Documentation</h4>
        <ul>
          <li><a href="https://dugurs.github.io/homeassistant-addons/fast-control-guide/" target="_blank" rel="noopener">Fast Control Mode Guide ↗</a></li>
          <li><a href="https://dugurs.github.io/homeassistant-addons/cli-reasoning-guide/" target="_blank" rel="noopener">CLI Reasoning Mode Guide ↗</a></li>
        </ul>
      </div>
      <div class="help-section">
        <h4>Keyboard Shortcuts</h4>
        <ul>
          <li><span class="mono">Ctrl+K</span> — Start new conversation</li>
          <li><span class="mono">Enter</span> — New line; <span class="mono">Ctrl+Enter</span> or <strong>Send button</strong> to send</li>
          <li><span class="mono">/codesearch &lt;query&gt;</span> — Workspace code search (built-in grep)</li>
        </ul>
      </div>
      <div class="help-section">
        <h4>MCP Integration</h4>
        <ul id="help-mcp-list"><li>Loading...</li></ul>
      </div>
      <div class="help-section">
        <h4>Skills</h4>
        <ul id="help-skills-list"><li>Loading...</li></ul>
      </div>
      <div class="help-section">
        <h4>Hooks</h4>
        <ul id="help-hooks-list"><li>Loading...</li></ul>
      </div>
      <div class="help-section">
        <h4>Bug Reports / Feature Requests</h4>
        <a href="https://github.com/dugurs/homeassistant-addons/issues" target="_blank" rel="noopener">Submit on GitHub Issues ↗</a>
      </div>
    </div>
  </div>

  <div class="hw-notice-overlay" id="hw-notice-overlay" onclick="if(event.target===this) closeHwNotice(false)">
    <div class="hw-notice-box">
      <div class="hw-notice-icon">⚠️</div>
      <h3 class="hw-notice-title">CLI Reasoning Mode — Hardware Limitation Detected</h3>
      <ul class="hw-notice-list">
        <li>This CPU does not support AVX/AVX2 instruction sets required by the agy engine; real-time reasoning progress may not display on screen.</li>
        <li>If running in a VM, try switching the CPU in your hypervisor settings to <strong>Host Passthrough mode</strong>.</li>
        <li>Responses will still arrive, but may take <strong>1–2+ minutes</strong> to complete.</li>
        <li>You can use <strong>Web Terminal Mode</strong> to view the reasoning progress.</li>
      </ul>
      <div class="hw-notice-actions">
        <button class="hw-notice-btn-secondary" onclick="closeHwNotice(true)">Do not show again</button>
        <button class="hw-notice-btn-primary" onclick="closeHwNotice(false)">Close</button>
      </div>
    </div>
  </div>

  <!-- Full, unfolded file-edit diff -- opened by the "⤢ View Full" button
       inside a reasoning-timeline diff step (see openDiffModal() /
       stepDetailHTML() in core/ui/scripts.py). -->
  <div class="diff-modal-overlay" id="diff-modal-overlay" onclick="if(event.target===this) closeDiffModal()">
    <div class="diff-modal-box">
      <div class="diff-modal-top">
        <h3>Full Diff</h3>
        <button class="diff-modal-close" onclick="closeDiffModal()"><span class="icon">{ICON_X}</span></button>
      </div>
      <div class="diff-modal-body" id="diff-modal-body"></div>
    </div>
  </div>

  <div class="app-layout">
    <!-- Collapsible Session Sidebar -->
    <aside id="session-sidebar" class="session-sidebar">
      <div class="sidebar-top">
        <div class="sidebar-nav-title">Navigation</div>
        <button class="sidebar-close-btn" onclick="toggleSessionSidebar()" title="Close sidebar"><span class="icon">{ICON_X}</span></button>
      </div>
      <nav class="sidebar-nav">
        <button class="sidebar-nav-item active" id="nav-tab-chat" onclick="switchTab('chat')"><span class="icon">{ICON_MESSAGE}</span><span>AI Chat</span></button>
        <button class="sidebar-nav-item" id="nav-tab-terminal" onclick="switchTab('terminal')"><span class="icon">{ICON_TERMINAL}</span><span>Web Terminal (ttyd)</span></button>
      </nav>
      <div class="sidebar-divider"></div>
      <div class="sidebar-remote-control-row remote-control-row">
        <div>
          <div class="remote-control-label">
            Remote Daemon
            <button type="button" class="remote-control-info-btn" onclick="toggleRemoteControlInfo(this)" title="How to connect remotely via web">{ICON_INFO}</button>
            <a class="remote-control-link-btn" href="https://antigravity.google.com" target="_blank" rel="noopener" title="Open remote access page (antigravity.google.com)">{ICON_EXTERNAL_LINK}</a>
          </div>
          <div class="remote-control-status" id="remote-control-status">Checking status...</div>
        </div>
        <label class="rc-toggle-switch toggle-disabled" id="remote-control-toggle">
          <input type="checkbox" id="remote-control-checkbox" onchange="onRemoteControlToggle(this)">
          <span class="toggle-track"><span class="toggle-thumb"></span></span>
        </label>
      </div>
      <div class="sidebar-divider"></div>
      <div class="sidebar-new-chat-wrap">
        <button class="new-chat-btn-sidebar" onclick="startNewSession()">
          <span class="icon icon-blue">{ICON_PLUS}</span>
          <span>Start new conversation</span>
          <span class="kbd-hint">Ctrl+K</span>
        </button>
      </div>
      <div class="sidebar-divider"></div>
      <div class="sidebar-section-title">
        <span id="session-list-title">Recent Conversations (0)</span>
        <button class="session-select-btn" id="session-select-btn" onclick="toggleSessionSelectMode()">Select</button>
      </div>
      <div id="session-list" class="session-list">
        <div class="session-loading">Loading sessions...</div>
      </div>
      <div class="sidebar-bottom-slot">
        <div class="session-select-toolbar" id="session-select-toolbar" style="display:none;">
          <button onclick="selectAllSessions()"><span id="session-select-all-label">Select All</span></button>
          <button class="session-delete-btn" id="session-delete-btn" onclick="deleteSelectedSessions()" disabled>
            <span class="icon">{ICON_TRASH}</span><span>Delete Selected (<span id="session-delete-count">0</span>)</span>
          </button>
        </div>
        <div class="sidebar-footer" id="sidebar-footer">0 sessions total</div>
      </div>
    </aside>

    <div class="sidebar-overlay" id="sidebar-overlay" onclick="toggleSessionSidebar()"></div>

    <main>
      <!-- Chat View -->
      <section id="chat-view" class="tab-view active">
        <!-- Top Pinned Resource Panel (Collapsible) -- scoped to the chat
             column (not the header/sidebar) so it never overlaps the
             session list, and the two can be open at the same time. -->
        <div id="top-resource-panel" class="top-resource-panel">
          <div class="panel-inner">
            <div class="panel-grid">
              <div class="chart-box">
                <div class="chart-top">
                  <span class="chart-title">⚙️ CPU</span>
                  <div class="chart-legend">
                    <span class="lg-item lg-purple">● Add-on <strong id="val-addon-cpu">0.0%</strong></span>
                    <span class="lg-item lg-blue">● System <strong id="val-sys-cpu">0.0%</strong></span>
                  </div>
                </div>
                <div class="canvas-holder">
                  <canvas id="cpu-dual-chart" width="460" height="75"></canvas>
                </div>
              </div>
              <div class="chart-box">
                <div class="chart-top">
                  <span class="chart-title">💾 RAM</span>
                  <div class="chart-legend">
                    <span class="lg-item lg-green">● Add-on <strong id="val-addon-ram">0MB (0%)</strong></span>
                    <span class="lg-item lg-cyan">● System <strong id="val-sys-ram">0GB (0%)</strong></span>
                  </div>
                </div>
                <div class="canvas-holder">
                  <canvas id="ram-dual-chart" width="460" height="75"></canvas>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="chat-container" id="chat-box">
          <div class="hero-card" id="chat-hero-card">
            <span class="hero-badge">Google Antigravity Engine</span>
            <h2>How can I help you?</h2>
            <p>Real-time AI assistant for Home Assistant smart home control and environmental analysis.</p>
            <div class="quick-grid" id="quick-grid"></div>
          </div>
        </div>
        <div class="pull-up-indicator" id="pull-up-indicator">
          <span class="pull-up-icon" id="pull-up-icon">⬆️</span>
          <span class="pull-up-text" id="pull-up-text">Pull up to refresh latest conversation</span>
        </div>
        <div class="input-bar-wrap">
          <div class="quota-banner" id="quota-banner" style="display:none;">
            <span class="quota-banner-icon">⚠️</span>
            <div class="quota-banner-body">
              <div class="quota-banner-title">Default Model Quota Exhausted</div>
              <div class="quota-banner-desc" id="quota-banner-desc"></div>
            </div>
            <button class="quota-banner-dismiss" onclick="dismissQuotaBanner()">Close</button>
          </div>
          <div class="composer" id="composer">
            <div class="attach-preview-row" id="attach-preview-row" style="display:none;"></div>
            <input type="file" id="attach-file-input" multiple accept=".py,.js,.ts,.java,.c,.cpp,.go,.rs,.sh,.bat,.ps1,.json,.yaml,.yml,.xml,.toml,.ini,.env,.csv,.tsv,.txt,.md,.pdf,.docx,.png,.jpg,.jpeg,.webp,.gif" style="display:none;" onchange="handleFilesSelected(event)">
            <textarea id="user-input" placeholder="Ask anything..." rows="1" oninput="updateSendBtn(); autoResizeTextarea(); updateSlashCommandMenu()" onkeydown="handleKey(event)" onblur="closeSlashCommandMenu()"></textarea>
            <div class="slash-command-menu" id="slash-command-menu"></div>
            <div class="composer-toolbar">
              <div class="composer-toolbar-left">
                <button class="attach-btn" id="attach-btn" onclick="triggerFileAttach()" title="Attach file or image (CLI Reasoning Mode only)"><span class="icon">{ICON_PLUS}</span></button>

                <div class="model-picker" id="stream-mode-picker">
                  <button class="mode-picker-btn" id="stream-mode-btn" onclick="toggleStreamModePicker()" title="Change Execution Mode">
                    <span class="icon" id="stream-mode-icon">{ICON_ZAP}</span>
                    <span id="stream-mode-current">Control</span>
                    <span class="icon icon-sm">{ICON_CHEVRON_DOWN}</span>
                  </button>
                  <div class="model-dropdown" id="stream-mode-dropdown">
                    <div class="model-dropdown-title">Execution Modes (Mode)</div>
                    <div id="stream-mode-list" class="model-dropdown-list"></div>
                  </div>
                </div>

                <div class="model-picker" id="model-picker">
                  <button class="mode-picker-btn model-picker-btn" id="model-picker-btn" onclick="toggleModelPicker()" title="Change Model and Thinking Effort">
                    <span class="icon icon-sm icon-dim">{ICON_PLUS}</span>
                    <span id="model-picker-current" class="model-picker-name">Select Model</span>
                    <span class="model-effort-tag" id="model-picker-effort" style="display:none;"></span>
                    <span class="usage-mini-ring model-picker-usage-ring" id="model-picker-usage-ring" style="display:none;"></span>
                    <span class="icon icon-sm">{ICON_CHEVRON_UP}</span>
                  </button>
                  <div class="model-dropdown" id="model-dropdown">
                    <div class="model-dropdown-title">Model</div>
                    <div id="model-dropdown-list" class="model-dropdown-list">
                      <div class="model-dropdown-loading">Loading models...</div>
                    </div>
                    <div class="usage-view-row" id="usage-view-row" onmouseenter="openUsagePanel()" onmouseleave="closeUsagePanel()">
                      <span><span class="icon icon-sm">{ICON_BAR_CHART}</span><span>View Usage</span></span>
                      <span class="icon icon-sm">{ICON_CHEVRON_RIGHT}</span>
                    </div>
                  </div>
                  <div class="usage-panel" id="usage-panel" onmouseenter="openUsagePanel()" onmouseleave="closeUsagePanel()">
                    <div class="usage-panel-loading">Loading usage...</div>
                  </div>
                </div>

                <div class="model-picker" id="agent-picker" style="display:none;">
                  <button class="mode-picker-btn model-picker-btn" id="agent-picker-btn" onclick="toggleAgentPicker()" title="Change Custom Agent">
                    <span class="icon icon-sm icon-dim">{ICON_USER}</span>
                    <span id="agent-picker-current" class="model-picker-name">Default agent</span>
                    <span class="icon icon-sm">{ICON_CHEVRON_UP}</span>
                  </button>
                  <div class="model-dropdown" id="agent-dropdown">
                    <div class="model-dropdown-title">Agent</div>
                    <div id="agent-dropdown-list" class="model-dropdown-list"></div>
                  </div>
                </div>
              </div>
              <div class="composer-toolbar-right">
                <button class="mic-btn" id="mic-btn" onclick="toggleRecording()" title="Ask with voice"><span class="icon">{ICON_MIC}</span></button>
                <button class="send-btn" id="send-btn" onclick="sendMessage()"><span class="icon">{ICON_ARROW_UP}</span></button>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Terminal View -->
      <section id="terminal-view" class="tab-view">
        <div id="terminal-confirm-overlay" class="terminal-confirm-overlay" style="display:none;">
          <div class="terminal-confirm-box">
            <p>Launch agy (Antigravity CLI)?</p>
            <div class="terminal-confirm-actions">
              <button class="terminal-confirm-yes" onclick="confirmRunAgy(true)">Yes</button>
              <button class="terminal-confirm-no" onclick="confirmRunAgy(false)">No</button>
            </div>
          </div>
        </div>
        <iframe id="terminal-iframe" src="./terminal/"></iframe>
      </section>
    </main>
  </div>
""".strip()
