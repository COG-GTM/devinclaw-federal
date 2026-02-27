# DevinClaw Federal

**Federal compliance AI modernization framework — extending [DevinClaw](https://github.com/COG-GTM/devinclaw) with full federal compliance capabilities.**

DevinClaw Federal builds on the commercial DevinClaw framework and adds STIG enforcement, NIST 800-53 control mapping, FedRAMP authorization support, ATO evidence generation, FISMA compliance, RMF integration, and CVE vulnerability management — all baked into every task lifecycle.

---

## What It Does

DevinClaw Federal turns natural language into executed, tested, reviewed, and audited code — with federal compliance at every step. You say what needs to happen. The system handles the rest — from specification to deployment — producing ATO-ready evidence packs and STIG-mapped audit trails.

```
"Migrate the notification PL/SQL procedures to PostgreSQL"

→ Indexes the codebase (DeepWiki)
→ Generates a specification (SDD)
→ Writes tests first (TDD)
→ Spawns 12 parallel build sessions (Devin)
→ Reviews every PR automatically (Devin Review)
→ Runs STIG/NIST compliance validation
→ Maps findings to CVE identifiers where applicable
→ Validates the full lifecycle was followed (OpenClaw)
→ Generates ATO evidence pack
→ Updates the knowledge base (Advanced Devin)
→ Next task starts smarter than the last
```

---

## What Federal Adds to Base DevinClaw

| Capability | Base DevinClaw | DevinClaw Federal |
|-----------|---------------|-------------------|
| SDLC Governance | ✅ | ✅ |
| Parallel Execution | ✅ | ✅ |
| Self-Evolving Knowledge | ✅ | ✅ |
| STIG Mapping (CAT I/II/III) | — | ✅ |
| NIST 800-53 Rev 5 Controls | — | ✅ |
| FedRAMP Baseline Support | — | ✅ |
| ATO Evidence Pack Generation | — | ✅ |
| FISMA Compliance | — | ✅ |
| RMF Integration | — | ✅ |
| CVE Vulnerability Tracking | — | ✅ |
| FIPS 140-2 Crypto Enforcement | — | ✅ |
| Zero Trust (NIST 800-207) | — | ✅ |
| Iron Bank Container Compliance | — | ✅ |
| FAR 4.703 Evidence Retention | — | ✅ |

---

## Quick Start

```bash
git clone <this-repo>
cd devinclaw-federal
chmod +x setup.sh
./setup.sh    # Installs OpenClaw, loads skills, configures APIs
openclaw      # Start modernizing
```

**Prerequisites:** Node.js 20+, Git, Devin API key ([app.devin.ai](https://app.devin.ai))

---

## Architecture

```
                    ┌──────────────────────┐
                    │     ENGINEER         │
                    │  (Natural Language)   │
                    └──────────┬───────────┘
                               │
                ┌──────────────▼──────────────┐
                │         OPENCLAW            │
                │       (Orchestrator)        │
                │                             │
                │  • Skill routing            │
                │  • Guardrail enforcement    │
                │  • SDLC validation          │
                │  • Federal compliance gates │
                │  • ATO evidence generation  │
                │  • Audit trail              │
                │  • MCP: Jira, Slack, Teams  │
                └──────────────┬──────────────┘
                               │
                ┌──────────────▼──────────────┐
                │    DEEPWIKI + ADVANCED DEVIN │
                │    (Brain + Knowledge)       │
                │                             │
                │  • Codebase intelligence    │
                │  • Session analysis         │
                │  • Playbook generation      │
                │  • STIG/NIST knowledge base │
                │  • CVE correlation          │
                │  • Self-improving knowledge │
                └──────────────┬──────────────┘
                               │
          ┌────────┬───────────┼──────────┬─────────┐
          ▼        ▼           ▼          ▼         ▼
     ┌─────────┐┌────────┐┌────────┐┌─────────┐┌────────┐
     │  DEVIN  ││ DEVIN  ││ DEVIN  ││  DEVIN  ││ DEVIN  │
     │  CLOUD  ││  CLI   ││  API   ││  IDE    ││ REVIEW │
     │         ││        ││        ││         ││        │
     │ 100+    ││ Local  ││ CI/CD  ││ FedRAMP ││ Auto   │
     │ parallel││ exec   ││ webhooks│ High    ││ PR     │
     │ sessions││ air-gap││ batch  ││ IL5-IL6 ││ review │
     └─────────┘└────────┘└────────┘└─────────┘└────────┘
```

---

## Pre-Loaded Skills

15 skills covering federal enterprise modernization scenarios. Each skill is a complete workflow: specification → tests → build → review → compliance validation → audit.

| Skill | What It Does |
|-------|-------------|
| `legacy-analysis` | Index and assess a codebase with DeepWiki. Produce modernization roadmap. |
| `plsql-migration` | Migrate Oracle PL/SQL → PostgreSQL. Type mapping, exception handling, batch parallel. |
| `cobol-conversion` | Convert COBOL → Java/Python/TypeScript. Preserve exact business logic. |
| `db-rationalization` | Analyze, deduplicate, and consolidate database portfolios. |
| `security-scan` | STIG/NIST/FedRAMP compliance scanning, CVE correlation, and auto-remediation. |
| `test-generation` | Generate comprehensive test suites for untested legacy code. |
| `feature-dev` | Build new features from requirements using SDD + TDD pipeline. |
| `pr-review` | Automated PR review via Devin Review. Bug catch, auto-fix. |
| `incident-response` | Auto-investigate production alerts, open fix PRs. |
| `parallel-migration` | Spawn 100+ parallel sessions for large-scale batch work. |
| `api-modernization` | SOAP→REST, REST→GraphQL, monolith→microservices. |
| `containerization` | Dockerize legacy apps. Multi-stage builds, K8s manifests, Iron Bank compliance. |
| `sdlc-validator` | Validate every task followed the full SDLC lifecycle. |
| `guardrail-auditor` | Monitor Devin Enterprise Guardrails API for policy violations. |
| `skill-creator` | **Meta-skill**: creates new skills when no match exists. Self-evolving system. |

---

## Every Task Follows the Same Lifecycle

```
1. INTAKE       → OpenClaw matches task to skill
2. CONTEXT      → DeepWiki provides codebase intelligence
3. SPEC         → Spec-Driven Design generates specification
4. TEST         → Test-Driven Design writes tests first
5. BUILD        → Devin executes (1 to 100+ parallel sessions)
6. REVIEW       → Devin Review auto-reviews every PR
7. COMPLIANCE   → STIG/NIST/FedRAMP gates checked
                   CVE scan against known vulnerabilities
8. VALIDATE     → OpenClaw checks all hard gates:
                   ✅ Spec exists
                   ✅ Tests pass
                   ✅ Coverage met
                   ✅ Review clean
                   ✅ Security scan clean (STIG CAT I: 0 findings)
                   ✅ CVE scan: no critical/high unmitigated
                   ✅ Guardrails: 0 violations
                   ✅ NIST 800-53 controls satisfied
9. EVIDENCE     → ATO evidence pack generated
10. LEARN       → Advanced Devin analyzes session → improves playbooks
```

If a task has no matching skill, the `skill-creator` meta-skill builds one, pushes it to the repo, and the whole team gains the capability.

---

## Verification System

DevinClaw Federal uses a multi-layered verification architecture to ensure every output is defensible, traceable, and predictably escalated when confidence is insufficient.

### Self-Verification Loop
Every skill runs a self-verification loop after completing its primary procedure: verify → auto-fix → re-verify → escalate. This eliminates the "ship and hope" pattern that plagues autonomous AI systems.

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
| SOC 2 Type II | Devin Cloud platform |

Every session produces an immutable audit trail. See [SECURITY.md](SECURITY.md).

---

## MCP Integration

Both OpenClaw and Devin connect to external tools via Model Context Protocol:

**OpenClaw layer** (task intake + validation): Jira, Slack, Teams, GitHub, DeepWiki, PostgreSQL

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
├── SKILLS-MAP.md          # Skill → enterprise scenario mapping
├── setup.sh               # One-command bootstrap
│
├── skills/                # 15 pre-loaded OpenClaw skills
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
├── sdd/                   # Spec-Driven Design templates + playbooks
├── tdd/                   # Test-Driven Design templates + playbooks
├── compliance/            # STIG, NIST, FedRAMP, FISMA, RMF, Zero Trust
├── knowledge/             # 6 Devin Knowledge entries (enterprise domain expertise)
├── playbooks/             # 8 Devin playbooks for common tasks
├── deepwiki/              # DeepWiki MCP config + enterprise knowledge base
├── mcp/                   # MCP server configurations
├── audit/                 # Guardrail config, SDLC checklist, arena config, artifact schemas
├── skills-parser/         # Convert OpenClaw skills → Devin playbooks
└── docs/                  # Architecture, SDLC mapping, use cases, FAQ
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

*Built with [Devin](https://devin.ai) • [DeepWiki](https://deepwiki.com) • [OpenClaw](https://openclaw.ai) • [Cognition AI](https://cognition.ai)*
