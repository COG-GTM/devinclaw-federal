---
name: incident-response
description: Automatically investigate and remediate production incidents triggered by monitoring alerts from Sentry, Datadog, or manual escalation. Use this skill when enterprise systems trigger error alerts, when production anomalies are detected, or when rapid root cause analysis and remediation is needed for mission-critical enterprise systems.
---

# Production Incident Response

## Overview

This skill provides automated investigation and remediation of production incidents affecting enterprise systems. It ingests alerts from monitoring platforms (Sentry, Datadog, PagerDuty, or manual escalation), triages severity against operational safety impact criteria, performs root cause analysis using log correlation and code tracing, generates a remediation plan, implements the fix through the full SDD-TDD-Devin pipeline, and produces a post-incident report for compliance and organizational learning.

Enterprises operate mission-critical systems that support the mission-critical systems  with 24/7/365 uptime requirements. Systems like core processing system (Legacy Core Processing), traffic management system (Enterprise Traffic Management), data exchange (Enterprise Data Exchange), and notification (Enterprise Notifications) directly impact operational safety and enterprise operations. Downtime or degraded performance in these systems can cascade into service disruptions, capacity reductions, and in worst-case scenarios, safety events. Incident response must be rapid, thorough, and fully auditable to meet enterprise policy (Enterprise Maintenance Policy) and DOT Order 1351.37 (Departmental Cybersecurity Policy).

This skill integrates with the escalation policy defined in GUARDRAILS.md. Critical and High severity incidents automatically trigger the escalation process in parallel with automated investigation, ensuring human oversight is engaged immediately for safety-impacting events.

## What's Needed From User

- **Alert source**: The monitoring platform that triggered the incident (Sentry issue URL, Datadog alert ID, PagerDuty incident ID, or a manual description of the observed anomaly).
- **Affected system**: The enterprise application or service experiencing the incident (e.g., core processing system, traffic management system, data exchange, notification, enterprise services).
- **Environment**: Which environment is affected (production, staging, disaster recovery, COOP site).
- **Observed symptoms**: Description of the user-visible or system-visible symptoms (error messages, degraded response times, data inconsistencies, service unavailability).
- **Impact assessment** (optional): Known impact on operations -- number of users affected, services impacted, service regions affected, or downstream systems experiencing degradation.
- **Timeline** (optional): When the issue was first observed, any recent deployments or configuration changes that may correlate.
- **Repository URL**: The Git repository containing the source code for the affected system, if not already indexed in DeepWiki.
- **Access to logs** (optional): Log aggregation platform credentials or log file paths (Splunk, ELK, CloudWatch, or local log directories).
- **Runbook reference** (optional): Link to any existing operational runbook for the affected system.

## Procedure

1. **Receive and parse the alert**
   - Accept the incoming alert from Sentry webhook, Datadog webhook, PagerDuty event, Jira ticket, or manual user input.
   - Extract structured alert data:
     - Error type and message.
     - Stack trace or error trace (if available).
     - Affected endpoint, service, or component.
     - Timestamp of first occurrence and frequency.
     - Environment and deployment version.
     - Affected users or request volume.
   - Normalize the alert into a standard incident record format regardless of source platform.
   - Assign a unique incident ID and create the incident timeline log.

2. **Triage severity using enterprise mpact criteria**
   - Classify the incident severity using the following matrix:
     - **SEV-1 (Critical)**: enterprise system is down or degraded to the point of safety impact. Enterprise operations are directly affected. Examples: core system outage, data feed failure, notification distribution failure.
     - **SEV-2 (High)**: System is degraded but operational. Performance is below acceptable thresholds. Workarounds exist but are manual. Examples: 50%+ increase in response latency, partial data loss in non-safety systems, authentication failures affecting controller access.
     - **SEV-3 (Medium)**: Non-critical functionality is impaired. Core operations continue normally. Examples: reporting dashboard errors, batch job delays, non-critical API endpoint failures.
     - **SEV-4 (Low)**: Cosmetic or minor issues with no operational impact. Examples: logging format errors, non-user-facing warnings, development environment issues.
   - For SEV-1 and SEV-2 incidents, immediately trigger the escalation process per GUARDRAILS.md escalation policy (15-minute SLA for Critical, 1-hour SLA for High).
   - Record the severity classification with justification in the incident timeline.

