# Evaluation Criteria

Scoring rubric for DevinClaw test runs. Rate each category from 0–10, then average for the overall score.

---

## Categories

### Completeness (0–10)
*Did the skill produce all expected outputs?*

| Score | Meaning |
|-------|---------|
| 9–10 | All expected artifacts produced. Nothing missing. Evidence pack is complete. |
| 7–8 | Most artifacts produced. Minor gaps that don't block usability. |
| 5–6 | Core outputs present but notable omissions. Manual follow-up needed. |
| 3–4 | Significant gaps. Key artifacts missing or incomplete. |
| 0–2 | Skill failed to produce meaningful output. |

### Accuracy (0–10)
*Are findings real and correctly categorized?*

| Score | Meaning |
|-------|---------|
| 9–10 | All findings verified as real. Severity/category ratings are correct. Zero false positives. |
| 7–8 | Findings are overwhelmingly accurate. Minor miscategorizations. False positive rate < 10%. |
| 5–6 | Majority accurate but some false positives or misclassified findings. Needs human review. |
| 3–4 | Mixed accuracy. Significant false positives or missed real issues. |
| 0–2 | Mostly incorrect or fabricated findings. |

### Actionability (0–10)
*Can an engineer act on the output immediately?*

| Score | Meaning |
|-------|---------|
| 9–10 | Engineer can start working from the output today. Clear next steps, file references, and remediation guidance. |
| 7–8 | Highly actionable with minimal interpretation needed. |
| 5–6 | Useful but requires additional context or research to act on. |
| 3–4 | Vague recommendations. Engineer needs to redo significant analysis. |
| 0–2 | Output is not actionable without starting over. |

### SDLC Compliance (0–10)
*Were all artifact contracts met? Evidence pack complete?*

| Score | Meaning |
|-------|---------|
| 9–10 | Full compliance with DevinClaw's SDLC artifact contracts. All required documents, formats, and evidence present. |
| 7–8 | Minor deviations from artifact contracts. All critical documents present. |
| 5–6 | Some artifact contracts missed. Evidence pack has gaps. |
| 3–4 | Significant non-compliance. Missing required artifacts. |
| 0–2 | No adherence to SDLC artifact contracts. |

### Domain Expertise (0–10)
*Did knowledge bases and personas add value beyond generic analysis?*

| Score | Meaning |
|-------|---------|
| 9–10 | Output demonstrates deep domain understanding. Findings reflect expertise that a generic tool would miss. |
| 7–8 | Clear evidence of domain-specific insight. Most recommendations are contextually appropriate. |
| 5–6 | Some domain awareness but largely generic analysis. |
| 3–4 | Minimal domain expertise visible. Output could come from any static analysis tool. |
| 0–2 | No domain expertise demonstrated. |

---

## Overall Score

**Overall Score = Average of all five categories**

| Range | Verdict | Interpretation |
|-------|---------|----------------|
| **8.0–10.0** | **Production-Ready** | Output can be used as-is in professional workflows. Minimal to no manual review needed. |
| **7.0–7.9** | **Pass** | Strong output. Minor polish may be needed but fundamentally sound. |
| **5.0–6.9** | **Conditional Pass** | Usable with manual review and supplementation. Identifies areas for skill improvement. |
| **3.0–4.9** | **Below Expectations** | Significant gaps. Investigate whether the skill was used correctly or if the target codebase is outside supported parameters. |
| **0.0–2.9** | **Fail** | Output is not usable. Report to Cognition for investigation. |

---

## Tips for Fair Evaluation

1. **Compare against alternatives** — How long would this take a senior engineer manually? Even a score of 6 may represent massive time savings.
2. **Use real code** — Toy projects don't test DevinClaw's strengths. Use production codebases.
3. **Run multiple skills** — One test run is a data point. Three or more reveal patterns.
4. **Document context** — Note anything unusual about your codebase that might affect results (e.g., proprietary frameworks, unusual architecture).
