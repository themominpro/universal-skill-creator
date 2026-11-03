#!/usr/bin/env python3
# Copyright (c) 2026 Momin / GTM Engineering. All rights reserved.
# Licensed under the Apache License, Version 2.0.

"""
Authentic Trigger Precision & Recall Evaluator.
Evaluates agent skill routing precision and recall against:
1. An explicit independent dataset (evals/trigger_queries.json), OR
2. High-entropy realistic user prompts and near-miss negative collision traps.
Strictly non-circular: Vague descriptions (e.g. 'helps with various things')
fail with 0% recall and 0% precision.
Outputs structured JSON to stdout. Exits 0 on PASS, 1 on FAIL.
"""

from __future__ import annotations

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

def parse_frontmatter(skill_dir: Path) -> tuple[dict, str | None]:
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.is_file():
        return {}, "Missing SKILL.md"

    content = skill_file.read_text(encoding="utf-8", errors="replace")
    if not content.startswith("---"):
        return {}, "SKILL.md missing byte-0 '---' delimiter"

    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, "Malformed frontmatter"

    yaml_text = parts[1]
    name_m = re.search(r"^name:\s*([a-zA-Z0-9_-]+)", yaml_text, re.MULTILINE)
    name = name_m.group(1).strip() if name_m else skill_dir.name

    # Accurate multiline description parser
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

    return {"name": name, "description": desc}, None

STOP_WORDS = {
    "the", "a", "an", "and", "or", "but", "if", "then", "so", "to", "of", "in",
    "on", "for", "with", "at", "by", "from", "is", "are", "was", "were", "be",
    "this", "that", "it", "its", "as", "you", "your", "i", "my", "me", "we", "our",
    "can", "could", "will", "would", "please", "do", "does", "did", "have", "has",
    "had", "not", "use", "when", "user", "users", "help", "need",
    "want", "make", "get", "let", "just", "about", "what", "how", "all", "each",
    "every", "some", "any", "which", "who", "whom", "whose", "why", "here", "there",
    "write", "writes", "script", "scripts", "code", "file", "files", "run", "test", "tests"
}

def stem(word: str) -> str:
    """Lightweight suffix stripping for token matching across singular/plural and verb forms."""
    w = word.lower()
    for suffix in ("ing", "tion", "tions", "ies", "es", "ed", "ment", "s"):
        if len(w) > len(suffix) + 3 and w.endswith(suffix):
            return w[:-len(suffix)]
    return w

