---
name: {SKILL_NAME}
description: >-
  {WHAT_IT_DOES}. Use this skill whenever the user asks to {ACTION_VERBS}
  involving {KEYWORDS_AND_EXTENSIONS}. Do NOT use for {OUT_OF_SCOPE_TASKS}.
compatibility: Requires Python 3.9+ and standard workspace tools
metadata:
  version: "1.0.0"
allowed-tools: Bash(python3:*) Bash(python:*) Read Write Edit Glob Grep
# --- External API Keys & Secrets (Include only if skill uses third-party APIs) ---
# requires_secrets:
#   - key: {SERVICE_API_KEY}
#     service: "{SERVICE_NAME}"
#     url: "{SIGNUP_OR_KEY_URL}"
#     description: "{WHAT_THIS_KEY_POWERS}"
#     hint: "{FORMAT_HINT_E_G_STARTS_WITH_AIZA}"
#     required: true
#     instructions: |
#       1. Navigate to {SIGNUP_OR_KEY_URL}
#       2. Create an account or sign in
#       3. Generate an API Key
#       4. Add KEY_NAME=your_key to your project's .env file
---

# {HUMAN_READABLE_TITLE}

## 1. Core Reframing & Non-Negotiable Invariants

- **Mental Model**: {ONE_SENTENCE_MENTAL_MODEL_REFRAMING}.
- **Environment & Secrets**: API keys are loaded strictly from the project's `.env` file via `load_env()`. NEVER hardcode credentials in prompts or script files.
- **Hard Invariant 1**: Never deliver output while `python3 scripts/validate.py <target>` reports errors (customize `scripts/validate.py` with domain-specific AST, schema, or structural checks).
- **Hard Invariant 2**: Existing repository conventions strictly override generic defaults in this skill.
- **Hard Invariant 3**: Preserve existing formatting and non-target blocks when modifying user files.

---

## 2. Task Routing Decision Table

| Scenario / Intent | Recommended Approach & Tool | On-Demand Reference |
|:------------------|:----------------------------|:--------------------|
| Create new {ARTIFACT} from scratch | Use {DEFAULT_TOOL_A} via Phase 2 | `references/{PRIMARY_GUIDE}.md` |
| Modify or patch existing {ARTIFACT} | Inspect structure first; apply minimal diff | `references/{EDITING_GUIDE}.md` |
| Batch or high-risk mutation | Enforce Plan, Validate, Execute workflow | `references/{SPECIALIZED_GUIDE}.md` |

---

## 3. Phase 1: Silent Discovery & Ambiguity Triage (Zone 1 Gate)

- [ ] **Step 1.1 (Silent Discovery)**: Inspect workspace configuration files, `.env.example`, and existing patterns. Never ask a question that repository files can answer.
- [ ] **Step 1.2 (OMSC Ambiguity Evaluation)**: Check whether Objective, Metric, Scope, or Constraints contain a blocking unknown.
  - *Low Blast Radius / Reversible*: Proceed immediately using recommended defaults; list active assumptions in a summary block.
  - *High Blast Radius / Irreversible*: Pause and ask at most 1 to 3 numbered questions. For each question:
    - State recommended default (`(Recommended) Option A`).
    - Provide 2–3 mutually exclusive choices with one-line engineering trade-offs.

---

## 4. Phase 2: Step-by-Step Execution Procedure (Zone 2 Reasoning)

Copy this checklist into working notes and check off each item as completed:

- [ ] **Step 2.1 (Plan Intermediate State)**: For complex or batch changes, write target state to `plan.json`.
- [ ] **Step 2.2 (Execute Core Workflow)**: Implement changes according to the Task Routing Table, adhering strictly to the Footguns below.
- [ ] **Step 2.3 (Deterministic Validation — Zone 3 Gate)**: Run verification:
  ```bash
  python3 scripts/validate.py path/to/output
  ```
- [ ] **Step 2.4 (Fix Loop)**: If `validate.py` outputs JSON errors, fix each coordinate and re-run Step 2.3 until 0 errors remain.

---

## 5. High-Specificity Domain Footguns

1. **Footgun 1 ({COMMON_TRAP_1})**: Never {NAIVE_PATTERN} because it causes {EXACT_FAILURE_SYMPTOM}. Instead, use {EXACT_SYNTAX}.
2. **Footgun 2 ({COMMON_TRAP_2})**: Remember that {SYSTEM_A} differs from {SYSTEM_B}; verify sample coordinates before batch mutation.
3. **Footgun 3 ({COMMON_TRAP_3})**: Saving with {LIBRARY_X} strips {PROPERTY}; preserve properties prior to writing.

---

## 6. Anti-Rationalization Guardrails

| Common Model Excuse | Why It Is Strictly Forbidden & Required Action |
|:--------------------|:-----------------------------------------------|
| "The change is small, so running scripts/validate.py is unnecessary." | Small edits routinely introduce syntax or schema regressions. Running validate.py is mandatory on every run. |
| "The error appears to predate these changes, so it can be ignored." | You cannot assume errors are pre-existing. Prove origin by checking the unmodified baseline file first. |
| "I verified the output mentally by reading the code." | Mental verification misses runtime edge cases. Always run the automated validation script. |
| "I'll hardcode the API key for now to test quickly." | Hardcoded secrets lead to credential leaks and security bans. Always read keys from .env. |

---

## 7. What This Skill Does NOT Do

- Does NOT handle {OUT_OF_SCOPE_TASK_1} (use {ALTERNATIVE_SKILL_OR_TOOL}).
- Does NOT handle {OUT_OF_SCOPE_TASK_2}.
- Does NOT make permanent unapproved production database changes.
- Does NOT commit private `.env` secret keys into version control.
