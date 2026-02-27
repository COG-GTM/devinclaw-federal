# Test-Driven Design (TDD) Templates

Test-Driven Design ensures every piece of modernized code is validated before it ships. In DevinClaw, TDD is not optional — it is a guardrail. No code merges without tests.

## Pipeline

```
Requirements → Test Plan → Test Stubs (Red) → Implementation (Green) → Refactor → Coverage Report
```

## Templates

| Template | Purpose |
|----------|---------|
| `templates/test-plan.md` | Structured test plan for a migration or feature |
| `templates/test-matrix.md` | Test case matrix with inputs, expected outputs, coverage mapping |
| `templates/coverage-requirements.md` | Minimum coverage thresholds by code category |

## Devin Playbook

| Playbook | Purpose |
|----------|---------|
| `playbooks/tdd_cycle.devin.md` | Devin playbook for executing the TDD red-green-refactor cycle |

## Coverage Thresholds

| Code Category | Minimum Branch Coverage |
|--------------|------------------------|
| Authentication / Authorization | 100% |
| Data validation / Input sanitization | 100% |
| Financial calculations | 100% |
| Migration logic (data transformation) | 100% |
| API endpoints | 90% |
| Business logic | 85% |
| UI components | 80% |
| Utility functions | 80% |
| Configuration / Setup | 70% |
