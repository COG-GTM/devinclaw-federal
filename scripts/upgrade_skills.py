#!/usr/bin/env python3
"""Add Devin 2.2 sections to all 15 skills before Forbidden Actions."""
import os

SKILLS_DIR = os.path.expanduser("~/clawd/projects/devinclaw/skills")

# Per-skill customizations
SKILL_CONFIG = {
    "legacy-analysis": {
        "stages": [
            ("Repository Indexing", "indexing", "indexing"),
            ("Architecture Analysis", "architecture", "architecture"),
            ("Dependency Catalog", "dependencies", "dependencies"),
            ("Technical Debt Assessment", "tech_debt", "tech_debt"),
            ("Data Flow Mapping", "data_flows", "data_flows"),
            ("Modernization Report", "modernization_report", "modernization_report"),
            ("Migration Roadmap", "migration_roadmap", "migration_roadmap"),
        ],
        "verify_gates": "Build/test gates: static analysis validation, DeepWiki indexing confirmation\n   - Security gates: credential detection in codebase, dependency CVE scan\n   - Analysis gates: cross-reference report findings against source evidence",
        "human_approval": "modernization phase sequencing, budget allocation recommendations, system decommissioning decisions",
    },
    "plsql-migration": {
        "stages": [
            ("Schema Analysis", "schema_analysis", "schema_analysis"),
            ("Type Mapping", "type_mapping", "type_mapping"),
            ("Procedure Conversion", "procedure_conversion", "procedure_conversion"),
            ("Test Validation", "test_validation", "test_validation"),
            ("Performance Benchmarking", "performance_benchmark", "performance_benchmark"),
        ],
        "verify_gates": "Build/test gates: PostgreSQL syntax validation, unit tests, integration tests against target DB\n   - DB gates: schema diff review, rollback script verification, migration dry-run\n   - Performance gates: query execution plan comparison (Oracle vs PostgreSQL)",
        "human_approval": "production cutover scheduling, data backfill strategies, rollback trigger criteria",
    },
    "cobol-conversion": {
        "stages": [
            ("Copybook Analysis", "copybook_analysis", "copybook_analysis"),
            ("Program Inventory", "program_inventory", "program_inventory"),
            ("Conversion Specification", "conversion_spec", "conversion_spec"),
            ("Code Generation", "code_generation", "code_generation"),
            ("Equivalence Testing", "equivalence_test", "equivalence_test"),
        ],
        "verify_gates": "Build/test gates: target language compilation, unit tests, numeric precision validation\n   - Equivalence gates: bit-exact comparison of COMP-3 decimal outputs, batch job result comparison\n   - Security gates: credential scan on converted code",
        "human_approval": "packed decimal precision strategy, CICS transaction mapping decisions, batch job scheduling changes",
    },
    "db-rationalization": {
        "stages": [
            ("Schema Inventory", "schema_inventory", "schema_inventory"),
            ("Duplicate Detection", "duplicate_detection", "duplicate_detection"),
            ("Consolidation Analysis", "consolidation_analysis", "consolidation_analysis"),
            ("Rationalization Plan", "rationalization_plan", "rationalization_plan"),
            ("Migration Script Generation", "migration_scripts", "migration_scripts"),
        ],
        "verify_gates": "Build/test gates: migration script syntax validation, idempotency verification\n   - DB gates: schema diff review, rollback script completeness, row count reconciliation queries\n   - Data gates: PII field identification confirmation, referential integrity preservation",
        "human_approval": "production database cutover, data backfill execution, cross-LOB consolidation decisions, decommissioning approvals",
    },
    "security-scan": {
        "stages": [
            ("STIG Scan", "stig_scan", "stig_scan"),
            ("NIST 800-53 Assessment", "nist_assessment", "nist_assessment"),
            ("FedRAMP Validation", "fedramp_validation", "fedramp_validation"),
            ("Zero Trust Assessment", "zero_trust", "zero_trust"),
            ("Remediation SDD", "remediation_sdd", "remediation_sdd"),
            ("Compliance Report", "compliance_report", "compliance_report"),
        ],
        "verify_gates": "Build/test gates: remediation code compilation, security test suite execution\n   - Security gates: re-scan STIG benchmarks post-remediation, dependency CVE re-scan, secrets scan\n   - Compliance gates: XCCDF result validation, OSCAL format verification",
        "human_approval": "CAT I finding risk acceptance, ATO package submission, safety-critical code changes (DO-178C DAL A-C), POA&M entry creation",
    },
    "test-generation": {
        "stages": [
            ("Coverage Analysis", "coverage_analysis", "coverage_analysis"),
            ("Test Plan Design", "test_plan", "test_plan"),
            ("Test Code Generation", "test_code", "test_code"),
            ("Test Execution", "test_execution", "test_execution"),
            ("Coverage Report", "coverage_report", "coverage_report"),
        ],
        "verify_gates": "Build/test gates: all generated tests compile and execute, zero flaky tests detected\n   - Coverage gates: branch coverage >= 80%, mutation testing kill rate >= 70%\n   - Security gates: no credentials or PII in test fixtures",
        "human_approval": "test strategy for safety-critical code paths, acceptance criteria for equivalence testing, mutation testing threshold exceptions",
    },
    "feature-dev": {
        "stages": [
            ("Requirements Analysis", "requirements", "requirements"),
            ("SDD Specification", "sdd_spec", "sdd_spec"),
            ("TDD Test Stubs", "tdd_stubs", "tdd_stubs"),
            ("Implementation", "implementation", "implementation"),
            ("Integration Testing", "integration_test", "integration_test"),
        ],
        "verify_gates": "Build/test gates: compilation, unit tests, integration tests, lint, typecheck\n   - Security gates: dependency scan, STIG compliance check, input validation audit\n   - UI gates: computer-use E2E smoke test (if applicable), Section 508 accessibility validation",
        "human_approval": "new API contract definitions, database schema changes, authentication/authorization modifications, safety-critical feature logic",
    },
    "pr-review": {
        "stages": [
            ("Diff Analysis", "diff_analysis", "diff_analysis"),
            ("Bug Detection", "bug_detection", "bug_detection"),
            ("Compliance Check", "compliance_check", "compliance_check"),
            ("Review Report", "review_report", "review_report"),
        ],
        "verify_gates": "Build/test gates: verify PR branch builds cleanly, all tests pass on PR branch\n   - Security gates: STIG scan on changed files, dependency vulnerability check on new dependencies\n   - Review gates: all Critical/High findings resolved or documented as accepted risk",
        "human_approval": "database migration PR approval, authentication/authorization changes, API contract modifications, safety-critical code changes",
    },
    "incident-response": {
        "stages": [
            ("Alert Triage", "alert_triage", "alert_triage"),
            ("Root Cause Analysis", "root_cause", "root_cause"),
            ("Remediation PR", "remediation_pr", "remediation_pr"),
            ("Post-Incident Report", "post_incident", "post_incident"),
        ],
        "verify_gates": "Build/test gates: remediation code compilation, regression tests pass, existing tests unbroken\n   - Security gates: remediation does not introduce new vulnerabilities, secrets scan on fix\n   - Operational gates: rollback procedure documented and tested",
        "human_approval": "production deployment of fix, SEV-1/SEV-2 incident closure, root cause classification for safety-critical systems, infrastructure-level remediations",
    },
    "parallel-migration": {
        "stages": [
            ("Manifest Generation", "manifest", "manifest"),
            ("Pilot Batch Execution", "pilot_batch", "pilot_batch"),
            ("Full Migration Execution", "full_migration", "full_migration"),
            ("Aggregation & Reporting", "aggregation", "aggregation"),
        ],
        "verify_gates": "Build/test gates: each session's output compiles and tests pass independently\n   - Integration gates: aggregated changes build together without conflicts\n   - Security gates: no credentials in migration artifacts, dependency scan on new dependencies",
        "human_approval": "pilot-to-full migration go/no-go decision, failed session root cause escalation, cross-dependency wave sequencing changes",
    },
    "api-modernization": {
        "stages": [
            ("API Inventory", "api_inventory", "api_inventory"),
            ("Contract Design", "contract_design", "contract_design"),
            ("Implementation", "implementation", "implementation"),
            ("Consumer Migration", "consumer_migration", "consumer_migration"),
            ("Traffic Cutover Plan", "cutover_plan", "cutover_plan"),
        ],
        "verify_gates": "Build/test gates: new API endpoints compile, contract tests pass, backward compatibility verified\n   - Security gates: authentication/authorization on all new endpoints, TLS configuration, CORS policy\n   - Integration gates: consumer smoke tests against new API, load test results within SLA",
        "human_approval": "legacy endpoint decommissioning, traffic cutover scheduling, WS-Security to OAuth 2.0 migration, SWIM interface changes",
    },
    "containerization": {
        "stages": [
            ("Application Analysis", "app_analysis", "app_analysis"),
            ("Dockerfile Creation", "dockerfile", "dockerfile"),
            ("Kubernetes Manifest Generation", "k8s_manifests", "k8s_manifests"),
            ("Image Scan & Validation", "image_scan", "image_scan"),
            ("Deployment Verification", "deploy_verify", "deploy_verify"),
        ],
        "verify_gates": "Build/test gates: Docker image builds successfully, container starts and passes health checks\n   - Security gates: Trivy vulnerability scan (zero Critical/High), non-root user verification, no embedded secrets\n   - K8s gates: resource limits defined, liveness/readiness probes configured, Iron Bank base image compliance",
        "human_approval": "production deployment approval, resource limit exceptions, base image substitutions, persistent volume provisioning",
    },
    "sdlc-validator": {
        "stages": [
            ("Session Artifact Collection", "artifact_collection", "artifact_collection"),
            ("Hard Gate Validation", "gate_validation", "gate_validation"),
            ("Compliance Assessment", "compliance_assessment", "compliance_assessment"),
            ("Certificate Generation", "certificate", "certificate"),
        ],
        "verify_gates": "Build/test gates: validation scripts execute without errors, all 10 hard gates checked\n   - Compliance gates: timestamps verified, artifact hashes match, no retroactive modifications detected\n   - Audit gates: immutable log entries confirmed, certificate data integrity verified",
        "human_approval": "ATO evidence package compilation, cross-boundary session validation, certificate issuance for safety-critical systems",
    },
    "guardrail-auditor": {
        "stages": [
            ("Violation Polling", "violation_poll", "violation_poll"),
            ("Violation Analysis", "violation_analysis", "violation_analysis"),
            ("Alert Generation", "alert_generation", "alert_generation"),
            ("Compliance Report", "compliance_report", "compliance_report"),
        ],
        "verify_gates": "Build/test gates: API connectivity confirmed, violation log integrity verified\n   - Audit gates: no gaps in polling timeline, all violations classified and logged\n   - Alert gates: notification delivery confirmed for Critical/High violations",
        "human_approval": "guardrail rule modifications, violation severity reclassification, enforcement mode changes (monitor → enforce), audit log export for ATO",
    },
    "skill-creator": {
        "stages": [
            ("Gap Analysis", "gap_analysis", "gap_analysis"),
            ("Skill Design", "skill_design", "skill_design"),
            ("SKILL.md Generation", "skill_generation", "skill_generation"),
            ("Validation & Registration", "validation", "validation"),
        ],
        "verify_gates": "Build/test gates: generated SKILL.md passes validate_skill.py, parser produces valid playbook and knowledge\n   - Quality gates: skill does not duplicate existing skills, all required sections present\n   - Integration gates: SKILLS-MAP.md updated, skill-descriptors.json entry created",
        "human_approval": "new skill approval for production use, skill retirement decisions, cross-skill dependency changes",
    },
}

