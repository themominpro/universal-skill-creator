---
name: universal-skill-creator
description: >-
  Synthesizes, audits, benchmarks, and refines AI Agent Skills adhering to the agentskills.io
  open standard. Performs competitor teardowns, ingests domain literature and practitioner
  transcripts into mental models, auto-discovers MCP tools, enforces 6-tier compaction-resilient
  layout, writes companion deterministic validation scripts in scripts/, audits against the UC
  Irvine 26-Smell Taxonomy, and runs verified evals.
  Trigger on: "create skill", "build a skill", "write skill", "skill creator",
  "make a skill from notes", "turn this into a skill", "audit skill", "audit an existing skill", "audit existing skill", "build commercial skill".
  Do NOT use for one-off shell scripting or general codebase refactoring without skills.
license: Apache-2.0
compatibility: Requires Python 3.9+ and standard shell environment (Windows, macOS, Linux)
metadata:
  version: "1.0.0"
  last_reviewed: "2026-11-04"
  tested_harnesses: "Linux static audit, security, trigger, and eval runs on 2026-11-04; live harness testing is still required before claiming cross-harness parity"
  known_limitations: "Trigger test is a heuristic smoke test, not live LLM arbitration; task evals cover the shipped example skill only"
allowed-tools: Bash(python3:*) Bash(python:*) Read Write Edit Glob Grep
---

# Universal Skill Creator

## 1. Core Reframing & Non-Negotiable Invariants

- **Mental Model**: A world-class skill is an on-demand procedural operating system, NOT an unstructured prompt. It pairs proprietary practitioner IP with deterministic code gates (Three-Zone Hybrid Architecture) adhering strictly to `references/agentskills_spec.md`.
- **Environment Notice**: Python 3 and standard workspace discovery tools are pre-installed. Do NOT attempt to install package runners unless an explicit import fails.
- **Hard Invariant 1 (Zero-Smell Gate)**: Never deliver a skill that fails `python3 scripts/audit_skill.py <path>`. All structural layout smells must be audited and resolved.
- **Hard Invariant 2 (Script Smithing Mandate)**: Whenever a candidate skill performs validation, schema checks, or AST comparisons, you MUST author the companion executable utility in `scripts/validate.py` (0 context tokens for script code).
- **Hard Invariant 3 (Compaction Survival)**: Invariants, package notices, and the Task Routing Table MUST reside within the top 1,000 tokens of `SKILL.md` to prevent compaction shearing (`references/compaction_resilience.md`).
- **Hard Invariant 4 (Production Standard)**: Every skill must include domain-standard dialect, an Anti-Rationalization Table, and verifiable evaluation test cases.

---

## 2. Task Routing Decision Table

| User Intent / Input Type | Recommended Creation Workflow | Supporting On-Demand Reference |
|:-------------------------|:------------------------------|:-------------------------------|
| Commercial B2B Skill (for sale / client delivery) | Execute Full 6-Phase Pipeline (Phases 0–5) | `references/competitor_teardown_protocol.md` |
| Raw notes / SOP / Developer transcript | Execute Full 6-Phase Creation Pipeline | `references/domain_knowledge_ingestion.md` |
| Skill requiring external APIs or MCP servers | Run Phase 1 Tool Discovery + MCP Wiring | `references/mcp_tool_patterns.md` |
| Auditing or fixing an existing skill | Run Zero-Token 26-Smell Audit & Patch | `references/smell_taxonomy_26.md` |
| Multi-turn interactive wizard creation | Apply OMSC Ambiguity Triage Protocol | `references/question_triage_omsc.md` |

---

## 3. Phase 0: Deep Market Intelligence & Competitor Teardown

Before drafting instructions, execute competitive reconnaissance using [agents/niche_researcher.md](agents/niche_researcher.md):

- [ ] **Step 0.1 (Competitor Teardown)**: Search for existing public skills, prompts, or custom instructions in this niche.
  - Audit competitor offerings against the 26-Smell taxonomy (`references/competitor_teardown_protocol.md`).
  - Identify their structural flaws (e.g., generic AI slop, Option Buffet, missing validation scripts).
  - Define the antidote that fixes the competitors' structural flaws.
