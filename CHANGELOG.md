# Changelog

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
