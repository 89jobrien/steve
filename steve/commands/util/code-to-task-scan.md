---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: commands
---

# Scan Code for Tasks

Scan codebase for TODO/FIXME comments, technical debt markers, and code issues, then output findings to CURRENT_TASKS.local.md

## Purpose

This command scans your codebase for TODO/FIXME comments, technical debt markers, deprecated code, and other indicators that should be tracked as tasks. It generates a CURRENT_TASKS.local.md file in the project root with organized, prioritized tasks.

## Usage

```bash
/code-to-task
```

## Instructions

### 1. Scan for Task Markers

Search for common patterns indicating needed work. Exclude lock files, node_modules, and generated files:

```bash
rg "TODO|FIXME|HACK|XXX|OPTIMIZE|REFACTOR" \
  --glob '!*.lock' \
  --glob '!package-lock.json' \
  --glob '!yarn.lock' \
  --glob '!node_modules/**' \
  --glob '!*.min.js' \
  --glob '!*.generated.*' \
  -n

rg "@deprecated|DEPRECATED|@obsolete" \
  --glob '!node_modules/**' \
  --glob '!*.lock' \
  -n

rg "SECURITY|INSECURE|VULNERABILITY" \
  --glob '!node_modules/**' \
  --glob '!*.lock' \
  -n -i
```

### 2. Categorize Findings

Group findings by priority:

**URGENT (P0):** Security issues, vulnerabilities
**HIGH (P1):** FIXME, HACK, XXX, deprecated code
**MEDIUM (P2):** TODO comments
**LOW (P3):** OPTIMIZE, REFACTOR suggestions

### 3. Generate CURRENT_TASKS.local.md

Create or update the file in the project root with this structure:

```markdown
# Current Tasks

Generated: YYYY-MM-DD HH:MM

## Summary
- Total items: N
- Urgent: N | High: N | Medium: N | Low: N

## Urgent (P0)
Tasks requiring immediate attention (security, critical bugs)

### [Title from comment]
- **File:** `path/to/file.ts:123`
- **Type:** security | vulnerability
- **Comment:** The actual comment text
- **Context:** Brief code context if helpful

## High Priority (P1)
FIXMEs, HACKs, deprecated code

### [Title]
- **File:** `path/to/file.ts:45`
- **Type:** fixme | hack | deprecated
- **Comment:** Comment text

## Medium Priority (P2)
Standard TODOs

### [Title]
- **File:** `path/to/file.ts:78`
- **Type:** todo
- **Comment:** Comment text

## Low Priority (P3)
Optimization and refactoring suggestions

### [Title]
- **File:** `path/to/file.ts:90`
- **Type:** optimize | refactor
- **Comment:** Comment text

## By File
Quick reference of which files have the most tasks:
- `src/api/auth.ts` - 5 items
- `src/utils/helpers.ts` - 3 items

## Recommendations
- Address P0 items immediately
- Schedule P1 items for current sprint
- Add P2/P3 to backlog
```

### 4. Handle Edge Cases

**No findings:**

```markdown
# Current Tasks

Generated: YYYY-MM-DD HH:MM

## Summary
No TODO comments, FIXMEs, or technical debt markers found.

This codebase appears clean of tracked technical debt.
```

**Filter false positives:**

- Ignore matches in lock files (package-lock.json, yarn.lock, etc.)
- Ignore matches in node_modules
- Ignore matches in minified files
- Ignore matches that are clearly not code comments (e.g., "template" matching "TEMP")

### 5. Output Location

Always write to `CURRENT_TASKS.local.md` in the project root. The `.local.md` suffix indicates this is a local file that should typically be gitignored.

## Example Output

```markdown
# Current Tasks

Generated: 2024-12-07 14:30

## Summary
- Total items: 12
- Urgent: 1 | High: 3 | Medium: 6 | Low: 2

## Urgent (P0)

### Hardcoded API credentials
- **File:** `src/config/api.ts:45`
- **Type:** security
- **Comment:** SECURITY: Remove hardcoded API key before production

## High Priority (P1)

### Race condition in data sync
- **File:** `src/services/sync.ts:78`
- **Type:** fixme
- **Comment:** FIXME: Race condition when multiple clients update simultaneously

### Legacy auth method
- **File:** `src/api/auth.ts:120`
- **Type:** deprecated
- **Comment:** @deprecated Use OAuth2 flow instead

### Temporary workaround for API bug
- **File:** `src/utils/fetch.ts:34`
- **Type:** hack
- **Comment:** HACK: Remove after backend fixes response format

## Medium Priority (P2)

### Add input validation
- **File:** `src/components/Form.tsx:56`
- **Type:** todo
- **Comment:** TODO: Add proper validation for email field

### Implement retry logic
- **File:** `src/api/client.ts:89`
- **Type:** todo
- **Comment:** TODO: Add exponential backoff for failed requests

## Low Priority (P3)

### Optimize database queries
- **File:** `src/db/queries.ts:145`
- **Type:** optimize
- **Comment:** OPTIMIZE: This query could use an index

## By File
- `src/api/auth.ts` - 3 items
- `src/services/sync.ts` - 2 items
- `src/config/api.ts` - 1 item
- `src/utils/fetch.ts` - 1 item
- `src/components/Form.tsx` - 1 item

## Recommendations
- Address the security issue in api.ts immediately
- Fix the race condition before next release
- Migrate away from deprecated auth method
```

## Tips

- Run this command periodically to track technical debt
- Add CURRENT_TASKS.local.md to .gitignore
- Use consistent comment formats (TODO:, FIXME:, etc.)
- Include context in comments: `TODO(username): description`
