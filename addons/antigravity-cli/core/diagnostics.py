"""Home Assistant Log Diagnostics and Health Analysis Module.
Provides non-blocking log parsing, error extraction, integration grouping,
and actionable troubleshooting recommendations.
"""

from dataclasses import asdict, dataclass
import os
from pathlib import Path
import re
from typing import Any, Dict, List, Optional


@dataclass
class LogEntry:
    timestamp: str
    level: str
    thread: str
    component: str
    message: str
    traceback: Optional[str] = None


@dataclass
class DiagnosticsSummary:
    log_file: str
    total_lines_analyzed: int
    error_count: int
    warning_count: int
    traceback_count: int
    top_components_with_errors: List[Dict[str, Any]]
    offline_entities_detected: List[str]
    recent_errors: List[Dict[str, Any]]
    recommendations: List[str]


LOG_ENTRY_PATTERN = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}(?:\.\d+)?)\s+"
    r"(?P<level>[A-Z]+)\s+"
    r"\((?P<thread>[^)]+)\)\s+"
    r"\[(?P<component>[^\]]+)\]\s+"
    r"(?P<message>.*)$"
)

ENTITY_OFFLINE_PATTERNS = [
    re.compile(r"entity\s+['\"]?([a-z0-9_]+\.[a-z0-9_]+)['\"]?\s+is\s+(?:unavailable|not\s+found|offline)", re.IGNORECASE),
    re.compile(r"unable\s+to\s+(?:find|update|fetch)\s+entity\s+['\"]?([a-z0-9_]+\.[a-z0-9_]+)['\"]?", re.IGNORECASE),
    re.compile(r"failed\s+to\s+call\s+service\s+for\s+['\"]?([a-z0-9_]+\.[a-z0-9_]+)['\"]?", re.IGNORECASE),
    re.compile(r"device\s+['\"]?([a-z0-9_]+\.[a-z0-9_]+)['\"]?\s+disconnected", re.IGNORECASE),
]


def get_ha_log_path() -> Optional[Path]:
    """Resolve the active Home Assistant log file path."""
    env_path = os.environ.get("HA_LOG_FILE")
    if env_path and os.path.exists(env_path):
        return Path(env_path)

    candidates = [
        Path("/config/home-assistant.log"),
        Path("/homeassistant/home-assistant.log"),
        Path("home-assistant.log"),
        Path("../home-assistant.log"),
    ]
    for c in candidates:
        if c.exists() and c.is_file():
            return c
    return None


def read_tail_lines(file_path: Path, max_lines: int = 200, chunk_size: int = 8192) -> List[str]:
    """Read the last `max_lines` from a file efficiently without reading the entire file."""
    if not file_path.exists():
        return []

    lines: List[str] = []
    try:
        with open(file_path, "rb") as f:
            f.seek(0, os.SEEK_END)
            file_size = f.tell()
            buffer = bytearray()
            pos = file_size

            while pos > 0 and len(lines) <= max_lines:
                read_len = min(chunk_size, pos)
                pos -= read_len
                f.seek(pos)
                chunk = f.read(read_len)
                buffer = chunk + buffer
                lines = buffer.decode("utf-8", errors="replace").splitlines()

            return lines[-max_lines:]
    except Exception:
        # Fallback to standard reading if seek fails
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                all_lines = f.readlines()
                return [l.rstrip("\r\n") for l in all_lines[-max_lines:]]
        except Exception:
            return []


def parse_log_lines(raw_lines: List[str]) -> List[LogEntry]:
    """Parse raw log lines into structured LogEntry items with multiline traceback collation."""
    entries: List[LogEntry] = []
    current_entry: Optional[LogEntry] = None
    current_traceback: List[str] = []

    for line in raw_lines:
        match = LOG_ENTRY_PATTERN.match(line)
        if match:
            if current_entry:
                if current_traceback:
                    current_entry.traceback = "\n".join(current_traceback).strip()
                entries.append(current_entry)
                current_traceback = []

            current_entry = LogEntry(
                timestamp=match.group("timestamp"),
                level=match.group("level"),
                thread=match.group("thread"),
                component=match.group("component"),
                message=match.group("message"),
                traceback=None,
            )
        else:
            # Continuation line or traceback stack trace
            if current_entry:
                current_traceback.append(line)

    if current_entry:
        if current_traceback:
            current_entry.traceback = "\n".join(current_traceback).strip()
        entries.append(current_entry)

    return entries


