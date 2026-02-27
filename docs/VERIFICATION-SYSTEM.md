# Verification System: Coherence, Divergence, and Evidence Gating

## Why Verification Must Be a First-Class System

In enterprise modernization contexts, the failure mode is not slow delivery — it is **loss of trust**. A single hallucinated finding, a missed vulnerability, or an incorrect migration can cascade into ATO delays, safety incidents, or regulatory consequences. The verification system must:

- **Quantify uncertainty**: Every finding must carry a confidence score and supporting evidence.
- **Detect contradictions**: When multiple analysis sessions produce conflicting results, the system must surface the divergence rather than silently choosing one.
- **Preserve evidence**: Every artifact, scan result, test output, and review finding must be retained with SHA-256 hashes for auditability.
- **Escalate predictably**: Clear, deterministic rules for when human intervention is required — no judgment calls by the AI.

---

## Divergence Detection Pattern ("Competing Strategies")

For high-impact tasks where AI confidence must be independently validated, DevinClaw uses the **arena pattern**: run N independent Devin sessions with different prompts, playbooks, or analysis approaches, then compare their outputs.

### How It Works

1. **Parallel Execution**: OpenClaw launches N independent Devin sessions (typically N=2 for standard tasks, N=3 for high-risk tasks). Each session receives:
   - The same input repository and scope
   - Different playbook variants or prompt framings
   - Independent DevBox environments (no shared state)

2. **Output Normalization**: Each session produces artifacts conforming to the same JSON schema (defined in `audit/artifact-schemas/`). The normalization step ensures:
   - Entities are identified by canonical keys (file path, function name, table name)
   - Findings are classified using the same severity taxonomy
   - Recommendations use the same action vocabulary

3. **Divergence Computation**: The orchestrator computes divergence across session outputs:
   - **Entity overlap**: What percentage of identified entities appear in all sessions' outputs? Low overlap indicates incomplete analysis.
   - **Agreement on key invariants**: Do all sessions agree on the top-level architectural patterns, critical vulnerabilities, and primary risks? Disagreement on invariants is a red flag.
   - **Conflicting claims**: Are there direct contradictions (e.g., Session A says a function is dead code, Session B says it handles critical authentication)? Conflicting claims require resolution.
   - **Confidence distribution**: If sessions assign different severity levels to the same finding, the divergence score increases.

4. **Divergence Score Calculation**:
   ```
   divergence = 1.0 - (
     0.30 * entity_overlap_ratio +
     0.30 * invariant_agreement_ratio +
     0.25 * (1.0 - conflicting_claims_ratio) +
     0.15 * confidence_alignment_ratio
   )
   ```
   - Score 0.00–0.15: **High agreement** — proceed with merged output.
   - Score 0.15–0.35: **Moderate divergence** — merge with annotations noting areas of disagreement. Flag for reviewer awareness.
   - Score 0.35+: **High divergence** — escalate to human reviewer. Do not auto-merge.

5. **Resolution**:
   - If divergence < threshold: merge outputs, annotating any minor disagreements.
   - If divergence >= threshold: Devin performs **targeted additional verification** — re-analyzes the specific entities/claims in dispute with focused prompts.
   - If still unresolved after targeted verification: escalate to human reviewer with a complete evidence pack containing both session outputs, the divergence analysis, and the targeted verification results.

---

## Arena Concept: Risk-Based Execution Modes

The arena pattern is expensive (2-3x compute cost), so it should be applied selectively based on risk classification.

### Execution Modes

| Mode | Sessions | When to Use | Cost Multiplier |
|------|----------|-------------|-----------------|
| **single-run** | 1 | Low-risk, well-understood tasks (formatting, simple test generation, documentation updates) | 1x |
| **arena-run** | 2–3 | High-risk tasks where incorrect output has significant consequences | 2–3x |

### Risk Classification Per Skill

Risk classification determines the default execution mode. See `audit/arena-config.json` for the full configuration.

| Risk Level | Skills | Default Mode |
|------------|--------|-------------|
| **Critical** | security-scan, db-rationalization, incident-response | arena-run (N=3) |
| **High** | legacy-analysis, plsql-migration, cobol-conversion, api-modernization | arena-run (N=2) |
| **Medium** | feature-dev, test-generation, parallel-migration, containerization | single-run (arena optional) |
| **Low** | pr-review, sdlc-validator, guardrail-auditor, skill-creator | single-run |

