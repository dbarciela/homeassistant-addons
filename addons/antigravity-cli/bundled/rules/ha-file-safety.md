---
name: ha-file-safety
description: Require explicit user approval before deleting or overwriting any file, and never touch Home Assistant's critical config data under any circumstance
trigger: always_on
---

# Home Assistant File Safety Rules (Mandatory)

## 1. Prior Approval Required Before File Deletion or Overwriting
When processing a user request that involves **deleting (rm, unlink, etc.) or irreversibly overwriting a file or folder**, NEVER execute it preemptively. Always follow these exact steps:
1. List the **exact full path(s)** of the file(s) to be deleted or modified.
2. State the **total count** of affected files.
3. Explain **why** the deletion or modification is required.
4. Present this explanation in your response, do NOT execute the destructive command, and **wait for clear, explicit user approval** ("yes", "delete it", "proceed", "confirmed", etc.) in the user's next message.
5. Never execute `rm`, file overwrites, moves, or replacements before user approval is received.
6. This rule applies equally even if only 1 file is affected. Never "just proceed because it's a minor task".
7. **Deleting directories/folders always requires explicit warning and confirmation without exception.** Directory removal (`rm -rf`, `rmdir`) wipes out multiple files simultaneously. Even if the folder appears empty or minor, and even if it is not in the protected list in Section 2, always present the full path and contents/count before requesting approval.

## 2. Strictly Forbidden From Deletion or Modification (Deny even if explicitly requested by user)
The following items are mission-critical Home Assistant system data. Deleting or modifying them causes irreversible damage (loss of all entities, devices, and automations; inability to log in; broken cloud integrations). Even if the user explicitly asks to delete or "reset" them, **NEVER execute it**, explain the risks, and suggest alternatives (HA backups, official UI settings). Vague requests like "clean up" or "tidy up" must NEVER touch these items.

| Path | Contents | Risk |
|---|---|---|
| `/homeassistant/.storage/` (Entire directory) | Entity, device, area registries, credentials, config entries, dashboards | Deleting resets all devices, automations, and deletes login accounts |
| `/homeassistant/secrets.yaml` | Passwords, tokens, sensitive credentials | Deleting breaks all configurations referencing secrets |
| `/homeassistant/configuration.yaml` | Home Assistant main configuration | Deleting prevents Home Assistant from booting |
| `/homeassistant/.uuid` | Unique identifier of this HA instance | Deleting breaks Nabu Casa Cloud and mobile app integrations |
| `/homeassistant/.HA_VERSION` | Internal version marker | Deleting disrupts update and migration logic |
| `/homeassistant/home-assistant_v2.db` (including `-wal`, `-shm`) | Recorder history and logbook database | Deleting erases all historical sensor logs |
| `/homeassistant/.cloud/` | Nabu Casa Cloud auth tokens | Deleting disconnects remote access and voice assistants |
| `/config/.gemini/` | Antigravity CLI configuration, auth, and history | Deleting resets the AI agent's own login and session |
| `/homeassistant/automations.yaml`, `/homeassistant/scripts.yaml`, `/homeassistant/scenes.yaml` | User-defined automations, scripts, and scenes | Deleting destroys all user-created automations |
| `/homeassistant/custom_components/` | Installed custom integrations (HACS, etc.) | Deleting disables all custom integrations |
| `/backup/` (Entire directory) | Home Assistant backup archives | Deleting removes all disaster recovery options |

## 3. All Other Files
For ordinary files not listed above (e.g., images in `www/`, log files), Rule 1 (prior explicit approval) remains fully in effect.
