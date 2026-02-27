# Spec-Driven Design (SDD) in DevinClaw

## Overview

Spec-Driven Design is the structured methodology at the heart of DevinClaw's approach to enterprise ederal modernization. Adapted from [Cognition-SDD](https://github.com/Cognition-SDD), SDD ensures that **specifications are the single source of truth** driving all implementation. Every feature, migration, and modernization effort follows a disciplined pipeline before a single line of production code is written.

In the DevinClaw architecture, SDD bridges the gap between user intent (expressed in natural language through OpenClaw) and autonomous implementation (executed by Devin sessions). Whether specs are authored interactively or Devin is autonomously implementing tasks at scale, the same structured pipeline governs the work.

## The SDD Pipeline

```
Constitution --> Specification --> Design --> Task Breakdown --> TDD Implementation --> Verification
```

| Phase | What Happens | Output | DevinClaw Integration |
|-------|-------------|--------|----------------------|
| **1. Constitution** | Establish governing principles: code quality, security (STIG/NIST), testing, architecture constraints | `constitution.md` | Read by every Devin session |
| **2. Specification** | Define WHAT to build and WHY. User stories in EARS format, acceptance criteria, NFRs. No technology choices. | `spec.md` | Created via `sdd_create_spec` playbook or `/spec-to-code` workflow |
| **3. Design** | Define HOW: architecture, data models, API contracts, sequence diagrams, traceability matrix | `design.md` | Created via `sdd_create_plan` playbook |
| **4. Task Breakdown** | Decompose design into small, ordered, testable tasks with dependencies and parallelization markers | `tasks.md` | Created via `sdd_create_tasks` playbook |
| **5. TDD Implementation** | For each task: write failing test (RED) --> implement minimal code (GREEN) --> refactor | Production code + tests | Executed via `sdd_implement_tasks` playbook or `/tdd-cycle` workflow |
| **6. Verification** | All tests pass, coverage met, traceability confirmed, guardrails API shows 0 violations | Ship it | Validated by OpenClaw's SDLC checklist |

## Quick Start

### With Devin (Autonomous Implementation)

1. Add the four SDD playbooks from `sdd/devin/playbooks/` to your Devin organization
2. Add `sdd/devin/knowledge.md` as a Devin Knowledge entry
3. Start a Devin session and attach the appropriate phase playbook
4. Follow the pipeline: Spec --> Plan --> Tasks --> Implement

5. Use `/spec-to-code [feature]` to run the full pipeline

### Using Both Together (Recommended for Enterprise Modernization)

- **Devin (Outer Loop)**: Implementation and delivery. Autonomous, PR-based, scalable. Devin reads committed specs/plans from Git and implements via TDD with full audit trails.

### Devin Execution Modes

| Mode | Best For | How It Works |
|------|----------|-------------|
| **Devin Cloud** | Autonomous implementation and delivery at scale | Playbooks + Knowledge drive Devin sessions, 100+ parallel sessions |
| **Devin CLI** | Local development, interactive spec authoring | Developer runs Devin locally with full context |
| **Devin API** | Programmatic integration, CI/CD pipelines | API-driven session management |
| **Devin Review** | PR review and compliance checking | Automated code review with STIG/NIST awareness |

## Directory Structure

```
sdd/
├── README.md                          # This file
├── templates/                         # SDD document templates
│   ├── constitution.md                # Governing principles template
│   ├── spec.md                        # Feature specification template
│   ├── design.md                      # Technical design template
│   └── tasks.md                       # Task breakdown template
├── devin/                             # Devin integration
│   ├── playbooks/                     # Phase-specific Devin playbooks
│   │   ├── sdd_create_spec.devin.md   # Phase 1: Create specification
│   │   ├── sdd_create_plan.devin.md   # Phase 2: Create implementation plan
│   │   ├── sdd_create_tasks.devin.md  # Phase 3: Generate task list
│   │   └── sdd_implement_tasks.devin.md # Phase 4: Implement tasks
│   └── knowledge.md                   # SDD knowledge entry for Devin
    ├── rules/                         # Cascade rules (auto-loaded)
    │   ├── sdd-process.md             # SDD pipeline and process rules
    │   ├── code-standards.md          # Code quality and style rules
    │   └── testing-standards.md       # TDD and testing rules
    ├── workflows/                     # Cascade workflows (slash commands)
    │   ├── spec-to-code.md            # Full SDD pipeline workflow
    │   └── tdd-cycle.md               # Red-green-refactor cycle
    └── memories/                      # Persistent project context
        └── project-context.md         # DevinClaw project context
```

## Core Principles

These principles govern all SDD work in DevinClaw:

- **Constitution first**: Establish governing principles before any spec work. These constrain all downstream decisions, including federal compliance requirements (STIG, NIST, FedRAMP).
- **Clarify before planning**: Validate and refine specs before generating plans. Mark ambiguities with `[NEEDS CLARIFICATION]`. Reduces expensive rework.
- **No code without spec**: A hard guardrail enforced by OpenClaw. Implementation cannot begin until spec and plan are approved.
- **Test-first is non-negotiable**: TDD provides machine-verifiable evidence that the system works. Tests are the proof, not subjective claims.
- **Traceability end-to-end**: Every requirement traces to a design element, every design element to a task, every task to tests, every test to code.
- **Iterative refinement**: Specs are living documents. Update them when requirements change; regenerate plans and tasks.

## Related Directories

- `tdd/` -- Test-Driven Design templates and playbooks
- `compliance/` -- Federal security compliance (STIG, NIST, FedRAMP, Zero Trust)
- `playbooks/` -- Additional Devin playbooks for migration and modernization
- `skills/` -- OpenClaw skills (complete workflows triggered by natural language)

## enterprise Federal Modernization Context

DevinClaw's SDD methodology is specifically tailored for enterprise modernization scenarios:

- **Legacy Analysis**: DeepWiki indexes existing enterprise codebases; specs capture current-state understanding before modernization
- **Migration at Scale**: SDD ensures each migration (PL/SQL to PostgreSQL, COBOL to modern languages) follows the same structured pipeline
- **Compliance Built-In**: Constitutional gates enforce STIG/NIST requirements at every phase
- **Audit Trail**: Every SDD artifact (spec, plan, tasks, tests) is version-controlled and traceable, satisfying federal audit requirements
- **Parallel Execution**: Task breakdowns with `[P]` markers enable Devin to spawn 100+ parallel sessions for batch migrations
