# DevinClaw Guardrails

Guardrails are the non-negotiable constraints that govern every DevinClaw session. No code merges, no artifact ships, no session closes without passing every applicable gate.

---

## Hard Gates

Hard gates are binary pass/fail checks. If any hard gate fails, the session cannot produce a deliverable. There are no overrides for hard gates; the code must be fixed until the gate passes.

| Gate ID | Gate Name | Check | Failure Action |
|---------|-----------|-------|----------------|
| HG-001 | **Tests Pass** | All unit, integration, and e2e tests execute and pass | Block PR; fix failing tests |
| HG-002 | **STIG Scan Clean** | Zero High findings from DISA STIG scanner | Block PR; remediate all High findings |
| HG-003 | **Lint/Format Pass** | Language-appropriate linter and formatter report zero errors | Block PR; auto-fix or manual fix |
| HG-004 | **Coverage Threshold** | Code coverage >= 80% for new/modified code | Block PR; write additional tests |
| HG-005 | **No Secrets** | Secret scanner (TruffleHog/GitLeaks) reports zero findings | Block PR; remove secrets, rotate if leaked |
| HG-006 | **Dependency Scan** | No Critical/High CVEs in new/updated dependencies | Block PR; upgrade or mitigate dependencies |
| HG-007 | **Signed Commits** | All commits in the branch are GPG-signed | Block PR; re-sign commits |
| HG-008 | **Audit Trail Complete** | Session audit log contains all required events | Block PR; regenerate audit artifacts |
| HG-009 | **License Compliance** | No GPL/AGPL dependencies introduced in Apache-licensed modules | Block PR; replace dependency |
| HG-010 | **NIST Controls Met** | All applicable NIST 800-53 controls validated | Block PR; implement missing controls |

---

## SDLC Completion Checklist

Every DevinClaw session must produce the following artifacts before marking a task complete. OpenClaw validates this checklist automatically.

### Phase 1: Specification
- [ ] Task parsed and intent confirmed with user (or auto-confirmed for batch)
- [ ] Skill selected and loaded (or new skill scaffolded)
- [ ] DeepWiki context retrieved for target codebase
- [ ] Structured specification document generated
- [ ] Specification reviewed by Advanced Devin for architectural fit
- [ ] Acceptance criteria defined as testable assertions

### Phase 2: Test First
- [ ] Failing tests written per acceptance criteria
- [ ] Test framework configured for target language/platform
- [ ] Tests execute and fail for the right reasons (not setup errors)
- [ ] Test coverage baseline captured

### Phase 3: Implementation
- [ ] Solution implemented per specification
- [ ] All pre-existing tests still pass (no regressions)
- [ ] New tests now pass
- [ ] Code follows project style conventions (auto-formatted)

### Phase 4: Review
- [ ] Devin Review auto-review completed
- [ ] STIG scanner executed with zero High findings
- [ ] Secret scanner executed with zero findings
- [ ] Dependency scanner executed with no Critical/High CVEs
- [ ] Advanced Devin deep analysis completed
- [ ] Review findings addressed or documented as accepted risk

### Phase 5: Delivery
- [ ] PR/MR created with descriptive title and body
- [ ] Audit trail attached to PR as comment or artifact
- [ ] Test results attached (JUnit XML or equivalent)
- [ ] STIG scan results attached (XCCDF format)
- [ ] Coverage report attached
- [ ] DeepWiki updated with session learnings
- [ ] Session archived in OpenClaw ledger

---

## Session Limits

These limits prevent runaway sessions from consuming resources or producing sprawling, unreviewable changes.

| Limit | Value | Rationale |
|-------|-------|-----------|
| **Max session duration** | 4 hours | Prevents stale context and resource hoarding |
| **Max files modified per session** | 50 | Keeps PRs reviewable by humans |
| **Max lines changed per session** | 5,000 | Ensures changes are digestible and auditable |
| **Max parallel sessions per user** | 10 | Prevents resource exhaustion on shared infrastructure |
| **Max parallel sessions per org** | 100 | Platform-level capacity management |
| **Max retries per hard gate** | 3 | Prevents infinite fix loops; escalates after 3 failures |
| **Max skill creation per session** | 1 | New skills require focused attention and validation |
| **Session idle timeout** | 30 minutes | Reclaims resources from abandoned sessions |
| **Max dependency additions** | 10 | Prevents dependency bloat; requires justification above 10 |
| **Max cost per session** | $50 (configurable) | Budget guardrail for compute-intensive tasks |

When a session approaches a limit (80% threshold), OpenClaw issues a warning to the user and begins preparing session artifacts for graceful handoff.

---

## Escalation Policy

When DevinClaw cannot resolve an issue autonomously, it escalates to a human operator. Escalation is not failure; it is a governance feature.

### Escalation Triggers

