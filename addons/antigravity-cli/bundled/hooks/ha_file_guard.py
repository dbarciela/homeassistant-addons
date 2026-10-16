#!/usr/bin/env python3
"""PreToolUse hook: hard-block deletion/overwrite of Home Assistant's
critical config data (see run.sh's ha-file-safety.md for the same list in
rule-instruction form -- this is the enforced counterpart, matched on
run_command's shell command line and on write_to_file/replace_file_content's
target path).

Payload shape and decision contract per antigravity.google/docs/hooks/:
    stdin:  {"toolCall": {"name": ..., "args": {...}}, ...}
    stdout: {"decision": "allow"} | {"decision": "deny", "reason": "..."}
"""
import json
import re
import sys

PROTECTED = [
    ("/homeassistant/.storage", ".storage registry (entity/device/user accounts core HA state)"),
    ("/homeassistant/secrets.yaml", "sensitive credentials (passwords/tokens) file"),
    ("/homeassistant/configuration.yaml", "HA main configuration file"),
    ("/homeassistant/.uuid", "unique identifier for this HA instance"),
    ("/homeassistant/.HA_VERSION", "internal version marker"),
    ("/homeassistant/home-assistant_v2.db", "recorder history and logbook database"),
    ("/homeassistant/.cloud", "Nabu Casa Cloud auth token"),
    ("/config/.gemini", "Antigravity CLI configuration, auth, and session history"),
    ("/homeassistant/automations.yaml", "user automation definitions"),
    ("/homeassistant/scripts.yaml", "user script definitions"),
    ("/homeassistant/scenes.yaml", "user scene definitions"),
    ("/homeassistant/custom_components", "installed custom integrations (HACS, etc.)"),
    ("/backup", "Home Assistant backup archives"),
]

# A protected path substring alone isn't enough (plain `cat`/`ls`/`grep` must
# stay unblocked) -- only deny when a destructive verb/redirect is also
# present. `>` (but not `>>`, which only appends) covers truncate-by-redirect.
_DESTRUCTIVE_RE = re.compile(r"(?:^|[\s;&|])(rm|unlink|shred|truncate|mv)\b|(?<!>)>(?!>)")


def _unwrap(value):
    """agy has been observed double-JSON-encoding string tool-call args for
    some fields (confirmed for AbsolutePath/CodeContent/TargetContent in
    transcript.jsonl -- see core/streamer.py _agy_str()). This hook gets its
    payload from a separate, first-class stdin contract that may or may not
    share the quirk, so unwrap defensively either way -- a plain unquoted
    path string just fails json.loads and falls through unchanged."""
    if not isinstance(value, str):
        return value
    try:
        unwrapped = json.loads(value)
        if isinstance(unwrapped, str):
            return unwrapped
    except Exception:
        pass
    return value


def _deny(path, why):
    print(json.dumps({
        "decision": "deny",
        "reason": (
            f"[HA File Protection] '{path}' is critical Home Assistant operational data ({why}). "
            "Under this add-on's safety policy, deletion or overwriting is strictly blocked for all requests. "
            "Inform the user of this protection and the associated risks. If this change is truly necessary, "
            "guide them to use Home Assistant's native backup/restore or the official configuration UI."
        ),
    }, ensure_ascii=False))


def _allow():
    print(json.dumps({"decision": "allow"}))


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        _allow()
        return

    tool_call = payload.get("toolCall") or {}
    name = tool_call.get("name", "")
    args = tool_call.get("args")
    if isinstance(args, str):
        args = _unwrap(args)
        if isinstance(args, str):
            try:
                args = json.loads(args)
            except Exception:
                args = {}
    if not isinstance(args, dict):
        args = {}

    if name == "run_command":
        cmd = _unwrap(args.get("CommandLine", "")) or ""
        if _DESTRUCTIVE_RE.search(cmd):
            for path, why in PROTECTED:
                if path in cmd:
                    _deny(path, why)
                    return
        _allow()
        return

    if name in ("write_to_file", "replace_file_content"):
        target = _unwrap(args.get("AbsolutePath", "")) or ""
        for path, why in PROTECTED:
            if target == path or target.startswith(path.rstrip("/") + "/"):
                _deny(path, why)
                return
        _allow()
        return

    _allow()


if __name__ == "__main__":
    main()
