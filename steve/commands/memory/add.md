---
allowed-tools: Grep, Write
description: Add new entities or observations to the knowledge graph
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: commands
name: add
---

# Memory Add Command

Adds new information to the persistent knowledge graph.

## Usage

```
/memory:add <type> <name> [observation]
```

## Examples

### Add Entity

```
/memory:add project webapp-todo "Starting new React todo application"
```

### Add Person

```
/memory:add person john-doe "Lead developer on the project"
```

### Add Concept

```
/memory:add concept authentication "Using JWT tokens for API auth"
```

### Add Preference

```
/memory:add preference coding-style "User prefers functional programming"
```

## Entity Types

- **project**: Software projects, initiatives
- **person**: Team members, stakeholders
- **concept**: Technical concepts, patterns
- **preference**: User or project preferences
- **tool**: Development tools, services
- **decision**: Architectural or design decisions
- **issue**: Problems, bugs, or concerns

## Instructions

When this command is invoked:

1. Parse the entity type and name from the command
2. Check if entity already exists using `mcp__memory__search_nodes`
3. If new, create entity with `mcp__memory__create_entities`
4. Add any provided observation with `mcp__memory__add_observations`
5. Suggest related entities to connect
6. Confirm successful addition

## Best Practices

- Use kebab-case for entity names
- Keep names unique and descriptive
- Add timestamp to observations
- Check for duplicates before creating
- Include context in observations

## Response Format

```
✓ Created entity: {name} (type: {type})
✓ Added observation: {summary}

Related entities found:
- {existing_entity} - consider creating relation

Current stats:
- Total entities: {count}
- Type {type}: {type_count}
```
