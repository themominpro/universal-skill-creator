#!/usr/bin/env python3
"""Split trigger queries into train/test sets, deterministically.

Usage: python3 scripts/eval_description_split.py <queries.json> <output_dir> [--train-ratio 0.6]
Queries file format: a list of {"query": str, "should_trigger": bool},
or a dict with a "queries" list. Split is by stable hash of the query
text, so the same input always gives the same split, and train/test
never overlap. The agent must then run test_skill_trigger.py separately
on each split and choose the best description by TEST score, not train
score. See references/baseline_grading.md, description optimisation.

Exit 0 on PASS, 1 if test set is empty or lacks both classes.
"""
import argparse
import hashlib
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("queries")
    parser.add_argument("output_dir")
    parser.add_argument("--train-ratio", type=float, default=0.6)
    args = parser.parse_args()
    data = json.loads(Path(args.queries).read_text(encoding="utf-8"))
    queries = data["queries"] if isinstance(data, dict) else data
    if not isinstance(queries, list) or not queries:
        print(json.dumps({"status": "FAIL", "reason": "no queries found"}))
        return 1
    def key(q):
        text = q.get("query") or q.get("text") or str(q)
        return hashlib.sha256(text.encode("utf-8")).hexdigest()
    ordered = sorted(queries, key=key)
    n_train = int(len(ordered) * args.train_ratio)
    train, test = ordered[:n_train], ordered[n_train:]
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "train.json").write_text(json.dumps(train, indent=2), encoding="utf-8")
    (out / "test.json").write_text(json.dumps(test, indent=2), encoding="utf-8")
    overlap = {key(q) for q in train} & {key(q) for q in test}
    test_classes = {q.get("should_trigger") for q in test}
    violations = []
    if not test:
        violations.append("test set is empty")
    if overlap:
        violations.append("train/test overlap")
    if test_classes != {True, False}:
        violations.append("test set must contain both should-trigger and should-not-trigger queries")
    status = "FAIL" if violations else "PASS"
    print(json.dumps({"status": status, "train_count": len(train), "test_count": len(test), "train_file": str(out / "train.json"), "test_file": str(out / "test.json"), "violations": violations}, indent=2))
    return 1 if violations else 0


if __name__ == "__main__":
    raise SystemExit(main())
