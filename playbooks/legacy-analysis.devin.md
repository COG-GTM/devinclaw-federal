# Playbook: Legacy Codebase Analysis

> **Required Knowledge:** `enterprise-modernizer`

## Overview
Rapidly index and analyze a legacy codebase to produce a modernization assessment. Uses DeepWiki for instant codebase intelligence.

## When to Use
- First step in any modernization engagement
- Assessing a new enterprise application for migration feasibility
- Building context before spawning migration sessions

## Instructions

1. **Index with DeepWiki**: Point DeepWiki at the repository or source code archive. DeepWiki will automatically analyze the codebase structure, languages, dependencies, and architecture.

2. **Generate inventory report**:
   - Languages and frameworks detected (with LOC per language)
   - Dependency list with version currency (outdated, EOL, current)
   - Architecture pattern (monolith, layered, microservices, etc.)
   - Database technology and schema complexity
   - Test coverage (if tests exist)
   - CI/CD pipeline presence and health

3. **Identify modernization targets**:
   - Dead code (unreachable, unused imports, commented-out blocks)
   - Security vulnerabilities (hardcoded secrets, deprecated libraries, missing input validation)
   - Technical debt hotspots (high cyclomatic complexity, large files, deep nesting)
   - Deprecated APIs and frameworks at or near end-of-life
   - Database coupling (direct SQL in business logic, no ORM/repository pattern)

4. **Assess migration complexity**: Rate each component:
   - **Low**: Standard CRUD, well-structured, good test coverage
   - **Medium**: Business logic complexity, some coupling, partial tests
   - **High**: Deep framework integration, no tests, Oracle-specific features
   - **Critical**: Mission-critical data, real-time requirements, no documentation

5. **Produce modernization roadmap**: Prioritized list of modernization tasks with estimated effort, dependencies, and recommended approach (rewrite, refactor, re-platform, retire).

6. **Seed DeepWiki knowledge base**: Create knowledge entries for the codebase's architecture, conventions, and domain terms so all future Devin sessions have context.

## Specifications
- Analysis must complete within 30 minutes for codebases up to 500K LOC
- Report format: Markdown with structured data tables
- Dependency vulnerability scanning against NVD (National Vulnerability Database)

## Advice
- Always run legacy analysis BEFORE planning any migration — assumptions about "simple" legacy code are almost always wrong
- Dead code percentage in enterprise legacy systems is typically 20-40% — removing it first simplifies everything
- If the codebase has zero tests, test generation should be the FIRST modernization task (before any code changes)


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
