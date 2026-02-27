# Playbook: COBOL to Modern Language Conversion

> **Required Knowledge:** `cobol-converter`

## Overview
Convert COBOL programs to Java, Python, or TypeScript while preserving exact business logic. Handles COBOL data structures, control flow, file I/O, and CICS transaction processing.

## When to Use
- Mainframe decommissioning projects
- Converting COBOL batch programs to modern services
- Eliminating mainframe licensing costs

## Instructions

1. **Analyze the COBOL program structure**: Map all four divisions, identify copybooks, and build a dependency graph.

2. **Index with DeepWiki**: Feed all COBOL source files and copybooks to DeepWiki for full context.

3. **Map data structures**: Convert PICTURE clauses to modern types:
   - PIC 9(5)V99 → BigDecimal / Decimal
   - PIC X(20) → String
   - PIC S9(7) COMP-3 → long / int (packed decimal)
   - 88-level conditions → Enums or boolean predicates
   - REDEFINES → Union types or parser functions

4. **Convert control flow**:
   - PERFORM → function call
   - PERFORM VARYING → for loop
   - EVALUATE/WHEN → switch/match
   - GO TO → eliminate (restructure to structured control flow)
   - Paragraph fall-through → explicit function calls

5. **Handle file I/O**:
   - Sequential files (QSAM) → file stream or database table
   - Indexed files (VSAM KSDS) → database table with primary key
   - JCL batch jobs → cron jobs or workflow orchestrator

6. **Handle CICS** (if present):
   - CICS SEND MAP → API response
   - CICS RECEIVE MAP → API request
   - CICS LINK/XCTL → API call or message queue
   - BMS maps → UI components or API schemas

7. **Generate tests**: Write equivalence tests using known COBOL input/output pairs.

8. **Build and validate**: Implement in target language, run all tests, verify numeric precision to exact decimal places.

## Specifications
- Preserve business logic EXACTLY — do not optimize or modernize logic during conversion
- Numeric precision must be bit-exact for packed decimal (COMP-3) values
- All copybook variants must be inventoried before conversion begins
- EBCDIC → UTF-8 encoding conversion required

## Advice
- Implicit decimal points (PIC 9(5)V99) have NO actual decimal in storage — handle correctly or financial calculations will be off by orders of magnitude
- COBOL truncates by default, modern languages round — use explicit TRUNCATE
- Paragraph fall-through is like goto, not function calls — must be explicitly restructured
- Y2K date fixes may be inconsistent across programs — audit every date field


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
