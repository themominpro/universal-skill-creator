#!/usr/bin/env python3
# Copyright (c) 2026 Momin / GTM Engineering. All rights reserved.
# Licensed under the Apache License, Version 2.0.

"""
Zero-Dependency Secret & .env Onboarding Manager.
1. Parses requires_secrets from candidate SKILL.md.
2. Checks workspace .env and .env.example status.
3. Automatically ensures .gitignore contains .env.
4. Can safely set or verify keys without token echoes.
Outputs structured JSON to stdout.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

def parse_requires_secrets(skill_dir: Path) -> list[dict]:
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.is_file():
        return []

    content = skill_file.read_text(encoding="utf-8", errors="replace")
    if not content.startswith("---"):
        return []
    parts = content.split("---", 2)
    if len(parts) < 3:
        return []

    yaml_text = parts[1]
    if "requires_secrets:" not in yaml_text:
        return []

    # Parse simple secret blocks
    secrets = []
    lines = yaml_text.splitlines()
    in_secrets = False
    current_sec = {}

    for line in lines:
        if re.match(r"^requires_secrets:\s*$", line):
            in_secrets = True
            continue
        if in_secrets:
            if re.match(r"^[a-zA-Z_-]+:\s*", line) and not line.startswith("  "):
                break # Reached next top-level key
            key_m = re.match(r"^\s*-\s*key:\s*([A-Z0-9_]+)", line)
            if key_m:
                if current_sec and "key" in current_sec:
                    secrets.append(current_sec)
                current_sec = {"key": key_m.group(1).strip()}
                continue
            prop_m = re.match(r"^\s*([a-zA-Z_-]+):\s*(.*)$", line)
            if prop_m and current_sec:
                prop = prop_m.group(1).strip()
                val = prop_m.group(2).strip().strip("'\"")
                current_sec[prop] = val

    if current_sec and "key" in current_sec:
        secrets.append(current_sec)

    return secrets

def find_script_env_vars(skill_dir: Path) -> set[str]:
    """Env vars actually used in scripts, not just declared in SKILL.md.
    Without this, a skill with undeclared env use reports all_configured True."""
    import re as _re
    found = set()
    scripts_dir = skill_dir / "scripts"
    if scripts_dir.is_dir():
        for f in scripts_dir.rglob("*.py"):
            text = f.read_text(encoding="utf-8", errors="replace")
            found.update(_re.findall(r'os\.environ\.get\(\s*["\']([A-Z0-9_]+)["\']', text))
            found.update(_re.findall(r'os\.environ\[\s*["\']([A-Z0-9_]+)["\']', text))
    return found


def ensure_gitignore(workspace: Path) -> dict:
    gi = workspace / ".gitignore"
    added = False
    if not gi.is_file():
        gi.write_text("# Secrets\n.env\n.env.local\n__pycache__/\n", encoding="utf-8")
        return {"status": "CREATED", "message": "Created .gitignore with .env excluded."}
    
    content = gi.read_text(encoding="utf-8", errors="replace")
    if not re.search(r"^\.env\b", content, re.MULTILINE):
        gi.write_text(content.rstrip() + "\n.env\n", encoding="utf-8")
        added = True
    return {"status": "UPDATED" if added else "EXISTS", "message": ".env is excluded in .gitignore."}

def check_env_status(workspace: Path, required_secrets: list[dict]) -> dict:
    env_file = workspace / ".env"
    env_example = workspace / ".env.example"

    existing_env_keys = {}
    if env_file.is_file():
        for line in env_file.read_text(encoding="utf-8", errors="replace").splitlines():
            m = re.match(r"^([A-Z0-9_]+)=(.*)$", line.strip())
            if m:
                existing_env_keys[m.group(1)] = bool(m.group(2).strip())

    existing_example_keys = set()
    if env_example.is_file():
        for line in env_example.read_text(encoding="utf-8", errors="replace").splitlines():
            m = re.match(r"^([A-Z0-9_]+)=", line.strip())
            if m:
                existing_example_keys.add(m.group(1))

    secret_statuses = []
    missing_count = 0

    for sec in required_secrets:
        key = sec["key"]
        has_val = existing_env_keys.get(key, False)
        in_example = key in existing_example_keys
        if not has_val:
            missing_count += 1
        secret_statuses.append({
            "key": key,
            "service": sec.get("service", "External API"),
            "url": sec.get("url", ""),
            "configured_in_env": has_val,
            "present_in_example": in_example,
            "hint": sec.get("hint", "")
        })

    return {
        "workspace": str(workspace),
        "total_required": len(required_secrets),
        "missing_count": missing_count,
        "all_configured": (missing_count == 0),
        "secrets": secret_statuses
    }

def set_secret(workspace: Path, key: str, value: str) -> dict:
    env_file = workspace / ".env"
    env_example = workspace / ".env.example"

    # Update .env
    lines = []
    key_found = False
    if env_file.is_file():
        for line in env_file.read_text(encoding="utf-8", errors="replace").splitlines():
            if re.match(rf"^{re.escape(key)}=", line.strip()):
                lines.append(f"{key}={value}")
                key_found = True
            else:
                lines.append(line)
    if not key_found:
        lines.append(f"{key}={value}")

    env_file.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")

    # Update .env.example
    example_lines = []
    ex_found = False
    if env_example.is_file():
        for line in env_example.read_text(encoding="utf-8", errors="replace").splitlines():
            if re.match(rf"^{re.escape(key)}=", line.strip()):
                example_lines.append(f"{key}=your_{key.lower()}_here")
                ex_found = True
            else:
                example_lines.append(line)
    if not ex_found:
        example_lines.append(f"{key}=your_{key.lower()}_here")

    env_example.write_text("\n".join(example_lines).strip() + "\n", encoding="utf-8")

    return {
        "status": "SUCCESS",
        "key": key,
        "message": f"Successfully updated '{key}' in .env and .env.example."
    }

def main():
    parser = argparse.ArgumentParser(description="Configure and verify API secrets for agent skills.")
    parser.add_argument("skill_dir", help="Path to the skill directory")
    parser.add_argument("--workspace", default=".", help="Target workspace path containing .env")
    parser.add_argument("--set", nargs=2, metavar=("KEY", "VALUE"), help="Set an API key in workspace .env. Warning: the value appears in shell history. Prefer --prompt.")
    parser.add_argument("--prompt", metavar="KEY", help="Prompt for a secret value with hidden input (getpass), so it never appears in shell history")
    args = parser.parse_args()

    workspace = Path(args.workspace).resolve()
    skill_dir = Path(args.skill_dir).resolve()

    ensure_gitignore(workspace)

    if args.set:
        res = set_secret(workspace, args.set[0], args.set[1])
        print(json.dumps(res, indent=2))
        sys.exit(0)

    if args.prompt:
        import getpass
        value = getpass.getpass(f"Enter value for {args.prompt}: ")
        res = set_secret(workspace, args.prompt, value)
        print(json.dumps(res, indent=2))
        sys.exit(0)

    secrets = parse_requires_secrets(skill_dir)
    # Union declared secrets with env vars actually used in scripts, so an
    # undeclared env var is reported as missing instead of all_configured True.
    declared_keys = {s["key"] for s in secrets}
    for key in sorted(find_script_env_vars(skill_dir) - declared_keys):
        secrets.append({"key": key, "description": "Used in scripts but not declared in requires_secrets"})
    status = check_env_status(workspace, secrets)
    print(json.dumps(status, indent=2))
    sys.exit(0 if status["all_configured"] else 1)

if __name__ == "__main__":
    main()