| Trigger | Severity | Escalation Target |
|---------|----------|-------------------|
| Hard gate fails 3 consecutive times | High | Assigned engineer + tech lead |
| STIG High finding cannot be auto-remediated | High | Security team + ISSO |
| Session duration exceeds 4 hours | Medium | Assigned engineer |
| Files modified exceeds 50 | Medium | Assigned engineer + tech lead |
| Secret detected in codebase (pre-existing) | Critical | Security team + ISSO + PM |
| Architectural decision required (new service, new dependency) | Medium | Tech lead + architect |
| Skill not found for requested task | Low | Assigned engineer |
| Devin API rate limit or availability issue | Medium | Platform team |
| Cost threshold exceeded | Medium | PM + assigned engineer |
| Classified data handling required | Critical | Security team + ISSO + FSO |

### Escalation Process

1. **Detection**: OpenClaw detects the escalation trigger automatically
2. **Notification**: Alert sent via configured channel (Slack, Teams, email, or GitLab issue)
3. **Context Package**: OpenClaw generates a context package containing:
   - Session ID and full audit trail
   - Current task specification
   - Work completed so far (diff, test results)
   - Specific blocker description
   - Recommended next steps
4. **Handoff**: Session is paused (not terminated) pending human input
5. **Resolution**: Human provides guidance; session resumes or is reassigned
6. **Learning**: Resolution is captured in DeepWiki for future sessions

### Escalation SLAs

| Severity | Initial Response | Resolution Target |
|----------|-----------------|-------------------|
| Critical | 15 minutes | 2 hours |
| High | 1 hour | 8 hours |
| Medium | 4 hours | 24 hours |
| Low | 24 hours | 72 hours |

---

## Verification Integration

Guardrails integrate with the DevinClaw verification system to provide layered assurance:

### Self-Verification Loop
Every skill execution includes a self-verification loop that runs applicable hard gates automatically:
1. **Verify**: Run all hard gates applicable to the skill's output.
2. **Auto-fix**: If a gate fails, attempt automated repair (up to 2 attempts).
3. **Re-verify**: Confirm the gate transitions from FAIL to PASS.
4. **Escalate**: If auto-fix fails after 2 attempts, escalate with evidence pack.

The self-verification loop runs *before* the PR is created — failures are caught at the skill level, not at the merge gate.

### Arena Verification
For high-risk and critical-risk skills, guardrails are enforced independently across all arena sessions. A hard gate failure in any arena session blocks the merged output, even if other sessions passed. This prevents the "majority rules" failure mode where a flawed session's output contaminates the merge.

Arena configuration is defined in `audit/arena-config.json`. Risk classification per skill determines whether arena verification is mandatory.

### Evidence Pack Validation
OpenClaw rejects any task marked "done" if:
- The evidence pack is missing or malformed (does not conform to `audit/artifact-schemas/evidence-pack.schema.json`).
- Any artifact hash in the evidence pack does not match the actual file hash.
- Required artifacts for the completed stages are absent.
- Verification gate results show any FAIL without a corresponding escalation record.

### Constitution Stage Gates
The SDLC constitution (`audit/constitution-template.json`) defines required inputs and outputs at each stage boundary. OpenClaw validates stage transitions — a task cannot advance from "build" to "review" unless all build-stage required outputs are present and all build-stage gate criteria are met.

---

## Guardrail Configuration

Guardrails are configured in `config/guardrails.yaml`. Organizations can customize thresholds while maintaining minimum baselines.

```yaml
guardrails:
  hard_gates:
    tests_pass: true                    # Cannot be disabled
    stig_scan_clean: true               # Cannot be disabled
    lint_format_pass: true              # Can be set to warn-only in dev
    coverage_threshold: 80              # Minimum: 60, Default: 80
    no_secrets: true                    # Cannot be disabled
    dependency_scan: true               # Cannot be disabled
    signed_commits: true                # Can be disabled for dev environments
    audit_trail_complete: true          # Cannot be disabled
    license_compliance: true            # Cannot be disabled
    nist_controls_met: true             # Cannot be disabled for prod

  session_limits:
    max_duration_hours: 4               # Range: 1-8
    max_files_modified: 50              # Range: 10-100
    max_lines_changed: 5000             # Range: 1000-10000
    max_parallel_user: 10               # Range: 1-25
    max_parallel_org: 100               # Range: 10-500
    max_retries: 3                      # Range: 1-5
    idle_timeout_minutes: 30            # Range: 10-60
    max_cost_usd: 50                    # Range: 10-500

  escalation:
    channels:
      - type: slack
        webhook: ${SLACK_WEBHOOK_URL}
      - type: gitlab_issue
        project: ${GITLAB_PROJECT_ID}
    sla:
      critical_response_minutes: 15
      high_response_minutes: 60
      medium_response_minutes: 240
      low_response_minutes: 1440
```

---

## Guardrail Bypass Policy

There is no bypass mechanism for hard gates in production environments. In development and staging environments, the following controlled exceptions are available:

| Exception | Allowed In | Approval Required | Expires |
|-----------|-----------|-------------------|---------|
| Reduce coverage threshold to 60% | Dev only | Tech lead | Per-session |
| Disable signed commits | Dev only | None | Per-environment |
| Set lint to warn-only | Dev, Staging | Tech lead | Per-sprint |
| Extend session duration to 8 hours | All | PM + Tech lead | Per-session |
| Increase file limit to 100 | All | Tech lead | Per-session |

All bypass requests are logged in the audit trail with requestor, approver, justification, and expiration timestamp.
