# Test Plan: [Feature / Migration Name]

## 1. Scope
- **What is being tested**: [Description of the system, module, or migration under test]
- **What is NOT being tested**: [Explicitly state out-of-scope items]
- **SDD Reference**: [Link to the SDD spec this test plan validates]

## 2. Test Strategy
- **Unit tests**: [Framework: Jest/pytest/JUnit] — test individual functions and business logic
- **Integration tests**: [Framework] — test API endpoints, database operations, service interactions
- **E2E tests**: [Framework: Playwright/Cypress] — test full user workflows (if applicable)
- **Performance tests**: [Framework: k6/Artillery] — test response times and throughput (if applicable)
- **Security tests**: STIG compliance checks, injection testing, auth bypass attempts

## 3. Test Environment
- **Database**: [PostgreSQL 15+ / Oracle 19c for baseline comparison]
- **Runtime**: [Node.js 20+ / Java 21+ / Python 3.12+]
- **Test data**: [Synthetic / Sanitized production / Both]
- **CI integration**: [GitHub Actions / Azure DevOps Pipelines]

## 4. Test Cases

### 4.1 Happy Path Tests
| ID | Description | Input | Expected Output | Priority |
|----|-------------|-------|-----------------|----------|
| TC-001 | | | | P1 |
| TC-002 | | | | P1 |

### 4.2 Edge Case Tests
| ID | Description | Input | Expected Output | Priority |
|----|-------------|-------|-----------------|----------|
| TC-100 | Null input handling | null | Appropriate error | P1 |
| TC-101 | Empty string input | "" | Appropriate handling | P2 |
| TC-102 | Maximum length input | Max chars | Truncation or error | P2 |

### 4.3 Error Path Tests
| ID | Description | Input | Expected Output | Priority |
|----|-------------|-------|-----------------|----------|
| TC-200 | Invalid authentication | Bad token | 401 Unauthorized | P1 |
| TC-201 | Insufficient permissions | Valid token, wrong role | 403 Forbidden | P1 |
| TC-202 | Resource not found | Invalid ID | 404 Not Found | P2 |

### 4.4 Migration Equivalence Tests (if applicable)
| ID | Description | Oracle Output | PostgreSQL Output | Match? |
|----|-------------|--------------|-------------------|--------|
| ME-001 | | | | |

### 4.5 Security Tests
| ID | STIG Control | Test Description | Expected Result |
|----|-------------|------------------|-----------------|
| ST-001 | SI-10 | SQL injection attempt | Input rejected |
| ST-002 | SI-10 | XSS attempt | Input sanitized |
| ST-003 | SC-8 | Verify TLS 1.2+ | Connection encrypted |
| ST-004 | IA-5 | Weak password attempt | Rejected |

## 5. Coverage Requirements
- **Overall**: ≥ 85% branch coverage
- **Critical paths**: 100% (auth, data validation, financial logic)
- **Migration code**: 100% equivalence coverage

## 6. Acceptance Criteria
- [ ] All P1 test cases passing
- [ ] All P2 test cases passing or documented as known limitations
- [ ] Coverage thresholds met
- [ ] No CRITICAL security findings
- [ ] Performance within 120% of baseline (if applicable)
- [ ] Migration equivalence validated (if applicable)
