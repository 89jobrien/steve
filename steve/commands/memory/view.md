---
description: View the knowledge graph or specific entities with their relationships
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: commands
---

# Memory View Command

Displays the current state of the knowledge graph or specific entities.

## Usage

```
/memory:view [entity|all|graph|stats]
```

## Examples

### View Specific Entity

```
/memory:view webapp-todo
```

### View All Entities

```
/memory:view all
```

### View Graph Structure

```
/memory:view graph
```

### View Statistics

```
/memory:view stats
```

## View Modes

### Entity View

Shows detailed information about a specific entity:

- All observations with timestamps
- Incoming relationships
- Outgoing relationships
- Related entities

### Graph View

Displays the entire knowledge graph structure:

- All entities organized by type
- Relationship connections
- Visual representation (ASCII art)

### Stats View

Provides graph statistics:

- Total entities by type
- Relationship counts
- Most connected entities
- Recent additions
- Graph density

### Recent View

Shows recently modified entities:

```
/memory:view recent
```

## Instructions

When this command is invoked:

1. Determine view mode from parameter
2. For entity view: Use `mcp__memory__open_nodes`
3. For graph view: Use `mcp__memory__read_graph`
4. For stats: Analyze graph structure
5. Format output based on view mode
6. Highlight important connections

## Response Formats

### Entity View

```
Entity: {name}
Type: {type}
Created: {timestamp}

Observations ({count}):
1. {observation_text} [{timestamp}]
2. {observation_text} [{timestamp}]

Incoming Relations ({count}):
← {entity} --[{relationship}]--

Outgoing Relations ({count}):
→ --[{relationship}]--> {entity}

Related Entities:
- {entity_1} (via {relationship})
- {entity_2} (via {relationship})
```

### Graph View

```
Knowledge Graph Structure:

Projects ({count}):
├── webapp-todo
│   ├── works_on ← john-doe
│   ├── uses → react
│   └── depends_on → auth-service
└── auth-service
    └── uses → jwt

People ({count}):
└── john-doe
    └── works_on → webapp-todo

[Total: {total_entities} entities, {total_relations} relationships]
```

### Stats View

```
Knowledge Graph Statistics:

Entities: {total}
├── Projects: {count}
├── People: {count}
├── Concepts: {count}
└── Other: {count}

Relationships: {total}
├── works_on: {count}
├── depends_on: {count}
└── Other: {count}

Most Connected:
1. {entity} ({connection_count} connections)
2. {entity} ({connection_count} connections)

Recent Activity:
- {entity} added {time_ago}
- {relationship} created {time_ago}
```

## Best Practices

- Use entity view for detailed inspection
- Use graph view for overview
- Check stats regularly for growth
- Review recent changes
- Identify orphaned entities
- Monitor graph complexity
