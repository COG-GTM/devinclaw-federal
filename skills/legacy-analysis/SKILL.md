---
name: legacy-analysis
description: Analyze legacy codebases using DeepWiki MCP to identify modernization opportunities, technical debt, and migration paths. Use this skill when onboarding a new enterprise application for modernization assessment, when performing portfolio-level analysis across business units, or when generating the initial modernization roadmap for any legacy system.
---

# Legacy Codebase Analysis

## Overview

This skill performs deep analysis of legacy codebases to produce actionable modernization assessments. It leverages the DeepWiki MCP server to index and understand repositories, then systematically catalogs architecture, dependencies, technical debt, data flows, and integration points. The output is a structured modernization report with prioritized findings and a phased migration roadmap.

This skill is the typical entry point for any enterprise modernization engagement. Enterprise portfolios typically include 200+ applications built with Java/Spring, Oracle PL/SQL, COBOL, mainframe assembler, C/C++, and various proprietary frameworks. Many of these systems were built in the 1980s-1990s and have accumulated decades of technical debt, undocumented tribal knowledge, and tightly coupled integrations.

## What's Needed From User

- **Repository URL or local path**: The Git repository or local directory containing the legacy codebase to analyze.
- **Application name**: The enterprise application identifier (e.g., traffic management system, core processing system, data exchange, notification).
- **Line of Business (LOB)**: Which enterprise LOB owns this application (e.g., Operations, Engineering, Finance, IT, Security).
- **Known technology stack** (optional): Any known languages, frameworks, or databases. If not provided, the skill will auto-detect.
- **Modernization priority** (optional): Whether the focus is on cloud migration, language conversion, database migration, API modernization, or full rewrite.
- **Existing documentation** (optional): Links to any existing architecture documents, data dictionaries, or interface control documents (ICDs).

## Procedure

1. **Index the repository with DeepWiki MCP**
   - Connect to the DeepWiki MCP server.
   - Submit the repository URL for indexing.
   - Wait for indexing to complete and confirm the knowledge graph is populated.
   - If the repository is large (>500K LOC), request incremental indexing by module or directory.

2. **Analyze top-level architecture**
   - Query DeepWiki for the project structure, entry points, and module boundaries.
   - Identify the architectural pattern (monolith, layered, SOA, client-server, mainframe batch).
   - Map the directory structure to logical components.
   - Identify build systems (Maven, Gradle, Ant, Make, JCL).
   - Document the deployment topology if configuration files are present (e.g., server.xml, web.xml, CICS definitions).

3. **Identify languages, frameworks, and runtime dependencies**
   - Catalog every language present by file extension and content analysis.
   - Identify frameworks (Spring, Struts, EJB, JSF, CICS, IMS, MQ).
   - Identify middleware and messaging (IBM MQ, TIBCO, JMS, Kafka).
   - List external service integrations (SOAP, REST, CORBA, RMI).
   - Identify database access layers (JDBC, JPA/Hibernate, embedded SQL, EXEC SQL, Pro*C).
   - Record runtime versions where detectable (JDK version, COBOL compiler level, Oracle version).

4. **Catalog dependencies and integration points**
   - Parse dependency manifests (pom.xml, build.gradle, package.json, CICS CSD).
   - Identify internal dependencies between modules.
   - Map external system integrations and data feeds.
   - Identify shared libraries, copybooks, or common modules used across applications.
   - Flag deprecated or end-of-life dependencies with CVE exposure.
   - Document all inbound and outbound interfaces with protocol and data format.

5. **Assess technical debt**
   - Measure code complexity metrics (cyclomatic complexity, coupling, cohesion).
   - Identify code duplication across modules.
   - Flag dead code, unused imports, and commented-out blocks.
   - Assess test coverage (if tests exist) and identify untested critical paths.
   - Identify hardcoded configuration values, magic numbers, and embedded credentials.
   - Check for known anti-patterns (God classes, circular dependencies, deep inheritance hierarchies).
   - Estimate debt severity: Critical (blocks modernization), High (significant rework), Medium (manageable), Low (cosmetic).

