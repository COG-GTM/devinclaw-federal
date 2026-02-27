# Example: Legacy Java Application Analysis

## Scenario

You have a 10-year-old Java monolith (Spring Boot 1.x, ~200K LOC) that needs modernization. Documentation is sparse, the original team has left, and you need to understand the system before planning a migration.

## Setup

| Field | Value |
|-------|-------|
| **Skill** | Legacy Codebase Analysis |
| **Target** | Internal inventory management system (Java 8, Spring Boot 1.5, Maven) |
| **Goal** | Produce a comprehensive system understanding document |

## What to Prompt Devin

> Analyze this legacy Java application. Identify the architecture, key dependencies, technical debt, and migration risks. Produce a Legacy Codebase Analysis report following DevinClaw's artifact contract.

## Expected Outputs

- Architecture overview (component diagram, dependency map)
- Technical debt inventory (categorized by severity)
- Dependency analysis (outdated libs, known CVEs)
- Migration risk assessment
- Recommended modernization sequence

## What to Score

- **Completeness:** Did you get all five outputs above?
- **Accuracy:** Are the architectural findings correct? Do the dependencies match reality?
- **Actionability:** Could a new engineer onboard using this report?
- **SDLC Compliance:** Does the report follow the artifact contract format?
- **Domain Expertise:** Does the analysis reflect understanding of Java/Spring patterns (not just generic code scanning)?

## What "Good" Looks Like

A strong run (score 8+) will surface things like:
- Circular dependencies between modules
- Spring Boot 1.x → 2.x/3.x migration blockers
- Deprecated API usage with specific remediation steps
- Business logic buried in controller layers
- Missing test coverage in critical paths
