# Best Practices

Guidelines for creating, organizing, and maintaining high-quality Steve components.

## General Principles

### 1. Single Responsibility

Each component should do one thing well:

```yaml
# Good: Focused purpose
name: code-reviewer
description: Reviews code for quality, security, and best practices

# Bad: Too broad
name: code-helper
description: Reviews, writes, tests, deploys, and documents code
```

### 2. Explicit Over Implicit

Be clear about what a component does:

```yaml
# Good: Clear tool restrictions
tools: Read, Grep, Glob

# Bad: Overly permissive
tools: All tools
```

### 3. Composition Over Duplication

Reference shared skills instead of duplicating knowledge:

```yaml
# Good: Reference shared skill
skills: code-review, security-audit

# Bad: Duplicate instructions in every agent
```

### 4. Convention Over Configuration

Follow established patterns:

- Use `kebab-case` for names
- Place files in appropriate directories
- Use standard frontmatter fields

## Agent Best Practices

### Naming

```yaml
# Good: Descriptive, action-oriented
name: code-reviewer
name: security-auditor
name: performance-optimizer

# Bad: Vague or generic
name: helper
name: assistant
name: tool
```

### Descriptions

Write descriptions that help Claude select the right agent:

```yaml
# Good: Specific with keywords
description: >-
  Reviews Python and JavaScript code for quality issues, security vulnerabilities,
  performance problems, and adherence to best practices. Provides actionable feedback.

# Bad: Too generic
description: Reviews code
```

### Tool Selection

Grant minimum necessary tools:

| Task Type | Recommended Tools |
|-----------|------------------|
| Analysis only | `Read, Grep, Glob` |
| Code modification | `Read, Write, Edit, Grep, Glob` |
| Testing | `Read, Write, Edit, Bash, Grep, Glob` |
| Orchestration | `Task, Read` |

```yaml
# Good: Restricted to needs
tools: Read, Grep, Glob

# Acceptable: When modification needed
tools: Read, Write, Edit, Grep, Glob

# Caution: Full access
tools: All tools
```

### Model Selection

Choose appropriate models:

| Model | Use For |
|-------|---------|
| `haiku` | Simple formatting, quick lookups, repetitive tasks |
| `sonnet` | Most development tasks, code review, debugging |
| `opus` | Complex architecture, research, nuanced analysis |

```yaml
# Simple task
model: haiku

# Standard development
model: sonnet

# Complex reasoning
model: opus
```

### Skill References

Reference only necessary skills:

```yaml
# Good: Focused skills
skills: code-review, security-audit

# Bad: Kitchen sink
skills: code-review, security-audit, testing, documentation, performance, debugging
```

### Instructions

Write clear, actionable instructions:

```markdown
## Instructions

1. Read the target file(s) completely
2. Identify issues by category:
   - Security vulnerabilities
   - Performance problems
   - Code quality issues
3. Provide specific, actionable feedback
4. Include code examples for fixes
```

Avoid:

- Vague directives ("be helpful")
- Redundant instructions (Claude already knows basics)
- Overly long explanations

## Skill Best Practices

### Structure

Follow the standard skill structure:

```text
skill-name/
├── SKILL.md           # Required: Main definition
├── references/        # Optional: Supporting documentation
│   ├── patterns.md
│   └── anti-patterns.md
├── scripts/           # Optional: Helper code
│   └── analyze.py
└── assets/            # Optional: Generated outputs
```

### SKILL.md Content

Include essential sections:

```markdown
---
name: skill-name
description: What this skill provides
---

## When to Use

Clear criteria for when this skill applies.

## Methodology

Step-by-step process or framework.

## Checklists

- [ ] Verification items
- [ ] Quality checks

## Examples

Concrete examples of application.
```

### Progressive Disclosure

Keep main skill file focused:

```markdown
# In SKILL.md
## Methodology
1. Identify patterns
2. Apply transformations
3. Validate results

See `references/patterns.md` for detailed pattern catalog.
```

Move detailed content to `references/`:

```text
references/
├── patterns.md        # Detailed pattern explanations
├── anti-patterns.md   # What to avoid
└── examples.md        # Extended examples
```

### Reusability

Design skills for multiple agents:

```yaml
# Skill used by multiple agents
name: code-review

# Agent 1
name: code-reviewer
skills: code-review

# Agent 2
name: security-engineer
skills: code-review, security-audit
```

## Command Best Practices

### Naming

Use clear, verb-based names:

```text
# Good
review-code.md
clean-branches.md
run-tests.md

# Bad
code.md
branches.md
tests.md
```

### Namespacing

Group related commands:

```text
commands/
├── dev/
│   ├── review-code.md      # /dev:review-code
│   └── debug-error.md      # /dev:debug-error
├── git/
│   ├── clean-branches.md   # /git:clean-branches
│   └── create-pr.md        # /git:create-pr
└── test/
    ├── run.md              # /test:run
    └── report.md           # /test:report
```

### Arguments

Document expected arguments:

```yaml
---
description: Review code for quality issues
argument-hint: [file-path] | [commit-hash] | [--verbose]
allowed-tools: Read, Grep, Glob
---
```

### Instructions

Write commands as task specifications:

```markdown
## Task

Review the code at $ARGUMENTS for:
- Code quality issues
- Security vulnerabilities
- Performance problems

## Process

1. Use the code-reviewer agent
2. Generate actionable feedback
3. Prioritize findings by severity

## Output

Provide a structured report with:
- Summary of findings
- Detailed issues with line references
- Recommended fixes
```

