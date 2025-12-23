---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: commands
---

# Commands

Slash commands organized by category for Claude Code.

## Structure

Commands are organized into category directories:

- **`_team/`** - Team collaboration commands
- **`_incoming/`** - Incoming/imported commands
- **`agents/`** - Agent management commands
- **`context/`** - Context management commands
- **`debug/`** - Debugging commands
- **`dev/`** - Development workflow commands
- **`docs/`** - Documentation commands
- **`git/`** - Git workflow commands
- **`memory/`** - Memory management commands
- **`meta/`** - Meta/configuration commands
- **`prompts/`** - Prompt-related commands
- **`setup/`** - Setup and installation commands
- **`skills/`** - Skill management commands
- **`tdd/`** - Test-driven development commands
- **`test/`** - Testing commands
- **`todo/`** - Todo list management commands
- **`util/`** - Utility commands

## File Format

Commands are markdown files with clear usage instructions:

```markdown
# Command Name

Brief description of what the command does.

## Usage

\command-name [options] [arguments]

## Options

- `--option`: Description

## Examples

\command-name example-usage

## Related Commands

- \related-command-1
- \related-command-2
```

## Naming Conventions

- Use `kebab-case.md` for command files (e.g., `create-subagent.md`)
- Command names should be clear and action-oriented
- Prefix with category when helpful (e.g., `git-commit-helper.md`)

## Best Practices

1. **Clear Usage**: Provide clear usage examples
2. **Options Documentation**: Document all options and flags
3. **Examples**: Include multiple real-world examples
4. **Related Commands**: Link to related commands
5. **Error Handling**: Document common errors and solutions

## Creating New Commands

1. Choose the appropriate category directory
2. Create a new `.md` file with kebab-case name
3. Use the template from `steve/templates/SLASH_COMMAND.template.md`
4. Follow the structure guidelines
5. Test the command

## Examples

See existing commands in each category directory for reference patterns.
