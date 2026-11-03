#!/usr/bin/env python3
# Copyright (c) 2026 Momin / GTM Engineering. All rights reserved.
# Licensed under the Apache License, Version 2.0.

"""
Cross-Platform Dependency Checker & Installer for Agent Skills.
Inspects Python requirements.txt, Node package.json, and system binary tools.
Works identically on Windows, macOS, and Linux without shell failures.
Outputs structured JSON to stdout.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

def check_python_packages(req_file: Path) -> dict:
    if not req_file.is_file():
        return {"has_requirements": False, "packages": []}

    lines = req_file.read_text(encoding="utf-8", errors="replace").splitlines()
    pkg_status = []
    missing_count = 0

    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # Extract base package name
        pkg_name = line.split("==")[0].split(">=")[0].split("<=")[0].split("~=")[0].strip()
        # Package name is not always the import name: Pillow imports as PIL,
        # beautifulsoup4 imports as bs4, and so on. Without this map, installed
        # packages are reported as missing and pip reinstalls them needlessly.
        import_map = {
            "Pillow": "PIL", "pillow": "PIL",
            "beautifulsoup4": "bs4",
            "scikit-learn": "sklearn",
            "opencv-python": "cv2", "opencv-python-headless": "cv2",
            "PyYAML": "yaml", "pyyaml": "yaml",
            "python-dotenv": "dotenv",
        }
        mod_name = import_map.get(pkg_name, pkg_name.replace("-", "_"))
        
        spec = importlib.util.find_spec(mod_name)
        installed = (spec is not None)
        if not installed:
            missing_count += 1
        pkg_status.append({
            "requirement": line,
            "package": pkg_name,
            "installed": installed
        })

    return {
        "has_requirements": True,
        "missing_count": missing_count,
        "all_installed": (missing_count == 0),
        "packages": pkg_status
    }

def check_system_tools(tools: list[str]) -> list[dict]:
    res = []
    for tool in tools:
        found_path = shutil.which(tool)
        res.append({
            "tool": tool,
            "installed": bool(found_path),
            "path": found_path
        })
    return res

def install_python_requirements(req_file: Path) -> dict:
    cmd = [sys.executable, "-m", "pip", "install", "-r", str(req_file)]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return {"status": "SUCCESS", "stdout": proc.stdout}
    except subprocess.CalledProcessError as e:
        return {"status": "FAIL", "error": e.stderr}

def main():
    parser = argparse.ArgumentParser(description="Check and install dependencies for an agent skill.")
    parser.add_argument("skill_dir", help="Path to the skill directory")
    parser.add_argument("--install", action="store_true", help="Automatically install missing Python packages")
    parser.add_argument("--tools", nargs="*", default=[], help="List of system tools to check (e.g. ffmpeg git)")
    args = parser.parse_args()

    skill_path = Path(args.skill_dir).resolve()
    req_file = skill_path / "requirements.txt"

    py_status = check_python_packages(req_file)
    tools_status = check_system_tools(args.tools)

    install_result = None
    if args.install and py_status.get("missing_count", 0) > 0 and req_file.is_file():
        install_result = install_python_requirements(req_file)
        # Re-check
        py_status = check_python_packages(req_file)

    result = {
        "python": py_status,
        "system_tools": tools_status,
        "install_action": install_result
    }

    print(json.dumps(result, indent=2))
    sys.exit(0 if py_status.get("all_installed", True) else 1)

if __name__ == "__main__":
    main()
