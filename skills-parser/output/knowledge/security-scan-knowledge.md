# Knowledge: security-scan

## Overview
Scan codebases for STIG, NIST 800-53, and FedRAMP compliance violations. Use this skill when performing federal security audits on enterprise applications, when validating compliance posture before ATO submissions, or when scanning for vulnerabilities and security misconfigurations in modernized code.

## What's Needed From User
- **Repository URL or local path**: The Git repository or local directory containing the codebase to scan.
- **Application name**: The enterprise application identifier (e.g., traffic management system, core processing system, data exchange, notification, Asset Detection System).
- **System categorization**: FISMA impact level -- Low, Moderate, or High. This determines which NIST 800-53 control baselines apply.
- **FedRAMP baseline** (optional): If the application is FedRAMP-authorized, specify the baseline (Low, Moderate, High, or LI-SaaS). If not provided, the FISMA categorization is used to select the equivalent baseline.
- **Technology stack** (optional): Languages, frameworks, and platforms in use. If not provided, the skill will auto-detect from the repository.
- **Existing ATO package** (optional): Links to current System Security Plan (SSP), Plan of Action and Milestones (POA&M), and previous scan results for delta analysis.
- **Scan scope** (optional): Full scan (default) or targeted scan of specific STIG IDs, NIST control families, or code directories.
- **Remediation mode**: Report-only (default) or auto-remediate. In auto-remediate mode, the skill will generate fixes and create PRs.
- **Safety criticality level** (optional): If the application is safety-critical, specify the Design Assurance Level (DAL A through DAL E per DO-178C). This triggers additional verification requirements.

## Procedure
1. **Connect to SonarQube MCP and establish scan baseline**
   - Connect to the SonarQube MCP server via SSE transport.
   - Verify the project exists in SonarQube or create a new project configuration.
   - Retrieve the current quality profile for the project's language(s).
   - Ensure the quality profile includes the enterprise Federal Security ruleset (STIG-aligned rules, OWASP Top 10, CWE Top 25).
   - If a previous scan exists, retrieve the baseline metrics (findings count, coverage, quality gate status) for delta comparison.
   - Record the scan initiation event in the session audit log.

