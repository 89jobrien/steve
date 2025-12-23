---
name: migrations
description: 'DEPRECATED: Use ''documentation'' skill instead. Migration guide and
  upgrade path specialist.'
deprecated: true
superseded_by: documentation
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: skill
---

> **⚠️ DEPRECATED**: This skill has been consolidated into the `documentation` skill. Use `documentation` instead, which includes migration guides plus API docs, technical writing, design docs, and changelogs.

# Migrations Skill

Creates comprehensive migration guides for version upgrades, breaking changes, and system migrations.

## What This Skill Does

- Documents breaking changes
- Creates step-by-step migration guides
- Provides before/after code examples
- Plans database migrations
- Documents API changes
- Creates rollback procedures

## When to Use

- Major version releases
- Breaking API changes
- Database schema migrations
- Configuration changes
- Dependency upgrades

## Reference Files

- `references/MIGRATION_GUIDE.template.md` - Comprehensive migration documentation format

## Migration Guide Structure

1. **Overview** - What's changing and why
2. **Breaking Changes** - With code examples
3. **Deprecations** - Timeline and replacements
4. **Step-by-Step** - Detailed migration steps
5. **Troubleshooting** - Common issues
6. **Rollback** - How to revert

## Best Practices

- Show before/after for every change
- Provide automated codemods when possible
- Include verification steps
- Document rollback procedures
- List all deprecated items with timelines
- Test migration path thoroughly
