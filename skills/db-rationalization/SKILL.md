---
name: db-rationalization
description: Analyze database schemas across multiple instances to identify duplication, consolidation opportunities, and rationalization paths. Use this skill when performing enterprise-wide database portfolio analysis, when reducing the 3,000 database footprint, when identifying redundant data stores across business units, or when planning database consolidation prior to cloud migration.
---

# Database Rationalization

## Overview

This skill performs cross-instance database analysis to identify schema duplication, redundant data storage, consolidation opportunities, and rationalization paths. It connects to multiple database instances via Database MCP, fingerprints table structures, detects semantic duplicates (tables that store the same data but with different names or structures), maps foreign key relationships, analyzes data volumes, and produces an actionable rationalization plan with migration scripts.

Enterprises operate approximately 3,000 database instances across all business units. Many of these databases were created independently by different programs and contractors over decades, resulting in massive duplication of reference data (airports, airlines, aircraft types, personnel), inconsistent schemas for the same business entities, and fragmented data that should be unified. Rationalization is a prerequisite for effective cloud migration and data analytics initiatives.

> **Objective Constraint:** Database migration is the highest-risk modernization activity. Devin is positioned as an **analysis and documentation accelerator** — not a sole executor of production migration plans. Data migration execution plans (cutover, backfill, reconciliation) generally require subject matter experts (SMEs) with operational domain knowledge and direct access to production constraints. Human SMEs are required for cutover scheduling, backfill validation, reconciliation decisions, and go/no-go authorization. This skill produces draft analysis artifacts and candidate migration scripts for human review — not production-ready migration packages.

## What's Needed From User

- **Database connection details**: Connection strings, credentials (via secrets manager), or Database MCP configuration for each database instance to analyze.
- **Scope**: Which databases or LOBs to include in the analysis (full portfolio or subset).
- **Database platforms**: Which database engines are in scope (Oracle, PostgreSQL, SQL Server, DB2, MySQL, SQLite).
- **Known reference data**: Any existing master data management (MDM) sources or authoritative data sources.
- **Business domain context**: Description of the business domains these databases serve (e.g., core operations, personnel, finance, safety).
- **Consolidation constraints** (optional): Any databases that cannot be consolidated due to regulatory, security, or contractual requirements.
- **Target architecture** (optional): Whether the target is a single consolidated database, a data lake, a federated model, or a microservices-per-database model.

## Procedure

1. **Connect via Database MCP and inventory schemas**
   - Connect to each database instance through the Database MCP server.
   - For each instance, extract the complete schema catalog:
     - All schemas/databases/tablespaces.
     - All tables, views, and materialized views with column definitions.
     - All indexes (primary key, unique, non-unique, composite).
     - All constraints (foreign keys, check constraints, unique constraints, NOT NULL).
     - All stored procedures, functions, packages, and triggers.
     - All sequences and auto-increment definitions.
   - Record database platform, version, character set, and collation for each instance.
   - Store the full inventory in a structured format (JSON) for cross-instance analysis.

2. **Fingerprint tables for duplicate detection**
   - Generate structural fingerprints for every table by hashing:
     - Column names (normalized: lowercased, common abbreviations expanded).
     - Column types (normalized to canonical types: integer, string, decimal, date, boolean, binary).
     - Column count.
     - Nullable patterns.
   - Generate semantic fingerprints using:
     - Table name similarity (Levenshtein distance, Jaccard similarity on tokenized names).
     - Column name overlap percentage.
     - Column type pattern matching.
     - Primary key structure similarity.
   - Cluster tables into candidate duplicate groups where structural similarity exceeds 70% or semantic similarity exceeds 60%.

3. **Detect duplicates and near-duplicates**
   - For each candidate duplicate group, perform detailed comparison:
     - Exact duplicates: Identical column names, types, and constraints (possibly in different databases).
     - Structural duplicates: Same columns but different names (renamed but same data).
     - Semantic duplicates: Different schemas representing the same business entity (e.g., AIRPORT_INFO vs AERODROME_DATA).
     - Subset duplicates: One table is a subset of another (fewer columns but same rows).
     - Versioned duplicates: Same table at different schema evolution stages.
   - For each duplicate pair/group, calculate a confidence score (0-100%) based on the matching evidence.
   - Flag reference data duplicates separately (airports, airlines, aircraft types, country codes, etc.) as these are the highest-value consolidation targets.