3. **Query DeepWiki for affected codebase context**
   - Connect to the DeepWiki MCP server and retrieve the knowledge graph for the affected repository.
   - If the repository is not yet indexed, trigger indexing and wait for completion before proceeding.
   - Query DeepWiki for:
     - Architecture of the affected component or service.
     - Recent changes to the affected area (commits in the last 7 days).
     - Known dependencies and integration points.
     - Historical incidents in the same area (if tracked in DeepWiki).
     - Test coverage status for the affected code paths.
   - Retrieve the full file context for any files referenced in the error stack trace.
   - Map the error location to the broader system architecture to understand blast radius.

4. **Analyze error traces, logs, and metrics**
   - Parse the full stack trace from the alert to identify:
     - The exact line of code where the error originated.
     - The call chain leading to the error.
     - Any caught and re-thrown exceptions that may mask the root cause.
   - If log access is available, query the log aggregation platform for:
     - All log entries from the affected service within the incident time window (first occurrence minus 30 minutes to present).
     - Correlated logs from upstream and downstream services.
     - Any warning or error patterns that preceded the incident.
   - If metrics access is available (Datadog, Prometheus, CloudWatch), examine:
     - Request rate, error rate, and latency trends around the incident start time.
     - Resource utilization (CPU, memory, disk, network) for the affected hosts.
     - Queue depths, connection pool exhaustion, or thread pool saturation.
     - Database query latency and connection counts.
   - Build a timeline of events from the earliest anomaly signal to the current state.

5. **Identify root cause**
   - Cross-reference the error analysis with recent code changes:
     - Query Git history for commits to the affected files in the last 14 days.
     - Identify any deployments that occurred within 24 hours before the incident.
     - Check for configuration changes, feature flag toggles, or infrastructure modifications.
   - Classify the root cause into one of the following categories:
     - **Code defect**: Bug introduced in a recent change (null pointer, unhandled exception, logic error, race condition).
     - **Configuration error**: Misconfigured environment variable, connection string, timeout value, or feature flag.
     - **Infrastructure failure**: Host failure, network partition, disk full, certificate expiration, DNS resolution failure.
     - **Dependency failure**: External service outage, third-party API change, library incompatibility, database connection exhaustion.
     - **Data issue**: Corrupt data, schema mismatch, unexpected input format, data volume exceeding capacity.
     - **Capacity exhaustion**: Traffic spike exceeding auto-scaling limits, memory leak, connection pool exhaustion, thread starvation.
   - Document the root cause with supporting evidence (specific log entries, metrics, code diffs, or configuration changes).
   - If root cause cannot be determined with high confidence, document the top three hypotheses ranked by likelihood and the evidence for/against each.

6. **Generate SDD remediation specification**
   - Produce a Software Design Document specifying the remediation:
     - Root cause summary and evidence.
     - Proposed fix with detailed technical approach.
     - Files to be modified and the nature of each change.
     - Rollback plan if the fix introduces regressions.
     - Impact assessment of the fix on other components.
     - Performance implications of the fix.
   - For SEV-1 incidents, the SDD must also include:
     - Immediate mitigation steps (can the system be stabilized before the full fix is deployed?).
     - Interim workaround instructions for operations staff.
     - Communication plan for affected stakeholders.
   - The SDD is reviewed by Advanced Devin for architectural fit before proceeding to implementation.

7. **Generate TDD regression test cases**
   - Create test cases that:
     - Reproduce the exact failure condition that caused the incident (the "regression test").
     - Verify the fix resolves the issue under the failure condition.
     - Test boundary conditions around the root cause (e.g., if a null pointer, test all nullable inputs to the affected method).
     - Validate that the fix does not break existing functionality (guard tests for adjacent behavior).
     - Test the failure mode gracefully (e.g., if the root cause was an unhandled exception, verify the new handling produces correct error responses).
   - Tests must initially fail against the current (broken) code, confirming they accurately detect the defect.
   - Test framework selection matches the project's existing test infrastructure (JUnit, pytest, Jest, etc.).

8. **Spawn Devin to implement the fix**
   - Create a Devin session via the Devin API with:
     - The SDD remediation specification as the task description.
     - The TDD test cases as acceptance criteria.
     - The affected repository and branch information.
     - Any relevant DeepWiki context for the codebase.
   - Devin implements the fix according to the SDD specification.
   - Devin runs all existing tests plus the new regression tests.
   - Devin creates a pull request with:
     - Descriptive title referencing the incident ID.
     - PR body containing the root cause summary, fix description, and test results.
     - Labels indicating severity and incident-response origin.

9. **Invoke Devin Review on the fix PR**
   - Submit the PR to Devin Review via the `devin-review-mcp` server.
   - Devin Review evaluates:
     - Code quality and adherence to project conventions.
     - Security implications of the change (no new vulnerabilities introduced).
     - Test coverage adequacy (new tests cover the fix, overall coverage maintained).
     - Architectural consistency (fix does not introduce debt or anti-patterns).
   - Address all review findings before proceeding.
   - For SEV-1 incidents, expedited review with a 30-minute SLA is requested.

