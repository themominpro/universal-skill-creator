#!/usr/bin/env python3
# Copyright (c) 2026 Momin / GTM Engineering. All rights reserved.
# Licensed under the Apache License, Version 2.0.

"""
Zero-Dependency Universal Skill Bundler.
Packages a validated skill directory into .zip and .tar.gz archives.
Generates WORKFLOW.md and distribution README.md if missing.
Excludes cache files, OS metadata, and git directories.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tarfile
import zipfile
from pathlib import Path

EXCLUDE_PATTERNS = {
    ".git", "__pycache__", ".venv", "venv", "node_modules",
    ".DS_Store", "Thumbs.db", ".pytest_cache", ".ruff_cache",
    ".env", ".env.local", ".env.production", ".env.development", ".env.test"
}

def generate_workflow_md(skill_dir: Path, skill_name: str, description: str) -> Path:
    workflow_file = skill_dir / "WORKFLOW.md"
    if workflow_file.is_file():
        return workflow_file

    content = f"""# 🚀 Quick Start & Workflow Guide: {skill_name}

## Overview
{description}

---

## ⚡ How to Trigger This Skill

In your AI chat (Antigravity, Claude Code, Cursor, Windsurf), type:
> *"Run {skill_name} on [target]"*

---

## 📋 Recommended Workflow

1. **Phase 1: Discovery & Context Read**
   - The skill silently inspects the workspace, configuration files, and active dependencies.
2. **Phase 2: Execution & Code Generation**
   - Follows step-by-step procedures with deterministic validation.
3. **Phase 3: Verification**
   - Runs bundled Python test scripts in `scripts/` to confirm output validity before final delivery.

---

## 🔑 Secret Configuration
If this skill requires external API keys, copy `.env.example` to `.env` in your project root and supply the required values.
"""
    workflow_file.write_text(content.strip() + "\n", encoding="utf-8")
    return workflow_file

def generate_readme_md(skill_dir: Path, skill_name: str, version: str, description: str) -> Path:
    readme_file = skill_dir / "README.md"
    if readme_file.is_file():
        return readme_file

    content = f"""# {skill_name} (v{version})

{description}

---

## 📦 What's Included

- `SKILL.md`: Main execution rules and procedural operating system.
- `scripts/`: Zero-token deterministic companion scripts.
- `references/`: Flat, on-demand reference playbooks.
- `assets/`: Reusable templates and schemas.
- `WORKFLOW.md`: Fast onboarding and trigger guide.

---

## 🛠️ Installation

Use the universal skill installer or copy directly to your AI agent skills folder:
- **Antigravity**: `~/.gemini/config/skills/{skill_name}/`
- **Claude Code**: `~/.claude/skills/{skill_name}/`
- **Cursor / Workspace**: `.cursor/skills/{skill_name}/` or `./skills/{skill_name}/`

