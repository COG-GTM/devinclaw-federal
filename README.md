# DevinClaw Federal

**Standalone, production-grade AI modernization orchestrator for federal government systems — deployable via `docker-compose up`.**

DevinClaw Federal is a fully self-contained orchestration platform that automates the transformation of legacy enterprise systems (COBOL, PL/SQL, mainframe) into modern, cloud-native architectures while ensuring compliance with federal security standards (STIG, NIST 800-53, FedRAMP, FISMA, EO 14028, Zero Trust).

> **Architecture Shift**: This project has been transformed from an OpenClaw-dependent framework into a **standalone orchestrator** with its own FastAPI backend, Next.js dashboard, embedded Devin CLI terminal, and full API surface — no external orchestrator dependency required.

---

## What It Does

DevinClaw Federal turns natural language into executed, tested, reviewed, and audited code — with federal compliance at every step. You say what needs to happen. The system handles the rest — from specification to deployment — producing ATO-ready evidence packs and STIG-mapped audit trails.

```
"Migrate the notification PL/SQL procedures to PostgreSQL"

-> Routes to skill via built-in Skill Router
-> Enforces guardrails (10 hard gates)
-> Selects optimal Devin spoke (Cloud/CLI/API/Review/IDE)
-> Determines arena mode (single-run or multi-session verification)
-> Spawns parallel build sessions via Devin API
-> Reviews every PR automatically (Devin Review)
-> Runs STIG/NIST compliance validation
-> Validates the full SDLC lifecycle (10 phases)
-> Generates ATO evidence pack with SHA-256 tamper evidence
-> Updates the knowledge base for compound learning
-> Next task starts smarter than the last
```

---

## Standalone Architecture

DevinClaw Federal is a self-contained platform with four services orchestrated via Docker Compose:

```
                    +----------------------+
                    |     ENGINEER         |
                    |  (Natural Language)   |
                    +----------+-----------+
                               |
              +----------------v----------------+
              |     DEVINCLAW DASHBOARD         |
              |     Next.js + Embedded Terminal  |
              |     Port 3000                    |
              +----------------+----------------+
                               |
              +----------------v----------------+
              |     DEVINCLAW API (FastAPI)      |
              |     Port 8420                    |
              |                                 |
              |  +-----------------------------+|
              |  | Orchestration Engine         ||
              |  |  - Skill Router             ||
              |  |  - Spoke Selector           ||
              |  |  - Guardrail Enforcer       ||
              |  |  - Arena Executor           ||
              |  |  - SDLC Validator           ||
              |  |  - Session Manager          ||
              |  |  - Audit Writer             ||
              |  |  - Memory Manager           ||
              |  +-----------------------------+|
              |                                 |
              |  +-----------------------------+|
              |  | Auth & Multi-Tenancy        ||
              |  |  - JWT with IP binding      ||
              |  |  - RBAC (admin/eng/viewer)  ||
              |  |  - Zero Trust middleware     ||
              |  |  - Audit logging            ||
              |  +-----------------------------+|
              |                                 |
              |  +-----------------------------+|
              |  | CLI Bridge + Terminal        ||
              |  |  - PTY subprocess mgmt      ||
              |  |  - WebSocket streaming       ||
              |  |  - Auto-retry on crash       ||
              |  +-----------------------------+|
              |                                 |
              |  +-----------------------------+|
              |  | Scheduler (arq + Redis)     ||
              |  |  - Cron-based recurring      ||
              |  |  - Webhook-triggered         ||
              |  |  - Built-in nightly scans    ||
              |  +-----------------------------+|
              +----+------------------+---------+
                   |                  |
          +--------v------+   +------v--------+
          |  PostgreSQL   |   |    Redis       |
          |  Port 5432    |   |  Port 6379     |
          +---------------+   +---------------+
```

### What Changed from OpenClaw-Dependent to Standalone

| Aspect | Before (OpenClaw) | After (Standalone) |
|--------|-------------------|-------------------|
| Orchestrator | External OpenClaw service | Built-in FastAPI backend |
| Skill Routing | OpenClaw API | `src/core/skill_router.py` |
| Guardrails | OpenClaw enforcement | `src/core/guardrail_enforcer.py` |
| SDLC Validation | OpenClaw validation | `src/core/sdlc_validator.py` |
| Session Management | Manual CLI | `src/core/session_manager.py` |
| Arena Verification | Conceptual | `src/core/arena_executor.py` |
| Audit Trail | File-based scripts | `src/core/audit_writer.py` + API |
| Authentication | None | JWT + Zero Trust + RBAC |
| Dashboard | None | Next.js with embedded terminal |
| Deployment | `setup.sh` + OpenClaw | `docker-compose up` |
| API Surface | None | Full REST API + WebSocket |
| Scheduling | None | arq (Redis-backed) scheduler |
| Memory System | None | Four-scope compound learning |

