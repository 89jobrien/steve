# Getting Started with Steve

This guide will help you get started with Steve, a collection of reusable components for Claude Code.

## What is Steve?

Steve is a centralized repository of Claude Code components including:

- **137 Agents** - Specialized AI assistants for specific tasks
- **97 Commands** - Slash commands for common workflows
- **57 Skills** - Reusable expertise bundles
- **59 Hooks** - Automated code analysis and guards
- **27 Templates** - Scaffolds for creating new components

These components extend Claude Code's capabilities, giving you pre-built solutions for code review, testing,
documentation, DevOps, and more.

## Prerequisites

Before using Steve, ensure you have:

- **Claude Code** installed and configured
- **Python 3.10+** with `uv` package manager
- **Git** for cloning and version control
- **GitHub account** (optional, for Gist publishing)

## Quick Start (5 Minutes)

### Step 1: Clone the Repository

```bash
git clone https://github.com/joe/steve.git
cd steve
```

### Step 2: Install Dependencies

```bash
uv sync
```

### Step 3: Browse Available Components

```bash
# Build the component index
uv run scripts/build_index.py

# List all components
uv run scripts/list_components.py

# Search for specific components
uv run scripts/list_components.py --search "review"

# List by type
uv run scripts/list_components.py --type agents
```

### Step 4: Install Your First Component

Use the install script or copy manually:

```bash
# Install using the script (recommended)
uv run scripts/install_component.py code-reviewer

# Or copy manually
cp steve/agents/code-quality/code-reviewer.md ~/.claude/agents/
cp -r steve/skills/code-review ~/.claude/skills/
cp steve/commands/dev/review-code.md ~/.claude/commands/
```

### Step 5: Use the Component

In Claude Code, you can now use the installed components:

```text
# Use an agent via Task tool
@code-reviewer Please review my latest changes

# Use a slash command
/dev:review-code src/main.py

# Skills are automatically loaded by agents that reference them
```

## Understanding Component Types

### Agents

Agents are specialized AI assistants configured for specific tasks. Each agent has:

- **Tools** - Which Claude Code tools it can use
- **Model** - Which Claude model powers it (haiku, sonnet, opus)
- **Skills** - Domain expertise it references

Example use cases:

- `code-reviewer` - Reviews code for bugs and best practices
- `debugger` - Helps diagnose and fix errors
- `backend-architect` - Designs system architecture

See [Using Agents](USING_AGENTS.md) for detailed guidance.

### Skills

Skills are bundles of domain expertise that agents can reference. They may include:

- **SKILL.md** - Core knowledge and instructions
- **references/** - Supporting documentation
- **scripts/** - Helper Python scripts
- **assets/** - Generated outputs

Example skills:

- `code-review` - Code review methodology
- `testing` - TDD and testing practices
- `documentation` - Technical writing standards

See [Using Skills](USING_SKILLS.md) for detailed guidance.

### Commands

Commands are slash-invoked workflows for common tasks:

```text
/dev:review-code [file]     - Review code quality
/git:create-pr              - Create a pull request
/test:run                   - Run test suite
/docs:update-docs           - Update documentation
```

See [Using Commands](USING_COMMANDS.md) for detailed guidance.

### Hooks

Hooks run automatically in response to Claude Code events:

- **Analyzers** - Analyze code on file changes
- **Guards** - Prevent commits with issues
- **Workflows** - Automate multi-step processes
- **Lifecycle** - React to session events

See [Using Hooks](USING_HOOKS.md) for detailed guidance.

## Directory Structure

Components in your Claude Code configuration (`~/.claude/`):

```text
~/.claude/
├── agents/           # Agent configurations
├── skills/           # Skill bundles
├── commands/         # Slash commands
├── hooks/            # Automated hooks
└── settings.json     # Claude Code settings
```

Components in the Steve repository:

```text
steve/
├── agents/           # Organized by domain
│   ├── code-quality/
│   ├── development/
│   ├── devops-infrastructure/
│   └── ...
├── skills/           # Each in its own directory
├── commands/         # Organized by category
├── hooks/            # Organized by type
└── templates/        # For creating new components
```

## Finding the Right Component

### By Domain

Browse agents by their domain directory:

| Domain | Description |
|--------|-------------|
| `code-quality/` | Code review, linting, refactoring |
| `development/` | General development workflows |
| `devops-infrastructure/` | CI/CD, deployment, infrastructure |
| `database/` | Database design and optimization |
| `data-ai/` | ML, data science, AI applications |
| `web-tools/` | Frontend, React, CSS, SEO |
| `documentation/` | Technical writing, docs generation |

### By Task

Common tasks and recommended components:

| Task | Component Type | Recommended |
|------|----------------|-------------|
| Review my code | Agent | `code-reviewer` |
| Fix a bug | Agent | `debugger` |
| Write tests | Agent | `test-engineer` |
| Create PR | Command | `/git:create-pr` |
| Run tests | Command | `/test:run` |
| Check code quality | Hook | `post_tool_use.py` |

### By Search

Use the list_components script to search:

```bash
# Search component names and descriptions
uv run scripts/list_components.py --search "review"

# Filter by type and search
uv run scripts/list_components.py --type agents --search "database"
```

## Next Steps

1. **Browse the catalog** - See [Component Catalog](COMPONENT_CATALOG.md) for the full list
2. **Learn about agents** - Read [Using Agents](USING_AGENTS.md)
3. **Set up hooks** - Read [Using Hooks](USING_HOOKS.md) for automated quality checks
4. **Create your own** - See templates in `steve/templates/`

## Getting Help

- **Documentation** - Browse the `docs/` directory
- **Examples** - See [Examples](EXAMPLES.md) for real-world usage
- **Troubleshooting** - See [Troubleshooting](TROUBLESHOOTING.md) for common issues
- **FAQ** - See [FAQ](FAQ.md) for common questions
