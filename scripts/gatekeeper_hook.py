#!/usr/bin/env python3
"""Print only the gatekeeper router text. No writes, no network, no secrets.

Exit 0 when the router text is printed. If this prints nothing, the hook
is not wired and the Creator is documentation, not workflow.
See references/gatekeeper_bootstrap.md.
"""
import sys

ROUTER_TEXT = """If there is even a 1% chance a skill-creation workflow applies to what
you are doing, invoke universal-skill-creator before ANY response,
including clarifying questions.
Trigger on: create skill, build a skill, write skill, skill creator,
make a skill from notes, turn this into a skill, audit skill.
Priority: user instructions > skills > default model behaviour.
Dispatched subagents working on a specific task are exempt."""

def main():
    sys.stdout.write(ROUTER_TEXT + "\n")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
