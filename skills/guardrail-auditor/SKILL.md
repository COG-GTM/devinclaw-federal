---
name: guardrail-auditor
description: Monitor and enforce Devin Enterprise guardrail compliance across all active sessions. Polls the Guardrails API for violations, logs findings to the audit trail, alerts the team on any breach, and blocks non-compliant work from merging. Use this skill as a continuous governance layer during any modernization campaign.
---

# Guardrail Auditor

## Overview

This skill provides continuous governance and compliance monitoring for all Devin sessions running within a DevinClaw modernization campaign. It integrates with the Devin Enterprise Guardrails API (`/v3beta1/enterprise/guardrail-violations`) to detect policy violations in real-time, log them to the centralized audit trail, and enforce organizational security and quality standards.

In a federal modernization context where 50-100+ Devin sessions may be running in parallel, automated guardrail enforcement is essential. Human reviewers cannot monitor every session — this skill ensures that no violation goes undetected, no non-compliant code reaches production, and every enforcement action is documented for federal audit requirements.

## What's Needed From User

- **Devin Enterprise API key**: Service user credential with `ManageEnterpriseSettings` permission
- **Guardrail configuration**: Which guardrails are active (defined in `audit/guardrail-config.json`)
- **Alert channel**: Where to send violation notifications (Slack channel, Teams channel, or email)
- **Enforcement mode**: `monitor` (log only) or `enforce` (block non-compliant PRs)
- **Polling interval** (optional): How frequently to check for violations (default: every 5 minutes)

## Procedure

1. **Load guardrail configuration**
   - Read `audit/guardrail-config.json` for active guardrail rules
   - Verify Devin Enterprise API connectivity with a test call
   - Confirm service user has `ManageEnterpriseSettings` permission
   - Log audit start event with timestamp and configuration hash

2. **Poll for guardrail violations**
   - Call `GET /v3beta1/enterprise/guardrail-violations` with time window filter
   - Parameters: `time_after` = last poll timestamp, `order` = asc, `first` = 200
   - Paginate through all results if `has_next_page` is true
   - Parse each violation: session_id, guardrail_id, timestamp, details

3. **Classify violation severity**
   - **CRITICAL**: Security guardrails (credentials in code, unauthorized network access, data exfiltration attempts)
   - **HIGH**: Quality guardrails (tests not written, spec not followed, forbidden file modifications)
   - **MEDIUM**: Process guardrails (PR description missing, commit message format, branch naming)
   - **LOW**: Style guardrails (formatting, naming conventions)

4. **Log to audit trail**
   - Write each violation to `audit/violations/YYYY-MM-DD.json` in structured format:
     ```json
     {
       "timestamp": "ISO-8601",
       "session_id": "devin-session-id",
       "guardrail_id": "guardrail-rule-id",
       "severity": "CRITICAL|HIGH|MEDIUM|LOW",
       "description": "What was violated",
       "action_taken": "logged|alerted|blocked",
       "resolved": false
     }
     ```
   - Append to running daily log — never overwrite

5. **Alert on violations**
   - CRITICAL: Immediate alert to all configured channels + attempt to pause the session
   - HIGH: Alert to primary channel within 1 minute
   - MEDIUM: Batch alerts every 15 minutes
   - LOW: Include in daily summary report only
   - Alert format: `[GUARDRAIL VIOLATION] Severity: {X} | Session: {id} | Rule: {name} | Details: {description}`

6. **Enforce compliance (if enforcement mode is active)**
   - For CRITICAL/HIGH violations: add a comment to the associated PR requesting fix before merge
   - For sessions with 3+ unresolved violations: flag session for human review
   - Block merge of any PR with unresolved CRITICAL findings
   - Maintain a compliance scorecard per session and per engineer

7. **Generate compliance reports**
   - Daily summary: total sessions, total violations by severity, resolution rate, top violated rules
   - Weekly trend: violation rate over time, improving/degrading areas, engineer compliance scores
   - On-demand: full audit export for federal compliance reviews (JSON + CSV formats)

8. **Validate SDLC completion**
   - Cross-reference with `audit/sdlc-checklist.json` for every completed session:
     - [ ] SDD spec document exists in PR
     - [ ] TDD test plan exists
     - [ ] All tests passing
     - [ ] Devin Review completed with no unresolved CRITICAL bugs
     - [ ] Guardrails: zero CRITICAL/HIGH violations
     - [ ] Security scan completed
   - Sessions missing any checklist item are flagged as incomplete

## Specifications

