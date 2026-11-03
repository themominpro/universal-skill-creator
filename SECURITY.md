# Security Policy

## 🔒 Supported Versions

The Universal Skill Creator engineering team actively maintains and releases security patches for the following versions:

| Version | Supported          |
|:--------|:-------------------|
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

---

## 🛡️ Architectural Security Commitments

Universal Skill Creator is engineered specifically to eliminate supply-chain and execution vulnerabilities common in LLM tooling:

1. **Deterministic Pre-Execution AST Gate**: Skills created or verified through this framework must pass `scripts/security_scan.py` with zero critical findings before distribution.
2. **Dynamic Execution Prohibitions**: Prohibits `eval()`, `exec()`, `os.system()`, and `subprocess(..., shell=True)` across all companion scripts.
3. **Zip-Slip & Symlink Immunity**: Extraction scripts strictly reject symlinks and validate all archive member paths against parent directory escapes.
4. **Secret Isolation**: Real API credentials must strictly reside in `.env` (gitignored). `.env.example` accepts placeholder strings only.

---

## 🚨 Reporting a Vulnerability

If you discover a security vulnerability, private credential leak, or code execution loophole, please report it responsibly:

- **Email**: `security@gtmengineering.io` (or open a confidential draft advisory on GitHub via **Security -> Report a vulnerability**).
- **Include**:
  1. A description of the vulnerability and attack vector.
  2. Proof-of-concept repository, script, or steps to reproduce.
  3. Affected component(s) (`scripts/`, `agents/`, `evals/`, or runtime engines).
- **Timeline**:
  - Initial acknowledgement: within **24 hours**.
  - Assessment and status update: within **48 hours**.
  - Remediation patch release: within **7 days** (or sooner depending on severity).

Please do **NOT** open public GitHub issues or post exploit details on social media until a security fix has been released.