*Adheres to the open `agentskills.io` standard.*
"""
    readme_file.write_text(content.strip() + "\n", encoding="utf-8")
    return readme_file

def bundle_skill(skill_dir: str | Path, output_dir: str | Path, format_type: str = "both", skip_gates: bool = False) -> dict:
    source = Path(skill_dir).resolve()
    dest = Path(output_dir).resolve()
    dest.mkdir(parents=True, exist_ok=True)
    # Gate: audit and security must pass before any archive is created.
    # The audit and security scripts are taken from the target skill if it ships them,
    # otherwise from this bundler's own scripts folder, so a generated skill can be gated
    # even though its own scripts/ folder only contains its validate.py.
    if not skip_gates:
        scripts_dir = Path(__file__).resolve().parent
        for gate_name in ("audit_skill.py", "security_scan.py"):
            gate_path = source / "scripts" / gate_name
            if not gate_path.is_file():
                gate_path = scripts_dir / gate_name
            if not gate_path.is_file():
                continue
            import subprocess
            proc = subprocess.run([sys.executable, str(gate_path), str(source)], capture_output=True, text=True)
            if proc.returncode != 0:
                return {
                    "status": "FAIL",
                    "error": f"Bundle gate failed: {gate_name} did not pass for '{source}'. Fix the failures first, or pass --skip-gates explicitly if you accept shipping an ungated skill.",
                    "gate": gate_name,
                    "gate_output": (proc.stdout.strip() or proc.stderr.strip())[:500],
                }

    skill_file = source / "SKILL.md"
    if not skill_file.is_file():
        return {"status": "FAIL", "error": f"Missing SKILL.md in '{source}'."}

    # Extract name and version
    text = skill_file.read_text(encoding="utf-8", errors="replace")
    name_m = re.search(r"^name:\s*([a-zA-Z0-9_-]+)", text, re.MULTILINE)
    name = name_m.group(1).strip() if name_m else source.name
    ver_m = re.search(r"version:\s*['\"]?([0-9]+\.[0-9]+\.[0-9]+)['\"]?", text, re.MULTILINE)
    version = ver_m.group(1).strip() if ver_m else "1.0.0"

    desc_m = re.search(r"^description:\s*(?:>-?|\|-?)?\s*\n?((?:(?:\s{2,}.*\n?)+)|(?:.*$))", text, re.MULTILINE)
    description = " ".join([l.strip() for l in desc_m.group(1).splitlines()]).strip() if desc_m else "Agent skill package."

    # Ensure auxiliary docs exist
    generate_workflow_md(source, name, description)
    generate_readme_md(source, name, version, description)

    # Security Pre-Check: Scan for active .env or credential files
    active_env_files = [
        p for p in source.rglob("*")
        if p.is_file() and (
            p.name in (".env", ".env.local", ".env.production", ".env.development", ".env.test") or
            (p.name.startswith(".env") and not p.name.endswith(".example") and not p.name.endswith(".template")) or
            p.suffix.lower() in (".pem", ".key")
        ) and ".git" not in p.parts and "node_modules" not in p.parts and ".venv" not in p.parts
    ]

    if active_env_files:
        rel_files = [str(f.relative_to(source)) for f in active_env_files]
        return {
            "status": "FAIL",
            "error": f"Security abort: Active environment/secret files detected in skill directory: {rel_files}. Never ship active .env or key files! Remove them or ship .env.example only."
        }

    artifacts = []

    def should_include(path: Path) -> bool:
        name_lower = path.name.lower()
        if name_lower in (".env", ".env.local", ".env.production", ".env.development", ".env.test"):
            return False
        if name_lower.startswith(".env") and not (name_lower.endswith(".example") or name_lower.endswith(".template")):
            return False
        if path.suffix.lower() in (".pem", ".key", ".crt", ".pyc"):
            return False
        for part in path.parts:
            if part in EXCLUDE_PATTERNS or part.endswith(".pyc"):
                return False
        return True

    # Build ZIP archive
    if format_type in ("zip", "both"):
        zip_path = dest / f"{name}-v{version}.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, _, files in os.walk(source):
                for file in files:
                    fp = Path(root) / file
                    if should_include(fp):
                        rel = fp.relative_to(source)
                        zf.write(fp, arcname=str(Path(name) / rel))
        artifacts.append({
            "format": "zip",
            "path": str(zip_path),
            "size_kb": round(zip_path.stat().st_size / 1024, 2)
        })

    # Build TAR.GZ archive
    if format_type in ("tar.gz", "both"):
        tar_path = dest / f"{name}-v{version}.tar.gz"
        with tarfile.open(tar_path, "w:gz") as tf:
            for root, _, files in os.walk(source):
                for file in files:
                    fp = Path(root) / file
                    if should_include(fp):
                        rel = fp.relative_to(source)
                        tf.add(fp, arcname=str(Path(name) / rel))
        artifacts.append({
            "format": "tar.gz",
            "path": str(tar_path),
            "size_kb": round(tar_path.stat().st_size / 1024, 2)
        })

    return {
        "status": "SUCCESS",
        "skill_name": name,
        "version": version,
        "output_directory": str(dest),
        "artifacts": artifacts
    }

def main():
    parser = argparse.ArgumentParser(description="Package an AI agent skill for distribution.")
    parser.add_argument("skill_dir", help="Path to the skill directory")
    parser.add_argument("output_dir", help="Destination directory for distribution archives")
    parser.add_argument("--format", choices=["zip", "tar.gz", "both"], default="both", help="Archive format")
    parser.add_argument("--skip-gates", action="store_true", help="Skip audit and security gates. Not recommended.")
    args = parser.parse_args()

    result = bundle_skill(args.skill_dir, args.output_dir, args.format, skip_gates=args.skip_gates)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result.get("status") == "SUCCESS" else 1)

if __name__ == "__main__":
    main()

