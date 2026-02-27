# Tasks: [Feature Name]

**Date**: [Date]
**Author**: [Author]
**Feature ID**: [NNN]
**Design Reference**: `specs/[feature-id]-[name]/design.md`
**Spec Reference**: `specs/[feature-id]-[name]/spec.md`

---

## Task Summary

| Task ID | Description | Complexity | Dependencies | Parallel | Status |
|---------|-------------|-----------|--------------|----------|--------|
| TASK-001 | [Brief description] | S | None | -- | Pending |
| TASK-002 | [Brief description] | M | TASK-001 | -- | Pending |
| TASK-003 | [Brief description] | S | TASK-001 | [P] | Pending |
| TASK-004 | [Brief description] | M | TASK-001 | [P] | Pending |
| TASK-005 | [Brief description] | L | TASK-002, TASK-003 | -- | Pending |
| TASK-006 | [Brief description] | S | TASK-005 | -- | Pending |

**Complexity Key**: S = Small (< 1 hour), M = Medium (1-4 hours), L = Large (4-8 hours)
**Parallel Marker**: [P] = Can execute in parallel with other [P] tasks in the same phase

---

## Execution Order

Tasks MUST follow test-first order: contracts --> tests --> implementation.

```
Phase 1: Contracts & Foundation
├── TASK-001: [Foundation task -- data models, schemas, interfaces]

Phase 2: Tests (write BEFORE implementation)
├── TASK-002: [Write unit tests for Component 1]
├── TASK-003: [Write integration tests for API endpoints] [P]
├── TASK-004: [Write security tests for auth flows] [P]

Phase 3: Implementation (make tests pass)
├── TASK-005: [Implement Component 1 to pass unit tests]
├── TASK-006: [Implement API endpoints to pass integration tests]

Phase 4: Verification & Cleanup
├── TASK-007: [Run full test suite, verify coverage thresholds]
├── TASK-008: [Update documentation]
```

### Dependency Graph

```
TASK-001 (contracts/foundation)
├── TASK-002 (tests - depends on contracts)
├── TASK-003 (tests - depends on contracts) [P]
├── TASK-004 (tests - depends on contracts) [P]
│
├── TASK-005 (implementation - depends on TASK-002)
├── TASK-006 (implementation - depends on TASK-003, TASK-004)
│
└── TASK-007 (verification - depends on all implementation tasks)
    └── TASK-008 (documentation - depends on verification)
```

---

## Task Details

### TASK-001: [Task Title]

- **Description**: [Detailed description of what needs to be built]
- **Phase**: 1 - Contracts & Foundation
- **Design Reference**: [Which design section this implements]
- **Requirements Addressed**: REQ-001
- **Dependencies**: None
- **Complexity**: S | M | L
- **Files to Create/Modify**:
  - `src/[path]/[file]` -- [what changes]
  - `src/[path]/[file]` -- [what changes]
- **Acceptance Criteria**:
  - [ ] [Testable criterion -- becomes a test case]
  - [ ] [Testable criterion -- becomes a test case]
- **Test Cases to Write**:
  - `test_[unit]_[scenario]_[expected_result]`
  - `test_[unit]_[scenario]_[expected_result]`
- **Status**: Pending | In Progress | [DONE]
- **Notes**: [Implementation guidance or considerations]

### TASK-002: [Task Title]

- **Description**: [Detailed description]
- **Phase**: 2 - Tests
- **Design Reference**: [Design section]
- **Requirements Addressed**: REQ-001, REQ-002
- **Dependencies**: TASK-001
- **Complexity**: M
- **Files to Create/Modify**:
  - `tests/unit/[test_file]` -- [what tests]
- **Acceptance Criteria**:
  - [ ] [Criterion]
  - [ ] [Criterion]
- **Test Cases to Write**:
  - `test_[description]`
  - `test_[description]`
- **Status**: Pending
- **Notes**: [Notes]

### TASK-003: [Task Title] [P]

- **Description**: [Detailed description]
- **Phase**: 2 - Tests
- **Design Reference**: [Design section]
- **Requirements Addressed**: REQ-003
- **Dependencies**: TASK-001
- **Complexity**: S
- **Parallel**: Can run in parallel with TASK-004
- **Files to Create/Modify**:
  - `tests/integration/[test_file]` -- [what tests]
- **Acceptance Criteria**:
  - [ ] [Criterion]
- **Test Cases to Write**:
  - `test_[description]`
- **Status**: Pending
- **Notes**: [Notes]

---

## Implementation Log

Track progress as tasks are completed. Update this section after each task.

| Task | Started | Completed | Tests Written | Tests Passing | Notes |
|------|---------|-----------|--------------|---------------|-------|
| TASK-001 | [date] | [date] | [count] | [count] | [notes] |
| TASK-002 | [date] | [date] | [count] | [count] | [notes] |

---

## Completion Checklist

- [ ] All tasks marked as [DONE]
- [ ] All tests passing (unit, integration, e2e, security)
- [ ] Code coverage meets constitutional thresholds (80%+ overall, 90%+ critical, 100% security)
- [ ] Implementation matches approved design document
- [ ] No orphaned code (all code traced to a task)
- [ ] Traceability verified: requirement --> design --> task --> test --> code
- [ ] Security scan: 0 violations
- [ ] Federal compliance controls verified
- [ ] Documentation updated
- [ ] PR created with links to spec, plan, and tasks

---

## Session Planning

For Devin implementation sessions, group tasks into manageable batches (3-7 tasks per session):

| Session | Tasks | Estimated Duration | Prerequisites |
|---------|-------|--------------------|---------------|
| Session 1 | TASK-001, TASK-002 | [hours] | None |
| Session 2 | TASK-003, TASK-004 | [hours] | Session 1 complete |
| Session 3 | TASK-005, TASK-006 | [hours] | Session 2 complete |
| Session 4 | TASK-007, TASK-008 | [hours] | Session 3 complete |
