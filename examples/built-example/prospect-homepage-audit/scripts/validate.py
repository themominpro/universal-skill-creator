#!/usr/bin/env python3
"""Validate one prospect homepage audit record.

Usage: python3 scripts/validate.py path/to/prospect.json
Exit 0 on pass, 1 on fail. Output is compact JSON, no extra prose.
"""
import json
import sys
from pathlib import Path
from urllib.parse import urlparse


def main() -> int:
    if len(sys.argv) != 2:
        print(json.dumps({"status": "FAIL", "errors": ["Usage: python3 scripts/validate.py path/to/prospect.json"]}))
        return 1
    path = Path(sys.argv[1])
    if not path.is_file():
        print(json.dumps({"status": "FAIL", "errors": [f"File not found: {path}"]}))
        return 1
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(json.dumps({"status": "FAIL", "errors": [f"Invalid JSON: {exc}"]}))
        return 1
    errors = []
    if not isinstance(record, dict):
        print(json.dumps({"status": "FAIL", "errors": ["Record must be a JSON object"]}))
        return 1
    if not record.get("name") or not isinstance(record.get("name"), str):
        errors.append("name is required and must be a string")
    website = record.get("website", "")
    if website not in ("Unknown", ""):
        parsed = urlparse(website)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            errors.append("website must be a full http or https URL, or Unknown")
    verdict = record.get("verdict")
    if verdict not in ("Pitch", "Skip", "Unknown"):
        errors.append("verdict must be Pitch, Skip, or Unknown")
    evidence = record.get("evidence", "")
    if verdict in ("Pitch", "Skip") and (not evidence or len(evidence.strip()) < 10):
        errors.append("evidence is required for Pitch and Skip verdicts and must be at least 10 characters")
    pitch_angle = record.get("pitch_angle", "")
    if verdict == "Pitch" and (not pitch_angle or len(pitch_angle.strip()) < 10):
        errors.append("pitch_angle is required for Pitch verdicts and must be at least 10 characters")
    if verdict == "Skip" and pitch_angle:
        errors.append("pitch_angle must be empty for Skip verdicts: do not pitch a good homepage")
    if errors:
        print(json.dumps({"status": "FAIL", "errors": errors}))
        return 1
    print(json.dumps({"status": "PASS", "verdict": verdict}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
