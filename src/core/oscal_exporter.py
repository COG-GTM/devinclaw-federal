"""OSCAL Exporter — NIST OSCAL System Security Plan (SSP) export.

Generates machine-readable OSCAL JSON for ATO (Authorization to Operate)
packages.  OSCAL (Open Security Controls Assessment Language) is the
NIST standard for expressing security plans, assessments, and results.

Supports:
  - System Security Plan (SSP) export
  - Control implementation statements
  - Component inventory
  - NIST 800-53 Rev 5 control mappings
"""

from __future__ import annotations

import json
import logging
import os
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

logger = logging.getLogger("devinclaw.oscal")


# ---------------------------------------------------------------------------
# NIST 800-53 Rev 5 control mappings for DevinClaw components
# ---------------------------------------------------------------------------

CONTROL_IMPLEMENTATIONS: list[dict[str, Any]] = [
    {
        "control_id": "ac-2",
        "title": "Account Management",
        "description": "User accounts managed via RBAC with four roles (admin, engineer, viewer, auditor). "
        "Account creation requires admin approval. Inactive accounts disabled after 90 days.",
        "status": "implemented",
        "component": "auth-service",
    },
    {
        "control_id": "ac-7",
        "title": "Unsuccessful Logon Attempts",
        "description": "Account lockout after 5 failed attempts with 15-minute lockout duration. "
        "All failed attempts logged with timestamp, IP, and user identifier.",
        "status": "implemented",
        "component": "auth-service",
    },
    {
        "control_id": "ac-12",
        "title": "Session Termination",
        "description": "Sessions terminate after 15 minutes of inactivity (STIG V-220630). "
        "Inactivity tracked per-request via middleware. Session invalidated on logout.",
        "status": "implemented",
        "component": "session-middleware",
    },
    {
        "control_id": "au-2",
        "title": "Event Logging",
        "description": "All security-relevant events logged in structured JSON format with "
        "correlation IDs. Events include auth, access, modification, and admin actions.",
        "status": "implemented",
        "component": "audit-service",
    },
    {
        "control_id": "au-3",
        "title": "Content of Audit Records",
        "description": "Audit records include: timestamp, event type, user ID, IP address, "
        "outcome, correlation ID, and SHA-256 hash for tamper evidence.",
        "status": "implemented",
        "component": "audit-service",
    },
    {
        "control_id": "au-9",
        "title": "Protection of Audit Information",
        "description": "Audit entries are append-only with SHA-256 hashing per entry. "
        "Evidence packs are digitally signed. Retention per FAR 4.703.",
        "status": "implemented",
        "component": "audit-service",
    },
    {
        "control_id": "ia-2",
        "title": "Identification and Authentication",
        "description": "Multi-factor authentication supported via CAC/PIV smart card certificates "
        "(X.509) and password-based auth with bcrypt-12 hashing.",
        "status": "partially-implemented",
        "component": "auth-service",
    },
    {
        "control_id": "ia-5",
        "title": "Authenticator Management",
        "description": "Password policy: 14+ characters, uppercase, lowercase, digit, special char. "
        "Passwords hashed with bcrypt (12 rounds). API keys SHA-256 hashed.",
        "status": "implemented",
        "component": "auth-service",
    },
    {
        "control_id": "sc-8",
        "title": "Transmission Confidentiality and Integrity",
        "description": "All communications require TLS 1.2+. JWT tokens include IP binding. "
        "WebSocket connections authenticated before data exchange.",
        "status": "implemented",
        "component": "network-layer",
    },
    {
        "control_id": "sc-28",
        "title": "Protection of Information at Rest",
        "description": "Sensitive data encrypted at rest using AES-256. Devin API keys stored "
        "in encrypted columns. Vault abstraction for secrets management.",
        "status": "implemented",
        "component": "data-layer",
    },
    {
        "control_id": "si-10",
        "title": "Information Input Validation",
        "description": "All user inputs validated via Pydantic models with strict type checking. "
        "Guardrail engine scans for injection patterns, PII, and credentials.",
        "status": "implemented",
        "component": "guardrail-engine",
    },
    {
        "control_id": "si-11",
        "title": "Error Handling",
        "description": "Generic error messages returned to users. Detailed errors logged internally "
        "with stack traces. Security headers enforced on all responses.",
        "status": "implemented",
        "component": "api-gateway",
    },
    {
        "control_id": "sr-4",
        "title": "Provenance",
        "description": "CycloneDX SBOM generated for all dependencies (EO 14028). "
        "Evidence packs include artifact SHA-256 hashes and build provenance.",
        "status": "implemented",
        "component": "sbom-generator",
    },
]


# ---------------------------------------------------------------------------
# SSP generation
# ---------------------------------------------------------------------------


