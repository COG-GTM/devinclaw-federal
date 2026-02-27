---
name: skill-creator
description: Meta-skill that creates new OpenClaw skills when no existing skill matches a user's task. Cross-references Devin documentation, the use case gallery, and DeepWiki codebase context to generate a complete SKILL.md with full SDD→TDD→Build→Review→Audit workflow. Pushes the new skill to the DevinClaw repository and updates SKILLS-MAP.md so the entire team gains the capability immediately. This is the self-evolving mechanism that makes DevinClaw an adaptive system.
---

# Skill Creator (Meta-Skill)

## Overview

This is the most important skill in DevinClaw. It is the self-evolving mechanism that ensures the framework can handle ANY modernization task, not just the ones that were pre-configured. When a user asks DevinClaw to perform a task and no existing skill matches, this meta-skill activates to create a new skill on-the-fly.

The newly created skill is:
1. Fully functional — complete SKILL.md with YAML frontmatter, procedure, specs, and guardrails
2. Immediately usable — installed into the running OpenClaw instance
3. Shared with the team — pushed to the DevinClaw repository so every engineer benefits
4. Documented — SKILLS-MAP.md and repository docs are updated automatically
5. Convertible — can be run through the Skills Parser to generate Devin playbooks and knowledge entries

This creates a compound learning effect: the more tasks DevinClaw handles, the more capable it becomes. After 100 modernization tasks, the framework has 100+ battle-tested skills that encode organizational knowledge about how to modernize specific types of systems.

## What's Needed From User

- **Task description**: Natural language description of what needs to be done (this is what triggered the skill-creator because no match was found)
- **Codebase context** (optional): If the task involves specific code, DeepWiki context will be pulled automatically
- **Constraints** (optional): Any specific requirements — target language, framework, compliance standards, performance criteria

## Procedure

1. **Confirm no existing skill matches**
   - Re-read SKILLS-MAP.md to verify no skill covers this task (avoid duplicates)
   - Check for partial matches — if an existing skill covers 80%+ of the task, extend it instead of creating new
   - If extending, branch the existing skill and add the new capability
   - Log the gap: what was asked, what was searched, why nothing matched

2. **Research the task domain**
   - Query DeepWiki MCP for relevant codebase context (if a codebase is involved)
   - Search Devin documentation use case gallery (`docs.devin.ai/use-cases/gallery`) for similar patterns
   - Identify which Devin spoke(s) are best suited: Cloud (autonomous), CLI (local), API (programmatic), Review (PR analysis)
   - Identify relevant MCP servers the skill should leverage
   - Review existing skills for structural patterns to maintain consistency

3. **Generate the skill specification**
   - Determine skill name: lowercase, hyphens, max 40 characters, descriptive
   - Write a comprehensive description (minimum 20 characters, should explain what/when/why)
   - Define the full procedure following the DevinClaw standard workflow:
     a. **Context gathering** — what DeepWiki/MCP data is needed
     b. **SDD specification** — how to generate the spec for this type of task
     c. **TDD test plan** — what tests validate success
     d. **Devin session spawning** — which spoke, what prompt, parallel or sequential
     e. **Build execution** — implementation steps
     f. **Review** — Devin Review integration, what to check
     g. **Audit** — guardrail validation, SDLC checklist compliance
     h. **Knowledge capture** — what the system learns from this task

