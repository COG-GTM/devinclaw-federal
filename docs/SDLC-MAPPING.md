# SDLC Mapping — Where Each Tool Fits

## Full Software Development Lifecycle Coverage

DevinClaw provides AI-augmented tooling across every phase of the SDLC. No phase is left to manual processes alone.

| Phase | Tool | Capability | Human Role |
|-------|------|-----------|------------|
| **Requirements** | OpenClaw + Jira MCP | Natural language → structured requirements. Pull Jira tickets directly into the workflow. | Review and approve requirements |
| **Specification** | SDD Templates + DeepWiki | Spec-Driven Design generates specification documents with full codebase context from DeepWiki. | Review spec accuracy |
| **Design** | DeepWiki + Devin Cloud | Architecture design informed by existing codebase analysis. Dependency mapping, component design. | Approve architecture decisions |
| **Implementation** | Devin Cloud / CLI / API | Autonomous implementation from spec. 100+ parallel sessions for large-scale work. | Monitor progress, unblock issues |
| **Testing** | TDD Templates + Devin | Tests written BEFORE code (TDD). Automated test generation, coverage enforcement. | Review test completeness |
| **Code Review** | Devin Review | Automatic PR review with bug detection, severity classification, auto-fix suggestions. | Final approval on PRs |
| **Security** | Compliance Suite | STIG/NIST/FedRAMP scanning. Zero Trust enforcement. | Review security findings |
| **Deployment** | Devin API + CI/CD | Automated pipeline integration via webhooks. Containerized deployments. | Approve production releases |
| **Monitoring** | Sentry/Datadog MCPs | Auto-investigate production alerts. Open fix PRs for detected issues. | Prioritize incident response |
| **Knowledge Capture** | Advanced Devin + DeepWiki | Session analysis → playbook generation → knowledge base growth. System improves continuously. | Review and curate knowledge |

## SDLC Phase Detail

### Phase 1: Requirements Intake
```
Jira Ticket → OpenClaw (via Jira MCP) → Parse requirements → Map to skill
```
- OpenClaw receives task from Jira, Slack, Teams, or direct chat
- Natural language is parsed into structured task definition
- SKILLS-MAP.md is consulted to find the matching workflow
- If no match: skill-creator generates a new skill

### Phase 2: Specification (SDD)
```
Task + DeepWiki Context → SDD Template → spec.md + design.md
```
- DeepWiki provides full codebase context (architecture, dependencies, conventions)
- SDD templates ensure consistent specification format
- Output: constitution.md, spec.md, design.md, tasks.md
- Spec is the single source of truth for all downstream work

### Phase 3: Design
```
spec.md + DeepWiki Analysis → Architecture Decision → design.md
```
- DeepWiki analyzes existing code patterns and architecture
- Design decisions documented as ADRs
- Target architecture defined with traceability to requirements

### Phase 4: Implementation
```
tasks.md → Devin Sessions (1 to 100+) → Code + Tests
```
- Task breakdown from SDD drives session creation
- Single tasks → Devin CLI or Cloud (one session)
- Batch tasks → Advanced Devin batch sessions (50-100+ parallel)
- Each session receives: spec, tests, context, transformation rules
- Devin builds from spec, runs tests, creates PR

### Phase 5: Testing (TDD)
```
Test Plan → Test Stubs (Red) → Implementation (Green) → Refactor → Coverage Report
```
- Tests are written BEFORE implementation (TDD cycle)
- Coverage thresholds enforced per code category
- Migration code requires 100% equivalence coverage
- Security tests included for all STIG-relevant controls

### Phase 6: Code Review
```
PR Created → Devin Review Auto-Triggers → Bug Catch → Auto-Fix → Human Approval
```
- Devin Review runs automatically on every PR
- Smart diff organization groups related changes logically
- Bug catcher classifies findings by severity (CRITICAL → investigate → informational)
- Auto-fix proposes and applies fixes for detected bugs
- Human reviewer gives final approval

### Phase 7: Security
```
Code → STIG/NIST Scan → Findings Report → Remediation → Rescan
```
- Automated scanning against federal security controls
- CAT I findings block deployment
- Zero Trust middleware templates included

### Phase 8: Deployment
```
Approved PR → CI/CD Pipeline → Container Build → Deploy → Smoke Test
```
- Devin API integrates with CI/CD via webhooks
- Containerized deployments with hardened base images
- Blue/green or canary deployment strategies
- Rollback capability required for all deployments

### Phase 9: Monitoring & Incident Response
```
Sentry/Datadog Alert → Devin API (webhook) → Auto-Investigate → Fix PR
```
- Production alerts trigger Devin sessions automatically
- Root cause analysis with full codebase context
- Fix PRs opened by morning for overnight errors
- Devin Review validates the fix before merge

### Phase 10: Knowledge Capture
```
Completed Session → Advanced Devin Analysis → Playbook Update → Knowledge Growth
```
- Every session is analyzed for patterns and learnings
- Successful patterns become reusable playbooks
- Failed patterns become documented pitfalls
- DeepWiki re-indexes with every codebase change
- The system compounds: Session 1 takes 4 hours, Session 100 takes 45 minutes
