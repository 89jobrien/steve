---
description: Search and query the knowledge graph for stored information
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: commands
---

# Memory Search Command

Searches the persistent knowledge graph for entities, relationships, and observations.

## Usage

```
/memory:search <query>
```

## Examples

### Search by Name

```
/memory:search webapp-todo
```

### Search by Type

```
/memory:search type:project
```

### Search by Keyword

```
/memory:search authentication
```

### Search Related

```
/memory:search related:john-doe
```

## Search Patterns

- **Exact match**: Search for specific entity names
- **Type filter**: `type:project` finds all projects
- **Keyword search**: Searches in observations
- **Related search**: `related:entity` finds connected entities
- **Recent search**: `recent` shows recently modified

## Instructions

When this command is invoked:

1. Parse the search query and identify search type
2. Execute search using `mcp__memory__search_nodes`
3. For each result, get details with `mcp__memory__open_nodes`
4. Show relationships using the graph structure
5. Format results in hierarchical view
6. Suggest refinements if many results

## Advanced Queries

### Combined Searches

```
/memory:search type:project status:active
```

### Relationship Queries

```
/memory:search works_on:webapp-todo
```

### Time-based Queries

```
/memory:search modified:today
```

## Response Format

```
Search Results for: {query}
Found: {count} entities

1. {entity_name} ({type})
   Observations:
   - {observation_1}
   - {observation_2}

   Relationships:
   - {relation_type} -> {related_entity}

2. {next_entity}...

Refine search:
- Add type filter: type:{suggested_type}
- Search related: related:{entity}
```

## Best Practices

- Start with broad searches
- Use type filters for large graphs
- Follow relationships for context
- Combine multiple search terms
- Check recent changes regularly