---

## Quick Start

```bash
git clone <this-repo>
cd devinclaw-federal

# Option 1: Docker Compose (recommended)
docker-compose up -d

# Option 2: Local development
make dev
```

The system starts four services:
- **Dashboard**: http://localhost:3000 — Next.js frontend with terminal
- **API**: http://localhost:8420 — FastAPI backend with Swagger docs at /docs
- **PostgreSQL**: localhost:5432 — persistent storage
- **Redis**: localhost:6379 — job scheduling and caching

**Prerequisites:** Docker + Docker Compose, or Python 3.12+ and Node.js 20+ for local dev.

**Environment Variables:**
```bash
DEVIN_API_KEY=your-devin-api-key    # From app.devin.ai
JWT_SECRET_KEY=change-in-production  # JWT signing secret
DATABASE_URL=postgresql+asyncpg://devinclaw:devinclaw@localhost:5432/devinclaw
REDIS_URL=redis://localhost:6379/0
```

---

## What Federal Adds to Base DevinClaw

| Capability | Base DevinClaw | DevinClaw Federal |
|-----------|---------------|-------------------|
| SDLC Governance | Yes | Yes |
| Parallel Execution | Yes | Yes |
| Self-Evolving Knowledge | Yes | Yes |
| **Standalone Orchestrator** | -- | **Yes** |
| **REST API + WebSocket** | -- | **Yes** |
| **Next.js Dashboard** | -- | **Yes** |
| **Docker Compose Deploy** | -- | **Yes** |
| STIG Mapping (CAT I/II/III) | -- | Yes |
| NIST 800-53 Rev 5 Controls | -- | Yes |
| FedRAMP Baseline Support | -- | Yes |
| ATO Evidence Pack Generation | -- | Yes |
| FISMA Compliance | -- | Yes |
| CVE Vulnerability Tracking | -- | Yes |
| FIPS 140-2 Crypto Enforcement | -- | Yes |
| Zero Trust (NIST 800-207) | -- | Yes |
| Iron Bank Container Compliance | -- | Yes |
| FAR 4.703 Evidence Retention | -- | Yes |

---

## API Surface

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register user + organization |
| POST | `/auth/login` | Authenticate, return JWT |
| POST | `/auth/logout` | Invalidate session |
| GET | `/auth/me` | Current user profile |
| POST | `/auth/api-keys` | Create API key |
| DELETE | `/auth/api-keys/{id}` | Revoke API key |

### Tasks
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/tasks` | Submit task (natural language) |
| GET | `/api/v1/tasks/{id}` | Task status + audit trail |
| GET | `/api/v1/tasks/{id}/guardrails` | Guardrail results |
| POST | `/api/v1/tasks/{id}/cancel` | Cancel task |
| GET | `/api/v1/tasks` | List tasks (paginated) |

### Sessions
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/sessions` | List Devin sessions |
| GET | `/api/v1/sessions/{id}` | Session detail + messages |
| POST | `/api/v1/sessions/{id}/escalate` | Escalate to human |

### Skills
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/skills` | List all skills |
| GET | `/api/v1/skills/{name}` | Skill definition |
| POST | `/api/v1/skills` | Register new skill |

### Compliance
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/compliance/dashboard` | Aggregate metrics |
| GET | `/api/v1/compliance/nist` | NIST 800-53 coverage |
| GET | `/api/v1/compliance/stig` | STIG findings |
| GET | `/api/v1/compliance/guardrails` | Violation summary |

### Audit
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/audit` | Searchable audit trail |
| GET | `/api/v1/audit/export` | Export JSON/CSV (SIEM) |
| GET | `/api/v1/audit/evidence-packs` | List evidence packs |
| GET | `/api/v1/audit/evidence-packs/{id}` | Download pack |

### Schedule
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/schedules` | Create scheduled task |
| GET | `/api/v1/schedules` | List schedules |
| DELETE | `/api/v1/schedules/{id}` | Remove schedule |
| GET | `/api/v1/schedules/{id}/runs` | Run history |