10. **Run guardrails validation**
    - Execute the full guardrails validation suite on the fix PR:
      - HG-001: All tests pass (including new regression tests).
      - HG-002: STIG scan clean (no new High findings).
      - HG-003: Lint/format pass.
      - HG-004: Coverage threshold met (80%+ on modified code).
      - HG-005: No secrets introduced.
      - HG-006: No new Critical/High CVE dependencies.
      - HG-007: Signed commits.
      - HG-008: Audit trail complete.
    - If any hard gate fails, fix the issue and re-validate (up to 3 retries per GUARDRAILS.md).
    - Record all guardrail results in the incident timeline.

11. **Generate post-incident report**
    - Produce a comprehensive post-incident report containing:
      - **Incident summary**: One-paragraph description of what happened, when, and impact.
      - **Timeline**: Chronological log of all events from first alert to resolution, with timestamps.
      - **Root cause analysis**: Detailed technical explanation with evidence.
      - **Impact assessment**: Systems affected, duration of impact, users affected, services impacted (if applicable).
      - **Resolution**: What was fixed and how, with links to the remediation PR.
      - **Detection assessment**: How quickly was the incident detected? Could detection be improved?
      - **Response assessment**: How quickly was the incident triaged and fixed? Where were delays?
      - **Preventive measures**: Specific actions to prevent recurrence:
        - Additional monitoring or alerting rules.
        - Code improvements beyond the immediate fix.
        - Process improvements.
        - Additional test coverage.
      - **Lessons learned**: What worked well, what could be improved.
    - Store the post-incident report in the repository under `docs/incidents/{incident-id}-postmortem-{YYYY-MM-DD}.md`.
    - Update DeepWiki with the incident context and resolution for future reference.
    - If the incident revealed a gap in monitoring, create a follow-up task to implement additional alerting.

## Specifications

- **Alert ingestion**: The skill must support Sentry webhook payloads (v2 format), Datadog webhook payloads (v2 format), PagerDuty Events API v2, Jira issue webhooks, and free-text manual input. Unknown alert formats must be parseable on a best-effort basis.
- **Severity SLAs**: SEV-1 incidents must have automated investigation initiated within 5 minutes of alert receipt. SEV-2 within 15 minutes. SEV-3 and SEV-4 within 1 hour.
- **Root cause confidence**: Root cause analysis must include a confidence level (High: >80% certainty, Medium: 50-80%, Low: <50%). If confidence is Low, the incident must be escalated to a human engineer with all findings.
- **Post-incident report format**: Reports must follow the template in `docs/templates/incident-postmortem-template.md` and be stored under `docs/incidents/`. Naming convention: `{incident-id}-postmortem-{YYYY-MM-DD}.md`.
- **Audit trail**: Every action taken during incident investigation must be logged with timestamp, action description, data sources queried, and findings. The audit trail is attached to the remediation PR and the post-incident report.
- **enterprise compliance**: All incident response activities must comply with DOT Order 1351.37 (Departmental Cybersecurity Policy), enterprise policy (enterprise Information Security and Privacy Program), and NIST SP 800-61 (Computer Security Incident Handling Guide).
- **Evidence preservation**: All logs, metrics snapshots, and configuration states captured during investigation must be preserved as artifacts attached to the incident record. These artifacts have a retention period of 3 years per FAR 4.703.
- **Classification**: Incident reports and investigation artifacts must be marked UNCLASSIFIED // FOR OFFICIAL USE ONLY (U//FOUO) unless otherwise directed.
- **Communication**: For SEV-1 and SEV-2 incidents, status updates must be posted to the configured escalation channel (Slack/Teams) at 15-minute intervals until resolution.
- **Rollback threshold**: If the fix cannot pass all guardrails within 3 attempts, the skill must recommend rollback to the last known good deployment and escalate to a human engineer.

## Advice and Pointers

