#!/usr/bin/env python3
# Copyright (c) 2026 Momin / GTM Engineering. All rights reserved.
# Licensed under the Apache License, Version 2.0.

"""
Safe Cross-Platform Skill Unpacker & Pre-Install Scanner.
Safely uncompresses .zip or .tar.gz archives (Zip-Slip protected)
and runs AST security verification before any file is copied to target harness.
Outputs structured JSON to stdout. Exits 0 if safe, 1 if critical issues found.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import tarfile
import tempfile
import zipfile
from pathlib import Path

# Import security scanner from current directory
from security_scan import scan_directory

def safe_extract_zip(zip_path: Path, dest_dir: Path) -> Path:
    with zipfile.ZipFile(zip_path, "r") as zf:
        for member in zf.infolist():
            # Zip slip defense: prevent path traversal outside dest_dir
            target_path = dest_dir / member.filename
            if not target_path.resolve().is_relative_to(dest_dir.resolve()):
                raise ValueError(f"Zip slip security violation detected in member: {member.filename}")
            # Reject symlinks stored in zip files: extractall would otherwise
            # write the link target as a file, and later members could follow it.
            mode = (member.external_attr >> 16) & 0o777777
            if (mode & 0o120000) == 0o120000:
                raise ValueError(f"Symlink member rejected in zip: {member.filename}")
        zf.extractall(dest_dir)
    return dest_dir

def safe_extract_tar(tar_path: Path, dest_dir: Path) -> Path:
    with tarfile.open(tar_path, "r:*") as tf:
        for member in tf.getmembers():
            target_path = dest_dir / member.name
            if not target_path.resolve().is_relative_to(dest_dir.resolve()):
                raise ValueError(f"Tar traversal security violation detected in member: {member.name}")
            # Symlink and hardlink members are rejected outright. A path check
            # on member.name alone does not stop a symlink inside the archive
            # pointing outside, with a later file written through that link.
            if member.issym() or member.islnk():
                raise ValueError(f"Symlink/hardlink member rejected in tar: {member.name} -> {member.linkname}")
        try:
            tf.extractall(dest_dir, filter="data")
        except TypeError:
            tf.extractall(dest_dir)
    return dest_dir

def find_skill_root(search_dir: Path) -> Path | None:
    # Check top-level
    if (search_dir / "SKILL.md").is_file():
        return search_dir
    # Check 1 level down
    for child in search_dir.iterdir():
        if child.is_dir() and (child / "SKILL.md").is_file():
            return child
    return None

def unpack_and_verify(package_path: str | Path) -> dict:
    source = Path(package_path).resolve()
    if not source.exists():
        return {"status": "FAIL", "error": f"Source path '{package_path}' does not exist."}

    is_archive = source.is_file() and (source.suffix in (".zip", ".gz", ".tar") or source.name.endswith(".tar.gz"))
    temp_dir = None

    try:
        if is_archive:
            temp_dir = Path(tempfile.mkdtemp(prefix="skill_install_"))
            if source.suffix == ".zip":
                safe_extract_zip(source, temp_dir)
            else:
                safe_extract_tar(source, temp_dir)
            skill_root = find_skill_root(temp_dir)
        else:
            skill_root = find_skill_root(source)

        if not skill_root:
            return {
                "status": "FAIL",
                "error": "No valid SKILL.md found in package root or first-level subdirectory."
            }

        # Run AST security scanner
        scan_res = scan_directory(skill_root)

        return {
            "status": scan_res["status"],
            "skill_root": str(skill_root),
            "temp_dir": str(temp_dir) if temp_dir else None,
            "security": scan_res
        }

    except Exception as e:
        if temp_dir and temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)
        return {"status": "FAIL", "error": str(e)}

def main():
    parser = argparse.ArgumentParser(description="Unpack and verify an AI agent skill package.")
    parser.add_argument("package_path", help="Path to .zip, .tar.gz, or uncompressed folder")
    args = parser.parse_args()

    result = unpack_and_verify(args.package_path)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result.get("status") == "PASS" else 1)

if __name__ == "__main__":
    main()
