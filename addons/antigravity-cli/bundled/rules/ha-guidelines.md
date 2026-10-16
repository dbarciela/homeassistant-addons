---
name: ha-guidelines
description: Always prioritize using ha-mcp tools over direct curl API calls when controlling or querying Home Assistant
trigger: always_on
---

# Home Assistant Guidelines

## Tools & Integrations
- Always prioritize using `ha-mcp` tools (`control_activate`, `get_entity_state`, `search_entities`, etc.) when interacting with Home Assistant entities, devices, and states.
- Avoid using direct shell `curl` commands to the Home Assistant REST API unless explicitly requested or when MCP tools are unavailable for the specific task.

## Language & Communication Style
- **English-First Baseline**: The project architecture, documentation, configuration files, and tool definitions are English-first.
- **Adaptive Language Mirroring**: Always detect and mirror the language spoken by the user. If the user addresses you in Portuguese (e.g. pt-PT or pt-BR), reply naturally and fluently in Portuguese. If the user communicates in English, Spanish, French, Korean, or any other language, respond in that exact language. Preserve entity IDs, YAML syntax, and technical identifiers in their exact form without translation.
