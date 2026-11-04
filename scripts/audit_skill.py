#!/usr/bin/env python3
"""
Zero-Token Structural Skill Linter & Layout Conformance Auditor.
Performs deep structural, syntactic, and AST verification against:
1. agentskills.io specification (byte-0, frontmatter schema, triggers, exclusions)
2. Agentic Smell Taxonomy (RL, TOB, MUS, LSB, NPT, TSW, NG, MDT)
3. AST code safety & secret leak detection (no eval/exec, shell=True, hardcoded tokens)
Outputs structured JSON to stdout. Exits 0 on PASS (Grade A/A+), 1 on FAIL.
"""

from __future__ import annotations

import ast
import json
import os
import re
import sys
from pathlib import Path

VAGUE_DESCRIPTION_PATTERNS = [
    re.compile(r"\bhelps? with various things\b", re.IGNORECASE),
    re.compile(r"\bdoes stuff\b", re.IGNORECASE),
    re.compile(r"\bgeneral assistant\b", re.IGNORECASE),
    re.compile(r"\bvarious tasks\b", re.IGNORECASE),
    re.compile(r"\bgeneral purpose\b", re.IGNORECASE),
    re.compile(r"\bmiscellaneous\b", re.IGNORECASE),
]

SECRET_PATTERNS = [
    (re.compile(r"AIza[0-9A-Za-z-_]{35}"), "Google AI / Firebase API Key"),
    (re.compile(r"sk-[a-zA-Z0-9]{20,}"), "OpenAI API Key (Generic/Legacy)"),
    (re.compile(r"sk-proj-[a-zA-Z0-9-_]{40,}"), "OpenAI Project API Key"),
    (re.compile(r"sk-ant-[a-zA-Z0-9-_]{30,}"), "Anthropic Claude API Key"),
    (re.compile(r"AKIA[0-9A-Z]{16}"), "AWS Access Key ID"),
    (re.compile(r"ghp_[0-9a-zA-Z]{36}"), "GitHub Personal Access Token"),
    (re.compile(r"Bearer\s+['\"][a-zA-Z0-9_\-\.]{16,}['\"]"), "Hardcoded Bearer Token"),
]

def parse_markdown_tables(text: str) -> list[dict]:
    """Extracts all markdown tables and their parsed headers and rows."""
    tables = []
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        # Look for table header and separator
        if "|" in line and i + 1 < len(lines):
            sep = lines[i+1].strip()
            if re.match(r"^\|?(\s*:?-+:?\s*\|)+\s*:?-+:?\s*\|?$", sep):
                headers = [h.strip().lower() for h in line.strip("|").split("|")]
                rows = []
                j = i + 2
                while j < len(lines) and "|" in lines[j] and lines[j].strip():
                    row_cells = [c.strip() for c in lines[j].strip("|").split("|")]
                    rows.append(row_cells)
                    j += 1
                tables.append({"headers": headers, "rows": rows, "start_line": i + 1})
                i = j
                continue
        i += 1
    return tables

