# agentskills.io Specification Reference & Standards

This document specifies the open standard for Agent Skills governed by the Agentic AI Foundation (AAIF) and formalized at [agentskills.io/specification](https://agentskills.io/specification).

---

## 1. Directory Structure Standards

An Agent Skill is a directory residing in a configured skill search path.

```text
<skill-name>/
├── SKILL.md              # Mandatory: Core metadata and procedural instructions
├── scripts/              # Optional: Deterministic executable tools (Python, Bash, Node.js)
├── references/           # Optional: Deep documentation files loaded on-demand
└── assets/               # Optional: Static resources, schemas, templates
```

- The directory name must match the `name` field in YAML frontmatter character-for-character.
- `SKILL.md` is strictly case-sensitive. `skill.md` or `SKILL.MD` are invalid.

---

## 2. YAML Frontmatter Specification

`SKILL.md` MUST begin at byte 0 with `---` and conclude the frontmatter block with a matching `---`.

```yaml
---
name: my-specialized-skill
description: >-
  Concise third-person description stating what the skill does and when to activate it.
  Must include relevant domain keywords and negative boundaries.
license: Apache-2.0
compatibility: Requires Python 3.10+ and git CLI
metadata:
  author: platform-team
  version: "1.0.0"
allowed-tools: Bash(python3:*) Read Write
---
```

### Field Definitions

| Field | Requirement | Type | Description & Limits |
|:------|:------------|:-----|:---------------------|
| `name` | **Required** | string | 1–64 characters. Lowercase alphanumeric characters (`a-z`, `0-9`) and single hyphens (`-`). No double hyphens (`--`), no leading or trailing hyphens. Must match folder name. |
| `description` | **Required** | string | 1–1,024 characters. Evaluated at startup discovery to decide whether to activate the skill. Must use third-person grammar. |
| `license` | Optional | string | Short SPDX license identifier (e.g., `Apache-2.0`, `MIT`, `Proprietary`) or reference to LICENSE file. |
| `compatibility` | Optional | string | 1–500 characters. Declares system runtime requirements (e.g., Python version, OS dependencies). |
| `metadata` | Optional | map | Arbitrary string-to-string key-value pairs (e.g. `version`, `author`, `team`). |
| `allowed-tools` | Optional | string | Space-separated list of approved tool patterns. |

### Critical Frontmatter Constraints
- **Zero Leading Bytes**: No blank lines, comments, or byte-order marks before the first `---`.
- **No Angle Brackets**: Never include `<` or `>` inside the YAML frontmatter. Automated scanners and agent harnesses flag these as prompt-injection payloads.

---

## 3. Context Loading Protocol (Progressive Disclosure)

Agent Skills operate under a 3-level progressive disclosure protocol:

1. **Level 1 (Discovery)**: At session startup, the agent reads ONLY the `name` and `description` from the YAML frontmatter (~50–100 tokens per skill) into its system prompt.
2. **Level 2 (Activation)**: When a user prompt matches the description, the agent executes a file read to load the full `SKILL.md` Markdown body (<5,000 tokens) into active conversation context.
3. **Level 3 (Execution)**: The agent accesses supporting resources strictly on demand:
   - Reads files in `references/` only when a step explicitly requires that reference.
   - Executes scripts in `scripts/` via sandbox shell; script source code never enters context, only stdout JSON is returned.

