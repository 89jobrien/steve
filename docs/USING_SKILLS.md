# Using Skills

Skills are reusable bundles of domain expertise that agents can reference. This guide explains how skills work
and how to use them effectively.

## What is a Skill?

A skill is a directory containing domain knowledge, methodologies, and optional helper resources:

```text
skills/code-review/
├── SKILL.md           # Main skill definition (required)
├── references/        # Supporting documentation (optional)
│   ├── checklist.md
│   └── patterns.md
├── scripts/           # Helper scripts (optional)
│   └── analyze.py
└── assets/            # Generated outputs (optional)
    └── report.md
```

Skills provide consistent, reusable expertise that multiple agents can share.

## Skill Structure

### SKILL.md (Required)

The main skill file contains YAML frontmatter and markdown content:

```yaml
---
name: code-review
description: Expert code review methodology for quality and security
---

# Code Review Skill

This skill provides systematic code review methodology.

## When to Use

Use this skill when:
- Reviewing pull requests
- Auditing code quality
- Identifying security issues

## Methodology

1. **Understand Context** - Read the PR description and related issues
2. **Check Architecture** - Verify design patterns and structure
3. **Review Logic** - Trace code flow and edge cases
4. **Assess Security** - Look for vulnerabilities
5. **Evaluate Style** - Check formatting and conventions

## Checklist

- [ ] No hardcoded secrets
- [ ] Error handling is appropriate
- [ ] Tests cover new functionality
...
```

### references/ (Optional)

Supporting documentation that provides additional context:

```text
references/
├── CHECKLIST.md       # Detailed checklists
├── PATTERNS.md        # Common patterns to look for
├── ANTI_PATTERNS.md   # Things to avoid
└── EXAMPLES.md        # Example reviews
```

### scripts/ (Optional)

Executable code that extends skill capabilities:

```text
scripts/
├── analyze.py         # Analysis helper
├── report.py          # Report generator
└── validate.py        # Validation script
```

### assets/ (Optional)

Generated outputs or templates:

```text
assets/
├── report_template.md
└── summary_template.md
```

## How Skills Work

### Agent References

Agents reference skills in their frontmatter:

```yaml
---
name: code-reviewer
skills: code-review, testing
---
```

When the agent is invoked, Claude Code automatically loads the referenced skills.

### Skill Loading

Skills are loaded in order of reference. The skill content becomes part of the agent's context,
providing domain expertise for the task.

### Skill Chaining

Multiple skills can work together:

```yaml
skills: code-review, security-audit, testing
```

The agent gains expertise from all referenced skills.

## Available Skills

### Development Skills

| Skill | Description |
|-------|-------------|
| `code-review` | Code review methodology |
| `debugging` | Debugging workflows and patterns |
| `testing` | TDD and testing practices |
| `dead-code-removal` | Unused code detection |

### Documentation Skills

| Skill | Description |
|-------|-------------|
| `documentation` | Technical writing standards |
| `git-workflow` | Git and PR conventions |
| `git-commit-helper` | Commit message generation |

### Infrastructure Skills

| Skill | Description |
|-------|-------------|
| `cloud-infrastructure` | AWS/Azure/GCP patterns |
| `network-engineering` | Network architecture |
| `shell-scripting` | Shell script best practices |

### Specialized Skills

| Skill | Description |
|-------|-------------|
| `database-optimization` | Query and schema optimization |
| `security-audit` | Security assessment methodology |
| `performance` | Performance optimization |
| `ai-ethics` | Responsible AI development |

See [Component Catalog](COMPONENT_CATALOG.md#skills) for the complete list.

## Using Skills in Practice

### With Agents

The most common way to use skills is through agents:

```text
Use the code-reviewer agent to review my changes
```

The `code-reviewer` agent automatically loads its referenced skills.

### Direct Reference

You can also reference skills directly in prompts:

```text
Using the code-review skill methodology, review src/auth.py
```

### Skill Commands

Some skills have associated commands:

```text
/skills:list          # List all skills
/skills:search test   # Search for testing skills
```

## Creating Custom Skills

### Basic Skill

Create a new skill directory:

```bash
mkdir -p ~/.claude/skills/my-skill
```

Create `SKILL.md`:

```yaml
---
name: my-skill
description: What this skill provides
---

# My Skill

## When to Use

Use this skill when...

## Methodology

1. First step
2. Second step
3. Third step

## Best Practices

- Practice one
- Practice two
```

### Skill with References

Add supporting documentation:

```bash
mkdir ~/.claude/skills/my-skill/references
```

Create reference files that expand on the main skill.

### Skill with Scripts

Add helper scripts:

```bash
mkdir ~/.claude/skills/my-skill/scripts
```

Scripts should be executable and well-documented.

### Using Templates

Use the skill template:

```bash
cp steve/templates/AGENT_SKILL.template.md ~/.claude/skills/my-skill/SKILL.md
```

Or use the meta command:

```text
/meta:create-skill api-design "REST API design patterns and best practices"
```

## Skill Best Practices

### Design Principles

1. **Single Responsibility** - Each skill should focus on one domain
2. **Reusability** - Design for use by multiple agents
3. **Completeness** - Include enough detail to be self-contained
4. **Practicality** - Focus on actionable guidance

### Content Guidelines

1. **When to Use** - Clear triggers for skill application
2. **Methodology** - Step-by-step process
3. **Checklists** - Concrete items to verify
4. **Examples** - Real-world applications
5. **Anti-patterns** - What to avoid

### Organization

1. **Clear Structure** - Consistent section headings
2. **Progressive Detail** - Overview first, details in references
3. **Cross-references** - Link to related skills
4. **Version Notes** - Track significant changes

## Skill Patterns

### The Methodology Pattern

Skills that define a process:

```yaml
---
name: incident-response
description: Systematic incident response methodology
---

## Phases

1. Detection
2. Triage
3. Investigation
4. Resolution
5. Post-mortem
```

### The Checklist Pattern

Skills that provide verification lists:

```yaml
---
name: deployment-checklist
description: Pre-deployment verification checklist
---

## Pre-Deployment

- [ ] All tests passing
- [ ] Code reviewed
- [ ] Documentation updated
- [ ] Rollback plan ready
```

### The Reference Pattern

Skills that collect domain knowledge:

```yaml
---
name: sql-patterns
description: Common SQL patterns and anti-patterns
---

## Query Patterns

### Pagination
```sql
SELECT * FROM users LIMIT 10 OFFSET 20;
```

### Anti-patterns to Avoid

- SELECT *
- Missing indexes
- N+1 queries

```

### The Toolbox Pattern

Skills with helper scripts:

```text
skill/
├── SKILL.md
└── scripts/
    ├── analyze.py
    ├── report.py
    └── validate.py
```

## Troubleshooting

### Skill Not Loading

1. Verify skill directory exists in `~/.claude/skills/`
2. Check `SKILL.md` exists in the skill directory
3. Verify frontmatter has `name` field
4. Check agent's `skills:` field matches skill name exactly

### Skill Content Not Applied

1. Verify the agent references the skill
2. Check skill content is relevant to the task
3. Try explicitly mentioning the skill in your prompt

### Script Not Running

1. Check script has execute permissions: `chmod +x script.py`
2. Verify Python path is correct
3. Test script manually: `uv run scripts/analyze.py`

## See Also

- [Component Catalog](COMPONENT_CATALOG.md#skills) - Browse all skills
- [Using Agents](USING_AGENTS.md) - How agents use skills
- [Installation](INSTALLATION.md) - Install new skills
- [Development](DEVELOPMENT.md) - Create custom skills
