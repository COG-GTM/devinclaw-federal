# sdlc-validator

## Overview
Validate that a task or session has completed the full SDLC loop as required by DevinClaw guardrails. Use this skill when verifying that modernization tasks have produced all required artifacts, when auditing session compliance before merge, or when generating SDLC completion certificates for federal audit trails.

## When to Use
This skill validates that a DevinClaw task or session has completed every phase of the Software Development Lifecycle as defined in the DevinClaw guardrails and SDLC completion checklist. It systematically verifies the presence and quality of every required artifact -- from the initial SDD specification through TDD test plans, implementation, Devin Review completion, guardrail gate passage, and knowledge base updates -- and produces a formal SDLC compliance report suitable for federal audit trails.

This is an internal OpenClaw governance skill. It does not produce application code or modify repositories. Instead, it acts as the final quality gate that confirms a session has followed the complete DevinClaw SDLC loop before artifacts are accepted, PRs are approved for merge, and sessions are marked complete in the OpenClaw ledger. In federal modernization contexts, this skill generates the compliance certificates that auditors, ISSOs, and program managers rely on to verify that AI-assisted development followed all required processes.

The enterprise nd other federal agencies operate under strict FISMA, FedRAMP, and NIST 800-53 requirements that mandate documented, repeatable, and auditable development processes. Every modernization task executed by DevinClaw must produce evidence that the full SDLC was followed. This skill automates the verification of that evidence, replacing manual checklists with deterministic, reproducible validation that can be run at any time against any session.

## Instructions
1. **Receive and resolve the task or session identifier**
   - Accept the task ID or session ID from the user or from an automated trigger (e.g., pre-merge hook, scheduled audit).
   - Query the OpenClaw Internal API (`GET /tasks/{id}`) to retrieve the full task record, including associated Devin session IDs, skill used, timestamps, and current status.
   - If a session ID is provided instead of a task ID, resolve it to the parent task via `GET /sessions/{id}`.
   - If a batch pattern is provided, enumerate all matching tasks and queue them for sequential validation.
   - Validate that the task exists and is in a terminal state (completed, failed, or cancelled). If the task is still in progress, report its current phase and defer validation.

2. **Check for SDD specification artifact**
   - Query the task's artifact list via `GET /tasks/{id}/artifacts` or inspect the session directory for specification documents.
   - Verify that a Software Design Document (SDD) exists with the correct naming convention: `{task-id}-sdd-spec.md` or equivalent.
   - Validate that the SDD contains all required sections: purpose, scope, acceptance criteria, architectural approach, input/output definitions, and security considerations.
   - Verify that the SDD was reviewed by Advanced Devin for architectural fit (check for the review timestamp and approval marker in the document metadata or audit log).
   - Record the SDD validation result: PASS (present and complete), PARTIAL (present but missing sections), or FAIL (absent).

3. **Check for TDD test plan and test artifacts**
   - Verify that a test plan document exists corresponding to the SDD specification.
   - Confirm that test cases were written before implementation by comparing timestamps: test file creation timestamps must precede implementation file creation timestamps.
   - Validate that test cases cover all acceptance criteria defined in the SDD.
   - Check that the test framework is appropriate for the target language and platform.
   - Verify that tests were initially in a failing state (test-first methodology) by checking the test execution history in the audit log for an initial red-phase run.
   - Record the TDD validation result: PASS, PARTIAL (tests exist but not test-first), or FAIL (no tests).

4. **Check for implementation artifacts**
   - Verify that implementation code exists in the session's working branch or PR.
   - Confirm that the implementation addresses all requirements in the SDD specification.
   - Check that pre-existing tests still pass (no regressions introduced) by examining the test execution results.
   - Verify that the implementation follows project style conventions by checking lint and format results.
   - Record the implementation validation result: PASS, PARTIAL, or FAIL.

5. **Check test results: pass/fail status and coverage threshold**
   - Retrieve the final test execution results from the session artifacts (JUnit XML, pytest results, Jest output, or equivalent).
   - Verify that all tests pass with zero failures and zero errors.
   - Retrieve the code coverage report and verify that coverage for new and modified code meets or exceeds the configured threshold (default: 80%, per Hard Gate HG-004).
   - If coverage is below threshold, calculate the gap and identify which files or methods lack coverage.
   - Cross-reference the coverage report with the SDD to ensure critical business logic paths are covered.
   - Record the test results validation: PASS (all green, coverage >= 80%), PARTIAL (tests pass but coverage below threshold), or FAIL (test failures exist).

6. **Check PR creation and completeness**
   - Verify that a Pull Request or Merge Request was created for the task via the GitLab MCP or Git MCP.
   - Validate that the PR includes: descriptive title, body with change summary, linked task/issue ID, test results attachment, STIG scan results attachment, coverage report attachment, and audit trail attachment.
   - Check that all commits in the PR branch are GPG-signed (Hard Gate HG-007).
   - Verify that the PR has not exceeded session limits (max 50 files modified, max 5,000 lines changed).
   - Record the PR validation result: PASS, PARTIAL (PR exists but missing attachments), or FAIL (no PR created).