6. **Map data flows and business logic**
   - Trace data flows from input sources through processing to output destinations.
   - Identify business rules embedded in code (especially in COBOL paragraphs, PL/SQL procedures, and Java service layers).
   - Map database read/write patterns and transaction boundaries.
   - Identify batch processing jobs and their schedules.
   - Document ETL pipelines and data transformation logic.
   - Flag business logic that is duplicated across multiple systems.

7. **Generate the modernization report**
   - Produce a structured report containing:
     - Executive summary with risk assessment.
     - Application profile (languages, LOC, complexity scores).
     - Architecture diagram description (component inventory and relationships).
     - Dependency inventory with risk ratings.
     - Technical debt catalog with severity classifications.
     - Data flow maps.
     - Integration point inventory.
   - Prioritize findings using a weighted scoring model:
     - Security risk (weight: 0.30)
     - Operational risk (weight: 0.25)
     - Modernization complexity (weight: 0.25)
     - Business value impact (weight: 0.20)

8. **Create the migration roadmap**
   - Define migration phases:
     - Phase 1: Quick wins (configuration externalization, dependency updates, security fixes).
     - Phase 2: Database migration (Oracle to PostgreSQL, DB2 to PostgreSQL).
     - Phase 3: Language modernization (COBOL to Java/Python, PL/SQL to PostgreSQL functions).
     - Phase 4: Architecture modernization (monolith decomposition, API creation, containerization).
     - Phase 5: Cloud deployment (Kubernetes, CI/CD, observability).
   - Estimate effort for each phase in story points and calendar weeks.
   - Identify dependencies between phases.
   - Flag risks and mitigation strategies for each phase.
   - Recommend which OpenClaw skills to invoke for each phase.

## Specifications

- **Output format**: The modernization report must be generated as a Markdown document stored in the repository under `docs/modernization/` with the naming convention `{app-name}-modernization-report-{YYYY-MM-DD}.md`.
- **DeepWiki indexing**: Always confirm indexing is complete before querying. If DeepWiki is unavailable, fall back to static code analysis using file traversal and pattern matching.
- **Language detection**: Must detect at minimum: Java, COBOL, PL/SQL, Python, C, C++, JavaScript/TypeScript, shell scripts, JCL, and assembler.
- **Complexity thresholds**: Flag any method/paragraph with cyclomatic complexity > 20 as High complexity, > 50 as Critical.
- **Dependency age**: Flag any dependency not updated in > 3 years as a technical debt item.
- **LOC counting**: Use logical lines of code (exclude blanks and comments) for all metrics.
- **business units**: Valid business units are Engineering (Core Systems), Operations (System Reliability), AST (Commercial Space Transportation), Infrastructure (Facilities), Finance (Budget and Admin), AHR (Human Resource Management), AIT (Information Technology), and ASH (Security and Hazardous Materials Safety).
- **Classification**: All reports must be marked UNCLASSIFIED // FOR OFFICIAL USE ONLY (U//FOUO) unless otherwise directed.
- **Retention**: Analysis artifacts must be retained for the duration of the contract plus 3 years per FAR 4.703.

## Advice and Pointers

- Start with the build system. A working build tells you more about the real dependency graph than any documentation.
- COBOL copybooks are the Rosetta Stone for mainframe data structures. Always analyze them before the procedural code.
- enterprise systems frequently use TIBCO and IBM MQ for inter-system messaging. Look for queue definitions and message format specifications.
- Many enterprise applications have configuration spread across multiple locations: properties files, database tables, JNDI entries, and environment variables. Catalog all of them.
- When analyzing Oracle PL/SQL, pay special attention to database triggers and materialized views -- these often contain hidden business logic that is not visible in application code.
- If the repository contains JCL, this indicates mainframe batch processing. Map the JCL PROCs to understand job flows.
- Prioritize security findings above all else. enterprise systems are critical national infrastructure under federal oversight.
- When estimating effort, multiply initial estimates by 1.5x for enterprise systems due to compliance overhead (FISMA, FedRAMP, STIG).


## Self-Verification Loop (Devin 2.2)

