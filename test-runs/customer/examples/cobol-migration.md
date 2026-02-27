# Example: COBOL Migration Assessment

## Scenario

Your organization runs critical batch processing on a COBOL mainframe system. Leadership wants a migration feasibility study before committing budget. You need to understand what you're dealing with.

## Setup

| Field | Value |
|-------|-------|
| **Skill** | Legacy Codebase Analysis |
| **Target** | Payroll batch processing system (COBOL 85, ~50K LOC, JCL job control) |
| **Goal** | Assess migration complexity and produce a conversion roadmap |

## What to Prompt Devin

> Analyze this COBOL codebase for migration feasibility. Identify program structure, data dependencies, business rules embedded in code, and conversion complexity. Produce a migration assessment following DevinClaw's artifact contract.

## Expected Outputs

- Program inventory (copybooks, paragraphs, call trees)
- Data flow analysis (file I/O, database interactions, inter-program communication)
- Business rule extraction (logic embedded in PERFORM/EVALUATE blocks)
- Conversion complexity rating per program
- Recommended migration phases

## What to Score

- **Completeness:** Were all COBOL programs catalogued? Were copybook dependencies traced?
- **Accuracy:** Are the extracted business rules correct? Do data flows match actual file layouts?
- **Actionability:** Could a migration team use this to estimate effort?
- **SDLC Compliance:** Full artifact pack with traceability?
- **Domain Expertise:** Does the analysis understand COBOL idioms (e.g., REDEFINES, level-88 conditions, indexed files)?

## What "Good" Looks Like

A strong run (score 8+) will identify:
- Hidden business rules in nested PERFORM loops
- REDEFINES that change data interpretation based on context
- Shared copybooks creating cross-program coupling
- JCL dependencies that affect execution order
- Programs that can migrate independently vs. those that must move together
