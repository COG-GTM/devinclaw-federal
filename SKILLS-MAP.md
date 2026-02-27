# DevinClaw — Skills Map

## Pre-Loaded Use Cases (Enterprise Modernization)

| Skill | enterprise Scenario | Devin Use Case | Spoke(s) |
|-------|-------------|----------------|----------|
| `legacy-analysis` | Analyze 200+ enterprise applications | Investigate codebase | Cloud + DeepWiki |
| `plsql-migration` | Oracle PL/SQL → PostgreSQL | Parallelize migration | Cloud (batch) + API |
| `cobol-conversion` | COBOL → Java/Python/TypeScript | Code conversion | Cloud + CLI |
| `db-rationalization` | Rationalize 3,000 databases | Data & Analytics | Cloud (batch) |
| `security-scan` | STIG/NIST compliance | Automated security | Cloud + Review |
| `test-generation` | Add test coverage to legacy | Test coverage playbook | Cloud + CLI |
| `feature-dev` | New features from specs | Implement from spec | Cloud |
| `pr-review` | Code review at scale | Devin Review | Review (auto) |
| `incident-response` | Sentry/Datadog alerts | Auto-investigate alerts | API (webhook) |
| `parallel-migration` | Batch migrate 50+ files | Batch sessions | Cloud (Advanced) |
| `api-modernization` | REST→GraphQL, monolith→micro | Migration playbook | Cloud + CLI |
| `containerization` | Dockerize legacy apps | Containerize application | Cloud |
| `sdlc-validator` | Verify SDLC compliance | Custom validation | OpenClaw |
| `guardrail-auditor` | Audit guardrail violations | Enterprise API | OpenClaw |
| `skill-creator` | Create skills for new tasks | Self-evolving | OpenClaw + Cloud |

---

## Skill Detail Registry

### legacy-analysis
- **Path:** `skills/legacy-analysis/SKILL.md`
- **Trigger:** "analyze", "assess", "audit codebase", "modernization report", "technical debt"
- **Input:** Repository URL, application name, LOB, optional tech stack
- **Output:** Markdown modernization report with prioritized findings and phased roadmap
- **MCP Required:** DeepWiki
- **Spoke:** Devin Cloud + DeepWiki MCP
- **SDLC Phase:** Discovery / Assessment

### plsql-migration
- **Path:** `skills/plsql-migration/SKILL.md`
- **Trigger:** "migrate plsql", "oracle to postgres", "pl/sql", "stored procedure migration"
- **Input:** Oracle schema, target PostgreSQL version, procedure list
- **Output:** Converted PostgreSQL functions, migration scripts, comparison test results
- **MCP Required:** Database, DeepWiki
- **Spoke:** Devin Cloud (batch) + Devin API
- **SDLC Phase:** Implementation

### cobol-conversion
- **Path:** `skills/cobol-conversion/SKILL.md`
- **Trigger:** "convert cobol", "cobol to java", "cobol to python", "mainframe modernization"
- **Input:** COBOL sources, copybooks, target language, dialect
- **Output:** Converted source code, test suites, COBOL-to-target mapping file
- **MCP Required:** DeepWiki
- **Spoke:** Devin Cloud + Devin CLI
- **SDLC Phase:** Implementation

### db-rationalization
- **Path:** `skills/db-rationalization/SKILL.md`
- **Trigger:** "rationalize database", "consolidate schemas", "duplicate tables", "3000 databases"
- **Input:** Database connection details, schema inventory, consolidation goals
- **Output:** Rationalization plan, dedup report, idempotent migration scripts
- **MCP Required:** Database, DeepWiki
- **Spoke:** Devin Cloud (batch)
- **SDLC Phase:** Analysis + Implementation

### security-scan
- **Path:** `skills/security-scan/SKILL.md`
- **Trigger:** "security scan", "stig check", "nist compliance", "fedramp audit", "vulnerability scan"
- **Input:** Repository URL or path, compliance frameworks to check
- **Output:** Compliance report with findings, severity ratings, remediation PRs
- **MCP Required:** SonarQube, STIG Scanner, NIST Controls
- **Spoke:** Devin Cloud + Devin Review
- **SDLC Phase:** Verification / Audit

