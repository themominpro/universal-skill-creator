#!/usr/bin/env python3
"""
Empirical Skill Evaluation & Benchmark Runner.
Executes test cases defined in evals/cases.json, runs validation scripts,
and measures empirical assertion pass rates.
Outputs structured JSON to stdout and writes results to evals/results.json.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

SAMPLE_CASES = [
    {
        "id": "case-01-audit-clean",
        "name": "Audit Self-Integrity Check",
        "description": "Verifies that the skill passes structural 26-smell audit with 0 violations",
        "command": "python scripts/audit_skill.py .",
        "expected_exit_code": 0,
        "required_output_substrings": ["\"grade\": \"A+\"", "\"status\": \"PASS\""]
    },
    {
        "id": "case-02-security-scan",
        "name": "Security & Secret Leak Scan",
        "description": "Verifies that scripts contain no dangerous execution or hardcoded tokens",
        "command": "python scripts/security_scan.py .",
        "expected_exit_code": 0,
        "required_output_substrings": ["\"critical_count\": 0", "\"status\": \"PASS\""]
    }
]

def init_evals(skill_dir: Path) -> dict:
    eval_dir = skill_dir / "evals"
    eval_dir.mkdir(parents=True, exist_ok=True)
    cases_file = eval_dir / "cases.json"
    if not cases_file.is_file():
        cases_file.write_text(json.dumps(SAMPLE_CASES, indent=2), encoding="utf-8")
        return {"status": "INITIALIZED", "path": str(cases_file), "message": "Created evals/cases.json template."}
    return {"status": "EXISTS", "path": str(cases_file), "message": "evals/cases.json already exists."}

def run_evaluations(skill_dir: Path) -> dict:
    eval_dir = skill_dir / "evals"
    cases_file = eval_dir / "cases.json"

    if not cases_file.is_file():
        # Auto-initialize template
        init_evals(skill_dir)
        return {
            "status": "INITIALIZED",
            "message": "No test cases found. Initialized evals/cases.json. Add domain test cases and re-run.",
            "total_cases": 0,
            "pass_rate": 0.0
        }

    try:
        cases = json.loads(cases_file.read_text(encoding="utf-8"))
    except Exception as e:
        return {"status": "FAIL", "error": f"Failed to parse evals/cases.json: {e}"}

    results = []
    passed_count = 0

    for case in cases:
        cid = case.get("id", "unknown")
        cmd_str = case.get("command") or case.get("validator_command")
        expected_code = case.get("expected_exit_code", 0)
        required_substrings = case.get("required_output_substrings", [])
        expected_artifacts = case.get("expected_artifacts", [])
        
        # Check artifact existence
        artifacts_ok = True
        missing_art = []
        for art in expected_artifacts:
            art_path = skill_dir / art
            if not art_path.exists():
                artifacts_ok = False
                missing_art.append(art)

        # Run command if specified
        cmd_ok = True
        cmd_output = ""
        missing_assertions = []
        if cmd_str:
            try:
                import shlex
                cmd_args = shlex.split(cmd_str) if isinstance(cmd_str, str) else cmd_str
                if cmd_args and cmd_args[0] in ("python", "python3"):
                    cmd_args[0] = sys.executable
                proc = subprocess.run(cmd_args, cwd=str(skill_dir), capture_output=True, text=True)
                code_matches = (proc.returncode == expected_code)
                cmd_output = proc.stdout.strip() or proc.stderr.strip()
                
                # Check required substrings
                for sub in required_substrings:
                    if sub not in cmd_output:
                        missing_assertions.append(sub)

                cmd_ok = code_matches and (len(missing_assertions) == 0)
            except Exception as e:
                cmd_ok = False
                cmd_output = str(e)

        case_passed = artifacts_ok and cmd_ok
        if case_passed:
            passed_count += 1

        # Sanitize absolute paths from output snippet to avoid local path leakage
        sanitized_snippet = cmd_output
        sdir_str = str(skill_dir)
        sanitized_snippet = sanitized_snippet.replace(sdir_str, ".")
        sanitized_snippet = sanitized_snippet.replace(sdir_str.replace("\\", "\\\\"), ".")
        sanitized_snippet = sanitized_snippet.replace(sdir_str.replace("\\", "/"), ".")
        home_str = str(Path.home())
        if home_str:
            sanitized_snippet = sanitized_snippet.replace(home_str, "~")
            sanitized_snippet = sanitized_snippet.replace(home_str.replace("\\", "\\\\"), "~")
            sanitized_snippet = sanitized_snippet.replace(home_str.replace("\\", "/"), "~")

        results.append({
            "id": cid,
            "name": case.get("name", cid),
            "command_executed": cmd_str,
            "exit_code_matched": (proc.returncode == expected_code) if cmd_str else True,
            "missing_assertions": missing_assertions,
            "missing_artifacts": missing_art,
            "output_snippet": sanitized_snippet[:120] if sanitized_snippet else "OK",
            "status": "PASS" if case_passed else "FAIL"
        })

    total = len(cases)
    pass_rate = round((passed_count / total) * 100, 1) if total > 0 else 0.0

    eval_summary = {
        "status": "PASS" if passed_count == total else "FAIL",
        "total_cases": total,
        "passed_cases": passed_count,
        "failed_cases": total - passed_count,
        "pass_rate": pass_rate,
        "cases": results
    }

    # Save real verified results
    results_file = eval_dir / "results.json"
    results_file.write_text(json.dumps(eval_summary, indent=2), encoding="utf-8")

    return eval_summary

def main():
    parser = argparse.ArgumentParser(description="Run empirical evaluations on an AI agent skill.")
    parser.add_argument("skill_dir", help="Path to the skill directory")
    parser.add_argument("--init", action="store_true", help="Initialize evals/cases.json template")
    args = parser.parse_args()

    sdir = Path(args.skill_dir).resolve()
    if args.init:
        res = init_evals(sdir)
        print(json.dumps(res, indent=2))
        sys.exit(0)

    res = run_evaluations(sdir)
    print(json.dumps(res, indent=2))
    sys.exit(0 if res.get("status") == "PASS" else 1)

if __name__ == "__main__":
    main()