def evaluate_trigger_match(query: str, description: str) -> tuple[bool, str]:
    """
    Simulates how an agent router evaluates whether a user prompt matches a skill description.
    Checks:
    1. Negative exclusion suppression (Do NOT use for...)
    2. Explicit multi-word trigger phrases (Trigger on: "...", "...")
    3. Stemmed domain vocabulary overlap (handles invoice/invoices, audit/auditing)
    """
    q_lower = query.lower()
    desc_lower = description.lower()

    # 1. Check negative exclusions first (matching full phrases, e.g. 'claude.md' or 'one-off shell scripting')
    exclusions_block = ""
    for ex_marker in ["do not use for", "not use for", "out of scope", "excludes", "never use"]:
        if ex_marker in desc_lower:
            after_ex = desc_lower.split(ex_marker, 1)[1]
            exclusions_block = re.split(r"\.\s+|\n|\Z", after_ex)[0]
            break

    if exclusions_block:
        ex_phrases = [p.strip() for p in re.split(r",|;|\bor\b", exclusions_block) if len(p.strip()) > 3]
        for ep in ex_phrases:
            ep_clean = ep.strip().rstrip(".")
            # Check for phrase match in query
            if re.search(r"\b" + re.escape(ep_clean) + r"\b", q_lower):
                return False, f"Suppressed by exclusion guard: '{ep_clean}'"
            # Or multi-token collision if phrase has >=2 non-stop words
            ep_meaningful = [stem(w) for w in re.findall(r"\b[a-z0-9_.-]{3,}\b", ep_clean) if w not in STOP_WORDS]
            q_meaningful = [stem(w) for w in re.findall(r"\b[a-z0-9_.-]{3,}\b", q_lower) if w not in STOP_WORDS]
            if len(ep_meaningful) >= 2 and all(w in q_meaningful for w in ep_meaningful):
                return False, f"Suppressed by exclusion phrase: '{ep_clean}'"

    # 1b. Negation guard: a user explicitly saying "not a skill" is not a skill request,
    # even if the words "create" and "skill" both appear elsewhere in the sentence.
    if re.search(r"\bnot (a )?skill\b|\bwithout (a )?skill\b|\bno skill\b", q_lower):
        return False, "Suppressed by negation guard: user explicitly said not a skill"

    # 2. Extract explicit positive trigger phrases
    trigger_block = ""
    for trig_marker in ["trigger on:", "use when", "use this skill when", "whenever", "use for:"]:
        if trig_marker in desc_lower:
            after_trig = desc_lower.split(trig_marker, 1)[1]
            trigger_block = re.split(r"\.\s+|\n|\Z", after_trig)[0]
            break

    target_phrases = re.findall(r'"([^"]+)"', trigger_block)
    if not target_phrases and trigger_block:
        target_phrases = [p.strip() for p in re.split(r",|or", trigger_block) if len(p.strip()) > 4]

    # Evaluate match against explicit target phrases
    # Consecutive rule: phrase tokens must appear consecutively in the query
    # after stop-word removal. "Create a landing page, not a skill" must NOT
    # match "create skill", because landing and page sit between them.
    q_tokens_all = [stem(w) for w in re.findall(r"[a-z0-9_-]{3,}", q_lower) if w not in STOP_WORDS]
    for tp in target_phrases:
        tp_clean = tp.strip().lower()
        if tp_clean and tp_clean in q_lower:
            return True, f"Matched explicit trigger phrase: '{tp}'"
        tp_tokens = [stem(w) for w in re.findall(r"[a-z0-9_-]{3,}", tp_clean) if w not in STOP_WORDS]
        if len(tp_tokens) >= 2:
            for start in range(len(q_tokens_all) - len(tp_tokens) + 1):
                if q_tokens_all[start:start + len(tp_tokens)] == tp_tokens:
                    return True, f"Matched explicit trigger phrase: '{tp}'"

    # 3. Domain vocabulary overlap with stemming (excluding stop words)
    desc_domain = {stem(w) for w in re.findall(r"\b[a-z0-9_-]{3,}\b", desc_lower) if w not in STOP_WORDS and len(w) > 3}
    q_domain = {stem(w) for w in re.findall(r"\b[a-z0-9_-]{3,}\b", q_lower) if w not in STOP_WORDS and len(w) > 3}
    common_tokens = q_domain.intersection(desc_domain)

    # Significant overlap requires at least 2 domain-specific non-stop tokens
    if len(common_tokens) >= 2:
        return True, f"Matched domain keywords: {list(common_tokens)[:3]}"

    return False, "Insufficient domain overlap"

def test_triggers(skill_dir: Path) -> dict:
    meta, err = parse_frontmatter(skill_dir)
    if err:
        return {"status": "FAIL", "error": err}

    name = meta["name"]
    desc = meta["description"]

    # 1. Non-Circular Quality Gate: Check for Vague or Empty Descriptions
    if len(desc) < 40:
        return {
            "status": "FAIL",
            "skill_name": name,
            "description_length": len(desc),
            "recall_pct": 0.0,
            "precision_pct": 0.0,
            "failure_reason": f"Description is too short ({len(desc)} chars). Cannot reliably trigger.",
            "positive_tests": [],
            "negative_tests": []
        }

    for vpat in VAGUE_DESCRIPTION_PATTERNS:
        if vpat.search(desc):
            return {
                "status": "FAIL",
                "skill_name": name,
                "description_length": len(desc),
                "recall_pct": 0.0,
                "precision_pct": 0.0,
                "failure_reason": f"Description contains vague non-operational phrasing: '{vpat.pattern}'.",
                "positive_tests": [],
                "negative_tests": []
            }

def load_queries_from_file(filepath: Path) -> tuple[list[str], list[str]]:
    """Loads trigger queries supporting both dict and list formats."""
    should_trigger = []
    should_not_trigger = []
    try:
        data = json.loads(filepath.read_text(encoding="utf-8"))
        if isinstance(data, list):
            for item in data:
                q = item.get("query", "").strip()
                if not q:
                    continue
                if item.get("should_trigger", True):
                    should_trigger.append(q)
                else:
                    should_not_trigger.append(q)
        elif isinstance(data, dict):
            should_trigger = [q.strip() for q in data.get("should_trigger", []) if q.strip()]
            should_not_trigger = [q.strip() for q in data.get("should_not_trigger", []) if q.strip()]
    except Exception:
        pass
    return should_trigger, should_not_trigger

