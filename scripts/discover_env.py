#!/usr/bin/env python3
"""
Environment and Tool Discovery Utility
Scans the local host environment for OS details, shell environment, installed
CLI binaries, package managers, and configured MCP servers.
Fix 4 Patch: Reports exact resolved python_command to prevent Windows Store redirects.
Outputs compact JSON to stdout (0 context token load).
"""

import os
import sys
import json
import shutil
import platform
from pathlib import Path

COMMON_BINARIES = [
    "git", "python", "python3", "node", "npm", "npx", "yarn", "pnpm", "bun",
    "docker", "docker-compose", "kubectl", "helm", "terraform",
    "gh", "aws", "gcloud", "az", "cargo", "rustc", "go", "make",
    "pytest", "ruff", "black", "mypy", "eslint", "prettier", "tsc", "jq", "curl"
]

def detect_os():
    is_win = platform.system() == "Windows"
    return {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "is_windows": is_win,
        "is_macos": platform.system() == "Darwin",
        "is_linux": platform.system() == "Linux",
        "python_version": sys.version.split()[0],
        "python_executable": sys.executable,
        "preferred_python_cmd": "python" if is_win else "python3"
    }

def detect_binaries():
    found = {}
    missing = []
    for binary in COMMON_BINARIES:
        path = shutil.which(binary)
        if path:
            found[binary] = path
        else:
            missing.append(binary)
    return {"installed": found, "missing": missing}

def detect_mcp_servers():
    """Inspects common MCP configuration locations across platforms."""
    mcp_data = {"servers": [], "source_files": []}
    home = Path.home()
    
    candidate_paths = [
        home / ".gemini" / "antigravity" / "mcp",
        home / ".gemini" / "config" / "mcp_config.json",
        home / "AppData" / "Roaming" / "Claude" / "claude_desktop_config.json",
        home / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json",
        home / ".config" / "claude" / "claude_desktop_config.json",
        # VS Code and Cursor, including the current project folder
        home / ".vscode" / "mcp.json",
        home / ".config" / "Code" / "User" / "mcp.json",
        home / "Library" / "Application Support" / "Code" / "User" / "mcp.json",
        home / ".cursor" / "mcp.json",
        Path.cwd() / ".vscode" / "mcp.json",
        Path.cwd() / ".cursor" / "mcp.json",
    ]
    
    for path in candidate_paths:
        if path.is_file():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    servers = config.get("mcpServers", {}) or config.get("servers", {})
                    for name, details in servers.items():
                        cmd = details.get("command", "")
                        args = details.get("args", [])
                        mcp_data["servers"].append({
                            "name": name,
                            "command": cmd,
                            "args": args[:3],
                            "source": str(path)
                        })
                    mcp_data["source_files"].append(str(path))
            except Exception:
                pass
        elif path.is_dir():
            mcp_data["source_files"].append(str(path))
            for item in path.iterdir():
                if item.is_dir():
                    mcp_data["servers"].append({
                        "name": item.name,
                        "source": str(item)
                    })

    return mcp_data

def main():
    result = {
        "os": detect_os(),
        "binaries": detect_binaries(),
        "mcp": detect_mcp_servers(),
        "cwd": os.getcwd(),
    }
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
