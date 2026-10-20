"""ESPHome & Microcontroller Management Module.
Provides discovery of ESPHome device YAMLs, USB/Serial port inspection,
and non-blocking compilation and validation routines.
"""

from dataclasses import asdict, dataclass
import glob
import os
from pathlib import Path
import re
import shutil
import subprocess
from typing import Any, Dict, List, Optional


@dataclass
class ESPHomeDevice:
    name: str
    friendly_name: Optional[str]
    file_path: str
    file_name: str
    platform: str
    board: Optional[str]
    is_compiled: bool
    last_modified: float


def get_esphome_directory() -> Optional[Path]:
    """Resolve the ESPHome configuration directory."""
    candidates = [
        Path("/config/esphome"),
        Path("/homeassistant/esphome"),
        Path("esphome"),
        Path("/config"),
    ]
    for c in candidates:
        if c.exists() and c.is_dir():
            return c
    return None


def detect_usb_serial_ports() -> List[Dict[str, str]]:
    """Detect available USB-to-UART / Serial ports for ESP microcontrollers."""
    ports: List[Dict[str, str]] = []

    # 1. Inspect Linux /dev/serial/by-id/
    by_id_path = Path("/dev/serial/by-id")
    if by_id_path.exists():
        try:
            for item in by_id_path.iterdir():
                try:
                    resolved = str(item.resolve())
                    ports.append({
                        "path": str(item),
                        "resolved_path": resolved,
                        "description": item.name,
                    })
                except Exception:
                    pass
        except Exception:
            pass

    # 2. Inspect /dev/ttyUSB* and /dev/ttyACM*
    for pattern in ["/dev/ttyUSB*", "/dev/ttyACM*"]:
        for dev in glob.glob(pattern):
            if not any(p["resolved_path"] == dev for p in ports if "resolved_path" in p):
                ports.append({
                    "path": dev,
                    "resolved_path": dev,
                    "description": os.path.basename(dev),
                })

    return ports


def parse_esphome_yaml(yaml_path: Path) -> Optional[ESPHomeDevice]:
    """Extract metadata from an ESPHome YAML file without executing full external compiler."""
    try:
        content = yaml_path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return None

    # Verify it looks like an ESPHome config
    if "esphome:" not in content and not yaml_path.parent.name == "esphome":
        return None

    name = yaml_path.stem
    friendly_name = None
    platform = "esp32"
    board = None

    # Regex extractions
    m_name = re.search(r"^\s*name:\s*[\"']?([a-zA-Z0-9_\-]+)[\"']?", content, re.MULTILINE)
    if m_name:
        name = m_name.group(1)

    m_friendly = re.search(r"^\s*friendly_name:\s*[\"']?([^\"'\n]+)[\"']?", content, re.MULTILINE)
    if m_friendly:
        friendly_name = m_friendly.group(1).strip()

    if "esp8266:" in content:
        platform = "esp8266"
        m_board = re.search(r"^\s*board:\s*[\"']?([a-zA-Z0-9_\-]+)[\"']?", content, re.MULTILINE)
        if m_board:
            board = m_board.group(1)
    elif "esp32:" in content:
        platform = "esp32"
        m_board = re.search(r"^\s*board:\s*[\"']?([a-zA-Z0-9_\-]+)[\"']?", content, re.MULTILINE)
        if m_board:
            board = m_board.group(1)
    elif "rp2040:" in content:
        platform = "rp2040"

    # Check compilation build artifacts
    build_dir = yaml_path.parent / ".esphome" / "build" / name
    is_compiled = build_dir.exists() and any(build_dir.glob("*.bin"))

    stat = yaml_path.stat()
    return ESPHomeDevice(
        name=name,
        friendly_name=friendly_name,
        file_path=str(yaml_path),
        file_name=yaml_path.name,
        platform=platform,
        board=board,
        is_compiled=is_compiled,
        last_modified=stat.st_mtime,
    )


def discover_esphome_devices() -> List[Dict[str, Any]]:
    """Scan and return all ESPHome device configurations."""
    esphome_dir = get_esphome_directory()
    if not esphome_dir:
        return []

    devices: List[Dict[str, Any]] = []
    # Ignore secrets, packages, components
    ignore_files = {"secrets.yaml", "common.yaml", "base.yaml"}

    for yaml_file in esphome_dir.glob("*.yaml"):
        if yaml_file.name.lower() in ignore_files or yaml_file.name.startswith("."):
            continue
        dev = parse_esphome_yaml(yaml_file)
        if dev:
            devices.append(asdict(dev))

    return sorted(devices, key=lambda d: d["name"])


def find_device_config(target: str) -> Optional[Path]:
    """Find the YAML configuration file for a given device name or filename."""
    esphome_dir = get_esphome_directory()
    if not esphome_dir:
        return None

    # Check exact match
    clean_target = target.strip()
    if not clean_target.endswith(".yaml"):
        clean_target += ".yaml"

    direct_path = esphome_dir / clean_target
    if direct_path.exists():
        return direct_path

    # Check by device name
    for yf in esphome_dir.glob("*.yaml"):
        dev = parse_esphome_yaml(yf)
        if dev and (dev.name.lower() == target.lower() or yf.stem.lower() == target.lower()):
            return yf

    return None


