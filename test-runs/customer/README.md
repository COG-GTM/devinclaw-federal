# How to Run Your Own DevinClaw Test

This guide walks you through validating DevinClaw against your own codebase. Whether you're evaluating for purchase, running a proof-of-concept, or benchmarking against your current tooling — this is where to start.

## Prerequisites

- Access to a Devin workspace with DevinClaw skills installed
- A target codebase (ideally real legacy code from your environment)
- 30–60 minutes per test run

## Step-by-Step

### 1. Pick a Target Codebase

Choose something representative of your actual environment. The best targets are:
- Legacy applications with known technical debt
- Codebases with incomplete or outdated documentation
- Systems approaching a migration or modernization effort

Avoid toy projects — DevinClaw shines on real complexity.

### 2. Choose Which Skill(s) to Test

DevinClaw skills are designed for specific SDLC phases. Pick the one that matches your immediate need:

| Skill | Best For |
|-------|----------|
| Legacy Codebase Analysis | Understanding undocumented or complex systems |
| Security Vulnerability Scan | Finding real vulnerabilities with remediation plans |
| Test Generation | Producing meaningful test suites from existing code |
| SDD Spec Generation | Creating structured design documents from code |

### 3. Copy the Template

Copy [`TEMPLATE.md`](./TEMPLATE.md) into a new file (e.g., `my-test-run-1.md`) and fill it out as you go. The template mirrors our internal format so results are directly comparable.

### 4. Run the Skill in Devin

Execute the chosen skill against your target codebase. Document:
- What you asked Devin to do (exact prompt or task description)
- What Devin produced (outputs, artifacts, findings)
- How long it took

### 5. Score Using the Rubric

Use [`EVALUATION-CRITERIA.md`](./EVALUATION-CRITERIA.md) to score the run across five dimensions. Be honest — the rubric is designed to surface both strengths and gaps.

### 6. Determine Pass/Fail

- **Overall Score ≥ 7.0** → Pass (production-ready output)
- **Overall Score 5.0–6.9** → Conditional Pass (usable with manual review)
- **Overall Score < 5.0** → Fail (needs investigation)

### 7. Submit Results (Optional)

Share your completed test run with Cognition to:
- Help improve DevinClaw skills based on real-world feedback
- Get recommendations for optimizing your workflow
- Contribute to the community benchmark dataset

Contact your Cognition account team or submit via the DevinClaw repository.

## Examples

See the [`examples/`](./examples/) directory for sample test scenarios:
- [Legacy Java App](./examples/legacy-java-app.md) — Testing legacy codebase analysis
- [COBOL Migration](./examples/cobol-migration.md) — Testing COBOL conversion skill
- [Security Audit](./examples/security-audit.md) — Testing security scanning skill
