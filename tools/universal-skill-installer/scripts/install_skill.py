#!/usr/bin/env python3
# Copyright (c) 2026 Momin / GTM Engineering. All rights reserved.
# Licensed under the Apache License, Version 2.0.

"""
Install a verified skill directory into a harness target.

This is the copy step the installer was missing: unpack_and_scan.py only
verifies a package, it never copies it. This script copies, creates the
target directory, refuses to overwrite an existing install unless --force
is given, and optionally cleans a temp extraction directory afterwards.

Temp-dir safety: --temp-dir is only removed if its name starts with
skill_install_ and it lives under the system temp directory. It is never
used to delete an arbitrary folder.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path


def install_skill(skill_dir: str | Path, target: str | Path, force: bool = False, temp_dir: str | Path | None = None) -> dict:
    source = Path(skill_dir).resolve()
    dest = Path(target).resolve()

    if not (source / "SKILL.md").is_file():
        return {"status": "FAIL", "error": f"Missing SKILL.md in '{source}'. Run unpack_and_scan.py first."}
    if dest.exists() and not force:
        return {"status": "FAIL", "error": f"Target '{dest}' already exists. Use --force to overwrite it."}

    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(source, dest, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))

    temp_cleaned = False
    if temp_dir:
        tmp = Path(temp_dir)
        # Safety: only clean our own extraction dirs, never an arbitrary path.
        if tmp.name.startswith("skill_install_") and str(tmp.parent) == tempfile.gettempdir():
            shutil.rmtree(tmp, ignore_errors=True)
            temp_cleaned = not tmp.exists()

    return {
        "status": "SUCCESS",
        "skill": source.name,
        "installed_to": str(dest),
        "temp_dir_cleaned": temp_cleaned,
    }


def main():
    parser = argparse.ArgumentParser(description="Install a verified skill directory into a harness target.")
    parser.add_argument("skill_dir", help="Path to the verified skill directory")
    parser.add_argument("target", help="Target harness path, e.g. ~/.gemini/config/skills/<skill-name>/")
    parser.add_argument("--force", action="store_true", help="Overwrite an existing install at the target")
    parser.add_argument("--temp-dir", default=None, help="Temp extraction dir from unpack_and_scan.py, cleaned after a successful copy")
    args = parser.parse_args()
    result = install_skill(args.skill_dir, args.target, force=args.force, temp_dir=args.temp_dir)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result.get("status") == "SUCCESS" else 1)


if __name__ == "__main__":
    main()
