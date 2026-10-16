# Antigravity CLI Communication Specification (Session-Aware Baseline v2.4)

> **Status: Actively Maintained (LOCKED)**
> **Baseline Commit: `1fd3b01` Session Resume Specification Implementation (`feature/session-resume-v2`)**
> **Mandatory Rule:** This specification and its communication interfaces must not be arbitrarily modified without reference to official documentation and prior user approval.
> **Official Docs**: https://antigravity.google/docs/cli/conversations , https://antigravity.google/docs/cli/headless (Verified 2026-08-31). `agy --help` (installed binary, v1.1.22) is the authoritative source for CLI flag names.

---

## 1. Overview
Defines the HTTP/SSE communication and session resumption (Resume) specifications between the Home Assistant add-on backend (`addons/antigravity-cli`) and the frontend / integration components.

This document reflects the reimplementation based on `main` (commit `1fd3b01`), created after the earlier v2.1 attempt (`feature/integrate-react-webui`) was discarded for breaking real-time stream-json communication in Mode 3 (Antigravity CLI headless). Refer to [Section 3: Mandatory Constraints](#3-mandatory-constraints) for required technical boundaries.

---

## 2. API Endpoint Specifications

### 1) POST `/api/chat` (or `/api/prompt`)
- **Description**: Real-time conversation and streaming device control endpoint
- **Content-Type**: `application/json`
- **Response Content-Type**: `text/event-stream; charset=utf-8`

#### [Request Payload]
```json
{
  "prompt": "Turn on the living room light",
  "stream_mode": 1,
  "conversation_id": "optional-uuid",
  "is_direct_llm": false,
  "is_mobile": false
}
```
- `stream_mode`:
  - `1`: AI Deep Brain / Environmental Analysis (sensor analysis and advice)
  - `2`: Ultra-Fast Smart Home Control (0.05s fast device control)
  - `3`: Antigravity CLI v2.0 Headless Agent (autonomous coding / deep agent)
- `conversation_id`: (Optional) Provide to continue an existing session. If omitted, a new ID is issued.

#### [SSE Response Stream Events]
All events are sent in `data: <JSON>\n\n` format.

1. **`session_init` event** (notifies session ID on the first line of the stream):
   ```json
   {"type": "session_init", "content": "2938460a-218d-48ad-9e24-6d95217e87f9"}
   ```
2. **`tool` / `live_log` event** (progress updates / tool execution logs):
   ```json
   {"type": "tool", "content": "⚡ [Mode 2: Fast Smart Home] Fast discovery of devices and entity states"}
   ```
3. **`chunk` / `text` event** (final response text streaming):
   ```json
   {"type": "text", "content": "🏠 Turned on living room lights."}
   ```
4. **`done` event** (stream termination and metrics):
   ```json
   {"type": "done", "tokens": {"input": 48, "output": 120, "total": 168, "speed_tps": 450.0, "elapsed": 0.05}}
   ```

When `result.status` is not `"SUCCESS"` (possible official values: `SUCCESS`, `ERROR`, `CANCELED`, `INTERRUPTED`, `INVALID`, `WAITING`, `RUNNING` — e.g., `ERROR` when quota is exceeded), the stream closes normally, but an error message is first transmitted via a `chunk` event before `done`. The stream never terminates with an empty `done` event.

---

### 2) GET `/api/sessions`
- **Description**: List previous conversation sessions
- **Response**: `application/json`
```json
{
  "sessions": [
    {
      "conversation_id": "2938460a-218d-48ad-9e24-6d95217e87f9",
      "title": "Turn on living room lights",
      "turns": 6,
      "last_message": "📊 [AI Environment] Living room CO2 is 650ppm...",
      "updated_at": "2026-08-31T12:07:56+09:00",
      "timestamp": 1788145676.0
    }
  ]
}
```

---

### 3) GET `/api/sessions/<conversation_id>`
- **Description**: Retrieve full message history and tool call records for a specific session
- **Response**: `application/json`
```json
{
  "conversation_id": "2938460a-218d-48ad-9e24-6d95217e87f9",
  "history": [
    {"step_index": 1, "type": "USER_INPUT", "content": "Turn on living room lights"},
    {"step_index": 2, "type": "PLANNER_RESPONSE", "thinking": "...", "tool_calls": [...]},
    {"step_index": 3, "type": "PLANNER_RESPONSE", "content": "💡 Successfully turned on living room lights."}
  ]
}
```

---

## 3. Mandatory Constraints

When maintaining `core/session_manager.py` / `core/streamer.py`, the following rules must be observed to prevent breaking Mode 3 real-time communication:

1. **The CLI flag for resuming sessions is `--conversation <id>`. There is no `--resume` flag.**
   `agy --help` (v1.1.22) defines `--conversation` ("Resume a previous conversation by ID") and `--continue`/`-c` ("Continue the most recent conversation"). Earlier code assumed `--resume <id>`, which was undocumented and unreliable. Always use `--conversation`.
2. **Never tail existing transcript files from offset 0 when resuming.**
   `tail_transcript()` in `stream_headless_cli()` must execute `file_obj.seek(0, os.SEEK_END)` immediately upon opening resumed sessions. Otherwise, past turns will replay onto the live stream as if they occurred just now.
3. **Unicode decoding must target exact `\uXXXX` literals via regex.**
   Using `.encode("utf-8").decode("unicode_escape")` on full strings corrupts valid UTF-8 characters. Localized replacement matching `re.sub(r"\\u[0-9a-fA-F]{4}", ...)` must be used.
4. **`transcript.jsonl` (`.system_generated/logs/transcript.jsonl`) is the single cumulative source of truth.**
   Modes 1 and 2 write directly to this file, and Mode 3 (`agy`) accumulates all resumed turns into it. Conversely, `transcript_full/00000000.jsonl` is agy's initial snapshot and only contains turn 1; it is never updated on resume.
5. **Never ignore non-SUCCESS `result.status` from `agy`.**
   Even if `result.response` is empty, do not treat it as completed. Stream error notifications to the user whenever `status != "SUCCESS"`.
6. **Clients must not generate artificial conversation_ids for agy.**
   In Mode 3, `agy` issues its own conversation ID during the `init` event. Generating an ID beforehand causes agy to treat it as unknown and fork an unwanted new session.
7. **Transitioning from Modes 1/2 to Mode 3 within a single chat requires continuation linking.**
   If a session was initialized in Modes 1/2 and subsequently switched to Mode 3, `is_agy_native_session()` detects the absence of agy's initial snapshot and allows agy to generate its native ID. Both IDs are linked via `continued_as.txt`/`continued_from.txt` markers, ensuring `get_session_history()` seamlessly unifies the conversation history.

---

## 4. Changelog
| Date | Version | Description | Rationale |
|:---|:---|:---|:---|
| 2026-09-02 | v2.4 | Added Constraint #7: Fixed session splitting when transitioning from Modes 1/2 to Mode 3. Integrated `is_agy_native_session()` and `link_conversation_continuation()`. | Prevent broken conversation history when switching modes within a chat. |
| 2026-08-31 | v2.3 | Aligned with official docs (`/docs/cli/conversations`, `/docs/cli/headless`). Replaced `--resume` with `--conversation`, adopted agy-issued IDs, expanded error checking to all `!= "SUCCESS"` statuses. | Fixed silent resume failures caused by nonexistent CLI flags and mismatched IDs. |
| 2026-08-31 | v2.2 | Reimplemented in `feature/session-resume-v2`: seek-to-end on resume, regex Unicode decoding, dual transcript paths. | Recovered from regression introduced in v2.1. |
| 2026-08-31 | v2.1 | (Discarded) Session management REST API and `session_init` SSE event. | Discarded due to regressions in Mode 3 streaming. |
| 2026-08-30 | v2.0 | Standardized and frozen streaming protocol for Modes 1, 2, and 3. | Baseline frozen on commit `1fd3b01`. |
