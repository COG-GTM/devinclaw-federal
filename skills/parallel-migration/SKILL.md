---
name: parallel-migration
description: Execute batch migrations across 50-100+ files simultaneously using Advanced Devin parallel session management. Use this skill when performing large-scale file migrations, framework upgrades across many modules, or batch transformations where the same pattern applies to many files in enterprise application portfolios.
---

# Parallel Batch Migration

## Overview

This skill executes large-scale file migrations across 50-100+ files simultaneously by leveraging the Advanced Devin parallel session management capabilities. It accepts a migration manifest defining the files to transform and the transformation rules to apply, validates the manifest, generates specifications and test plans, then orchestrates parallel Devin sessions to execute the migration at scale. Each session is independently monitored, results are aggregated, and a comprehensive status report is produced.

The enterprise application portfolio spans 200+ applications across all business units, many of which require systematic modernization. Common batch migration scenarios include: upgrading framework versions across hundreds of modules (e.g., Spring Boot 2.x to 3.x across 80 microservices), converting build systems (Ant to Maven/Gradle across 60 modules), migrating configuration formats (XML to YAML across 100+ config files), applying security patches across all instances of a library, converting Java EE to Jakarta EE namespace changes, and standardizing code patterns across legacy applications. These migrations follow repeatable patterns that apply to many files -- the ideal workload for parallel automated execution.

This skill relies on the `devin-cloud-mcp` server for spawning and managing up to 100+ concurrent Devin sessions, the `devin-api-mcp` server for programmatic task submission and status polling, and the `devin-review-mcp` server for batch code review of resulting pull requests.

## What's Needed From User

- **Migration manifest**: A structured document (JSON, YAML, or CSV) listing:
  - Every file to be migrated, with its repository path.
  - The transformation rules to apply to each file (or a reference to a shared rule set).
  - Any file-specific overrides or exceptions to the standard transformation.
- **Repository URL**: The Git repository (or repositories) containing the files to migrate.
- **Transformation rules**: The specific migration patterns to apply. This can be:
  - A find-and-replace pattern set (regex-based).
  - A structural transformation description (e.g., "convert XML bean definitions to Java @Configuration classes").
  - A reference migration example (before/after pair showing the expected transformation).
  - An AST-level transformation specification for complex refactoring.
- **Target branch**: The branch to create migration PRs against (default: main/develop).
- **Batch size** (optional): How many files to process per Devin session (default: 1 file per session for isolation; can be grouped for related files).
- **Concurrency limit** (optional): Maximum number of parallel Devin sessions (default: 50, max: 100 per GUARDRAILS.md org limits).
- **Priority order** (optional): If certain files should be migrated first (e.g., shared libraries before consumers), specify the dependency order.
- **Rollback strategy** (optional): Whether to create individual PRs per file, grouped PRs per batch, or a single PR for the entire migration.

## Procedure

1. **Receive and validate the migration manifest**
   - Parse the migration manifest from the provided format (JSON, YAML, or CSV).
   - Validate that every file listed in the manifest exists in the target repository.
   - Validate that the transformation rules are syntactically correct and can be applied.
   - Check for duplicate entries in the manifest.
   - Identify files with dependencies on each other and flag them for ordered migration.
   - Verify that the total file count and estimated session count fall within GUARDRAILS.md session limits (max 100 parallel sessions per org).
   - Produce a validated manifest summary:
     - Total files to migrate.
     - Estimated number of Devin sessions required.
     - Files grouped by transformation rule type.
     - Dependency chains identified.
     - Estimated total migration duration.

2. **Index affected repositories with DeepWiki**
   - Connect to the DeepWiki MCP server and ensure all affected repositories are indexed.
   - For each file in the manifest, retrieve:
     - The file's role in the overall architecture.
     - Dependencies (what imports this file, what this file imports).
     - Test files associated with the source file.
     - Recent change history.
   - Build a dependency graph of all manifest files to determine safe parallelization groups.
   - Files with no cross-dependencies can be migrated in parallel. Files with dependencies must be ordered: dependencies first, dependents second.

3. **Generate SDD migration specification**
   - Produce a Software Design Document for the overall migration that specifies:
     - Migration objective and business justification.
     - Transformation rules with detailed examples (before/after for each rule type).
     - File grouping strategy (which files are batched together).
     - Execution order for dependency-ordered groups.
     - Expected output format and validation criteria for each transformation.
     - Rollback procedure for partial and full migration rollback.
     - Risk assessment: which transformations are high-risk (semantic changes) vs. low-risk (syntactic changes).
   - For each unique transformation rule, include at least one worked example showing the full before-and-after transformation.
   - The SDD is reviewed by Advanced Devin for completeness and correctness before proceeding.

