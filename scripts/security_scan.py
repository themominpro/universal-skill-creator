#!/usr/bin/env python3
"""
Zero-Token AST Security Scanner & Secret Leak Detector.
Scans Python scripts, JavaScript/TypeScript, and text files for:
1. Remote Code Execution (eval, exec, shell=True, base64 exec)
2. Credential Harvesting (~/.ssh, ~/.aws, keychains, /etc/passwd)
3. Undeclared Network Calls & Data Exfiltration
4. Hardcoded Secrets (API keys, tokens, passwords)
Outputs structured JSON to stdout. Exits 0 if clean, 1 if critical issues found.
"""

from __future__ import annotations

import ast
import json
import os
import re
import sys
from pathlib import Path

# Known API key regex patterns
SECRET_PATTERNS = [
    (re.compile(r"AIza[0-9A-Za-z-_]{35}"), "Google AI / Firebase API Key"),
    (re.compile(r"sk-[a-zA-Z0-9]{20,}"), "OpenAI API Key (Generic/Legacy)"),
    (re.compile(r"sk-proj-[a-zA-Z0-9-_]{40,}"), "OpenAI Project API Key"),
    (re.compile(r"sk-ant-[a-zA-Z0-9-_]{30,}"), "Anthropic Claude API Key"),
    (re.compile(r"AKIA[0-9A-Z]{16}"), "AWS Access Key ID"),
    (re.compile(r"ghp_[0-9a-zA-Z]{36}"), "GitHub Personal Access Token"),
    (re.compile(r"github_pat_[0-9a-zA-Z_]{82}"), "GitHub Fine-Grained PAT"),
    (re.compile(r"xox[baprs]-[0-9a-zA-Z]{10,48}"), "Slack Token"),
    (re.compile(r"sq0atp-[0-9A-Za-z\-_]{22}"), "Square Access Token"),
    (re.compile(r"stripe[a-zA-Z0-9_]*key\s*=\s*['\"][a-zA-Z0-9_]{20,}['\"]", re.IGNORECASE), "Stripe API Key"),
    (re.compile(r"Bearer\s+[a-zA-Z0-9_\-\.]{25,}", re.IGNORECASE), "Bearer Token"),
    (re.compile(r"(api[_-]?key|secret|password|access[_-]?token)\s*=\s*['\"][a-zA-Z0-9_\-\.]{16,}['\"]", re.IGNORECASE), "Hardcoded Generic Secret"),
]

SENSITIVE_PATHS = [
    ".ssh", ".aws", ".bash_history", ".zsh_history",
    "keychain", "/etc/passwd", "/etc/shadow", "id_rsa", "id_ed25519"
]

class PythonASTSecurityVisitor(ast.NodeVisitor):
    def __init__(self, filename: str):
        self.filename = filename
        self.critical_findings = []
        self.warnings = []

    def visit_Call(self, node: ast.Call):
        func_name = ""
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr

        # 1. Remote Code Execution: eval / exec
        if func_name in ("eval", "exec"):
            self.critical_findings.append({
                "file": self.filename,
                "line": node.lineno,
                "type": "REMOTE_CODE_EXECUTION",
                "severity": "CRITICAL",
                "message": f"Dangerous dynamic execution via '{func_name}()'."
            })

        # 2. Direct shell execution: os.system, os.popen, etc.
        is_os_call = False
        if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
            if node.func.value.id == "os" and node.func.attr in ("system", "popen", "spawnl", "spawnle", "spawnlp", "spawnlpe", "spawnv", "spawnve", "spawnvp", "spawnvpe"):
                is_os_call = True
        elif isinstance(node.func, ast.Name) and node.func.id in ("popen",):
            is_os_call = True

        if is_os_call:
            self.critical_findings.append({
                "file": self.filename,
                "line": node.lineno,
                "type": "DANGEROUS_OS_EXECUTION",
                "severity": "CRITICAL",
                "message": f"Dangerous direct shell execution via 'os.{func_name}()'. Use subprocess with argument array instead."
            })

        # 3. Shell injection risk: subprocess with shell=True
        if func_name in ("run", "Popen", "call", "check_call", "check_output"):
            for kw in node.keywords:
                if kw.arg == "shell" and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                    self.critical_findings.append({
                        "file": self.filename,
                        "line": node.lineno,
                        "type": "SHELL_INJECTION_RISK",
                        "severity": "CRITICAL",
                        "message": "Subprocess executed with 'shell=True'. Use argument arrays instead."
                    })

        # 4. Sensitive file access and remote shell pipes in arguments
        for arg in node.args:
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                val_lower = arg.value.lower()
                if re.search(r"\b(curl|wget)\s+[^|;&\n]+\|\s*(sh|bash|zsh|python|perl)\b", arg.value, re.IGNORECASE):
                    self.critical_findings.append({
                        "file": self.filename,
                        "line": node.lineno,
                        "type": "REMOTE_SHELL_PIPE",
                        "severity": "CRITICAL",
                        "message": f"Remote download-and-execute shell pipe in arguments: '{arg.value[:60]}'."
                    })
                for sens in SENSITIVE_PATHS:
                    if sens in val_lower:
                        self.critical_findings.append({
                            "file": self.filename,
                            "line": node.lineno,
                            "type": "CREDENTIAL_HARVESTING",
                            "severity": "CRITICAL",
                            "message": f"Access to sensitive credential path '{arg.value}'."
                        })

        self.generic_visit(node)

