# Integration Details: How OpenClaw Drives Devin

## Overview

OpenClaw programmatically orchestrates Devin sessions through three integration surfaces:

1. **Devin v3 REST API** — session lifecycle, playbooks, knowledge, secrets, schedules
2. **DeepWiki MCP / Devin MCP** — knowledge queries without session overhead
3. **PR URLs + Devin Review** — independent verification and auto-fix

---

## 1. Devin v3 REST API

The v3 API is the primary integration surface. Legacy v1/v2 will be deprecated with notice.

### Authentication
- Use **service users** with RBAC for all automated workflows.
- Service users are created in the Devin Enterprise admin console.
- API key scopes: Organization API (`/v3/organizations/...`) or Enterprise API (`/v3/enterprise/...`).
- Attribute sessions with `create_as_user_id` when user-level accountability is required.

### Session Lifecycle
```
1. Create session (POST /v3/sessions)
   - Provide: prompt, playbook_id, repos, secrets, knowledge scope
   - Returns: session_id, status

2. Poll status (GET /v3/sessions/{id})
   - States: running, paused, completed, failed, escalated

3. Fetch messages (GET /v3/sessions/{id}/messages)
   - Returns: timestamped message history including artifacts

4. Collect artifacts
   - Extract PR URLs, file outputs, evidence packs from messages

5. Register results in OpenClaw artifact registry
```

### Scheduled Sessions
For lights-out operations (nightly tests, weekly security scans, health digests):
- Use the Devin v3 schedule API to create recurring sessions.
- Each scheduled session inherits the playbook, repos, secrets, and knowledge scope.
- OpenClaw monitors scheduled session completions and routes results to the appropriate notification channel.

### Secret Management
- Use **session-scoped secrets** for automation workflows — limits blast radius.
- Never store static secrets in OpenClaw configuration files.
- Secrets are injected at session creation time via the v3 API `secrets` parameter.
- Rotate credentials on a schedule; never embed secrets in playbooks or knowledge entries.

---

## 2. DeepWiki MCP / Devin MCP

### Two-Tier Knowledge Access

| Tier | MCP Server | Auth | Repos | Use Case |
|------|-----------|------|-------|----------|
| **Fast understanding** | DeepWiki MCP (`mcp.deepwiki.com/mcp`) | None | Public only | Quick repo assessment, architecture overview, Q&A |
| **Full understanding** | Devin MCP (`mcp.devin.ai/mcp`) | Devin API key | Public + Private | Deep analysis of private enterprise epos |

### MCP Tools Available
Both servers expose the same tool surface:
- `read_wiki_structure` — get the knowledge graph structure for a repo
- `read_wiki_contents` — read specific wiki pages/sections
- `ask_question` — natural language Q&A against the indexed codebase

### Practical enterprise Workflow
```
Intake: "Assess repo X for security + modernization readiness"

Step 1 (cheap, fast):
  OpenClaw calls Devin MCP → read_wiki_structure
  → Get initial system map, major subsystems, tech stack

Step 2 (cheap, fast):
  OpenClaw calls Devin MCP → ask_question
  → "What are the critical integration points?"
  → "Where is business logic embedded in stored procedures?"
  → "What are the known security concerns?"

Step 3 (expensive, high-fidelity):
  Based on MCP answers, OpenClaw launches parallel Devin sessions
  with playbooks specialized per identified hotspot.
```

### Why MCP Matters for Portability
MCP is a standard integration boundary. Any orchestrator (OpenClaw, Personnel and Leave Management, or a custom pipeline) can query repo intelligence using the same tool shape. This avoids hard-coding Devin-specific APIs for knowledge queries — the orchestrator remains portable.

---

## 3. PR URLs + Devin Review

### Integration Pattern
1. Devin session completes implementation → opens PR on GitHub/GitLab.
2. OpenClaw receives PR URL from session messages.
3. Devin Review auto-triggers on PR (configurable: on open, on commit, on ready-for-review).
4. Devin Review produces:
   - Smart diff organization with copy/move detection
   - Bug Catcher findings (bugs + flags, severity, confidence)
   - GitHub-compatible comments and approval recommendations
5. If auto-fix is enabled: Devin Review can propose and apply fixes for Devin-authored PRs.
6. OpenClaw collects review findings as part of the evidence pack.

### Constraints
- Devin Review will **not** create commits or comments as a user without explicit initiation.
- In "lights-out" (autonomous) mode, the PR workflow should use:
  - A **service user** with explicit merge permissions, and/or
  - PR bot workflows that are explicitly enabled and governed in repo settings.
- Human approval is still required for merge in high-risk skills (security-scan, db-rationalization, incident-response).

### Review Configuration
- Place a `REVIEW.md` file in the repo root to customize review behavior.
- Place an `AGENTS.md` file in the repo root for agent-specific instructions.
- Devin Review respects both files for context-aware review.

---

## 4. Artifact Contract Enforcement (OpenClaw Orchestrator)

OpenClaw rejects "done" messages that do not include required deliverables:

### Enforcement Rules
```
For every completed session, OpenClaw checks:

1. Required files present:
   - spec.md + spec.json (if spec stage was executed)
   - test_summary.json (if tests were run)
   - review_findings.json (if PR was reviewed)
   - evidence-pack.json (always required)

2. Evidence pack validation:
   - All artifact hashes are present and verifiable
   - Verification gates show pass/fail for each required gate
   - No required gate is missing from the evidence
   - Escalation records are present if any gate failed

3. Required links:
   - PR URL (if code changes were made)
   - Devin Review URL (if review was conducted)
   - Session URL (always)

4. If any check fails:
   - Session is NOT marked as complete
   - OpenClaw creates a follow-up session to address the gap
   - The gap is logged in the audit trail
```

### Poll + Correlate Pattern
Since Devin v3 does not currently provide push webhooks for all events, OpenClaw uses a poll-based pattern:

```
1. Create session via v3 API
2. Poll session status every 30 seconds
3. On status=completed: fetch messages, extract artifacts
4. Validate artifact contract
5. If valid: register in artifact registry, update audit trail
6. If invalid: create remediation session or escalate
7. For arena-run: wait for all N sessions, then run divergence check
```

---

## 5. Service User Architecture

### Recommended Setup for the enterprise Deployment

| Service User | Purpose | Permissions |
|-------------|---------|-------------|
| `devinclaw-orchestrator` | OpenClaw → Devin API calls | Create sessions, read messages, manage knowledge |
| `devinclaw-reviewer` | Automated PR review triggers | Read repos, create review comments |
| `devinclaw-deployer` | CI/CD pipeline integration | Create sessions with deploy playbooks |
| `devinclaw-scheduler` | Scheduled session management | Create/manage scheduled sessions |

### RBAC Principles
- **Least privilege**: Each service user has only the permissions required for its function.
- **Separation of duties**: The orchestrator cannot merge PRs. The deployer cannot modify knowledge.
- **Auditability**: All API calls are attributed to specific service users with timestamps.
- **Rotation**: Service user API keys rotate on a 90-day cycle (or per agency policy).

---

*This integration architecture ensures OpenClaw and Devin operate as complementary layers — orchestration and governance on one side, execution and verification on the other — with clear boundaries, standard interfaces, and auditable handoffs.*
