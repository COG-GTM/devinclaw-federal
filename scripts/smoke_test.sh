#!/bin/bash
# DevinClaw Smoke Test — validates the entire repo is functional
REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PASS=0
FAIL=0

check() {
    local name="$1"
    shift
    if "$@" > /dev/null 2>&1; then
        echo "  ✅ $name"
        PASS=$((PASS + 1))
    else
        echo "  ❌ $name"
        FAIL=$((FAIL + 1))
    fi
}

echo "DevinClaw Smoke Test"
echo "===================="
echo ""

echo "1. Skills Validation"
for skill in "$REPO_DIR"/skills/*/; do
    skill_name=$(basename "$skill")
    check "  skill: $skill_name" python3 "$REPO_DIR/skills-parser/scripts/validate_skill.py" "$skill"
done

echo ""
echo "2. Skills Parser"
TMPDIR=$(mktemp -d)
check "  parse plsql-migration" python3 "$REPO_DIR/skills-parser/scripts/parse_skill.py" "$REPO_DIR/skills/plsql-migration/" --output-dir "$TMPDIR"
check "  output files exist" test -f "$TMPDIR/plsql-migration-playbook.md" -a -f "$TMPDIR/plsql-migration-knowledge.md"
rm -rf "$TMPDIR"

echo ""
echo "3. Config Validation (JSON)"
for config in "$REPO_DIR"/audit/*.json; do
    config_name=$(basename "$config")
    check "  json: $config_name" python3 -c "import json; json.load(open('$config'))"
done

echo ""
echo "4. Knowledge Entries"
for entry in "$REPO_DIR"/knowledge/*.md; do
    entry_name=$(basename "$entry")
    [ "$entry_name" = "README.md" ] && continue
    check "  knowledge: $entry_name has trigger" grep -q "Trigger:" "$entry"
done

echo ""
echo "5. Playbooks"
for pb in "$REPO_DIR"/playbooks/*.devin.md; do
    pb_name=$(basename "$pb")
    check "  playbook: $pb_name has knowledge ref" grep -q "Required Knowledge" "$pb"
done

echo ""
echo "6. Verification System"
check "  arena-config.json valid" python3 -c "import json; json.load(open('$REPO_DIR/audit/arena-config.json'))"
check "  constitution-template.json valid" python3 -c "import json; json.load(open('$REPO_DIR/audit/constitution-template.json'))"
check "  skill-descriptors.json valid" python3 -c "import json; json.load(open('$REPO_DIR/audit/skill-descriptors.json'))"
check "  evidence-pack schema valid" python3 -c "import json; json.load(open('$REPO_DIR/audit/artifact-schemas/evidence-pack.schema.json'))"
check "  verification-record schema valid" python3 -c "import json; json.load(open('$REPO_DIR/audit/artifact-schemas/verification-record.schema.json'))"
check "  VERIFICATION-SYSTEM.md exists" test -f "$REPO_DIR/docs/VERIFICATION-SYSTEM.md"

# Verify all 15 skills have Devin 2.2 sections
for skill in "$REPO_DIR"/skills/*/; do
    skill_name=$(basename "$skill")
    check "  $skill_name: Self-Verification Loop" grep -q "Self-Verification Loop" "$skill/SKILL.md"
    check "  $skill_name: Artifact Contract" grep -q "Artifact Contract" "$skill/SKILL.md"
    check "  $skill_name: Evidence Pack" grep -q "Evidence Pack" "$skill/SKILL.md"
    check "  $skill_name: Escalation Policy" grep -q "Escalation Policy" "$skill/SKILL.md"
done

# Verify skill-descriptors.json has all 15 skills
check "  skill-descriptors: 15 skills" python3 -c "import json; d=json.load(open('$REPO_DIR/audit/skill-descriptors.json')); assert len(d['skills'])==15, f'Expected 15 skills, got {len(d[\"skills\"])}'"

# Verify arena-config.json has all 15 skills
check "  arena-config: 15 skills" python3 -c "import json; d=json.load(open('$REPO_DIR/audit/arena-config.json')); assert len(d['skills'])==15, f'Expected 15 skills, got {len(d[\"skills\"])}'"

echo ""
echo "7. Workspace Files"
check "  SOUL.md exists" test -f "$REPO_DIR/SOUL.md"
check "  GUARDRAILS.md exists" test -f "$REPO_DIR/GUARDRAILS.md"
check "  TOOLS.md exists" test -f "$REPO_DIR/TOOLS.md"
check "  SECURITY.md exists" test -f "$REPO_DIR/SECURITY.md"

echo ""
echo "8. SDLC Validator"
check "  validate_sdlc.py runs" python3 "$REPO_DIR/scripts/validate_sdlc.py" --workdir "$REPO_DIR" --spec SPEC.md

echo ""
echo "===================="
echo "Results: $PASS passed, $FAIL failed"
if [ "$FAIL" -gt 0 ]; then
    echo "❌ SMOKE TEST FAILED"
    exit 1
else
    echo "✅ ALL CHECKS PASSED"
    exit 0
fi