- [ ] **Step 0.2 (Domain Literature & Dialect Ingestion)**:
  - Ingest relevant books, whitepapers, podcast transcripts, and enterprise SOPs.
  - Follow `references/domain_knowledge_ingestion.md` to extract:
    1. Authoritative industry acronyms, metrics, and standard dialect (e.g. MEDDPICC, CAC payback, hook dwell-time).
    2. Candidate lexicon terms via `python3 scripts/build_domain_lexicon.py <sources> --output evals/lexicon.json`.
    3. Algorithmic thresholds and measurable formulas.
    4. High-density lists of non-obvious failure modes ("footguns").

---

## 4. Phase 1: Environment & Tool Discovery (Zone 1 Gate)

Copy and execute this discovery step before writing any documentation:

- [ ] **Step 1.1 (Probe Environment & Tools)**: Run the bundled discovery script:
  ```bash
  python3 scripts/discover_env.py
  ```
  *(On Windows PowerShell, use `python3 scripts/discover_env.py`)*
  - Inspect output for detected OS, available CLI binaries (`git`, `docker`, `python`, etc.), and active MCP servers.
  - If the candidate skill involves an external service (e.g. Figma, GitHub, Postgres), check if a matching MCP tool or CLI exists in the environment.

---

## 5. Phase 2: Silent Workspace Discovery & OMSC Triage

- [ ] **Step 2.1 (Silent Context Read)**: Inspect active repository configuration files (`package.json`, `pyproject.toml`, `Cargo.toml`, `.env.example`, git history).
  - *Hard Rule*: Never ask the user a question about language, framework, or tooling that can be discovered by reading files in the workspace.
- [ ] **Step 2.2 (The OMSC Ambiguity Filter)**:
  - Check whether Objective, Metric, Scope, or Constraints contain blocking unknowns (`references/decision_matrices_and_escalation.md`).
  - *If Low Blast Radius / Standard Workflow*: Proceed immediately using domain defaults. Ask 0 questions.
  - *If High Blast Radius / Mutually Exclusive UX Branch*: Pause and ask at most **1 to 3 compact questions**:
    1. Attach `(Recommended)` to the safest default choice.
    2. Provide 2–3 lettered options with one-line trade-offs.

---

## 6. Phase 3: Hybrid 3-Zone Synthesis

Author the complete skill folder structure: `<skill-name>/` containing `SKILL.md`, `scripts/`, `references/`, and `assets/`.

- [ ] **Step 3.1 (Author SKILL.md via 6-Tier Architecture)**:
  Adopt the [agents/architect.md](agents/architect.md) role to synthesize the core specification using `assets/master_template.md`:
  - **Byte 0**: Starts immediately with `---`. Zero angle brackets in frontmatter.
  - **Tier 1 (Tokens 1–500)**: Domain mental model & Non-Negotiable Invariants.
  - **Tier 2 (Tokens 500–1,000)**: Task Routing Decision Table (kills TOB/MDT smells).
  - **Tier 3 (Tokens 1,000–1,500)**: Silent Discovery & OMSC Ambiguity Triage.
  - **Tier 4 (Tokens 1,500–3,000)**: Numbered steps with copyable `- [ ]` checklists.
  - **Tier 5 (Tokens 3,000–4,200)**: High-density Domain Footguns & Anti-Rationalization Table.
  - **Tier 6 (Tokens 4,200–4,800)**: What This Skill Does NOT Do (kills NG smell).
  - *Total Body Limit*: Keep under 450 lines (<5,000 tokens).
- [ ] **Step 3.2 (Synthesize Companion Deterministic Scripts & Secret Templates)**:
  Adopt the [agents/script_smith.md](agents/script_smith.md) role:
  - For validation: author `scripts/validate.py` using `assets/script_templates/validator_template.py`.
  - For batch/destructive mutations: author `scripts/validate_plan.py`.
  - If `requires_secrets:` is declared in `SKILL.md`: author `.env.example` in the skill root with dashboard URLs and placeholder values.
  - Ensure scripts emit compact JSON to stdout and exit 0 on pass / 1 on fail.
