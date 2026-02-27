# Devin Knowledge Entries

## What Is This?

These are [Devin Knowledge entries](https://docs.devin.ai/product-guides/knowledge) — domain expertise that Devin automatically recalls when working on related tasks. Each file contains a **trigger description** and **content** following Devin's native Knowledge format.

Knowledge entries make Devin a federal enterprise domain expert from the first prompt. Instead of generic code generation, Devin understands STIG controls, enterprise system architecture, Oracle-to-PostgreSQL migration patterns, and COBOL conversion strategies.

## How They Work

1. Upload each file as a Knowledge entry in Devin's Settings & Library
2. Set the **Trigger Description** from the `trigger:` field in each file
3. Devin automatically retrieves the right knowledge when the task matches

## Entries

| File | Domain | Auto-Triggers On |
|------|--------|-----------------|
| `security-auditor.md` | STIG/NIST/FedRAMP compliance | Security scans, vulnerability review, ATO prep |
| `oracle-migrator.md` | Oracle → PostgreSQL migration | PL/SQL conversion, database migration |
| `cobol-converter.md` | COBOL → modern language conversion | Mainframe modernization, COBOL analysis |
| `enterprise-modernizer.md` | enterprise systems domain | enterprise apps, data exchange, notification, enterprise systems |
| `db-architect.md` | Database rationalization | Schema consolidation, DB deduplication |
| `test-engineer.md` | Federal test engineering | Test generation, coverage, TDD |

## Relationship to Skills and Playbooks

| Layer | What It Is | Where It Lives |
|-------|-----------|---------------|
| **Skills** (OpenClaw) | Orchestrator routing + governance | `skills/` — decides WHAT to do and enforces rules |
| **Knowledge** (Devin) | Domain expertise for sessions | `knowledge/` — makes Devin a domain expert |
| **Playbooks** (Devin) | Step-by-step execution templates | `playbooks/` — tells Devin HOW to execute |
