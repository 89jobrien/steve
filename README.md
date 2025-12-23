# steve

Centralized repository for Claude Code agent configurations, hooks, commands, skills, and templates.

## Project Status

| Metric         | Value                                                                  |
| -------------- | ---------------------------------------------------------------------- |
| **Components** | 377 total (137 agents, 97 commands, 57 skills, 59 hooks, 27 templates) |
| **Test Suite** | 415 tests passing                                                      |
| **Coverage**   | 82.5%                                                                  |
| **Python**     | 3.10+                                                                  |

## Overview

This repository provides a well-organized collection of reusable components for Claude Code, including:

- **Agents** - Sub-agent configurations organized by domain and specialization
- **Hooks** - Claude hooks for analysis, guards, workflows, and lifecycle events
- **Commands** - Slash commands for various development workflows
- **Skills** - Reusable skills with bundled resources
- **Rules** - Language and format-specific coding rules
- **Templates** - Templates for creating new components

## Map of Contents

### Core Modules

| Module                        | Description                        | Location           |
| ----------------------------- | ---------------------------------- | ------------------ |
| [Agents](steve/agents/)       | Sub-agent configurations by domain | `steve/agents/`    |
| [Commands](steve/commands/)   | Slash commands for workflows       | `steve/commands/`  |
| [Skills](steve/skills/)       | Reusable domain knowledge bundles  | `steve/skills/`    |
| [Hooks](steve/hooks/)         | Event-driven automation            | `steve/hooks/`     |
| [Templates](steve/templates/) | Component scaffolds                | `steve/templates/` |
| [Rules](steve/rules/)         | Language-specific coding rules     | `steve/rules/`     |
| [Helpers](steve/helpers/)     | Python utility modules             | `steve/helpers/`   |

### Scripts

| Script                                              | Description                  | Location                        |
| --------------------------------------------------- | ---------------------------- | ------------------------------- |
| [build_index](scripts/build_index.py)               | Build component index        | `scripts/build_index.py`        |
| [list_components](scripts/list_components.py)       | Search and list components   | `scripts/list_components.py`    |
| [install_component](scripts/install_component.py)   | Install by name              | `scripts/install_component.py`  |
| [install_from_gist](scripts/install_from_gist.py)   | Install from GitHub Gist     | `scripts/install_from_gist.py`  |
| [publish_to_gist](scripts/publish_to_gist.py)       | Publish to Gist              | `scripts/publish_to_gist.py`    |
| [publish_all](scripts/publish_all.py)               | Batch publish all components | `scripts/publish_all.py`        |
| [add_metadata](scripts/add_metadata.py)             | Update frontmatter metadata  | `scripts/add_metadata.py`       |
| [batch_add_metadata](scripts/batch_add_metadata.py) | Batch metadata updates       | `scripts/batch_add_metadata.py` |
| [detect_secrets](scripts/detect_secrets.py)         | Security scanning            | `scripts/detect_secrets.py`     |

### Documentation

| Document                                       | Description                |
| ---------------------------------------------- | -------------------------- |
| [Getting Started](docs/GETTING_STARTED.md)     | Quick start guide          |
| [Installation](docs/INSTALLATION.md)           | Detailed installation      |
| [Architecture](docs/ARCHITECTURE.md)           | System design              |
| [Development](docs/DEVELOPMENT.md)             | Development workflow       |
| [Using Agents](docs/USING_AGENTS.md)           | Agent usage guide          |
| [Using Commands](docs/USING_COMMANDS.md)       | Command usage guide        |
| [Using Skills](docs/USING_SKILLS.md)           | Skill usage guide          |
| [Using Hooks](docs/USING_HOOKS.md)             | Hook usage guide           |
| [Contributing](docs/CONTRIBUTING.md)           | Contribution guidelines    |
| [Scripts Reference](docs/SCRIPTS_REFERENCE.md) | Script documentation       |
| [FAQ](docs/FAQ.md)                             | Frequently asked questions |

## Repository Structure

```
steve/
├── agents/              # Sub-agent configurations
│   ├── core/           # Core system agents
│   ├── development/    # Development workflow agents
│   ├── code-quality/   # Code quality and review agents
│   ├── expert-advisors/# Domain expert advisors
│   └── ...             # More specialized domains
│
├── hooks/               # Claude hooks
│   ├── analyzers/      # Code analysis hooks
│   ├── guards/         # Guard hooks (pre-commit checks)
│   ├── workflows/      # Workflow automation hooks
│   ├── lifecycle/      # Lifecycle event hooks
│   └── context/        # Context management hooks
│
├── commands/            # Slash commands
│   ├── _team/          # Team collaboration commands
│   ├── agents/         # Agent management commands
│   ├── git/            # Git workflow commands
│   ├── dev/            # Development commands
│   └── ...             # More command categories
│
├── skills/              # Reusable skills
│   ├── skill-name/     # Each skill in its own directory
│   │   ├── SKILL.md    # Main skill definition
│   │   ├── references/ # Documentation references
│   │   ├── scripts/    # Executable code
│   │   └── assets/     # Output files
│   └── ...
│
├── rules/               # Language-specific rules
│   ├── python.md
│   ├── typescript.md
│   ├── shell.md
│   └── ...
│
├── templates/           # Component templates
│   ├── AGENT_PLAYBOOK.template.md
│   ├── AGENT_SKILL.template.md
│   ├── SLASH_COMMAND.template.md
│   └── ...
│
├── helpers/             # Python helper modules
│   ├── context_monitor.py
│   ├── debug_rotation.py
│   ├── history_archival.py
│   └── ...
│
└── scripts/             # Python management scripts
    ├── build_index.py
    ├── install_component.py
    ├── list_components.py
    └── ...
```

