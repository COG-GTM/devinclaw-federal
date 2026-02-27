# TDD Cycle Playbook

## Overview
Execute the Test-Driven Design red-green-refactor cycle for a specific task or migration unit. This playbook ensures tests are written BEFORE implementation and that every code path is validated.

## When to Use
- After SDD specification is complete and before implementation begins
- When adding test coverage to existing untested legacy code
- When validating migration equivalence between Oracle and PostgreSQL implementations

## Instructions

### Phase 1: Red (Write Failing Tests)
1. Read the SDD specification for the task
2. For each requirement in the spec, write one or more test cases that:
   - Describe the expected behavior in plain English (test name)
   - Set up the necessary preconditions (arrange)
   - Execute the function/endpoint under test (act)
   - Assert the expected outcome (assert)
3. Include tests for:
   - Happy path (normal operation)
   - Edge cases (null, empty, boundary values)
   - Error paths (invalid input, unauthorized access, resource not found)
   - Security (injection attempts, auth bypass)
4. Run all tests — they should ALL FAIL (red)
5. If any test passes before implementation, the test is not testing new behavior — review it

### Phase 2: Green (Implement Minimum Code)
1. For each failing test, write the MINIMUM code to make it pass
2. Do not add features or optimizations not covered by a test
3. Run tests after each small change — watch them turn green one by one
4. If a test is difficult to make pass, the test may be too broad — split it
5. Continue until all tests pass

### Phase 3: Refactor
1. With all tests green, improve code quality:
   - Extract common patterns into helper functions
   - Improve naming for clarity
   - Remove duplication
   - Optimize performance-critical paths
2. Run tests after every refactor step — they must stay green
3. If a test breaks during refactor, undo the last change and try a smaller step

### Phase 4: Coverage Validation
1. Generate coverage report
2. Check against thresholds in `tdd/templates/coverage-requirements.md`
3. If below threshold, identify uncovered branches and write additional tests
4. Commit coverage report with the PR

## Specifications
- Test framework: Use the project's existing framework. Default: Jest (TS/JS), pytest (Python), JUnit (Java)
- Coverage tool: Istanbul/nyc, coverage.py, or JaCoCo
- All tests must be deterministic — no flaky tests allowed
- Test execution time: individual tests < 5 seconds, full suite < 5 minutes
- No network calls in unit tests — mock all external dependencies

## Advice
- Write the test name as a sentence: `test('returns 401 when auth token is expired')`
- One assertion per test when possible — easier to diagnose failures
- For migration equivalence: capture Oracle output as fixtures, assert PostgreSQL matches exactly
- If you find yourself writing complex test setup, the code under test may need a simpler interface
