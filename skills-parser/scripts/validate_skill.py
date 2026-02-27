#!/usr/bin/env python3
"""Validate an OpenClaw skill directory for correctness."""

import sys
import os
import re
import ast


def validate_skill(skill_path, strict=False):
    """Validate a skill directory containing SKILL.md."""
    errors = []
    warnings = []

    # Check SKILL.md exists
    skill_file = os.path.join(skill_path, "SKILL.md")
    if not os.path.isfile(skill_file):
        errors.append(f"SKILL.md not found in {skill_path}")
        return errors, warnings

    # Read SKILL.md
    with open(skill_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Check YAML frontmatter
    if not content.startswith("---"):
        errors.append("SKILL.md must start with YAML frontmatter (---)")
    else:
        # Extract frontmatter
        parts = content.split("---", 2)
        if len(parts) < 3:
            errors.append("YAML frontmatter not properly closed (missing second ---)")
        else:
            frontmatter = parts[1].strip()

            # Check name field
            name_match = re.search(r"^name:\s*(.+)$", frontmatter, re.MULTILINE)
            if not name_match:
                errors.append("YAML frontmatter missing 'name' field")
            else:
                name = name_match.group(1).strip()
                # Validate name format
                if not re.match(r"^[a-z0-9-]+$", name):
                    errors.append(
                        f"Skill name '{name}' must be lowercase letters, numbers, and hyphens only"
                    )
                if len(name) > 40:
                    errors.append(
                        f"Skill name '{name}' exceeds 40 character limit ({len(name)} chars)"
                    )
                if name.startswith("-") or name.endswith("-") or "--" in name:
                    errors.append(
                        f"Skill name '{name}' has leading/trailing/consecutive hyphens"
                    )

            # Check description field
            desc_match = re.search(
                r"^description:\s*(.+)$", frontmatter, re.MULTILINE
            )
            if not desc_match:
                errors.append("YAML frontmatter missing 'description' field")
            else:
                desc = desc_match.group(1).strip()
                if len(desc) < 20:
                    warnings.append(
                        f"Description is short ({len(desc)} chars) — recommend 20+ characters"
                    )

            # Check body content exists
            body = parts[2].strip()
            if not body:
                errors.append("SKILL.md has no content after frontmatter")

    # Check for Python scripts and validate syntax
    scripts_dir = os.path.join(skill_path, "scripts")
    if os.path.isdir(scripts_dir):
        for filename in os.listdir(scripts_dir):
            if filename.endswith(".py"):
                script_path = os.path.join(scripts_dir, filename)
                try:
                    with open(script_path, "r", encoding="utf-8") as f:
                        ast.parse(f.read())
                except SyntaxError as e:
                    errors.append(f"Python syntax error in {filename}: {e}")

    if strict:
        errors.extend(warnings)
        warnings = []

    return errors, warnings


def main():
    if len(sys.argv) < 2:
        print("Usage: validate_skill.py <skill-directory> [--strict]")
        sys.exit(1)

    skill_path = sys.argv[1]
    strict = "--strict" in sys.argv

    if not os.path.isdir(skill_path):
        print(f"Error: {skill_path} is not a directory")
        sys.exit(1)

    errors, warnings = validate_skill(skill_path, strict)

    if warnings:
        for w in warnings:
            print(f"  WARNING: {w}")

    if errors:
        for e in errors:
            print(f"  ERROR: {e}")
        print(f"\nValidation FAILED ({len(errors)} errors)")
        sys.exit(1)
    else:
        skill_name = os.path.basename(os.path.normpath(skill_path))
        print(f"  ✅ {skill_name} — valid")
        sys.exit(0)


if __name__ == "__main__":
    main()