### Memory
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/memory` | List memory entries |
| POST | `/api/v1/memory` | Create entry |
| GET | `/api/v1/memory/search` | Semantic search |
| DELETE | `/api/v1/memory/{id}` | Remove entry |

### WebSocket
| Endpoint | Description |
|----------|-------------|
| `/ws/terminal/{session_id}` | Bidirectional CLI terminal |

### Health
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |

---

## Pre-Loaded Skills

15 skills covering federal enterprise modernization scenarios. Each skill is a complete workflow: specification -> tests -> build -> review -> compliance validation -> audit.

| Skill | What It Does |
|-------|-------------|
| `legacy-analysis` | Index and assess a codebase with DeepWiki. Produce modernization roadmap. |
| `plsql-migration` | Migrate Oracle PL/SQL to PostgreSQL. Type mapping, exception handling, batch parallel. |
| `cobol-conversion` | Convert COBOL to Java/Python/TypeScript. Preserve exact business logic. |
| `db-rationalization` | Analyze, deduplicate, and consolidate database portfolios. |
| `security-scan` | STIG/NIST/FedRAMP compliance scanning, CVE correlation, and auto-remediation. |
| `test-generation` | Generate comprehensive test suites for untested legacy code. |
| `feature-dev` | Build new features from requirements using SDD + TDD pipeline. |
| `pr-review` | Automated PR review via Devin Review. Bug catch, auto-fix. |
| `incident-response` | Auto-investigate production alerts, open fix PRs. |
| `parallel-migration` | Spawn 100+ parallel sessions for large-scale batch work. |
| `api-modernization` | SOAP to REST, REST to GraphQL, monolith to microservices. |
| `containerization` | Dockerize legacy apps. Multi-stage builds, K8s manifests, Iron Bank compliance. |
| `sdlc-validator` | Validate every task followed the full SDLC lifecycle. |
| `guardrail-auditor` | Monitor Devin Enterprise Guardrails API for policy violations. |
| `skill-creator` | **Meta-skill**: creates new skills when no match exists. Self-evolving system. |

---

## Every Task Follows the Same Lifecycle

```
1. INTAKE       -> Skill Router matches task to skill
2. GUARDRAILS   -> Guardrail Enforcer runs 10 hard gates (pre-execution)
3. SPOKE        -> Spoke Selector picks optimal Devin execution environment
4. ARENA        -> Arena Executor determines single-run vs multi-session verification
5. MEMORY       -> Memory Manager injects relevant context from prior sessions
6. EXECUTE      -> Session Manager launches Devin session(s) (1 to 100+ parallel)
7. MONITOR      -> Poll sessions until completion, collect artifacts
8. SDLC         -> SDLC Validator checks all 10 completion phases
9. EVIDENCE     -> Audit Writer generates evidence pack with SHA-256 hashing
10. LEARN       -> Memory Manager stores learnings for compound effect
```

If a task has no matching skill, the `skill-creator` meta-skill builds one, pushes it to the repo, and the whole team gains the capability.

---

## Verification System

DevinClaw Federal uses a multi-layered verification architecture to ensure every output is defensible, traceable, and predictably escalated when confidence is insufficient.

### Self-Verification Loop
Every skill runs a self-verification loop after completing its primary procedure: verify -> auto-fix -> re-verify -> escalate. This eliminates the "ship and hope" pattern that plagues autonomous AI systems.

### Arena Pattern (Divergence Detection)
For high-risk tasks (security scanning, database rationalization, incident response), DevinClaw Federal runs **multiple independent Devin sessions** with different playbook variants, then compares their outputs using a divergence scoring algorithm. If sessions disagree beyond a configurable threshold (default: 0.35), the system escalates to human review rather than silently choosing one output.

| Risk Level | Default Mode | Example Skills |
|------------|-------------|----------------|
| Critical | Arena (N=3) | security-scan, db-rationalization, incident-response |
| High | Arena (N=2) | legacy-analysis, plsql-migration, cobol-conversion |
| Medium | Single-run | feature-dev, test-generation, containerization |
| Low | Single-run | pr-review, sdlc-validator, guardrail-auditor |

### Evidence Packs
Every completed task produces an `evidence-pack.json` containing artifact hashes, verification gate results, test summaries, STIG findings, CVE scan results, NIST control mappings, and escalation records. These evidence packs are retained for the contract duration plus 3 years (FAR 4.703) and serve as the foundation for ATO evidence packages.

See [docs/VERIFICATION-SYSTEM.md](docs/VERIFICATION-SYSTEM.md) for the complete verification architecture.

---

## Federal Compliance

| Framework | Coverage |
|-----------|---------|
| NIST SP 800-53 Rev 5 | AC, AU, IA, SC, SI control families |
| NIST SP 800-207 | Zero Trust Architecture |
| DISA STIGs | All 18 security categories (CAT I/II/III severity classification) |
| FedRAMP | Low/Moderate/High baselines |
| FISMA | Annual assessment support, continuous monitoring |
| RMF | Risk Management Framework integration across lifecycle |
| CVE/NVD | Vulnerability tracking against National Vulnerability Database |
| FIPS 140-2 | Cryptographic module validation |
| EO 14028 | Improving the Nation's Cybersecurity |
| SOC 2 Type II | Devin Cloud platform |

Every session produces an immutable audit trail. See [SECURITY.md](SECURITY.md).

---

## MCP Integration

The DevinClaw API connects to external tools via Model Context Protocol:

**Orchestrator layer** (task intake + validation): Jira, Slack, Teams, GitHub, DeepWiki, PostgreSQL

**Devin layer** (execution): GitHub, Sentry, Datadog, SonarQube, databases

The orchestrator can independently verify what the executor did. See [docs/MCP-GUIDE.md](docs/MCP-GUIDE.md).

---

## Repository Structure

```
devinclaw-federal/
├── README.md              # This file
├── SOUL.md                # Identity, mission, values
├── GUARDRAILS.md          # Hard gates for all operations
├── TOOLS.md               # MCP servers and tool registry
├── SECURITY.md            # Federal compliance posture
├── SKILLS-MAP.md          # Skill -> enterprise scenario mapping
├── TEST-PLAN.md           # Comprehensive test suite
│
├── src/                   # Standalone backend (FastAPI)
│   ├── api/               # FastAPI application
│   │   ├── main.py        # App entry point, lifespan, middleware, routers
│   │   ├── routes/        # REST API endpoints
│   │   │   ├── auth.py    # Registration, login, JWT, API keys
│   │   │   ├── tasks.py   # Task submission and monitoring
│   │   │   ├── sessions.py # Devin session management
│   │   │   ├── skills.py  # Skill registry
│   │   │   ├── schedule.py # Scheduled/recurring tasks
│   │   │   ├── memory.py  # Four-scope memory system
│   │   │   ├── audit.py   # Audit trail + evidence packs
│   │   │   ├── compliance.py # NIST/STIG/FedRAMP dashboards
│   │   │   └── ws.py      # WebSocket terminal streaming
│   │   └── middleware/     # Security middleware
│   │       ├── zero_trust.py # Zero Trust request flow
│   │       ├── rbac.py    # Role-based access control
│   │       └── audit_log.py # Request logging (NIST AU-3)
│   ├── core/              # Orchestration engine
│   │   ├── orchestrator.py # Main 12-step orchestration loop
│   │   ├── skill_router.py # Keyword -> skill routing
│   │   ├── spoke_selector.py # Devin spoke selection matrix
│   │   ├── session_manager.py # Devin API client + session registry
│   │   ├── guardrail_enforcer.py # 10 hard gate enforcement
│   │   ├── sdlc_validator.py # 10-phase SDLC validation
│   │   ├── arena_executor.py # Multi-session divergence detection
│   │   └── audit_writer.py # SHA-256 hashed audit entries
│   ├── auth/              # Authentication & multi-tenancy
│   │   ├── models.py      # SQLAlchemy ORM (User, Org, APIKey, Session)
│   │   ├── jwt.py         # JWT creation/verification with IP binding
│   │   └── passwords.py   # bcrypt-12, 14+ char policy, lockout
│   ├── cli/               # Devin CLI bridge
│   │   ├── bridge.py      # PTY subprocess management
│   │   └── stream.py      # Real-time output streaming
│   ├── scheduler/         # Job scheduling
│   │   ├── scheduler.py   # arq (Redis-backed) scheduler
│   │   └── jobs.py        # Built-in scheduled jobs
│   ├── memory/            # Compound learning
│   │   └── memory_manager.py # Four-scope memory (session/user/org/project)
│   └── config.py          # Central configuration (Pydantic Settings)
│
├── dashboard/             # Next.js frontend
│   ├── src/app/           # App Router pages
│   │   ├── page.tsx       # Operations dashboard
│   │   └── terminal/page.tsx # Embedded CLI terminal
│   ├── package.json
│   └── next.config.js
│
├── docker-compose.yml     # One-command deployment
├── docker/                # Container images
│   ├── Dockerfile.api     # Python 3.12 FastAPI
│   ├── Dockerfile.dashboard # Node 20 + nginx
│   └── nginx.conf         # Reverse proxy with security headers
├── pyproject.toml         # Python dependencies
├── Makefile               # Dev/test/build/deploy targets
│
├── skills/                # 15 pre-loaded skills
│   ├── legacy-analysis/
│   ├── plsql-migration/
│   ├── cobol-conversion/
│   ├── db-rationalization/
│   ├── security-scan/
│   ├── test-generation/
│   ├── feature-dev/
│   ├── pr-review/
│   ├── incident-response/
│   ├── parallel-migration/
│   ├── api-modernization/
│   ├── containerization/
│   ├── sdlc-validator/
│   ├── guardrail-auditor/
│   └── skill-creator/
│
├── audit/                 # Guardrail config, SDLC checklist, arena config, artifact schemas
├── knowledge/             # Devin Knowledge entries
├── playbooks/             # Devin playbooks
├── compliance/            # STIG, NIST, FedRAMP, FISMA, RMF, Zero Trust
├── skills-parser/         # Convert skills -> Devin playbooks
└── docs/                  # Architecture, SDLC mapping, use cases, FAQ
```

---

## Development

```bash
# Install dependencies
pip install -e ".[dev]"

