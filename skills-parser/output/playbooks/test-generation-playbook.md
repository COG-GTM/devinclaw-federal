# test-generation

## Overview
Generate comprehensive automated test suites for legacy and modernized codebases. Use this skill when adding test coverage to untested enterprise applications, when generating regression test suites for migration validation, when implementing TDD test plans for Oracle stored procedures or COBOL programs, or when bringing legacy Java/Spring Boot applications to the 80% coverage threshold required by DevinClaw guardrails.

## When to Use
This skill systematically generates automated test suites for codebases that lack adequate test coverage. It analyzes existing code to understand business logic, identifies all testable code paths, generates specification-driven test plans, and produces executable test suites across multiple languages and frameworks. The skill leverages DeepWiki MCP for codebase understanding, generates SDD specifications and TDD test plans before writing any test code, and can spawn parallel Devin sessions for large-scale test generation across hundreds of modules.

Enterprises operate 200+ mission-critical applications, many of which were built over decades without automated testing. These applications support mission-critical operations, transaction processing, facility operations, and regulatory compliance. Adding test coverage is a prerequisite for safe modernization — no code can be refactored, migrated, or replaced without a regression safety net. DevinClaw guardrail HG-004 requires minimum 80% branch coverage for all new and modified code, making test generation a foundational skill for every other modernization activity.

## Instructions
1. **Index codebase with DeepWiki**
   - Connect to the repository via DeepWiki MCP and build a full semantic index.
   - Identify all source modules: classes, functions, stored procedures, API endpoints, UI components.
   - Build a dependency graph showing which modules call which, including external service dependencies.
   - Identify the application framework, dependency injection patterns, and configuration mechanisms.
   - Catalog all database interactions: repositories, DAOs, stored procedure calls, raw queries.
   - Record the total module count, estimated LOC, and current test coverage baseline (0% if no tests exist).

2. **Analyze code paths and generate coverage map**
   - For each target module, perform static analysis to identify:
     - All public methods and their entry points.
     - Branching logic: if/else, switch/case, ternary operators, guard clauses.
     - Loop constructs and their termination conditions.
     - Exception handling paths: try/catch blocks, custom exception types, error propagation.
     - Null/empty checks and defensive code paths.
   - Classify each code path by type:
     - **Happy path**: Normal successful execution.
     - **Edge case**: Boundary values, empty collections, zero/negative inputs.
     - **Error path**: Exceptions, validation failures, timeout conditions.
     - **Security path**: Authentication checks, authorization gates, input validation.
   - Produce a coverage map document listing every testable path per module.

3. **Generate SDD specification for test plan**
   - For each target module or logical group, produce a Software Design Document that specifies:
     - Module purpose and business context within the enterprise application.
     - All dependencies (internal and external) and how they will be mocked or stubbed.
     - Test data requirements: input fixtures, expected outputs, database seed data.
     - Test isolation strategy: how tests will avoid shared state, database side effects, and external service calls.
     - Test organization: test class structure, naming conventions, grouping by feature or code path.
     - Performance test criteria for latency-sensitive modules (e.g., transaction processing).
   - Submit the SDD to Advanced Devin for architectural review and completeness check.

4. **Generate TDD test stubs (failing tests)**
   - For each module, generate test stubs that:
     - Cover every code path identified in the coverage map.
     - Follow the Arrange-Act-Assert (AAA) pattern consistently.
     - Use descriptive test names that document the expected behavior: `should_return_empty_list_when_no_records_match_criteria`.
     - Include appropriate assertions for return values, side effects, exception types, and state changes.
     - Mock all external dependencies using the project's mocking framework (Mockito, unittest.mock, jest.mock).
   - For **Java/Spring Boot** applications:
     - Generate JUnit 5 test classes with `@SpringBootTest` for integration tests and plain `@ExtendWith(MockitoExtension.class)` for unit tests.
     - Use `@MockBean` for Spring-managed dependencies and `@Mock` for plain unit tests.
     - Generate `@WebMvcTest` or `@WebFluxTest` for REST controller tests.
     - Generate `@DataJpaTest` with embedded H2 or Testcontainers for repository tests.
   - For **Oracle stored procedures**:
     - Generate pgTAP test cases for PostgreSQL-migrated procedures.
     - Generate utPLSQL test packages for Oracle-native testing.
     - Include data setup/teardown scripts using temporary tables or savepoints.
   - For **COBOL programs**:
     - Generate test cases using the target language test framework (JUnit if converted to Java, pytest if converted to Python).
     - Include copybook-derived test data structures.
     - Test all paragraph/section entry points and PERFORM THRU paths.
   - For **UI components**:
     - Generate Jest/React Testing Library tests for component rendering, user interactions, and state changes.
     - Generate Playwright tests for critical user flows and accessibility compliance (Section 508).
   - Execute all generated tests to confirm they fail for the right reasons (not due to setup errors or missing imports).

