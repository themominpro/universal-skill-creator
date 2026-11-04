# 🛡️ The 38 Agent & Skill Anti-Patterns Reference (`playbook_anti_patterns_38.md`)

Derived from the empirical **LLM Agent Skills Playbook (2026)**, this reference codifies the 38 fatal anti-patterns across skill authoring, prompting, and agent harnesses.

---

## Part 1: Skill Authoring Anti-Patterns (1–22)

| # | Anti-pattern | Symptom in Production | Root Cause | Architectural Remedy |
|---|---|---|---|---|
| **1** | **Vague / Descriptive Description** | Skill never triggers autonomously; user must manually force invocation. | Description lacks imperative action verbs ("Use this skill when...") or YAML is malformed. | Rewrite description with clear trigger verbs and file extensions. |
| **2** | **Over-Broad Description** | Skill fires on adjacent, unrelated tasks, stealing triggers from sibling skills. | Generic verbs without negative exclusion guards. | Append explicit negative boundaries: `"Do NOT use for..."`. |
| **3** | **Skill Sprawl / Description Bloat** | Descriptions are silently dropped by the harness (Claude Code caps at 1% context, Codex at 2%/8k chars). | Too many installed skills or verbose frontmatter. | Front-load trigger terms; keep description strictly under 1,024 characters. |
| **4** | **Tutorial Body** | Slow execution, high token burn, zero accuracy gain. | Restating generic programming or API facts the frontier model already knows. | Delete tutorials. Author **gotchas, non-obvious traps, and footguns only**. |
| **5** | **500+ Line Monolith Body** | Instructions are ignored mid-file; severe context compaction shearing. | Cramming schemas, playbooks, and docs into a single `SKILL.md`. | Split secondary guides into flat `references/` (1 hop deep). Keep body <450 lines. |
| **6** | **Nested Multi-Hop References (A→B→C)** | Model executes partial reads (`head -100`), loses links, misses rules. | Deep directory trees and chained links. | Every reference file must be linked directly from `SKILL.md` (exactly 1 hop). |
| **7** | **Logic in Prose (The MUS Smell)** | Inconsistent outputs, hallucinated calculations, slow token spend. | Asking the LLM to execute math, regex, AST diffs, or parsing in prompt tokens. | Bundle executable Python scripts in `scripts/`; say "run", never "read". |
| **8** | **Chatty / Deferring Scripts** | Model gets confused by Python tracebacks or unhandled exceptions. | `except: pass`, raw tracebacks, or undocumented magic numbers. | Scripts must output clean, structured JSON to `stdout` with actionable error messages. |
| **9** | **Trusting the Green Exit Code Alone** | Corrupted or incomplete results delivered confidently. | Validator returns 0 without validating semantic completeness. | Inspect stdout JSON status and error arrays, not just exit code 0. |
| **10** | **No Verification Gate** | Silent errors ship directly to the user. | Absence of an external validation signal. | Enforce render/validate/recalc loops before task completion. |
| **11** | **Critical Rules Deep in Prose** | Rules followed initially, forgotten after long conversation turns. | Auto-compaction preserves only the first 5,000 tokens of invoked skills. | Place hard invariants and routing tables within the top 1,000 tokens of `SKILL.md`. |
| **12** | **Conflicting Instructions Across Skills** | Model hesitates, pauses, asks unnecessary user confirmation. | Accretion of competing rules across `AGENTS.md` and installed skills. | State precedence clearly; establish deterministic task boundaries. |
| **13** | **Hardcoded Time-Sensitive Facts** | Outdated recommendations generated after software updates. | Hardcoded dates like "before August 2025...". | Decouple legacy conventions into a dedicated "Deprecated Patterns" section. |
| **14** | **The Option Buffet (TOB)** | Model dithers, halts, or picks suboptimal tools. | Listing multiple libraries or approaches without an opinionated default. | Provide a single default tool per scenario and an escape hatch table. |
| **15** | **Inconsistent Terminology** | Rules misapplied to adjacent UI or domain components. | Using synonyms interchangeably (e.g., box/field/input/control). | Standardize on one exact domain term per concept. |
| **16** | **Platform Assumption / Shell Syntax Traps** | Scripts crash on Windows or non-Unix developer environments. | Hardcoded `scripts\x.py` backslashes or bash commands like `mktemp` and `unzip`. | Use Python's standard library (`pathlib`, `zipfile`, `tarfile`) for 100% cross-platform parity. |
| **17** | **Vendor Extension Overload** | Skill breaks when ported from Claude to Cursor, Antigravity, or Codex. | Relying on proprietary frontmatter keys (`hooks`, `paths`, `context: fork`). | Maintain a portable core (`name`, `description`, `license`, `metadata`, `requires_secrets`). |
| **18** | **Hardcoded Credentials / Unsafe Fetches** | Exfiltration vulnerability and security scanner rejection. | Embedding live API tokens or fetching unverified URLs. | Load keys from `.env` via zero-dependency `load_env()`; enforce pre-export AST scans. |
| **19** | **Authoring from Imagination** | Skill solves theoretical non-problems while missing real failure modes. | Writing rules without running baseline baseline-vs-skill evals. | Observe baseline model failures on real tasks before writing instructions. |
| **20** | **Evaluating in the Authoring Session** | False positive passes during QA. | Residual conversational context masks skill gaps. | Always test candidate skills in a fresh context or via isolated child subagents. |
| **21** | **Trivial Negative Trigger Tests** | Over-triggering skills ship to production. | Testing against obvious negatives like `"Write a poem about the ocean"`. | Test against **near-miss negatives** (adjacent domain prompts that belong elsewhere). |
| **22** | **Single-Model Calibration Bias** | Skill under-instructs lighter models or over-explains to frontier reasoning models. | Testing exclusively on a single model family. | Validate across model tiers (fast models vs. frontier reasoning models). |