- **Polling interval**: Configurable, default 5 minutes, minimum 1 minute
- **Retention**: Violation logs retained indefinitely (federal audit requirement)
- **API pagination**: Handle up to 10,000 violations per polling cycle
- **Time window**: Maximum 100-day lookback per API call (Devin API constraint)
- **Concurrency**: Single auditor instance per DevinClaw deployment (avoid duplicate alerts)
- **Idempotency**: Track last processed violation cursor to avoid re-processing

## Advice and Pointers

- Start in `monitor` mode for the first week to establish baseline violation rates before switching to `enforce`
- The most common violations in migration campaigns are: missing test coverage, hardcoded connection strings from copied legacy code, and overly broad file access patterns
- Keep guardrail rules specific and actionable — vague rules generate false positives that erode trust in the system
- Review and tune guardrail rules weekly based on violation patterns — too many LOW violations create alert fatigue
- Federal auditors will ask for the violation log during Authority to Operate (ATO) reviews — ensure the log format is clean and queryable


## Self-Verification Loop (Devin 2.2)

After completing the primary procedure:

1. **Self-verify**: Run all applicable verification gates:
   - Build/test gates: API connectivity confirmed, violation log integrity verified
   - Audit gates: no gaps in polling timeline, all violations classified and logged
   - Alert gates: notification delivery confirmed for Critical/High violations
2. **Auto-fix**: If any verification gate fails, attempt automated repair — adjust code, configuration, or test fixtures to resolve the failure.
3. **Re-verify**: Run all verification gates again after fixes. Confirm each gate transitions from FAIL to PASS.
4. **Escalate**: If auto-fix fails after 2 attempts, escalate to human reviewer with a complete evidence pack. Include the failing gate identifier, error output, attempted fixes, and root cause hypothesis.

## Artifact Contract

Every stage of this skill produces paired outputs for machine-consumable handoff:

| Stage | Markdown Output | JSON Output |
|-------|----------------|-------------|
| Violation Polling | `violation_poll.md` | `violation_poll.json` |
| Violation Analysis | `violation_analysis.md` | `violation_analysis.json` |
| Alert Generation | `alert_generation.md` | `alert_generation.json` |
| Compliance Report | `compliance_report.md` | `compliance_report.json` |

JSON outputs must conform to the schema defined in `audit/artifact-schemas/`. Markdown outputs are the human-readable narrative; JSON outputs are the machine-consumable contract consumed by the next stage or by OpenClaw for artifact validation.

## Evidence Pack

On completion, produce `evidence-pack.json` containing:

```json
{
  "session_id": "<Devin session identifier>",
  "timestamp": "<ISO 8601 completion time>",
  "skill_id": "devinclaw.guardrail_auditor.v1",
  "artifacts": [
    {
      "filename": "<output file>",
      "sha256": "<SHA-256 hash of file contents>",
      "stage": "<which stage produced this artifact>"
    }
  ],
  "verification": {
    "gates_run": ["<gate_1>", "<gate_2>"],
    "gates_passed": ["<gate_1>", "<gate_2>"],
    "gates_failed": [],
    "auto_fix_attempts": 0,
    "test_summary": {"passed": 0, "failed": 0, "skipped": 0},
    "scan_summary": {"critical": 0, "high": 0, "medium": 0, "low": 0}
  },
  "knowledge_updates": [
    {
      "action": "created|updated",
      "knowledge_id": "<Devin knowledge entry ID>",
      "summary": "<what was learned>"
    }
  ],
  "escalations": [
    {
      "gate": "<failing gate>",
      "reason": "<why auto-fix failed>",
      "evidence": "<link to error output>"
    }
  ]
}
```

## Escalation Policy

- **Divergence threshold**: 0.35 — if parallel verification sessions disagree beyond this threshold on key findings, escalate to human reviewer with both evidence packs for adjudication.
- **Human approval required for**: guardrail rule modifications, violation severity reclassification, enforcement mode changes (monitor → enforce), audit log export for ATO.
- **Auto-escalate on**: Any security finding rated HIGH or CRITICAL, any risk of data loss or corruption, any changes to authentication or authorization logic, any modification to safety-critical code paths (DO-178C applicable systems).

## Forbidden Actions

- Do not delete or modify violation log entries — audit logs are immutable
- Do not disable guardrails without explicit human authorization logged in the audit trail
- Do not automatically resolve violations — only humans can mark violations as resolved
- Do not expose API credentials in violation reports or alerts
- Do not skip polling cycles — if the API is unavailable, log the outage and retry with exponential backoff
