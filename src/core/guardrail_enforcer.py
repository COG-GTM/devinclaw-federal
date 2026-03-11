"""Guardrail Enforcer — evaluates guardrail rules against task context.

Loads audit/guardrail-config.json and enforces security, process, and access guardrails.
"""

from __future__ import annotations

import json
import logging
import os
import re
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

logger = logging.getLogger("devinclaw.guardrail_enforcer")

# Credential patterns (GR-SEC-001)
CREDENTIAL_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"""(?:api[_-]?key|apikey)\s*[:=]\s*['"][A-Za-z0-9+/=]{20,}['"]""", re.IGNORECASE),
    re.compile(r"""(?:password|passwd|pwd)\s*[:=]\s*['"][^'"]{8,}['"]""", re.IGNORECASE),
    re.compile(r"""(?:secret|token)\s*[:=]\s*['"][A-Za-z0-9+/=]{20,}['"]""", re.IGNORECASE),
    re.compile(r"""(?:aws_access_key_id)\s*[:=]\s*['"]?AKIA[0-9A-Z]{16}['"]?""", re.IGNORECASE),
    re.compile(r"""(?:aws_secret_access_key)\s*[:=]\s*['"]?[A-Za-z0-9/+=]{40}['"]?""", re.IGNORECASE),
    re.compile(r"""ghp_[A-Za-z0-9]{36}"""),
    re.compile(r"""-----BEGIN (?:RSA |EC |DSA )?PRIVATE KEY-----"""),
]

# PII / SSN patterns (GR-SEC-002)
PII_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"""\b\d{3}-\d{2}-\d{4}\b"""),  # SSN
    re.compile(r"""\b\d{9}\b"""),  # SSN without dashes (context-dependent)
    re.compile(
        r"""\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"""
    ),  # Email (flagged in code comments)
]

# TLS minimum version patterns (GR-SEC-003)
INSECURE_TLS_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"""SSLv[23]""", re.IGNORECASE),
    re.compile(r"""TLSv1(?:\.0|\.1)?(?:\b|[^.2-9])""", re.IGNORECASE),
    re.compile(r"""ssl\.PROTOCOL_TLSv1(?:_1)?""", re.IGNORECASE),
    re.compile(r"""MinVersion:\s*tls\.VersionTLS1[01]""", re.IGNORECASE),
]


