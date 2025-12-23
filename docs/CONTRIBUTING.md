# Contributing Guide

Guidelines for contributing to the Steve component library.

## Getting Started

### Prerequisites

- Claude Code 1.0+
- Python 3.12+
- Git
- GitHub account (for gist publishing)

### Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/username/steve.git
   cd steve
   ```

2. **Install dependencies:**

   ```bash
   uv sync
   ```

3. **Run initial checks:**

   ```bash
   # Verify component index
   uv run scripts/build_index.py

   # Check for secrets
   uv run scripts/detect_secrets.py --scan
   ```

## Contribution Types

### Adding Components

The most common contribution is adding new components:

| Component | Location | Template |
|-----------|----------|----------|
| Agent | `agents/{domain}/` | `templates/AGENT_PLAYBOOK.template.md` |
| Skill | `skills/{name}/` | `templates/AGENT_SKILL.template.md` |
| Command | `commands/{category}/` | `templates/SLASH_COMMAND.template.md` |
| Hook | `hooks/{type}/` | `templates/CLAUDE_HOOK.template.md` |

### Improving Existing Components

- Fix bugs in component behavior
- Improve descriptions for better agent selection
- Add missing skill references
- Optimize hook performance
- Update outdated content

### Documentation

- Fix typos and errors
- Improve clarity
- Add examples
- Update for new features

## Workflow

### 1. Create a Branch

```bash
git checkout -b feature/new-agent-name
# or
git checkout -b fix/hook-timeout-issue
```

**Branch naming:**

- `feature/` - New components or capabilities
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `refactor/` - Code restructuring

### 2. Make Changes

Follow the appropriate guide:

- [Development Guide](DEVELOPMENT.md) - Creating components
- [Best Practices](BEST_PRACTICES.md) - Quality standards

### 3. Test Your Changes

**For agents:**

```bash
# Copy to Claude config
cp agents/domain/my-agent.md ~/.claude/agents/

# Test invocation
# In Claude Code: "Use the my-agent agent to..."
```

**For commands:**

```bash
# Copy to Claude config
cp commands/category/my-command.md ~/.claude/commands/category/

# Test invocation
# In Claude Code: /category:my-command
```

**For hooks:**

```bash
# Test manually
python hooks/type/my_hook.py /path/to/test/file

# Copy and configure in settings.json
```

**For skills:**

```bash
# Copy to Claude config
cp -r skills/my-skill/ ~/.claude/skills/

# Test via agent that references the skill
```

### 4. Run Quality Checks

```bash
# Rebuild index
uv run scripts/build_index.py

# Check for secrets
uv run scripts/detect_secrets.py --scan

# Validate YAML frontmatter (manual check)
```

### 5. Commit Changes

**Commit message format:**

```text
type(scope): short description

Longer description if needed.

- Detail 1
- Detail 2
```

**Types:**

- `feat` - New component or feature
- `fix` - Bug fix
- `docs` - Documentation
- `refactor` - Code restructuring
- `style` - Formatting changes
- `test` - Adding tests

**Examples:**

```bash
git commit -m "feat(agent): add security-scanner agent for vulnerability detection"
git commit -m "fix(hook): resolve timeout issue in lint_changed hook"
git commit -m "docs: update installation guide for Windows users"
```

### 6. Push and Create PR

```bash
git push origin feature/new-agent-name
```

Create a pull request with:

- Clear title describing the change
- Description of what and why
- Testing performed
- Related issues (if any)

## Component Guidelines

### Agent Requirements

**Required:**

```yaml
---
name: agent-name           # Unique, kebab-case
description: What it does  # Clear, specific
---
```

**Recommended:**

```yaml
---
name: agent-name
description: Action-oriented description with keywords
tools: Read, Write, Edit   # Minimum necessary
model: sonnet              # Appropriate for complexity
skills: skill1, skill2     # Referenced, not duplicated
---
```

**Content structure:**

```markdown
## Purpose

Why this agent exists and when to use it.

## Instructions

Step-by-step process the agent follows.

## Best Practices

