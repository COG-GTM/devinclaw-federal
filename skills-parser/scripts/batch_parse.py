#!/usr/bin/env python3
"""Batch parse all OpenClaw skills into Devin playbooks and knowledge entries."""

import sys
import os
from parse_skill import parse_skill
from validate_skill import validate_skill


def batch_parse(skills_dir, output_dir, stop_on_error=False, quiet=False):
    """Discover and parse all skills in a directory."""
    if not os.path.isdir(skills_dir):
        print(f"Error: {skills_dir} is not a directory")
        return 1

    # Discover skills
    skill_dirs = []
    for entry in sorted(os.listdir(skills_dir)):
        skill_path = os.path.join(skills_dir, entry)
        skill_file = os.path.join(skill_path, "SKILL.md")
        if os.path.isdir(skill_path) and os.path.isfile(skill_file):
            skill_dirs.append(skill_path)

    if not skill_dirs:
        print(f"No skills found in {skills_dir}")
        return 1

    print(f"Found {len(skill_dirs)} skills in {skills_dir}")
    print()

    # Create output directories
    playbooks_dir = os.path.join(output_dir, "playbooks")
    knowledge_dir = os.path.join(output_dir, "knowledge")
    os.makedirs(playbooks_dir, exist_ok=True)
    os.makedirs(knowledge_dir, exist_ok=True)

    # Process each skill
    succeeded = 0
    failed = 0
    results = []

    for skill_path in skill_dirs:
        skill_name = os.path.basename(skill_path)

        # Validate first
        errors, warnings = validate_skill(skill_path)
        if errors:
            print(f"  ❌ {skill_name} — validation failed")
            for e in errors:
                print(f"     {e}")
            failed += 1
            if stop_on_error:
                print("\nStopping on first error (--stop-on-error)")
                break
            continue

        # Parse
        try:
            name, pb_path, kn_path = parse_skill(skill_path, output_dir, quiet)

            # Move to organized structure
            pb_dest = os.path.join(playbooks_dir, f"{name}-playbook.md")
            kn_dest = os.path.join(knowledge_dir, f"{name}-knowledge.md")

            if os.path.exists(pb_path) and pb_path != pb_dest:
                os.rename(pb_path, pb_dest)
            if os.path.exists(kn_path) and kn_path != kn_dest:
                os.rename(kn_path, kn_dest)

            results.append({"name": name, "playbook": pb_dest, "knowledge": kn_dest})
            succeeded += 1

        except Exception as e:
            print(f"  ❌ {skill_name} — parse error: {e}")
            failed += 1
            if stop_on_error:
                print("\nStopping on first error (--stop-on-error)")
                break

    # Summary
    print()
    print(f"Results: {succeeded} succeeded, {failed} failed, {len(skill_dirs)} total")
    print(f"Output:  {output_dir}")
    print(f"  Playbooks:  {playbooks_dir}/")
    print(f"  Knowledge:  {knowledge_dir}/")

    return 0 if failed == 0 else 1


def main():
    if len(sys.argv) < 2:
        print(
            "Usage: batch_parse.py <skills-directory> [--output-dir <dir>] [--stop-on-error] [--quiet]"
        )
        sys.exit(1)

    skills_dir = sys.argv[1]
    output_dir = "skills-parser/output"
    stop_on_error = "--stop-on-error" in sys.argv
    quiet = "--quiet" in sys.argv

    if "--output-dir" in sys.argv:
        idx = sys.argv.index("--output-dir")
        if idx + 1 < len(sys.argv):
            output_dir = sys.argv[idx + 1]

    result = batch_parse(skills_dir, output_dir, stop_on_error, quiet)
    sys.exit(result)


if __name__ == "__main__":
    main()
