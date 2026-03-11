"""SBOM Generator — CycloneDX Software Bill of Materials.

Produces a CycloneDX 1.5 SBOM in JSON format from the project's
dependency manifest (pyproject.toml, requirements.txt, package.json).

Required by Executive Order 14028 (Improving the Nation's Cybersecurity)
Section 4(e) and NIST SP 800-218 (SSDF).
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

logger = logging.getLogger("devinclaw.sbom")


# ---------------------------------------------------------------------------
# Dependency parsers
# ---------------------------------------------------------------------------


def _parse_pyproject_toml(path: str) -> list[dict[str, str]]:
    """Extract dependencies from pyproject.toml."""
    components: list[dict[str, str]] = []
    if not os.path.exists(path):
        return components

    with open(path) as f:
        content = f.read()

    # Simple TOML parsing for dependencies section
    in_deps = False
    for line in content.splitlines():
        stripped = line.strip()
        if stripped == "dependencies = [":
            in_deps = True
            continue
        if in_deps and stripped == "]":
            in_deps = False
            continue
        if in_deps and stripped.startswith('"'):
            dep = stripped.strip('",').strip()
            name, version = _parse_dep_string(dep)
            components.append({"name": name, "version": version, "type": "library", "purl": f"pkg:pypi/{name}@{version}"})

    return components


def _parse_requirements_txt(path: str) -> list[dict[str, str]]:
    """Extract dependencies from requirements.txt."""
    components: list[dict[str, str]] = []
    if not os.path.exists(path):
        return components

    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            name, version = _parse_dep_string(line)
            components.append({"name": name, "version": version, "type": "library", "purl": f"pkg:pypi/{name}@{version}"})

    return components


def _parse_package_json(path: str) -> list[dict[str, str]]:
    """Extract dependencies from package.json."""
    components: list[dict[str, str]] = []
    if not os.path.exists(path):
        return components

    with open(path) as f:
        data = json.load(f)

    for section in ("dependencies", "devDependencies"):
        for name, version in data.get(section, {}).items():
            clean_version = version.lstrip("^~>=<")
            components.append({
                "name": name,
                "version": clean_version,
                "type": "library",
                "purl": f"pkg:npm/{name}@{clean_version}",
            })

    return components


def _parse_dep_string(dep: str) -> tuple[str, str]:
    """Parse a dependency string like 'fastapi>=0.110.0' into (name, version)."""
    for sep in (">=", "<=", "==", "~=", "!=", ">", "<"):
        if sep in dep:
            parts = dep.split(sep, 1)
            return parts[0].strip().split("[")[0], parts[1].strip().split(",")[0]
    # No version specifier
    return dep.strip().split("[")[0], "unspecified"


# ---------------------------------------------------------------------------
# CycloneDX 1.5 SBOM generation
# ---------------------------------------------------------------------------


def generate_sbom(
    project_dir: str = ".",
    project_name: str = "devinclaw-federal",
    project_version: str = "1.0.0",
) -> dict[str, Any]:
    """Generate a CycloneDX 1.5 JSON SBOM for the project.

    Scans for:
      - pyproject.toml
      - requirements.txt
      - dashboard/package.json

    Returns:
        CycloneDX 1.5 compliant JSON dict.
    """
    serial = f"urn:uuid:{uuid4()}"
    timestamp = datetime.now(UTC).isoformat()

    # Collect components from all manifests
    all_components: list[dict[str, str]] = []
    all_components.extend(_parse_pyproject_toml(os.path.join(project_dir, "pyproject.toml")))
    all_components.extend(_parse_requirements_txt(os.path.join(project_dir, "requirements.txt")))
    all_components.extend(_parse_package_json(os.path.join(project_dir, "dashboard", "package.json")))

    # Build CycloneDX components
    cdx_components: list[dict[str, Any]] = []
    for comp in all_components:
        cdx_components.append({
            "type": comp["type"],
            "name": comp["name"],
            "version": comp["version"],
            "purl": comp["purl"],
            "bom-ref": f"{comp['name']}@{comp['version']}",
        })

    sbom: dict[str, Any] = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "serialNumber": serial,
        "version": 1,
        "metadata": {
            "timestamp": timestamp,
            "tools": [
                {
                    "vendor": "DevinClaw Federal",
                    "name": "sbom-generator",
                    "version": "1.0.0",
                }
            ],
            "component": {
                "type": "application",
                "name": project_name,
                "version": project_version,
                "bom-ref": f"{project_name}@{project_version}",
            },
            "properties": [
                {"name": "compliance:eo14028", "value": "Section 4(e) — SBOM requirement"},
                {"name": "compliance:nist", "value": "SP 800-218 (SSDF)"},
            ],
        },
        "components": cdx_components,
    }

    # Compute hash of the SBOM for integrity verification
    sbom_json = json.dumps(sbom, sort_keys=True)
    sbom["metadata"]["properties"].append({
        "name": "integrity:sha256",
        "value": hashlib.sha256(sbom_json.encode()).hexdigest(),
    })

    logger.info(
        "Generated CycloneDX SBOM: %d components from %s",
        len(cdx_components),
        project_dir,
    )
    return sbom


def write_sbom(
    output_path: str,
    project_dir: str = ".",
    project_name: str = "devinclaw-federal",
    project_version: str = "1.0.0",
) -> str:
    """Generate and write SBOM to a file.  Returns the output path."""
    sbom = generate_sbom(project_dir, project_name, project_version)
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(sbom, f, indent=2)
    logger.info("SBOM written to %s", output_path)
    return output_path
