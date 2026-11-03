---
name: prospect-homepage-audit
description: >-
  Audits a prospect homepage in the browser and records a verified Pitch or Skip verdict with plain-word evidence.
  Use this skill when deciding whether a design or Framer rebuild pitch is justified from the homepage itself.
  Trigger on: "audit prospect homepage", "pitch or skip", "homepage audit".
  Do NOT use for cold outreach copy, pricing, or contact discovery. Do NOT use for judging a site from search snippets alone.
compatibility: Requires Python 3.9+ for scripts/validate.py
metadata:
  version: "1.0.0"
allowed-tools: Bash(python3:*) Read Write Glob Grep
---

# Prospect Homepage Audit

## 1. Core Reframing and Non-Negotiable Invariants

- **Mental Model**: A pitch is justified only by a flaw actually seen on the homepage, not by a funding or hiring trigger alone.
- **Hard Invariant 1**: Never deliver a Pitch verdict without a validate.py pass.
- **Hard Invariant 2**: Never guess a website, handle, or contact. Mark it Unknown and stop that branch.
- **Hard Invariant 3**: Keep trigger, verdict, evidence, and pitch angle in separate fields, so one strong trigger cannot hide a good homepage.

## 2. Task Routing Decision Table

| Scenario / Intent | Recommended Approach | Supporting Reference |
|:------------------|:---------------------|:---------------------|
| Judge one homepage for a rebuild pitch | Run Phase 1 and Phase 2 below, then validate | references/homepage-verdicts.md |
| Re-check a homepage that may have changed | Re-run Phase 1 from a fresh browser view, do not reuse an old verdict | references/homepage-verdicts.md |
| Homepage is good but hiring is live | Do not pitch the homepage, pitch the hiring need only after re-checking the role is open | references/homepage-verdicts.md |

## 3. Phase 1: Silent Discovery and Ambiguity Triage

- [ ] **Step 1.1**: Open the prospect homepage in the browser and record what you actually saw, in plain words.
- [ ] **Step 1.2**: If the homepage cannot be opened, mark verdict Unknown, mark website Unknown if no verified site exists, and stop. Do not guess an address.
- [ ] **Step 1.3**: If the request is unclear about which prospect or which URL, ask at most 1 to 3 compact questions, with a recommended default where safe. Otherwise proceed.

## 4. Phase 2: Step-by-Step Execution Procedure

- [ ] **Step 2.1**: Classify the homepage using references/homepage-verdicts.md: Pitch only when it looks weak, rushed, or unfinished. Skip when it already looks polished and complete.
- [ ] **Step 2.2**: Write evidence as one concrete sentence, for example: text-only hero, no product visual, right side empty.
- [ ] **Step 2.3**: Write a pitch angle only for Pitch verdicts, and only from the evidence in Step 2.2. For Skip verdicts, write no homepage pitch angle.
- [ ] **Step 2.4**: Save the record as JSON with name, website, verdict, evidence, and pitch_angle, then run deterministic validation:
  ```bash
  python3 scripts/validate.py path/to/prospect.json
  ```
- [ ] **Step 2.5**: If validate.py fails, fix the record at its source field and re-run until it passes with exit code 0. Do not report a verdict while validation fails.

## 5. Anti-Rationalization Guardrails

| Common Excuse | Why It Is Forbidden and Required Action |
|:--------------|:----------------------------------------|
| "The funding news is strong, so the site must be weak." | Funding is not a homepage flaw. Open the homepage and judge it, or mark verdict Unknown. |
| "The search snippet looks dated, so I can pitch it." | Snippets are leads, not proof. Use the browser view only for the verdict. |
| "Validation is overkill for one record." | One bad record misdirects outreach. Run validate.py on every record. |

## 6. What This Skill Does NOT Do

- Does NOT write outreach messages, subject lines, or Loom scripts.
- Does NOT find emails, LinkedIn profiles, or phone numbers.
- Does NOT judge inner pages, pricing pages, or company pages as a substitute for the homepage.
- Does NOT deliver a verdict from a search snippet, screenshot caption, or second-hand description.