4. **Map foreign key relationships and data lineage**
   - Extract all explicit foreign key constraints.
   - Infer implicit foreign keys by analyzing:
     - Column name patterns (columns named `*_id`, `*_code`, `*_key`).
     - JOIN patterns in views and stored procedures.
     - Application code references (if source code is available via DeepWiki).
   - Build a cross-database entity relationship graph.
   - Identify data flow direction: source systems (systems of record) vs. downstream consumers.
   - Map data lineage: which database is the authoritative source for each business entity.

5. **Analyze data volumes and growth patterns**
   - For each table, collect:
     - Row count.
     - Data size (MB/GB).
     - Index size.
     - Average row size.
     - Estimated growth rate (if historical stats are available).
   - Identify the largest tables and their growth trajectories.
   - Flag tables with >1M rows that are duplicated -- these represent the highest storage waste.
   - Calculate total duplication cost in storage (GB) and licensing (Oracle per-CPU costs).

6. **Identify consolidation targets**
   - Rank consolidation opportunities by:
     - Duplication factor (how many copies exist).
     - Data volume savings.
     - Licensing cost reduction.
     - Application impact (how many applications reference each database).
     - Complexity of consolidation (schema differences to reconcile).
   - Classify each consolidation opportunity:
     - **Merge**: Identical schemas can be merged with data deduplication.
     - **Migrate and redirect**: One instance becomes authoritative; others redirect via views or APIs.
     - **Federate**: Keep separate but unify access through a federation layer or API.
     - **Archive and decommission**: Database is unused or contains only historical data; archive to cold storage.
   - Identify dependencies that must be resolved before consolidation (e.g., application code changes, ETL pipeline updates).

7. **Generate the rationalization plan**
   - Produce a comprehensive rationalization plan document containing:
     - Executive summary with projected cost savings.
     - Current state inventory (database count, total size, duplication percentage).
     - Duplicate analysis findings with confidence scores.
     - Consolidation recommendations prioritized by ROI.
     - Target state architecture diagram description.
     - Phase plan with dependencies and timelines.
     - Risk assessment and mitigation strategies.
     - Application impact analysis (which applications need changes per consolidation).

8. **Produce draft migration scripts (for human SME review)**
   - For each approved consolidation, generate:
     - Schema creation DDL for the consolidated target.
     - Data migration scripts (INSERT ... SELECT, with deduplication logic).
     - View creation scripts for backward compatibility (old schema views pointing to new tables).
     - Index creation scripts optimized for the consolidated workload.
     - Constraint creation scripts.
     - Rollback scripts for every migration step.
   - Scripts must be idempotent (safe to re-run).
   - Scripts must include data validation queries (row counts, checksum verification).

## Specifications

- **Database MCP**: All database access must go through the Database MCP server. Direct database connections using raw connection strings in code are prohibited.
- **Read-only access**: All analysis operations must be read-only. No DDL or DML is executed against production databases during the analysis phase.
- **Fingerprint algorithm**: Table fingerprints must use SHA-256 hashing on normalized column definitions. The normalization rules must be documented and reproducible.
- **Similarity thresholds**: Duplicate candidates require structural similarity >= 70% OR semantic similarity >= 60%. These thresholds can be adjusted by the user.
- **Confidence scoring**: Duplicate pair confidence must be calculated as: (0.3 * column_name_overlap) + (0.25 * column_type_match) + (0.2 * pk_structure_match) + (0.15 * table_name_similarity) + (0.1 * constraint_similarity).
- **Output format**: The rationalization plan must be generated as Markdown stored in `docs/rationalization/` with the naming convention `{scope}-rationalization-plan-{YYYY-MM-DD}.md`.
- **Migration scripts**: All generated scripts must target the specified database platform and version. Scripts must be syntactically valid and parseable.
- **Data sensitivity**: PII columns (names, SSNs, badge numbers) must be identified and flagged. Migration scripts must not expose PII in logs or intermediate files.
- **Concurrency**: When analyzing multiple databases in parallel, limit to 5 concurrent Database MCP connections to avoid overloading database servers.
- **Audit trail**: Every analysis action must be logged with timestamp, database instance, and operation performed.

