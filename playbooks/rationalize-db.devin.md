# Playbook: Database Rationalization

> **Required Knowledge:** `db-architect`

## Overview
Analyze, classify, and plan the rationalization of a large database portfolio. Identifies redundancy, maps dependencies, and produces a sequenced migration plan.

## When to Use
- the enterprise's 3,000 database rationalization initiative
- Reducing licensing costs through consolidation
- Eliminating redundant data stores across business units

## Instructions

1. **Inventory all databases**: Catalog name, engine, version, size, owner, application(s), last accessed date, criticality rating.

2. **Classify each database** by disposition:
   - **Retain**: Active, critical, no redundancy
   - **Migrate**: Active but on expensive/legacy platform
   - **Consolidate**: Overlapping data with other databases
   - **Archive**: Historical, rarely accessed
   - **Decommission**: Unused or replaced

3. **Build dependency graph**: Map which applications read/write each database, which databases feed other databases (ETL, CDC, DB links, flat files).

4. **Detect duplicates**: Compare schemas across databases. Flag tables with >80% column overlap across different databases.

5. **Sequence migrations**: Leaf nodes first (databases nothing depends on), shared databases last. Never migrate a database before its dependents are handled.

6. **Generate migration plans**: For each database marked Migrate or Consolidate, create an SDD spec with target platform, schema mapping, data migration strategy, and cutover plan.

7. **Validate**: Row counts, checksums, referential integrity checks post-migration. Maintain source in read-only mode until validation complete.

## Specifications
- Size target environments with 50% headroom for growth
- Preserve all audit trails during migration — audit data loss is a federal compliance violation
- 24/7 uptime systems require zero-downtime migration strategies (CDC-based)
- All PII fields must be identified and tagged before migration

## Advice
- Start with quick wins: small, standalone databases with no dependencies
- Database links are hidden dependencies — query ALL_DB_LINKS in every Oracle instance
- Some enterprise databases haven't been accessed in years but contain legally required retention data — archive, don't delete
- data exchange data publishers must be redirected during cutover — coordinate with enterprise ntegration teams


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
