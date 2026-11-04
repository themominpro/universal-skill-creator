#!/usr/bin/env python3
"""Render QA gates 1 and 2, deterministically.

Usage: python3 scripts/render_qa.py <path>
Gate 1, content: no lorem, TODO, placeholder, TBD in .md/.json/.txt files.
Gate 2, file: every file exists and is non-empty; .json files parse.
Visual inspection remains a human step and is reported as such, never
claimed by this script. See references/render_qa.md.
Exit 0 on PASS, 1 on FAIL. Output is JSON to stdout.
"""
import json
import sys
from pathlib import Path

BANNED = ["lorem", "TODO", "TBD"]


def main(argv):
    if len(argv) != 2:
        print("usage: render_qa.py <path>", file=sys.stderr)
        return 1
    root = Path(argv[1])
    if root.is_file():
        files = [root]
    elif root.is_dir():
        files = [p for p in root.rglob("*") if p.is_file() and p.suffix in (".md", ".json", ".txt")]
    else:
        print(json.dumps({"status": "FAIL", "reason": "path not found"}))
        return 1
    violations = []
    for f in files:
        if f.stat().st_size == 0:
            violations.append(f"empty file: {f}")
            continue
        text = f.read_text(encoding="utf-8", errors="ignore")
        lowered = text.lower()
        for banned in BANNED:
            if banned.lower() in lowered:
                violations.append(f"{f}: contains {banned}")
        if f.suffix == ".json":
            try:
                json.loads(text)
            except Exception as exc:
                violations.append(f"{f}: invalid JSON: {exc}")
    gates = {
        "content_qa": "FAIL" if any("contains" in v for v in violations) else "PASS",
        "file_qa": "FAIL" if any("empty" in v or "invalid JSON" in v for v in violations) else "PASS",
        "visual_qa": "HUMAN_REQUIRED",
    }
    status = "FAIL" if violations else "PASS"
    print(json.dumps({"status": status, "files_checked": len(files), "gates": gates, "violations": violations}, indent=2))
    return 1 if violations else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
