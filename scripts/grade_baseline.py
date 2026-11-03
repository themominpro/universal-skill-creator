#!/usr/bin/env python3
# Copyright (c) 2026 Momin / GTM Engineering. All rights reserved.
# Licensed under the Apache License, Version 2.0.

"""Validate a grader contract and, optionally, compare with vs baseline.

Usage:
  python3 scripts/grade_baseline.py <grading.json>
  python3 scripts/grade_baseline.py --with <with.json> --baseline <baseline.json>

Contract, exact (see references/baseline_grading.md and agents/grader.md):
each entry has exactly text, passed, evidence; passed is bool;
evidence is non-empty quoted text. A top-level eval_feedback block is
required. No partial credit is represented: passed must be true/false.

Ship gate, two-file mode only:
  with pass_rate >= 80, delta > 0, and no regression (an assertion
  that passed at baseline must not fail with-skill).
Exit 0 on PASS, 1 on FAIL. Output is JSON to stdout.
"""
import argparse
import json
import sys
from pathlib import Path


def load(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(data, dict):
        entries = data.get("entries") or data.get("grades") or data.get("assertions") or []
        feedback = data.get("eval_feedback")
    else:
        entries, feedback = data, None
    return entries, feedback


def validate(path):
    entries, feedback = load(path)
    violations = []
    if not isinstance(entries, list) or not entries:
        violations.append("no grading entries found")
        entries = []
    for i, entry in enumerate(entries):
        if not isinstance(entry, dict):
            violations.append(f"entry {i} is not an object")
            continue
        if set(entry.keys()) != {"text", "passed", "evidence"}:
            violations.append(f"entry {i} keys must be exactly text/passed/evidence, got {sorted(entry.keys())}")
        if not isinstance(entry.get("passed"), bool):
            violations.append(f"entry {i} passed must be true/false, no partial credit")
        ev = entry.get("evidence")
        if not isinstance(ev, str) or len(ev.strip()) < 10:
            violations.append(f"entry {i} evidence must be a non-empty quote")
        if not isinstance(entry.get("text"), str) or not entry.get("text", "").strip():
            violations.append(f"entry {i} text must be non-empty")
    if feedback is None:
        violations.append("eval_feedback block is missing")
    passed = sum(1 for e in entries if isinstance(e, dict) and e.get("passed") is True)
    total = len(entries)
    rate = round(100.0 * passed / total, 1) if total else 0.0
    return {"path": str(path), "total": total, "passed": passed, "pass_rate": rate, "violations": violations}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("grading", nargs="?")
    parser.add_argument("--with", dest="with_path")
    parser.add_argument("--baseline", dest="baseline_path")
    args = parser.parse_args()
    if args.with_path and args.baseline_path:
        with_r = validate(args.with_path)
        base_r = validate(args.baseline_path)
        violations = with_r["violations"] + base_r["violations"]
        delta = round(with_r["pass_rate"] - base_r["pass_rate"], 1)
        # Regression: same text passed at baseline, failed with-skill.
        base_map = {}
        try:
            entries, _ = load(args.baseline_path)
            for e in entries:
                if isinstance(e, dict):
                    base_map[e.get("text")] = e.get("passed")
            entries_w, _ = load(args.with_path)
            regressions = [e.get("text") for e in entries_w if isinstance(e, dict) and base_map.get(e.get("text")) is True and e.get("passed") is False]
        except Exception:
            regressions = []
        if with_r["pass_rate"] < 80:
            violations.append("ship gate: with-skill pass_rate below 80")
        if delta <= 0:
            violations.append("ship gate: with-skill must beat baseline, delta must be > 0")
        if regressions:
            violations.append(f"ship gate: regressions: {regressions}")
        status = "FAIL" if violations else "PASS"
        print(json.dumps({"status": status, "with_skill": with_r, "baseline": base_r, "delta": delta, "regressions": regressions, "violations": violations}, indent=2))
        return 1 if violations else 0
    if not args.grading:
        parser.print_usage(sys.stderr)
        return 1
    result = validate(args.grading)
    status = "FAIL" if result["violations"] else "PASS"
    print(json.dumps({"status": status, **result}, indent=2))
    return 1 if result["violations"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