Guidelines for effective use.
```

### Skill Requirements

**Directory structure:**

```text
skill-name/
├── SKILL.md           # Required
├── references/        # Optional: detailed docs
├── scripts/           # Optional: helper code
└── assets/            # Optional: outputs
```

**SKILL.md structure:**

```markdown
---
name: skill-name
description: What expertise this provides
---

## When to Use

Clear criteria for when this skill applies.

## Methodology

Step-by-step framework or process.

## Checklists

- [ ] Verification items
- [ ] Quality checks

## Examples

Concrete application examples.
```

### Command Requirements

**Frontmatter:**

```yaml
---
description: What this command does
argument-hint: [arg1] | [--option]
allowed-tools: Read, Write, Edit
---
```

**Content:**

```markdown
## Task

What the command accomplishes.

## Process

How to execute the task.

## Output

Expected results.
```

### Hook Requirements

**Python file:**

```python
#!/usr/bin/env python3
"""Hook description."""

import sys
from pathlib import Path

def main():
    # Implementation
    pass

if __name__ == "__main__":
    main()
```

**Documentation file:**

```markdown
---
name: hook_name
description: What this hook does
trigger: PostToolUse
matcher: Write|Edit
---

## Purpose

Why this hook exists.

## Configuration

How to register in settings.json.

## Behavior

What happens when triggered.
```

## Code Style

### Python

- Follow PEP 8
- Use type hints
- Add docstrings
- Handle errors gracefully

```python
def process_file(file_path: str) -> bool:
    """Process a file and return success status.

    Args:
        file_path: Path to the file to process.

    Returns:
        True if processing succeeded, False otherwise.
    """
    try:
        # Implementation
        return True
    except FileNotFoundError:
        print(f"File not found: {file_path}", file=sys.stderr)
        return False
```

### Markdown

- Use ATX-style headers (`#`)
- Use fenced code blocks with language
- Keep lines under 120 characters
- No trailing whitespace

### YAML Frontmatter

- Use lowercase keys
- Use kebab-case for names
- Comma-separated lists for tools/skills

```yaml
---
name: component-name
description: Clear description
tools: Read, Write, Edit
skills: skill1, skill2
---
```

## Review Process

### What Reviewers Check

1. **Functionality:**
   - Component works as described
   - No breaking changes to existing components

2. **Quality:**
   - Follows naming conventions
   - Includes required fields
   - Description enables accurate selection

3. **Security:**
   - No secrets in content
   - Appropriate tool restrictions
   - Safe hook implementations

4. **Documentation:**
   - Clear purpose and usage
   - Examples provided
   - Cross-references where appropriate

### Review Checklist

- [ ] Frontmatter is valid YAML
- [ ] Name is unique and follows conventions
- [ ] Description is clear and specific
- [ ] Tools are restricted appropriately
- [ ] Skills are referenced (not duplicated)
- [ ] No secrets in content
- [ ] Index rebuilds successfully
- [ ] Component works when tested

## Publishing

After your PR is merged, components can be published to GitHub Gists for distribution.

See [Publishing Guide](PUBLISHING.md) for details.

## Getting Help

### Questions

- Check [FAQ](FAQ.md) for common questions
- Review existing components for examples
- Open an issue for discussion

### Issues

When reporting issues, include:

- Component name and type
- Steps to reproduce
- Expected vs actual behavior
- Error messages (if any)
- Claude Code version

### Feature Requests

When requesting features:

- Describe the use case
- Explain why existing components don't suffice
- Propose a solution if you have one

## Recognition

Contributors are recognized in:

- Git commit history
- PR acknowledgments
- Component metadata (optional `author` field)

## Code of Conduct

- Be respectful and constructive
- Focus on the contribution, not the contributor
- Help others learn and improve
- Keep discussions technical and on-topic

## See Also

- [Development Guide](DEVELOPMENT.md) - Creating components
- [Best Practices](BEST_PRACTICES.md) - Quality standards
- [Publishing Guide](PUBLISHING.md) - Distribution workflow
- [Architecture](ARCHITECTURE.md) - System design
