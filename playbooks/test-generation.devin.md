# Playbook: Automated Test Suite Generation

> **Required Knowledge:** `test-engineer`

## Overview
Generate comprehensive test suites for legacy codebases that have zero or minimal test coverage. This is typically the FIRST modernization task — you cannot safely change code without tests.

## When to Use
- Legacy enterprise applications with no test coverage
- Before any migration or refactoring work begins
- Meeting federal testing requirements for ATO

## Instructions

1. **Analyze the codebase** with DeepWiki to understand: entry points, business logic paths, data flows, external dependencies.

2. **Identify critical paths**: Authentication, authorization, data validation, business calculations, API endpoints, database operations.

3. **Generate test plan** using `tdd/templates/test-plan.md`. Prioritize: critical paths (100% coverage) → business logic (85%) → utilities (80%).

4. **Write test stubs**: For each critical path, generate test files with descriptive test names and TODO implementations.

5. **Implement tests**: Fill in test implementations. For each function/endpoint:
   - Happy path test (normal operation)
   - At least one edge case (null, empty, boundary)
   - At least one error path (invalid input, unauthorized)

6. **Mock external dependencies**: Database calls, API calls, file system access — all mocked in unit tests.

7. **Run and validate**: Execute full test suite, generate coverage report, identify gaps.

8. **Create PR** with test suite. Devin Review validates test quality.

## Specifications
- Framework: match project's existing framework, or Jest (JS/TS), pytest (Python), JUnit (Java)
- Coverage target: 80% branch coverage minimum for initial generation
- All tests must be deterministic — no flaky tests
- Test execution time: < 5 minutes for full suite

## Advice
- For completely untested legacy code, start with integration/API tests (higher coverage per test) then add unit tests
- Capture real Oracle/database outputs as test fixtures for migration equivalence testing later
- Legacy code often has hidden side effects — test for state changes, not just return values


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
