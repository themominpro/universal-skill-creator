# Compaction-Resilient Skill Architecture & Token Layout

In long-running agentic conversations, conversational context triggers **auto-compaction**. In systems like Claude Code and other modern harnesses, the harness re-attaches **only the first 5,000 tokens** of an invoked skill within a shared compaction budget.

Any critical safety rules, invariants, or tool choices placed below the 5,000-token threshold are **permanently sheared off** after compaction.

---

## The 6-Tier Priority Token Layout

To maximize survival of core invariants through context compaction, organize `SKILL.md` in this exact top-down hierarchy:

```
┌────────────────────────────────────────────────────────────────────────┐
│ TIER 1: Core Reframing & Non-Negotiable Invariants  (Tokens 1–500)      │
│ - Mental model of the domain                                           │
│ - Pre-installed package notices (saves shell turns)                    │
│ - Hard safety invariants that MUST survive auto-compaction             │
├────────────────────────────────────────────────────────────────────────┤
│ TIER 2: Task Routing Decision Table                  (Tokens 500–1,000)│
│ - Maps scenario -> Single default tool -> On-demand reference file     │
│ - Eliminates Option Buffet (TOB) and Missing Decision Tree (MDT)      │
├────────────────────────────────────────────────────────────────────────┤
│ TIER 3: Deterministic Gates & Ambiguity Triage     (Tokens 1,000–1,500)│
│ - Zone 1 preconditions (must pass before open reasoning)               │
│ - OMSC Question triage protocol (silent discovery before asking)       │
├────────────────────────────────────────────────────────────────────────┤
│ TIER 4: Numbered Steps & Copyable Checklists       (Tokens 1,500–3,000)│
│ - Numbered imperative execution phases (Step 1, Step 2)                │
│ - Copyable `- [ ]` progress checklists (eliminates NPT smell)          │
│ - Links to deterministic scripts in scripts/                           │
├────────────────────────────────────────────────────────────────────────┤
│ TIER 5: Domain Footguns & Anti-Rationalization     (Tokens 3,000–4,200)│
│ - High-specificity API traps and coordinate offsets                    │
│ - Anti-Rationalization Table (bans model excuses for skipping checks)  │
├────────────────────────────────────────────────────────────────────────┤
│ TIER 6: Output Contract & Scope Exclusions         (Tokens 4,200–4,800)│
│ - Standardized report or deliverable format                            │
│ - Explicit "What This Skill Does NOT Do" boundary block                │
└────────────────────────────────────────────────────────────────────────┘
```

---

## Token Allocation Budgets

| Component | Target Budget | Hard Maximum | If Exceeded, Remediation Action |
|:----------|:--------------|:-------------|:--------------------------------|
| Frontmatter | ~100 tokens | 1,024 chars | Shorten description; remove verbose fluff. |
| Tier 1–3 (Core & Routing) | ~1,200 tokens | 1,500 tokens | Condense into Markdown tables. |
| Tier 4 (Workflow & Steps) | ~1,500 tokens | 2,000 tokens | Move detailed API guides into `references/`. |
| Tier 5–6 (Guards & Scope) | ~1,200 tokens | 1,500 tokens | Focus on the top 3–5 real footguns; prune theoretical edge cases. |
| **Total SKILL.md Body** | **<4,000 tokens** | **<5,000 tokens** | Move sub-workflows to `references/` (1 hop deep). |