def audit_frontmatter(content: str, skill_dir: Path) -> tuple[dict, list[dict], list[dict]]:
    violations = []
    warnings = []

    # 1. Byte-0 Check
    if not content.startswith("---"):
        violations.append({
            "code": "SPEC-01",
            "smell": "Byte-0 Delimiter Missing",
            "message": "SKILL.md must start with '---' at byte 0. Leading blank lines or characters are forbidden."
        })
        return {}, violations, warnings

    parts = content.split("---", 2)
    if len(parts) < 3:
        violations.append({
            "code": "SPEC-02",
            "smell": "Malformed Frontmatter",
            "message": "Frontmatter is not closed with a second '---' delimiter."
        })
        return {}, violations, warnings

    yaml_text = parts[1]

    # 2. Angle Brackets Injection Check
    for idx, line in enumerate(yaml_text.splitlines(), start=1):
        if re.match(r"^[a-zA-Z_-]+:\s*>-?\s*$", line.strip()):
            continue
        if "<" in line or ">" in line:
            violations.append({
                "code": "SPEC-03",
                "smell": "Illegal Angle Brackets",
                "message": f"Line {idx} in frontmatter contains '<' or '>', which triggers prompt injection filters."
            })

    # 3. Parse Metadata
    metadata = {}
    name_m = re.search(r"^name:\s*([a-zA-Z0-9_-]+)", yaml_text, re.MULTILINE)
    if name_m:
        metadata["name"] = name_m.group(1).strip()
    else:
        violations.append({
            "code": "SPEC-NAME-01",
            "smell": "Missing Name",
            "message": "Frontmatter missing required 'name' field."
        })

    name = metadata.get("name", "")
    if name:
        if not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", name):
            violations.append({
                "code": "SPEC-NAME-02",
                "smell": "Invalid Name Format",
                "message": f"Name '{name}' violates spec: must be lowercase alphanumeric with single hyphens."
            })
        if len(name) > 64:
            violations.append({"code": "LSN", "smell": "Lengthy Skill Name", "message": "Name exceeds 64 chars."})
        
        expected_dir = skill_dir.resolve().name
        if name != expected_dir:
            warnings.append({
                "code": "SPEC-NAME-03",
                "smell": "Folder Name Parity Mismatch",
                "message": f"Skill name '{name}' does not match directory '{expected_dir}'."
            })

    # 4. Accurate YAML Description Parser (handles block scalars >-, |, etc.)
    lines = yaml_text.splitlines()
    in_desc = False
    desc_lines = []
    for line in lines:
        if re.match(r"^description:\s*", line):
            in_desc = True
            val = re.sub(r"^description:\s*(?:>-?|\|-?)?", "", line).strip()
            if val:
                desc_lines.append(val)
            continue
        if in_desc:
            if re.match(r"^[a-zA-Z0-9_-]+:\s*", line) and not line.startswith("  "):
                break
            desc_lines.append(line.strip())
    desc = " ".join([l for l in desc_lines if l]).strip()
    metadata["description"] = desc

    if not desc:
        violations.append({"code": "SPEC-DESC-01", "smell": "Missing Description", "message": "Frontmatter missing required 'description'."})
    else:
        if len(desc) < 40:
            violations.append({
                "code": "CSD-VAGUE",
                "smell": "Vague / Minimal Description",
                "message": f"Description is only {len(desc)} characters. It must explain what the skill does and when to use it."
            })
        for vpat in VAGUE_DESCRIPTION_PATTERNS:
            if vpat.search(desc):
                violations.append({
                    "code": "CSD-VAGUE-PHRASE",
                    "smell": "Generic / Uninformative Description",
                    "message": f"Description contains vague non-operational phrasing: '{vpat.pattern}'."
                })
        if len(desc) > 1024:
            violations.append({"code": "LSD", "smell": "Lengthy Skill Description", "message": f"Description exceeds 1,024 chars ({len(desc)} chars)."})

        desc_lower = desc.lower()
        if not any(k in desc_lower for k in ["use this skill", "trigger on", "when", "use when", "whenever"]):
            violations.append({
                "code": "CSD-NO-TRIGGER",
                "smell": "Missing Trigger Directive",
                "message": "Description lacks imperative trigger phrasing ('Use this skill when...', 'Trigger on:...')."
            })
        if not any(k in desc_lower for k in ["do not use for", "not use for", "out of scope", "excludes", "never use"]):
            warnings.append({
                "code": "CSD-NO-EXCLUSION",
                "smell": "Missing Negative Boundary",
                "message": "Description lacks negative scope boundary ('Do NOT use for...'). May cause trigger collisions."
            })

    # 5. Secret Hygiene (.env.example check)
    if "requires_secrets:" in yaml_text:
        env_example = skill_dir / ".env.example"
        if not env_example.is_file():
            violations.append({
                "code": "MISSING-ENV-EXAMPLE",
                "smell": "Missing .env.example Template",
                "message": "Skill declares 'requires_secrets' but is missing companion '.env.example' in root."
            })

    return metadata, violations, warnings