### Override Rules

- Users can override the default mode in either direction (promote single-run to arena, or demote arena to single-run).
- Overrides to lower risk must be logged in the audit trail with explicit justification.
- Safety-critical systems (DO-178C DAL A-C) always use arena-run regardless of skill risk classification.

---

## Confidence Scoring

Every finding produced by DevinClaw carries a confidence score:

| Score Range | Label | Meaning |
|-------------|-------|---------|
| 0.90–1.00 | **Definitive** | Verified by multiple independent methods (code, tests, scans). Safe to act on. |
| 0.70–0.89 | **High** | Strong evidence from primary analysis. Recommended for action with standard review. |
| 0.50–0.69 | **Moderate** | Evidence present but with caveats. Requires human review before action. |
| 0.30–0.49 | **Low** | Preliminary signal. Must be validated by additional analysis or SME review. |
| 0.00–0.29 | **Speculative** | Insufficient evidence. Flagged for awareness only. Do not act without independent confirmation. |

### Confidence Boosters
- Finding confirmed by arena-run (multiple sessions agree): +0.15
- Finding confirmed by Devin Review independently: +0.10
- Finding backed by automated test evidence: +0.10
- Finding backed by STIG/CVE database match: +0.10

### Confidence Reducers
- Finding contradicted by another session in arena: -0.20
- Finding in area where DeepWiki indexing was incomplete: -0.15
- Finding in language/framework where Devin has known limitations: -0.10
- Finding based on pattern matching without semantic analysis: -0.10

---

## Evidence Preservation

Every verification activity produces an immutable evidence record:

```json
{
  "verification_id": "ver_<uuid>",
  "timestamp": "<ISO 8601>",
  "work_order_id": "<parent work order>",
  "mode": "single-run|arena-run",
  "sessions": [
    {
      "session_id": "<Devin session ID>",
      "playbook_variant": "<variant identifier>",
      "artifacts": [
        {
          "filename": "<file>",
          "sha256": "<hash>",
          "stage": "<stage>"
        }
      ]
    }
  ],
  "divergence": {
    "score": 0.12,
    "entity_overlap": 0.95,
    "invariant_agreement": 0.90,
    "conflicting_claims": 0.02,
    "confidence_alignment": 0.88
  },
  "resolution": "auto-merged|targeted-verification|human-escalated",
  "human_reviewer": null,
  "audit_hash": "<SHA-256 of this record>"
}
```

Evidence records are stored in `audit/verification-logs/` and must be retained for the contract duration plus 3 years per FAR 4.703.

---

## Escalation Thresholds

| Condition | Action |
|-----------|--------|
| Divergence score >= 0.35 | Escalate to human reviewer with evidence pack |
| Any finding rated CRITICAL | Immediate escalation regardless of divergence |
| Finding involves authentication/authorization changes | Human approval required before merge |
| Finding involves database migration execution | Human SME sign-off required |
| Finding involves safety-critical code (DO-178C) | Human DER review required |
| Two consecutive auto-fix failures on the same gate | Escalate with root cause hypothesis |
| Session produces no artifacts (empty output) | Flag as anomaly, re-run with different playbook |

---

## Integration with OpenClaw Orchestrator

OpenClaw implements the verification system as an **orchestration policy**:

1. **Task intake**: OpenClaw classifies the task's risk level using `audit/arena-config.json`.
2. **Session launch**: OpenClaw creates the appropriate number of Devin sessions (1 for single-run, 2-3 for arena-run).
3. **Output collection**: OpenClaw polls session completion and collects artifacts.
4. **Divergence check**: For arena-run tasks, OpenClaw computes divergence and determines resolution path.
5. **Evidence storage**: OpenClaw writes the verification record to the audit trail.
6. **Artifact validation**: OpenClaw rejects "done" status if required artifacts are missing, hashes don't match, or evidence pack is incomplete (per Section 9.3 of the architecture document).

---

*This verification system is the trust foundation for the entire DevinClaw architecture. Without it, autonomous AI-driven modernization is a liability. With it, every output is defensible, every decision is traceable, and every escalation is predictable.*
