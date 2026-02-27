# Playbook: Oracle PL/SQL to PostgreSQL Migration

> **Required Knowledge:** `oracle-migrator`

## Overview
Systematically migrate Oracle PL/SQL stored procedures, packages, and functions to PostgreSQL PL/pgSQL. Handles syntax conversion, type mapping, exception handling, and procedural logic translation.

## When to Use
- enterprise database modernization from Oracle to PostgreSQL
- Reducing Oracle licensing costs
- Moving database workloads to cloud-native PostgreSQL (Aurora, Azure PG)

## Instructions

1. **Index the Oracle schema** using DeepWiki MCP. Build a complete dependency graph of all PL/SQL objects.

2. **Inventory and classify** every object:
   - Simple (direct syntax mapping)
   - Moderate (requires logic restructuring)
   - Complex (requires PostgreSQL extension or redesign)

3. **Generate SDD specification** for each migration unit using the `sdd/templates/spec.md` template.

4. **Generate TDD test cases** that validate equivalence between Oracle and PostgreSQL outputs.

5. **Apply systematic transformations**:
   - NVL() → COALESCE()
   - SYSDATE → CURRENT_TIMESTAMP
   - DECODE() → CASE WHEN
   - VARCHAR2 → VARCHAR
   - NUMBER → NUMERIC
   - CONNECT BY → WITH RECURSIVE
   - (+) syntax → ANSI OUTER JOIN

6. **Handle Oracle-specific features**:
   - Package global variables → session variables or config table
   - Autonomous transactions → dblink or separate connection
   - DBMS_OUTPUT → RAISE NOTICE
   - UTL_FILE → pg_read_file or application layer

7. **Run tests** against both Oracle (baseline) and PostgreSQL (migrated). Compare outputs row-by-row.

8. **Create PR** with migration summary. Devin Review auto-triggers.

9. **Validate**: zero CRITICAL findings, all tests green, coverage ≥ 100% for migration code.

## Specifications
- Target: PostgreSQL 15+
- Naming: lowercase with underscores (Oracle uppercase → PostgreSQL lowercase)
- Every migration script must have a corresponding rollback script
- Performance: migrated procedures must execute within 120% of Oracle baseline

## Advice
- Oracle empty string = NULL behavior is the #1 source of migration bugs
- Always migrate in dependency order: types → functions → packages (spec then body) → triggers
- DUAL table does not exist in PostgreSQL — remove FROM DUAL
- Test with the actual application, not just unit tests


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