def audit_body(content: str, skill_dir: Path) -> tuple[list[dict], list[dict]]:
    violations = []
    warnings = []

    parts = content.split("---", 2)
    body = parts[2] if len(parts) >= 3 else content
    lines = body.splitlines()
    line_count = len(lines)
    word_count = len(body.split())

    # LSB: Lengthy Skill Body
    if line_count > 500:
        violations.append({"code": "LSB", "smell": "Lengthy Skill Body", "message": f"Body has {line_count} lines (>500 lines). Severe risk of compaction shearing."})
    if word_count > 4000:
        warnings.append({"code": "LSB-TOKENS", "smell": "High Token Load", "message": f"Body has ~{word_count} words (>4,000 words). Delegate playbooks to references/."})

    tables = parse_markdown_tables(body)
    body_lower = body.lower()

    # 1. Rationalization Guardrails Check (RL)
    # Accepts structured Anti-Rationalization Table, Excuses-to-Reject Table, or Non-Negotiables / Guardrails section
    rl_found = False
    for t in tables:
        h_str = " ".join(t["headers"])
        if any(k in h_str for k in ["excuse", "rationalization", "why", "rule", "wrong", "trap", "guardrail"]):
            if any(k in h_str for k in ["action", "forbidden", "why", "guardrail", "fix", "template", "wrong"]):
                if len(t["rows"]) >= 2:
                    rl_found = True
                    break
    if not rl_found:
        # Check for dedicated non-negotiables / guardrails / traps section with >=2 items
        rule_matches = re.findall(r"(?:###?|\*\*)\s*(?:non-negotiable|guardrail|rule|trap|footgun|gotcha|excuse)", body_lower)
        bullet_items = re.findall(r"^\s*(?:\d+\.|\*|-)\s+.*", body, re.MULTILINE)
        if rule_matches and len(bullet_items) >= 2:
            rl_found = True

    if not rl_found:
        violations.append({
            "code": "RL",
            "smell": "Rationalization Loophole",
            "message": "Missing explicit guardrails against model cutting corners. Add an Anti-Rationalization table or a 'Non-Negotiables / Guardrails' section."
        })

    # 2. Decision & Task Routing Table Check (TOB / MDT)
    # Required if the skill offers multiple options, workflows, tiers, or tools
    has_multiple_paths = bool(re.search(r"\b(tier|workflow|option|alternative|when to use which|approach)\b", body_lower))
    routing_table_found = False
    for t in tables:
        h_str = " ".join(t["headers"])
        if any(k in h_str for k in ["scenario", "intent", "task", "situation", "tier", "use for", "workflow"]):
            if any(k in h_str for k in ["tool", "approach", "action", "workflow", "template", "script"]):
                if len(t["rows"]) >= 2:
                    routing_table_found = True
                    break

    if has_multiple_paths and not routing_table_found:
        violations.append({
            "code": "MDT",
            "smell": "Missing Decision / Routing Table",
            "message": "Skill presents multiple workflows/tiers but lacks a decision table mapping scenarios to default approaches."
        })

    # 3. Checklists & Phasing (NPT & TSW)
    has_checklist = "- [ ]" in content
    phase_matches = re.findall(r"(?:###?|\*\*|\d+\.)\s*(?:step|phase|\d+[\.\)])\s*", body_lower)
    numbered_steps = re.findall(r"^\s*\d+\.\s+.*", body, re.MULTILINE)
    total_steps = len(phase_matches) + len(numbered_steps)

    if total_steps >= 4 and not has_checklist:
        warnings.append({
            "code": "NPT",
            "smell": "No Progress Tracking",
            "message": "Multi-step workflow (>=4 steps) lacks copyable '- [ ]' checklist. Recommend adding a checklist to prevent skipped steps."
        })

    if total_steps < 2:
        violations.append({
            "code": "TSW",
            "smell": "The Stepless Workflow",
            "message": "Workflow is not decomposed into actionable steps (minimum 2 steps required)."
        })

    # 4. Exclusions / Guardrails Section (NG)
    # Check if negative scope boundary is declared in frontmatter description OR in body
    ng_found = False
    desc_str = content.split("---")[1] if len(content.split("---")) >= 3 else ""
    if any(k in desc_str.lower() for k in ["do not use", "not for", "out of scope", "excludes", "never use"]):
        ng_found = True
    elif any(k in body_lower for k in ["not do", "out of scope", "exclusions", "do not use", "never use"]):
        ng_found = True

    if not ng_found:
        violations.append({
            "code": "NG",
            "smell": "No Guardrails (Missing Exclusions)",
            "message": "Missing negative scope boundary. Declare what the skill does NOT do in description or in a dedicated section."
        })

    # 5. Flat References Check (No Multi-Hop ../)
    nested_links = re.findall(r"\]\((?!https?://|\w+://)([^)]+)\)", body)
    for link in nested_links:
        clean = link.split("#")[0].strip()
        if "../" in clean or clean.startswith(".."):
            violations.append({
                "code": "DEEP-REF",
                "smell": "Multi-Hop Reference Traversal",
                "message": f"Reference link '{link}' traverses parent directories. References must be flat (1-hop deep)."
            })

    return violations, warnings

