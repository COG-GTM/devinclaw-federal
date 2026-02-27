# Playbook: Parallel Migration (100+ Sessions)

> **Required Knowledge:** `enterprise-modernizer`, `oracle-migrator`

## Overview
Execute large-scale migrations by spawning 100+ parallel Devin sessions, each handling an independent migration unit. Uses Advanced Devin batch session capability.

## When to Use
- Migrating 50+ database packages, files, or modules simultaneously
- REST-to-GraphQL migration across hundreds of endpoints
- Adding test coverage to a large untested codebase
- Any task that can be decomposed into independent, parallelizable units

## Instructions

1. **Decompose the task** into independent work units:
   - Each unit must be self-contained (no cross-unit dependencies during execution)
   - Group by dependency order: process leaf nodes first
   - Create a manifest file listing all units with metadata

2. **Prepare the batch specification**:
   - For each unit: task description, input files, expected outputs, test criteria
   - Select the appropriate Devin playbook for all sessions
   - Define the shared context (DeepWiki knowledge, project conventions)

3. **Spawn batch sessions via Advanced Devin**:
   - Navigate to Advanced Mode → Start Batch Sessions
   - Select the playbook
   - Upload the manifest or describe the decomposition
   - Review proposed sessions before approval
   - Limit: 10-50 concurrent sessions per batch (avoid resource contention)

4. **Monitor session progress**:
   - Use Devin API `GET /v3/organizations/sessions` to poll status
   - Track: running, completed, failed, blocked
   - For failed sessions: analyze error, fix, re-spawn

5. **Collect and validate results**:
   - Gather all PRs created by parallel sessions
   - Run cross-unit integration tests (dependencies between migrated units)
   - Validate no conflicts between parallel PRs (merge conflicts, shared file edits)

6. **Merge in dependency order**:
   - Merge leaf-node PRs first
   - Run integration tests after each merge batch
   - Continue up the dependency tree

7. **Run Advanced Devin analysis**:
   - Analyze all sessions for patterns: which succeeded, which failed, why
   - Generate improved playbook based on learnings
   - Update knowledge base with migration patterns discovered

## Specifications
- Maximum concurrent sessions: 50 (configurable)
- Each session must be fully independent during execution
- Shared resources (databases, APIs) must handle concurrent access
- Session timeout: 4 hours per unit
- Failed sessions are retried once automatically, then flagged for human review

## Advice
- Split by file/module boundaries for cleanest parallelization
- If two units touch the same file, they CANNOT run in parallel — sequence them
- Monitor resource usage: 100 sessions hitting the same database will cause contention
- Use Advanced Devin's "Analyze sessions" after completion to extract patterns and improve the playbook for next time
- The first batch of 10 is a calibration run — tune the playbook before scaling to 100+


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