4. **Write the SKILL.md file**
   - Follow the Agent Skills Specification format exactly:
     ```markdown
     ---
     name: skill-name
     description: Comprehensive description of the skill
     ---

     # Skill Title

     ## Overview
     ## What's Needed From User
     ## Procedure
     ## Specifications
     ## Advice and Pointers
     
## Self-Verification Loop (Devin 2.2)

After completing the primary procedure:

1. **Self-verify**: Run all applicable verification gates:
   - Build/test gates: generated SKILL.md passes validate_skill.py, parser produces valid playbook and knowledge
   - Quality gates: skill does not duplicate existing skills, all required sections present
   - Integration gates: SKILLS-MAP.md updated, skill-descriptors.json entry created
2. **Auto-fix**: If any verification gate fails, attempt automated repair — adjust code, configuration, or test fixtures to resolve the failure.
3. **Re-verify**: Run all verification gates again after fixes. Confirm each gate transitions from FAIL to PASS.
4. **Escalate**: If auto-fix fails after 2 attempts, escalate to human reviewer with a complete evidence pack. Include the failing gate identifier, error output, attempted fixes, and root cause hypothesis.

## Artifact Contract

Every stage of this skill produces paired outputs for machine-consumable handoff:

| Stage | Markdown Output | JSON Output |
|-------|----------------|-------------|
| Gap Analysis | `gap_analysis.md` | `gap_analysis.json` |
| Skill Design | `skill_design.md` | `skill_design.json` |
| SKILL.md Generation | `skill_generation.md` | `skill_generation.json` |
| Validation & Registration | `validation.md` | `validation.json` |

JSON outputs must conform to the schema defined in `audit/artifact-schemas/`. Markdown outputs are the human-readable narrative; JSON outputs are the machine-consumable contract consumed by the next stage or by OpenClaw for artifact validation.

## Evidence Pack

On completion, produce `evidence-pack.json` containing:

```json
{
  "session_id": "<Devin session identifier>",
  "timestamp": "<ISO 8601 completion time>",
  "skill_id": "devinclaw.skill_creator.v1",
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
- **Human approval required for**: new skill approval for production use, skill retirement decisions, cross-skill dependency changes.
- **Auto-escalate on**: Any security finding rated HIGH or CRITICAL, any risk of data loss or corruption, any changes to authentication or authorization logic, any modification to safety-critical code paths (DO-178C applicable systems).

## Forbidden Actions
     ```
   - Every section must have substantive content — no placeholders, no TODOs
   - The Procedure must be detailed enough that a junior engineer could follow it
   - Include specific enterprise/federal context where relevant

5. **Create the skill directory and install**
   - Create `skills/{skill-name}/SKILL.md`
   - If the skill requires supporting files (scripts, templates, reference docs), create them in the skill directory
   - Install the skill into the running OpenClaw instance: `openclaw skills install skills/{skill-name}/`
   - Verify the skill is listed: `openclaw skills list`

6. **Update SKILLS-MAP.md**
   - Add the new skill to the master registry with:
     - Skill name
     - enterprise cenario it addresses
     - Devin use case mapping (from the gallery)
     - Spoke(s) used
   - Mark it as `[AUTO-GENERATED]` so humans know it was created by the meta-skill

7. **Run the Skills Parser**
   - Execute: `python skills-parser/scripts/parse_skill.py skills/{skill-name}/ --output-dir skills-parser/output/`
   - This generates `{skill-name}-playbook.md` and `{skill-name}-knowledge.md` for Devin
   - Verify generated files are well-formed

8. **Push to repository**
   - Stage: `git add skills/{skill-name}/ SKILLS-MAP.md skills-parser/output/`
   - Commit: `git commit -m "feat(skill): auto-generated {skill-name} skill"`
   - Push to the DevinClaw repository
   - The entire team now has the new capability

9. **Execute the original task**
   - Now that the skill exists, execute it against the user's original task
   - This validates the skill works in practice, not just in theory
   - If execution reveals issues, iterate on the skill before the push

10. **Capture learnings via Advanced Devin**
    - After execution, use Advanced Devin to analyze the session
    - If the skill performed well, note what worked for future skill creation
    - If it needed adjustments, update the skill and re-push
    - Log the creation event in the audit trail

## Specifications

- **Naming**: lowercase, hyphens only, max 40 chars, no leading/trailing/consecutive hyphens
- **Description minimum**: 20 characters, should explain what the skill does and when to use it
- **Procedure minimum**: At least 5 numbered steps covering context→spec→build→review→audit
- **Quality bar**: New skills must match the quality of `plsql-migration` SKILL.md (the reference standard)
- **Dedup check**: Always check SKILLS-MAP.md before creating — never create duplicate skills
- **Frontmatter required**: YAML frontmatter with `name` and `description` fields is mandatory
- **Parser compatibility**: Generated SKILL.md must pass `validate_skill.py` without errors

## Advice and Pointers

- The best skills come from real task execution. Create the skill, execute the task, then refine the skill based on what you learned. Don't try to make it perfect before first use.
- Look at the Devin use case gallery for inspiration on task structure — many modernization patterns are already documented there.
- Keep skills focused on one type of task. A skill that tries to do "everything" will do nothing well. It's better to have 50 specific skills than 5 generic ones.
- When creating skills for enterprise-specific tasks, include domain context (notification formats, data standard schemas, enterprise ystem names) in the Advice and Pointers section — this is what makes Devin effective in the enterprise domain.
- The Skills Parser generates Devin playbooks and knowledge entries automatically. Write the SKILL.md well and the Devin artifacts will be good too.
- Review auto-generated skills monthly. Some may become redundant as the system evolves. Consolidate or retire as needed.

## Forbidden Actions

- Do not create skills that duplicate existing ones — extend instead
- Do not create skills without the full SDD→TDD→Build→Review→Audit workflow — partial workflows bypass guardrails
- Do not skip the SKILLS-MAP.md update — undocumented skills are invisible to the team
- Do not push skills that fail `validate_skill.py` — quality gates exist for a reason
- Do not create skills that bypass security controls or guardrails
- Do not create skills that access systems outside the authorized scope
