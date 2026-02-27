# Quick Start Guide

Get DevinClaw running in 5 minutes.

## Prerequisites

- **Node.js 20+** installed
- **Git** installed
- **Devin account** with API access (Team or Enterprise plan)
- **DeepWiki API key** (from deepwiki.com)

## Step 1: Clone the Repository

```bash
git clone https://github.com/COG-GTM/devinclaw.git
cd devinclaw
```

## Step 2: Run Setup

```bash
chmod +x setup.sh
./setup.sh
```

The setup script will:
1. Install OpenClaw (if not already installed)
2. Configure the OpenClaw workspace
3. Install all DevinClaw skills
4. Prompt you for your Devin API key and DeepWiki API key
5. Configure MCP servers
6. Verify the installation

## Step 3: Start DevinClaw

```bash
openclaw
```

You'll see the OpenClaw chat interface. DevinClaw is ready.

## Step 4: Try Your First Task

```
> Analyze this codebase and give me a modernization assessment
```

DevinClaw will:
1. Index the codebase with DeepWiki
2. Run the `legacy-analysis` skill
3. Produce a full modernization report

## Step 5: Run a Migration

```
> Migrate all PL/SQL stored procedures to PostgreSQL
```

DevinClaw will:
1. Inventory all PL/SQL objects
2. Generate SDD specifications
3. Generate TDD test cases
4. Spawn parallel Devin sessions
5. Build, test, and create PRs
6. Run Devin Review on every PR
7. Validate the full SDLC checklist

## Available Commands

| Command | What It Does |
|---------|-------------|
| `openclaw skills list` | Show all installed DevinClaw skills |
| `openclaw status` | Check system health |
| `openclaw config set <key> <value>` | Update configuration |

## What's Installed

After setup, you have:
- **15 pre-configured skills** for enterprise modernization tasks
- **8 Devin playbooks** for common workflows
- **6 Devin Knowledge entries** with enterprise omain expertise
- **Federal compliance framework** (STIG, NIST 800-53, FedRAMP, Zero Trust)
- **SDD + TDD templates** for structured development
- **MCP server configurations** for GitHub, Jira, Slack, Datadog, Sentry, and more
- **Audit and governance** with guardrail enforcement
- **Skills Parser** to convert OpenClaw skills to Devin playbooks

## Next Steps

1. Read `docs/ARCHITECTURE.md` to understand the system
2. Read `docs/USE-CASES.md` for enterprise modernization scenarios
3. Review `SKILLS-MAP.md` for the full skill registry
4. Review `SECURITY.md` for federal compliance posture
