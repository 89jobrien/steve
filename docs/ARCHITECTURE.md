# Architecture

This document describes the design decisions, patterns, and principles underlying the Steve component system.

## Overview

Steve is a modular component library for Claude Code. It provides reusable agents, skills, commands, hooks, and
templates that extend Claude Code's capabilities through a consistent architecture.

## Design Principles

### 1. Composition Over Inheritance

Components are designed to be composed rather than extended:

- **Agents** reference skills instead of duplicating knowledge
- **Skills** are modular bundles that multiple agents can share
- **Commands** invoke agents rather than reimplementing their logic
- **Hooks** are independent scripts that can be combined

This enables mixing and matching components without tight coupling.

### 2. Convention Over Configuration

Steve follows predictable conventions to minimize configuration:

| Convention | Example |
|------------|---------|
| Naming | `kebab-case` for all component names |
| Location | Component type determines directory (`agents/`, `skills/`, etc.) |
| Format | Markdown with YAML frontmatter |
| Structure | Consistent section ordering |

### 3. Progressive Disclosure

Components reveal complexity gradually:

- **Basic usage** requires only name and invocation
- **Configuration** is optional with sensible defaults
- **Customization** is available for advanced users

### 4. Separation of Concerns

Each component type has a distinct responsibility:

| Component | Responsibility |
|-----------|---------------|
| Agent | Task execution with specific tools/model |
| Skill | Domain knowledge and methodology |
| Command | User-facing workflow automation |
| Hook | Event-driven automation |
| Template | Scaffolding for new components |

## Component Model

### Component Hierarchy

```text
User Request
    │
    ▼
┌─────────┐     ┌──────────┐
│ Command │────▶│  Agent   │
└─────────┘     └────┬─────┘
                     │
              ┌──────┴──────┐
              │             │
              ▼             ▼
         ┌─────────┐   ┌─────────┐
         │  Skill  │   │  Tools  │
         └─────────┘   └─────────┘
```

**Flow:**

1. User invokes a command or requests an agent
2. Command may invoke one or more agents
3. Agent loads referenced skills for domain expertise
4. Agent uses permitted tools to complete the task

### Component Metadata

All components use YAML frontmatter for metadata:

```yaml
---
name: component-name          # Unique identifier (required)
description: What it does     # Purpose description (required)
tools: Read, Write, Edit      # Tool restrictions (agents only)
model: sonnet                 # Model selection (agents only)
skills: skill1, skill2        # Skill references (agents only)
---
```

### Component Lifecycle

```text
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  Create  │───▶│ Install  │───▶│  Invoke  │───▶│  Result  │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
     │               │               │               │
     ▼               ▼               ▼               ▼
  Template      Copy to           Task tool      Output to
  scaffolds     ~/.claude/        executes       conversation
```

## Agent Architecture

### Agent Structure

```text
agent-name.md
├── Frontmatter (YAML)
│   ├── name: unique identifier
│   ├── description: task-oriented description
│   ├── tools: permitted tool list
│   ├── model: haiku/sonnet/opus
│   └── skills: referenced skills
│
└── Body (Markdown)
    ├── Purpose section
    ├── Instructions section
    └── Best Practices section
```

### Agent Selection

Claude Code uses the agent description for selection:

```text
User Request: "Review my code for security issues"
                    │
                    ▼
┌─────────────────────────────────────────┐
│        Agent Description Matching       │
│                                         │
│  "security" + "code review" matches:    │
│  - code-reviewer (code quality)         │
│  - security-engineer (security focus)   │
└─────────────────────────────────────────┘
                    │
                    ▼
            Best match selected
```

### Agent Tool Restrictions

Tools are explicitly granted to limit agent capabilities:

| Pattern | Tools | Use Case |
|---------|-------|----------|
| Read-only | `Read, Grep, Glob` | Analysis, research |
| Edit | `Read, Write, Edit, Grep, Glob` | Code modification |
| Full | `All tools` or explicit list | Complex tasks |
| Orchestrator | `Task` | Coordinating other agents |

### Agent Model Selection

Model choice impacts capability and cost:

| Model | Characteristics | Best For |
|-------|-----------------|----------|
| haiku | Fast, economical | Simple tasks, formatting |
| sonnet | Balanced | Most development tasks |
| opus | Powerful reasoning | Complex architecture, research |

## Skill Architecture

### Skill Structure

```text
skill-name/
├── SKILL.md           # Main definition (required)
│   ├── Frontmatter
│   │   ├── name
│   │   └── description
│   └── Body
│       ├── When to Use
│       ├── Methodology
│       └── Checklists
│
├── references/        # Supporting docs (optional)
│   ├── patterns.md
│   └── anti-patterns.md
│
├── scripts/           # Helper code (optional)
│   └── analyze.py
│
└── assets/            # Generated outputs (optional)
    └── template.md
```

### Skill Loading

Skills are loaded when agents reference them:

```text
Agent Invocation
       │
       ▼
┌──────────────────┐
│ Read Frontmatter │
│ skills: a, b, c  │
└────────┬─────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌───────┐ ┌───────┐
│Skill A│ │Skill B│ ...
└───────┘ └───────┘
    │         │
    └────┬────┘
         ▼
┌──────────────────┐
│ Merged Context   │
│ (agent + skills) │
└──────────────────┘
```

### Skill Composition

Skills can be composed for complex tasks:

```yaml
# Agent referencing multiple skills
skills: code-review, security-audit, testing
```

The agent receives combined expertise from all referenced skills.

## Command Architecture

### Command Structure

```text
command-name.md
├── Frontmatter (YAML)
│   ├── description: what it does
│   ├── argument-hint: expected args
│   └── allowed-tools: tool restrictions
│
└── Body (Markdown)
    ├── Instructions
    ├── Process steps
    └── Expected output
```

### Command Namespacing

Commands are organized by category:

```text
~/.claude/commands/
├── dev/
│   └── review-code.md      → /dev:review-code
├── git/
│   └── clean-branches.md   → /git:clean-branches
└── my-command.md           → /my-command
```

### Command Execution

```text
/dev:review-code src/main.py
         │
         ▼
┌────────────────────────┐
│  Load command file     │
│  dev/review-code.md    │
└───────────┬────────────┘
            │
            ▼
┌────────────────────────┐
│  Expand to prompt      │
│  with arguments        │
└───────────┬────────────┘
            │
            ▼
┌────────────────────────┐
│  Execute instructions  │
│  (may invoke agents)   │
└────────────────────────┘
```

## Hook Architecture

### Hook Types

| Type | Event | Purpose |
|------|-------|---------|
| PreToolUse | Before tool execution | Validation, preprocessing |
| PostToolUse | After tool execution | Analysis, follow-up actions |
| SessionStart | Session begins | Context loading, initialization |
| SessionEnd | Session ends | Cleanup, summarization |
| UserPrompt | User sends message | Context injection |

### Hook Configuration

Hooks are registered in `settings.json`:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "command": "python ~/.claude/hooks/analyzers/lint.py $FILE"
      }
    ]
  }
}
```

### Hook Execution Flow

```text
Tool Invocation (e.g., Write)
              │
              ▼
┌─────────────────────────────┐
│     Check hook matchers     │
│     "Write|Edit" matches    │
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│    Execute hook script      │
│    with environment vars    │
│    ($FILE, $TOOL, etc.)     │
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│    Hook output appears      │
│    in conversation          │
└─────────────────────────────┘
```

### Hook Patterns

Common hook implementation patterns:

| Pattern | Purpose | Exit Code |
|---------|---------|-----------|
| Guard | Block problematic changes | Non-zero to block |
| Reporter | Generate reports | Zero (informational) |
| Context | Inject information | Zero |

## Directory Structure

### Repository Layout

```text
steve/
├── agents/                    # Agent definitions
│   ├── code-quality/          # Domain grouping
│   ├── development/
│   └── ...
│
├── skills/                    # Skill bundles
│   ├── code-review/
│   │   ├── SKILL.md
│   │   └── references/
│   └── ...
│
├── commands/                  # Slash commands
│   ├── dev/                   # Category grouping
│   ├── git/
│   └── ...
│
├── hooks/                     # Automation hooks
│   ├── analyzers/
│   ├── lifecycle/
│   └── ...
│
├── templates/                 # Component templates
│
├── scripts/                   # Management utilities
│
└── docs/                      # Documentation
```

### Claude Code Layout

When installed, components live in `~/.claude/`:

```text
~/.claude/
├── agents/          # Installed agents
├── skills/          # Installed skills
├── commands/        # Installed commands
├── hooks/           # Installed hooks
├── settings.json    # Hook registration
└── CLAUDE.md        # Global instructions
```

## Data Flow

### Request Processing

```text
User: "Review the authentication code"
                    │
                    ▼