### test-generation
- **Path:** `skills/test-generation/SKILL.md`
- **Trigger:** "generate tests", "add test coverage", "write unit tests", "test suite", "coverage"
- **Input:** Repository, target modules, coverage threshold, test framework preference
- **Output:** Test suites, coverage report, test plan document
- **MCP Required:** DeepWiki
- **Spoke:** Devin Cloud + Devin CLI
- **SDLC Phase:** Testing

### feature-dev
- **Path:** `skills/feature-dev/SKILL.md`
- **Trigger:** "implement feature", "build from spec", "new feature", "add functionality"
- **Input:** Feature requirements (natural language or spec document), target repository
- **Output:** Implementation with tests, SDD spec, PR with Devin Review
- **MCP Required:** DeepWiki, GitHub/GitLab
- **Spoke:** Devin Cloud
- **SDLC Phase:** Full SDLC (Spec → Test → Build → Review)

### pr-review
- **Path:** `skills/pr-review/SKILL.md`
- **Trigger:** "review pr", "code review", "review pull request", "check my code"
- **Input:** PR URL or number, repository
- **Output:** Review comments, bug reports, auto-fix PRs
- **MCP Required:** GitHub/GitLab
- **Spoke:** Devin Review (auto)
- **SDLC Phase:** Review

### incident-response
- **Path:** `skills/incident-response/SKILL.md`
- **Trigger:** "sentry alert", "datadog alert", "production error", "incident", "outage"
- **Input:** Alert payload (Sentry/Datadog webhook), affected service
- **Output:** Root cause analysis, remediation PR, regression tests
- **MCP Required:** Sentry, Datadog, GitHub/GitLab
- **Spoke:** Devin API (webhook)
- **SDLC Phase:** Maintenance / Response

### parallel-migration
- **Path:** `skills/parallel-migration/SKILL.md`
- **Trigger:** "batch migrate", "parallel migration", "migrate 50 files", "mass migration"
- **Input:** Migration manifest (file list, transformation rules), batch size
- **Output:** Batch session results, per-file PRs, aggregate status report
- **MCP Required:** DeepWiki, GitHub/GitLab
- **Spoke:** Devin Cloud (Advanced Devin batch)
- **SDLC Phase:** Implementation (at scale)

### api-modernization
- **Path:** `skills/api-modernization/SKILL.md`
- **Trigger:** "modernize api", "rest to graphql", "monolith to microservices", "api migration"
- **Input:** Existing API specs (OpenAPI/Swagger), target architecture, service boundaries
- **Output:** Modernized API code, OpenAPI specs, migration guide, integration tests
- **MCP Required:** DeepWiki, GitHub/GitLab
- **Spoke:** Devin Cloud + Devin CLI
- **SDLC Phase:** Implementation

### containerization
- **Path:** `skills/containerization/SKILL.md`
- **Trigger:** "dockerize", "containerize", "kubernetes", "container migration"
- **Input:** Application source, runtime requirements, target platform (Docker/K8s)
- **Output:** Dockerfile, docker-compose.yml, K8s manifests, CI/CD pipeline config
- **MCP Required:** DeepWiki
- **Spoke:** Devin Cloud
- **SDLC Phase:** Implementation / Deployment

### sdlc-validator
- **Path:** `skills/sdlc-validator/SKILL.md`
- **Trigger:** "validate sdlc", "check compliance", "sdlc audit", "verify completion"
- **Input:** Task ID or session ID, expected SDLC artifacts
- **Output:** SDLC compliance report (pass/fail per gate)
- **MCP Required:** GitHub/GitLab, Devin Enterprise API
- **Spoke:** OpenClaw (internal)
- **SDLC Phase:** Governance