def audit_scripts(skill_dir: Path) -> tuple[list[dict], list[dict], list[str]]:
    violations = []
    warnings = []
    scripts_dir = skill_dir / "scripts"
    detected_scripts = []

    if not scripts_dir.is_dir():
        violations.append({
            "code": "MUS",
            "smell": "Missing Utility Scripts (MUS)",
            "message": "Skill directory is missing mandatory 'scripts/' directory. Deterministic gates must reside in executable code."
        })
        return violations, warnings, detected_scripts

    script_files = [f for f in scripts_dir.iterdir() if f.is_file() and f.suffix in (".py", ".js", ".ts", ".sh")]
    detected_scripts = [f.name for f in script_files]

    if not script_files:
        violations.append({
            "code": "MUS-EMPTY",
            "smell": "Empty Scripts Directory",
            "message": "Directory 'scripts/' contains no executable scripts (.py, .js, .sh)."
        })
        return violations, warnings, detected_scripts

    # AST check on all Python scripts
    for sf in script_files:
        if sf.suffix == ".py":
            try:
                code = sf.read_text(encoding="utf-8", errors="replace")
                tree = ast.parse(code, filename=sf.name)
            except SyntaxError as se:
                violations.append({
                    "code": "SCRIPT-SYNTAX",
                    "smell": "Script Syntax Error",
                    "message": f"Syntax error in '{sf.name}' at line {se.lineno}: {se.msg}"
                })
                continue

            # AST Visitor for dangerous calls
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    fname = ""
                    if isinstance(node.func, ast.Name):
                        fname = node.func.id
                    elif isinstance(node.func, ast.Attribute):
                        fname = node.func.attr
                    
                    if fname in ("eval", "exec"):
                        violations.append({
                            "code": "SCRIPT-DANGEROUS-EXEC",
                            "smell": "Remote Code Execution Risk",
                            "message": f"Forbidden dynamic execution via '{fname}()' in '{sf.name}' at line {node.lineno}."
                        })
                    # Check for dangerous os.system or direct system calls
                    is_os_call = False
                    if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
                        if node.func.value.id == "os" and node.func.attr in ("system", "popen", "spawnl", "spawnle", "spawnlp", "spawnlpe", "spawnv", "spawnve", "spawnvp", "spawnvpe"):
                            is_os_call = True
                    elif isinstance(node.func, ast.Name) and node.func.id in ("popen",):
                        is_os_call = True

                    if is_os_call:
                        violations.append({
                            "code": "SCRIPT-DANGEROUS-OS",
                            "smell": "Direct Shell Execution Risk",
                            "message": f"Forbidden direct shell execution via 'os.{fname}()' in '{sf.name}' at line {node.lineno}."
                        })
                    if fname in ("run", "Popen", "call") and any(k.arg == "shell" and getattr(k.value, "value", False) is True for k in node.keywords):
                        violations.append({
                            "code": "SCRIPT-SHELL-TRUE",
                            "smell": "Subprocess Shell=True Risk",
                            "message": f"Forbidden 'shell=True' in '{sf.name}' at line {node.lineno}. Use argument array instead."
                        })
                    for arg in node.args:
                        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                            if re.search(r"\b(curl|wget)\s+[^|;&\n]+\|\s*(sh|bash|zsh|python|perl)\b", arg.value, re.IGNORECASE):
                                violations.append({
                                    "code": "SCRIPT-SHELL-PIPE",
                                    "smell": "Remote Shell Pipe Risk",
                                    "message": f"Dangerous remote shell pipe ('curl | sh') in '{sf.name}' at line {node.lineno}."
                                })

            # Check for hardcoded secrets
            lines = code.splitlines()
            for lidx, line in enumerate(lines, start=1):
                if line.strip().startswith("#"):
                    continue
                for pat, sname in SECRET_PATTERNS:
                    if pat.search(line):
                        violations.append({
                            "code": "SCRIPT-SECRET-LEAK",
                            "smell": "Hardcoded API Secret",
                            "message": f"Detected {sname} in '{sf.name}' at line {lidx}. Secrets must be loaded via .env!"
                        })

    return violations, warnings, detected_scripts


def audit_placeholders(skill_dir: Path) -> list[dict]:
    """Fail on unreplaced template placeholders in the shipped skill body and references.

    Template files under assets/ and scripts/ templates are excluded on purpose:
    they are meant to contain placeholders. SKILL.md and references/ are not.
    """
    violations = []
    pattern = re.compile(r"\{[A-Z_]{3,}\}|\{SKILL_NAME\}|\{WHAT_IT_DOES\}")
    todo_pattern = re.compile(r"\bTODO\b|\bFIXME\b")
    targets = []
    skill_file = skill_dir / "SKILL.md"
    if skill_file.is_file():
        targets.append(skill_file)
    ref_dir = skill_dir / "references"
    if ref_dir.is_dir():
        targets.extend([f for f in ref_dir.iterdir() if f.is_file() and f.suffix == ".md"])
    agents_dir = skill_dir / "agents"
    if agents_dir.is_dir():
        targets.extend([f for f in agents_dir.iterdir() if f.is_file() and f.suffix == ".md"])
    examples_dir = skill_dir / "examples"
    if examples_dir.is_dir():
        for example_skill in examples_dir.rglob("SKILL.md"):
            targets.append(example_skill)
        for example_ref in examples_dir.rglob("references"):
            if example_ref.is_dir():
                targets.extend([f for f in example_ref.iterdir() if f.is_file() and f.suffix == ".md"])
    for target in targets:
        try:
            text = target.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        for lineno, line in enumerate(text.splitlines(), start=1):
            if pattern.search(line):
                violations.append({
                    "code": "PLACEHOLDER",
                    "smell": "Unreplaced Template Placeholder",
                    "message": f"Placeholder pattern in '{target.name}' line {lineno}. Replace every template placeholder before shipping.",
                })
            if todo_pattern.search(line):
                violations.append({
                    "code": "TODO-LEFT",
                    "smell": "Unfinished TODO Left in Shipped Skill",
                    "message": f"TODO/FIXME left in '{target.name}' line {lineno}. Finish it or remove it before shipping.",
                })
    return violations


