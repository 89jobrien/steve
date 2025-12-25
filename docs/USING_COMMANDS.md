# Using Commands

Commands are slash-invoked workflows for common tasks. This guide explains how to use and create commands.

## What is a Command?

A command is a markdown file that defines a reusable workflow. When invoked with a slash (`/`), the command
expands into a prompt that guides task execution.

Example command file (`review-code.md`):

```yaml
---
description: Comprehensive code quality review
allowed-tools: Read, Grep, Glob, Edit
argument-hint: [file-path] | [commit-hash] | full
---

# Code Review

Review the specified code for:
- Bugs and logic errors
- Security vulnerabilities
- Performance issues
- Code style and conventions

## Arguments

- `file-path`: Review a specific file
- `commit-hash`: Review changes in a commit
- `full`: Review entire codebase

## Process

1. Identify the scope of review
2. Read and understand the code
3. Check for issues by category
4. Provide prioritized feedback
```

## Invoking Commands

### Basic Syntax

```text
/command-name [arguments]
```

### Namespaced Commands

Commands in subdirectories use a namespace:

```text
/category:command-name [arguments]
```

Examples:

```text
/dev:review-code src/main.py
/git:clean-branches --dry-run
/test:run --coverage
/docs:update-docs
```

### With Arguments

Commands can accept arguments:

```text
/dev:review-code src/auth.py      # Review specific file
/test:run --watch                  # Run with flag
/setup:setup-docker-containers     # No arguments needed
```

### Without Arguments

Some commands work without arguments:

```text
/analyze-codebase                  # Analyzes current codebase
/prep-for-standup                  # Generates standup report
```

## Command Categories

### Development (`/dev:*`)

| Command                    | Description             | Usage                                  |
| -------------------------- | ----------------------- | -------------------------------------- |
| `review-code`              | Code quality review     | `/dev:review-code [file]`              |
| `review-architecture`      | Architecture analysis   | `/dev:review-architecture [scope]`     |
| `containerize-application` | Create Dockerfile       | `/dev:containerize-application [type]` |
| `design-rest-api`          | API design              | `/dev:design-rest-api [version]`       |
| `remove-ai-slop`           | Clean AI-generated code | `/dev:remove-ai-slop [branch]`         |

### Git (`/git:*`)

| Command             | Description             | Usage                              |
| ------------------- | ----------------------- | ---------------------------------- |
| `clean-branches`    | Clean merged branches   | `/git:clean-branches [--dry-run]`  |
| `git-bisect-helper` | Find regression commits | `/git:git-bisect-helper [commits]` |

### Testing (`/test:*`)

| Command  | Description            | Usage                      |
| -------- | ---------------------- | -------------------------- |
| `init`   | Initialize test config | `/test:init [--framework]` |
| `run`    | Run tests              | `/test:run [--coverage]`   |
| `report` | Generate test report   | `/test:report [--verbose]` |
| `test`   | Write tests (TDD)      | `/test:test [file]`        |

### Documentation (`/docs:*`)

| Command                             | Description             | Usage                                     |
| ----------------------------------- | ----------------------- | ----------------------------------------- |
| `create-prd`                        | Create PRD              | `/docs:create-prd [feature]`              |
| `update-docs`                       | Update documentation    | `/docs:update-docs [type]`                |
| `create-architecture-documentation` | Generate arch docs      | `/docs:create-architecture-documentation` |
| `create-onboarding-guide`           | Create onboarding guide | `/docs:create-onboarding-guide [type]`    |

### Setup (`/setup:*`)

| Command                   | Description          | Usage                                    |
| ------------------------- | -------------------- | ---------------------------------------- |
| `setup-ci-cd-pipeline`    | Setup CI/CD          | `/setup:setup-ci-cd-pipeline [platform]` |
| `setup-docker-containers` | Setup Docker dev env | `/setup:setup-docker-containers`         |
| `setup-linting`           | Configure linting    | `/setup:setup-linting [language]`        |
| `setup-formatting`        | Configure formatting | `/setup:setup-formatting [language]`     |
| `setup-monorepo`          | Configure monorepo   | `/setup:setup-monorepo [tool]`           |

### Memory (`/memory:*`)

| Command  | Description            | Usage            |
| -------- | ---------------------- | ---------------- |
| `add`    | Add to knowledge graph | `/memory:add`    |
| `search` | Search knowledge graph | `/memory:search` |
| `view`   | View knowledge graph   | `/memory:view`   |
| `relate` | Create relationships   | `/memory:relate` |
| `forget` | Remove from graph      | `/memory:forget` |

### Meta (`/meta:*`)