### guardrail-auditor
- **Path:** `skills/guardrail-auditor/SKILL.md`
- **Trigger:** "audit guardrails", "check violations", "guardrail report", "compliance check"
- **Input:** Time range, session IDs (optional), violation severity filter
- **Output:** Guardrail violation report, trend analysis, remediation recommendations
- **MCP Required:** Devin Enterprise API
- **Spoke:** OpenClaw (internal)
- **SDLC Phase:** Governance

### skill-creator
- **Path:** `skills/skill-creator/SKILL.md`
- **Trigger:** Automatic — activates when no existing skill matches the user's request
- **Input:** User's natural language task description, available context
- **Output:** New SKILL.md, updated SKILLS-MAP.md, team notification
- **MCP Required:** DeepWiki, GitHub/GitLab
- **Spoke:** OpenClaw + Devin Cloud
- **SDLC Phase:** Meta / Self-Evolving

---

## Devin Use Case Gallery Mapping

Maps [docs.devin.ai/use-cases/gallery](https://docs.devin.ai/use-cases/gallery) to enterprise cenarios:

| Gallery Use Case | enterprise Application | DevinClaw Skill |
|-----------------|-----------------|-----------------|
| Auto-Triage Bugs via Linear | Jira ticket → auto-investigate enterprise ugs | `incident-response` |
| Daily Sentry Error Fixes | Overnight enterprise ystem error remediation | `incident-response` |
| Migrate 50 Files REST→GraphQL | enterprise API modernization at scale | `parallel-migration` + `api-modernization` |
| React 18→19 Upgrade Playbook | Framework upgrades across enterprise apps | `parallel-migration` |
| Add Unit Tests to Service | Test coverage for the enterprise mission-critical code | `test-generation` |
| Implement API from OpenAPI Spec | New enterprise ervice endpoints | `feature-dev` |
| Dockerize Application | Containerize enterprise legacy apps for cloud | `containerization` |
| Debug Bug Report E2E | Root cause analysis with DB access | `incident-response` |
| Figma to Code | enterprise UI modernization from designs | `feature-dev` |
| Auto-Investigate Datadog Alerts | enterprise perational monitoring | `incident-response` |
| Investigate Codebase | Legacy application assessment | `legacy-analysis` |
| Parallelize Migration | Batch Oracle PL/SQL conversions | `plsql-migration` + `parallel-migration` |
| Data & Analytics | Database rationalization and dedup | `db-rationalization` |

---

## Skill Routing Logic

OpenClaw uses the following routing algorithm:

```
1. Receive user input (natural language)
2. Extract intent keywords from input
3. Match keywords against skill trigger patterns (above)
4. If SINGLE match → route to that skill
5. If MULTIPLE matches → select highest-priority skill, chain others
6. If NO match → route to skill-creator meta-skill
7. skill-creator creates new skill → executes immediately
8. Update SKILLS-MAP.md with new skill entry
```

### Priority Order (when multiple skills match)

1. `security-scan` (security always takes priority)
2. `incident-response` (production issues are urgent)
3. Specific migration/conversion skills (`plsql-migration`, `cobol-conversion`, etc.)
4. `feature-dev` (general development)
5. `test-generation` (testing)
6. `pr-review` (review)
7. `sdlc-validator`, `guardrail-auditor` (governance)

---

## Self-Evolving

When a task doesn't match any skill:

1. `skill-creator` activates
2. Reads Devin docs + use case gallery
3. Reads DeepWiki codebase context
4. Creates new SKILL.md with complete workflow
5. Pushes to repo → updates this file
6. Team notification sent
7. New skill executes immediately

---

## Machine-Consumable Registry

For automated skill routing, arena configuration, and artifact validation, see:

- **`audit/skill-descriptors.json`** — Structured skill descriptors with triggers, risk levels, arena modes, MCP requirements, and hard gate mappings.
- **`audit/arena-config.json`** — Risk-based execution mode configuration (single-run vs. arena-run) per skill.
- **`audit/constitution-template.json`** — SDLC stage boundary definitions with required inputs/outputs and gate criteria.
