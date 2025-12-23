# Installation Guide

This guide covers how to install Steve components into your Claude Code configuration.

## Prerequisites

Before installing components, ensure you have:

- **Claude Code** installed and configured
- **Python 3.10+** with `uv` package manager
- **Git** for cloning the repository
- **GitHub CLI** (optional, for Gist publishing)

## Installation Methods

### Method 1: Manual Copy (Recommended for Beginners)

The simplest way to install components is to copy them directly to your Claude Code configuration directory.

#### Step 1: Clone the Repository

```bash
git clone https://github.com/joe/steve.git
cd steve
```

#### Step 2: Locate Your Claude Code Directory

Claude Code stores its configuration in `~/.claude/`:

```text
~/.claude/
├── agents/           # Agent configurations
├── commands/         # Slash commands
├── skills/           # Skill bundles
├── hooks/            # Automated hooks
├── settings.json     # Claude Code settings
└── CLAUDE.md         # Global instructions
```

#### Step 3: Copy Components

```bash
# Install a single agent
cp steve/agents/code-quality/code-reviewer.md ~/.claude/agents/

# Install a skill (entire directory)
cp -r steve/skills/code-review ~/.claude/skills/

# Install a command
cp steve/commands/dev/review-code.md ~/.claude/commands/dev/

# Install a hook
cp steve/hooks/analyzers/lint_changed.md ~/.claude/hooks/
cp steve/hooks/analyzers/lint_changed.py ~/.claude/hooks/
```

### Method 2: Using the Install Script

Steve includes a helper script for installing components by name.

```bash
# Install a component by name
uv run scripts/install_component.py code-reviewer

# List available components first
uv run scripts/list_components.py

# Search for specific components
uv run scripts/list_components.py --search "database"
```

### Method 3: Install from Gist

Components can be published to and installed from GitHub Gists.

```bash
# Install from a Gist URL
uv run scripts/install_from_gist.py https://gist.github.com/user/abc123

# Install from a Gist ID
uv run scripts/install_from_gist.py abc123
```

### Method 4: Bulk Installation

To install multiple components at once:

```bash
# Install all agents from a domain
cp steve/agents/code-quality/*.md ~/.claude/agents/

# Install all commands from a category
cp steve/commands/dev/*.md ~/.claude/commands/dev/

# Install all skills
cp -r steve/skills/* ~/.claude/skills/
```

## Directory Structure

### Agents

Agents are single markdown files with YAML frontmatter:

```text
~/.claude/agents/
├── code-reviewer.md
├── debugger.md
└── test-engineer.md
```

### Skills

Skills are directories containing a main file and optional resources:

```text
~/.claude/skills/
├── code-review/
│   ├── SKILL.md           # Main skill definition
│   └── references/        # Supporting documentation
├── testing/
│   ├── SKILL.md
│   ├── references/
│   └── scripts/           # Helper scripts
└── documentation/
    └── SKILL.md
```

### Commands

Commands are markdown files organized by category:

```text
~/.claude/commands/
├── dev/
│   ├── review-code.md
│   └── containerize-application.md
├── git/
│   ├── clean-branches.md
│   └── git-bisect-helper.md
└── test/
    ├── run.md
    └── report.md
```

### Hooks

Hooks are Python files with companion markdown documentation:

```text
~/.claude/hooks/
├── analyzers/
│   ├── lint_changed.py
│   └── lint_changed.md
├── lifecycle/
│   ├── session_start.py
│   └── session_start.md
└── workflows/
    ├── post_tool_use.py
    └── post_tool_use.md
```

## Configuration

### Enabling Hooks

Hooks must be registered in your Claude Code settings. Edit `~/.claude/settings.json`:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "command": "python ~/.claude/hooks/analyzers/lint_changed.py $FILE"
      }
    ],
    "SessionStart": [
      {
        "command": "python ~/.claude/hooks/lifecycle/session_start.py"
      }
    ]
  }
}
```

### Agent Model Configuration

Agents specify their preferred model in frontmatter. Override in settings if needed:

```json
{
  "agentModelOverrides": {
    "code-reviewer": "opus",
    "debugger": "sonnet"
  }
}
```

### Skill References

Agents reference skills in their frontmatter:

```yaml
---
name: code-reviewer
skills: code-review, testing
---
```

The referenced skills must be installed in `~/.claude/skills/`.

## Verifying Installation

### Check Installed Agents

```bash
ls ~/.claude/agents/
```

In Claude Code, agents appear in the Task tool's `subagent_type` options.

### Check Installed Commands

```bash
ls ~/.claude/commands/
```

Commands are available via slash syntax: `/dev:review-code`, `/test:run`, etc.

### Check Installed Skills

```bash
ls ~/.claude/skills/
```

Skills are automatically loaded when agents reference them.

### Check Installed Hooks

```bash
ls ~/.claude/hooks/
```

Verify hooks are registered in `settings.json`.

## Updating Components

### Manual Update

Pull the latest changes and re-copy:

```bash
cd steve
git pull
cp steve/agents/code-quality/code-reviewer.md ~/.claude/agents/
```

### Version Tracking

Keep track of installed versions by maintaining a local manifest:

```bash
# Create a manifest of installed components
cat > ~/.claude/installed-components.json << 'EOF'
{
  "agents": ["code-reviewer", "debugger"],
  "skills": ["code-review", "testing"],
  "commands": ["dev/review-code", "test/run"],
  "source": "steve",
  "updated": "2024-01-15"
}
EOF
```

## Uninstalling Components

### Remove Individual Components

```bash
# Remove an agent
rm ~/.claude/agents/code-reviewer.md

# Remove a skill
rm -rf ~/.claude/skills/code-review

# Remove a command
rm ~/.claude/commands/dev/review-code.md

# Remove a hook
rm ~/.claude/hooks/analyzers/lint_changed.py
rm ~/.claude/hooks/analyzers/lint_changed.md
```

### Clean Hook Registration

After removing hooks, update `settings.json` to remove their registrations.

## Troubleshooting

### Agent Not Available

1. Verify the file exists in `~/.claude/agents/`
2. Check the frontmatter has required `name` field
3. Restart Claude Code to reload configurations

### Command Not Found

1. Verify the file exists in `~/.claude/commands/`
2. Check the file has `.md` extension
3. For nested commands, use the full path: `/category:command-name`

### Skill Not Loading

1. Verify the skill directory exists in `~/.claude/skills/`
2. Check `SKILL.md` exists in the skill directory
3. Verify the agent's `skills:` frontmatter lists the skill name correctly

### Hook Not Running

1. Verify the hook is registered in `settings.json`
2. Check the Python file is executable
3. Test the hook manually: `python ~/.claude/hooks/analyzers/lint_changed.py`
4. Check hook output in Claude Code logs

## Next Steps

- [Using Agents](USING_AGENTS.md) - Learn how to invoke and work with agents
- [Using Skills](USING_SKILLS.md) - Understand skill structure and usage
- [Using Commands](USING_COMMANDS.md) - Master slash command workflows
- [Using Hooks](USING_HOOKS.md) - Set up automated hooks
- [Component Catalog](COMPONENT_CATALOG.md) - Browse all available components