- Start with the stack trace. A good stack trace tells you 80% of the story. Parse it before querying logs or metrics.
- Correlation is not causation in incident analysis. A recent deployment may correlate with the incident timeline but may not be the actual cause. Always verify by examining the specific code changes.
- For enterprise enterprise systems, check the notification system first when investigating data-related incidents. Many enterprise data feeds depend on notification data, and notification distribution issues cascade broadly.
- Database connection pool exhaustion is the single most common root cause in enterprise Java/Spring applications. Check HikariCP or c3p0 pool metrics early in the investigation.
- When investigating intermittent failures, look for race conditions in multi-threaded code and timing-dependent operations in distributed systems. enterprise systems frequently use IBM MQ and TIBCO, which have subtle timing behaviors.
- Certificate expiration is a recurring theme in government systems due to long deployment cycles and manual certificate management. Check certificate validity dates early for any TLS-related errors.
- Always check if the affected system has a runbook in Confluence before starting investigation. Existing runbooks may document known failure modes and recovery procedures.
- For Sentry alerts, pay attention to the "first seen" vs. "last seen" timestamps. An error that was first seen weeks ago but is now alerting may indicate a threshold breach rather than a new defect.
- Do not underestimate configuration drift. In enterprise environments with multiple deployment stages (dev, test, staging, production, DR), configuration differences between environments are a frequent source of production-only failures.
- When the root cause involves a third-party dependency, document the dependency version, the known issue, and the upgrade path. Many enterprise systems run on older dependency versions due to change control processes.


## Self-Verification Loop (Devin 2.2)

After completing the primary procedure:

1. **Self-verify**: Run all applicable verification gates:
   - Build/test gates: remediation code compilation, regression tests pass, existing tests unbroken
   - Security gates: remediation does not introduce new vulnerabilities, secrets scan on fix
   - Operational gates: rollback procedure documented and tested
2. **Auto-fix**: If any verification gate fails, attempt automated repair — adjust code, configuration, or test fixtures to resolve the failure.
3. **Re-verify**: Run all verification gates again after fixes. Confirm each gate transitions from FAIL to PASS.
4. **Escalate**: If auto-fix fails after 2 attempts, escalate to human reviewer with a complete evidence pack. Include the failing gate identifier, error output, attempted fixes, and root cause hypothesis.

## Artifact Contract

Every stage of this skill produces paired outputs for machine-consumable handoff:

| Stage | Markdown Output | JSON Output |
|-------|----------------|-------------|
| Alert Triage | `alert_triage.md` | `alert_triage.json` |
| Root Cause Analysis | `root_cause.md` | `root_cause.json` |
| Remediation PR | `remediation_pr.md` | `remediation_pr.json` |
| Post-Incident Report | `post_incident.md` | `post_incident.json` |

JSON outputs must conform to the schema defined in `audit/artifact-schemas/`. Markdown outputs are the human-readable narrative; JSON outputs are the machine-consumable contract consumed by the next stage or by OpenClaw for artifact validation.

## Evidence Pack

On completion, produce `evidence-pack.json` containing:

```json
{
  "session_id": "<Devin session identifier>",
  "timestamp": "<ISO 8601 completion time>",
  "skill_id": "devinclaw.incident_response.v1",
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
- **Human approval required for**: production deployment of fix, SEV-1/SEV-2 incident closure, root cause classification for safety-critical systems, infrastructure-level remediations.
- **Auto-escalate on**: Any security finding rated HIGH or CRITICAL, any risk of data loss or corruption, any changes to authentication or authorization logic, any modification to safety-critical code paths (DO-178C applicable systems).

## Forbidden Actions

- Do not deploy fixes directly to production. All fixes must go through the PR pipeline with full guardrails validation, regardless of incident severity. Emergency deployments require human approval through the escalation process.
- Do not modify production configuration or infrastructure during automated investigation. Investigation must be read-only against production systems. Only the remediation PR (after review and guardrails) may introduce changes.
- Do not access or store credentials discovered during log analysis. If credentials are found in logs, flag this as a separate security incident and redact the values in all reports.
- Do not skip the severity triage step. Every incident must be classified before investigation proceeds, as severity determines escalation requirements and response SLAs.
- Do not generate a post-incident report without completing root cause analysis. Partial reports with "root cause unknown" are acceptable only when explicitly noted with a follow-up investigation plan and timeline.
- Do not close an incident without regression tests. Every incident must produce at least one automated test that would detect the same failure if it recurred.
- Do not suppress or downgrade alert severity to avoid escalation. If a SEV-1 or SEV-2 classification is warranted by the impact criteria, escalation must proceed.
- Do not include Personally Identifiable Information (PII), Sensitive Security Information (SSI), or classified operational data in post-incident reports. Anonymize all user identifiers, transaction IDs, and system-specific details unless the report is appropriately classified.
- Do not attempt to fix infrastructure issues (host failures, network partitions, disk full) through code changes. These require infrastructure team intervention and should be escalated, not worked around in application code.
- Do not investigate incidents in systems where DeepWiki indexing has not completed. Without codebase context, root cause analysis confidence is insufficient. Wait for indexing or fall back to manual investigation with explicit reduced-confidence notation.
