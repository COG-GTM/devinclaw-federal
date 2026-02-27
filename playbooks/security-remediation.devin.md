# Playbook: Security Vulnerability Remediation

> **Required Knowledge:** `security-auditor`

## Overview
Scan codebases for security vulnerabilities against federal standards (STIG, NIST 800-53, FedRAMP) and auto-remediate findings. Integrates with Devin Review bug catcher for continuous security enforcement.

## When to Use
- Pre-deployment security hardening
- Remediating findings from security audits or penetration tests
- Continuous compliance monitoring during modernization
- Preparing for Authority to Operate (ATO) review

## Instructions

1. **Run static analysis**: Scan the codebase with SonarQube MCP (if available) or built-in analysis for OWASP Top 10 vulnerabilities. Cross-reference findings against the CVE/NVD database to identify known vulnerabilities (CVE identifiers) in dependencies and code patterns.

2. **Map findings to federal controls**: Each finding maps to STIG V-number and NIST 800-53 control. Classify by STIG severity: CAT I (fix now), CAT II (30 days), CAT III (90 days).

3. **Generate SDD remediation spec**: For each CAT I/II finding, create a spec describing the vulnerability, impact, and remediation approach.

4. **Remediate**: Apply fixes following the spec. Common patterns:
   - SQL injection → parameterized queries
   - XSS → input sanitization + CSP headers
   - Hardcoded credentials → environment variables + secrets manager
   - Missing auth → middleware enforcement
   - Weak crypto → upgrade to FIPS 140-2 approved algorithms
   - Missing audit logs → structured logging with security events

5. **Write regression tests**: For each remediated vulnerability, write a test that reproduces the original attack vector and validates it's blocked.

6. **Devin Review**: Auto-review the remediation PR. Bug catcher validates no new vulnerabilities introduced.

7. **CVE correlation**: For each finding, check if it maps to a known CVE identifier. Include CVE IDs in the remediation report for traceability against the National Vulnerability Database (NVD).

8. **Generate compliance report**: Output: finding ID, CVE ID (if applicable), severity, status (remediated/mitigated/accepted risk), test case ID, control mapping.

## Specifications
- CAT I findings must be remediated before any production deployment
- All crypto must be FIPS 140-2 validated (SC-13)
- TLS minimum: 1.2, prefer 1.3 (SC-8)
- Session timeout: ≤ 15 minutes (STIG V-220630)
- Password minimum: 14 characters (STIG V-220629)

## Advice
- The most common federal finding is missing audit logging — it's also the easiest to fix and the hardest to retrofit later
- Hardcoded credentials in migrated code is extremely common — grep for them in every PR
- Don't just fix the symptom; fix the pattern. If one endpoint has SQL injection, check ALL endpoints


## Self-Verification (Devin 2.2)

Before declaring this playbook complete:

1. **Run all verification gates**: Execute the full self-verify loop — build, test, lint, typecheck, security scan. If the playbook produced code changes, run the test suite and confirm all tests pass.
2. **Auto-fix failures**: If any gate fails, attempt automated repair. Re-run the failing gate. If it fails again after 2 attempts, escalate to human reviewer.
3. **Computer-use E2E** (if applicable): For changes that affect UI or user-facing functionality, use Devin 2.2 computer use to run the application and verify functional correctness.

## Evidence Pack Generation

On completion, produce `evidence-pack.json` in the output directory:

```json
{
  "playbook": "<this playbook name>",
  "session_id": "<Devin session ID>",
  "timestamp": "<ISO 8601>",
  "artifacts": [
    { "filename": "<file>", "sha256": "<hash>", "stage": "<stage>" }
  ],
  "verification": {
    "tests_passed": true,
    "lint_clean": true,
    "security_scan_clean": true,
    "gates_failed_and_auto_fixed": []
  },
  "knowledge_updates": [],
  "escalations": []
}
```

This evidence pack is required for SDLC validation and audit trail compliance (FAR 4.703).
