---
paths:
- '**/*.ts'
- '**/*.tsx'
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: rule
---

# TypeScript Rules

## Bun-Only Environment

**CRITICAL**: Use `bun` for all TypeScript/JavaScript operations:

| Instead of | Use |
|------------|-----|
| `node` | `bun` |
| `npm install` | `bun install` |
| `npm run` | `bun run` |
| `npx` | `bunx` |
| `ts-node` | `bun` (runs .ts directly) |
| `jest` | `bun test` |
| `vitest` | `bun test` |

## Running TypeScript

```bash
# Run a TypeScript file directly (no compilation needed)
bun script.ts

# Run with watch mode
bun --watch script.ts

# Run tests
bun test
```

## Package Management

```bash
bun install              # Install dependencies
bun add <package>        # Add dependency
bun add -d <package>     # Add dev dependency
bun remove <package>     # Remove dependency
```

## Type Checking

```bash
bunx tsc --noEmit        # Type check without emitting
```