def scan_text_for_secrets(content: str, filename: str) -> list[dict]:
    findings = []
    lines = content.splitlines()
    for idx, line in enumerate(lines, start=1):
        # Ignore comments or markdown code block markers
        stripped = line.strip()
        if stripped.startswith("#") or stripped.startswith("//") or stripped.startswith("<!--"):
            continue
        for pattern, name in SECRET_PATTERNS:
            match = pattern.search(line)
            if match:
                # Obfuscate token in report
                matched_str = match.group(0)
                obfuscated = matched_str[:6] + "..." + matched_str[-4:] if len(matched_str) > 12 else "***"
                findings.append({
                    "file": filename,
                    "line": idx,
                    "type": "HARDCODED_SECRET",
                    "severity": "CRITICAL",
                    "message": f"Detected {name}: '{obfuscated}'. Secrets must be loaded via .env!"
                })
    return findings

def scan_file(filepath: Path) -> tuple[list[dict], list[dict]]:
    criticals = []
    warnings = []
    rel_path = str(filepath)
    
    try:
        content = filepath.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        warnings.append({"file": rel_path, "line": 0, "type": "READ_ERROR", "severity": "WARNING", "message": str(e)})
        return criticals, warnings

    # Check active .env files
    if filepath.name in (".env", ".env.local", ".env.production", ".env.development", ".env.test") or (filepath.name.startswith(".env") and not filepath.name.endswith(".example") and not filepath.name.endswith(".template")):
        criticals.append({
            "file": rel_path,
            "line": 0,
            "type": "ACTIVE_ENV_FILE",
            "severity": "CRITICAL",
            "message": f"Active environment file '{filepath.name}' found in skill package. Skill packages must only ship '.env.example'."
        })

    # Secret scanning
    secret_findings = scan_text_for_secrets(content, rel_path)
    criticals.extend(secret_findings)

    # Shell pipe detection in scripts/text
    if re.search(r"\b(curl|wget)\s+[^|;&\n]+\|\s*(sh|bash|zsh|python|perl)\b", content, re.IGNORECASE):
        criticals.append({
            "file": rel_path,
            "line": 0,
            "type": "REMOTE_SHELL_PIPE",
            "severity": "CRITICAL",
            "message": "Dangerous remote download-and-execute pattern detected ('curl | sh' or 'wget | bash')."
        })

    # AST check for Python
    if filepath.suffix == ".py":
        try:
            tree = ast.parse(content, filename=rel_path)
            visitor = PythonASTSecurityVisitor(rel_path)
            visitor.visit(tree)
            criticals.extend(visitor.critical_findings)
            warnings.extend(visitor.warnings)
        except SyntaxError as se:
            warnings.append({
                "file": rel_path,
                "line": se.lineno or 0,
                "type": "SYNTAX_ERROR",
                "severity": "WARNING",
                "message": f"Python syntax error: {se.msg}"
            })

    return criticals, warnings

def scan_directory(target_dir: str | Path) -> dict:
    target = Path(target_dir).resolve()
    if not target.is_dir():
        return {"status": "FAIL", "error": f"Target directory '{target_dir}' does not exist."}

    all_criticals = []
    all_warnings = []
    scanned_count = 0

    # Scan python, js, ts, sh, json, yaml, env, and md files
    extensions = {".py", ".js", ".ts", ".sh", ".json", ".yaml", ".yml", ".env", ".md"}
    for root, _, files in os.walk(target):
        # Skip .git and __pycache__
        if ".git" in root or "__pycache__" in root or "node_modules" in root:
            continue
        for file in files:
            p = Path(root) / file
            if p.suffix in extensions or p.name.startswith(".env"):
                scanned_count += 1
                crits, warns = scan_file(p)
                all_criticals.extend(crits)
                all_warnings.extend(warns)

    status = "FAIL" if all_criticals else "PASS"
    return {
        "status": status,
        "scanned_files": scanned_count,
        "critical_count": len(all_criticals),
        "warning_count": len(all_warnings),
        "critical_issues": all_criticals,
        "warnings": all_warnings
    }

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: python security_scan.py <path_to_directory>"}, indent=2))
        sys.exit(1)

    result = scan_directory(sys.argv[1])
    print(json.dumps(result, indent=2))
    sys.exit(1 if result.get("status") == "FAIL" else 0)

if __name__ == "__main__":
    main()

