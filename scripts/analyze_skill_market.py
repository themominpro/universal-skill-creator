#!/usr/bin/env python3
"""Validate a competitive landscape record and emit research gaps."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

REQUIRED = {
    "name", "source", "audience", "job", "architecture", "workflow",
    "strengths", "weaknesses", "evidence_quality"
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit a skill market landscape")
    parser.add_argument("landscape", type=Path)
    args = parser.parse_args()
    data = json.loads(args.landscape.read_text(encoding="utf-8-sig"))
    entries = data.get("comparables", [])
    findings = []
    if len(entries) < 3:
        findings.append("Fewer than three comparables; record the search boundary and uncertainty.")
    for index, entry in enumerate(entries):
        missing = sorted(REQUIRED - set(entry))
        if missing:
            findings.append(f"comparable {index} missing: {', '.join(missing)}")
        if not entry.get("source"):
            findings.append(f"comparable {index} has no source")
        if not entry.get("weaknesses"):
            findings.append(f"comparable {index} has no weakness analysis")
    result = {
        "status": "needs_research" if findings else "ready_for_synthesis",
        "comparables": len(entries),
        "findings": findings,
        "next_step": "Complete evidence and differentiation brief before authoring." if findings else "Proceed to differentiation and architecture."
    }
    print(json.dumps(result, indent=2))
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