4. **Generate TDD test templates per batch**
   - For each transformation rule, create a test template that:
     - Validates the syntactic correctness of the transformed output (compiles, parses, lints cleanly).
     - Validates the semantic correctness of the transformation (behavior is preserved or correctly modified per the migration intent).
     - Checks for common migration errors specific to the transformation type:
       - For namespace migrations: all old namespaces replaced, no partial replacements.
       - For framework upgrades: deprecated API calls replaced with new equivalents.
       - For build system conversions: dependency declarations complete, build produces identical artifacts.
       - For configuration migrations: all keys mapped, no orphaned values.
     - Verifies that existing tests in the project still pass after the transformation.
   - Each Devin session receives the test template adapted to its specific file(s).
   - Tests must run in isolation per session so that parallel sessions do not interfere.

5. **Partition files into migration batches**
   - Group files into batches based on:
     - Dependency order: files with no dependents can be processed in any order; files with dependents must be processed after their dependencies.
     - Transformation similarity: files requiring the same transformation rule are grouped for efficient session reuse.
     - Repository locality: files in the same module or package are grouped to minimize cross-module coordination.
     - Batch size limits: each batch contains at most the user-specified batch size (default: 1 file for maximum isolation).
   - Assign each batch a unique batch ID and priority level.
   - Create an execution plan showing:
     - Wave 1: Independent batches that can all run in parallel.
     - Wave 2: Batches that depend on Wave 1 completion.
     - Wave N: Subsequent dependency waves.
   - Log the execution plan with estimated timing for each wave.

6. **Spawn parallel Devin sessions via Advanced Devin API**
   - For each batch in the current wave, create a Devin session via the `devin-cloud-mcp` server:
     - Task payload includes: the SDD migration specification, the TDD test template, the specific file(s) to transform, the transformation rules, and the DeepWiki context for the file(s).
     - Each session is tagged with: the migration ID, batch ID, wave number, and file paths for attribution tracking.
     - Session configuration includes: the target repository, branch, and PR creation settings.
   - Respect the concurrency limit: never exceed the user-specified or guardrail-enforced maximum parallel sessions.
   - Log the session ID, batch ID, and start time for every spawned session.
   - For large migrations (100+ files), spawn sessions in controlled bursts of 20-25 to avoid overwhelming the Devin API rate limits (100 req/min commercial, 50 req/min GovCloud).

7. **Monitor session progress and handle failures**
   - Poll all active sessions at 30-second intervals using the Devin API status endpoint.
   - Track per-session progress:
     - Queued: session created but not yet started.
     - Running: session actively executing the transformation.
     - Completed: session finished successfully, PR created.
     - Failed: session encountered an error.
     - Cancelled: session was manually or automatically cancelled.
   - For failed sessions:
     - Retrieve the error details and session logs.
     - Classify the failure: transient (network, timeout) vs. permanent (transformation error, test failure).
     - Transient failures: automatically retry up to 3 times with exponential backoff.
     - Permanent failures: log the failure, exclude the file from the current migration wave, and add it to a manual remediation queue.
   - Maintain a real-time migration dashboard (structured log) showing:
     - Total sessions: queued/running/completed/failed.
     - Current wave progress percentage.
     - Estimated time remaining.
     - List of failed files with error summaries.
   - When all sessions in a wave complete, validate cross-batch consistency before starting the next wave.

8. **Collect results and aggregate PRs**
   - For each completed session, retrieve:
     - The created PR (URL, number, branch name).
     - Test results (pass/fail counts, coverage).
     - Transformation logs (what changes were made).
     - Any warnings or non-blocking issues.
   - Aggregate results into a migration status matrix:
     - File path | Batch ID | Session ID | Status | PR URL | Tests Pass | Coverage | Warnings.
   - If the user requested grouped PRs (multiple files per PR), verify that all files in the group completed successfully before the PR is finalized.
   - If the user requested a single aggregate PR, create a merge branch combining all individual session branches, resolving any merge conflicts.

9. **Execute batch Devin Review on all PRs**
   - Submit all created PRs to Devin Review via the `devin-review-mcp` server.
   - For efficiency, submit reviews in batches of 20 (respecting the Devin Review rate limit of 20 reviews/hour).
   - Devin Review checks each PR for:
     - Transformation correctness (does the change match the specification?).
     - No unintended modifications (only the specified transformation was applied).
     - Code quality and style consistency.
     - Security implications (no secrets introduced, no vulnerable patterns).
   - Collect review findings and categorize:
     - Blocking: must be fixed before merge.
     - Non-blocking: documented but acceptable.
   - For PRs with blocking findings, create remediation tasks and re-run the affected sessions.

