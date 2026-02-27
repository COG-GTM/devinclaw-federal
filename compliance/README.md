# DevinClaw Federal Security Compliance Framework

> Centralized STIG, NIST 800-53, and Zero Trust compliance for the enterprise federal modernization with Devin, adapted for the DevinClaw platform.

## Platform Authorization Status

| Platform | FedRAMP Status | IL Level | Use Case |
|----------|----------------|----------|----------|
| **Devin** | Not FedRAMP Certified | N/A | Generate compliant code patterns, autonomous modernization agents |

## Quick Start

### For Devin Users
1. Copy `devin/knowledge.md` to Devin Knowledge
2. Copy `devin/playbook.md` to Devin Playbooks
3. Copy `devin/zero-trust-knowledge.md` to Devin Knowledge (Zero Trust)
4. Copy `devin/zero-trust-playbook.md` to Devin Playbooks (Zero Trust)
5. Done -- Devin will generate Zero Trust compliant code for enterprise modernization tasks.

3. Done -- Cascade will enforce Zero Trust compliance automatically.

## What's Included

| File | Purpose |
|------|---------|
| `devin/knowledge.md` | Security knowledge base for Devin agents |
| `devin/playbook.md` | Secure development workflow for Devin |
| `devin/zero-trust-knowledge.md` | Zero Trust principles for Devin |
| `devin/zero-trust-playbook.md` | Zero Trust workflow for Devin |
| `templates/` | Reusable secure Python modules |
| `tests/` | Automated compliance verification tests |
| `docs/` | Architecture and compliance documentation |

## Compliance Coverage

- **Zero Trust Architecture** -- NIST SP 800-207 implementation
- **STIG** -- All 18 security categories
- **NIST 800-53** -- AC, AU, IA, SC, SI control families
- **FedRAMP** -- Moderate and High baseline
- **Federal Enterprise Modernization** -- Aligned with Executive Order 14028 and enterprise systems modernization requirements

## Zero Trust Architecture

This framework implements **NIST SP 800-207 Zero Trust Architecture** principles for DevinClaw's autonomous modernization agents:

| Principle | Implementation | Why It Matters |
|-----------|----------------|----------------|
| **Never Trust, Always Verify** | Continuous session verification | Tokens can be stolen mid-session |
| **IP-Bound Sessions** | Sessions tied to originating IP | Stolen tokens useless from different IP |
| **Session Regeneration** | New session ID after auth | Prevents session fixation attacks |
| **15-Minute Timeout** | Sessions expire per STIG V-220630 | Limits attack window |
| **Least Privilege** | Default deny, explicit grants | Limits blast radius of compromise |
| **Full Audit Trail** | Every action logged | Forensics and compliance |

### Zero Trust Flow

```
Request --> Verify Session --> Check IP Binding --> Check Timeout --> Authorize --> Process --> Log
              |                    |                  |               |
           Missing?            Mismatch?           Expired?        Denied?
              |                    |                  |               |
           REJECT              DESTROY +           REJECT          REJECT
                               LOG ALERT
```

## Key Security Controls

| Control | Implementation | Federal Mapping |
|---------|----------------|-----------------|
| Input Validation | Whitelist validation, sanitization | STIG V-220631, NIST SI-10 |
| Authentication | 14+ char passwords, MFA, CAC/PIV | STIG V-220629, NIST IA-2 |
| Session Security | 15 min timeout, IP binding | STIG V-220630, NIST AC-12 |
| Encryption | AES-256 at rest, TLS 1.2+ in transit | STIG V-220633/34, NIST SC-8/28 |
| Audit Logging | JSON format, all security events | STIG V-220635, NIST AU-2/3 |
| Security Headers | HSTS, CSP, X-Frame-Options | STIG V-220641, NIST SI-11 |

## Templates

### Python Security Modules
- `security_utils.py` -- Input validation, sanitization, rate limiting
- `auth_manager.py` -- Authentication, sessions, password policies
- `audit_logger.py` -- Structured audit logging
- `zero_trust_middleware.py` -- IP binding, continuous verification, session management
- `cac_piv_handler.py` -- CAC/PIV certificate authentication for DoD/enterprise systems

## Testing

Run the compliance test suite:

```bash
# Run all Zero Trust tests
pytest compliance/tests/test_zero_trust.py -v

# Run with coverage
pytest compliance/tests/ -v --cov=compliance/templates

# Run specific test class
pytest compliance/tests/test_zero_trust.py::TestIPBoundSessions -v
```

### What Tests Verify

| Test | Zero Trust Principle |
|------|---------------------|
| `TestIPBoundSessions` | Sessions reject requests from different IPs |
| `TestSessionTimeout` | Sessions expire after 15 minutes |
| `TestSessionRegeneration` | New session ID generated after login |
| `TestContinuousVerification` | Every request must have valid session |
| `TestAuditLogging` | Security events are properly logged |
| `TestAccountLockout` | Account lockout after 5 failed attempts |
| `TestSessionSecurity` | Session IDs are cryptographically random |

---

**Classification: UNCLASSIFIED**
**Adapted for DevinClaw enterprise Federal Modernization**
