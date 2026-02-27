# Constitution: [Project Name]

**Date**: [Date]
**Author**: [Author]
**Status**: Draft | In Review | Approved
**Version**: 1.0

---

## Project Identity

### Mission
[Brief statement of the project's purpose and the problem it solves.]

### Scope
[What this project covers and explicitly does NOT cover.]

### Target Users
[Who uses this system and in what context.]

### Federal Context
[enterprise ine of business, program office, or system this supports. Reference applicable Authority to Operate (ATO) or system categorization.]

---

## Core Values

1. **Security First** -- Every action complies with NIST 800-53, DISA STIG, and FedRAMP controls. Security is not an afterthought; it is a constitutional requirement.
2. **Transparency** -- Full audit trail for every modification, every session, every PR. Federal systems demand accountability.
3. **Simplicity Over Cleverness** -- Prefer straightforward solutions. Code should be readable by the next engineer, not impressive to the current one.
4. **Test-First Discipline** -- No production code without a failing test. Tests are the proof that the system works.
5. **Traceability** -- Every line of code traces back to a requirement, every requirement to a business need.

---

## Architecture Principles

### Simplicity Gate

All design decisions must pass the simplicity gate:

- [ ] Can a junior developer understand this in under 5 minutes?
- [ ] Does this introduce fewer than 3 new concepts?
- [ ] Is there a simpler approach that meets the same requirements?
- [ ] Does this avoid premature optimization?

If any answer is "no," document the justification in the design's Complexity Tracking section.

### Anti-Abstraction Principle

- Use frameworks and libraries directly; do not wrap them in unnecessary abstraction layers
- Avoid creating interfaces or abstractions "for future flexibility" unless a current requirement demands it
- If an abstraction does not serve at least two concrete use cases today, remove it
- Prefer flat, explicit code over deep inheritance hierarchies

### Integration-First Testing

- Prefer integration tests with real dependencies (test containers, test databases) over unit tests with mocks
- Mock only at true system boundaries (external APIs, third-party services)
- Test the contract, not the implementation detail
- Use realistic test data that reflects actual enterprise perational scenarios

### Technology Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| [Layer] | [Technology] | [Why this was chosen] |
| [Layer] | [Technology] | [Why this was chosen] |
| [Layer] | [Technology] | [Why this was chosen] |

### Dependency Rules

- Pin all dependency versions in lock files
- Review new dependencies before adding (security audit required for federal systems)
- Prefer well-maintained packages with active security patch cadence
- Minimize dependency count -- fewer dependencies means smaller attack surface

---

## Security Requirements

### Compliance Frameworks

- [ ] **NIST 800-53**: [Applicable control families, e.g., AC, AU, CM, IA, SC]
- [ ] **DISA STIG**: [Applicable STIGs for the technology stack]
- [ ] **FedRAMP**: [Applicable baseline: Low, Moderate, High]
- [ ] **FISMA**: [System categorization: Low, Moderate, High]

### Security Controls

| Control | Description | Implementation |
|---------|-------------|----------------|
| Authentication | [Method: CAC/PIV, SAML, OAuth] | [How it is implemented] |
| Authorization | [RBAC, ABAC, policy-based] | [How it is implemented] |
| Encryption at Rest | [AES-256, FIPS 140-2 validated] | [How it is implemented] |
| Encryption in Transit | [TLS 1.2+, mutual TLS] | [How it is implemented] |
| Audit Logging | [All access and modification events] | [How it is implemented] |
| Input Validation | [Boundary validation, sanitization] | [How it is implemented] |

### Forbidden in Code

- Hardcoded credentials, API keys, or secrets
- PII or classified data in source code, comments, or test fixtures
- Disabled security controls (even temporarily)
- Unencrypted storage of sensitive data
- Direct database queries without parameterization (SQL injection risk)

---

## Testing Requirements

### Coverage Thresholds

| Metric | Minimum | Target | Enforced |
|--------|---------|--------|----------|
| Overall line coverage | 80% | 90% | CI gate |
| Critical path coverage | 90% | 100% | CI gate |
| Security control coverage | 100% | 100% | CI gate |
| New code coverage | 80% | 95% | PR check |

### TDD Mandate

- All new features MUST follow Test-Driven Development (red-green-refactor)
- Tests are written BEFORE implementation code
- Tests must fail before implementation (Red phase verified)
- Implementation must be minimal code to make tests pass (Green phase)
- Refactoring only when all tests are green

### Test Categories

| Category | Location | Run When | Time Budget |
|----------|----------|----------|-------------|
| Unit | `tests/unit/` | Every commit | < 30 seconds |
| Integration | `tests/integration/` | Pre-merge | < 2 minutes |
| E2E | `tests/e2e/` | CI pipeline | < 5 minutes |
| Security | `tests/security/` | Pre-merge + nightly | < 3 minutes |
| Performance | `tests/performance/` | Pre-release | < 10 minutes |

---

## Code Standards

### General Rules

- Write clean, readable, self-documenting code
- Follow the Single Responsibility Principle (SRP)
- Keep functions under 30 lines
- Use meaningful, descriptive names
- Handle errors explicitly -- never silently swallow exceptions
- Document all public APIs with docstrings/JSDoc

### Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Files | `kebab-case` | `task-service.ts` |
| Classes | `PascalCase` | `TaskService` |
| Functions (TS/JS) | `camelCase` | `createTask()` |
| Functions (Python) | `snake_case` | `create_task()` |
| Constants | `UPPER_SNAKE_CASE` | `MAX_RETRY_COUNT` |

### Version Control

- Conventional commit messages (`feat:`, `fix:`, `refactor:`, `test:`, `docs:`)
- Each commit represents a single logical change
- Never commit secrets, credentials, or environment-specific configuration
- PR templates require links to spec/plan/tasks

---

## Constitutional Gates

Before any implementation begins, verify:

- [ ] Constitution is read and understood
- [ ] Spec exists and is approved (no `[NEEDS CLARIFICATION]` markers remain)
- [ ] Design passes the Simplicity Gate
- [ ] Design passes the Anti-Abstraction check
- [ ] Security requirements are addressed in the design
- [ ] Test strategy covers all acceptance criteria
- [ ] Federal compliance controls are mapped to implementation

Before any PR is merged, verify:

- [ ] All tests pass
- [ ] Coverage thresholds met
- [ ] No security violations (Guardrails API: 0 violations)
- [ ] Implementation matches approved design
- [ ] Audit trail is complete
- [ ] Documentation is updated

---

**Approval**:
- [ ] Project Lead approved
- [ ] Security Officer approved
- [ ] Compliance Officer approved
- Date approved: [Date]
