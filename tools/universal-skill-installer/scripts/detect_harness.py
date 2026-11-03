#!/usr/bin/env python3
# Copyright (c) 2026 Momin / GTM Engineering. All rights reserved.
# Licensed under the Apache License, Version 2.0.

"""
Multi-Harness Environment Detector for AI Agent Skills.
Detects active AI coding environments (Antigravity, Claude Code, Cursor, Codex)
and resolves the correct global or workspace skill installation path.
Outputs structured JSON to stdout.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

def detect_harnesses(workspace_path: str | Path | None = None) -> dict:
    home = Path.home()
    workspace = Path(workspace_path).resolve() if workspace_path else Path.cwd().resolve()
    
    harnesses = []

    # 1. Google Antigravity / Gemini CLI
    gemini_global = home / ".gemini" / "config" / "skills"
    gemini_active = (home / ".gemini").is_dir() or (workspace / ".gemini").is_dir()
    if gemini_active or gemini_global.exists():
        harnesses.append({
            "name": "Google Antigravity",
            "id": "antigravity",
            "global_path": str(gemini_global),
            "workspace_path": str(workspace / ".gemini" / "skills"),
            "detected": True
        })

    # 2. Claude Code CLI
    claude_global = home / ".claude" / "skills"
    claude_workspace = workspace / ".claude" / "skills"
    claude_detected = (home / ".claude").is_dir() or claude_workspace.is_dir()
    if claude_detected:
        harnesses.append({
            "name": "Claude Code",
            "id": "claude",
            "global_path": str(claude_global),
            "workspace_path": str(claude_workspace),
            "detected": True
        })

    # 3. Cursor IDE
    cursor_workspace = workspace / ".cursor" / "skills"
    cursor_detected = (workspace / ".cursor").is_dir()
    if cursor_detected:
        harnesses.append({
            "name": "Cursor IDE",
            "id": "cursor",
            "global_path": None,
            "workspace_path": str(cursor_workspace),
            "detected": True
        })

    # 4. OpenAI Codex CLI
    codex_global = home / ".codex" / "skills"
    if (home / ".codex").is_dir():
        harnesses.append({
            "name": "OpenAI Codex",
            "id": "codex",
            "global_path": str(codex_global),
            "workspace_path": str(workspace / ".codex" / "skills"),
            "detected": True
        })

    # Fallback generic project workspace. This is a fallback, not a detection:
    # it is listed so the user always has a target, but detected is False.
    generic_workspace = workspace / "skills"
    harnesses.append({
        "name": "Generic Project Workspace",
        "id": "generic",
        "global_path": str(home / ".agents" / "skills"),
        "workspace_path": str(generic_workspace),
        "detected": False
    })

    # Recommend default
    preferred = harnesses[0] if harnesses else None
    recommended_path = preferred["global_path"] if preferred and preferred.get("global_path") else str(generic_workspace)

    return {
        "status": "SUCCESS",
        "workspace": str(workspace),
        "detected_count": sum(1 for h in harnesses if h["detected"]),
        "recommended_harness": preferred["id"] if preferred else "generic",
        "recommended_install_path": recommended_path,
        "available_harnesses": harnesses
    }

def main():
    target_workspace = sys.argv[1] if len(sys.argv) > 1 else None
    result = detect_harnesses(target_workspace)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
