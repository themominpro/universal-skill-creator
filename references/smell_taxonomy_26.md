# The 26-Smell Taxonomy for AI Agent Skills

Synthesized from the empirical study *From Anatomy to Smells: An Empirical Study of SKILL.md in Agent Skills* (Hong, Imani, Ahmed, UC Irvine / arXiv:2607.01456).

---

## 1. Under-Specified Guidance

| Acronym | Smell Name | Failure Mechanism | Remediation Standard |
|:--------|:-----------|:------------------|:---------------------|
| **TSW** | The Stepless Workflow | Writing an entire procedure as a monolithic paragraph. The agent skips sub-steps and loses execution state. | Decompose into numbered, imperative phases (`Step 1`, `Step 2`) with explicit inputs and outputs. |
| **TOB** | The Option Buffet | Listing multiple alternative tools or libraries (e.g. *"Use pypdf, fitz, or pdfplumber"*) without picking one. The agent hesitates or picks randomly. | Prescribe a single opinionated default tool. State exact criteria for when to fall back. |
| **MUS** | Missing Utility Script | Asking the LLM to do fragile parsing, regex, AST diffing, or schema validation in tokens. Model hallucinates coordinates or misses syntax errors. | Offload all deterministic math, AST comparisons, and validation to executable scripts in `scripts/`. |
| **MDT** | Missing Decision Tree | Failing to provide routing logic when a skill handles multiple tasks (e.g. create vs. edit vs. inspect). | Place an explicit Task Routing Table at the top of `SKILL.md` mapping scenarios to workflows. |

---

## 2. Over-Prescribed Guidance

| Acronym | Smell Name | Failure Mechanism | Remediation Standard |
|:--------|:-----------|:------------------|:---------------------|
| **SOC** | Series of Commands | Dictating a rigid, unadaptable sequence of literal shell commands without explaining intent. Strips the LLM of adaptive judgment on edge cases. | Keep deterministic gates in code (`scripts/`), but give the LLM goal-oriented flexibility and edge-case heuristics in the reasoning zone. |

---

## 3. Missing Verification & Feedback Loops

| Acronym | Smell Name | Failure Mechanism | Remediation Standard |
|:--------|:-----------|:------------------|:---------------------|
| **NVS** | No Validation Step | Treating output generation as a one-shot process without post-generation verification. Corrupted outputs ship directly to the user. | Mandate a `Run, Validate, Fix, Repeat` loop using a deterministic script or visual check. |
| **EWP** | Execute Without a Plan | Instructing the agent to immediately execute destructive or batch mutations without an intermediate planning step. | Enforce `Plan, Validate, Execute`: output a structured plan file (e.g. `plan.json`), validate it, then execute. |
| **NAH** | Never Asks Human | Providing no instruction for when the agent must pause for human clarification on blocking unknowns. Agent silently guesses user intent. | Encode an explicit ambiguity triage protocol (OMSC) that asks 1–3 high-leverage multiple-choice questions with defaults. |

---

## 4. Missing Follow-Through Guards

| Acronym | Smell Name | Failure Mechanism | Remediation Standard |
|:--------|:-----------|:------------------|:---------------------|
| **RL** | Rationalization Loophole | The #1 defect in production skills. Soft instructions allow the model to invent excuses to skip tests (*"The change was small so testing is unnecessary"*). | Include an explicit **Anti-Rationalization Table** naming model excuses and why each is strictly forbidden. |
| **NPT** | No Progress Tracking | Running multi-file or multi-turn tasks without a checklist. The agent forgets what has been done and duplicates work. | Provide a copyable Markdown checklist (`- [ ] Step 1...`) that the agent checks off during execution. |

---

## 5. Context Bloat

| Acronym | Smell Name | Failure Mechanism | Remediation Standard |
|:--------|:-----------|:------------------|:---------------------|
| **UD** | Undelegated Detail | Embedding massive API schemas, 500-line code blocks, or rare edge-case manuals directly in `SKILL.md`. Dilutes agent attention. | Keep `SKILL.md` under 500 lines; push deep reference manuals to `references/` and templates to `assets/`. |
| **LSB** | Lengthy Skill Body | `SKILL.md` body exceeds 5,000 tokens. Instructions get permanently sheared off during context auto-compaction. | Enforce top-heavy token layout; move sub-workflows to 1-hop reference files. |
| **LSN** | Lengthy Skill Name | Skill name exceeds 64 characters, causing parser rejections. | Keep `name` between 1–64 characters, lowercase alphanumeric with hyphens. |
| **LSD** | Lengthy Description | Description exceeds 1,024 characters, overflowing the system prompt discovery catalog. | Keep `description` under 1,024 characters, concise, and keyword-rich. |
| **CSD** | Confusing Description | Description omits [What it does], [When to trigger], or colloquial user keywords. Skill undertriggers. | Structure description as an assertive third-person trigger contract with negative boundaries. |

---

## 6. Missing Safeguards

| Acronym | Smell Name | Failure Mechanism | Remediation Standard |
|:--------|:-----------|:------------------|:---------------------|
| **NG** | No Guardrails | Failing to define scope exclusions. Skill activates on out-of-scope or destructive requests. | Include an explicit **What This Skill Does NOT Do** section. |
| **MZ** | Mixed Zones | Mixing deterministic compliance checks with soft LLM suggestions in the same paragraph without distinction. | Partition into 3 distinct zones: Zone 1 (Deterministic Pre-Gates), Zone 2 (LLM Reasoning), Zone 3 (Deterministic Output Verification). |