def analyze_home_assistant_logs(max_lines: int = 500) -> Dict[str, Any]:
    """Analyze recent Home Assistant logs and generate a structured diagnostic summary."""
    log_path = get_ha_log_path()
    if not log_path:
        return asdict(
            DiagnosticsSummary(
                log_file="Not found (/config/home-assistant.log)",
                total_lines_analyzed=0,
                error_count=0,
                warning_count=0,
                traceback_count=0,
                top_components_with_errors=[],
                offline_entities_detected=[],
                recent_errors=[],
                recommendations=["O ficheiro de log do Home Assistant não foi detetado em /config/home-assistant.log."],
            )
        )

    raw_lines = read_tail_lines(log_path, max_lines=max_lines)
    entries = parse_log_lines(raw_lines)

    error_count = 0
    warning_count = 0
    traceback_count = 0
    component_error_map: Dict[str, int] = {}
    offline_entities: set[str] = set()
    recent_errors: List[Dict[str, Any]] = []

    for entry in entries:
        if entry.level == "ERROR":
            error_count += 1
            component_error_map[entry.component] = component_error_map.get(entry.component, 0) + 1
            if len(recent_errors) < 10:
                recent_errors.append({
                    "timestamp": entry.timestamp,
                    "component": entry.component,
                    "message": entry.message,
                    "has_traceback": bool(entry.traceback),
                    "traceback_snippet": entry.traceback[:300] if entry.traceback else None,
                })
        elif entry.level == "WARNING":
            warning_count += 1

        if entry.traceback:
            traceback_count += 1

        # Search for offline entities in messages
        combined_text = f"{entry.message} {entry.traceback or ''}"
        for pattern in ENTITY_OFFLINE_PATTERNS:
            for m in pattern.finditer(combined_text):
                offline_entities.add(m.group(1))

    # Sort components by error count
    sorted_components = sorted(component_error_map.items(), key=lambda x: x[1], reverse=True)
    top_components = [{"component": c, "error_count": count} for c, count in sorted_components[:5]]

    # Generate actionable recommendations
    recommendations: List[str] = []
    if error_count == 0 and warning_count == 0:
        recommendations.append("✅ O Home Assistant está a funcionar sem erros ou avisos recentes no log.")
    else:
        for comp, count in sorted_components[:3]:
            if "custom_components" in comp or "hacs" in comp:
                recommendations.append(
                    f"⚠️ **{comp}** gerou {count} erro(s): Verificar compatibilidade ou atualizações pendentes no HACS."
                )
            elif "esphome" in comp:
                recommendations.append(
                    f"⚡ **ESPHome**: {count} erro(s) detetados. Verificar conectividade Wi-Fi ou portas USB dos microcontroladores."
                )
            elif "mqtt" in comp or "zigbee" in comp:
                recommendations.append(
                    f"📡 **{comp}**: {count} erro(s). Verificar se o broker MQTT ou coordenador Zigbee está operacional."
                )
            elif "recorder" in comp or "database" in comp:
                recommendations.append(
                    f"💾 **Base de Dados/Recorder**: Erros detetados. Verificar integridade do ficheiro home-assistant_v2.db."
                )
            else:
                recommendations.append(
                    f"🔍 **{comp}**: {count} erro(s). Inspecione a configuração YAML ou credenciais do componente."
                )

        if offline_entities:
            recommendations.append(
                f"🔌 **Entidades Indisponíveis**: Detetadas {len(offline_entities)} entidade(s) com falhas de comunicação."
            )

    summary = DiagnosticsSummary(
        log_file=str(log_path),
        total_lines_analyzed=len(raw_lines),
        error_count=error_count,
        warning_count=warning_count,
        traceback_count=traceback_count,
        top_components_with_errors=top_components,
        offline_entities_detected=sorted(list(offline_entities))[:15],
        recent_errors=recent_errors,
        recommendations=recommendations,
    )
    return asdict(summary)


def format_diagnostics_markdown(data: Dict[str, Any], is_pt: bool = True) -> str:
    """Format diagnostic analysis data into a clean, GitHub-flavored markdown report."""
    err_count = data.get("error_count", 0)
    warn_count = data.get("warning_count", 0)
    tb_count = data.get("traceback_count", 0)
    lines_analyzed = data.get("total_lines_analyzed", 0)
    log_file = data.get("log_file", "Desconhecido")

    if is_pt:
        title = "### 🩺 Relatório de Diagnóstico do Home Assistant"
        status_line = (
            f"**Ficheiro analisado:** `{log_file}` ({lines_analyzed} linhas)\n"
            f"- **Erros (ERROR):** {err_count}\n"
            f"- **Avisos (WARNING):** {warn_count}\n"
            f"- **Exceções (Tracebacks):** {tb_count}"
        )
        comp_header = "#### 📊 Componentes com Mais Erros"
        comp_empty = "*Nenhum erro de componente detetado.*"
        offline_header = "#### 🔌 Entidades Offline ou com Falhas"
        rec_header = "#### 💡 Recomendações e Ações Corretivas"
    else:
        title = "### 🩺 Home Assistant Diagnostics Report"
        status_line = (
            f"**Analyzed file:** `{log_file}` ({lines_analyzed} lines)\n"
            f"- **Errors (ERROR):** {err_count}\n"
            f"- **Warnings (WARNING):** {warn_count}\n"
            f"- **Exceptions (Tracebacks):** {tb_count}"
        )
        comp_header = "#### 📊 Top Failing Components"
        comp_empty = "*No component errors detected.*"
        offline_header = "#### 🔌 Offline or Failing Entities"
        rec_header = "#### 💡 Recommendations & Corrective Actions"

    parts = [title, "", status_line, ""]

    # Top components
    top_comps = data.get("top_components_with_errors", [])
    if top_comps:
        parts.append(comp_header)
        for c in top_comps:
            parts.append(f"- **`{c['component']}`**: {c['error_count']} erro(s)")
        parts.append("")
    else:
        parts.append(comp_header)
        parts.append(comp_empty)
        parts.append("")

    # Offline entities
    offline = data.get("offline_entities_detected", [])
    if offline:
        parts.append(offline_header)
        for ent in offline:
            parts.append(f"- `{ent}`")
        parts.append("")

    # Recommendations
    recs = data.get("recommendations", [])
    if recs:
        parts.append(rec_header)
        for r in recs:
            parts.append(f"- {r}")
        parts.append("")

    return "\n".join(parts)
