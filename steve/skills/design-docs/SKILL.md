---
name: design-docs
description: 'DEPRECATED: Use ''documentation'' skill instead. Design documentation
  and architecture decision specialist.'
deprecated: true
superseded_by: documentation
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: skill
---

> **⚠️ DEPRECATED**: This skill has been consolidated into the `documentation` skill. Use `documentation` instead, which includes all design documentation capabilities plus API docs, technical writing, and changelogs.

# Design Documentation Skill

Creates comprehensive design specifications and architecture decision records for technical projects.

## What This Skill Does

- Writes feature design specifications
- Creates Architecture Decision Records (ADRs)
- Documents system architecture
- Captures design rationale
- Records considered alternatives
- Defines rollout plans

## When to Use

- New feature planning
- Architecture decisions
- Major refactoring
- System design reviews
- Technical planning sessions

## Reference Files

- `references/DESIGN_SPEC.template.md` - Comprehensive feature specification format
- `references/ARCHITECTURE_DECISION_RECORD.template.md` - ADR format for decisions

## Design Spec Components

1. Problem statement and goals
2. Background and constraints
3. Proposed solution with diagrams
4. API and data model design
5. Security and performance considerations
6. Testing strategy
7. Rollout plan

## ADR Format

- **Context** - Why this decision is needed
- **Decision Drivers** - What factors matter
- **Options** - Alternatives considered
- **Decision** - What was chosen and why
- **Consequences** - Expected positive/negative outcomes

## Best Practices

- Start with the problem, not the solution
- Document alternatives even if rejected
- Include success criteria
- Plan for rollback
