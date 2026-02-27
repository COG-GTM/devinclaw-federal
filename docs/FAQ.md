# Frequently Asked Questions

## General

**Q: What is DevinClaw?**
A: DevinClaw is a pre-configured AI modernization framework that combines OpenClaw (orchestrator), DeepWiki (knowledge), and Devin (execution) into a single downloadable system for enterprise-scale application and database modernization.

**Q: Who is DevinClaw for?**
A: Government contractors, federal agencies, and enterprise teams modernizing large application portfolios. It's designed for the enterprise's 200+ application and 3,000 database modernization initiative but applicable to any large-scale modernization.

**Q: How is this different from just using Devin directly?**
A: Devin is the execution engine. DevinClaw adds: an orchestration layer (skill routing, SDLC validation, audit trail), a knowledge layer (DeepWiki integration, domain knowledge, self-improving playbooks), federal compliance (STIG, NIST, FedRAMP), and a structured methodology (SDD + TDD). It turns Devin from a tool into a governed modernization factory.

**Q: Can DevinClaw handle classified workloads?**
A: Devin Cloud operates at SOC 2 Type II. For classified workloads, Devin operates within authorized security boundaries.

## Technical

**Q: How many parallel Devin sessions can DevinClaw run?**
A: Up to 100+ via Advanced Devin batch sessions. Default configuration limits to 50 concurrent sessions to avoid resource contention. Configurable per deployment.

**Q: What happens when DevinClaw encounters a task type it hasn't seen before?**
A: The `skill-creator` meta-skill activates. It cross-references Devin docs, the codebase context from DeepWiki, and existing skills to create a new skill on-the-fly. The new skill is pushed to the repository so the entire team benefits.

**Q: What MCP servers does DevinClaw support?**
A: Any MCP server that implements the Model Context Protocol. Pre-configured: GitHub, Jira, Slack, Teams, PostgreSQL, Sentry, Datadog, SonarQube, DeepWiki. Custom servers can be added via STDIO, HTTP, or SSE transport.

**Q: Does DevinClaw require internet access?**
A: OpenClaw and Devin CLI can operate in air-gapped environments. Devin Cloud and the Devin API require internet connectivity. Devin CLI can operate in disconnected mode for classified environments.

## Security & Compliance

**Q: What federal security frameworks does DevinClaw support?**
A: NIST SP 800-53 Rev 5, NIST SP 800-207 (Zero Trust), DISA STIGs (all 18 categories), FedRAMP (Moderate and High baselines), and FISMA.

**Q: Can DevinClaw access production systems?**
A: No. A guardrail (`GR-ACCESS-001`) blocks all Devin sessions from accessing production systems. All work occurs in sandbox/staging environments.

**Q: How is the audit trail maintained?**
A: Every action across all sessions is logged to `audit/` in structured JSON format. Logs are immutable and retained indefinitely per federal records management requirements. The `guardrail-auditor` skill continuously monitors for policy violations.

**Q: What happens when a guardrail is violated?**
A: CRITICAL violations trigger immediate alerts and can pause sessions. HIGH violations alert within 1 minute. All violations are logged, and CRITICAL/HIGH violations block PR merge until resolved by a human.

## Methodology

**Q: What is Spec-Driven Design (SDD)?**
A: A methodology where specifications are the single source of truth. Every feature follows: Constitution → Specification → Design → Task Breakdown → TDD Implementation → Verification. Specs are written before code, ensuring consistent quality across 100+ parallel sessions.

**Q: What is the difference between SDD and TDD?**
A: SDD defines WHAT to build (specifications). TDD defines HOW to validate (tests before code). DevinClaw uses both: SDD generates the spec, TDD ensures the implementation is correct.

**Q: Can I skip SDD/TDD for simple tasks?**
A: No. `GUARDRAILS.md` requires specs and tests for ALL tasks. This is non-negotiable for federal compliance — every change must be traceable from requirement to test to implementation.
