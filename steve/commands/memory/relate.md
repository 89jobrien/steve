---
allowed-tools: Grep, Write
description: Create relationships between entities in the knowledge graph
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: commands
name: relate
---

# Memory Relate Command

Creates relationships between entities in the knowledge graph to build connections and context.

## Usage

```
/memory:relate <entity1> <relationship> <entity2>
```

## Examples

### Project Relationships

```
/memory:relate john-doe works_on webapp-todo
```

### Dependency Relationships

```
/memory:relate webapp-todo depends_on auth-service
```

### Preference Relationships

```
/memory:relate user-prefs applies_to webapp-todo
```

### Concept Relationships

```
/memory:relate jwt-auth used_by webapp-todo
```

## Common Relationship Types

### People Relations

- **works_on**: Person working on project
- **manages**: Person managing project/team
- **collaborates_with**: People working together
- **reports_to**: Reporting structure

### Project Relations

- **depends_on**: Project dependencies
- **integrates_with**: Integration points
- **replaces**: Superseding projects
- **related_to**: General relationship

### Technical Relations

- **uses**: Technologies used
- **implements**: Patterns implemented
- **connects_to**: Service connections
- **backed_by**: Data storage

### Preference Relations

- **applies_to**: Where preference applies
- **preferred_by**: Who prefers
- **overrides**: Preference precedence

## Instructions

When this command is invoked:

1. Parse the two entities and relationship type
2. Verify both entities exist using `mcp__memory__search_nodes`
3. If entities missing, suggest creating them first
4. Create relationship with `mcp__memory__create_relations`
5. Add observation about why relationship exists
6. Show updated entity connections

## Bidirectional Relations

Some relationships imply bidirectionality:

- `collaborates_with` implies mutual collaboration
- `related_to` implies mutual relation
- `integrates_with` implies mutual integration

Consider creating reverse relations when appropriate.

## Response Format

```
✓ Created relationship:
  {entity1} --[{relationship}]--> {entity2}

Entity connections updated:

{entity1}:
  Outgoing: {count}
  - {relationship} -> {entity2} [NEW]
  - {existing_relation} -> {other_entity}

{entity2}:
  Incoming: {count}
  - {relationship} <- {entity1} [NEW]
  - {existing_relation} <- {other_entity}

Related suggestions:
- Consider: {entity2} {reverse_relation} {entity1}
```

## Best Practices

- Use consistent relationship names
- Consider relationship direction
- Document why relationships exist
- Avoid redundant relationships
- Update relationships as they change
- Remove outdated relationships
