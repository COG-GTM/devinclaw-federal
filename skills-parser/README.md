# Skills Parser

Convert OpenClaw skills (SKILL.md format) into Devin-compatible playbooks and knowledge entries.

## Why This Exists

DevinClaw writes skills in OpenClaw's SKILL.md format. Devin uses playbooks and knowledge entries. The Skills Parser bridges the gap — write once, both systems consume.

## Usage

### Validate a skill
```bash
python scripts/validate_skill.py skills/plsql-migration/
```

### Parse a single skill
```bash
python scripts/parse_skill.py skills/plsql-migration/ --output-dir output/
```
Generates:
- `output/plsql-migration-playbook.md`
- `output/plsql-migration-knowledge.md`

### Batch parse all skills
```bash
python scripts/batch_parse.py skills/ --output-dir output/
```
Generates playbook and knowledge files for every skill in the `skills/` directory.

## Output

| File | Devin Destination |
|------|-------------------|
| `*-playbook.md` | Add as Devin Playbook (Settings > Playbooks) |
| `*-knowledge.md` | Add as Devin Knowledge (Settings > Knowledge) |

## Integration with setup.sh

The setup script automatically runs `batch_parse.py` on all skills during installation. This ensures Devin has playbook and knowledge entries for every DevinClaw skill from day one.

## Reference

- See `reference-skills-parser-playbook.md` in the repo root for the full specification
- See `reference-agent-skills-spec.md` for the Agent Skills format specification
