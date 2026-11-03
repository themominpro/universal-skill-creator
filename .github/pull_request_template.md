## Description
Provide a concise explanation of what this pull request changes and why.

## Type of Change
- [ ] 🐛 Bug fix (non-breaking change fixing an issue)
- [ ] ✨ New feature / script / reference guide
- [ ] 🔒 Security patch
- [ ] 📝 Documentation enhancement
- [ ] 🧪 Evaluation cases / test additions

## Checklist Before Merging
All contributors must run and pass the following quality gates locally:
- [ ] `python scripts/audit_skill.py .` reports **100/100 (Grade A+, PASS)**
- [ ] `python scripts/security_scan.py .` reports **status: PASS (0 criticals)**
- [ ] `python scripts/run_evals.py .` reports **10/10 PASS (100% pass rate)**
- [ ] `python scripts/test_skill_trigger.py .` passes trigger precision & recall checks
- [ ] No unrendered placeholders (`{TODO}`, `{PLACEHOLDER}`) remain in committed files
- [ ] Zero secret leaks or uncommitted `.env` files
