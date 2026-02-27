# DevinClaw Tools Reference

This document catalogs every MCP server, Devin execution spoke, and API endpoint available in the DevinClaw framework. Tools are organized by layer: OpenClaw orchestration and Devin execution.

---

## MCP Servers — OpenClaw Layer

These MCP servers provide the orchestration layer with access to external systems, data sources, and infrastructure. They run within the OpenClaw process and are available to the routing engine, guardrail evaluator, and skill executor.

| MCP Server | Transport | Purpose | Key Capabilities |
|------------|-----------|---------|------------------|
| `deepwiki-mcp` | stdio | Codebase knowledge management | Index repositories, semantic search across codebases, retrieve contextual documentation, maintain cross-session memory, track architectural decisions |
| `filesystem-mcp` | stdio | Secure file operations | Read/write files within session sandboxes, enforce path restrictions, maintain file operation audit log, support atomic writes |
| `git-mcp` | stdio | Version control operations | Clone, branch, commit, merge with full audit logging; GPG signing enforcement; diff generation; history traversal |
| `gitlab-mcp` | SSE | GitLab platform integration | Create/update merge requests, trigger pipelines, manage issues, read CI/CD status, post review comments, manage labels and milestones |
| `postgres-mcp` | stdio | Database introspection | Schema discovery, table/column enumeration, constraint mapping, migration script validation, query plan analysis, data type compatibility checks |
| `jira-mcp` | SSE | Issue tracking integration | Read/update Jira tickets, transition workflows, attach artifacts, link issues to MRs, query sprint boards |
| `confluence-mcp` | SSE | Documentation platform | Read/write Confluence pages, attach session artifacts, update architecture decision records, manage space hierarchies |
| `vault-mcp` | SSE | Secrets management | Retrieve secrets for session execution, rotate credentials, validate secret policies, audit secret access |
| `artifactory-mcp` | SSE | Artifact repository | Push/pull build artifacts, validate checksums, manage Docker images, enforce retention policies |
| `sonarqube-mcp` | SSE | Code quality platform | Retrieve quality gate results, fetch issue lists, compare quality profiles, validate coverage metrics |

### MCP Server Configuration

MCP servers are registered in `config/mcp-servers.json`:

```json
{
  "mcpServers": {
    "deepwiki-mcp": {
      "command": "npx",
      "args": ["-y", "@anthropic/deepwiki-mcp"],
      "env": {
        "DEEPWIKI_INDEX_PATH": "${WORKSPACE}/deepwiki-index",
        "DEEPWIKI_MODEL": "devin"
      }
    },
    "filesystem-mcp": {
      "command": "npx",
      "args": ["-y", "@anthropic/filesystem-mcp"],
      "env": {
        "ALLOWED_PATHS": "${WORKSPACE},${SESSION_DIR}",
        "AUDIT_LOG": "${SESSION_DIR}/fs-audit.jsonl"
      }
    },
    "git-mcp": {
      "command": "npx",
      "args": ["-y", "@anthropic/git-mcp"],
      "env": {
        "GPG_SIGNING": "required",
        "AUDIT_LOG": "${SESSION_DIR}/git-audit.jsonl"
      }
    },
    "gitlab-mcp": {
      "url": "${GITLAB_MCP_URL}",
      "transport": "sse",
      "headers": {
        "Authorization": "Bearer ${GITLAB_TOKEN}"
      }
    },
    "postgres-mcp": {
      "command": "npx",
      "args": ["-y", "@anthropic/postgres-mcp"],
      "env": {
        "DATABASE_URL": "${DATABASE_URL}",
        "READ_ONLY": "true"
      }
    }
  }
}
```

---

## MCP Servers — Devin Layer

These MCP servers bridge the OpenClaw orchestrator to Devin's execution capabilities. They translate orchestration commands into Devin-native operations.

