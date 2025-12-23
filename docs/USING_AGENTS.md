# Using Agents

Agents are specialized AI assistants configured for specific tasks. This guide explains how to invoke, configure,
and work effectively with agents.

## What is an Agent?

An agent is a markdown file with YAML frontmatter that defines:

- **Name** - Unique identifier for invocation
- **Description** - What the agent does (used for agent selection)
- **Tools** - Which Claude Code tools the agent can use
- **Model** - Which Claude model powers it (haiku, sonnet, opus)
- **Skills** - Domain expertise the agent references

Example agent file (`code-reviewer.md`):

```yaml
---
name: code-reviewer
description: Reviews code for bugs, security vulnerabilities, and best practices
tools: Read, Grep, Glob, Edit
model: sonnet
skills: code-review
---

# Code Reviewer

You are an expert code reviewer specializing in identifying bugs, security issues,
and opportunities for improvement.

## Instructions

1. Read the code thoroughly before making suggestions
2. Prioritize issues by severity (critical, high, medium, low)
3. Provide actionable feedback with specific line references
...
```

## Invoking Agents

### Via Task Tool

Agents are invoked using the Task tool with the `subagent_type` parameter:

```text
Use the Task tool to invoke the code-reviewer agent to review src/main.py
```

Claude Code translates this to:

```json
{
  "tool": "Task",
  "parameters": {
    "subagent_type": "code-reviewer",
    "prompt": "Review src/main.py for bugs and best practices",
    "description": "Code review of main.py"
  }
}
```

### Via Natural Language

You can request agents naturally:

```text
@code-reviewer Please review my latest changes
```

```text
Have the debugger investigate the error in auth.py
```

```text
Ask the backend-architect to design the API for user management
```

### Via Commands

Some commands invoke agents internally:

```text
/dev:review-code src/main.py
```

This command may invoke the `code-reviewer` agent behind the scenes.

## Agent Selection

### Finding the Right Agent

Use the agent finder command:

```text
/agents:find I need to optimize my database queries
```

Or search by keyword:

```text
/agents:search database
```

### Agent Categories

Agents are organized by domain:

| Domain | Use Cases |
|--------|-----------|
| `code-quality` | Code review, linting, refactoring |
| `development` | Debugging, feature development |
| `devops-infrastructure` | CI/CD, deployment, Docker |
| `database` | Schema design, query optimization |
| `data-ai` | ML pipelines, data analysis |
| `documentation` | Technical writing, API docs |
| `quality` | Testing, TDD, performance |
| `web-tools` | Frontend, SEO, accessibility |

### Recommended Agents by Task

| Task | Agent |
|------|-------|
| Review code changes | `code-reviewer` |
| Debug an error | `debugger` |
| Write tests | `test-engineer` |
| Design database schema | `database-architect` |
| Optimize queries | `database-optimizer` |
| Set up CI/CD | `github-actions-expert` |
| Create Docker setup | `docker-expert` |
| Research a topic | `research-orchestrator-v2` |

## Agent Configuration

### Frontmatter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Unique identifier (kebab-case) |
| `description` | Yes | What the agent does |
| `tools` | No | Comma-separated tool list |
| `model` | No | `haiku`, `sonnet`, or `opus` (default: sonnet) |
| `skills` | No | Comma-separated skill names |
| `color` | No | Terminal color for output |

### Tool Restrictions

Agents can only use tools listed in their `tools` field:

```yaml
tools: Read, Grep, Glob  # Read-only agent
```

```yaml
tools: Read, Write, Edit, Bash  # Full access agent
```

```yaml
tools: All tools  # Unrestricted access
```

Common tool combinations:

| Use Case | Tools |
|----------|-------|
| Read-only analysis | `Read, Grep, Glob` |
| Code modification | `Read, Write, Edit, Grep, Glob` |
| Full development | `Read, Write, Edit, Bash, Grep, Glob` |
| Research | `Read, WebFetch, WebSearch` |

### Model Selection

Choose the model based on task complexity:

| Model | Best For |
|-------|----------|
| `haiku` | Simple, fast tasks (formatting, quick lookups) |
| `sonnet` | Most tasks (code review, debugging, development) |
| `opus` | Complex reasoning (architecture, research synthesis) |

### Skill References

Skills provide domain expertise. Reference them in frontmatter:

```yaml
skills: code-review, testing
```

The agent automatically loads these skills when invoked.

## Working with Agent Output

### Understanding Results

Agent results are returned to the main conversation. The output includes:

- Task completion summary
- Any files created or modified
- Recommendations or findings
- Errors encountered

### Continuing Work

After an agent completes, you can:

1. **Ask follow-up questions** about the results
2. **Invoke another agent** to continue the work
3. **Take manual action** based on recommendations

### Agent Chaining

Chain multiple agents for complex workflows:

```text
1. Use code-reviewer to review the changes
2. Based on the review, use debugger to fix any issues
3. Use test-engineer to write tests for the fixes
```

## Creating Custom Agents

### Basic Structure

Create a new agent file in `~/.claude/agents/`:

```yaml
---
name: my-custom-agent
description: Does something specific
tools: Read, Write, Edit
model: sonnet
---

# My Custom Agent

[Purpose and instructions here]
```

### Using Templates

Use the agent template from Steve:

```bash
cp steve/templates/SUBAGENT.template.md ~/.claude/agents/my-agent.md
```

Or use the meta command:

```text
/meta:create-subagent code analyzer for Python async patterns
```

### Best Practices

1. **Be specific** - Clear description helps agent selection
2. **Limit tools** - Only grant necessary permissions
3. **Reference skills** - Leverage existing expertise
4. **Include examples** - Show expected behavior
5. **Define scope** - What the agent should and shouldn't do

## Agent Patterns

### The Specialist Pattern

Create focused agents for specific domains:

```yaml
---
name: python-async-expert
description: Specializes in Python asyncio patterns and debugging
tools: Read, Grep, Glob, Edit
skills: debugging, python-scripting
---
```

### The Orchestrator Pattern

Create agents that coordinate other agents:

```yaml
---
name: code-quality-orchestrator
description: Coordinates code review, testing, and documentation agents
tools: Task, Read
---
```

### The Guardian Pattern

Create agents that validate and enforce standards:

```yaml
---
name: security-guardian
description: Validates code for security vulnerabilities before commit
tools: Read, Grep, Glob
skills: security-audit
---
```

## Troubleshooting

### Agent Not Found

1. Verify the file exists in `~/.claude/agents/`
2. Check the `name` field in frontmatter matches what you're invoking
3. Restart Claude Code to reload configurations

### Agent Using Wrong Tools

1. Check the `tools` field in frontmatter
2. Ensure tools are comma-separated
3. Use exact tool names: `Read`, `Write`, `Edit`, `Bash`, `Grep`, `Glob`, `Task`

### Agent Not Using Skills

1. Verify skills are installed in `~/.claude/skills/`
2. Check skill names match exactly (case-sensitive)
3. Ensure `SKILL.md` exists in each skill directory

### Agent Producing Poor Results

1. **Improve the description** - More specific descriptions lead to better behavior
2. **Add instructions** - Include detailed guidance in the markdown body
3. **Use a better model** - Try `opus` for complex tasks
4. **Reference skills** - Add domain expertise

## See Also

- [Component Catalog](COMPONENT_CATALOG.md) - Browse all agents
- [Using Skills](USING_SKILLS.md) - Understand skill references
- [Installation](INSTALLATION.md) - Install new agents
- [Development](DEVELOPMENT.md) - Create custom agents
