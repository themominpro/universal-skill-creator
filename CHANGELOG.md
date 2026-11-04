# Changelog

## v1.0 - Example Guardrail - 2026-11-04, no version bump

- Hard Invariant 6 added to SKILL.md, and the same line added to examples/built-example/prospect-homepage-audit/README.md: shipped examples show structure only, do NOT copy an example's domain rules into a new skill, build every new skill from the user's SOP, transcript, and domain research. SKILL.md is now 250 lines, file count unchanged at 65.

## v1.0 - Final - 2026-11-04

- Pure package: dossier, WORKFLOW, dead templates, duplicate packager, and author fields removed. What remains is SKILL.md, 5 agent roles, 9 references, 8 scripts, 2 templates, and 1 built example.
- Trigger fix: negation guard and consecutive phrase matching in test_skill_trigger.py, so "Create a landing page, not a skill" no longer triggers.
- Audit fix: placeholder and TODO checks extended to agents/ and examples/ skills, and unreferenced agent files are now warnings.
- Security fix: security_scan.py now scans .md files for hardcoded secrets, in addition to code and config files.
- Bundle fix: bundle_package.py now runs audit and security gates before creating archives, and aborts if either fails, unless --skip-gates is passed explicitly.
- MCP fix: discover_env.py now also checks VS Code and Cursor MCP configs, in addition to Antigravity and Claude Desktop paths.
- Connection fix: references/landscape-example.json added as the schema template for analyze_skill_market.py, referenced from competitor_teardown_protocol.md.
- Test results for this final package, from the packaged zip installed as universal-skill-creator, 2026-11-04:
  - audit_skill.py: 100, Grade A+, PASS, 0 violations, 0 warnings
  - security_scan.py: PASS, 40 files scanned including .md files, 0 critical, 0 warnings
  - test_skill_trigger.py main set: 12/12 positive, 14/14 negative, 100.0% recall, 100.0% precision
  - test_skill_trigger.py negation set: 6/6 positive, 6/6 negative
  - run_evals.py: 10/10 cases PASS, 100.0%, including bundle gate pass, bundle gate fail, trigger negation, and discover_env
  - Example skill audit: prospect-homepage-audit 100, Grade A+, PASS
  - Bundle gate verified: packaging the passing example succeeds, packaging the gate-test bad skill fails with no archive created
  - File count in zip: 37 files, including the new landscape example, negation queries, and gate-test fixture

## v1.0 - God-Tier Behaviour Gates - 2026-11-04

- Version stays 1.0.0, no version bump, no author fields. This is the same v1.0 package with the 6 Top 7 gaps closed.
- Gatekeeper: references/gatekeeper_bootstrap.md + scripts/gatekeeper_hook.py, 1% rule, priority user > skills > default, subagent exemption, compaction failure mode.
- Pressure: references/pressure_scenarios.md + scripts/generate_pressure_scenarios.py, 4 combined scenarios, verbatim rationalizations, Thought | Reality table required, identical runs do not ship.
- Baseline grading: references/baseline_grading.md + agents/grader.md + scripts/grade_baseline.py, exact text/passed/evidence contract, eval_feedback required, ship gate with-skill >= 80%, delta > 0, no regression.
- Description split: scripts/eval_description_split.py, deterministic 60/40 train/test split by query hash, no overlap, test set must contain both classes, best description chosen by test score.
- Stub/router: references/stub_router_mode.md + scripts/router_eval.py + examples/stub-example/ (50-line stub, guide.md, router cases). Stub is exempt from full audit_skill.py; its gate is router_eval.py.
- Render QA: references/render_qa.md + scripts/render_qa.py, content + file gates, visual QA marked HUMAN_REQUIRED, never claimed by script.
- Fixed: SKILL.md section 12 no longer says "client proof dossiers"; that phrase contradicted the dossier removal. SKILL.md is now 228 lines, still under 450.
- Test results for this package, from the packaged zip installed as universal-skill-creator, 2026-11-04:
  - audit_skill.py: 100, Grade A+, PASS, 0 violations, 0 warnings
  - security_scan.py: PASS, 59 files scanned, 0 critical, 0 warnings
  - test_skill_trigger.py main set: 12/12 positive, 14/14 negative, 100.0% recall, 100.0% precision
  - run_evals.py: 17/17 cases PASS, 100.0%, including gatekeeper, pressure, baseline pass, baseline contract fail, description split, router, and render QA
  - Example skill audit: prospect-homepage-audit 100, Grade A+, PASS
  - Stub example: 50 lines, router_eval PASS, 3/3 router cases
  - Bundle gate verified: packaging the passing example succeeds, packaging the gate-test bad skill fails with no archive created

## v1.0 - QA Checkpoints, Docx/Pdf Extractor, Dossier Wording Removed - 2026-11-04

- Version stays 1.0.0, no version bump, no author fields.
- QA checkpoints: references/qa_checkpoints.md + scripts/record_qa.py, 5 checkpoints (teardown-domain, architecture, draft-workflow, gates, ship), max 2 questions per checkpoint, 5-line decision summary, (Recommended) default, high blast radius waits for user reply, low blast radius records assumed defaults. SKILL Phase 2 now has QA checkpoints as Step 2.2, before OMSC triage as Step 2.3.
- Input extractor: scripts/extract_text.py, no external dependencies, handles .txt, .md, .docx (ZIP/XML paragraph runs), and text-based .pdf (Tj/TJ streams, zlib). Scanned image-only PDFs warn and return no text, never invented text. Phase 0.2 now requires extraction before lexicon for .docx/.pdf.
- Dossier wording removed: references/competitor_teardown_protocol.md no longer says to emphasize advantages in a Client Pitch Dossier; agents/niche_researcher.md now returns a Market Intelligence Report, not a Dossier.
- Test results for this package, from the packaged zip installed as universal-skill-creator, 2026-11-04:
  - audit_skill.py: 100, Grade A+, PASS, 0 violations, 0 warnings
  - security_scan.py: PASS, 64 files scanned, 0 critical, 0 warnings
  - test_skill_trigger.py main set: 12/12 positive, 14/14 negative, 100.0% recall, 100.0% precision
  - run_evals.py: 20/20 cases PASS in working dir, including QA record pass, QA 3-question fail, and real .docx extraction

## v1.0 - Format Rule Clarified: Harness-First, Extractor Optional - 2026-11-04

- Version stays 1.0.0, no version bump.
- User clarification applied: this skill is used on Claude Code and Claude, which read .md, .pdf, .docx, .ppt, and similar formats natively, so format extraction is NOT a hard rule.
- SKILL Phase 0.2, routing table, domain ingestion reference, and extract_text.py docstring now say: use harness-native reading first, do not force extraction when the harness already read the file. The extractor remains as an optional fallback, with one hard use only: build_domain_lexicon.py reads text only, so extract to .txt first if you run the lexicon on a .docx or .pdf.