# Run API server
make dev-api

# Run dashboard
make dev-dashboard

# Run both
make dev

# Run tests
make test

# Lint
make lint

# Build Docker images
make build

# Deploy with Docker Compose
make deploy
```

---

## Documentation

| Document | What It Covers |
|----------|---------------|
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Full system architecture with data flow diagrams |
| [docs/SDLC-MAPPING.md](docs/SDLC-MAPPING.md) | Where each tool fits in the development lifecycle |
| [docs/USE-CASES.md](docs/USE-CASES.md) | Federal enterprise scenarios mapped to skills and Devin capabilities |
| [docs/QUICK-START.md](docs/QUICK-START.md) | 5-minute setup guide |
| [docs/MCP-GUIDE.md](docs/MCP-GUIDE.md) | How MCP servers connect the layers |
| [docs/SELF-EVOLVING.md](docs/SELF-EVOLVING.md) | How the system gets smarter over time |
| [docs/FAQ.md](docs/FAQ.md) | Common questions and answers |
| [docs/VERIFICATION-SYSTEM.md](docs/VERIFICATION-SYSTEM.md) | Divergence detection, arena pattern, evidence gating |

---

## Relationship to Base DevinClaw

DevinClaw Federal extends the [commercial DevinClaw framework](https://github.com/COG-GTM/devinclaw) with federal-specific compliance capabilities. The base framework provides the core SDLC governance, parallel execution, self-evolving knowledge, and verification systems. This federal variant adds:

- Standalone FastAPI backend (no external orchestrator dependency)
- Next.js dashboard with embedded Devin CLI terminal
- Docker Compose deployment
- Full REST API + WebSocket surface
- JWT authentication with Zero Trust and RBAC
- Redis-backed job scheduler
- Four-scope memory system for compound learning
- STIG severity classification and V-number mapping
- NIST 800-53 control family enforcement
- FedRAMP baseline authorization support
- ATO evidence pack generation
- FISMA annual assessment tooling
- RMF lifecycle integration
- CVE/NVD vulnerability correlation
- FIPS 140-2 cryptographic enforcement
- Iron Bank container compliance
- FAR 4.703 evidence retention

---

## The Compound Effect

```
Session 1:    4 hours  (full ramp-up, no context)
Session 10:   2 hours  (patterns known, playbooks established)
Session 50:   30 min   (deep domain knowledge, near-autonomous)
Session 100:  15 min   (human review only)
```

Every task makes the next one faster. After modernizing 200 federal applications, the framework encodes the collective knowledge of every migration, every edge case, every compliance finding, every lesson learned.

---

*Built with [Devin](https://devin.ai) • [DeepWiki](https://deepwiki.com) • [Cognition AI](https://cognition.ai)*
