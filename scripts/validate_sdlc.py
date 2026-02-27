#!/usr/bin/env python3
"""SDLC Validation Script — checks task completion against sdlc-checklist.json.

Usage:
    python validate_sdlc.py --workdir /path/to/repo [--spec spec.md] [--strict]

Checks:
    SDLC-001: Spec file exists
    SDLC-002: Test files exist
    SDLC-003: Tests pass (runs mvn test, npm test, or pytest)
    SDLC-007: Security scan completed
    SDLC-010: PR description exists
"""

import argparse
import json
import os
import subprocess
import sys
import glob


def check_spec_exists(workdir, spec_path):
    """SDLC-001: SDD spec document exists."""
    candidates = [spec_path, "spec.md", "SPEC.md", "docs/spec.md", "sdd/spec.md"]
    for c in candidates:
        if os.path.exists(os.path.join(workdir, c)):
            return True, f"Found: {c}"
    return False, "No spec file found"


def check_tests_exist(workdir):
    """SDLC-002: Test files exist."""
    patterns = [
        "src/test/**/*.java", "src/test/**/*.py",
        "**/*.test.ts", "**/*.test.js", "**/*.spec.ts",
        "__tests__/**/*", "tests/**/*.py", "test/**/*.py",
    ]
    for pattern in patterns:
        matches = glob.glob(os.path.join(workdir, pattern), recursive=True)
        if matches:
            return True, f"Found {len(matches)} test file(s) matching {pattern}"
    return False, "No test files found"


def check_tests_pass(workdir):
    """SDLC-003: All tests passing."""
    if os.path.exists(os.path.join(workdir, "pom.xml")):
        cmd = ["mvn", "test", "-q"]
    elif os.path.exists(os.path.join(workdir, "package.json")):
        cmd = ["npm", "test", "--", "--passWithNoTests"]
    elif os.path.exists(os.path.join(workdir, "pytest.ini")) or os.path.exists(
        os.path.join(workdir, "pyproject.toml")
    ):
        cmd = ["pytest", "-q"]
    else:
        return None, "No recognized build system (skipped)"

    try:
        result = subprocess.run(
            cmd, cwd=workdir, capture_output=True, text=True, timeout=120
        )
        if result.returncode == 0:
            return True, "Tests passed"
        return False, f"Tests failed (exit {result.returncode}): {result.stderr[:200]}"
    except FileNotFoundError:
        return None, f"Build tool not installed: {cmd[0]} (skipped)"
    except subprocess.TimeoutExpired:
        return False, "Tests timed out after 120s"


def check_security_scan(workdir):
    """SDLC-007: Security scan completed."""
    scan_indicators = [
        "security-scan.json", "security-report.md", "stig-findings.md",
        "sonarqube-report.json", "owasp-report.html", "bandit-report.json",
        "spotbugs-report.xml",
    ]
    for f in scan_indicators:
        matches = glob.glob(os.path.join(workdir, "**", f), recursive=True)
        if matches:
            return True, f"Found: {matches[0]}"
    return False, "No security scan output found"


def check_pr_description(workdir):
    """SDLC-010: PR description complete."""
    pr_files = ["PR_DESCRIPTION.md", "CHANGES.md", "CHANGELOG.md"]
    for f in pr_files:
        if os.path.exists(os.path.join(workdir, f)):
            return True, f"Found: {f}"
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "-1"],
            cwd=workdir, capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0 and len(result.stdout.strip()) > 10:
            return True, f"Git commit: {result.stdout.strip()[:60]}"
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return False, "No PR description found"


def main():
    parser = argparse.ArgumentParser(description="SDLC Validation Checker")
    parser.add_argument("--workdir", required=True, help="Path to repository")
    parser.add_argument("--spec", default="spec.md", help="Spec file path")
    parser.add_argument("--strict", action="store_true", help="Fail on any non-pass")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    checks = [
        ("SDLC-001", "Spec exists", lambda: check_spec_exists(args.workdir, args.spec)),
        ("SDLC-002", "Tests exist", lambda: check_tests_exist(args.workdir)),
        ("SDLC-003", "Tests pass", lambda: check_tests_pass(args.workdir)),
        ("SDLC-007", "Security scan", lambda: check_security_scan(args.workdir)),
        ("SDLC-010", "PR description", lambda: check_pr_description(args.workdir)),
    ]

    results = []
    passed = failed = skipped = 0

    for check_id, name, fn in checks:
        status, detail = fn()
        if status is True:
            icon, passed = "✅", passed + 1
        elif status is False:
            icon, failed = "❌", failed + 1
        else:
            icon, skipped = "⏭️", skipped + 1
        results.append({"id": check_id, "name": name, "passed": status, "detail": detail})
        if not args.json:
            print(f"  {icon} {check_id} — {name}: {detail}")

    if args.json:
        print(json.dumps({"checks": results, "passed": passed, "failed": failed, "skipped": skipped}, indent=2))
    else:
        print(f"\n  Result: {passed} passed, {failed} failed, {skipped} skipped")
        verdict = "PASS" if failed == 0 else "FAIL — blocked from merge"
        print(f"  Verdict: {verdict}")

    sys.exit(1 if (args.strict and failed > 0) else 0)


if __name__ == "__main__":
    main()
