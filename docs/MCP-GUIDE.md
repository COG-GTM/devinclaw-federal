# MCP Integration Guide

## What is MCP?

Model Context Protocol (MCP) is an open standard that lets AI agents interact with external tools and data sources. DevinClaw uses MCP at two layers:

1. **OpenClaw layer** — for task intake, coordination, and validation
2. **Devin layer** — for execution, code management, and monitoring

## Dual-Layer Architecture

### Why Two Layers?

The orchestrator (OpenClaw) and the executor (Devin) need different tools:

| Layer | MCPs | Purpose |
|-------|------|---------|
| OpenClaw | Jira, Slack, Teams, DeepWiki, GitHub | Receive tasks, query context, send notifications, validate results |
| Devin | GitHub, Database, Sentry, Datadog, SonarQube | Push code, run migrations, investigate errors, analyze quality |

### Cross-Layer Validation

Because both layers can access the same data sources (e.g., GitHub), the orchestrator can independently verify what the executor did. OpenClaw can check: "Did Devin actually create that PR? Do the tests actually pass? Is the coverage report real?"

## Configuring MCPs

### For OpenClaw
```bash
openclaw config set tools.mcp.deepwiki "$(cat mcp/configs/deepwiki.json)"
openclaw config set tools.mcp.github "$(cat mcp/configs/github.json)"
openclaw config set tools.mcp.jira "$(cat mcp/configs/jira.json)"
```

### For Devin
1. Go to app.devin.ai → Settings → MCP Marketplace
2. Add each MCP from `mcp/devin-mcps.json`
3. Or use "Add Your Own" with the JSON configs in `mcp/configs/`

## Available MCP Servers

| Server | Transport | Both Layers | Config File |
|--------|-----------|-------------|-------------|
| DeepWiki | STDIO | ✅ | `configs/deepwiki.json` |
| GitHub | STDIO | ✅ | `configs/github.json` |
| PostgreSQL | STDIO | ✅ | `configs/database.json` |
| Jira | HTTP | OpenClaw only | `configs/jira.json` |
| Slack | HTTP | OpenClaw only | `configs/slack.json` |
| Sentry | HTTP | Devin only | `configs/sentry.json` |
| Datadog | HTTP | Devin only | `configs/datadog.json` |
| SonarQube | HTTP | Devin only | `configs/sonarqube.json` |

## Adding Custom MCPs

DevinClaw supports any MCP server. Three transport types:

- **STDIO**: Local CLI-based (npx, Docker). Best for: database access, file processing
- **HTTP**: Remote servers via Streamable HTTP. Best for: cloud APIs, SaaS tools (recommended for new integrations)
- **SSE**: Remote servers via Server-Sent Events. Legacy — use HTTP instead for new servers

### Example: Adding an Oracle Database MCP
```json
{
  "transport": "STDIO",
  "command": "docker",
  "args": ["run", "-i", "--rm", "-e", "ORACLE_CONNECTION_STRING", "oracle-mcp-server:latest"],
  "env_variables": {
    "ORACLE_CONNECTION_STRING": "oracle://user:pass@host:1521/service"
  }
}
```

## MCP in the Workflow

```
1. User: "Migrate notification PL/SQL to PostgreSQL"
2. OpenClaw → Jira MCP: Pull related tickets for context
3. OpenClaw → DeepWiki MCP: Get codebase analysis
4. OpenClaw → Spawn Devin session with task
5. Devin → GitHub MCP: Clone repo, create branch
6. Devin → Database MCP: Analyze Oracle schema
7. Devin → Build migration code, run tests
8. Devin → GitHub MCP: Create PR
9. Devin Review → Auto-review PR
10. OpenClaw → GitHub MCP: Verify PR exists and tests pass
11. OpenClaw → Validate SDLC checklist ✅
```
