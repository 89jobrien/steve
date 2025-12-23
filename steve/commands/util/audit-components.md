---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: commands
---

---

allowed-tools: Read, Glob, Grep, Bash(wc:*), Bash(head:*)
argument-hint: [agents] | [skills] | [commands] | [hooks] | [all] | [--fix]
description: Audit Claude agents, skills, commands, and hooks against templates for quality and completeness
---

# Claude Components Audit

Audit workspace components against templates: $ARGUMENTS

## Current Component Inventory

- Agents: !`find ~/.claude/agents -name "*.md" -type f 2>/dev/null | wc -l | tr -d ' '` files
- Skills: !`find ~/.claude/skills -name "SKILL.md" -type f 2>/dev/null | wc -l | tr -d ' '` skills
- Commands: !`find ~/.claude/commands -name "*.md" -type f 2>/dev/null | wc -l | tr -d ' '` commands
- Templates: !`ls ~/.claude/templates/*.template.md 2>/dev/null | wc -l | tr -d ' '` templates

## Task

Perform comprehensive audit of Claude Code components against established templates and best practices.

## Audit Scope

Based on `$ARGUMENTS`:

- `agents` - Audit only agents
- `skills` - Audit only skills
- `commands` - Audit only commands
- `hooks` - Audit hooks configuration
- `all` or empty - Audit everything
- `--fix` - Attempt automatic fixes for common issues

## Audit Workflow

### 1. Load Templates

Read templates from `~/.claude/templates/`:

- `SUBAGENT.template.md` - Agent structure reference
- `AGENT_SKILL.template.md` - Skill structure reference
- `SLASH_COMMAND.template.md` - Command structure reference
- `CLAUDE_HOOK.template.md` - Hook configuration reference

### 2. Agent Audit

For each file in `~/.claude/agents/**/*.md`:

**Frontmatter Checks:**

- [ ] Has `name` field (required)
- [ ] Has `description` field (required)
- [ ] Has `tools` field (required)
- [ ] `model` is valid: haiku, sonnet, or opus
- [ ] `color` is valid if present

**Description Quality:**

- [ ] Starts with action phrase ("Use PROACTIVELY...", "Specialist for...")
- [ ] Explains WHEN to use, not just WHAT it does
- [ ] Length between 50-300 characters

**Body Structure:**

- [ ] Has Purpose/Role section
- [ ] Has Instructions with numbered steps
- [ ] Has Best Practices section
- [ ] Has Output Format section
- [ ] No placeholder text ({{...}})

**Tools Assessment:**

- [ ] Tools list is minimal (principle of least privilege)
- [ ] No unused tools declared
- [ ] MCP tools properly namespaced

### 3. Skill Audit

For each directory in `~/.claude/skills/*/`:

**Structure Checks:**

- [ ] Has `SKILL.md` file
- [ ] SKILL.md has valid frontmatter
- [ ] References exist if mentioned in SKILL.md
- [ ] Scripts are executable if present

**Frontmatter Checks:**

- [ ] Has `name` field matching directory name
- [ ] Has `description` field
- [ ] Description uses third-person

**Content Quality:**

- [ ] Has "When to Use" section
- [ ] Has workflow or process section
- [ ] Has examples section
- [ ] SKILL.md under 5000 words (use references for more)
- [ ] No placeholder text

**Progressive Disclosure:**

- [ ] Core workflow in SKILL.md
- [ ] Detailed content in references/
- [ ] No duplication between SKILL.md and references

### 4. Command Audit

For each file in `~/.claude/commands/**/*.md`:

**Frontmatter Checks:**

- [ ] Has `description` field
- [ ] `allowed-tools` is valid if present
- [ ] `argument-hint` is helpful if present

**Body Structure:**

- [ ] Has clear title
- [ ] Has task description
- [ ] Has workflow steps
- [ ] Uses `$ARGUMENTS` if arguments expected
- [ ] Dynamic context uses `!` syntax correctly

**Quality Checks:**

- [ ] Description under 100 characters
- [ ] Workflow is actionable
- [ ] No placeholder text

### 5. Hooks Audit

Check `~/.claude/settings.json`:

**Configuration Checks:**

- [ ] Valid JSON structure
- [ ] Hooks use valid event types
- [ ] Matchers are specific
- [ ] Commands are shell-valid

**Best Practices:**

- [ ] Hooks are fast (<1s execution)
- [ ] Error handling present
- [ ] No blocking operations

## Output Format

```
CLAUDE COMPONENTS AUDIT REPORT
==============================
Generated: {{timestamp}}

SUMMARY
-------
| Component | Total | Pass | Warn | Fail |
|-----------|-------|------|------|------|
| Agents    | {{n}} | {{p}} | {{w}} | {{f}} |
| Skills    | {{n}} | {{p}} | {{w}} | {{f}} |
| Commands  | {{n}} | {{p}} | {{w}} | {{f}} |
| Hooks     | {{n}} | {{p}} | {{w}} | {{f}} |

AGENTS ({{status}})
-------------------
[PASS] agent-name: All checks passed
[WARN] agent-name: Missing optional field 'color'
[FAIL] agent-name: Missing required field 'description'

SKILLS ({{status}})
-------------------
[PASS] skill-name: All checks passed
[WARN] skill-name: SKILL.md exceeds 5000 words
[FAIL] skill-name: Missing SKILL.md file

COMMANDS ({{status}})
---------------------
[PASS] command-name: All checks passed
[WARN] command-name: Description too long (>100 chars)
[FAIL] command-name: Contains placeholder text

HOOKS ({{status}})
------------------
[PASS] PreToolUse hooks configured correctly
[WARN] No hooks configured
[FAIL] Invalid JSON in settings.json

RECOMMENDATIONS
---------------
1. {{recommendation_1}}
2. {{recommendation_2}}
3. {{recommendation_3}}

QUICK FIXES
-----------
Run with --fix to attempt automatic corrections:
- Add missing optional fields with defaults
- Fix common frontmatter formatting issues
- Remove placeholder text markers
```

## Severity Levels

| Level | Meaning | Action |
|-------|---------|--------|
| PASS | Meets all requirements | None needed |
| WARN | Works but improvable | Review when possible |
| FAIL | Missing requirements | Fix before using |

## Common Issues and Fixes

### Missing Description

```yaml
description: Use PROACTIVELY for {{domain}} tasks including {{task1}}, {{task2}}
```

### Placeholder Text

Search for `{{` and replace with actual content.

### Oversized SKILL.md

Move detailed content to `references/` subdirectory.

### Invalid Tool Names

Valid tools: Read, Write, Edit, MultiEdit, Glob, Grep, Bash, Task, TodoWrite, WebFetch, WebSearch, AskUserQuestion, LS, mcp__*

## Integration

After audit, consider:

1. Updating README.md with component inventory
2. Running `/meta:create-subagent` for new agents
3. Running `/meta:create-skill` for new skills
4. Reviewing templates for needed updates