| MCP Server | Transport | Purpose | Key Capabilities |
|------------|-----------|---------|------------------|
| `devin-cloud-mcp` | SSE | Parallel cloud session management | Spawn sessions (up to 100+ concurrent), monitor execution progress, collect artifacts, manage session lifecycle, aggregate results across parallel runs |
| `devin-cli-mcp` | stdio | Local/air-gapped execution | Run Devin locally without external network, manage local model cache, execute in SCIF-compatible mode, support disconnected operation |
| `devin-api-mcp` | SSE | REST API bridge | Submit tasks via Devin API, poll session status, retrieve session artifacts, manage API keys and rate limits, support webhook callbacks |
| `devin-review-mcp` | SSE | Automated code review | Trigger PR reviews, retrieve review findings, manage finding lifecycle (open/accepted/resolved), configure review rules, post inline comments |
| `stig-scanner-mcp` | stdio | DISA STIG compliance | Run SCAP benchmarks, parse XCCDF results, map findings to STIG IDs (V-220629 through V-220641), generate remediation scripts, produce compliance reports |
| `nist-controls-mcp` | stdio | NIST 800-53 validation | Validate control implementations, map code changes to control families, generate control assessment evidence, track POA&M items |
| `sbom-mcp` | stdio | Software Bill of Materials | Generate SBOM in CycloneDX/SPDX formats, track component versions, validate license compliance, detect known vulnerabilities |
| `ironbank-mcp` | SSE | DoD Iron Bank integration | Validate container images against Iron Bank hardening guide, pull approved base images, submit hardening manifests |

---

## Devin Execution Spokes

Spokes are the five modalities through which Devin executes work. OpenClaw selects the appropriate spoke(s) based on task requirements, security classification, and deployment context.

| Spoke | Mode | Authorization | Concurrency | Network | Use Cases |
|-------|------|---------------|-------------|---------|-----------|
| **Devin Cloud** | Remote sandboxed VMs | Commercial + GovCloud | 100+ parallel sessions | Full internet | Batch modernization campaigns, large-scale COBOL migration, fleet-wide STIG remediation, mass test generation, parallel vulnerability scanning |
| **Devin CLI** | Local terminal process | On-premises authorized | 1 per terminal | Air-gapped capable | SCIF operations, classified workloads, disconnected development, local prototyping, IL6 environments |
| **Devin API** | REST endpoint | API key authenticated | Rate-limited (100 req/min) | HTTPS only | CI/CD pipeline integration, scheduled batch jobs, programmatic task submission, automated nightly runs, webhook-driven workflows |
| **Devin Review** | PR webhook listener | GitLab/GitHub integration | 1 per MR/PR | HTTPS only | Automated pull request review, STIG compliance checking, code quality enforcement, architectural drift detection, security finding triage |

### Spoke Selection Matrix

OpenClaw uses this matrix to automatically select the appropriate spoke:

| Scenario | Primary Spoke | Fallback Spoke | Rationale |
|----------|---------------|----------------|-----------|
| Batch migration (100+ files) | Cloud | API | Maximizes parallelism |
| Single file fix | API | CLI | Lightweight, fast |
| Air-gapped environment | CLI | — | Only option without network |
| Interactive development | CLI | CLI | Developer-in-the-loop |
| PR compliance check | Review | API | Webhook-native |
| CI/CD pipeline stage | API | Cloud | Pipeline integration |
| Classified workload (IL6) | CLI | — | Authorization boundary |
| Large refactor with review | Cloud + Review | API + Review | Build then review |

---

## APIs

### Devin REST API

Base URL: `https://api.devin.ai/v1` (Commercial) | `https://api.devin.gov/v1` (GovCloud)

| Endpoint | Method | Purpose | Request Body | Response |
|----------|--------|---------|-------------|----------|
| `/sessions` | POST | Create a new Devin session | `{ "task": "string", "skill": "string", "config": {} }` | `{ "session_id": "uuid", "status": "queued" }` |
| `/sessions/{id}` | GET | Get session status and details | — | `{ "session_id": "uuid", "status": "running\|completed\|failed", "progress": 0-100 }` |
| `/sessions/{id}/artifacts` | GET | Retrieve session output artifacts | — | `{ "artifacts": [{ "name": "string", "url": "string", "type": "string" }] }` |
| `/sessions/{id}/cancel` | POST | Cancel a running session | — | `{ "session_id": "uuid", "status": "cancelled" }` |
| `/sessions/{id}/logs` | GET | Stream session execution logs | — | Server-Sent Events stream |
| `/reviews` | POST | Submit a PR for Devin Review | `{ "repo": "string", "pr_number": int, "rules": [] }` | `{ "review_id": "uuid", "status": "queued" }` |
| `/reviews/{id}` | GET | Get review status and findings | — | `{ "review_id": "uuid", "findings": [], "status": "completed" }` |
| `/health` | GET | Platform health check | — | `{ "status": "healthy", "version": "string" }` |

### OpenClaw Internal API

