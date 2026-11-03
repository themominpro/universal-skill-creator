# Contributing to Universal Skill Creator

Thank you for your interest in contributing to **Universal Skill Creator**! We welcome contributions from the community to expand agent skills, improve static linting, and harden security gates.

---

## 🛠️ Development & Testing Workflow

Before opening a pull request, ensure all local verification checks pass:

### 1. Run the Empirical Test Suite
```bash
python scripts/run_evals.py .
```
All 10 test cases must report `status: PASS` with a 100% pass rate.

### 2. Run the Layout Conformance Linter
```bash
python scripts/audit_skill.py .
```
Must achieve **100/100 (Grade A+)** with 0 violations and 0 warnings.

### 3. Run the AST Security Scanner
```bash
python scripts/security_scan.py .
```
Must report `0 critical issues`.

### 4. Run the Dynamic Trigger Benchmark
```bash
python scripts/test_skill_trigger.py .
```
Must achieve 100% Recall and Precision against declared trigger queries.

---

## 📜 Architectural Guidelines

Any proposed changes or new skills must strictly adhere to the **Three-Zone Hybrid Architecture**:

1. **Zone 1 (`SKILL.md`)**:
   - Keep under 200 lines (<4,000 tokens).
   - Invariants and Task Routing Table must appear in the top 1,000 tokens.
   - Include copyable `- [ ]` checklists and an explicit Anti-Rationalization Table.
2. **Zone 2 (`scripts/`)**:
   - Offload heavy syntax, regex, schema validation, and calculations to standard-library Python scripts.
   - Scripts must emit clean JSON to `stdout` and exit `0` on pass / `1` on fail.
3. **Zone 3 (`references/`)**:
   - Organize secondary playbooks, schemas, and specifications into flat markdown files (exactly 1 hop deep).

---

## 🚀 Submitting a Pull Request

1. Fork the repository and create your branch from `main`:
   ```bash
   git checkout -b feature/my-new-skill-or-check
   ```
2. Commit your changes with clear, semantic commit messages:
   ```bash
   git commit -m "feat(linter): add new rule for parameter validation"
   ```
3. Push to your fork and submit a Pull Request describing your changes, test results, and rationale.

Thank you for building the open-source future of agentic AI skills!

