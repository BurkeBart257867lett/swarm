# Skill-Graphs Documentation

Skill-graphs are the **single source of truth** for how agents use external capabilities in the REDACTED AI Swarm.

## File Format (use this template)
```markdown
---
name: skill-name-here
category: finance | privacy | execution | narrative | scouting
version: 1.0
last_updated: 2026-02-25
dependencies: ["other-skill-1", "veil-privacy"]
tools: ["bankr", "phantom-mcp"]
---

# Skill Name

## Overview
One-sentence purpose.

## Capabilities
- Bullet list of what the agent can do

## Integration (for character.json)
```json
"skills": ["skill-name-here"],
"tools": ["bankr", "phantom-mcp"],
"system": "... use bankr for shielded treasury ..."
```

## Usage Examples
Agent prompt examples that trigger the skill.

## Security & Best Practices
- Privacy notes, key management, etc.

## Related Skills
- Links to other graphs
```

## How to add a new skill
1. Copy the template above
2. Update `central-index.md`
3. Reference the skill in any `.character.json`
4. Open a PR — we auto-merge skill-graph additions

All agents load `knowledge/skill-graphs/` at startup for self-reference.