Base URL: `http://localhost:8420/api/v1` (local orchestrator)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/tasks` | POST | Submit a new task to OpenClaw |
| `/tasks/{id}` | GET | Get task status, progress, and audit trail |
| `/tasks/{id}/guardrails` | GET | Get guardrail evaluation results for a task |
| `/skills` | GET | List all available skills |
| `/skills/{name}` | GET | Get skill definition and metadata |
| `/skills` | POST | Register a new skill |
| `/sessions` | GET | List active Devin sessions managed by OpenClaw |
| `/sessions/{id}/escalate` | POST | Manually trigger escalation for a session |
| `/config` | GET | Get current OpenClaw configuration |
| `/config/guardrails` | PUT | Update guardrail thresholds (within allowed ranges) |
| `/audit/{session_id}` | GET | Retrieve full audit trail for a session |
| `/deepwiki/search` | POST | Semantic search across indexed codebases |
| `/deepwiki/index` | POST | Trigger re-indexing of a repository |
| `/health` | GET | OpenClaw health and dependency status |

### Authentication

All API calls require authentication:

| API | Auth Method | Header |
|-----|------------|--------|
| Devin API | API Key | `Authorization: Bearer <DEVIN_API_KEY>` |
| OpenClaw API | mTLS + Session Token | `X-Session-Token: <token>` |
| GitLab MCP | Personal Access Token | Configured in MCP server env |
| Vault MCP | AppRole | Configured in MCP server env |

### Rate Limits

| API | Limit | Window | Burst |
|-----|-------|--------|-------|
| Devin API (Commercial) | 100 requests | Per minute | 20 |
| Devin API (GovCloud) | 50 requests | Per minute | 10 |
| OpenClaw Internal | 1000 requests | Per minute | 100 |
| Devin Review | 20 reviews | Per hour | 5 |

---

## Verification & Governance Artifacts

These configuration files govern the DevinClaw verification system and are consumed by the OpenClaw orchestrator at runtime:

| File | Purpose |
|------|---------|
| `audit/arena-config.json` | Risk classification per skill, arena execution mode (single-run vs. arena-run), session counts, safety-critical overrides |
| `audit/constitution-template.json` | SDLC stage boundary definitions with required inputs, outputs, and gate criteria at each stage transition |
| `audit/skill-descriptors.json` | Machine-consumable skill registry with triggers, risk levels, MCP requirements, and hard gate mappings |
| `audit/artifact-schemas/evidence-pack.schema.json` | JSON Schema for evidence-pack.json — validates artifact inventory, verification results, and escalation records |
| `audit/artifact-schemas/verification-record.schema.json` | JSON Schema for verification records produced by the divergence detection system |

OpenClaw validates all task artifacts against these schemas before accepting a "done" status. See [docs/VERIFICATION-SYSTEM.md](docs/VERIFICATION-SYSTEM.md) for the complete verification architecture.

---

## Tool Chain per Skill

Each skill declares the tools it requires. OpenClaw provisions the tool chain before session execution begins.

| Skill | Required MCP Servers | Primary Spoke | Additional Tools |
|-------|---------------------|---------------|-----------------|
| `cobol-to-java` | deepwiki, git, filesystem | Cloud | GnuCOBOL compiler, JDK 17, Maven |
| `stig-hardening` | stig-scanner, git, filesystem | Cloud or CLI | OpenSCAP, SCAP benchmarks |
| `ato-documentation` | deepwiki, confluence, git | Cloud | Pandoc, LaTeX |
| `api-modernization` | deepwiki, git, postgres | Cloud | OpenAPI Generator, Postman CLI |
| `database-migration` | postgres, git, filesystem | Cloud | Flyway, pgLoader, ora2pg |
| `container-packaging` | ironbank, git, sbom | Cloud | Docker, Podman, Trivy |
| `zero-trust-network` | nist-controls, git | Cloud or CLI | OPA/Rego, Istio CLI |
| `cicd-pipeline` | gitlab, git, sonarqube | API | GitLab Runner, Helm |
| `test-generation` | deepwiki, git, filesystem | Cloud | pytest, JUnit, Jest, Playwright |
| `documentation-gen` | deepwiki, confluence, git | Cloud | Sphinx, MkDocs, JSDoc |
| `vulnerability-remediation` | sbom, git, sonarqube | Cloud | Trivy, Grype, Snyk CLI |
| `infrastructure-as-code` | vault, git, filesystem | Cloud or CLI | Terraform, Ansible, AWS CLI |
| `508-accessibility` | deepwiki, git, filesystem | Cloud | axe-core, pa11y, Lighthouse |
| `data-pipeline` | postgres, git, filesystem | Cloud | Apache Spark, dbt, Airflow CLI |
| `incident-response` | jira, git, vault | CLI | Splunk CLI, YARA, Volatility |
