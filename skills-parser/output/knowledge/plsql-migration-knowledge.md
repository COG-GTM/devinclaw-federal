# Knowledge: plsql-migration

## Overview
Migrate Oracle PL/SQL stored procedures, packages, and functions to PostgreSQL-compatible SQL. Use this skill when converting Oracle database logic to PostgreSQL as part of enterprise database modernization, when eliminating Oracle licensing costs, or when moving database workloads to cloud-native PostgreSQL services (Amazon Aurora, Azure Database for PostgreSQL).

## What's Needed From User
- **Oracle schema access details**: Database connection information or DDL export files for the source Oracle schema.
- **Target PostgreSQL version**: The PostgreSQL version to target (default: PostgreSQL 15+).
- **Scope**: Which PL/SQL objects to migrate -- full schema, specific packages, or specific procedures/functions.
- **Application context**: The application(s) that call these PL/SQL objects, so call-site changes can be identified.
- **Test data availability**: Whether representative test data exists or needs to be synthesized.
- **Priority order** (optional): If migrating multiple packages, the preferred order of migration.
- **Oracle-specific features in use** (optional): Known usage of Oracle-specific features like Advanced Queuing, Spatial, XMLDB, or UTL packages.

## Procedure
1. **Index Oracle schema with DeepWiki**
   - Connect to the Oracle schema via Database MCP or import DDL export files.
   - Index all PL/SQL objects: packages (spec and body), standalone procedures, standalone functions, triggers, types, and type bodies.
   - Build a dependency graph of all PL/SQL objects (which packages call which).
   - Index all tables, views, materialized views, sequences, synonyms, and database links referenced by PL/SQL code.
   - Record the total object count and estimated LOC for migration sizing.

2. **Inventory PL/SQL objects and classify complexity**
   - Create an inventory spreadsheet of every PL/SQL object with:
     - Object name, type, LOC, and number of dependencies.
     - Oracle-specific feature usage (DBMS_OUTPUT, UTL_FILE, UTL_HTTP, DBMS_SCHEDULER, DBMS_LOB, DBMS_SQL, etc.).
     - Complexity rating: Simple (direct syntax mapping), Moderate (requires logic restructuring), Complex (requires PostgreSQL extension or custom implementation).
   - Group objects by package for migration batching.
   - Identify objects with no PostgreSQL equivalent that require architectural redesign.

3. **Generate SDD specification for each migration unit**
   - For each package or standalone object, produce a Software Design Document (SDD) that specifies:
     - Current Oracle behavior and business purpose.
     - Input/output parameter mappings with type conversions.
     - PostgreSQL target implementation approach.
     - Oracle-to-PostgreSQL syntax transformations required.
     - Exception handling mapping.
     - Transaction behavior preservation.
     - Performance considerations.

4. **Generate TDD test plans and test cases**
   - For each migration unit, create test cases that:
     - Exercise every code path in the original PL/SQL.
     - Test boundary conditions and NULL handling.
     - Validate output equivalence between Oracle and PostgreSQL implementations.
     - Test exception/error conditions.
     - Verify transaction rollback behavior.
   - Tests must be runnable against both Oracle (for baseline) and PostgreSQL (for validation).

5. **Execute syntax migration**
   - Apply the following systematic transformations:
     - **Data types**: NUMBER to NUMERIC/INTEGER/BIGINT, VARCHAR2 to VARCHAR, DATE to TIMESTAMP, CLOB to TEXT, BLOB to BYTEA, RAW to BYTEA, BOOLEAN (PL/SQL) to BOOLEAN.
     - **Functions**: NVL() to COALESCE(), SYSDATE to NOW() or CURRENT_TIMESTAMP, DECODE() to CASE WHEN, NVL2() to CASE WHEN, TRUNC(date) to DATE_TRUNC(), TO_CHAR/TO_DATE/TO_NUMBER (adjust format masks), SUBSTR() to SUBSTRING(), INSTR() to POSITION() or STRPOS(), ROWNUM to ROW_NUMBER() OVER() or LIMIT.
     - **String concatenation**: Oracle's implicit type conversion with || must be made explicit with CAST().
     - **Sequences**: schema.sequence.NEXTVAL to NEXTVAL('schema.sequence'), CURRVAL similarly.
     - **Outer joins**: Oracle (+) syntax to ANSI LEFT/RIGHT OUTER JOIN.
     - **CONNECT BY**: Convert to recursive CTEs (WITH RECURSIVE).
     - **MERGE statements**: Convert to INSERT ... ON CONFLICT (upsert).
     - **Package variables**: Convert to PostgreSQL session variables, temporary tables, or application-level state management.
     - **Autonomous transactions**: Refactor using dblink or separate connections, as PostgreSQL does not support autonomous transactions natively.

6. **Convert Oracle types and collections**
   - Convert Oracle object types to PostgreSQL composite types.
   - Convert Oracle nested tables and VARRAYs to PostgreSQL arrays or JSONB.
   - Convert Oracle associative arrays (INDEX BY tables) to PostgreSQL temporary tables or HSTORE/JSONB.
   - Convert REF CURSORs to PostgreSQL REFCURSOR or SETOF RECORD.
   - Convert Oracle %ROWTYPE and %TYPE to explicit type declarations.

