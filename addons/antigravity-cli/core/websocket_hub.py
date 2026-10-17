"""Centralized Real-Time WebSocket Event Hub for Antigravity Dual Ingress.

Provides an RFC 6455 compliant WebSocket server without external dependencies.
Broadcasts real-time telemetry (CPU, RAM, Uptime), Google Auth transitions,
Remote Daemon state changes, and system alerts directly to connected Web UI clients,
eliminating aggressive HTTP polling.
"""

import base64
import hashlib
import json
import select
import socket
import struct
import sys
import threading
import time
from typing import Dict, Optional, Set

from core.ui import UI_BUILD_VERSION


def _compute_accept_key(sec_key: str) -> str:
    """Compute the Sec-WebSocket-Accept key per RFC 6455."""
    guid = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
    accept_src = (sec_key.strip() + guid).encode("utf-8")
    return base64.b64encode(hashlib.sha1(accept_src).digest()).decode("utf-8")


def _encode_frame(opcode: int, payload: bytes) -> bytes:
    """Encode an RFC 6455 frame from server to client (unmasked)."""
    length = len(payload)
    if length <= 125:
        header = bytes([0x80 | (opcode & 0x0F), length])
    elif length <= 65535:
        header = struct.pack("!BBH", 0x80 | (opcode & 0x0F), 126, length)
    else:
        header = struct.pack("!BBQ", 0x80 | (opcode & 0x0F), 127, length)
    return header + payload


def _decode_frame(data: bytes):
    """Decode a masked RFC 6455 frame from client to server."""
    if len(data) < 2:
        return None, b"", 0
    byte1, byte2 = data[0], data[1]
    opcode = byte1 & 0x0F
    is_masked = (byte2 & 0x80) != 0
    payload_len = byte2 & 0x7F
    offset = 2
    if payload_len == 126:
        if len(data) < 4:
            return None, b"", 0
        payload_len = struct.unpack("!H", data[offset:offset + 2])[0]
        offset += 2
    elif payload_len == 127:
        if len(data) < 10:
            return None, b"", 0
        payload_len = struct.unpack("!Q", data[offset:offset + 8])[0]
        offset += 8

    if is_masked:
        if len(data) < offset + 4 + payload_len:
            return None, b"", 0
        mask = data[offset:offset + 4]
        offset += 4
        raw = data[offset:offset + payload_len]
        payload = bytes([b ^ mask[i % 4] for i, b in enumerate(raw)])
    else:
        if len(data) < offset + payload_len:
            return None, b"", 0
        payload = data[offset:offset + payload_len]

    total_consumed = offset + payload_len
    return opcode, payload, total_consumed


