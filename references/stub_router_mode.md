# Stub / Router Mode: For Version-Sensitive Skills

Use this mode when the generated skill wraps a moving target: a
CLI, an API, a tool whose flags change, or a guide that is updated
more often than the skill is reinstalled. This is the agent-browser
pattern, corrected: the installed SKILL.md is 50 lines, not 76,
and it is a pointer, not the guide.

## When to use it

Use stub mode only when a runtime router actually exists behind
the stub: a CLI command, a served guide, or a versioned reference
the agent can load at runtime. Do NOT use stub mode for a general
skill with no router behind it. An over-broad stub description
with no router causes false-positive triggering, which is exactly
what the trigger-negation guard prevents.

## The stub, 40-60 lines, no more

The installed SKILL.md must contain, and nothing else of substance:

1. One line naming the tool and its purpose.
2. One mandatory load command, in a Start Here section, for
   example: "Before running any command, load the real guide with
   `<tool> skills get core`." State explicitly: this file is a
   discovery stub, not the usage guide.
3. A routing list of specialised skills, as commands only, no
   prose per skill beyond a trailing comment.
4. A short why-section, at most 6 bullets, no workflow, no flags,
   no command list that belongs in the guide.

It must NOT contain: a version number, a flag list, a command
reference, an output format, or an error catalogue. Any of those
in the stub is a drift bug, because the stub can sit installed
for months while the tool changes.

## Why it prevents drift

The stub rarely changes, so it never goes stale. At runtime the
installed binary serves the guide bundled with that binary.
Upgrade the tool, and the guide upgrades automatically, with no
skill reinstall. Progressive disclosure lives in the router, not
the file: guide only by default, one reference on demand, full
guide only on explicit need.

## Router evals, mandatory for stub skills

Test the router, not just the output, with cases in this shape:

- id, prompt, category, expectedPatterns, forbiddenPatterns
- Categories: skill-loading, skill-selection, command-usage,
  reference-routing, context-footprint

Inject ONLY the stub as context. A case passes only if the model
outputs the right load or routing command, and does not output a
forbidden pattern, such as guessing a flag instead of loading the
reference, or loading everything with --full when one reference
would do. scripts/router_eval.py checks the deterministic part:
stub length, mandatory load command, no version numbers, and
pattern matching against stub plus guide text.

## Context footprint, stated numerically

Record, in bytes and approximate tokens: stub size, guide size,
and full size. The full size must not exceed 3x the guide size
without a written reason. State loading costs in the guide itself,
for example "snapshots cost about 200-400 tokens, full loading
costs several times more, load it only on need." A skill that
hides its cost is not apex-tier.