7. **Check Devin Review completion: zero bugs remaining**
   - Query the Devin Review API (`GET /reviews/{id}`) for the review associated with this task's PR.
   - Verify that Devin Review was triggered and completed (status: completed).
   - Check the review findings: confirm that all findings have been addressed (status: resolved or accepted_risk).
   - Verify that zero open bug findings remain. Accepted-risk findings must have documented justification.
   - Check that Advanced Devin deep analysis was also completed and its findings addressed.
   - Record the review validation result: PASS (review complete, zero open bugs), PARTIAL (review complete but open findings remain), or FAIL (review not performed).

8. **Check Guardrails API: zero violations**
   - Query the OpenClaw Guardrails API (`GET /tasks/{id}/guardrails`) to retrieve the guardrail evaluation results.
   - Verify that all Hard Gates passed:
     - HG-001: Tests Pass
     - HG-002: STIG Scan Clean (zero High findings)
     - HG-003: Lint/Format Pass
     - HG-004: Coverage Threshold (>= 80%)
     - HG-005: No Secrets (zero findings from TruffleHog/GitLeaks)
     - HG-006: Dependency Scan (no Critical/High CVEs)
     - HG-007: Signed Commits
     - HG-008: Audit Trail Complete
     - HG-009: License Compliance
     - HG-010: NIST Controls Met
   - For any failed gate, record the specific failure details (which gate, what finding, when it failed).
   - Check if any gates were retried and how many attempts were needed (max 3 retries per Hard Gate).
   - Record the guardrails validation result: PASS (all gates green), or FAIL (one or more gate failures).

9. **Check knowledge base update**
   - Verify that the DeepWiki knowledge base was updated with session learnings by querying the DeepWiki MCP server or checking the audit log for a DeepWiki update event.
   - Confirm that the session was archived in the OpenClaw ledger (`POST /audit/{session_id}`).
   - Verify that any architectural decisions made during the session were recorded.
   - Check that the session's outcomes (patterns discovered, issues encountered, solutions applied) were captured for future sessions.
   - Record the knowledge base validation result: PASS (DeepWiki updated and session archived), PARTIAL (session archived but DeepWiki not updated), or FAIL (neither completed).

10. **Generate SDLC compliance report**
    - Compile all validation results into a structured compliance report with the following sections:
      - **Header**: Task ID, Session ID, Skill used, Operator, Timestamps (start, end, validation time).
      - **Executive Summary**: Overall PASS/FAIL determination with counts of passed, partial, and failed checks.
      - **Phase-by-Phase Results**: Detailed results for each SDLC phase (Specification, Test First, Implementation, Review, Delivery) with evidence references.
      - **Hard Gate Results**: Individual pass/fail for each of the 10 Hard Gates with scan artifact references.
      - **Compliance Framework Mapping**: For each applicable framework (NIST 800-53, DISA STIG, FedRAMP), map the session's evidence to specific controls.
      - **Findings and Gaps**: Any missing artifacts, failed gates, or process deviations with severity classification.
      - **Remediation Recommendations**: For each finding, a specific remediation action and the skill or command to execute it.
    - Store the report in the session directory and attach it to the PR as a comment or artifact.

11. **Flag missing artifacts for remediation**
    - For each PARTIAL or FAIL result, generate a specific remediation ticket:
      - Identify the exact artifact that is missing or deficient.
      - Determine the skill, tool, or action needed to produce the missing artifact.
      - If remediation mode is enabled, automatically trigger the remediation action (e.g., re-run STIG scan, regenerate coverage report, trigger DeepWiki update).
      - If remediation mode is disabled, create an actionable remediation item in the compliance report with step-by-step instructions.
    - Escalate any findings that cannot be automatically remediated per the DevinClaw Escalation Policy (e.g., STIG High finding that requires architectural change).

12. **Generate SDLC completion certificate (if requested)**
    - If all checks pass (overall PASS), generate a formal SDLC completion certificate containing:
      - Certificate ID (unique, sequential).
      - Task ID and Session ID.
      - Date and time of validation.
      - Summary of all checks performed and their results.
      - Hash of the PR branch HEAD commit.
      - Hash of the compliance report.
      - Digital signature using the session's GPG key.
    - Store the certificate in the session directory and attach it to the PR.
    - If the overall result is not PASS, do not generate a certificate. Instead, generate a non-compliance notice detailing what must be resolved before a certificate can be issued.