## Hook Best Practices

### Performance

Hooks run synchronously - keep them fast:

```python
# Good: Early exit for unsupported files
SUPPORTED = {".py", ".js", ".ts"}

def main():
    file_path = sys.argv[1]
    if Path(file_path).suffix not in SUPPORTED:
        return  # Quick exit

    # Process file
```

### Error Handling

Handle errors gracefully:

```python
def main():
    try:
        file_path = sys.argv[1]
        process_file(file_path)
    except FileNotFoundError:
        print(f"File not found: {file_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
```

### Output

Provide useful feedback:

```python
# Good: Informative output
print(f"Linting {file_path}...")
print(f"Found {len(issues)} issues")
for issue in issues:
    print(f"  Line {issue.line}: {issue.message}")

# Bad: Silent or cryptic
print("done")
```

### Timeouts

Configure appropriate timeouts:

```json
{
  "matcher": "Write|Edit",
  "command": "python ~/.claude/hooks/lint.py $FILE",
  "timeout": 10000
}
```

### Idempotency

Hooks should be safe to run multiple times:

```python
# Good: Idempotent
def ensure_formatted(file_path):
    """Format file if not already formatted."""
    if is_formatted(file_path):
        return
    format_file(file_path)

# Bad: Not idempotent
def add_header(file_path):
    """Adds header every time - accumulates!"""
    with open(file_path, "r+") as f:
        content = f.read()
        f.seek(0)
        f.write(HEADER + content)
```

## Documentation Best Practices

### Frontmatter

Always include required fields:

```yaml
---
name: component-name
description: Clear, concise description
---
```

### README Files

Include README for complex components:

```text
my-skill/
├── SKILL.md
├── README.md          # Setup, usage, examples
└── references/
```

### Examples

Provide concrete examples:

```markdown
## Examples

### Basic Usage

```bash
/dev:review-code src/main.py
```

### With Options

```bash
/dev:review-code src/ --verbose
```

```

### Cross-References

Link related components:

```markdown
## See Also

- [code-review skill](../skills/code-review/SKILL.md)
- [security-audit skill](../skills/security-audit/SKILL.md)
- [test-engineer agent](../agents/testing/test-engineer.md)
```

## Organization Best Practices

### Directory Structure

Follow the established hierarchy:

```text
steve/
├── agents/
│   └── {domain}/
│       └── {agent-name}.md
├── skills/
│   └── {skill-name}/
│       └── SKILL.md
├── commands/
│   └── {category}/
│       └── {command-name}.md
└── hooks/
    └── {type}/
        ├── {hook-name}.py
        └── {hook-name}.md
```

### Naming Conventions

| Component | Convention | Example |
|-----------|------------|---------|
| Agents | `kebab-case` | `code-reviewer.md` |
| Skills | `kebab-case` directory | `code-review/SKILL.md` |
| Commands | `kebab-case` | `review-code.md` |
| Hooks | `snake_case` | `lint_changed.py` |

### Domain Organization

Group by logical domain:

```text
agents/
├── code-quality/      # Review, linting
├── testing/           # Test automation
├── database/          # DB operations
├── devops/            # Infrastructure
├── documentation/     # Writing
└── research/          # Research tasks
```

## Quality Checklist

### Before Publishing

- [ ] Frontmatter is valid YAML
- [ ] Name is unique and descriptive
- [ ] Description enables accurate selection
- [ ] Tools are restricted appropriately
- [ ] Skills are referenced (not duplicated)
- [ ] Instructions are clear and actionable
- [ ] Examples demonstrate usage
- [ ] No secrets in content
- [ ] File is in correct location

### For Agents

- [ ] Model is appropriate for task complexity
- [ ] Tool access is minimal necessary
- [ ] Skill references are focused
- [ ] Description has relevant keywords

### For Skills

- [ ] SKILL.md exists in skill directory
- [ ] Content is reusable across agents
- [ ] Detailed content is in references/
- [ ] Methodology is step-by-step

### For Commands

- [ ] Name reflects the action
- [ ] Category grouping is logical
- [ ] Arguments are documented
- [ ] Process is specified

### For Hooks

- [ ] Performance is acceptable
- [ ] Errors are handled gracefully
- [ ] Output is informative
- [ ] Hook is idempotent

## Anti-Patterns

### Avoid

1. **Overly broad agents**
   - Don't create "do everything" agents
   - Split into focused, composable agents

2. **Duplicated knowledge**
   - Don't copy instructions across agents
   - Extract shared knowledge into skills

3. **Excessive tool access**
   - Don't grant `All tools` without reason
   - Restrict to necessary tools

4. **Vague descriptions**
   - Don't use generic descriptions
   - Include specific keywords and capabilities

5. **Monolithic skills**
   - Don't put everything in SKILL.md
   - Use references/ for detailed content

6. **Slow hooks**
   - Don't do heavy processing in hooks
   - Filter early, timeout appropriately

7. **Silent failures**
   - Don't suppress errors silently
   - Provide meaningful feedback

## See Also

- [Development](DEVELOPMENT.md) - Creating components
- [Architecture](ARCHITECTURE.md) - Design decisions
- [Contributing](CONTRIBUTING.md) - Contribution workflow
- [Component Relationships](COMPONENT_RELATIONSHIPS.md) - How components work together