## Advice and Pointers

- Start with reference data tables (airports, airlines, aircraft types). These are the easiest to consolidate and provide immediate value by establishing a single source of truth.
- Oracle synonym chains can mask the true location of data. Always resolve synonyms to their base objects before fingerprinting.
- Many enterprise databases have "shadow" copies created for reporting workloads. These are prime decommissioning candidates if replaced with read replicas or materialized views.
- Watch for databases that appear unused but are actually consumed by batch jobs that run monthly or quarterly. Check job schedulers before recommending decommission.
- Database links (Oracle) and linked servers (SQL Server) indicate cross-database dependencies. Map these explicitly -- they represent integration points that must be preserved during consolidation.
- Schema names often encode organizational information (e.g., ATO_OPS, AVS_CERT). Use this to group databases by business domain.
- When calculating storage savings, remember to account for index overhead, which can be 50-100% of data size for heavily indexed OLTP tables.
- Historical tables and audit logs are often the largest tables. Consider time-partitioning and archival strategies rather than consolidation for these.
- Database migration is the highest-risk modernization activity. Always require human SME sign-off on migration plans, cutover schedules, and backfill strategies. Devin accelerates the analysis and documentation — humans own the execution decisions.


## Self-Verification Loop (Devin 2.2)

After completing the primary procedure:

1. **Self-verify**: Run all applicable verification gates:
   - Build/test gates: migration script syntax validation, idempotency verification
   - DB gates: schema diff review, rollback script completeness, row count reconciliation queries
   - Data gates: PII field identification confirmation, referential integrity preservation
2. **Auto-fix**: If any verification gate fails, attempt automated repair — adjust code, configuration, or test fixtures to resolve the failure.
3. **Re-verify**: Run all verification gates again after fixes. Confirm each gate transitions from FAIL to PASS.
4. **Escalate**: If auto-fix fails after 2 attempts, escalate to human reviewer with a complete evidence pack. Include the failing gate identifier, error output, attempted fixes, and root cause hypothesis.

## Artifact Contract

Every stage of this skill produces paired outputs for machine-consumable handoff:

| Stage | Markdown Output | JSON Output |
|-------|----------------|-------------|
| Schema Inventory | `schema_inventory.md` | `schema_inventory.json` |
| Duplicate Detection | `duplicate_detection.md` | `duplicate_detection.json` |
| Consolidation Analysis | `consolidation_analysis.md` | `consolidation_analysis.json` |
| Rationalization Plan | `rationalization_plan.md` | `rationalization_plan.json` |
| Migration Script Generation | `migration_scripts.md` | `migration_scripts.json` |

JSON outputs must conform to the schema defined in `audit/artifact-schemas/`. Markdown outputs are the human-readable narrative; JSON outputs are the machine-consumable contract consumed by the next stage or by OpenClaw for artifact validation.

## Evidence Pack

On completion, produce `evidence-pack.json` containing:

```json
{
  "session_id": "<Devin session identifier>",
  "timestamp": "<ISO 8601 completion time>",
  "skill_id": "devinclaw.db_rationalization.v1",
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
- **Human approval required for**: production database cutover, data backfill execution, cross-LOB consolidation decisions, decommissioning approvals.
- **Auto-escalate on**: Any security finding rated HIGH or CRITICAL, any risk of data loss or corruption, any changes to authentication or authorization logic, any modification to safety-critical code paths (DO-178C applicable systems).

## Forbidden Actions

- Do not execute any DDL (CREATE, ALTER, DROP) or DML (INSERT, UPDATE, DELETE) against production databases during analysis. Analysis is strictly read-only.
- Do not store database credentials in any output file, report, or migration script. All credentials must be managed through the secrets manager or Database MCP configuration.
- Do not recommend decommissioning a database without verifying that no active application or batch job depends on it.
- Do not generate migration scripts that lack rollback procedures. Every forward migration must have a corresponding rollback.
- Do not skip data validation steps in migration scripts. Every migration must include row count verification and data integrity checks.
- Do not merge databases across different security boundaries without explicitly documenting the security implications and obtaining authorization.
- Do not assume that identically named tables across databases contain the same data. Always verify with data sampling.
- Do not expose PII in analysis reports. Use anonymized or aggregated data in examples and findings.
