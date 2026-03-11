"""CAC/PIV Certificate Authentication — X.509 smart card auth stub.

Federal environments (DoD IL4-IL6) require CAC (Common Access Card) or
PIV (Personal Identity Verification) smart card authentication per
HSPD-12 and FIPS 201-3.

This module provides the interface contract and certificate parsing logic.
The actual TLS client-certificate negotiation happens at the reverse proxy
(nginx / HAProxy) layer; this module validates the forwarded certificate
fields.

STIG V-220629 (IA-2): Multi-factor authentication for privileged accounts.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger("devinclaw.cac_piv")


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------


@dataclass
class CertificateInfo:
    """Parsed X.509 certificate fields from a CAC/PIV card."""

    subject_dn: str = ""  # e.g. "CN=DOE.JOHN.1234567890,OU=DoD,O=U.S. Government"
    issuer_dn: str = ""  # e.g. "CN=DOD ID CA-59,OU=PKI,O=U.S. Government"
    serial_number: str = ""
    not_before: datetime | None = None
    not_after: datetime | None = None
    edipi: str = ""  # 10-digit DoD Electronic Data Interchange Personal Identifier
    email: str = ""
    common_name: str = ""
    organisation: str = ""
    key_usage: list[str] = field(default_factory=list)
    extended_key_usage: list[str] = field(default_factory=list)
    fingerprint_sha256: str = ""
    is_valid: bool = False
    validation_errors: list[str] = field(default_factory=list)


@dataclass
class CACAuthResult:
    """Result of CAC/PIV authentication attempt."""

    authenticated: bool = False
    certificate: CertificateInfo | None = None
    user_id: str | None = None
    edipi: str = ""
    method: str = "cac_piv"
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    errors: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Certificate parsing
# ---------------------------------------------------------------------------

# Regex for EDIPI extraction from DoD subject DN
_EDIPI_PATTERN = re.compile(r"CN=[\w.]+\.(\d{10})")

# Regex for email extraction from subject DN or SAN
_EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")


def parse_certificate_headers(headers: dict[str, str]) -> CertificateInfo:
    """Parse X.509 certificate fields from reverse-proxy forwarded headers.

    Nginx / HAProxy forwards client certificate info via headers such as:
      - X-SSL-Client-S-DN (subject DN)
      - X-SSL-Client-I-DN (issuer DN)
      - X-SSL-Client-Serial
      - X-SSL-Client-Not-Before / X-SSL-Client-Not-After
      - X-SSL-Client-Verify (SUCCESS | FAILED:reason)
      - X-SSL-Client-Fingerprint

    Returns a CertificateInfo with parsed fields and validation status.
    """
    cert = CertificateInfo()

    cert.subject_dn = headers.get("X-SSL-Client-S-DN", headers.get("x-ssl-client-s-dn", ""))
    cert.issuer_dn = headers.get("X-SSL-Client-I-DN", headers.get("x-ssl-client-i-dn", ""))
    cert.serial_number = headers.get("X-SSL-Client-Serial", headers.get("x-ssl-client-serial", ""))
    cert.fingerprint_sha256 = headers.get(
        "X-SSL-Client-Fingerprint", headers.get("x-ssl-client-fingerprint", "")
    )

    # Parse dates
    for date_header, attr in [
        ("X-SSL-Client-Not-Before", "not_before"),
        ("X-SSL-Client-Not-After", "not_after"),
    ]:
        raw = headers.get(date_header, headers.get(date_header.lower(), ""))
        if raw:
            try:
                setattr(cert, attr, datetime.fromisoformat(raw))
            except ValueError:
                cert.validation_errors.append(f"Invalid date format in {date_header}: {raw}")

    # Extract EDIPI from subject DN
    edipi_match = _EDIPI_PATTERN.search(cert.subject_dn)
    if edipi_match:
        cert.edipi = edipi_match.group(1)

    # Extract email
    email_match = _EMAIL_PATTERN.search(cert.subject_dn)
    if email_match:
        cert.email = email_match.group(0)

    # Extract CN
    cn_match = re.search(r"CN=([^,]+)", cert.subject_dn)
    if cn_match:
        cert.common_name = cn_match.group(1)

    # Extract O
    org_match = re.search(r"O=([^,]+)", cert.subject_dn)
    if org_match:
        cert.organisation = org_match.group(1)

    # Validate
    verify_status = headers.get("X-SSL-Client-Verify", headers.get("x-ssl-client-verify", ""))
    cert.is_valid = _validate_certificate(cert, verify_status)

    return cert


def _validate_certificate(cert: CertificateInfo, verify_status: str) -> bool:
    """Validate certificate fields and proxy verification status."""
    errors = cert.validation_errors

    # Check proxy-level verification
    if verify_status and verify_status.upper() != "SUCCESS":
        errors.append(f"Proxy verification failed: {verify_status}")

    # Must have subject DN
    if not cert.subject_dn:
        errors.append("Missing subject DN")

    # Must have issuer (should be a DoD CA)
    if not cert.issuer_dn:
        errors.append("Missing issuer DN")

    # Check expiry
    now = datetime.now(UTC)
    if cert.not_after and cert.not_after.replace(tzinfo=UTC) < now:
        errors.append("Certificate expired")
    if cert.not_before and cert.not_before.replace(tzinfo=UTC) > now:
        errors.append("Certificate not yet valid")

    return len(errors) == 0


# ---------------------------------------------------------------------------
# Authentication flow
# ---------------------------------------------------------------------------


async def authenticate_cac(
    headers: dict[str, str],
    user_lookup: Any | None = None,
) -> CACAuthResult:
    """Authenticate a user via CAC/PIV certificate.

    Args:
        headers: HTTP headers forwarded by the reverse proxy.
        user_lookup: Optional async callable(edipi: str) -> user_id | None.

    Returns:
        CACAuthResult with authentication outcome.
    """
    cert = parse_certificate_headers(headers)
    result = CACAuthResult(certificate=cert, edipi=cert.edipi)

    if not cert.is_valid:
        result.errors = list(cert.validation_errors)
        logger.warning("CAC authentication failed: %s", result.errors)
        return result

    # Look up user by EDIPI
    if user_lookup and cert.edipi:
        try:
            user_id = await user_lookup(cert.edipi)
            if user_id:
                result.authenticated = True
                result.user_id = user_id
                logger.info("CAC auth success: EDIPI=%s user=%s", cert.edipi, user_id)
            else:
                result.errors.append(f"No user found for EDIPI {cert.edipi}")
                logger.warning("CAC auth: no user for EDIPI %s", cert.edipi)
        except Exception:
            logger.exception("CAC user lookup failed for EDIPI %s", cert.edipi)
            result.errors.append("User lookup failed")
    elif cert.edipi:
        # No lookup function — stub mode, accept cert as valid
        result.authenticated = True
        result.user_id = f"cac-{cert.edipi}"
        logger.info("CAC auth (stub): EDIPI=%s", cert.edipi)
    else:
        result.errors.append("No EDIPI found in certificate")

    return result
