---
description: Remove AI-generated code slop from the current branch by comparing against
  a base branch
allowed-tools: Read, Edit, MultiEdit, Bash, Grep, Glob
argument-hint: '[base-branch] | --dev | --main | --master'
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: commands
name: remove-ai-slop
---

# Remove AI Code Slop

Check the diff against the base branch and remove all AI-generated slop introduced in the current branch.

## Arguments

Base branch to compare against: **$ARGUMENTS**

If no argument provided, default to `dev`. Common options:

- `dev` or `--dev` - Compare against dev branch
- `main` or `--main` - Compare against main branch
- `master` or `--master` - Compare against master branch

## Current Branch Context

!git branch --show-current 2>/dev/null

## Changed Files

!git diff $(git merge-base HEAD ${ARGUMENTS:-dev})..HEAD --name-only 2>/dev/null | head -30

## Slop Patterns to Remove

### 1. Unnecessary Comments

- Comments explaining obvious code that a human wouldn't add
- Comments inconsistent with the rest of the file's documentation style
- Redundant comments that just restate the code
- Over-documentation of simple operations

### 2. Defensive Bloat

- Extra try/catch blocks abnormal for that area of the codebase
- Defensive null/undefined checks on trusted/validated codepaths
- Redundant input validation when callers already validate
- Error handling that can never trigger given the call context

### 3. Type Workarounds

- Casts to `any` to bypass type issues
- Unnecessary type assertions (`as X`)
- `@ts-ignore` or `@ts-expect-error` without legitimate reason
- Overly complex generic constraints that could be simplified

### 4. Style Inconsistencies

- Naming conventions different from the rest of the file
- Formatting that doesn't match surrounding code
- Import organization inconsistent with file patterns
- Variable declarations inconsistent with file style

### 5. AI Tells

- Unnecessary emoji usage in code or comments
- Overly verbose variable names
- Redundant intermediate variables
- "Just in case" code with no actual use case

## Process

1. For each changed file, read the full file to understand existing style
2. Identify patterns from the slop categories above
3. Make surgical edits to remove slop while preserving functionality
4. Verify changes don't break the code

## Output

Provide ONLY a 1-3 sentence summary of what you changed. Do not explain your reasoning or list every change. Just state what categories of slop were removed and roughly how much.

Example outputs:

- "Removed 12 redundant comments and 3 unnecessary try/catch blocks across 4 files."
- "Cleaned up defensive null checks in auth module and removed 2 `as any` casts."
- "No significant slop found; code quality is consistent."
