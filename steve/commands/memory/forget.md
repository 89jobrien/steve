---
allowed-tools: Grep
description: Remove entities, relationships, or observations from the knowledge graph
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: commands
name: forget
---

# Memory Forget Command

Removes information from the knowledge graph including entities, relationships, and observations.

## Usage

```
/memory:forget <target> [options]
```

## Examples

### Remove Entity

```
/memory:forget entity webapp-todo
```

### Remove Relationship

```
/memory:forget relation "john-doe works_on webapp-todo"
```

### Remove Observation

```
/memory:forget observation webapp-todo --index 2
```

### Clear All (Dangerous)

```
/memory:forget all --confirm
```

## Deletion Types

### Entity Deletion

Removes entire entity and all its relationships:

- Entity itself
- All observations
- All incoming relationships
- All outgoing relationships

### Relationship Deletion

Removes specific relationship between entities:

- Keeps both entities
- Removes only the connection
- Preserves observations

### Observation Deletion

Removes specific observation from entity:

- Keeps entity
- Keeps relationships
- Removes selected observation

## Instructions

When this command is invoked:

1. Parse deletion target and validate
2. Check what will be affected
3. Request confirmation for destructive operations
4. For entities: Use `mcp__memory__delete_entities`
5. For relations: Use `mcp__memory__delete_relations`
6. For observations: Use `mcp__memory__delete_observations`
7. Verify deletion success
8. Report what was removed

## Safety Checks

### Before Entity Deletion

```
Warning: Deleting entity "{name}" will also remove:
- {count} observations
- {count} incoming relationships
- {count} outgoing relationships

Affected entities:
- {entity_1} (loses connection)
- {entity_2} (loses connection)

Type 'confirm' to proceed:
```

### Before Bulk Deletion

```
Warning: This will delete:
- {entity_count} entities
- {relation_count} relationships
- {observation_count} observations

This action cannot be undone!
Type 'DELETE ALL' to confirm:
```

## Response Format

### Successful Deletion

```
✓ Deleted successfully:

Removed entity: {name}
- Observations removed: {count}
- Relationships removed: {count}

Affected entities:
- {entity}: Lost {relationship} connection

Graph statistics:
- Entities: {before} → {after}
- Relationships: {before} → {after}
```

### Deletion Failed

```
✗ Deletion failed: {reason}

Suggestions:
- Check entity exists
- Verify exact name
- Try searching first
```

## Cleanup Operations

### Remove Orphaned Entities

```
/memory:forget orphaned
```

Removes entities with no relationships

### Remove Old Observations

```
/memory:forget old --days 30
```

Removes observations older than specified days

### Remove By Type

```
/memory:forget type:temporary
```

Removes all entities of specific type

## Best Practices

- Always verify before deleting
- Check dependencies first
- Consider archiving vs deleting
- Remove observations before entities
- Clean relationships before entities
- Keep audit trail of deletions
- Use specific targets, avoid wildcards
