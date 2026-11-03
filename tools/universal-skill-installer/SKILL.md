---
name: universal-skill-installer
description: >-
  Installs, security-verifies, and configures AI Agent Skills from .zip archives,
  .tar.gz packages, or folders into any AI environment (Antigravity, Claude Code, Cursor,
  Codex). Executes pre-install AST malware scans, auto-detects host harness paths,
  installs Python/Node dependencies, and guides interactive .env secret configuration.
  Trigger on: "install skill", "add skill", "setup skill", "import skill", "load skill".
  Do NOT use for creating skills from scratch or packaging skills for distribution.
compatibility: Requires Python 3.9+ and standard shell environment (Windows, macOS, Linux)
metadata:
  version: "1.0.0"
allowed-tools: Bash(python3:*) Bash(python:*) Read Write Edit Glob Grep
---

# Universal Skill Installer

## 1. Core Reframing & Non-Negotiable Invariants

- **Mental Model**: Skill installation is a sandboxed deployment process. Untrusted code must NEVER be copied into the user's active AI environment until mathematically proven clean by AST security verification.
- **Environment Notice**: Multi-harness detection automatically identifies Google Antigravity, Claude Code, Cursor, and Codex paths. Cross-platform Python standard library scripts prevent Windows shell crashes.
- **Hard Invariant 1 (Pre-Install Security Gate)**: Never copy files to the destination harness if `unpack_and_scan.py` detects CRITICAL issues (remote execution, credential harvesting, or exfiltration).
- **Hard Invariant 2 (Secret Isolation)**: Real API keys MUST reside only in `.env` (gitignored). `.env.example` receives placeholder strings only. NEVER print live keys to stdout or prompt echoes.
- **Hard Invariant 3 (Zip-Slip Defense)**: Extraction scripts must enforce strict path traversal validation and reject symlink/hardlink members, to prevent overwriting system or parent files through a link inside the archive.

---

## 2. Task Routing Decision Table

| Scenario / Intent | Recommended Workflow | Key Script Gate |
|:------------------|:---------------------|:----------------|
| Install downloaded .zip or .tar.gz archive | Run full 5-phase onboarding pipeline | `scripts/unpack_and_scan.py <archive>` |
| Install uncompressed skill folder | Detect harness, verify, and copy | `scripts/install_skill.py` |
| Copy a verified skill to its harness target | Copy, create target, clean temp | `scripts/install_skill.py <skill_dir> <target> --temp-dir <temp_dir>` |
| Configure missing API keys for installed skill | Run interactive secret configuration | `scripts/configure_secrets.py <path>` |
| Verify installed skill dependencies | Check Python and system binaries | `scripts/install_dependencies.py <path>` |

---

## 3. Phase 1: Environment & Harness Auto-Discovery

- [ ] **Step 1.1 (Detect Active AI Harnesses)**:
  Run the multi-harness detector:
  ```bash
  python scripts/detect_harness.py
  ```
  *(On Unix/macOS, use `python3 scripts/detect_harness.py`)*
  - Identifies target directories:
    - **Google Antigravity**: `~/.gemini/config/skills/<skill-name>/`
    - **Claude Code**: `~/.claude/skills/<skill-name>/`
    - **Cursor**: `.cursor/skills/<skill-name>/`
    - **Codex**: `~/.codex/skills/<skill-name>/`
    - **Workspace fallback**: `./skills/<skill-name>/` (listed as fallback, not as a detection)
- [ ] **Step 1.2 (Confirm Install Target)**: If multiple harnesses are detected, use the active session's host or prompt the user for preference.

---

## 4. Phase 2: Zero-Token Unpack & Pre-Install AST Security Audit

- [ ] **Step 2.1 (Safely Unpack & Audit Package)**:
  ```bash
  python scripts/unpack_and_scan.py path/to/skill-package
  ```
  - Inspect JSON report for `critical_issues`:
    1. **Remote Code Execution**: `eval()`, `exec()`, or `subprocess(..., shell=True)`.
    2. **Credential Harvesting**: Reads of `~/.ssh`, `~/.aws`, or keychain paths.
    3. **Hardcoded Secrets**: Leaked live credentials embedded in scripts.
- [ ] **Step 2.2 (Security Gate Decision)**:
  - If `status: "FAIL"`: **HALT IMMEDIATELY**. Display the exact file, line number, and risk explanation to the user. Do NOT install.
  - If `status: "PASS"`: Proceed to file installation.

---

## 5. Phase 3: Skill File Deployment

- [ ] **Step 3.1 (Copy Verified Files)**:
  ```bash
  python scripts/install_skill.py <verified_skill_dir> <target_path> --temp-dir <temp_dir_from_unpack>
  ```
  Copy verified skill directory into target harness destination:
  - Antigravity: `~/.gemini/config/skills/<name>/`
  - Claude: `~/.claude/skills/<name>/`
  - Cursor: `.cursor/skills/<name>/`
  - Codex: `~/.codex/skills/<name>/`
  install_skill.py creates the target, refuses to overwrite unless `--force` is given, and cleans the temp extraction directory when `--temp-dir` points to a skill_install_ folder.

---

## 6. Phase 4: Dependency Check & Environment Setup

- [ ] **Step 4.1 (Check & Install Python/Node Dependencies)**:
  ```bash
  python scripts/install_dependencies.py <destination_path>
  ```
  - If packages are missing: ask user for confirmation, then run with `--install`.
- [ ] **Step 4.2 (Configure API Keys & Secrets)**:
  ```bash
  python scripts/configure_secrets.py <destination_path> --workspace .
  ```
  - Inspect output for `missing_count`.
  - For each missing secret:
    1. Display the service name, pricing tier, format hint, and sign-up URL.
    2. Ask the user if they wish to configure it now.
    3. If provided, run `python scripts/configure_secrets.py <path> --prompt KEY` for hidden input. `--set KEY VALUE` still works, but the value then appears in shell history.
    4. Automatically confirms `.env` is listed in `.gitignore`.

---

## 7. Phase 5: Installation Verification & Quick Start

- [ ] **Step 5.1 (Run Final Verification)**:
  Confirm `SKILL.md` is readable, scripts are executable, and secrets are satisfied.
- [ ] **Step 5.2 (Present Quick Start Summary)**:
  Display trigger examples from `WORKFLOW.md` or `SKILL.md` description to the user:
  > *"Skill `<name>` successfully installed! Try typing: `Run <name> on [target]`."*

---

## 8. Anti-Rationalization Guardrails

| Common Model Excuse | Why It Is Strictly Forbidden & Required Action |
|:--------------------|:-----------------------------------------------|
| "The package is from a friend, so I can skip the security scan." | Malicious scripts can be packaged unknowingly. NEVER install without running `unpack_and_scan.py`. |
| "I'll copy files into .claude/skills by default even if running on Antigravity or Cursor." | Installing into an inactive harness makes the skill unusable. Always run `detect_harness.py`. |
| "I can print the API key in the chat to confirm it was saved." | NEVER echo live API keys to conversation logs. Always obfuscate credentials. |
| "I'll use shell unzip or mktemp commands." | Breaks on Windows PowerShell. Always use Python's built-in extraction utilities. |

---

## 9. What This Skill Does NOT Do

- Does NOT install unverified code that fails the AST security audit.
- Does NOT expose or log plaintext API keys in console outputs.
- Does NOT execute shell commands with platform-specific Unix dependencies.
- Does NOT author new skills from scratch (use `universal-skill-creator`).
