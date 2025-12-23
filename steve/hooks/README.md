---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: hook
---

# Hooks

Claude hooks organized by type for code analysis, guards, workflows, and lifecycle events.

## Structure

Hooks are organized by hook type:

- **`analyzers/`** - Code analysis hooks (analyze code patterns, detect issues)
- **`guards/`** - Guard hooks (pre-commit checks, validation)
- **`workflows/`** - Workflow automation hooks (automate repetitive tasks)
- **`lifecycle/`** - Lifecycle event hooks (on file save, on commit, etc.)
- **`context/`** - Context management hooks (manage context, memory)

## File Format

Each hook consists of a pair of files:

- **`hook-name.md`** - Hook documentation and configuration
- **`hook-name.py`** - Hook implementation (Python)

## Hook Types

### Analyzers

Analyze code patterns, detect issues, and provide insights:

- Code quality analysis
- Pattern detection
- Architecture validation
- Performance analysis

### Guards

Pre-commit checks and validation:

- Linting checks
- Security scanning
- Format validation
- Test requirements

### Workflows

Automate repetitive tasks:

- Code generation
- File organization
- Documentation updates
- Dependency management

### Lifecycle

Respond to lifecycle events:

- On file save
- On commit
- On branch creation
- On pull request

### Context

Manage context and memory:

- Context summarization
- Memory updates
- Knowledge graph updates
- Context cleanup

## Naming Conventions

- Use `kebab-case` for hook names (e.g., `secrets-detector`, `code-formatter`)
- Names should indicate the hook's purpose
- Prefix with type when helpful (e.g., `guard-linter.md`)

## Creating New Hooks

1. Choose the appropriate hook type directory
2. Create both `.md` and `.py` files with matching names
3. Use the template from `steve/templates/CLAUDE_HOOK.template.md`
4. Implement the Python hook logic
5. Test the hook

## Examples

See existing hooks in each type directory for reference patterns.
