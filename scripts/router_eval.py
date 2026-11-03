#!/usr/bin/env python3
# Copyright (c) 2026 Momin / GTM Engineering. All rights reserved.
# Licensed under the Apache License, Version 2.0.

"""Deterministic router checks for a stub skill.

Usage: python3 scripts/router_eval.py <stub_SKILL.md> <cases.json> [<guide.md>]
Checks:
  - stub is 40-60 lines
  - stub contains a mandatory load command ("skills get") and the words
    "discovery stub"
  - stub contains no version number like 1.2.3
  - for each case, expectedPatterns regexes are found in stub+guide text,
    and forbiddenPatterns regexes are NOT found in stub+guide text
Exit 0 on PASS, 1 on FAIL. Output is JSON to stdout.
See references/stub_router_mode.md.
"""
import json
import re
import sys
from pathlib import Path


def main(argv):
    if len(argv) < 3:
        print("usage: router_eval.py <stub_SKILL.md> <cases.json> [<guide.md>]", file=sys.stderr)
        return 1
    stub = Path(argv[1]).read_text(encoding="utf-8", errors="ignore")
    cases_data = json.loads(Path(argv[2]).read_text(encoding="utf-8"))
    cases = cases_data["cases"] if isinstance(cases_data, dict) else cases_data
    guide = ""
    if len(argv) >= 4:
        guide = Path(argv[3]).read_text(encoding="utf-8", errors="ignore")
    combined = stub + "\n" + guide
    lines = stub.count("\n") + (1 if stub and not stub.endswith("\n") else 0)
    violations = []
    if not (40 <= lines <= 60):
        violations.append(f"stub must be 40-60 lines, got {lines}")
    if "skills get" not in stub:
        violations.append("stub must contain a mandatory load command with 'skills get'")
    if "discovery stub" not in stub.lower():
        violations.append("stub must state it is a discovery stub, not the usage guide")
    if re.search(r"\d+\.\d+\.\d+", stub):
        violations.append("stub must not contain a version number")
    results = []
    for case in cases:
        expected = case.get("expectedPatterns", [])
        forbidden = case.get("forbiddenPatterns", [])
        missing = [p for p in expected if not re.search(p, combined)]
        found_forbidden = [p for p in forbidden if re.search(p, combined)]
        ok = not missing and not found_forbidden
        results.append({"id": case.get("id"), "passed": ok, "missing_expected": missing, "found_forbidden": found_forbidden})
        if not ok:
            violations.append(f"case {case.get('id')} failed")
    status = "FAIL" if violations else "PASS"
    print(json.dumps({"status": status, "stub_lines": lines, "cases": results, "violations": violations}, indent=2))
    return 1 if violations else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
