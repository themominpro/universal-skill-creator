#!/usr/bin/env python3
# Copyright (c) 2026 Momin / GTM Engineering. All rights reserved.
# Licensed under the Apache License, Version 2.0.

"""
Metadata, Version, and Secrets Alignment Verifier.
Validates:
1. Frontmatter metadata (name, description, version).
2. Alignment between os.environ calls in scripts and requires_secrets declarations.
3. Existence and coverage of .env.example.
Outputs structured JSON to stdout. Exits 0 on pass, 1 on fail.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

ENV_CALL_PATTERNS = [
    re.compile(r'os\.environ\.get\(\s*["\']([A-Z0-9_]+)["\']'),
    re.compile(r'os\.environ\[\s*["\']([A-Z0-9_]+)["\']'),
    re.compile(r'process\.env\.([A-Z0-9_]+)'),
]

IGNORE_SYSTEM_ENVS = {
    "PATH", "HOME", "USER", "USERNAME", "PWD", "SHELL", "TERM",
    "LANG", "LC_ALL", "PYTHONPATH", "VIRTUAL_ENV", "NODE_ENV", "TEMP", "TMP"
}

def parse_frontmatter(content: str) -> tuple[dict, list[str]]:
    errors = []
    if not content.startswith("---"):
        errors.append("SKILL.md does not start with '---' at byte 0.")
        return {}, errors

    parts = content.split("---", 2)
    if len(parts) < 3:
        errors.append("Malformed YAML frontmatter in SKILL.md.")
        return {}, errors

    yaml_text = parts[1]
    metadata = {
        "name": "",
        "version": "",
        "description": "",
        "requires_secrets": []
    }

    # Extract name
    name_m = re.search(r"^name:\s*([a-zA-Z0-9_-]+)", yaml_text, re.MULTILINE)
    if name_m:
        metadata["name"] = name_m.group(1).strip()

    # Extract version
    ver_m = re.search(r"version:\s*['\"]?([0-9]+\.[0-9]+\.[0-9]+)['\"]?", yaml_text, re.MULTILINE)
    if ver_m:
        metadata["version"] = ver_m.group(1).strip()

    # Extract description
    desc_m = re.search(r"^description:\s*(?:>-?|\|-?)?\s*\n?((?:(?:\s{2,}.*\n?)+)|(?:.*$))", yaml_text, re.MULTILINE)
    if desc_m:
        metadata["description"] = " ".join([line.strip() for line in desc_m.group(1).splitlines()]).strip()

    # Extract requires_secrets. Accept all three forms skills actually use:
    #   requires_secrets:
    #     - SECRET_API_KEY
    #   requires_secrets: [SECRET_API_KEY, OTHER_KEY]
    #   requires_secrets:
    #     - key: SECRET_API_KEY   (legacy form, kept for backward compatibility)
    secret_keys = []
    block_m = re.search(r"requires_secrets:\s*\n((?:\s+-\s+.*\n?)+)", yaml_text)
    if block_m:
        for line in block_m.group(1).splitlines():
            m = re.search(r"-\s*(?:key:\s*)?([A-Z][A-Z0-9_]*)", line.strip())
            if m:
                secret_keys.append(m.group(1))
    else:
        inline_m = re.search(r"requires_secrets:\s*\[([^\]]*)\]", yaml_text)
        if inline_m:
            secret_keys = [s.strip().strip("'\"") for s in inline_m.group(1).split(",") if s.strip()]
    if not secret_keys:
        secret_keys = re.findall(r"-\s*key:\s*([A-Z0-9_]+)", yaml_text)
    metadata["requires_secrets"] = secret_keys

    return metadata, errors

def find_script_env_vars(skill_path: Path) -> set[str]:
    used_vars = set()
    for root, _, files in os.walk(skill_path):
        if ".git" in root or "__pycache__" in root or "node_modules" in root:
            continue
        for file in files:
            if file.endswith((".py", ".js", ".ts", ".sh")):
                try:
                    text = (Path(root) / file).read_text(encoding="utf-8", errors="replace")
                    for pat in ENV_CALL_PATTERNS:
                        for match in pat.findall(text):
                            if match not in IGNORE_SYSTEM_ENVS:
                                used_vars.add(match)
                except Exception:
                    pass
    return used_vars

def verify_skill(skill_dir: str | Path) -> dict:
    p = Path(skill_dir).resolve()
    skill_file = p / "SKILL.md"
    errors = []
    warnings = []

    if not skill_file.is_file():
        return {"status": "FAIL", "errors": [f"Missing SKILL.md in '{p}'."]}

    content = skill_file.read_text(encoding="utf-8", errors="replace")
    meta, fm_errors = parse_frontmatter(content)
    errors.extend(fm_errors)

    if not meta.get("name"):
        errors.append("Frontmatter is missing required 'name' field.")
    if not meta.get("version"):
        errors.append("Frontmatter is missing required 'version' (e.g. metadata.version: '1.0.0').")
    if not meta.get("description"):
        errors.append("Frontmatter is missing required 'description'.")

    declared_secrets = set(meta.get("requires_secrets", []))
    used_secrets = find_script_env_vars(p)

    # Check for undeclared secrets
    undeclared = used_secrets - declared_secrets
    if undeclared:
        errors.append(f"Scripts use environment variables not declared in 'requires_secrets': {sorted(undeclared)}")

    # Check .env.example
    env_example = p / ".env.example"
    if declared_secrets or used_secrets:
        if not env_example.is_file():
            warnings.append("Skill accesses secrets but is missing companion '.env.example' in root.")
        else:
            env_content = env_example.read_text(encoding="utf-8", errors="replace")
            for sec in declared_secrets:
                if sec not in env_content:
                    warnings.append(f".env.example is missing placeholder for declared secret '{sec}'.")

    status = "FAIL" if errors else "PASS"
    return {
        "status": status,
        "name": meta.get("name", p.name),
        "version": meta.get("version", "unknown"),
        "declared_secrets": sorted(declared_secrets),
        "used_secrets": sorted(used_secrets),
        "errors": errors,
        "warnings": warnings
    }

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: python verify_metadata.py <path_to_skill>"}, indent=2))
        sys.exit(1)

    result = verify_skill(sys.argv[1])
    print(json.dumps(result, indent=2))
    sys.exit(1 if result.get("status") == "FAIL" else 0)

if __name__ == "__main__":
    main()