class WebSocketHub:
    """Central event hub managing WebSocket connections and telemetry pushes."""

    def __init__(self):
        self._clients: Set[socket.socket] = set()
        self._lock = threading.Lock()
        self._telemetry_thread: Optional[threading.Thread] = None
        self._running = True
        self._last_telemetry: Dict = {}

    def get_client_count(self) -> int:
        with self._lock:
            return len(self._clients)

    def register_client(self, client_sock: socket.socket):
        with self._lock:
            self._clients.add(client_sock)
        # Send initial welcome and current snapshot immediately
        self._send_to_client(client_sock, "welcome", {
            "version": UI_BUILD_VERSION,
            "connected_at": time.time(),
            "message": "Connected to Antigravity Real-time Event Hub",
        })
        if self._last_telemetry:
            self._send_to_client(client_sock, "telemetry", self._last_telemetry)

    def unregister_client(self, client_sock: socket.socket):
        with self._lock:
            self._clients.discard(client_sock)
        try:
            client_sock.close()
        except Exception:
            pass

    def _send_to_client(self, client_sock: socket.socket, event_type: str, data: dict) -> bool:
        """Send a single JSON event to a specific client socket."""
        try:
            payload = json.dumps({"event": event_type, "data": data}, ensure_ascii=False).encode("utf-8")
            frame = _encode_frame(0x1, payload)
            client_sock.sendall(frame)
            return True
        except Exception:
            return False

    def broadcast(self, event_type: str, data: dict):
        """Broadcast an event to all connected clients."""
        with self._lock:
            if not self._clients:
                return
            current_clients = list(self._clients)

        payload = json.dumps({"event": event_type, "data": data}, ensure_ascii=False).encode("utf-8")
        frame = _encode_frame(0x1, payload)

        disconnected = []
        for sock in current_clients:
            try:
                sock.sendall(frame)
            except Exception:
                disconnected.append(sock)

        if disconnected:
            with self._lock:
                for sock in disconnected:
                    self._clients.discard(sock)
                    try:
                        sock.close()
                    except Exception:
                        pass

    def handle_client_connection(self, sock: socket.socket, headers: dict):
        """Perform WebSocket handshake and manage client lifecycle."""
        sec_key = headers.get("Sec-WebSocket-Key") or headers.get("sec-websocket-key")
        if not sec_key:
            try:
                sock.sendall(b"HTTP/1.1 400 Bad Request\r\n\r\nMissing Sec-WebSocket-Key")
                sock.close()
            except Exception:
                pass
            return

        accept_val = _compute_accept_key(sec_key)
        handshake_resp = (
            "HTTP/1.1 101 Switching Protocols\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Accept: {accept_val}\r\n"
            "\r\n"
        ).encode("utf-8")

        try:
            sock.sendall(handshake_resp)
        except Exception:
            try:
                sock.close()
            except Exception:
                pass
            return

        self.register_client(sock)
        sock.setblocking(False)

        buffer = bytearray()
        last_ping = time.time()

        try:
            while self._running:
                # Periodic keep-alive ping frame every 20 seconds
                now = time.time()
                if now - last_ping >= 20.0:
                    try:
                        sock.sendall(_encode_frame(0x9, b"heartbeat"))
                        last_ping = now
                    except Exception:
                        break

                r, _, x = select.select([sock], [], [sock], 1.0)
                if x:
                    break
                if r:
                    try:
                        chunk = sock.recv(4096)
                        if not chunk:
                            break
                        buffer.extend(chunk)
                    except (BlockingIOError, InterruptedError):
                        continue
                    except Exception:
                        break

                    while len(buffer) >= 2:
                        opcode, payload, consumed = _decode_frame(bytes(buffer))
                        if opcode is None or consumed == 0:
                            break
                        buffer = buffer[consumed:]

                        if opcode == 0x8:  # Connection close
                            try:
                                sock.sendall(_encode_frame(0x8, payload))
                            except Exception:
                                pass
                            return
                        elif opcode == 0x9:  # Ping from client
                            try:
                                sock.sendall(_encode_frame(0xA, payload))  # Pong
                            except Exception:
                                pass
                        elif opcode == 0x1:  # Text frame from client
                            try:
                                text = payload.decode("utf-8")
                                msg = json.loads(text)
                                if msg.get("action") == "ping":
                                    self._send_to_client(sock, "pong", {"timestamp": time.time()})
                            except Exception:
                                pass
        finally:
            self.unregister_client(sock)

    def start_telemetry_loop(self, get_telemetry_fn):
        """Start background daemon thread that gathers telemetry and broadcasts."""
        if self._telemetry_thread and self._telemetry_thread.is_alive():
            return

        def _loop():
            while self._running:
                time.sleep(3.0)
                if self.get_client_count() == 0:
                    continue
                try:
                    telemetry = get_telemetry_fn()
                    if telemetry:
                        self._last_telemetry = telemetry
                        self.broadcast("telemetry", telemetry)
                except Exception as e:
                    print(f"[WebSocketHub] Telemetry error: {e}", file=sys.stderr)

        self._telemetry_thread = threading.Thread(target=_loop, daemon=True, name="WebSocketTelemetry")
        self._telemetry_thread.start()


# Global Singleton
_HUB_INSTANCE: Optional[WebSocketHub] = None
_HUB_LOCK = threading.Lock()


def get_websocket_hub() -> WebSocketHub:
    """Retrieve global WebSocketHub singleton."""
    global _HUB_INSTANCE
    with _HUB_LOCK:
        if _HUB_INSTANCE is None:
            _HUB_INSTANCE = WebSocketHub()
        return _HUB_INSTANCE


def broadcast_event(event_type: str, data: dict):
    """Convenience helper to broadcast an event across all WebSocket clients."""
    hub = get_websocket_hub()
    hub.broadcast(event_type, data)