7. **Handle exception blocks**
   - Map Oracle predefined exceptions to PostgreSQL SQLSTATE codes:
     - NO_DATA_FOUND to SQLSTATE '02000' (or use GET DIAGNOSTICS).
     - TOO_MANY_ROWS to SQLSTATE '21000'.
     - DUP_VAL_ON_INDEX to SQLSTATE '23505'.
     - ZERO_DIVIDE to SQLSTATE '22012'.
     - INVALID_NUMBER/VALUE_ERROR to SQLSTATE '22P02' or '22023'.
   - Convert RAISE_APPLICATION_ERROR to RAISE EXCEPTION with ERRCODE.
   - Convert PRAGMA EXCEPTION_INIT to explicit SQLSTATE checks.
   - Preserve WHEN OTHERS handlers but add explicit SQLSTATE logging.

8. **Run tests and validate**
   - Execute all TDD test cases against the migrated PostgreSQL code.
   - Compare outputs row-by-row and value-by-value against Oracle baseline results.
   - Validate that transaction semantics are preserved.
   - Run performance benchmarks on critical procedures.
   - Fix any failures and re-run until all tests pass.
   - Document any behavioral differences that are intentional (e.g., NULL handling edge cases).

9. **Spawn parallel Devin sessions for large migrations**
   - For schemas with >20 packages, create migration batches grouped by dependency order.
   - Spawn parallel Devin sessions (one per package or logical group) using the Devin API v3 batch endpoint.
   - Each session receives: the SDD spec, TDD test plan, source PL/SQL, and the migration transformation rules.
   - Monitor all sessions for completion and collect results.
   - Validate cross-package dependencies after all sessions complete.

10. **Create pull requests and invoke Devin Review**
    - Create one PR per package or logical migration unit.
    - PR description must include: migration summary, objects converted, test results, and known behavioral differences.
    - Invoke Devin Review on each PR for automated quality checks.
    - Address any review findings before merging.

## Specifications
- **Target compatibility**: All migrated code must be compatible with PostgreSQL 15+ and must not use deprecated features.
- **Naming conventions**: PostgreSQL object names must be lowercase with underscores (Oracle uppercase names converted to lowercase).
- **Schema mapping**: Oracle schemas map to PostgreSQL schemas. Preserve the schema namespace.
- **Grant/privilege migration**: Convert Oracle GRANT statements to PostgreSQL GRANT syntax. Map Oracle roles to PostgreSQL roles.
- **Test coverage**: Every migrated procedure/function must have at least one test case per code path. Target minimum 80% branch coverage.
- **Performance baseline**: Critical procedures (identified during inventory) must perform within 120% of Oracle baseline execution time.
- **Rollback capability**: All migration scripts must include corresponding rollback scripts.
- **Encoding**: Ensure character set compatibility. Oracle AL32UTF8 maps to PostgreSQL UTF8.
- **NULL semantics**: Document all cases where Oracle and PostgreSQL NULL handling differs (e.g., empty string vs NULL in Oracle).
- **Batch size**: When using parallel Devin sessions, limit to 10 concurrent sessions per migration run to avoid resource contention.

## Advice and Pointers
- Oracle's empty string equals NULL behavior is the single most common source of migration bugs. Audit every VARCHAR2 comparison and concatenation for this edge case.
- Package global variables have no direct PostgreSQL equivalent. The cleanest migration path is to use a dedicated configuration table or PostgreSQL's `SET` / `current_setting()` for session-level state.
- Oracle's implicit DATE-to-string and string-to-DATE conversions based on NLS_DATE_FORMAT cause silent bugs in PostgreSQL. Make all conversions explicit.
- Test with the actual application, not just unit tests. Many Oracle applications rely on implicit behaviors (like Oracle's automatic index usage hints) that differ in PostgreSQL.
- For DBMS_OUTPUT.PUT_LINE usage, convert to RAISE NOTICE for debugging purposes.
- Oracle's DUAL table does not exist in PostgreSQL. Remove FROM DUAL in SELECT statements (PostgreSQL allows SELECT without FROM).
- When migrating DBMS_SCHEDULER jobs, map them to pg_cron or external schedulers.
- Materialized view refresh syntax differs significantly. Plan for manual conversion of each refresh strategy.
- Always migrate and test in dependency order: types first, then standalone functions, then packages (specs before bodies), then triggers.

## Forbidden Actions
- Do not drop or modify any Oracle source objects. The Oracle schema must remain untouched as the source of truth during migration.
- Do not skip the SDD specification step. Every migration unit must have a documented design before code conversion begins.
- Do not skip the TDD test generation step. Every migration unit must have tests before migration.
- Do not use Ora2Pg or other automated tools as the sole migration method. Automated tools handle syntax but miss semantic and business logic issues. They may be used as an accelerator, but output must be reviewed and tested.
- Do not ignore Oracle-specific optimizer hints. While PostgreSQL does not use hints in the same way, the hint presence indicates performance-sensitive code that needs PostgreSQL-specific tuning (e.g., appropriate indexes, query restructuring).
- Do not migrate triggers without understanding their firing order. Oracle and PostgreSQL trigger execution order differs.
- Do not assume COMMIT/ROLLBACK behavior is identical. Oracle's implicit commit on DDL, auto-commit behavior, and savepoint handling all differ from PostgreSQL.
- Do not leave any SQLCODE or SQLERRM references unconverted. These are Oracle-specific and must be replaced with PostgreSQL's SQLSTATE and SQLERRM equivalents.

---
*Generated by DevinClaw Skills Parser at 2026-02-25T06:27:28Z*
*Source: skills/plsql-migration/SKILL.md*