---

## Part 2: Prompting & Agent Architecture Anti-Patterns (23–38)

| # | Anti-pattern | Symptom in Production | Root Cause | Architectural Remedy |
|---|---|---|---|---|
| **23** | **CoT Scaffolding on Reasoning Models** | Token inflation, slower latency, degraded output quality. | Prompting reasoning models (o3, Gemini 2.0 Flash Thinking, Claude 3.7) with "think step by step". | Focus prompts strictly on outcomes, constraints, and verifiable deliverables. |
| **24** | **Blanket Tool Mandates** | Tool over-triggering, runaway thinking loops. | Prompting with generic directives like "if in doubt, call tool X". | Use targeted, scenario-based Task Routing Tables. |
| **25** | **Contradictory System Prompts** | Wasted reasoning tokens, flaky execution. | Accretion of competing rules across system prompts and skills. | Resolve hierarchy; declare each invariant exactly once. |
| **26** | **Repetitive "Ask First" Restrictions** | Annoying approval loops for trivial, non-destructive actions. | Excessive defensive phrasing in prompt files. | Adopt the OMSC Ambiguity Filter: ask 0 questions for low-blast-radius standard tasks. |
| **27** | **Deprecated API Parameters** | HTTP 400 crashes on modern models. | Sending deprecated flags (e.g. `budget_tokens` on Claude 4.7+, `thinking_budget` on Gemini 3.x). | Use vendor-sanctioned parameters (`effort`, `reasoning.effort`). |
| **28** | **Multi-Agent by Default** | 15× token burn, coordination errors, latency spikes. | Spawning subagents for simple or shared-context tasks. | Use the Escalation Ladder: single agent loop first; reserve subagents for high-value parallel tasks. |
| **29** | **Intrinsic Self-Critique Loops** | Accuracy flatlines or hallucinates error fixes. | Asking the LLM to critique its own work without external tools. | Always ground critique in external signals (Python tests, schema linters, AST checks). |
| **30** | **Treating Reasoning Traces as Audit Guarantees** | False security assurance. | Assuming CoT verbalizes all internal model steps (studies show <20% reveal). | Audit environment state and deliverable outputs, not internal thoughts. |
| **31** | **Optimizing Against CoT Monitors** | Obfuscated reward hacking. | Model learns to disguise real actions to satisfy internal monitor. | Grade verifiable environment outcomes instead of monitoring tokens. |
| **32** | **Tool Sprawl & Overlap** | Model dithers between overlapping tools; high token burn. | Creating individual tools for every API endpoint. | Consolidate tools; use clear prefixes and parameter schemas. |
| **33** | **Dumping Raw Tool Outputs into Context** | Context rot, attention dilution, lost instructions. | Returning unpaginated 50KB JSON/CSV dumps into prompt tokens. | Filter and summarize tool outputs in code before returning to context. |
| **34** | **One-Shotting Long Software Builds** | Incomplete applications, premature "task completed" claims. | Attempting multi-hour tasks in a single turn without progress tracking. | Use Initializer + Worker harnesses with persistent progress files (`.passes` flags). |
| **35** | **Skipping End-to-End Verification** | Code looks syntactically valid but fails on execution. | Trusting code generation without running it. | Enforce Plan-Validate-Execute loops with test scripts. |
| **36** | **Misconfigured LLM Graders** | False evaluations; benchmark saturation. | Ambiguous evaluation rubrics without edge-case escapes. | Calibrate graders with human benchmarks; provide an "Unknown" escape hatch. |
| **37** | **Aggressive Context Compaction** | Subtle constraints lost during long chat turns. | Compaction prompts tuned purely for shortness. | Retain must-have rules in Tier 1; clear transient tool results before compacting core rules. |
| **38** | **Irrelevant Few-Shot Dumps** | High token waste, model blindly mimics irrelevant details. | Copy-pasting massive examples into prompt files. | Limit examples to 2–3 compact, highly diverse, relevant demonstrations. |