5. **Implement test fixtures and data factories**
   - Create reusable test data factories for domain objects:
     - Builder pattern or factory functions that produce valid default objects.
     - Methods to create objects in specific states (e.g., `createExpiredCertificate()`, `createActiveWorkOrder()`).
     - Randomized data generation for property-based testing where appropriate.
   - Create database seed scripts for integration tests:
     - Minimal representative data sets that exercise all foreign key relationships.
     - Idempotent seed scripts that can be run repeatedly without side effects.
     - Use Testcontainers or embedded databases to isolate test database state.
   - Create mock service responses for external API dependencies:
     - WireMock stubs for REST API dependencies.
     - Mock MQ message payloads for message-driven components.
     - Recorded/replayed HTTP interactions for third-party services (notification, weather, data exchange).

6. **Generate integration and end-to-end tests**
   - For API endpoints:
     - Generate full request/response tests covering all HTTP methods, status codes, and content types.
     - Test authentication and authorization enforcement (CAC/PIV simulation in test mode).
     - Test input validation with OWASP-style payloads (SQL injection, XSS, command injection).
     - Test pagination, filtering, sorting, and error responses.
   - For database interactions:
     - Generate tests that verify CRUD operations against a real database (Testcontainers).
     - Test transaction boundaries: rollback on failure, commit on success.
     - Test concurrent access patterns for multi-user scenarios.
   - For message-driven components:
     - Test message consumption, processing, and acknowledgment.
     - Test dead-letter queue behavior for failed messages.
     - Test idempotency for duplicate message delivery.

7. **Run full test suite and measure coverage**
   - Execute the complete test suite with coverage instrumentation enabled:
     - Java: JaCoCo with branch coverage reporting.
     - Python: coverage.py with branch coverage.
     - TypeScript/JavaScript: Istanbul/c8 with branch coverage.
     - PL/SQL: utPLSQL coverage or pgTAP with pg_coverage.
   - Generate coverage reports in multiple formats: HTML (for human review), XML (for CI/CD), and JSON (for programmatic analysis).
   - Identify any modules still below the coverage threshold.
   - Generate additional tests for uncovered paths until the threshold is met.
   - Validate that all tests are deterministic: run the suite 3 times and confirm identical results.

8. **Spawn parallel Devin sessions for large codebases**
   - For repositories with >30 modules requiring test generation, create batches grouped by:
     - Package or namespace boundaries.
     - Dependency order (test leaf nodes first, then modules that depend on them).
     - Priority (mission-critical modules first).
   - Spawn parallel Devin Cloud sessions (one per module group) using the Devin API v3 batch endpoint.
   - Each session receives: the SDD test plan, target module source code, project test configuration, and shared test utilities/factories.
   - Limit to 10 concurrent sessions per batch run to avoid resource contention.
   - Monitor all sessions for completion and collect coverage results.
   - Aggregate coverage reports across all sessions into a unified project-level report.

9. **Validate test quality**
   - Run mutation testing to validate test effectiveness:
     - Java: PIT (pitest) mutation testing.
     - Python: mutmut or cosmic-ray.
     - TypeScript: Stryker.
   - Target minimum 60% mutation kill rate for generated tests.
   - Identify weak tests (tests that pass even when source code is mutated) and strengthen assertions.
   - Verify that no tests are tautological (always passing regardless of implementation).
   - Confirm all tests have meaningful assertions (not just `assertNotNull`).

10. **Create pull requests and invoke Devin Review**
    - Create one PR per module group or logical test suite.
    - PR description must include:
      - Modules covered and code paths tested.
      - Coverage before and after (delta report).
      - Test framework and runner configuration changes.
      - Any new test dependencies added.
      - Mutation testing results summary.
    - Invoke Devin Review on each PR for automated quality checks.
    - Devin Review validates: test naming conventions, assertion quality, mock usage patterns, and test isolation.
    - Address any review findings before merging.
    - Update DeepWiki with test coverage state and test architecture decisions.

