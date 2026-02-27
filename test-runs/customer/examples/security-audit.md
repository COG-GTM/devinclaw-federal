# Example: Security Vulnerability Audit

## Scenario

Your team is preparing for a compliance audit (SOC 2 / ISO 27001). You need a thorough security scan of your web application before the auditors arrive, with findings documented in a format the compliance team can use.

## Setup

| Field | Value |
|-------|-------|
| **Skill** | Security Vulnerability Scan |
| **Target** | Customer-facing web application (Node.js/Express, React frontend, PostgreSQL) |
| **Goal** | Identify vulnerabilities with severity ratings and remediation guidance |

## What to Prompt Devin

> Perform a security vulnerability analysis of this web application. Identify OWASP Top 10 issues, dependency vulnerabilities, authentication/authorization gaps, and data exposure risks. Produce a Security Scan report following DevinClaw's artifact contract.

## Expected Outputs

- Vulnerability inventory (categorized by OWASP Top 10)
- Severity ratings (Critical / High / Medium / Low)
- Dependency audit (known CVEs in node_modules)
- Authentication/authorization review
- Remediation plan with prioritized fix order

## What to Score

- **Completeness:** Were all OWASP categories assessed? Were dependencies scanned?
- **Accuracy:** Are the vulnerabilities real (not false positives)? Are severity ratings appropriate?
- **Actionability:** Can an engineer fix these issues using only the report? Are file locations and code references included?
- **SDLC Compliance:** Does the report meet artifact contract requirements? Evidence of each finding?
- **Domain Expertise:** Does the analysis go beyond surface-level scanning (e.g., identifying business logic vulnerabilities, not just missing headers)?

## What "Good" Looks Like

A strong run (score 8+) will find:
- SQL injection or NoSQL injection vectors with exact code locations
- JWT misconfiguration or session management issues
- IDOR (Insecure Direct Object Reference) in API endpoints
- Dependency vulnerabilities with specific upgrade paths
- Missing rate limiting on authentication endpoints
- Data exposure through verbose error messages or debug endpoints