After completing the primary procedure:

1. **Self-verify**: Run all applicable verification gates:
   - Build/test gates: static analysis validation, DeepWiki indexing confirmation
   - Security gates: credential detection in codebase, dependency CVE scan
   - Analysis gates: cross-reference report findings against source evidence
2. **Auto-fix**: If any verification gate fails, attempt automated repair — adjust code, configuration, or test fixtures to resolve the failure.
3. **Re-verify**: Run all verification gates again after fixes. Confirm each gate transitions from FAIL to PASS.
4. **Escalate**: If auto-fix fails after 2 attempts, escalate to human reviewer with a complete evidence pack. Include the failing gate identifier, error output, attempted fixes, and root cause hypothesis.

## Artifact Contract

Every stage of this skill produces paired outputs for machine-consumable handoff:

| Stage | Markdown Output | JSON Output |
|-------|----------------|-------------|
| Repository Indexing | `indexing.md` | `indexing.json` |
| Architecture Analysis | `architecture.md` | `architecture.json` |
| Dependency Catalog | `dependencies.md` | `dependencies.json` |
| Technical Debt Assessment | `tech_debt.md` | `tech_debt.json` |
| Data Flow Mapping | `data_flows.md` | `data_flows.json` |
| Modernization Report | `modernization_report.md` | `modernization_report.json` |
| Migration Roadmap | `migration_roadmap.md` | `migration_roadmap.json` |

JSON outputs must conform to the schema defined in `audit/artifact-schemas/`. Markdown outputs are the human-readable narrative; JSON outputs are the machine-consumable contract consumed by the next stage or by OpenClaw for artifact validation.

## Evidence Pack

On completion, produce `evidence-pack.json` containing:

```json
{
  "session_id": "<Devin session identifier>",
  "timestamp": "<ISO 8601 completion time>",
  "skill_id": "devinclaw.legacy_analysis.v1",
  "artifacts": [
    {
      "filename": "<output file>",
      "sha256": "<SHA-256 hash of file contents>",
      "stage": "<which stage produced this artifact>"
    }
  ],
  "verification": {
    "gates_run": ["<gate_1>", "<gate_2>"],
    "gates_passed": ["<gate_1>", "<gate_2>"],
    "gates_failed": [],
    "auto_fix_attempts": 0,
    "test_summary": {"passed": 0, "failed": 0, "skipped": 0},
    "scan_summary": {"critical": 0, "high": 0, "medium": 0, "low": 0}
  },
  "knowledge_updates": [
    {
      "action": "created|updated",
      "knowledge_id": "<Devin knowledge entry ID>",
      "summary": "<what was learned>"
    }
  ],
  "escalations": [
    {
      "gate": "<failing gate>",
      "reason": "<why auto-fix failed>",
      "evidence": "<link to error output>"
    }
  ]
}
```

## Escalation Policy

- **Divergence threshold**: 0.35 — if parallel verification sessions disagree beyond this threshold on key findings, escalate to human reviewer with both evidence packs for adjudication.
- **Human approval required for**: modernization phase sequencing, budget allocation recommendations, system decommissioning decisions.
- **Auto-escalate on**: Any security finding rated HIGH or CRITICAL, any risk of data loss or corruption, any changes to authentication or authorization logic, any modification to safety-critical code paths (DO-178C applicable systems).

## Forbidden Actions

- Do not modify any source code in the repository during analysis. This skill is read-only.
- Do not execute any code from the repository. Analysis must be performed through static inspection only.
- Do not store or transmit any credentials, connection strings, or secrets discovered during analysis. Flag them in the report as findings but redact the actual values.
- Do not make assumptions about business logic correctness. Report what the code does, not what it should do.
- Do not skip the DeepWiki indexing step. If DeepWiki is unavailable, explicitly state the fallback method used and note reduced analysis confidence.
- Do not generate the modernization report without completing all prior analysis steps. Partial reports lead to incorrect migration planning.
- Do not assign severity ratings without supporting evidence from the code analysis.
- Do not include Personally Identifiable Information (PII) or Sensitive Security Information (SSI) in any report output.