| Command           | Description        | Usage                                       |
| ----------------- | ------------------ | ------------------------------------------- |
| `create-subagent` | Create new agent   | `/meta:create-subagent [description]`       |
| `create-skill`    | Create new skill   | `/meta:create-skill [name] [description]`   |
| `create-command`  | Create new command | `/meta:create-command [name] [description]` |

### Utilities (`/util:*`)

| Command               | Description      | Usage                                  |
| --------------------- | ---------------- | -------------------------------------- |
| `ultra-think`         | Deep analysis    | `/util:ultra-think [problem]`          |
| `update-dependencies` | Update deps      | `/util:update-dependencies [strategy]` |
| `audit-components`    | Audit components | `/util:audit-components [type]`        |

See [Component Catalog](COMPONENT_CATALOG.md#commands) for the complete list.

## Command Features

### Argument Hints

Commands can specify expected arguments:

```yaml
argument-hint: [file-path] | [commit-hash] | full
```

This helps users understand what input the command expects.

### Tool Restrictions

Commands can limit which tools are used:

```yaml
allowed-tools: Read, Grep, Glob
```

### Shell Embedding

Commands can embed shell output with `!` syntax:

```markdown
## Current Branch

!git branch --show-current

## Recent Commits

!git log --oneline -5
```

### Agent Invocation

Commands can invoke agents:

```markdown
Use the code-reviewer agent to perform the review.
```

## Creating Custom Commands

### Basic Command

Create a file in `~/.claude/commands/`:

```yaml
---
description: What this command does
---
# My Command

Instructions for what to do when invoked.
```

### Command with Arguments

```yaml
---
description: Process a file
argument-hint: [file-path] | [--all]
---

# Process Command

Process the specified file or all files if --all is provided.
```

### Command with Tool Restrictions

```yaml
---
description: Read-only analysis
allowed-tools: Read, Grep, Glob
---
# Analysis Command

Analyze code without making changes.
```

### Using Templates

Use the command template:

```bash
cp steve/templates/SLASH_COMMAND.template.md ~/.claude/commands/my-command.md
```

Or use the meta command:

```text
/meta:create-command format-imports "Format and sort imports in Python files"
```

## Command Patterns

### The Workflow Pattern

Commands that orchestrate multi-step processes:

```yaml
---
description: Full code review workflow
---
# Code Review Workflow

1. Check for uncommitted changes
2. Run linters
3. Run tests
4. Review code quality
5. Generate report
```

### The Analysis Pattern

Commands that gather and present information:

```yaml
---
description: Analyze codebase structure
allowed-tools: Read, Grep, Glob
---
# Codebase Analysis

Analyze and report on:
  - Directory structure
  - File counts by type
  - Dependency graph
  - Code metrics
```

### The Generator Pattern

Commands that create new content:

```yaml
---
description: Generate API documentation
---
# API Documentation Generator

Generate OpenAPI spec for all endpoints in the codebase.
```

### The Interactive Pattern

Commands that gather user input:

```yaml
---
description: Interactive setup wizard
---

# Setup Wizard

Ask the user about:
1. Project type
2. Language preferences
3. Tool choices

Then configure accordingly.
```

## Command Organization

### Directory Structure

```text
~/.claude/commands/
├── dev/                    # Development commands
│   ├── review-code.md
│   └── debug-error.md
├── git/                    # Git commands
│   ├── clean-branches.md
│   └── create-pr.md
├── test/                   # Testing commands
│   ├── run.md
│   └── report.md
└── my-command.md           # Root-level command
```

### Naming Conventions

- Use `kebab-case` for command names
- Keep names short but descriptive
- Group related commands in subdirectories

### Namespace Usage

- Root commands: `/command-name`
- Namespaced commands: `/category:command-name`

## Troubleshooting

### Command Not Found

1. Verify file exists in `~/.claude/commands/`
2. Check file has `.md` extension
3. For namespaced commands, verify directory structure
4. Restart Claude Code to reload

### Arguments Not Working

1. Check `argument-hint` in frontmatter
2. Verify argument parsing in command content
3. Test with different argument formats

### Tools Not Available

1. Check `allowed-tools` in frontmatter
2. Verify tool names are correct
3. Remove restriction to allow all tools

### Command Not Executing Properly

1. Review command content for clarity
2. Add more specific instructions
3. Include examples of expected behavior
4. Test with simpler inputs first

## See Also

- [Component Catalog](COMPONENT_CATALOG.md#commands) - Browse all commands
- [Using Agents](USING_AGENTS.md) - Commands can invoke agents
- [Installation](INSTALLATION.md) - Install new commands
- [Development](DEVELOPMENT.md) - Create custom commands