┌───────────────────────────────────────┐
│            Claude Code                │
│                                       │
│  1. Parse request                     │
│  2. Identify task (code review)       │
│  3. Select agent (code-reviewer)      │
│  4. Load skills (code-review)         │
│  5. Execute with tools (Read, Grep)   │
│  6. Return results                    │
└───────────────────────────────────────┘
                    │
                    ▼
        Results in conversation
```

### Hook Data Flow

```text
Claude Code writes file
          │
          ▼
┌─────────────────────┐
│   PostToolUse       │
│   event triggered   │
└──────────┬──────────┘
           │
    ┌──────┴──────┐
    │  matcher:   │
    │  Write|Edit │
    └──────┬──────┘
           │ matches
           ▼
┌─────────────────────┐
│   Execute hook      │
│   with $FILE env    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Hook output to    │
│   stdout/stderr     │
└──────────┬──────────┘
           │
           ▼
    Output in chat
```

## Extension Points

### Adding New Agents

1. Create markdown file with frontmatter
2. Define tools, model, skills
3. Write instructions in body
4. Place in appropriate domain directory

### Adding New Skills

1. Create skill directory
2. Add `SKILL.md` with methodology
3. Optionally add references, scripts, assets
4. Reference from agents via `skills:` field

### Adding New Commands

1. Create markdown file with frontmatter
2. Define allowed-tools, argument-hint
3. Write instructions
4. Place in category directory

### Adding New Hooks

1. Create Python script
2. Create companion markdown documentation
3. Register in `settings.json`
4. Test manually before enabling

## Design Decisions

### Why Markdown?

- **Human-readable**: Easy to review and modify
- **Version-control friendly**: Clean diffs
- **Tool-agnostic**: Works with any editor
- **Structured**: YAML frontmatter for metadata

### Why YAML Frontmatter?

- **Separation**: Metadata distinct from content
- **Standardized**: Well-known format
- **Flexible**: Supports various data types
- **Parseable**: Easy to extract programmatically

### Why Directory-Based Skills?

- **Bundling**: Keep related resources together
- **Modularity**: Easy to add/remove skills
- **Organization**: Clear structure for complex skills
- **Discoverability**: Browse skill contents

### Why Event-Based Hooks?

- **Decoupled**: Hooks don't know about each other
- **Composable**: Multiple hooks per event
- **Non-blocking**: Optional timeout handling
- **Transparent**: Clear trigger conditions

## Performance Considerations

### Agent Selection

- Keep descriptions concise but specific
- Use domain-appropriate keywords
- Avoid overly broad descriptions

### Skill Loading

- Reference only needed skills
- Keep skill content focused
- Use references/ for verbose content

### Hook Execution

- Hooks run synchronously
- Use timeouts to prevent blocking
- Filter early to skip unnecessary processing

## Security Considerations

### Tool Restrictions

- Grant minimum necessary tools
- Prefer read-only for analysis agents
- Document tool requirements

### Hook Safety

- Validate inputs in hook scripts
- Avoid shell injection vulnerabilities
- Don't expose secrets in output

### Skill Content

- Review skill content before installing
- Don't include sensitive patterns
- Keep executable scripts minimal

## See Also

- [Getting Started](GETTING_STARTED.md) - Quick start guide
- [Component Catalog](COMPONENT_CATALOG.md) - Browse all components
- [Using Agents](USING_AGENTS.md) - Agent invocation
- [Using Skills](USING_SKILLS.md) - Skill usage
- [Using Commands](USING_COMMANDS.md) - Command usage
- [Using Hooks](USING_HOOKS.md) - Hook configuration
