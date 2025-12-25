# Migration Guide

This document covers version history, breaking changes, and migration procedures for Steve components.

## Version History

### v1.0.0 (Current)

Initial stable release of the Steve component library.

**Components:**

- 137 agents across 15 domains
- 57 skills with bundled resources
- 61 slash commands in 17 categories
- 44 hooks across 4 types
- 27 templates

**Features:**

- YAML frontmatter for component metadata
- Skill bundling with references, scripts, assets
- Command namespacing with categories
- Hook event system with matchers
- Gist-based distribution

## Deprecations

### Deprecated Skills

The following skills are deprecated and should be replaced:

| Deprecated    | Replacement     | Notes                                            |
| ------------- | --------------- | ------------------------------------------------ |
| `design-docs` | `documentation` | Merged into unified documentation skill          |
| `migrations`  | `documentation` | Migration guides now part of documentation skill |

**Migration:**

```yaml
# Before
skills: design-docs, migrations

# After
skills: documentation
```

### Deprecated Patterns

**Direct tool invocation in commands:**

```markdown
# Deprecated: Direct Bash in command

Run: `bash scripts/lint.sh $ARGUMENTS`

# Preferred: Invoke agent

Use the code-linter agent to lint $ARGUMENTS
```

**Inline skill content in agents:**

```yaml
# Deprecated: Duplicating instructions
---
name: code-reviewer
---
## Code Review Process
1. Check for bugs...
2. Check for security...
# Preferred: Reference skill
---
name: code-reviewer
skills: code-review
---
```

## Breaking Changes

### From Pre-1.0

If migrating from early development versions:

**1. Frontmatter Format**

```yaml
# Old format (unsupported)
name = "agent-name"
tools = ["Read", "Write"]
# New format
---
name: agent-name
tools: Read, Write
---
```

**2. Skill Directory Structure**

```text
# Old structure
skills/
└── skill-name.md

# New structure
skills/
└── skill-name/
    └── SKILL.md
```

**3. Command Namespacing**

```text
# Old: Flat structure
commands/
├── review-code.md
└── clean-branches.md

# New: Category-based
commands/
├── dev/
│   └── review-code.md
└── git/
    └── clean-branches.md
```

**4. Hook Registration**

```json
// Old format
{
  "hooks": {
    "post_write": "python lint.py"
  }
}

// New format
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

## Migration Procedures

### Migrating Agents

**1. Update Frontmatter**

Ensure all required fields are present:

```yaml
---
name: agent-name # Required
description: What it does # Required
tools: Read, Write # Recommended
model: sonnet # Optional, defaults to sonnet
skills: skill1, skill2 # Optional
---
```

**2. Extract Inline Knowledge**

Move duplicated instructions to skills:

```yaml
# Before: Inline instructions
---
name: my-agent
---
## Process
1. Step one
2. Step two
# After: Reference skill
---
name: my-agent
skills: my-methodology
---
## Purpose
Apply my-methodology to the task.
```

**3. Update Tool Specifications**

Use comma-separated string format:

```yaml
# Correct
tools: Read, Write, Edit, Grep, Glob

# Wrong (old array format)
tools:
  - Read
  - Write
```

### Migrating Skills

**1. Convert to Directory Structure**

```bash
# Old: Single file
mv skills/my-skill.md skills/my-skill/SKILL.md
```

**2. Split Large Skills**

Move detailed content to references:

```bash
mkdir skills/my-skill/references/

# Move sections to separate files
# Keep SKILL.md focused on methodology
```

**3. Update Frontmatter**

```yaml
---
name: my-skill
description: What expertise this provides
---
```

### Migrating Commands

**1. Move to Category Directories**

```bash
# Create category
mkdir -p commands/dev/

# Move command
mv commands/review-code.md commands/dev/review-code.md
```

**2. Update References**

Update any documentation or scripts referencing old paths.

**3. Add Frontmatter**

```yaml
---
description: What this command does
argument-hint: [arg1] | [arg2]
allowed-tools: Read, Write
---
```

### Migrating Hooks

**1. Convert to New Event Names**

| Old               | New                                   |
| ----------------- | ------------------------------------- |
| `pre_write`       | `PreToolUse` with `matcher: "Write"`  |
| `post_write`      | `PostToolUse` with `matcher: "Write"` |
| `session_init`    | `SessionStart`                        |
| `session_cleanup` | `SessionEnd`                          |

**2. Update settings.json**

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "command": "python ~/.claude/hooks/analyzers/lint.py $FILE",
        "timeout": 10000
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

**3. Update Hook Scripts**

Ensure scripts handle new environment variables:

```python
import os
import sys

# Get file from argument or environment
file_path = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("FILE")
tool_name = os.environ.get("TOOL", "unknown")
```

## Compatibility Matrix

### Claude Code Versions

| Steve Version | Claude Code Version | Notes              |
| ------------- | ------------------- | ------------------ |
| 1.0.x         | 1.0+                | Full compatibility |

### Python Requirements

| Steve Version | Python Version | Notes                |
| ------------- | -------------- | -------------------- |
| 1.0.x         | 3.12+          | Required for scripts |

### Dependencies

Scripts require these packages (in `pyproject.toml`):

```toml
[project]
dependencies = [
    "pyyaml>=6.0",
    "requests>=2.31",
    "detect-secrets>=1.4",
]
```

## Upgrade Checklist

When upgrading to a new Steve version:

### Pre-Upgrade

- [ ] Back up current `~/.claude/` configuration
- [ ] Note any custom modifications
- [ ] Review changelog for breaking changes

### During Upgrade

- [ ] Pull latest Steve repository
- [ ] Run migration scripts if provided
- [ ] Update component files as needed
- [ ] Update settings.json for hook changes

### Post-Upgrade

- [ ] Verify agents are selectable
- [ ] Test command invocations
- [ ] Verify hooks are triggering
- [ ] Check skill loading in agents

## Rollback Procedure

If issues occur after upgrading:

**1. Restore Backup**

```bash
# Restore from backup
cp -r ~/.claude.backup/* ~/.claude/
```

**2. Revert Repository**

```bash
cd steve
git checkout v0.x.x  # Previous version tag
```

**3. Re-copy Components**

```bash
cp steve/agents/my-agent.md ~/.claude/agents/
```

## Getting Help

### Migration Issues

If you encounter migration problems:

1. Check the [Troubleshooting](TROUBLESHOOTING.md) guide
2. Review the [FAQ](FAQ.md)
3. Search existing GitHub issues
4. Open a new issue with:
   - Previous version
   - Target version
   - Error messages
   - Component files (sanitized)

### Resources

- [Changelog](../CHANGELOG.md) - Detailed version history
- [Architecture](ARCHITECTURE.md) - System design
- [Best Practices](BEST_PRACTICES.md) - Current standards