## Component Organization

### Domain/Specialization Hierarchy

Components are organized by domain and specialization to enable:

- **Easy discovery** - Find components by domain
- **Logical grouping** - Related components are co-located
- **Scalability** - Add new domains without restructuring

### Naming Conventions

- **Agents**: `kebab-case` (e.g., `code-reviewer`, `dependency-manager`)
- **Skills**: `kebab-case` (e.g., `code-context-finder`, `tdd-pytest`)
- **Commands**: `kebab-case.md` (e.g., `create-subagent.md`)
- **Hooks**: `kebab-case.py` and `kebab-case.md` pairs

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/joe/steve.git
cd steve

# Install dependencies
uv sync

# Build the component index
uv run scripts/build_index.py

# Run tests
uv run pytest
```

```bash
# Index
make run-index                              # Build index
make run-index ARGS="--verbose"             # With options

# List
make run-list                               # List all
make run-list ARGS="--type agent"           # Filter by type

# Install
make run-install ARGS="python-pro"          # Install component

# Publish
make run-publish                            # Publish ALL
make run-publish ARGS="steve/agents/core/*.md"  # Glob
make run-publish ARGS="steve/agents/core/example-agent.md"  # Single

# Secrets
make run-secrets ARGS="--scan"              # Scan
make run-secrets ARGS="--baseline"          # Baseline

# Metadata
make run-metadata ARGS="steve/agents/core/example-agent.md"
make run-metadata ARGS="steve/agents/core/*.md"  # Glob
make run-metadata ARGS="steve/agents/core/*.md --gist-url https://..."  # Glob with options

# Batch metadata
make run-batch-metadata ARGS='steve/agents --dry-run'
make run-batch-metadata ARGS='steve/agents --key version 1.0.1'
make run-batch-metadata ARGS='steve/agents --key author "Joseph OBrien" --key status unpublished --key updated 2025-12-23 --key version 1.0.1 --dry-run'
make run-batch-metadata ARGS='steve/agents/core --pattern "*.md" --key category core'
make run-batch-metadata ARGS='steve/skills --pattern "**/SKILL.md" --key type skill'

```

### Using Components

```bash
# List available components
uv run scripts/list_components.py

# Search for specific components
uv run scripts/list_components.py --search "code review"

# Install a component
uv run scripts/install_component.py code-reviewer
```

### Creating New Components

1. Use templates from `steve/templates/`
2. Follow naming conventions (kebab-case)
3. Include YAML frontmatter where applicable
4. Add README.md for complex components

## File Formats

### Agent Files

```yaml
---
name: agent-name
description: Action-oriented description
tools: Read, Write, Grep
model: sonnet
color: cyan
skills: skill1, skill2
---
# Purpose
---
## Instructions
```

### Skill Files

```yaml
---
name: skill-name
description: Third-person description
---
# Skill Title
```

## Contributing

1. Follow the domain/specialization structure
2. Use kebab-case naming conventions
3. Include YAML frontmatter where applicable
4. Add README.md files for complex components
5. Run secrets detection before committing (see Security section)

## Security

- **Secrets Detection**: Configured via `.pre-commit-config.yaml`
- **Sensitive Files**: Excluded via `.gitignore`
- **Public Repository**: Ensure no secrets are committed

## Scripts Reference

| Script                  | Description                           |
| ----------------------- | ------------------------------------- |
| `build_index.py`        | Build component index from repository |
| `list_components.py`    | List and search components            |
| `install_component.py`  | Install components to Claude Code     |
| `install_from_gist.py`  | Install from GitHub Gist              |
| `publish_to_gist.py`    | Publish components to Gist            |
| `publish_registry.py`   | Publish registry to Gist              |
| `add_metadata.py`       | Update component frontmatter          |
| `detect_secrets.py`     | Scan for secrets in codebase          |
| `python_to_markdown.py` | Convert Python to Markdown            |

## Documentation

- [Getting Started](docs/GETTING_STARTED.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Development Guide](docs/DEVELOPMENT.md)
- [Contributing](docs/CONTRIBUTING.md)
- [Scripts Reference](docs/SCRIPTS_REFERENCE.md)
- [FAQ](docs/FAQ.md)

See `CLAUDE.md` for Claude Code-specific configuration and `docs/` for complete documentation.
