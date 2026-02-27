# DeepWiki -- Brain & Knowledge Management for DevinClaw

## What is DeepWiki?

DeepWiki is a codebase intelligence engine developed by Cognition AI that automatically indexes source code repositories and builds a structured, queryable knowledge graph. It parses code structure, call graphs, dependency trees, data flows, and architectural patterns, then exposes this information through a Model Context Protocol (MCP) server that any AI agent can query in real time.

In the context of DevinClaw, DeepWiki serves as the **persistent brain** that remembers everything the system has learned across every modernization session. When a enterprise engineer asks DevinClaw to migrate a PL/SQL package, DeepWiki already knows:

- The schema structure and foreign key relationships
- Which stored procedures call which tables
- What downstream systems depend on the output
- What patterns succeeded in previous migration sessions
- Which STIG controls are relevant to the data classification

## How DeepWiki Integrates with DevinClaw

DeepWiki operates as an MCP server accessible to both the OpenClaw orchestration layer and individual Devin execution sessions.

### Architecture Position

```
OpenClaw (Orchestrator)
    |
    +--- DeepWiki MCP Server (STDIO transport)
    |        |
    |        +--- Repository Index Store
    |        +--- Knowledge Graph
    |        +--- Session Memory
    |        +--- enterprise Domain Knowledge
    |
    +--- Devin Sessions (each session also connects to DeepWiki MCP)
```

### Integration Points

| Layer | Access Pattern | Primary Use |
|-------|---------------|-------------|
| OpenClaw | MCP STDIO | Skill selection context, architecture queries, dependency mapping |
| Devin Cloud | MCP STDIO | Codebase context during implementation, pattern lookups |
| Devin CLI | MCP STDIO | Offline knowledge access in air-gapped environments |
| Advanced Devin | MCP STDIO + API | Session analysis, playbook generation, knowledge consolidation |

### MCP Capabilities

The DeepWiki MCP server exposes the following tools:

- **index_repository** -- Trigger indexing of a new or updated repository
- **query_codebase** -- Natural language queries against the indexed codebase
- **get_architecture** -- Retrieve architectural diagrams and component maps
- **search_patterns** -- Find code patterns, anti-patterns, and idioms
- **get_dependencies** -- Map upstream and downstream dependencies for any component
- **analyze_complexity** -- Cyclomatic complexity, coupling metrics, and maintainability scores

Configuration is stored in `mcp-config.json` in this directory.

## Enterprise Knowledge Base Structure

Add domain-specific knowledge files to a `knowledge/` subdirectory. These are pre-loaded into DeepWiki's index so that every Devin session starts with enterprise context.

```
knowledge/
  coding-conventions.md     # Java, PL/SQL, COBOL standards per enterprise policies
  tech-stack.md             # Complete technology inventory across business units
  systems-inventory.md      # Enterprise systems with tech stack and modernization status
```

Each file is structured with consistent headings so DeepWiki can parse and cross-reference entries. When a Devin session encounters domain-specific terminology, it queries DeepWiki, which returns the relevant domain knowledge along with codebase-specific context.

## How Knowledge Grows: The Self-Improving Cycle

DevinClaw's knowledge base is not static. It grows through a feedback loop driven by Advanced Devin:

### Knowledge Growth Cycle

```
1. Devin Session Executes
   (e.g., migrates 12 PL/SQL procedures to PostgreSQL)
        |
        v
2. Advanced Devin Analyzes Session
   - What patterns succeeded?
   - What edge cases were encountered?
   - What workarounds were needed?
   - What took longer than expected?
        |
        v
3. Knowledge Artifacts Generated
   - New playbook entries (or refinements to existing ones)
   - New knowledge entries (patterns, gotchas, best practices)
   - Updated knowledge context (domain-specific learnings)
        |
        v
4. DeepWiki Re-Indexes
   - New knowledge entries are ingested into the knowledge graph
   - Cross-references are updated
   - Embeddings are regenerated for semantic search
        |
        v
5. Next Session Starts Smarter
   - Future queries return richer, more accurate context
   - Skills operate with better pattern knowledge
   - Edge cases are anticipated rather than discovered
```

### Concrete Example

**Session 1:** Migrate `PKG_notification_PROCESS` from Oracle PL/SQL to PostgreSQL.
- DeepWiki provides: notification format reference, Oracle schema context, existing PL/SQL patterns.
- Devin discovers: Oracle-specific `CONNECT BY` hierarchical queries require recursive CTEs in PostgreSQL.
- Advanced Devin captures: "Pattern: CONNECT BY to WITH RECURSIVE CTE migration. 3 edge cases around NOCYCLE handling."

**Session 2:** Migrate `PKG_notification_ARCHIVE` from Oracle PL/SQL to PostgreSQL.
- DeepWiki now provides: All of the above, plus the `CONNECT BY` migration pattern with edge cases.
- Devin executes faster, avoids known pitfalls, and produces cleaner output.

### Knowledge Deduplication

Advanced Devin periodically consolidates the knowledge base:
- Merges overlapping entries
- Promotes frequently-referenced patterns to top-level knowledge
- Archives stale entries that no longer match the evolving codebase
- Tags entries with confidence scores based on how many sessions validated them

## Configuration

See `mcp-config.json` for the DeepWiki MCP server configuration. Environment variables required:

| Variable | Description | Where to Obtain |
|----------|-------------|-----------------|
| `DEEPWIKI_API_KEY` | Authentication key for DeepWiki API | Cognition AI dashboard or `app.devin.ai/settings` |
| `DEEPWIKI_BASE_URL` | DeepWiki service endpoint | Default: `https://deepwiki.devin.ai` |

For air-gapped deployments, DeepWiki can run in local mode with the index stored on the local filesystem. Set `DEEPWIKI_BASE_URL` to `http://localhost:8090` and run the DeepWiki container locally.
