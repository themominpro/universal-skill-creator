---
name: universal-skill-exporter
description: >-
  Audits, security-scans, validates metadata, and packages AI Agent Skills into
  clean, client-ready distribution archives (.zip and .tar.gz). Scans for hardcoded
  secrets and AST-level vulnerabilities, aligns requires_secrets declarations with .env.example,
  and generates WORKFLOW.md and distribution README.md files.
  Trigger on: "export skill", "package skill", "bundle skill", "prepare skill for distribution",
  "publish skill", "zip skill". Do NOT use for installing skills or writing skill logic from scratch.
compatibility: Requires Python 3.9+ and standard shell environment (Windows, macOS, Linux)
metadata:
  version: "1.0.0"
allowed-tools: Bash(python3:*) Bash(python:*) Read Write Edit Glob Grep
---

# Universal Skill Exporter

## 1. Core Reframing & Non-Negotiable Invariants

- **Mental Model**: An export package is a commercial software release, NOT a bare folder dump. It must be mathematically verified safe, structurally compliant, and ready for 1-click client onboarding.
- **Environment Notice**: Python 3 standard library (`zipfile`, `tarfile`, `ast`) handles bundling cross-platform. Do NOT execute external `zip` or `mktemp` CLI commands.
- **Hard Invariant 1 (Zero-Leak Gate)**: NEVER export a skill containing hardcoded secrets (API keys, tokens, private URLs). `python scripts/security_scan.py <path>` must return PASS.
- **Hard Invariant 2 (Secret Parity)**: Every environment variable accessed in Python/Node scripts must be declared in `requires_secrets:` in `SKILL.md` and present in `.env.example`.
- **Hard Invariant 3 (Clean Archive Boundary)**: Distribution archives MUST exclude `.git`, `__pycache__`, `.venv`, OS metadata files (`.DS_Store`, `Thumbs.db`), and secret files (`.env` except `.env.example`, `.pem`, `.key`, `.crt`). An active `.env` aborts the bundle, even with `--skip-gates`.

---

## 2. Task Routing Decision Table

| Scenario / Intent | Recommended Workflow | Key Script Gate |
|:------------------|:---------------------|:----------------|
| Package a verified skill for commercial client | Run full 4-phase export pipeline | `scripts/bundle_package.py --format both` |
| Security pre-flight check only | Run AST vulnerability scan | `scripts/security_scan.py <path>` |
| Validate metadata & secret alignment only | Run metadata alignment check | `scripts/verify_metadata.py <path>` |

---

## 3. Phase 1: Silent Discovery & Metadata Inspection

- [ ] **Step 1.1 (Locate Skill Directory)**: Inspect target directory and verify `SKILL.md` exists at the root.
- [ ] **Step 1.2 (Run Metadata & Secret Verifier)**:
  ```bash
  python scripts/verify_metadata.py path/to/skill
  ```
  *(On Unix/macOS, use `python3 scripts/verify_metadata.py`)*
  - If missing `version`: prompt user to confirm version number (e.g. `1.0.0`).
  - If scripts use undeclared environment variables: update `requires_secrets:` in `SKILL.md`.
  - If `.env.example` is missing or incomplete: generate placeholder entries.

---

## 4. Phase 2: Zero-Token AST Security Audit

- [ ] **Step 2.1 (Run Deterministic Security Scanner)**:
  ```bash
  python scripts/security_scan.py path/to/skill
  ```
  - Inspect JSON report for `critical_issues`:
    1. **Hardcoded Secrets**: Patterns matching `AIza`, `sk-`, `ghp_`, `Bearer`, or raw tokens.
    2. **Remote Code Execution**: Calls to `eval()`, `exec()`, or `subprocess(..., shell=True)`.
    3. **Credential Harvesting**: Unauthorized file reads of `~/.ssh`, `~/.aws`, or keychain paths.
- [ ] **Step 2.2 (Remediate Security Findings)**:
  - If hardcoded keys are detected: replace with `os.environ.get("KEY_NAME")` and add to `.env.example`.
  - If `shell=True` is detected: refactor to array-based subprocess invocation (`["cmd", "arg1", "arg2"]`).
  - Re-run `security_scan.py` until `status` is **PASS**.

---

## 5. Phase 3: Documentation & Client Collateral Generation

- [ ] **Step 3.1 (Verify or Generate WORKFLOW.md)**: bundle_package.py generates `WORKFLOW.md` and `README.md` in a temporary copy only. Exporting must never mutate the source skill folder.
- [ ] **Step 3.2 (Verify or Generate README.md)**: Ensure a client-facing `README.md` details features, installation instructions, and file architecture.

---

## 6. Phase 4: Cross-Platform Packaging & Hash Delivery

- [ ] **Step 4.1 (Bundle Distribution Archives)**:
  ```bash
  python scripts/bundle_package.py path/to/skill path/to/dist --format both
  ```
  - Builds both `.zip` (for Windows/general clients) and `.tar.gz` (for Linux/Docker/Cloud deployments).
  - bundle_package.py runs security_scan.py and verify_metadata.py first and aborts if either fails, unless `--skip-gates` is passed explicitly. Active secret files always abort.
- [ ] **Step 4.2 (Deliver Release Summary)**:
  Present the user with:
  1. Archive locations, file sizes, and sha256 hashes from the bundle output.
  2. Declared API keys required by the client.
  3. Clean security audit confirmation.

---

## 7. Anti-Rationalization Guardrails

| Common Model Excuse | Why It Is Strictly Forbidden & Required Action |
|:--------------------|:-----------------------------------------------|
| "The skill only has a simple script, so I can skip the security scan." | Attackers and accidental leaks hide in simple scripts. Always run `security_scan.py`. |
| "I will use bash zip commands to package the archive." | Bash `zip` fails on Windows. Always use Python's built-in `bundle_package.py`. |
| "The client knows how to get API keys, so setup instructions aren't needed." | Poor secret documentation is the #1 cause of client refunds. Always include dashboard URLs in `requires_secrets`. |
| "I can leave .env inside the exported package since it's just a test key." | NEVER distribute real credentials. Any `.env` inside the export folder is a critical security breach. |

---

## 8. What This Skill Does NOT Do

- Does NOT install skills into host IDEs (use `universal-skill-installer`).
- Does NOT distribute uncommitted `.env` files with live private credentials.
- Does NOT execute external shell package commands that break on non-Unix environments.
- Does NOT generate untested skills from scratch (use `universal-skill-creator`).