def generate_ssp(
    system_name: str = "DevinClaw Federal Orchestrator",
    system_id: str = "",
    authorization_boundary: str = "FedRAMP Moderate",
    impact_level: str = "moderate",
) -> dict[str, Any]:
    """Generate an OSCAL System Security Plan (SSP) in JSON format.

    Conforms to NIST OSCAL SSP model (oscal-ssp-schema 1.1.2).
    """
    if not system_id:
        system_id = str(uuid4())

    timestamp = datetime.now(UTC).isoformat()

    # Build control implementation statements
    implemented_reqs: list[dict[str, Any]] = []
    for ctrl in CONTROL_IMPLEMENTATIONS:
        implemented_reqs.append({
            "uuid": str(uuid4()),
            "control-id": ctrl["control_id"],
            "statements": [
                {
                    "statement-id": f"{ctrl['control_id']}_smt",
                    "uuid": str(uuid4()),
                    "description": ctrl["description"],
                }
            ],
            "props": [
                {"name": "implementation-status", "value": ctrl["status"]},
                {"name": "responsible-component", "value": ctrl["component"]},
            ],
        })

    # Build component inventory
    components: list[dict[str, Any]] = [
        {
            "uuid": str(uuid4()),
            "type": "software",
            "title": "DevinClaw API Server",
            "description": "FastAPI backend providing orchestration, auth, audit, and compliance APIs",
            "props": [{"name": "version", "value": "1.0.0"}],
            "status": {"state": "operational"},
        },
        {
            "uuid": str(uuid4()),
            "type": "software",
            "title": "DevinClaw Dashboard",
            "description": "Next.js frontend with embedded terminal and compliance visualisations",
            "props": [{"name": "version", "value": "1.0.0"}],
            "status": {"state": "operational"},
        },
        {
            "uuid": str(uuid4()),
            "type": "software",
            "title": "PostgreSQL Database",
            "description": "Primary data store for users, sessions, audit entries",
            "props": [{"name": "version", "value": "16"}],
            "status": {"state": "operational"},
        },
        {
            "uuid": str(uuid4()),
            "type": "software",
            "title": "Redis Cache",
            "description": "Job queue and session cache for the scheduler",
            "props": [{"name": "version", "value": "7"}],
            "status": {"state": "operational"},
        },
    ]

    ssp: dict[str, Any] = {
        "system-security-plan": {
            "uuid": str(uuid4()),
            "metadata": {
                "title": f"System Security Plan — {system_name}",
                "last-modified": timestamp,
                "version": "1.0.0",
                "oscal-version": "1.1.2",
                "roles": [
                    {"id": "admin", "title": "System Administrator"},
                    {"id": "engineer", "title": "DevSecOps Engineer"},
                    {"id": "auditor", "title": "Compliance Auditor"},
                    {"id": "viewer", "title": "Read-Only Viewer"},
                ],
                "props": [
                    {"name": "authorization-boundary", "value": authorization_boundary},
                    {"name": "impact-level", "value": impact_level},
                ],
            },
            "system-characteristics": {
                "system-id": system_id,
                "system-name": system_name,
                "description": (
                    "AI-powered modernisation orchestrator for federal application portfolios. "
                    "Routes tasks to skills, enforces guardrails, validates SDLC, generates "
                    "compliance evidence for ATO packages."
                ),
                "security-sensitivity-level": impact_level,
                "system-information": {
                    "information-types": [
                        {
                            "title": "Controlled Unclassified Information (CUI)",
                            "description": "Source code, configuration, audit logs",
                            "confidentiality-impact": {"base": impact_level},
                            "integrity-impact": {"base": impact_level},
                            "availability-impact": {"base": impact_level},
                        }
                    ]
                },
                "authorization-boundary": {
                    "description": (
                        "The system boundary includes the FastAPI backend, Next.js dashboard, "
                        "PostgreSQL database, Redis cache, and Devin API integration. "
                        "Air-gapped deployments use CLI spoke only."
                    )
                },
            },
            "system-implementation": {
                "components": components,
            },
            "control-implementation": {
                "description": "NIST 800-53 Rev 5 control implementations for DevinClaw Federal",
                "implemented-requirements": implemented_reqs,
            },
        }
    }

    logger.info(
        "Generated OSCAL SSP: %d controls, %d components",
        len(implemented_reqs),
        len(components),
    )
    return ssp


def write_ssp(
    output_path: str,
    system_name: str = "DevinClaw Federal Orchestrator",
) -> str:
    """Generate and write OSCAL SSP to file.  Returns the output path."""
    ssp = generate_ssp(system_name=system_name)
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(ssp, f, indent=2)
    logger.info("OSCAL SSP written to %s", output_path)
    return output_path