10. **Run guardrails validation per session**
    - Execute the full guardrails validation suite on every PR:
      - HG-001: Tests pass (project-wide and migration-specific tests).
      - HG-002: STIG scan clean.
      - HG-003: Lint/format pass (critical for batch migrations where formatting inconsistency is common).
      - HG-004: Coverage threshold met.
      - HG-005: No secrets.
      - HG-006: Dependency scan (especially important for dependency version migrations).
      - HG-007: Signed commits.
      - HG-008: Audit trail complete per session.
    - Aggregate guardrail results across all sessions.
    - Flag any session that fails a hard gate. Failed sessions cannot be merged until remediated.
    - For batch migrations, a common failure pattern is lint/format inconsistency. If >20% of sessions fail HG-003, consider adding a project-wide format normalization step before migration.

11. **Generate aggregate migration status report**
    - Produce a comprehensive migration report containing:
      - **Executive summary**: total files targeted, successfully migrated, failed, skipped.
      - **Migration statistics**: total Devin sessions spawned, total compute time, average session duration, total cost.
      - **Success matrix**: per-file status with PR links, test results, and review status.
      - **Failure analysis**: for each failed file, the root cause of failure and recommended manual remediation steps.
      - **Guardrail compliance**: aggregate pass/fail rates for each hard gate across all sessions.
      - **Review findings summary**: common findings across PRs, patterns that indicate systemic issues.
      - **Rollback instructions**: how to revert the entire migration or individual file migrations.
      - **Next steps**: remaining manual work, files that require human intervention, follow-up migrations.
    - Store the report in the repository under `docs/migrations/{migration-id}-status-{YYYY-MM-DD}.md`.
    - Update DeepWiki with the migration context and outcomes for future reference.

## Specifications

- **Manifest format**: The migration manifest must be parseable as JSON (preferred), YAML, or CSV. JSON schema for the manifest is defined in `config/schemas/migration-manifest.schema.json`.
- **Concurrency limits**: Maximum 100 parallel Devin sessions per org per GUARDRAILS.md. Default concurrency is 50 sessions. Users may reduce but not exceed the org limit.
- **Session timeout**: Individual Devin sessions have a 4-hour maximum duration per GUARDRAILS.md. Migrations that require longer per-file processing must be broken into smaller units.
- **Rate limiting**: Devin API calls are rate-limited to 100 requests/minute (commercial) or 50 requests/minute (GovCloud). Session spawning must respect these limits with appropriate throttling.
- **Batch attribution**: Every Devin session must be tagged with the migration ID, batch ID, and file path(s) for traceability. Session tags are used for cost attribution and audit trail linkage.
- **PR strategy**: Default is one PR per file for maximum isolation and reviewability. Grouped PRs (multiple files per PR) are allowed when files are tightly coupled. Single aggregate PR is allowed only for migrations under 50 files total (to keep PRs reviewable per GUARDRAILS.md max 50 files modified per session).
- **Retry policy**: Failed sessions are retried up to 3 times for transient errors. Permanent failures are not retried and are added to the manual remediation queue.
- **Ordering enforcement**: When dependency ordering is specified, the skill must not start Wave N+1 until all sessions in Wave N have completed successfully. Failed Wave N sessions block dependent Wave N+1 batches.
- **Cost tracking**: Total migration cost must be tracked by summing individual session costs. If the migration exceeds the configured budget threshold, the skill pauses and escalates for approval.
- **Idempotency**: The migration must be idempotent. Re-running the skill with the same manifest against already-migrated files must detect the completed state and skip those files.
- **Audit trail**: A complete audit trail must be maintained for the migration: manifest validation, session creation, session status transitions, PR creation, review results, guardrail results, and final report generation. Stored as `{migration-id}-audit.jsonl`.
- **Classification**: All migration artifacts must be marked UNCLASSIFIED // FOR OFFICIAL USE ONLY (U//FOUO) unless otherwise directed.

## Advice and Pointers

