#!/usr/bin/env python3
# Copyright (c) 2026 Momin / GTM Engineering. All rights reserved.
# Licensed under the Apache License, Version 2.0.

"""Extract candidate domain terms from supplied text files.

This produces candidates only; it does not assert that a term is correct.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

WORD = re.compile(r"[A-Za-z][A-Za-z0-9_-]{2,}")
STOP = {
    "the", "and", "for", "that", "this", "with", "from", "are", "you",
    "your", "into", "have", "will", "not", "use", "can", "our", "they",
    "them", "their", "these", "those", "what", "when", "where", "which",
    "how", "but", "all", "was", "were", "one", "more", "some", "than",
    "then", "there", "here", "also", "just", "does", "did", "has", "had",
    "its", "it", "out", "about", "who", "why", "too", "very", "only"
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract candidate domain terms")
    parser.add_argument("sources", nargs="+", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    counts = Counter()
    source_map = {}
    for source in args.sources:
        text = source.read_text(encoding="utf-8", errors="replace")
        for token in WORD.findall(text.lower()):
            if token not in STOP:
                counts[token] += 1
                source_map.setdefault(token, set()).add(str(source))
    terms = [
        {"term": term, "count": count, "sources": sorted(source_map[term]), "status": "candidate"}
        for term, count in counts.most_common(100)
    ]
    result = {
        "schema_version": "1.0",
        "source_count": len(args.sources),
        "terms": terms,
        "warning": "Candidates require human/domain validation before use as rules."
    }
    rendered = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
