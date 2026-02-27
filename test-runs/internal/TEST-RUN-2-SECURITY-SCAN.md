# Test Run 2: Security Scan
**Target:** `legacy-sample-app/legacy-client`
**Skill:** `security-scan`
**Spoke:** Manual execution following skill procedure
**Date:** 2026-02-24 11:00 PM PST

---

## Task
"Run a STIG/NIST compliance scan on the legacy-client codebase"

## Findings (STIG Mapped)

### CAT I — Fix Before Any Production Deployment

| ID | Control | Finding | File:Line |
|----|---------|---------|-----------|
| SEC-001 | SI-10 | **SQL Injection** — `fnsMessage.getFNS_ID()` concatenated into SQL string via `prepareStatement()`. Defeats parameterization. | NotamDb.java:371 |
| SEC-002 | AC-3 | **No authentication on REST API** — All endpoints (`/notamTable/:id`, `/notamSearch/:id`, etc.) accessible without auth. notification data exposed to any network client. | FnsRestApi.java:70+ |
| SEC-003 | SI-2 | **Log4Shell exposure** — `slf4j-log4j12:1.7.30` routes to vulnerable Log4j. | pom.xml |
| SEC-004 | SI-2 | **H2 RCE** — `h2:1.4.200` has remote code execution via JDBC URL. | pom.xml |
| SEC-005 | SI-2 | **Abandoned SSH library** — `jsch:0.1.55` has Terrapin attack vulnerability, no longer maintained. | pom.xml |

### CAT II — Fix Within 30 Days

| ID | Control | Finding | File:Line |
|----|---------|---------|-----------|
| SEC-006 | SC-8 | **No TLS on database connections** — `notamDbDataSource` uses plain JDBC URLs, no SSL/TLS enforcement. | NotamDb.java:48-50 |
| SEC-007 | AU-2 | **No security audit logging** — No log entries for data access, query execution, or REST requests beyond error handling. | All files |
| SEC-008 | SI-11 | **Verbose error messages** — `logger.error("Createing Select Statement: " + e.getMessage())` exposes internal details. | NotamDb.java:437,455,477 |
| SEC-009 | IA-5 | **Default empty password** — `protected String password = ""` as default. | NotamDbConfig.java:8 |
| SEC-010 | SI-2 | **Java 1.7 target** — End-of-life since 2022, missing security patches. | pom.xml |
| SEC-011 | SC-28 | **No encryption at rest** — H2 embedded database stores notification data unencrypted. | NotamDb.java |

### CAT III — Fix Within 90 Days

| ID | Control | Finding | File:Line |
|----|---------|---------|-----------|
| SEC-012 | — | Misspelled error messages (inconsistent logging) | NotamDb.java |
| SEC-013 | SI-10 | No input validation on REST path parameters (`:id`) | FnsRestApi.java:76 |
| SEC-014 | — | No security headers on REST responses (CSP, HSTS, X-Frame-Options) | FnsRestApi.java |

## Summary
| Severity | Count |
|----------|-------|
| CAT I (Critical) | 5 |
| CAT II (Medium) | 6 |
| CAT III (Low) | 3 |
| **Total** | **14** |

**Verdict:** This application would **fail** an ATO review. 5 CAT I findings must be remediated before any production deployment.

---

## Workflow Assessment

### What Worked
✅ STIG control mapping was straightforward — the persona knowledge helped me know what to look for
✅ Found a REAL SQL injection in REAL enterprise ode — this is exactly what the ChBA demo should show
✅ Dependency CVE analysis was accurate and actionable
✅ Findings are formatted in a way an ATO assessor would accept

### What Didn't Work
❌ **No automated scanning** — Manual grep/read vs. SonarQube MCP or OWASP ZAP that would find these automatically
❌ **No auto-remediation** — Skill says "auto-fix" but without Devin, I can only report findings, not fix them
❌ **No XCCDF output** — Skill mentions STIG scan results in XCCDF format, but there's no tooling to generate that
❌ **Missing regression tests** — Skill says "write a test that reproduces the original attack vector" — can't do that without Devin spawning a session

### Honest Score: 7/10
Higher than the legacy analysis because the security-auditor persona knowledge is genuinely good — it directed me to the right controls, the right patterns, and the right severity classifications. The findings are real and actionable. But it's still a manual process that wouldn't scale across 200 apps.