SECTION_TEMPLATE = """
## Self-Verification Loop (Devin 2.2)

After completing the primary procedure:

1. **Self-verify**: Run all applicable verification gates:
   - {verify_gates}
2. **Auto-fix**: If any verification gate fails, attempt automated repair — adjust code, configuration, or test fixtures to resolve the failure.
3. **Re-verify**: Run all verification gates again after fixes. Confirm each gate transitions from FAIL to PASS.
4. **Escalate**: If auto-fix fails after 2 attempts, escalate to human reviewer with a complete evidence pack. Include the failing gate identifier, error output, attempted fixes, and root cause hypothesis.

## Artifact Contract

Every stage of this skill produces paired outputs for machine-consumable handoff:

| Stage | Markdown Output | JSON Output |
|-------|----------------|-------------|
{stage_rows}

JSON outputs must conform to the schema defined in `audit/artifact-schemas/`. Markdown outputs are the human-readable narrative; JSON outputs are the machine-consumable contract consumed by the next stage or by OpenClaw for artifact validation.

## Evidence Pack

On completion, produce `evidence-pack.json` containing:

```json
{{
  "session_id": "<Devin session identifier>",
  "timestamp": "<ISO 8601 completion time>",
  "skill_id": "devinclaw.{skill_domain}.v1",
  "artifacts": [
    {{
      "filename": "<output file>",
      "sha256": "<SHA-256 hash of file contents>",
      "stage": "<which stage produced this artifact>"
    }}
  ],
  "verification": {{
    "gates_run": ["<gate_1>", "<gate_2>"],
    "gates_passed": ["<gate_1>", "<gate_2>"],
    "gates_failed": [],
    "auto_fix_attempts": 0,
    "test_summary": {{"passed": 0, "failed": 0, "skipped": 0}},
    "scan_summary": {{"critical": 0, "high": 0, "medium": 0, "low": 0}}
  }},
  "knowledge_updates": [
    {{
      "action": "created|updated",
      "knowledge_id": "<Devin knowledge entry ID>",
      "summary": "<what was learned>"
    }}
  ],
  "escalations": [
    {{
      "gate": "<failing gate>",
      "reason": "<why auto-fix failed>",
      "evidence": "<link to error output>"
    }}
  ]
}}
```

## Escalation Policy

- **Divergence threshold**: 0.35 — if parallel verification sessions disagree beyond this threshold on key findings, escalate to human reviewer with both evidence packs for adjudication.
- **Human approval required for**: {human_approval}.
- **Auto-escalate on**: Any security finding rated HIGH or CRITICAL, any risk of data loss or corruption, any changes to authentication or authorization logic, any modification to safety-critical code paths (DO-178C applicable systems).

"""

