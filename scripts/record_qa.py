#!/usr/bin/env python3
"""Record one QA checkpoint, deterministically.

Usage: python3 scripts/record_qa.py <output_json> --checkpoint <name> --summary <text> [--question <text> ...] [--confirmed|--assumed]
Rules from references/qa_checkpoints.md:
  - checkpoint name must be one of the 5 defined checkpoints
  - at most 2 questions
  - summary must be non-empty
Output is JSON to stdout and the record is appended to output_json.
Exit 0 on PASS, 1 on FAIL.
"""
import argparse
import json
import sys
from pathlib import Path

CHECKPOINTS = {
    "teardown-domain",
    "architecture",
    "draft-workflow",
    "gates",
    "ship",
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("output")
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--question", action="append", default=[])
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--confirmed", action="store_true")
    group.add_argument("--assumed", action="store_true")
    args = parser.parse_args()
    violations = []
    if args.checkpoint not in CHECKPOINTS:
        violations.append(f"unknown checkpoint {args.checkpoint}, must be one of {sorted(CHECKPOINTS)}")
    if not args.summary.strip():
        violations.append("summary must be non-empty")
    if len(args.question) > 2:
        violations.append("at most 2 questions per checkpoint")
    record = {
        "checkpoint": args.checkpoint,
        "summary": args.summary,
        "questions": args.question,
        "status": "confirmed" if args.confirmed else "assumed-default",
    }
    out = Path(args.output)
    existing = []
    if out.exists():
        try:
            existing = json.loads(out.read_text(encoding="utf-8"))
            if not isinstance(existing, list):
                existing = []
        except Exception:
            existing = []
    if not violations:
        existing.append(record)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(existing, indent=2), encoding="utf-8")
    status = "FAIL" if violations else "PASS"
    print(json.dumps({"status": status, "record": record, "violations": violations, "output": str(out)}, indent=2))
    return 1 if violations else 0


if __name__ == "__main__":
    raise SystemExit(main())