## Specifications
- **API dependencies**: This skill requires access to the OpenClaw Internal API (`/tasks`, `/sessions`, `/audit`), the Devin Review API (`/reviews`), the Guardrails API (`/tasks/{id}/guardrails`), the DeepWiki MCP server, and the GitLab MCP or Git MCP server.
- **Report format**: Compliance reports must be generated as Markdown stored in the session directory under `audit/` with the naming convention `{task-id}-sdlc-compliance-report-{YYYY-MM-DD}.md`. JSON reports use the same naming with a `.json` extension.
- **Certificate format**: SDLC completion certificates must be generated as Markdown with an embedded digital signature block at the bottom. The signature is a GPG detached signature of the certificate content hash (SHA-256).
- **Validation granularity**: Each SDLC phase check must produce one of three results: PASS (fully compliant), PARTIAL (partially compliant with specific gaps identified), or FAIL (non-compliant). The overall result is PASS only if all individual checks are PASS.
- **Timestamp verification**: Test-first methodology is verified by comparing file creation timestamps in the Git history. The first test commit must precede the first implementation commit on the session branch.
- **Hard Gate mapping**: All 10 Hard Gates from GUARDRAILS.md must be individually validated. The skill must not skip any gate, even if the task type makes a gate seem inapplicable (e.g., dependency scan for a documentation-only change).
- **Batch validation**: When validating multiple sessions, each session receives its own compliance report. A batch summary report is also generated listing all sessions with their overall PASS/FAIL status.
- **Idempotency**: Running validation multiple times against the same session must produce identical results unless the session's artifacts have changed between runs.
- **Classification**: All compliance reports and certificates must be marked UNCLASSIFIED // FOR OFFICIAL USE ONLY (U//FOUO) unless otherwise directed.
- **Retention**: Compliance reports and certificates must be retained for the duration of the contract plus 3 years per FAR 4.703, and additionally per NIST 800-53 AU-11 (Audit Record Retention).
- **Performance**: Validation of a single session must complete within 60 seconds. Batch validation must process at least 50 sessions per hour.

## Advice
- Run this skill as a pre-merge hook on every PR to catch compliance gaps before they enter the main branch. Automated validation is far more reliable than manual checklist review.
- When validating older sessions (more than 30 days old), some API endpoints may return stale or archived data. Use the archived session artifacts in the OpenClaw ledger as the authoritative source.
- The most common SDLC gap is missing DeepWiki knowledge base updates. Engineers frequently complete the build-and-review cycle but forget to trigger the learning phase. Configure OpenClaw to auto-trigger DeepWiki updates at session close.
- Coverage threshold failures are the second most common gap. When coverage falls between 75% and 80%, it is often faster to write a few additional tests than to request a threshold exception.
- For batch validation of large migration campaigns (100+ sessions), run validation in parallel batches of 10 to avoid overwhelming the OpenClaw API. Use the batch summary report to quickly identify outlier sessions that need attention.
- Test-first timestamp verification can produce false negatives if a developer amended commits or rebased during the session. In these cases, check the session audit log for the original commit sequence rather than the final Git history.
- Devin Review findings classified as accepted_risk must have a documented justification that references a specific NIST control or STIG finding ID. Generic justifications like "low impact" are insufficient for federal audit.
- When generating certificates for ATO packages, include the certificate in the System Security Plan (SSP) evidence appendix. ATO assessors expect to see reproducible evidence of process compliance.
- Session limits (50 files, 5,000 lines) occasionally force large tasks to be split across multiple sessions. When validating a multi-session task, validate each session individually and then produce a rollup report that confirms the combined deliverable is complete.

## Forbidden Actions
- Do not modify any session artifacts during validation. This skill is strictly read-only with respect to task outputs, code, test results, and audit logs. Validation must not alter the evidence it is evaluating.
- Do not generate a PASS result if any Hard Gate has failed. There are no overrides for Hard Gates in production environments. If a gate failed and was subsequently retried and passed, that is acceptable -- but the final state must be PASS.
- Do not generate an SDLC completion certificate for a session with any FAIL results. Certificates may only be issued for sessions that achieve an overall PASS across all validation checks.
- Do not skip validation of any Hard Gate, even if the gate appears inapplicable to the task type. All 10 gates must be explicitly checked and their result recorded. If a gate is truly not applicable (e.g., no dependencies were added), the gate should still be checked and recorded as PASS (no findings because no applicable changes).
- Do not accept Devin Review findings that are in an "open" state as compliant. All findings must be in "resolved" or "accepted_risk" status. Findings left in "open" or "in_progress" status indicate incomplete review remediation.
- Do not backdate or modify timestamps in compliance reports or certificates. All timestamps must reflect the actual time of validation.
- Do not store credentials, connection strings, secrets, or PII in compliance reports. If session artifacts contain secrets (which itself is a Hard Gate failure), reference the finding by ID without reproducing the secret value.
- Do not run remediation actions in remediation mode without explicit user confirmation if the remediation would modify production artifacts. Remediation mode is intended for re-running scans and regenerating reports, not for modifying application code.
- Do not validate sessions belonging to a different organization or security boundary without explicit cross-boundary authorization.

---
*Generated by DevinClaw Skills Parser at 2026-02-25T06:27:28Z*
*Source: skills/sdlc-validator/SKILL.md*