2. **Run STIG compliance scan (V-220629 through V-220641)**
   - Invoke the stig-scanner-mcp to run SCAP benchmarks against the codebase.
   - Scan for each applicable STIG rule:
     - **V-220629 (Authentication)**: Verify password policy enforcement (minimum 14 characters, complexity requirements, bcrypt with 12+ rounds), multi-factor authentication implementation, and account lockout after 5 failed attempts with 15-minute lockout duration.
     - **V-220630 (Session Management)**: Check session timeout configuration (15-minute inactivity), secure cookie flags (Secure, HttpOnly, SameSite=Strict), session ID regeneration after authentication, and session invalidation on logout.
     - **V-220631 (Input Validation)**: Verify whitelist-based input validation on all user-facing endpoints, length limit enforcement (max 255 characters default), format validation with regex patterns, and rejection of unexpected input patterns.
     - **V-220632 (Input Sanitization)**: Check for parameterized database queries (no string concatenation in SQL), output encoding to prevent XSS, removal of dangerous characters (< > " ' ; & | $ ( ) `), and CSRF token validation on state-changing operations.
     - **V-220633 (Encryption at Rest)**: Verify AES-256 encryption for data at rest, FIPS 140-2 validated cryptographic modules, encrypted database connections, and encrypted file storage for sensitive data.
     - **V-220634 (Encryption in Transit)**: Check TLS 1.2+ enforcement (TLS 1.0 and 1.1 disabled), certificate validation, HSTS header configuration, and mutual TLS where required by system architecture.
     - **V-220635 (Audit Logging)**: Verify structured JSON audit logging for authentication events (success and failure), authorization failures, data access and modification, administrative actions, and security-relevant system events.
     - **V-220636 (Access Control)**: Check role-based access control (RBAC) or attribute-based access control (ABAC) implementation, principle of least privilege enforcement, and separation of duties for administrative functions.
     - **V-220637 (Configuration Management)**: Verify no hardcoded credentials, API keys, or secrets in source code; environment-variable-based configuration; and secure default settings.
     - **V-220638 (Integrity Checking)**: Check for file integrity monitoring, code signing verification, and tamper detection mechanisms.
     - **V-220639 (Error Handling)**: Verify generic error messages returned to users (no stack traces, no internal details), detailed internal logging with stack traces, and graceful degradation under error conditions.
     - **V-220640 (Secure Communications)**: Check for secure inter-service communication, API authentication and authorization, and certificate pinning where applicable.
     - **V-220641 (Security Headers)**: Verify HTTP security headers on all responses: Strict-Transport-Security, X-Frame-Options (DENY), X-Content-Type-Options (nosniff), Content-Security-Policy (default-src 'self'), and X-XSS-Protection.
   - Parse SCAP/XCCDF results and classify each finding by severity: Critical, High, Medium, Low, Informational.
   - Map each STIG finding to the specific source file, line number, and code construct that triggered it.

3. **Check NIST 800-53 controls (AC, AU, IA, SC, SI)**
   - Invoke the nist-controls-mcp to validate control implementations for each applicable control family:
     - **AC (Access Control)**: AC-2 (Account Management), AC-3 (Access Enforcement), AC-6 (Least Privilege), AC-7 (Unsuccessful Logon Attempts), AC-8 (System Use Notification), AC-11 (Session Lock), AC-12 (Session Termination), AC-17 (Remote Access), AC-20 (Use of External Systems).
     - **AU (Audit and Accountability)**: AU-2 (Event Logging), AU-3 (Content of Audit Records), AU-4 (Audit Storage Capacity), AU-6 (Audit Review, Analysis, and Reporting), AU-8 (Time Stamps), AU-9 (Protection of Audit Information), AU-11 (Audit Record Retention), AU-12 (Audit Generation).
     - **IA (Identification and Authentication)**: IA-2 (Identification and Authentication for Organizational Users), IA-4 (Identifier Management), IA-5 (Authenticator Management), IA-6 (Authenticator Feedback), IA-8 (Identification and Authentication for Non-Organizational Users), IA-11 (Re-Authentication).
     - **SC (System and Communications Protection)**: SC-7 (Boundary Protection), SC-8 (Transmission Confidentiality and Integrity), SC-12 (Cryptographic Key Establishment and Management), SC-13 (Cryptographic Protection), SC-23 (Session Authenticity), SC-28 (Protection of Information at Rest).
     - **SI (System and Information Integrity)**: SI-2 (Flaw Remediation), SI-3 (Malicious Code Protection), SI-4 (System Monitoring), SI-5 (Security Alerts and Advisories), SI-10 (Information Input Validation), SI-11 (Error Handling), SI-16 (Memory Protection).
   - For each control, determine the implementation status: Implemented, Partially Implemented, Planned, Not Implemented, or Not Applicable.
   - Generate control assessment evidence by mapping code artifacts (configuration files, security middleware, authentication modules, logging implementations) to specific control requirements.
   - Flag any controls marked as Not Implemented or Partially Implemented as findings requiring remediation.

4. **Check FedRAMP baselines and continuous monitoring requirements**
   - Based on the system's FedRAMP baseline (Low, Moderate, or High), validate that all required controls from the FedRAMP Security Controls Baseline are addressed.
   - Verify continuous monitoring artifacts:
     - Vulnerability scan results are current (within 30 days for High, 90 days for Moderate).
     - Software inventory (SBOM) is current and complete.
     - Configuration baselines are documented and enforced.
     - Plan of Action and Milestones (POA&M) is maintained for open findings.
   - Check for FedRAMP-specific requirements beyond NIST 800-53:
     - FedRAMP parameter values (e.g., AC-7 lockout after 3 consecutive attempts for FedRAMP High vs. 5 for NIST baseline).
     - Additional FedRAMP controls not in the NIST baseline.
     - Incident response plan alignment with FedRAMP IR requirements.
   - Invoke the sbom-mcp to generate or validate the Software Bill of Materials in CycloneDX format.
   - Run dependency scanning through sonarqube-mcp to identify CVEs in third-party components.

5. **Validate Zero Trust architecture principles**
   - Assess the codebase against NIST SP 800-207 (Zero Trust Architecture) principles:
     - **Verify explicitly**: Check that every request is authenticated and authorized regardless of network location. Verify that API endpoints do not rely on network perimeter security alone.
     - **Use least privilege access**: Validate that service accounts, API keys, and user roles are scoped to minimum required permissions. Check for overly permissive IAM policies or broad database grants.
     - **Assume breach**: Verify that the application implements defense-in-depth: encrypted communications between microservices, segmented access to data stores, and monitoring for anomalous behavior.
   - Check for Zero Trust implementation patterns:
     - Service mesh authentication (mTLS between services).
     - Token-based authentication with short-lived tokens (JWT expiration <= 15 minutes).
     - API gateway enforcement with rate limiting and request validation.
     - Microsegmentation in network policies (if Kubernetes manifests or infrastructure-as-code are present).
   - Flag any reliance on perimeter-only security (e.g., "trusted" internal networks, IP-based allowlists without authentication) as architectural findings.

6. **Generate SDD specification for remediation**
   - For all findings classified as Critical or High, generate a Software Design Document (SDD) that specifies:
     - Finding identifier (STIG V-ID, NIST control ID, CVE number, or CWE ID).
     - Current vulnerable code location (file, line number, function).
     - Description of the vulnerability and its potential impact on enterprise perations.
     - Proposed remediation approach with specific code changes.
     - Mapping to the SDD constitution's security requirements.
     - Risk assessment if the finding is deferred (for POA&M documentation).
   - Group related findings into remediation packages (e.g., all authentication findings in one package, all encryption findings in another).
   - Produce a remediation SDD per package following the template in `sdd/templates/spec.md`.
   - Include architectural guidance for systemic issues (e.g., if the application lacks a centralized authentication module, specify the design for one).

7. **Generate TDD test cases for security fixes**
   - For each remediation SDD, generate test cases that:
     - Verify the vulnerability is no longer exploitable after the fix.
     - Test boundary conditions and edge cases (e.g., password exactly 13 characters must be rejected, exactly 14 must be accepted).
     - Validate that the fix does not break existing functionality (regression tests).
     - Test for related vulnerabilities (e.g., if fixing SQL injection in one endpoint, test all endpoints for the same class of vulnerability).
   - Create test stubs organized by security domain:
     - `tests/security/test_authentication.py` (or .java, .ts): Password policy, MFA, lockout, session management.
     - `tests/security/test_input_validation.py`: Input validation, sanitization, injection prevention.
     - `tests/security/test_encryption.py`: Encryption at rest, in transit, key management.
     - `tests/security/test_audit_logging.py`: Audit event generation, log format, log protection.
     - `tests/security/test_access_control.py`: RBAC enforcement, least privilege, separation of duties.
     - `tests/security/test_security_headers.py`: HTTP security headers on all response types.
   - Tests must be runnable in CI/CD and produce machine-readable results (JUnit XML, pytest XML, or Jest JSON).
   - For safety-critical systems (DO-178C), generate additional structural coverage tests per the applicable DAL requirements.

8. **Spawn Devin sessions to auto-remediate findings**
   - If remediation mode is auto-remediate, create Devin sessions via the Devin API to implement fixes:
     - Group findings by file or module to minimize context switching.
     - Create one Devin session per remediation package (e.g., one for authentication fixes, one for encryption fixes).
     - Each session receives: the remediation SDD, TDD test stubs, the source files requiring modification, and the compliance/devin/knowledge.md and compliance/devin/playbook.md as Devin Knowledge and Playbook.
     - Configure each session with the security-scan skill context and the project's constitution.
     - Limit to 10 concurrent Devin sessions per scan run to avoid resource contention.
   - For each Devin session:
     - Instruct Devin to implement the fix per the SDD specification.
     - Instruct Devin to make the TDD tests pass.
     - Instruct Devin to run the local linter and formatter.
     - Instruct Devin to create a feature branch named `security/{stig-id}-{short-description}` or `security/{nist-control}-{short-description}`.
     - Instruct Devin to commit with conventional commit format: `fix(security): remediate {finding-id} - {short-description}`.
   - Monitor all sessions for completion, collecting artifacts and test results.

9. **Invoke Devin Review on remediation PRs**
   - For each remediation PR created by Devin sessions:
     - Submit the PR to Devin Review via the devin-review-mcp.
     - Configure Devin Review with the enterprise Federal Security review ruleset:
       - STIG compliance rules mapped to the specific V-IDs being remediated.
       - NIST 800-53 control validation rules for the applicable control families.
       - OWASP Top 10 detection rules.
       - CWE Top 25 detection rules.
       - Secret detection (TruffleHog/GitLeaks patterns).
     - Review must confirm that:
       - The fix addresses the original finding.
       - The fix does not introduce new security issues.
       - The fix follows the project's coding standards.
       - All tests pass and coverage thresholds are met.
     - Address any Devin Review findings before proceeding.
     - If Devin Review identifies new findings, loop back to step 6 for those findings.

10. **Execute guardrails audit and produce compliance report**
    - Run the full DevinClaw guardrails checklist against all remediation changes:
      - HG-001 (Tests Pass): All unit, integration, and security tests execute and pass.
      - HG-002 (STIG Scan Clean): Re-run the STIG scanner to confirm zero High findings on remediated code.
      - HG-003 (Lint/Format Pass): Linter and formatter report zero errors.
      - HG-004 (Coverage Threshold): Code coverage >= 80% for new/modified code.
      - HG-005 (No Secrets): Secret scanner reports zero findings.
      - HG-006 (Dependency Scan): No Critical/High CVEs in dependencies.
      - HG-007 (Signed Commits): All commits are GPG-signed.
      - HG-008 (Audit Trail Complete): Session audit log contains all required events.
      - HG-010 (NIST Controls Met): All applicable NIST 800-53 controls validated.
    - Generate the compliance report containing:
      - Executive summary with overall compliance posture (pass/fail/partial).
      - Scan results summary: total findings by severity, findings remediated, findings remaining.
      - STIG compliance matrix: each V-ID with pass/fail status and evidence.
      - NIST 800-53 control assessment: each control with implementation status and evidence.
      - FedRAMP readiness assessment: baseline coverage percentage and gaps.
      - Zero Trust maturity assessment: current posture and recommendations.
      - POA&M entries for any findings not remediated in this scan cycle.
      - Delta comparison with previous scan (if baseline existed).
    - Store the report in the repository under `docs/compliance/` with the naming convention `{app-name}-security-scan-{YYYY-MM-DD}.md`.
    - Attach XCCDF scan results, test results (JUnit XML), and coverage reports as artifacts.
    - Update DeepWiki with scan findings and remediation learnings for future sessions.

## Specifications
- **STIG benchmark version**: Use the latest available DISA STIG benchmark for each technology in the stack. If the exact technology STIG is not available, apply the Application Security and Development STIG (V-222386 series) as the general baseline.
- **NIST 800-53 revision**: Use NIST 800-53 Rev. 5 (September 2020) control catalog. Map all controls to the applicable baseline per FIPS 199 categorization.
- **FedRAMP baselines**: Use the current FedRAMP Security Controls Baseline documents (Rev. 5). Apply FedRAMP-specific parameter values where they differ from NIST defaults.
- **Scan output format**: STIG scan results must be produced in XCCDF 1.2 format for import into eMASS or CSAM. NIST control assessments must be produced in OSCAL JSON format where possible.
- **Severity classification**: Use DISA severity categories: CAT I (Critical/High -- exploitable vulnerability that directly leads to unauthorized access), CAT II (Medium -- vulnerability that could lead to unauthorized access with additional information), CAT III (Low -- vulnerability that degrades security posture).
- **Remediation SLA**: CAT I findings must be remediated within 30 days. CAT II findings within 90 days. CAT III findings within 180 days. These align with DISA STIG timelines and enterprise security officer expectations.
- **Coverage for security tests**: Security test coverage must be 100% for code paths implementing security controls (authentication, authorization, encryption, input validation). Overall coverage threshold remains 80%.
- **DO-178C applicability**: For safety-critical systems (DAL A through DAL C), structural coverage analysis (MC/DC for DAL A, decision coverage for DAL B, statement coverage for DAL C) must be performed on security-relevant code.
- **Classification**: All scan reports must be marked UNCLASSIFIED // FOR OFFICIAL USE ONLY (U//FOUO) unless otherwise directed. Scan results may contain Sensitive Security Information (SSI) and must be handled per 49 CFR Part 1520.
- **Retention**: Scan results and compliance artifacts must be retained for the duration of the ATO plus 3 years per FAR 4.703 and NIST 800-53 AU-11.
- **Concurrency**: Maximum 10 concurrent Devin remediation sessions per scan run. Maximum 5 concurrent SonarQube scans to avoid overloading the analysis server.

## Advice and Pointers
- Always run the scan against the full codebase on the first pass, even if the user requests a targeted scan. The initial full scan establishes the baseline. Subsequent scans can be targeted.
- STIG findings often cluster. If you find one SQL injection vulnerability, assume there are more throughout the codebase and scan all database access patterns, not just the one file where the finding occurred.
- enterprise systems frequently use CAC/PIV (Common Access Card / Personal Identity Verification) for authentication. When scanning IA controls, check for CAC middleware integration (e.g., mod_ssl with client certificate authentication, PKCS#11 configurations).
- Many legacy enterprise applications were built before current STIG baselines existed. Expect a high volume of findings on initial scan. Prioritize CAT I findings and create a realistic POA&M for CAT II and CAT III.
- SonarQube quality profiles should be configured before scanning. The default profiles miss many federal-specific rules. Ensure the enterprise Federal Security ruleset is active.
- When scanning Java applications, pay special attention to deserialization vulnerabilities (CWE-502). Many enterprise applications use older versions of Apache Commons, Jackson, or XStream that are vulnerable.
- When scanning COBOL-to-Java converted code, check that packed decimal handling does not introduce arithmetic overflow vulnerabilities. COBOL's fixed-point arithmetic has different overflow behavior than Java's BigDecimal.
- Zero Trust validation is particularly important for enterprise applications that span multiple security enclaves (e.g., enterprise operational systems connecting to administrative systems). Network segmentation alone is insufficient.
- For safety-critical systems under DO-178C, coordinate with the Designated Engineering Representative (DER) before auto-remediating findings. Safety-critical code changes require additional verification beyond standard STIG compliance.
- The FedRAMP PMO periodically updates baseline requirements. Check for baseline revisions before submitting ATO packages. A scan against an outdated baseline will be rejected.

## Forbidden Actions
- Do not skip the STIG scan step. Every codebase scan must include STIG benchmark validation regardless of the user's requested scope. STIG compliance is a hard gate in the DevinClaw guardrails (HG-002).
- Do not auto-remediate findings in safety-critical systems (DO-178C DAL A through DAL C) without explicit user approval. Safety-critical code changes require human-in-the-loop verification and DER sign-off.
- Do not suppress or downgrade the severity of STIG findings. Severity classifications are set by DISA and cannot be altered. If a finding is believed to be a false positive, document it as such with evidence but do not change its severity.
- Do not store scan results containing vulnerability details in publicly accessible locations. Scan results must be stored in access-controlled directories and marked with appropriate handling caveats.
- Do not scan production systems directly. Scans must be performed against code repositories or staging environments. If runtime scanning is required, coordinate with the enterprise ISSO and obtain explicit authorization.
- Do not generate remediation code that disables security controls, even temporarily. Fixes must maintain or strengthen the security posture at every intermediate step.
- Do not commit scan results or compliance reports that contain Sensitive Security Information (SSI) to unprotected Git branches. Use encrypted storage or access-controlled artifact repositories.
- Do not ignore Zero Trust validation findings. Even if all STIG and NIST controls pass, perimeter-only security architectures represent a systemic risk that must be documented and addressed.
- Do not run more than 10 concurrent Devin remediation sessions or 5 concurrent SonarQube scans. Resource contention degrades scan accuracy and session reliability.
- Do not produce a compliance report without completing all prior scan and validation steps. Partial reports create a false sense of compliance and endanger ATO renewals.

---
*Generated by DevinClaw Skills Parser at 2026-02-25T06:27:28Z*
*Source: skills/security-scan/SKILL.md*