class GuardrailSeverity(StrEnum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class GuardrailAction(StrEnum):
    BLOCK_MERGE = "block_merge"
    BLOCK_SESSION = "block_session"
    ALERT = "alert"
    WARN = "warn"


@dataclass
class GuardrailRule:
    """A single guardrail rule."""

    rule_id: str
    name: str
    severity: GuardrailSeverity
    description: str
    action: GuardrailAction


@dataclass
class GuardrailResult:
    """Result of evaluating a single guardrail."""

    rule_id: str
    name: str
    passed: bool
    severity: GuardrailSeverity
    action: GuardrailAction
    details: str = ""
    findings: list[str] = field(default_factory=list)


@dataclass
class TaskContext:
    """Context for guardrail evaluation."""

    code_files: dict[str, str] = field(default_factory=dict)  # path -> content
    spec_exists: bool = False
    tests_exist: bool = False
    review_complete: bool = False
    coverage_percent: float = 0.0
    pr_description: str = ""
    target_repos: list[str] = field(default_factory=list)
    approved_repos: list[str] = field(default_factory=list)
    tls_configs: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class GuardrailEnforcer:
    """Loads and enforces guardrail rules."""

    def __init__(self, audit_dir: str = "audit") -> None:
        self.audit_dir = audit_dir
        self.rules: list[GuardrailRule] = []

    def load(self) -> None:
        """Load guardrail rules from audit/guardrail-config.json."""
        config_path = os.path.join(self.audit_dir, "guardrail-config.json")
        if not os.path.exists(config_path):
            logger.warning("guardrail-config.json not found at %s", config_path)
            return

        with open(config_path) as f:
            data = json.load(f)

        self.rules = []
        for entry in data.get("guardrails", []):
            self.rules.append(
                GuardrailRule(
                    rule_id=entry["id"],
                    name=entry["name"],
                    severity=GuardrailSeverity(entry.get("severity", "MEDIUM")),
                    description=entry.get("description", ""),
                    action=GuardrailAction(entry.get("action", "warn")),
                )
            )
        logger.info("Loaded %d guardrail rules", len(self.rules))

    def evaluate_guardrails(self, context: TaskContext) -> list[GuardrailResult]:
        """Evaluate all guardrail rules against the task context."""
        results: list[GuardrailResult] = []

        for rule in self.rules:
            result = self._evaluate_rule(rule, context)
            results.append(result)

        return results

    def _evaluate_rule(self, rule: GuardrailRule, context: TaskContext) -> GuardrailResult:
        """Evaluate a single rule against context."""
        evaluators = {
            "GR-SEC-001": self._check_no_credentials,
            "GR-SEC-002": self._check_no_pii,
            "GR-SEC-003": self._check_tls_version,
            "GR-SEC-004": self._check_fips_crypto,
            "GR-PROC-001": self._check_spec_required,
            "GR-PROC-002": self._check_tests_required,
            "GR-PROC-003": self._check_review_required,
            "GR-PROC-004": self._check_coverage_minimum,
            "GR-PROC-005": self._check_pr_description,
            "GR-ACCESS-001": self._check_no_production_access,
            "GR-ACCESS-002": self._check_approved_repos,
        }

        evaluator = evaluators.get(rule.rule_id)
        if evaluator:
            return evaluator(rule, context)

        # Unknown rule — pass by default with warning
        return GuardrailResult(
            rule_id=rule.rule_id,
            name=rule.name,
            passed=True,
            severity=rule.severity,
            action=rule.action,
            details=f"No evaluator for {rule.rule_id} — passing by default",
        )

    def _check_no_credentials(self, rule: GuardrailRule, context: TaskContext) -> GuardrailResult:
        """GR-SEC-001: No hardcoded credentials in code files."""
        findings: list[str] = []
        for filepath, content in context.code_files.items():
            for pattern in CREDENTIAL_PATTERNS:
                matches = pattern.findall(content)
                for match in matches:
                    findings.append(f"{filepath}: {match[:50]}...")

        return GuardrailResult(
            rule_id=rule.rule_id,
            name=rule.name,
            passed=len(findings) == 0,
            severity=rule.severity,
            action=rule.action,
            details=f"Found {len(findings)} credential pattern(s)" if findings else "Clean",
            findings=findings,
        )

    def _check_no_pii(self, rule: GuardrailRule, context: TaskContext) -> GuardrailResult:
        """GR-SEC-002: No PII/SSN in code or comments."""
        findings: list[str] = []
        for filepath, content in context.code_files.items():
            for pattern in PII_PATTERNS:
                matches = pattern.findall(content)
                for match in matches:
                    findings.append(f"{filepath}: potential PII ({match[:30]}...)")

        return GuardrailResult(
            rule_id=rule.rule_id,
            name=rule.name,
            passed=len(findings) == 0,
            severity=rule.severity,
            action=rule.action,
            details=f"Found {len(findings)} potential PII pattern(s)" if findings else "Clean",
            findings=findings,
        )

    def _check_tls_version(self, rule: GuardrailRule, context: TaskContext) -> GuardrailResult:
        """GR-SEC-003: TLS 1.2+ required."""
        findings: list[str] = []
        for filepath, content in context.code_files.items():
            for pattern in INSECURE_TLS_PATTERNS:
                matches = pattern.findall(content)
                for match in matches:
                    findings.append(f"{filepath}: insecure TLS ({match})")

        return GuardrailResult(
            rule_id=rule.rule_id,
            name=rule.name,
            passed=len(findings) == 0,
            severity=rule.severity,
            action=rule.action,
            details=f"Found {len(findings)} insecure TLS config(s)" if findings else "TLS 1.2+ OK",
            findings=findings,
        )

    def _check_fips_crypto(self, rule: GuardrailRule, context: TaskContext) -> GuardrailResult:
        """GR-SEC-004: FIPS 140-2 approved algorithms only."""
        # Simplified check — flag non-FIPS algorithms
        non_fips = ["md5", "des", "rc4", "blowfish"]
        findings: list[str] = []
        for filepath, content in context.code_files.items():
            content_lower = content.lower()
            for algo in non_fips:
                if algo in content_lower:
                    findings.append(f"{filepath}: non-FIPS algorithm '{algo}'")

        return GuardrailResult(
            rule_id=rule.rule_id,
            name=rule.name,
            passed=len(findings) == 0,
            severity=rule.severity,
            action=rule.action,
            details=f"Found {len(findings)} non-FIPS algorithm(s)" if findings else "FIPS OK",
            findings=findings,
        )

    def _check_spec_required(self, rule: GuardrailRule, context: TaskContext) -> GuardrailResult:
        """GR-PROC-001: SDD spec must exist before implementation."""
        return GuardrailResult(
            rule_id=rule.rule_id,
            name=rule.name,
            passed=context.spec_exists,
            severity=rule.severity,
            action=rule.action,
            details="Spec exists" if context.spec_exists else "No SDD specification found",
        )

    def _check_tests_required(self, rule: GuardrailRule, context: TaskContext) -> GuardrailResult:
        """GR-PROC-002: Tests must exist before code merges."""
        return GuardrailResult(
            rule_id=rule.rule_id,
            name=rule.name,
            passed=context.tests_exist,
            severity=rule.severity,
            action=rule.action,
            details="Tests exist" if context.tests_exist else "No test files found",
        )

    def _check_review_required(self, rule: GuardrailRule, context: TaskContext) -> GuardrailResult:
        """GR-PROC-003: Devin Review must complete on every PR."""
        return GuardrailResult(
            rule_id=rule.rule_id,
            name=rule.name,
            passed=context.review_complete,
            severity=rule.severity,
            action=rule.action,
            details="Review complete" if context.review_complete else "Review not complete",
        )

    def _check_coverage_minimum(self, rule: GuardrailRule, context: TaskContext) -> GuardrailResult:
        """GR-PROC-004: Branch coverage meets category thresholds (80%)."""
        threshold = 80.0
        passed = context.coverage_percent >= threshold
        return GuardrailResult(
            rule_id=rule.rule_id,
            name=rule.name,
            passed=passed,
            severity=rule.severity,
            action=rule.action,
            details=f"Coverage: {context.coverage_percent:.1f}% (threshold: {threshold}%)",
        )

    def _check_pr_description(self, rule: GuardrailRule, context: TaskContext) -> GuardrailResult:
        """GR-PROC-005: PR must include description."""
        has_desc = len(context.pr_description.strip()) > 20
        return GuardrailResult(
            rule_id=rule.rule_id,
            name=rule.name,
            passed=has_desc,
            severity=rule.severity,
            action=rule.action,
            details="PR description present" if has_desc else "PR description missing or too short",
        )

    def _check_no_production_access(self, rule: GuardrailRule, context: TaskContext) -> GuardrailResult:
        """GR-ACCESS-001: No production system access."""
        prod_indicators = ["prod", "production", "live"]
        findings: list[str] = []
        for repo in context.target_repos:
            repo_lower = repo.lower()
            for indicator in prod_indicators:
                if indicator in repo_lower:
                    findings.append(f"Target repo appears to be production: {repo}")

        return GuardrailResult(
            rule_id=rule.rule_id,
            name=rule.name,
            passed=len(findings) == 0,
            severity=rule.severity,
            action=rule.action,
            details="No production access detected" if not findings else "Production access detected",
            findings=findings,
        )

    def _check_approved_repos(self, rule: GuardrailRule, context: TaskContext) -> GuardrailResult:
        """GR-ACCESS-002: Sessions can only access pre-approved repos."""
        if not context.approved_repos:
            # No approved list configured — pass with warning
            return GuardrailResult(
                rule_id=rule.rule_id,
                name=rule.name,
                passed=True,
                severity=rule.severity,
                action=rule.action,
                details="No approved repos list configured — skipping check",
            )

        unapproved = [r for r in context.target_repos if r not in context.approved_repos]
        return GuardrailResult(
            rule_id=rule.rule_id,
            name=rule.name,
            passed=len(unapproved) == 0,
            severity=rule.severity,
            action=rule.action,
            details=f"Unapproved repos: {unapproved}" if unapproved else "All repos approved",
            findings=unapproved,
        )