## Specifications
- **Minimum coverage threshold**: 80% branch coverage for all target modules, per DevinClaw guardrail HG-004.
- **Test naming convention**: `should_[expected_behavior]_when_[condition]` for methods; `[ModuleName]Test` or `test_[module_name]` for classes/files.
- **Test isolation**: Every test must be independently runnable. No test may depend on execution order or shared mutable state.
- **Test determinism**: All tests must produce identical results on every run. No time-dependent, random-dependent, or environment-dependent tests without explicit seeding.
- **Test performance**: Individual unit tests must complete in <500ms. Integration tests must complete in <30s. The full suite for a single module must complete in <5 minutes.
- **Mock boundaries**: Mock at the architectural boundary (service layer mocks repositories, controller layer mocks services). Never mock the class under test.
- **Assertion specificity**: Every test must assert specific expected values, not just non-null or non-empty. Exception tests must assert the exception type and message.
- **Test data**: No production data in test fixtures. All test data must be synthetic. PII must never appear in test code.
- **Framework versions**: JUnit 5.10+, pytest 7.0+, Jest 29+, Playwright 1.40+, pgTAP 1.3+, utPLSQL 3.1+.
- **CI integration**: All generated tests must be runnable in the project's CI/CD pipeline without manual configuration. Test reports must output JUnit XML format for pipeline consumption.
- **Batch size**: When using parallel Devin sessions, limit to 10 concurrent sessions per test generation run.

## Advice
- Start with the most critical modules (transaction processing, safety systems, authentication) before generating tests for utilities and helpers. Prioritize by business risk, not by ease of testing.
- Legacy Spring Boot applications often have tight coupling between layers (controllers directly calling repositories). Generate tests at the integration level first (`@SpringBootTest`) to capture current behavior, then add unit tests as the code is refactored.
- For Oracle stored procedures, generate dual-target test cases: utPLSQL tests for validating current Oracle behavior AND pgTAP tests for validating the PostgreSQL migration target. This creates a bridge for the `plsql-migration` skill.
- COBOL programs frequently use global working storage variables as implicit parameters. Map every WORKING-STORAGE SECTION variable that is read or written by the target paragraph to an explicit test parameter.
- When testing enterprise-specific data formats (data standard, FIXM, notification), create fixture files with representative XML/JSON samples. These formats have strict schema validation that must be tested.
- Testcontainers is the preferred approach for database integration tests. It provides true database isolation without the behavioral differences of H2 or in-memory databases.
- For Section 508 accessibility testing, generate Playwright tests that run axe-core checks on every page load. Accessibility is a federal mandate, not optional.
- When generating tests for authentication and authorization, include negative tests: verify that unauthenticated requests receive 401, unauthorized requests receive 403, and expired sessions are rejected.
- Mutation testing is the best indicator of test quality. A high coverage number with a low mutation kill rate means the tests are executing code but not truly validating behavior.
- If the codebase has no test infrastructure at all (no test framework configured, no test directory), start by generating the project scaffolding: build tool test configuration, CI test stage, and a single passing "hello world" test to validate the pipeline.

## Forbidden Actions
- Do not modify production source code while generating tests. Test generation must be additive — only test files, test configuration, and test utilities may be created or modified.
- Do not skip the SDD specification step. Every test plan must have a documented design before test code is written.
- Do not generate tests that depend on network access to external services. All external dependencies must be mocked, stubbed, or containerized.
- Do not use production database credentials or connections in test code. All database tests must use embedded databases, Testcontainers, or dedicated test database instances.
- Do not include real PII, PHI, or sensitive enterprise perational data in test fixtures. All test data must be synthetic and clearly labeled as test data.
- Do not generate tests that modify shared state (global variables, static fields, environment variables) without proper cleanup in a teardown method.
- Do not generate flaky tests. Any test that fails intermittently must be fixed or removed before the PR is created. Non-deterministic tests erode trust in the entire test suite.
- Do not suppress or ignore test failures with `@Disabled`, `@pytest.mark.skip`, or `xit`. If a test cannot pass, fix the test or document the blocker — never skip it silently.
- Do not generate test code that itself contains security vulnerabilities (e.g., hardcoded credentials for test databases, disabled SSL verification, wildcard CORS in test configs).
- Do not add test dependencies that introduce Critical or High CVEs. All test dependencies are subject to the same dependency scanning guardrail (HG-006) as production dependencies.

---
*Generated by DevinClaw Skills Parser at 2026-02-25T06:27:28Z*
*Source: skills/test-generation/SKILL.md*