- [ ] **Step 3.3 (Delegate Deep Docs to Flat References)**:
  If domain playbooks, schemas, or secondary guides exceed 50 lines, place them in `references/<topic>.md`.
  - *Invariant*: References must be flat (exactly 1 hop deep from `SKILL.md`).

---

## 7. Phase 4: Zero-Token Structural 26-Smell Audit & Evals

- [ ] **Step 4.1 (Run Automated Static Linter)**:
  Execute the structural linter against the newly generated skill directory:
  ```bash
  python3 scripts/audit_skill.py path/to/generated-skill
  ```
- [ ] **Step 4.2 (Run Deterministic Security Scan)**:
  Execute the AST security scanner to verify zero remote code execution, shell injection, or credential leaks:
  ```bash
  python3 scripts/security_scan.py path/to/generated-skill
  ```
- [ ] **Step 4.3 (Patch All Violations & Smells)**:
  If the audit reports any violations, adopt the [agents/smell_auditor.md](agents/smell_auditor.md) role:
  - **Rationalization Loophole (RL)**: Add an explicit Anti-Rationalization Table refuting model excuses.
  - **Option Buffet (TOB)**: Replace tool lists with a single default tool per scenario.
  - **Lengthy Body (LSB)**: Move long code snippets to `references/` or `assets/`.
  - Re-run `audit_skill.py` until the status is **PASS** with a Grade of **A** or **A+**.
- [ ] **Step 4.4 (Run Empirical Benchmark Evals)**:
  Execute test cases to establish verifiable task pass rates:
  ```bash
  python3 scripts/run_evals.py path/to/generated-skill
  ```
  - For revisions, adopt the [agents/comparator.md](agents/comparator.md) role to perform double-blind comparison against the baseline.

---

## 8. Phase 5: Trigger Verification & Packaging

- [ ] **Step 5.1 (Test Trigger Precision & Recall)**:
  Test the YAML description with representative positive and negative prompts:
  ```bash
  python3 scripts/test_skill_trigger.py path/to/generated-skill
  ```

---

## 9. Anti-Rationalization Guardrails, Footguns & Excuses to Reject

Refutes common LLM rationalizations, cutting corners, and known failure patterns (`references/playbook_anti_patterns_38.md`):

| Common Model Excuse | Why It Is Strictly Forbidden & Required Action |
|:--------------------|:-----------------------------------------------|
| "The skill is simple, so writing a companion script in `scripts/` is overkill." | Missing Utility Script (MUS) is the #1 cause of agent failure. Always write the verification script. |
| "I can skip competitor research because I already know this domain." | Competitor teardown reveals user complaints, blind spots, and pricing opportunities. Never skip Phase 0. |
| "I can skip the 26-smell audit because the Markdown looks clean." | Visual inspection misses structural defects like compaction shearing and folder parity errors. Always run `audit_skill.py`. |
| "I'll ask the user 5 questions before starting to collect full context." | Asking lazy questions frustrates engineers. Silently read workspace files first; cap questions at 1–3. |
| "I will generate the skill entirely from my pretraining knowledge without reading docs." | SkillsBench proves self-generation degrades performance (-1.3 pp). Ground instructions in real failure modes and source docs. |

---

## 10. Final Changes and Limits

- No dossier, no WORKFLOW file, no dead templates, no duplicate packager, and no author fields. What remains is SKILL.md, agent roles, references, scripts, templates that are actually linked, and one built example.
- Trigger, audit, security, bundle, and MCP detection gaps found in the final review are closed in this package. See CHANGELOG.md for the exact list.
- Known limit, unchanged: trigger evaluation is a heuristic smoke test, not live LLM arbitration. Do not claim live model precision from it.

## 11. What This Skill Does NOT Do

- Does NOT generate bloated 2,000-line documentation dumps into a single `SKILL.md`.
- Does NOT execute destructive migrations or deployments directly without a Plan-Validate-Execute safety gate.
- Does NOT hallucinate uninstalled MCP tools or fictitious CLI commands.
- Does NOT deliver raw prompts without companion validation code and client proof dossiers.