def validate_esphome_config(target: str, timeout: int = 40) -> Dict[str, Any]:
    """Run `esphome config <target>` and return parsed results."""
    yaml_path = find_device_config(target)
    if not yaml_path:
        return {
            "ok": False,
            "error": f"Ficheiro de configuração para '{target}' não foi encontrado na pasta esphome.",
            "output": "",
        }

    esphome_bin = shutil.which("esphome") or "esphome"
    try:
        proc = subprocess.run(
            [esphome_bin, "config", str(yaml_path)],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "ok": proc.returncode == 0,
            "file": str(yaml_path),
            "output": proc.stdout if proc.returncode == 0 else proc.stderr or proc.stdout,
            "returncode": proc.returncode,
        }
    except subprocess.TimeoutExpired:
        return {
            "ok": False,
            "error": f"Tempo limite ({timeout}s) excedido ao validar {yaml_path.name}.",
            "output": "",
        }
    except Exception as e:
        return {
            "ok": False,
            "error": f"Falha ao executar validação esphome: {str(e)}",
            "output": "",
        }


def compile_esphome_firmware(target: str, timeout: int = 180) -> Dict[str, Any]:
    """Run `esphome compile <target>` and return status."""
    yaml_path = find_device_config(target)
    if not yaml_path:
        return {
            "ok": False,
            "error": f"Ficheiro de configuração para '{target}' não foi encontrado.",
            "output": "",
        }

    esphome_bin = shutil.which("esphome") or "esphome"
    try:
        proc = subprocess.run(
            [esphome_bin, "compile", str(yaml_path)],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "ok": proc.returncode == 0,
            "file": str(yaml_path),
            "output": proc.stdout if proc.returncode == 0 else proc.stderr or proc.stdout,
            "returncode": proc.returncode,
        }
    except subprocess.TimeoutExpired:
        return {
            "ok": False,
            "error": f"Tempo limite ({timeout}s) excedido ao compilar {yaml_path.name}.",
            "output": "",
        }
    except Exception as e:
        return {
            "ok": False,
            "error": f"Falha ao executar compilação esphome: {str(e)}",
            "output": "",
        }


def format_esphome_overview_markdown(is_pt: bool = True) -> str:
    """Format a clean markdown report of ESPHome devices and serial ports."""
    devices = discover_esphome_devices()
    serial_ports = detect_usb_serial_ports()
    esphome_installed = bool(shutil.which("esphome"))
    esptool_installed = bool(shutil.which("esptool.py") or shutil.which("esptool"))

    if is_pt:
        title = "### ⚡ Painel de Gestão ESPHome & Microcontroladores"
        tooling_hdr = "#### 🛠️ Estado dos Utilitários"
        ports_hdr = "#### 🔌 Portas USB / Serial Detetadas"
        devs_hdr = "#### 📱 Dispositivos ESPHome Configurados"
        empty_ports = "*(Nenhuma porta USB/Serial detetada)*"
        empty_devs = "*(Nenhum ficheiro .yaml encontrado em /config/esphome/)*"
        help_text = (
            "**Comandos disponíveis no chat:**\n"
            "- `/esphome list`: Lista dispositivos e portas detetadas\n"
            "- `/esphome validate <nome>`: Valida a sintaxe de um ficheiro .yaml\n"
            "- `/esphome compile <nome>`: Compila o firmware do dispositivo"
        )
    else:
        title = "### ⚡ ESPHome & Microcontroller Dashboard"
        tooling_hdr = "#### 🛠️ Tooling Status"
        ports_hdr = "#### 🔌 Detected USB / Serial Ports"
        devs_hdr = "#### 📱 Configured ESPHome Devices"
        empty_ports = "*(No USB/Serial ports detected)*"
        empty_devs = "*(No .yaml files found in /config/esphome/)*"
        help_text = (
            "**Available chat commands:**\n"
            "- `/esphome list`: List devices and detected ports\n"
            "- `/esphome validate <name>`: Validate configuration syntax of a .yaml file\n"
            "- `/esphome compile <name>`: Compile device firmware"
        )

    parts = [
        title,
        "",
        tooling_hdr,
        f"- **ESPHome CLI:** {'✅ Instalado' if esphome_installed else '⚪ Não encontrado no PATH'}",
        f"- **ESPTool:** {'✅ Instalado' if esptool_installed else '⚪ Não encontrado no PATH'}",
        "",
        ports_hdr,
    ]

    if serial_ports:
        for p in serial_ports:
            parts.append(f"- **`{p['path']}`** ({p.get('description', '')})")
    else:
        parts.append(empty_ports)

    parts.append("")
    parts.append(devs_hdr)

    if devices:
        for d in devices:
            fname = f" ({d['friendly_name']})" if d.get("friendly_name") else ""
            status = "🟢 Compilado" if d.get("is_compiled") else "⚪ Não compilado"
            board_info = f" · `{d.get('board') or d.get('platform')}`"
            parts.append(f"- **`{d['name']}`**{fname}{board_info} — {status}")
    else:
        parts.append(empty_devs)

    parts.append("")
    parts.append(help_text)
    return "\n".join(parts)
