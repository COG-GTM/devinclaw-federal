# DevinClaw — End-to-End Test Plan

**Purpose:** Validate that DevinClaw works as advertised. An engineer with zero context clones this repo, follows setup, and solves real enterprise-scale modernization problems.

**Principle:** Every test uses real open-source code that mirrors enterprise systems — Java, COBOL, PL/SQL, legacy databases. No toy examples.

---

## Test Environment Requirements

- macOS or Linux workstation
- Node.js 20+
- Git
- Devin API key (free tier works for CLI tests)
- GitHub account (for PR creation tests)

---

## Test Suite 1: Cold Start (Can a stranger use this?)

### T1.1 — Clone and Setup
```bash
git clone https://github.com/COG-GTM/devinclaw.git
cd devinclaw
chmod +x setup.sh
./setup.sh
```
**Pass criteria:** Setup completes without errors. OpenClaw is running. Skills are loaded.

### T1.2 — Smoke Test
```bash
bash scripts/smoke_test.sh
```
**Pass criteria:** 110/110 checks pass.

### T1.3 — SDLC Validation
```bash
python3 scripts/validate_sdlc.py
```
**Pass criteria:** All SDLC stages validated.

### T1.4 — Skill Discovery
Ask OpenClaw: "I need to migrate Oracle stored procedures to PostgreSQL"
**Pass criteria:** Routes to `plsql-migration` skill. Displays the skill's procedure.

### T1.5 — No-Match Skill Creation
Ask OpenClaw: "I need to convert MUMPS code to Python"
**Pass criteria:** `skill-creator` meta-skill activates and generates a new skill definition.

---

## Test Suite 2: Legacy Analysis (The the enterprise's #1 problem)