DOMAIN_MAP = {
    "legacy-analysis": "legacy_analysis",
    "plsql-migration": "plsql_migration",
    "cobol-conversion": "cobol_conversion",
    "db-rationalization": "db_rationalization",
    "security-scan": "security_scan",
    "test-generation": "test_generation",
    "feature-dev": "feature_dev",
    "pr-review": "pr_review",
    "incident-response": "incident_response",
    "parallel-migration": "parallel_migration",
    "api-modernization": "api_modernization",
    "containerization": "containerization",
    "sdlc-validator": "sdlc_validator",
    "guardrail-auditor": "guardrail_auditor",
    "skill-creator": "skill_creator",
}

for skill_name, config in SKILL_CONFIG.items():
    skill_path = os.path.join(SKILLS_DIR, skill_name, "SKILL.md")
    with open(skill_path, "r") as f:
        content = f.read()

    # Build stage rows
    stage_rows = ""
    for display_name, md_name, json_name in config["stages"]:
        stage_rows += f"| {display_name} | `{md_name}.md` | `{md_name}.json` |\n"

    section = SECTION_TEMPLATE.format(
        verify_gates=config["verify_gates"],
        stage_rows=stage_rows.rstrip(),
        skill_domain=DOMAIN_MAP[skill_name],
        human_approval=config["human_approval"],
    )

    # Insert before "## Forbidden Actions"
    marker = "## Forbidden Actions"
    if marker in content:
        content = content.replace(marker, section + marker, 1)
        with open(skill_path, "w") as f:
            f.write(content)
        print(f"✅ Updated {skill_name}")
    else:
        print(f"❌ Could not find '{marker}' in {skill_name}")

print("\nDone updating all skills.")
