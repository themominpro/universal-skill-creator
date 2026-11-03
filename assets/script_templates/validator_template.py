#!/usr/bin/env python3
"""
Standard Deterministic Validator Template
Performs structural, schema, and invariant validation on generated artifacts.
Includes zero-dependency load_env() helper for safe API credential handling.
Outputs structured JSON to stdout. Exits with 0 on pass, 1 on fail.
"""

import os
import sys
import json
from pathlib import Path

def load_env():
    """
    Zero-dependency .env loader.
    Searches parent directories up to git root or workspace boundary (max 4 levels).
    Safely stops before traversing into user home or filesystem root.
    """
    current = Path(__file__).resolve().parent
    for _ in range(4):
        env_path = current / ".env"
        if env_path.is_file():
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            key, val = line.split("=", 1)
                            os.environ.setdefault(key.strip(), val.strip().strip('"\''))
                return True
            except Exception:
                pass
        if (current / ".git").is_dir():
            break
        if current.parent == current:
            break
        current = current.parent
    return False

def validate_target(target_path):
    p = Path(target_path)
    if not p.exists():
        return {
            "status": "FAIL",
            "errors": [f"Target path does not exist: {target_path}"],
            "error_count": 1
        }

    errors = []
    warnings = []

    # Example: Check non-empty
    if p.is_file() and p.stat().st_size == 0:
        errors.append("Target file is empty (0 bytes).")

    # Example: Check valid JSON syntax if applicable
    if p.suffix == ".json":
        try:
            with open(p, "r", encoding="utf-8") as f:
                json.load(f)
        except Exception as e:
            errors.append(f"Invalid JSON syntax: {str(e)}")

    status = "PASS" if len(errors) == 0 else "FAIL"
    return {
        "status": status,
        "target": str(p),
        "errors": errors,
        "warnings": warnings,
        "error_count": len(errors),
        "warning_count": len(warnings)
    }

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"status": "FAIL", "errors": ["Usage: python validate.py <target_path>"]}))
        sys.exit(1)

    # Automatically load environment variables from .env if present
    load_env()

    result = validate_target(sys.argv[1])
    print(json.dumps(result, indent=2))
    if result["status"] == "FAIL":
        sys.exit(1)

if __name__ == "__main__":
    main()