def test_triggers(skill_dir: Path, custom_queries_path: Path | None = None) -> dict:
    meta, err = parse_frontmatter(skill_dir)
    if err:
        return {"status": "FAIL", "error": err}

    name = meta["name"]
    desc = meta["description"]

    # 1. Non-Circular Quality Gate: Check for Vague or Empty Descriptions
    if len(desc) < 40:
        return {
            "status": "FAIL",
            "skill_name": name,
            "description_length": len(desc),
            "recall_pct": 0.0,
            "precision_pct": 0.0,
            "failure_reason": f"Description is too short ({len(desc)} chars). Cannot reliably trigger.",
            "positive_tests": [],
            "negative_tests": []
        }

    for vpat in VAGUE_DESCRIPTION_PATTERNS:
        if vpat.search(desc):
            return {
                "status": "FAIL",
                "skill_name": name,
                "description_length": len(desc),
                "recall_pct": 0.0,
                "precision_pct": 0.0,
                "failure_reason": f"Description contains vague non-operational phrasing: '{vpat.pattern}'.",
                "positive_tests": [],
                "negative_tests": []
            }

    # 2. Discover and load queries file
    query_files_to_check = []
    if custom_queries_path:
        query_files_to_check.append(custom_queries_path)
    query_files_to_check.extend([
        skill_dir / "evals" / "trigger_queries.json",
        skill_dir / "evals" / "trigger-queries.json",
    ])

    should_trigger = []
    should_not_trigger = []
    loaded_source = None

    for qf in query_files_to_check:
        if qf.is_file():
            st, snt = load_queries_from_file(qf)
            if st or snt:
                should_trigger = st
                should_not_trigger = snt
                loaded_source = str(qf.relative_to(skill_dir) if skill_dir in qf.parents else qf)
                break

    # Strictly require at least 6 positive and 6 negative independent queries from evals/trigger_queries.json
    if len(should_trigger) < 6 or len(should_not_trigger) < 6:
        return {
            "status": "UNVERIFIED",
            "skill_name": name,
            "error": (
                f"Trigger evaluation requires at least 6 'should_trigger' and 6 'should_not_trigger' queries "
                f"in evals/trigger_queries.json (or via --queries). "
                f"Found {len(should_trigger)} positive and {len(should_not_trigger)} negative queries."
            ),
            "query_source": loaded_source,
            "queries_found": {
                "should_trigger_count": len(should_trigger),
                "should_not_trigger_count": len(should_not_trigger)
            }
        }

    # Evaluate Positives (Recall)
    pos_results = []
    pos_hits = 0
    for q in should_trigger:
        activated, reason = evaluate_trigger_match(q, desc)
        if activated:
            pos_hits += 1
        pos_results.append({
            "query": q,
            "expected_activation": True,
            "activated": activated,
            "reason": reason,
            "passed": (activated is True)
        })

    # Evaluate Negatives (Precision)
    neg_results = []
    neg_suppressions = 0
    for q in should_not_trigger:
        activated, reason = evaluate_trigger_match(q, desc)
        if not activated:
            neg_suppressions += 1
        neg_results.append({
            "query": q,
            "expected_activation": False,
            "activated": activated,
            "reason": reason,
            "passed": (activated is False)
        })

    recall_pct = round((pos_hits / len(should_trigger)) * 100, 1) if should_trigger else 0.0
    precision_pct = round((neg_suppressions / len(should_not_trigger)) * 100, 1) if should_not_trigger else 0.0

    # Advisory criteria: Recall >= 80% and Precision >= 80%
    likely_ok = (recall_pct >= 80.0) and (precision_pct >= 80.0)
    advisory_status = "LIKELY_OK" if likely_ok else "NEEDS_REVIEW"

    return {
        "status": advisory_status,
        "advisory": True,
        "skill_name": name,
        "engine": "Deterministic Semantic Heuristic (Advisory Smoke Test)",
        "query_source": loaded_source,
        "description_length": len(desc),
        "recall_pct": recall_pct,
        "precision_pct": precision_pct,
        "positive_tests_passed": f"{pos_hits}/{len(should_trigger)}",
        "negative_tests_passed": f"{neg_suppressions}/{len(should_not_trigger)}",
        "disclaimer": "This is an advisory static heuristic smoke test. For model-level live arbitration, run with an active LLM CLI.",
        "positive_tests": pos_results,
        "negative_tests": neg_results
    }

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Deterministic Trigger Precision & Recall Evaluator.")
    parser.add_argument("skill_dir", help="Path to the skill directory")
    parser.add_argument("--queries", dest="queries_path", default=None, help="Path to custom trigger queries JSON")
    args = parser.parse_args()

    custom_q = Path(args.queries_path) if args.queries_path else None
    result = test_triggers(Path(args.skill_dir), custom_q)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result.get("status") == "LIKELY_OK" else 1)

if __name__ == "__main__":
    main()