def audit_agents(skill_dir: Path, content: str) -> tuple[list[dict], list[dict]]:
    """Check agent files: referenced agents must exist, unreferenced agents are fluff."""
    violations = []
    warnings = []
    agents_dir = skill_dir / "agents"
    if not agents_dir.is_dir():
        return violations, warnings
    referenced = set(re.findall(r"agents/([A-Za-z0-9_\-]+\.md)", content))
    on_disk = {f.name for f in agents_dir.iterdir() if f.is_file() and f.suffix == ".md"}
    for name in sorted(referenced - on_disk):
        violations.append({
            "code": "AGENT-MISSING",
            "smell": "Referenced Agent File Missing",
            "message": f"Agent file 'agents/{name}' is referenced in SKILL.md but does not exist.",
        })
    for name in sorted(on_disk - referenced):
        warnings.append({
            "code": "AGENT-UNREFERENCED",
            "smell": "Unreferenced Agent File",
            "message": f"Agent file 'agents/{name}' exists but is never referenced in SKILL.md. Remove it or link it.",
        })
    return violations, warnings

def audit_skill_directory(skill_path: str | Path) -> dict:
    p = Path(skill_path).resolve()
    skill_file = p / "SKILL.md"

    if not p.is_dir():
        return {"status": "FAIL", "error": f"Path '{skill_path}' is not a directory."}
    if not skill_file.is_file():
        return {"status": "FAIL", "error": f"Directory '{skill_path}' missing mandatory 'SKILL.md'."}

    try:
        content = skill_file.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return {"status": "FAIL", "error": f"Cannot read SKILL.md: {str(e)}"}

    meta, fm_viols, fm_warns = audit_frontmatter(content, p)
    body_viols, body_warns = audit_body(content, p)
    script_viols, script_warns, scripts = audit_scripts(p)
    placeholder_viols = audit_placeholders(p)
    agent_viols, agent_warns = audit_agents(p, content)

    all_violations = fm_viols + body_viols + script_viols + placeholder_viols + agent_viols
    all_warnings = fm_warns + body_warns + script_warns + agent_warns

    ref_dir = p / "references"
    references = [f.name for f in ref_dir.iterdir() if f.is_file()] if ref_dir.is_dir() else []

    # Strict authentic scoring:
    # Violations: -20 pts each
    # Warnings: -5 pts each
    penalty = (len(all_violations) * 20) + (len(all_warnings) * 5)
    score = max(0, 100 - penalty)
    
    if score >= 95 and len(all_violations) == 0:
        grade = "A+"
        status = "PASS"
    elif score >= 85 and len(all_violations) == 0:
        grade = "A"
        status = "PASS"
    elif score >= 70:
        grade = "B"
        status = "FAIL"
    elif score >= 50:
        grade = "C"
        status = "FAIL"
    else:
        grade = "F"
        status = "FAIL"

    return {
        "skill_name": meta.get("name", p.name),
        "path": str(p),
        "layout_conformance_score": score,
        "score": score,
        "grade": grade,
        "status": status,
        "violations_count": len(all_violations),
        "warnings_count": len(all_warnings),
        "violations": all_violations,
        "warnings": all_warnings,
        "stats": {
            "scripts": scripts,
            "references": references,
            "body_lines": len(content.splitlines()),
            "body_words": len(content.split())
        }
    }

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: python audit_skill.py <path_to_skill_directory>"}, indent=2))
        sys.exit(1)

    result = audit_skill_directory(sys.argv[1])
    print(json.dumps(result, indent=2))
    sys.exit(0 if result.get("status") == "PASS" else 1)

if __name__ == "__main__":
    main()
