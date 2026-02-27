# Coverage Requirements — DevinClaw Federal Standard

## Branch Coverage Thresholds

| Code Category | Minimum | Target | Rationale |
|--------------|---------|--------|-----------|
| Authentication & Authorization | 100% | 100% | Security-critical — STIG AC-3, IA-2 |
| Input Validation & Sanitization | 100% | 100% | Injection prevention — STIG SI-10 |
| Financial / Numerical Calculations | 100% | 100% | Accuracy-critical — no tolerance for rounding errors |
| Data Migration & Transformation | 100% | 100% | Equivalence required — data loss is mission failure |
| API Endpoints | 90% | 95% | All paths including error handling |
| Business Logic | 85% | 90% | Core application behavior |
| UI Components | 80% | 85% | User-facing functionality |
| Utility Functions | 80% | 85% | Shared code used across modules |
| Configuration & Setup | 70% | 80% | Infrastructure code |

## Measurement

- Tool: Istanbul/nyc (JavaScript/TypeScript), coverage.py (Python), JaCoCo (Java)
- Report format: lcov + HTML summary
- CI gate: Build fails if any category falls below minimum
- Reports stored: `coverage/` directory in each PR

## Exceptions

Coverage exceptions require:
1. Written justification in the PR description
2. Approval from the security-auditor knowledge-guided review
3. Documented in `audit/coverage-exceptions.json`
4. Time-boxed — must be resolved within 30 days
