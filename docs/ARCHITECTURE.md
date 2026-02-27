# DevinClaw Architecture

## System Overview

DevinClaw is a three-layer AI modernization framework designed for enterprise-scale government application portfolios. It combines an orchestration layer (OpenClaw), a knowledge layer (DeepWiki + Advanced Devin), and an execution layer (Devin Cloud, CLI, API, and Devin Review) into a single, pre-configured system.

```
┌─────────────────────────────────────────────────────────────┐
│                     USER INTERFACE                           │
│              Natural language chat (OpenClaw)                │
│         "Migrate the notification PL/SQL procedures to Postgres"   │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│                                                              │
│                    ORCHESTRATOR LAYER                         │
│                       (OpenClaw)                             │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐  │
│  │ Skills   │  │Guardrails│  │  SDLC    │  │   Audit    │  │
│  │ Router   │  │Enforcer  │  │Validator │  │   Trail    │  │
│  └──────────┘  └──────────┘  └──────────┘  └────────────┘  │
│                                                              │
│  MCP Access: Jira │ Slack │ Teams │ GitHub │ DeepWiki       │
│                                                              │
│  Workspace: SOUL.md │ GUARDRAILS.md │ TOOLS.md │ SECURITY.md│
│             SKILLS-MAP.md                                    │
│                                                              │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│                                                              │
│                    KNOWLEDGE LAYER                            │
│              (DeepWiki + Advanced Devin)                      │
│                                                              │
│  ┌──────────────┐  ┌────────────────┐  ┌────────────────┐  │
│  │   DeepWiki   │  │   Advanced     │  │   Knowledge    │  │
│  │   MCP Server │  │   Devin        │  │   Base         │  │
│  │              │  │                │  │                │  │
│  │ • Codebase   │  │ • Session      │  │ • enterprise omain   │  │
│  │   indexing   │  │   analysis     │  │ • Playbooks    │  │
│  │ • Context    │  │ • Playbook     │  │ • Patterns     │  │
│  │   queries    │  │   generation   │  │ • Conventions  │  │
│  │ • Dependency │  │ • Knowledge    │  │ • Lessons      │  │
│  │   mapping    │  │   management   │  │   learned      │  │
│  └──────────────┘  └────────────────┘  └────────────────┘  │
│                                                              │
│  Self-Improving: Every session → analysis → better playbooks │
│                                                              │
└────────────────────────────┬────────────────────────────────┘
                             │
         ┌───────┬───────────┼───────────┬───────────┐
         │       │           │           │           │
┌────────▼──┐┌───▼───┐┌─────▼─────┐┌────▼────┐┌────▼────┐
│           ││       ││           ││         ││         │
│  DEVIN    ││ DEVIN ││  DEVIN    ││  DEVIN  ││  DEVIN  │
│  CLOUD    ││ CLI   ││  API      ││  IDE    ││ REVIEW  │
│           ││       ││           ││         ││         │
│ • 100+    ││• Local││• CI/CD    ││• FedRAMP││• Auto   │
│   parallel││  exec ││  webhooks ││  High   ││  PR     │
│   sessions││• Air  ││• Programm-││• IL5-IL6││  review │
│ • Autonom-││  gap  ││  atic     ││• Human +││• Bug    │
│   ous     ││  OK   ││  access   ││  AI     ││  catch  │
│ • Batch   ││• Quick││• Session  ││  collab ││• Auto   │
│   capable ││  tasks││  mgmt     ││         ││  fix    │
│           ││       ││           ││         ││         │
└───────────┘└───────┘└───────────┘└─────────┘└─────────┘
                    EXECUTION LAYER
                   (Devin Spokes)
```

## Data Flow: Task Lifecycle

