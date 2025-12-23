---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: agent
---

# Agents

Sub-agent configurations organized by domain and specialization.

## Structure

Agents are organized into domain directories:

- **`core/`** - Core system agents (meta, delegation, memory management)
- **`development/`** - Development workflow agents (debugging, refactoring, DX)
- **`code-quality/`** - Code quality and review agents
- **`expert-advisors/`** - Domain expert advisors (TypeScript, Docker, Git, etc.)
- **`ai-specialists/`** - AI/ML specialist agents
- **`data-ai/`** - Data science and AI engineering agents
- **`database/`** - Database administration and optimization agents
- **`devops-infrastructure/`** - DevOps and infrastructure agents
- **`documentation/`** - Documentation generation agents
- **`programming-languages/`** - Language-specific expert agents
- **`web-tools/`** - Web development tool specialists
- **`deep-research-team/`** - Research and analysis agents
- **`mcp/`** - MCP (Model Context Protocol) integration agents
- **`quality/`** - Quality assurance and testing agents
- **`codebase-ready/`** - Codebase preparation and validation agents
- **`utilitarian/`** - Utility agents for common tasks

## File Format

Each agent file uses YAML frontmatter followed by markdown content:

```yaml
---
name: agent-name
description: Action-oriented description starting with "Use PROACTIVELY for..." or "Specialist for..."
tools: Read, Write, Grep
model: sonnet  # haiku, sonnet, or opus
color: cyan    # red, blue, green, yellow, purple, orange, pink, cyan
skills: skill1, skill2  # Optional: comma-separated skill names
---
```

## Naming Conventions

- Use `kebab-case` for agent names (e.g., `code-reviewer`, `dependency-manager`)
- Names should be descriptive and indicate the agent's primary function
- Domain-specific agents should include domain prefix when helpful (e.g., `typescript-expert`)

## Required Fields

- **`name`**: Unique kebab-case identifier
- **`description`**: Action-oriented description that explains WHEN to use the agent

## Optional Fields

- **`tools`**: Comma-separated list of allowed tools. If omitted, agent gets ALL tools.
- **`model`**: Model to use (`haiku`, `sonnet`, `opus`). Defaults to `sonnet`.
- **`color`**: Display color for UI
- **`skills`**: Comma-separated list of skill names to load

## Content Structure

Agent files should include:

1. **Purpose** - Clear role definition
2. **Instructions** - Numbered step-by-step workflow
3. **Best Practices** - Domain-specific guidance
4. **Output Format** - Expected response structure (if applicable)

## Creating New Agents

1. Choose the appropriate domain directory
2. Create a new `.md` file with kebab-case name
3. Use the template from `steve/templates/AGENT_PLAYBOOK.template.md`
4. Follow the frontmatter and content structure guidelines
5. Test the agent configuration

## Examples

See existing agents in each domain directory for reference patterns.