- Start with a pilot batch of 5-10 files before launching the full migration. This validates the transformation rules and test templates at small scale, catching issues before they multiply across 100+ sessions.
- For framework upgrade migrations (e.g., Spring Boot 2.x to 3.x), the transformation rules often need to handle 20+ distinct patterns (namespace changes, API signature changes, configuration property renames, deprecation replacements). Document each pattern explicitly in the SDD rather than relying on a generic "upgrade" instruction.
- File dependency ordering is critical for migrations that change shared libraries or interfaces. If a shared utility class is migrated before its consumers, consumer sessions will build against the old version and may produce incorrect results. Always migrate bottom-up in the dependency graph.
- When migrating enterprise applications, expect to encounter inconsistent project structures across modules. Some modules may use Maven, others Gradle, others Ant. The transformation rules must account for per-module build system differences.
- Monitor the first 10 sessions closely before letting the remaining sessions run unattended. Early failures often indicate systematic issues with the transformation rules that will affect all sessions.
- For migrations touching database access code (e.g., JDBC to JPA, Hibernate version upgrades), group the migration with its associated database migration scripts and test data to ensure consistency.
- Keep individual session scope small. A single file per session is preferred over batching multiple files because it isolates failures and makes PRs reviewable. The exception is when files must change together (e.g., an interface and all its implementations).
- If the migration introduces new dependencies, verify that the new dependency versions are approved for the enterprise use (check the approved software list and Iron Bank registry for container-based deployments).
- Cost awareness: at approximately $0.25-0.50 per Devin session, a 100-file migration costs $25-50. Plan budget accordingly and set cost thresholds in the session configuration.


## Self-Verification Loop (Devin 2.2)

After completing the primary procedure:

1. **Self-verify**: Run all applicable verification gates:
   - Build/test gates: each session's output compiles and tests pass independently
   - Integration gates: aggregated changes build together without conflicts
   - Security gates: no credentials in migration artifacts, dependency scan on new dependencies
2. **Auto-fix**: If any verification gate fails, attempt automated repair — adjust code, configuration, or test fixtures to resolve the failure.
3. **Re-verify**: Run all verification gates again after fixes. Confirm each gate transitions from FAIL to PASS.
4. **Escalate**: If auto-fix fails after 2 attempts, escalate to human reviewer with a complete evidence pack. Include the failing gate identifier, error output, attempted fixes, and root cause hypothesis.

## Artifact Contract

Every stage of this skill produces paired outputs for machine-consumable handoff:

| Stage | Markdown Output | JSON Output |
|-------|----------------|-------------|
| Manifest Generation | `manifest.md` | `manifest.json` |
| Pilot Batch Execution | `pilot_batch.md` | `pilot_batch.json` |
| Full Migration Execution | `full_migration.md` | `full_migration.json` |
| Aggregation & Reporting | `aggregation.md` | `aggregation.json` |

JSON outputs must conform to the schema defined in `audit/artifact-schemas/`. Markdown outputs are the human-readable narrative; JSON outputs are the machine-consumable contract consumed by the next stage or by OpenClaw for artifact validation.

## Evidence Pack

On completion, produce `evidence-pack.json` containing:

```json
{
  "session_id": "<Devin session identifier>",
  "timestamp": "<ISO 8601 completion time>",
  "skill_id": "devinclaw.parallel_migration.v1",
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
- **Human approval required for**: pilot-to-full migration go/no-go decision, failed session root cause escalation, cross-dependency wave sequencing changes.
- **Auto-escalate on**: Any security finding rated HIGH or CRITICAL, any risk of data loss or corruption, any changes to authentication or authorization logic, any modification to safety-critical code paths (DO-178C applicable systems).

## Forbidden Actions

- Do not exceed the organization's parallel session limit (100 sessions per GUARDRAILS.md). The skill must enforce this limit regardless of user-requested concurrency.
- Do not skip the manifest validation step. An invalid manifest (missing files, duplicate entries, circular dependencies) will cause cascading failures across parallel sessions, wasting compute and creating an inconsistent codebase state.
- Do not start Wave N+1 while Wave N has unresolved failures in dependency-ordered migrations. Dependent files must only be processed after their dependencies are confirmed migrated and passing.
- Do not merge any PR that fails a guardrails hard gate. Failed PRs must be remediated or excluded from the migration.
- Do not create PRs that modify more than 50 files each (GUARDRAILS.md limit). If the aggregation strategy would produce a PR exceeding this limit, split into multiple PRs.
- Do not retry permanently failed sessions without analyzing the root cause. Retrying the same transformation against a file that consistently fails wastes compute and may indicate a flaw in the transformation rules.
- Do not run the full migration without completing the pilot batch first (unless explicitly overridden by the user). The pilot batch is the primary validation mechanism for transformation correctness.
- Do not modify the migration manifest during execution. If manifest changes are needed, the migration must be paused, the manifest updated, and the migration restarted with idempotent handling of already-completed files.
- Do not store API keys, tokens, or credentials in the migration manifest, session payloads, or audit logs. All authentication must go through the vault-mcp server.
- Do not generate migration reports without including rollback instructions. Every migration must be reversible, and the report must document how.
