# ⚡ Universal Skill Creator (v1.0)

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Standard: agentskills.io](https://img.shields.io/badge/Standard-agentskills.io-green.svg)](https://agentskills.io)
[![Layout Conformance: 100/100 A+](https://img.shields.io/badge/Audit-100%2F100%20Grade%20A%2B-success.svg)](#)
[![Security: Zero Critical Leaks](https://img.shields.io/badge/Security-Zero%20Critical%20Leaks-brightgreen.svg)](#)
[![Python: 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://python.org)
[![Evals: 20/20 Task Pass](https://img.shields.io/badge/Evals-20%2F20%20Passed-success.svg)](#)

> v1.0, apex-tier behaviour gates: gatekeeper bootstrap, pressure scenarios, with-skill vs baseline grading with a numeric ship gate, description train/test split, stub/router mode with router evals, and render QA. Adheres to open `agentskills.io` standard.

> Turns practitioner notes, books, transcripts, and competitor teardowns into AI Agent Skills adhering to the open `agentskills.io` standard. No pitch dossier, no marketing files, only the files an agent actually loads or runs.

---

## ⚡ How to Trigger This Skill

In your AI chat (Google Antigravity, Claude Code, Cursor, Windsurf, Codex), simply prompt:

```markdown
Create an AI skill for [Niche/Workflow].
Here are my practitioner notes / books / transcripts / competitor prompts:
[Paste raw text, attach PDF/DOCX, or specify folder path]
```

---

## 🏗️ What Makes Skills Built with This Engine "World-Class" (verified gate, not a slogan)

Unlike generic prompts or basic markdown files, skills built with this engine enforce:

1. **The 6-Tier Compaction-Resilient Layout (<450 lines)**:
   - Survives long conversations and auto-compaction without "attention rot" or forgetting rules.
2. **Deterministic Python Validation (`scripts/validate.py`)**:
   - Programmatic verification gates: Companion Python scripts execute syntax verification, schema validation, and domain assertions, exiting with clear non-zero codes if requirements fail.
3. **The Anti-Rationalization Table**:
   - Explicitly refutes the psychological excuses LLMs use to skip verification or cut corners.
4. **Domain Jargon & Anti-Patterns**:
   - Ingests real practitioner mental models, SOPs, and footguns so the AI sounds like a senior operator, not generic AI slop.
5. **Layout Conformance & Anti-Smell Audit**:
   - Pre-audited with `audit_skill.py` for structural layout conformance and common failure modes (RL, TOB, MUS, LSB, etc.).

---

## 🛠️ The 5-Phase Automated Execution Pipeline

When invoked, the engine automatically runs 5 distinct phases:

1. **Phase 0: Competitor Teardown & Domain Ingestion**
   - Audits existing public prompts/skills in that niche to identify their weaknesses.
   - Extracts high-value practitioner acronyms, metrics, formulas, and footguns.
2. **Phase 1 & 2: Environment Discovery & OMSC Triage**
   - Silently checks installed binaries (`python`, `node`, `docker`, `git`) and active MCP servers.
   - Resolves blocking unknowns with 0 to 3 targeted multiple-choice questions.
3. **Phase 3: Hybrid 3-Zone Synthesis**
   - Authors `SKILL.md` (<450 lines).
   - Generates companion Python scripts in `scripts/validate.py` (0 context tokens).
   - Generates `.env.example` if API keys are required.
   - Decouples deep playbooks into flat `references/` (1 hop deep).
4. **Phase 4: Structural Layout Conformance Audit**
   - Runs `scripts/audit_skill.py` on the output until it achieves Grade A layout conformance.
5. **Phase 5: Trigger Verification & Packaging**
   - Runs `scripts/test_skill_trigger.py` to evaluate advisory trigger precision and recall against `evals/trigger_queries.json`.
   - Ready for packaging via `python3 scripts/bundle_package.py path/to/skill dist/ --format both`.

> **Note on Evals**: `scripts/run_evals.py` is a deterministic script test harness that self-tests companion scripts and validates command assertions; live model arbitration on arbitrary tasks requires external multi-turn LLM runners.

## QA Checkpoints and Input Formats (new in this v1.0 package)

- **QA at every stage**: checkpoints after teardown, architecture, draft, gates, and ship, max 2 questions each, recorded with `scripts/record_qa.py`. High blast radius waits for your reply, low blast radius proceeds on the recommended default but still records it.
- **Inputs**: .txt, .md, notes, SOPs, transcripts, plus .docx, .pdf, .ppt, and similar formats read natively by Claude Code / Claude, no hard extraction rule. `scripts/extract_text.py` is an optional fallback only, for scripts that need plain text. Scanned image-only PDFs warn and return no text, they are not invented.
- **Dossier wording removed**: the competitor protocol no longer tells the agent to create a pitch dossier, and the niche researcher now returns a Market Intelligence Report.

## Apex-Tier Behaviour Gates (new in this v1.0 package)

1. **Gatekeeper**: `scripts/gatekeeper_hook.py` prints only the 1% router rule. A skill that never triggers is documentation, not workflow.
2. **Pressure**: `scripts/generate_pressure_scenarios.py` makes 4 combined scenarios (time, sunk cost, authority, exhaustion). Run baseline and with-skill, record verbatim excuses, build a Thought | Reality table.
3. **Baseline grading**: `agents/grader.md` + `scripts/grade_baseline.py`. Ship only if with-skill >= 80%, delta > 0, no regression.
4. **Description split**: `scripts/eval_description_split.py` splits trigger queries 60/40. Choose the best description by test score, not train score.
5. **Stub/router**: 40-60 line stub only, no version numbers, `scripts/router_eval.py` injects only the stub. Shipped stub example is exactly 50 lines.
6. **Render QA**: `scripts/render_qa.py` runs content and file gates. Visual QA is always human, never claimed by a script.

Also fixed: SKILL.md section 12 no longer mentions client proof dossiers, which were removed from this package.

---

## 📁 Architecture Overview

```
universal-skill-creator/
├── agents/             # 6 Specialist Subagents (Researcher, Architect, Script Smith, Auditor, Comparator, Grader)
├── assets/             # Scaffolds (master_template.md, validator_template.py)
├── references/         # 15 Flat Reference Files (including gatekeeper, pressure, baseline grading, stub/router, render QA)
├── scripts/            # 14 Deterministic Python Utilities (linter, trigger engine, eval runner, scanner, packager, pressure, grader, router eval, render QA, gatekeeper)
├── examples/           # 2 Shipped Examples: 1 Built Skill with its own validate.py, 1 Stub Skill (50 lines, router-gated)
├── SKILL.md            # The Execution OS (see CHANGELOG.md for line count and test results)
├── README.md           # This file, the only human entry point
├── CHANGELOG.md        # Version history
```
