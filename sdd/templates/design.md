# Design: [Feature Name]

**Date**: [Date]
**Author**: [Author]
**Status**: Draft | In Review | Approved
**Feature ID**: [NNN]
**Specification Reference**: `specs/[feature-id]-[name]/spec.md`
**Constitution Reference**: `constitution.md`

---

## Architecture Overview

[High-level description of how this feature fits into the system architecture. Explain the key components, their relationships, and how they satisfy the requirements defined in the specification.]

```
[Component diagram or ASCII art showing the main components and their relationships]

Example:
┌──────────┐     ┌──────────┐     ┌──────────┐
│  Client   │────>│   API    │────>│ Service  │
│           │<────│ Gateway  │<────│  Layer   │
└──────────┘     └──────────┘     └─────┬────┘
                                        │
                                  ┌─────▼────┐
                                  │ Data     │
                                  │ Store    │
                                  └──────────┘
```

---

## Component Design

### Component 1: [Component Name]

- **Purpose**: [What this component does]
- **Requirements Addressed**: REQ-001, REQ-002
- **Technology**: [Language, framework, library -- with rationale]
- **Location**: `src/[path]`
- **Interfaces**:
  - Input: [What it receives]
  - Output: [What it produces]
- **Dependencies**: [What it depends on]

### Component 2: [Component Name]

- **Purpose**: [What this component does]
- **Requirements Addressed**: REQ-003, REQ-NF-001
- **Technology**: [Language, framework, library -- with rationale]
- **Location**: `src/[path]`
- **Interfaces**:
  - Input: [What it receives]
  - Output: [What it produces]
- **Dependencies**: [What it depends on]

---

## Data Models

### [Model Name]

| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| id | string (UUID) | Yes | Unique identifier | Auto-generated, immutable |
| [field] | [type] | [Yes/No] | [Description] | [Constraints] |
| [field] | [type] | [Yes/No] | [Description] | [Constraints] |
| created_at | datetime (UTC) | Yes | Creation timestamp | Auto-set, immutable |
| updated_at | datetime (UTC) | Yes | Last update timestamp | Auto-set on modification |

**Requirements Addressed**: REQ-001
**Validation Rules**:
- [Rule 1: e.g., title must be 1-255 characters]
- [Rule 2: e.g., status must be one of: DRAFT, ACTIVE, ARCHIVED]

### [Model Name 2]

| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| [field] | [type] | [Yes/No] | [Description] | [Constraints] |

**Relationships**:
- [Relationship 1: e.g., belongs_to Model1 via foreign key]

---

## API Contracts

### [Endpoint Group]

#### [Operation Name]

- **Method**: GET | POST | PUT | PATCH | DELETE
- **Path**: `/api/v1/[resource]`
- **Requirements Addressed**: REQ-001
- **Authentication**: Required (CAC/PIV | Bearer Token | API Key)
- **Authorization**: [Role or permission required]
- **Request Body**:
```json
{
  "field": "type -- description"
}
```
- **Response** (200/201):
```json
{
  "field": "type -- description"
}
```
- **Error Responses**:
  - 400 Bad Request: Invalid input -- [when this occurs]
  - 401 Unauthorized: Missing or invalid credentials
  - 403 Forbidden: Insufficient permissions
  - 404 Not Found: Resource does not exist
  - 422 Unprocessable Entity: Validation failure -- [details]
  - 500 Internal Server Error: Unexpected failure -- [logged, not exposed]

---

## Sequence Diagrams

### [Flow Name]: [Brief Description]

```
User -> API Gateway: [HTTP Method] /[path]
API Gateway -> Auth: Validate credentials
Auth -> API Gateway: Authorized
API Gateway -> Service: [method](data)
Service -> Validator: validate(data)
Validator -> Service: validated_data
Service -> Repository: save(validated_data)
Repository -> Database: INSERT/UPDATE
Database -> Repository: record
Repository -> Service: entity
Service -> API Gateway: entity
API Gateway -> Audit Log: Log operation
API Gateway -> User: [status code] response
```

### [Flow Name 2]: [Brief Description]

```
[Sequence diagram for another key flow]
```

---

## Error Handling Strategy

| Error Type | HTTP Status | Handling Approach | User-Facing Message | Logging |
|-----------|-------------|-------------------|---------------------|---------|
| Validation error | 400 | Return field-level errors | "Invalid input: [details]" | WARN |
| Authentication failure | 401 | Return generic message | "Authentication required" | WARN |
| Authorization failure | 403 | Return generic message | "Access denied" | WARN + audit |
| Not found | 404 | Return generic message | "Resource not found" | INFO |
| Business logic error | 422 | Return specific message | "[Specific error]" | INFO |
| Server error | 500 | Log full error, return generic | "Internal server error" | ERROR + alert |

### Error Response Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Human-readable description",
    "details": [
      {
        "field": "title",
        "issue": "Must be between 1 and 255 characters"
      }
    ],
    "request_id": "uuid-for-tracing"
  }
}
```

---

## Security Considerations

- **Authentication**: [Method and implementation approach]
- **Authorization**: [RBAC/ABAC model, permission mapping]
- **Input Validation**: [Validation strategy at API boundary]
- **Data Protection**: [Encryption at rest and in transit]
- **Audit Logging**: [What events are logged, retention policy]
- **STIG Compliance**: [Applicable STIG rules and how they are met]
- **NIST Controls**: [Applicable NIST 800-53 controls mapped to components]

---

## Performance Considerations

- **Expected Load**: [Requests per second, concurrent users]
- **Latency Targets**: [p50, p95, p99 response times]
- **Caching Strategy**: [What is cached, TTL, invalidation approach]
- **Query Optimization**: [Indexes, query patterns, N+1 prevention]
- **Resource Limits**: [Connection pools, thread pools, memory bounds]

---

## Traceability Matrix

| Requirement | Design Component | Data Model | API Endpoint | Test Category |
|------------|-----------------|------------|-------------|---------------|
| REQ-001 | Component 1 | Model A | POST /resource | Unit + Integration |
| REQ-002 | Component 2 | Model A, Model B | GET /resource/:id | Unit + Integration |
| REQ-NF-001 | Component 1 | -- | All endpoints | Performance |
| REQ-NF-002 | Auth Component | -- | All endpoints | Security |

---

## Constitutional Compliance

### Simplicity Gate

- [ ] Junior developer can understand this design in under 5 minutes
- [ ] Fewer than 3 new concepts introduced
- [ ] No simpler approach exists that meets the same requirements
- [ ] No premature optimization

### Anti-Abstraction Check

- [ ] No unnecessary abstraction layers
- [ ] All abstractions serve at least 2 concrete use cases
- [ ] Frameworks/libraries used directly without wrapping

### Integration-First Testing

- [ ] Integration tests planned with real dependencies
- [ ] Mocks used only at true system boundaries
- [ ] Test data reflects realistic enterprise perational scenarios

### Complexity Tracking

[If any constitutional gate fails, document the justification here:]

| Gate | Violation | Justification |
|------|-----------|---------------|
| [Gate] | [What rule was bent] | [Why it was necessary] |

---

**Approval**:
- [ ] Tech Lead approved
- [ ] Security review completed
- [ ] Architecture review completed
- Date approved: [Date]
