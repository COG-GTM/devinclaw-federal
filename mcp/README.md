# MCP Server Configurations

Model Context Protocol (MCP) servers extend both OpenClaw and Devin with access to external tools and data sources. DevinClaw uses a dual-layer MCP architecture:

## Dual-Layer Architecture

### OpenClaw Layer (Orchestrator MCPs)
OpenClaw uses MCPs to receive tasks and coordinate work:
- **Jira/Linear**: Pull tickets, create tasks, track progress
- **Slack/Teams**: Receive commands, send notifications
- **GitHub/GitLab**: Monitor repos, trigger workflows
- **DeepWiki**: Query codebase intelligence

### Devin Layer (Execution MCPs)
Devin sessions use MCPs during task execution:
- **GitHub**: Create PRs, push code, manage branches
- **Database**: Query schemas, execute migrations
- **Sentry/Datadog**: Investigate errors, analyze logs
- **SonarQube**: Code quality analysis

## Configuration Files

| File | Purpose |
|------|---------|
| `openclaw-mcps.json` | MCPs available to the OpenClaw orchestrator |
| `devin-mcps.json` | MCPs available to Devin sessions |
| `configs/*.json` | Individual MCP server configurations |

## Setup

1. Copy the desired MCP configs to your Devin organization settings
2. For OpenClaw MCPs, configure via `openclaw config set tools.mcp.<name> <config>`
3. For Devin MCPs, add via Settings > MCP Marketplace > Add Your Own
4. Test connectivity before running any skills

## Adding Custom MCPs

DevinClaw supports any MCP server that implements the Model Context Protocol. Three transport types:
- **STDIO**: Local CLI-based servers (npx, uvx, Docker)
- **SSE**: Remote servers using Server-Sent Events (legacy)
- **HTTP**: Remote servers using Streamable HTTP (recommended for new integrations)