```
1. USER INPUT
   "Migrate all PL/SQL stored procedures in the notification schema to PostgreSQL"
   │
2. ORCHESTRATOR (OpenClaw)
   ├─ Parse intent → identify task type
   ├─ Search SKILLS-MAP.md → match: plsql-migration
   ├─ Load skill workflow from skills/plsql-migration/SKILL.md
   ├─ Check GUARDRAILS.md → all gates clear
   │
3. KNOWLEDGE (DeepWiki)
   ├─ Index target codebase (if not already indexed)
   ├─ Query: "All PL/SQL objects in notification schema"
   ├─ Return: dependency graph, object inventory, complexity ratings
   │
4. SPECIFICATION (SDD)
   ├─ Generate spec.md from skill template + DeepWiki context
   ├─ Include: Oracle behavior, type mappings, exception handling
   ├─ Store as artifact for audit trail
   │
5. TESTING (TDD)
   ├─ Generate test-plan.md from spec
   ├─ Create test stubs for all migration units
   ├─ Store as artifact for audit trail
   │
6. EXECUTION (Devin Spokes)
   ├─ Spawn Devin Cloud sessions (1 per package, up to 50 parallel)
   ├─ Each session receives: spec, tests, source PL/SQL, transformation rules
   ├─ Devin builds: migrate code, run tests, create PR
   │
7. REVIEW (Devin Review)
   ├─ Auto-review triggers on each PR
   ├─ Bug catcher: severity classification
   ├─ Auto-fix: apply fixes for detected bugs
   ├─ Codebase-aware chat for questions
   │
8. VALIDATION (OpenClaw)
   ├─ Check SDLC checklist:
   │   ✅ Spec exists
   │   ✅ Tests exist and pass
   │   ✅ Coverage meets thresholds
   │   ✅ Devin Review complete
   │   ✅ No CRITICAL bugs
   │   ✅ Guardrails: 0 violations
   │   ✅ Security scan clean
   ├─ Log to audit trail
   │
9. KNOWLEDGE CAPTURE (Advanced Devin)
   ├─ Analyze all sessions for patterns
   ├─ Create/improve playbooks based on outcomes
   ├─ Update knowledge base
   ├─ DeepWiki re-indexes with new code
   │
10. SYSTEM IS SMARTER
    └─ Next task starts with better context, better playbooks, fewer errors
```

## MCP Integration Architecture

```
                    OpenClaw
                       │
          ┌────────────┼────────────┐
          │            │            │
     Jira MCP    DeepWiki MCP   Slack MCP
     (tickets)   (codebase)    (notifications)
          │            │            │
          └────────────┼────────────┘
                       │
                  Devin Sessions
                       │
          ┌────────────┼────────────┐
          │            │            │
    GitHub MCP   Database MCP  Sentry MCP
    (PRs/code)   (schema/data) (errors/logs)
```

Both layers have MCP access. OpenClaw uses MCPs for task intake and coordination. Devin sessions use MCPs for execution. This dual-layer design means the orchestrator can validate results by querying the same data sources the executor used.

## Self-Evolving Architecture

```
                    ┌──────────────┐
                    │ New Task     │
                    │ (no skill)   │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │ skill-creator│
                    │ meta-skill   │
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
        Devin Docs    DeepWiki     Existing
        Use Cases     Context      Skills
              │            │            │
              └────────────┼────────────┘
                           │
                    ┌──────▼───────┐
                    │ New SKILL.md │
                    │ created      │
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
        Push to      Update        Run Skills
        Repo         SKILLS-MAP    Parser
              │            │            │
              └────────────┼────────────┘
                           │
                    ┌──────▼───────┐
                    │ Team gains   │
                    │ new capability│
                    └──────────────┘
```

When a task has no matching skill, the system creates one. This means DevinClaw's capability grows with every unique task it encounters. After 100 modernization tasks, the framework has 100+ battle-tested skills encoding organizational knowledge.

## Security Architecture

See `SECURITY.md` for full federal compliance posture. Key architectural decisions:

- **No production access**: Devin sessions operate only in sandbox/staging environments
- **Guardrail enforcement**: Enterprise API monitors all sessions for policy violations
- **Audit trail**: Every action logged — immutable, retained indefinitely
- **Zero Trust**: All inter-service communication authenticated and encrypted
- **Least privilege**: Each Devin session has only the permissions needed for its specific task