### T2.1 — Java Legacy Codebase (mirrors enterprise ata exchange)
**Target repo:** [enterprise ata exchange legacy-client](https://github.com/legacy-sample-app/legacy-client) (real enterprise pen-source, Java, 2.5K LOC)
```
Task: "Analyze this enterprise application for modernization readiness"
Skill: legacy-analysis
```
**Pass criteria:**
- [ ] System map generated (components, entry points, dependencies)
- [ ] Tech stack detected (Java version, frameworks, build system)
- [ ] Technical debt catalog produced with severity ratings
- [ ] Integration points identified (SOAP/REST services, DB connections)
- [ ] Modernization roadmap with phased approach
- [ ] All outputs in paired md + JSON format
- [ ] Evidence pack generated with SHA-256 hashes

### T2.2 — Multi-Module Java (mirrors enterprise ore processing system scale)
**Target repo:** [Apache Camel](https://github.com/apache/camel) (large, modular, Java — similar complexity to enterprise systems)
```
Task: "Analyze the core module for modernization opportunities"
Skill: legacy-analysis
```
**Pass criteria:** Handles 500K+ LOC without timeout. Produces meaningful subsystem map.

### T2.3 — COBOL Codebase (mirrors enterprise ainframe)
**Target repo:** [AWS Card Demo](https://github.com/aws-samples/aws-mainframe-modernization-carddemo) (COBOL, mainframe patterns, copybooks)
```
Task: "Analyze this COBOL application for conversion to Java"
Skill: legacy-analysis → cobol-conversion
```
**Pass criteria:**
- [ ] COBOL paragraphs mapped to business logic
- [ ] Copybooks identified and cataloged (these are the data structures)
- [ ] JCL batch jobs mapped
- [ ] Conversion complexity estimated per module

---

## Test Suite 3: Code Migration (The money skill)

### T3.1 — PL/SQL to PostgreSQL
**Target:** Create a test Oracle PL/SQL package with:
- Stored procedures with cursors, exception handling, bulk collect
- Package-level variables and types
- NVL, DECODE, SYSDATE, ROWNUM usage
- Oracle-specific string concatenation (||)
```
Task: "Migrate this PL/SQL package to PostgreSQL"
Skill: plsql-migration
```
**Pass criteria:**
- [ ] All Oracle-specific constructs converted (NVL→COALESCE, SYSDATE→CURRENT_TIMESTAMP, etc.)
- [ ] Exception handling converted (RAISE_APPLICATION_ERROR → RAISE EXCEPTION)
- [ ] Empty-string-equals-NULL behavior documented as a migration risk
- [ ] Tests generated for the converted code
- [ ] Conversion runs against a real PostgreSQL instance (use Docker)
- [ ] Evidence pack + self-verify loop completed

### T3.2 — COBOL to Java
**Target:** [AWS Card Demo](https://github.com/aws-samples/aws-mainframe-modernization-carddemo) — COBOL-CICS-DB2 application
```
Task: "Convert the CBACT01C program to Java"
Skill: cobol-conversion
```
**Pass criteria:**
- [ ] Packed decimal (COMP-3) handling preserved
- [ ] PERFORM THRU logic correctly converted
- [ ] Working storage → Java class fields
- [ ] CICS commands → Spring annotations or comments
- [ ] Test coverage on converted code

### T3.3 — API Modernization (SOAP → REST)
**Target:** Any open-source SOAP service (e.g., [Spring WS samples](https://github.com/spring-projects/spring-ws-samples))
```
Task: "Modernize this SOAP service to REST with OpenAPI spec"
Skill: api-modernization
```
**Pass criteria:**
- [ ] WSDL parsed and mapped to REST endpoints
- [ ] OpenAPI 3.0 spec generated
- [ ] Controller/handler code generated
- [ ] Request/response mapping preserved
- [ ] Tests for all endpoints

---

## Test Suite 4: Security (What gets ATOs)

### T4.1 — Vulnerability Scan on Known-Bad Code
**Target:** [OWASP WebGoat](https://github.com/WebGoat/WebGoat) (deliberately vulnerable Java app)
```
Task: "Perform a full security assessment per STIG/NIST standards"
Skill: security-scan
```
**Pass criteria:**
- [ ] SQL injection identified (STIG V-222604)
- [ ] XSS identified (STIG V-222602)
- [ ] Hardcoded credentials flagged
- [ ] Dependency CVEs cataloged with severity
- [ ] Each finding has: file path, code excerpt, severity, confidence, STIG/NIST mapping
- [ ] Remediation PRs generated for auto-fixable issues
- [ ] Arena mode (N=3) produces consistent findings across sessions

### T4.2 — Security Scan on enterprise Code
**Target:** [legacy-sample-app/legacy-client](https://github.com/legacy-sample-app/legacy-client)
```
Task: "Security assessment of this enterprise application"
Skill: security-scan
```
**Pass criteria:** Finds real issues (we already know about plaintext configs, missing input validation). Produces STIG-formatted findings.

### T4.3 — STIG Compliance Check
**Target:** Any containerized application
```
Task: "Validate this container against DISA Container Platform STIG"
Skill: security-scan + containerization
```
**Pass criteria:** STIG CAT I/II/III findings categorized. Remediation guidance per finding.

---

## Test Suite 5: Database Rationalization (3,000 databases)

### T5.1 — Schema Duplicate Detection
**Target:** Create 3 PostgreSQL databases with:
- DB1: `airports` table (code, name, city, state, lat, lon)
- DB2: `aerodrome_data` table (icao_code, aerodrome_name, municipality, region, latitude, longitude)
- DB3: `airport_info` table (airport_code, airport_name, city_name, state_code, lat, lng, elevation)
```
Task: "Analyze these 3 databases for consolidation opportunities"
Skill: db-rationalization
```
**Pass criteria:**
- [ ] All 3 tables identified as semantic duplicates (same business entity, different schemas)
- [ ] Confidence score > 60% for duplicate pairs
- [ ] Column mapping generated (code↔icao_code↔airport_code)
- [ ] Consolidation target schema proposed
- [ ] Migration scripts generated as DRAFTS (not production-ready)
- [ ] Explicitly states human SME review required

### T5.2 — Cross-Reference Detection
**Target:** Databases with shared reference data (airports, airlines, aircraft types)
**Pass criteria:** Identifies reference data duplication and recommends single source of truth.

---

## Test Suite 6: Testing (Meta-test: can DevinClaw test itself?)

### T6.1 — Test Generation for Untested Code
**Target:** [legacy-sample-app/legacy-client](https://github.com/legacy-sample-app/legacy-client) (minimal existing tests)
```
Task: "Generate comprehensive test suite for this codebase"
Skill: test-generation
```
**Pass criteria:**
- [ ] Unit tests generated for all public methods
- [ ] Integration tests for service layer
- [ ] Tests compile and run (not just generated)
- [ ] Coverage report shows > 60% branch coverage
- [ ] Tests are deterministic (no flakes)

### T6.2 — Computer-Use E2E (Devin 2.2)
**Target:** Any web application with a UI
```
Task: "Run E2E smoke test using computer use"
Skill: test-generation (with computer-use flag)
```
**Pass criteria:** Devin 2.2 opens the app in virtual desktop, clicks through flows, captures screenshots as evidence.

---

## Test Suite 7: Verification System (The trust layer)

### T7.1 — Arena Mode Divergence Detection
**Target:** Run `security-scan` on WebGoat with arena mode (N=3)
**Pass criteria:**
- [ ] 3 independent sessions complete
- [ ] Divergence score computed
- [ ] Findings that all 3 agree on get confidence boost (+0.15)
- [ ] Any contradictions flagged with divergence details
- [ ] Evidence pack contains all 3 session outputs

### T7.2 — Self-Verify + Auto-Fix Loop
**Target:** Intentionally introduce a failing test in a PR
```
Task: "Fix the failing CI build"
Skill: incident-response
```
**Pass criteria:** Devin identifies the failure, fixes it, re-runs tests, confirms pass, opens PR with evidence.

### T7.3 — Artifact Contract Enforcement
**Target:** Complete any skill but delete the evidence-pack.json before submission
**Pass criteria:** SDLC validator rejects the completion. Task not marked done.

---

## Test Suite 8: Compound Improvement (Does it get smarter?)

### T8.1 — Knowledge Accumulation
1. Run `legacy-analysis` on Repo A
2. Run `legacy-analysis` on Repo B (same tech stack)
**Pass criteria:** Session 2 is faster and references patterns from Session 1.

### T8.2 — Skill Creation Loop
1. Ask for a task with no matching skill (e.g., "Convert Fortran to Rust")
2. `skill-creator` generates new skill
3. Run the new skill
**Pass criteria:** Generated skill follows the standard format (procedure, artifact contract, verification, escalation).

---

## Test Suite 9: Parallel Execution (The scale story)

### T9.1 — Batch Migration
**Target:** 10 PL/SQL files
```
Task: "Migrate all 10 files to PostgreSQL in parallel"
Skill: parallel-migration
```
**Pass criteria:**
- [ ] 10 parallel Devin sessions spawned
- [ ] Each produces independent PR
- [ ] Pilot batch (first 2) validates rules before scaling
- [ ] All 10 complete within 2x single-session time

---

## Test Suite 10: Full End-to-End Demo (The Phase 3 Story)

### T10.1 — Complete Modernization Lifecycle
**Target:** [legacy-sample-app/legacy-client](https://github.com/legacy-sample-app/legacy-client)

Run the complete pipeline:
1. `legacy-analysis` → modernization report
2. `security-scan` → vulnerability findings + remediation PRs
3. `test-generation` → comprehensive test suite
4. `plsql-migration` or `api-modernization` → actual code changes
5. `pr-review` → Devin Review on the migration PR
6. `sdlc-validator` → confirm all stages completed

**Pass criteria:**
- [ ] All 6 stages produce paired md + JSON artifacts
- [ ] Evidence pack covers the entire lifecycle
- [ ] SDLC validator confirms full compliance
- [ ] Total wall-clock time < 2 hours for a 2.5K LOC app
- [ ] An engineer who wasn't involved can read the artifacts and understand exactly what happened

---

## Priority Order

| Priority | Test | Why |
|----------|------|-----|
| P0 | T1.1-T1.3 | If setup doesn't work, nothing else matters |
| P0 | T2.1 | Legacy analysis on real enterprise ode — the entry point for every engagement |
| P0 | T4.1 | Security findings are what gets ATOs |
| P1 | T3.1 | PL/SQL migration is the highest-volume enterprise se case |
| P1 | T7.1 | Arena mode is the differentiator — must prove it works |
| P1 | T10.1 | End-to-end demo is Phase 3 of the ChBA |
| P2 | T2.3, T3.2 | COBOL — important but lower volume than Java/PL/SQL |
| P2 | T5.1 | DB rationalization — proves the 3,000 database story |
| P2 | T6.1 | Test generation — force multiplier |
| P3 | T8.1-T8.2, T9.1 | Compound learning + parallelism — impressive but secondary to correctness |

---

## enterprise-Specific Test Repositories

| Repo | Why It's Relevant | Skills to Test |
|------|-------------------|----------------|
| [legacy-sample-app/legacy-client](https://github.com/legacy-sample-app/legacy-client) | Real enterprise ata exchange code, Java, 2.5K LOC | legacy-analysis, security-scan, test-generation |
| [legacy-sample-app/legacy-sample-app.github.io](https://github.com/legacy-sample-app/legacy-sample-app.github.io) | enterprise ata exchange documentation site | legacy-analysis |
| [aws-samples/aws-mainframe-modernization-carddemo](https://github.com/aws-samples/aws-mainframe-modernization-carddemo) | COBOL + CICS + DB2 — mirrors enterprise ainframe | cobol-conversion, legacy-analysis |
| [WebGoat/WebGoat](https://github.com/WebGoat/WebGoat) | Deliberately vulnerable Java — proves security scan | security-scan |
| [spring-projects/spring-ws-samples](https://github.com/spring-projects/spring-ws-samples) | SOAP services — mirrors enterprise ntegration patterns | api-modernization |
| [apache/camel](https://github.com/apache/camel) | Large Java, modular — tests scale | legacy-analysis, parallel-migration |

---

*Every test in this plan maps to a real enterprise modernization scenario. If DevinClaw passes these tests, it can handle the enterprise's 200+ applications.*
