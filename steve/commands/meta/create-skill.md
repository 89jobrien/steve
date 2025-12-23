---
description: Create a new Claude Skill following best practices. Guides through the
  complete skill creation process from concept to packaged distribution.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
argument-hint: '[skill-name] [description]'
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: commands
---

# Create Skill

Create a new Claude Skill or update an existing one following the skill-creator methodology: **$ARGUMENTS**

## Instructions

When this command is invoked, use the skill-creator-expert agent to guide the user through creating a skill.

### 1. Determine Skill Details

**If arguments provided:**

- Parse skill name and description from `$ARGUMENTS`
- Use these as starting points

**If no arguments:**

- Ask the user what skill they want to create
- Gather information about the skill's purpose

### 2. Follow Skill Creation Process

Use the skill-creator-expert agent which follows the skill-creator skill methodology:

1. **Understand with Examples**: Ask for concrete usage examples
2. **Plan Resources**: Identify scripts, references, and assets needed
3. **Initialize**: Run `init_skill.py` script to create structure
4. **Edit**: Create reusable resources and update SKILL.md
5. **Package**: Validate and package when ready
6. **Iterate**: Improve based on feedback

### 3. Skill Location

Determine where to create the skill:

- **Project skills**: `skills/` directory in current project
- **User skills**: `~/.claude/skills/` directory

If not specified, ask the user which location they prefer.

### 4. Initialize Skill

Run the initialization script:

```bash
python ~/.claude/skills/skill-creator/scripts/init_skill.py <skill-name> --path <output-directory>
```

This creates:

- Skill directory with proper structure
- SKILL.md template with frontmatter
- Example directories (scripts/, references/, assets/)

### 5. Guide Content Creation

Help the user:

- Create reusable resources (scripts, references, assets)
- Write SKILL.md with proper structure
- Follow imperative/infinitive writing style
- Include "When to Use" section
- Reference all bundled resources

### 6. Validate and Package

When the skill is complete:

```bash
python ~/.claude/skills/skill-creator/scripts/package_skill.py <skill-path>
```

This validates the skill and creates a distributable zip file.

## Skill Structure

Skills should include:

```
skill-name/
├── SKILL.md (required)
│   ├── Frontmatter (name, description)
│   └── Instructions (when to use, how to use)
└── [Optional Resources]
    ├── scripts/          # Executable helper scripts (Python, Bash, etc.)
    ├── references/        # Documentation references (detailed patterns, checklists, guides)
    └── assets/           # Templates, images, fonts, etc.
```

### Reference Files

Reference files (`references/`) store detailed documentation that would make SKILL.md too long. Use them for:

- **Detailed Patterns**: Common patterns and examples (e.g., `references/common_patterns.md`)
- **Checklists**: Comprehensive checklists (e.g., `references/review_checklist.md`)
- **Framework Guides**: Framework-specific documentation (e.g., `references/framework_patterns.md`)
- **API References**: API documentation and examples
- **Schemas**: Database schemas, data structures

**How to Reference:**
In SKILL.md, tell Claude when to load reference files:

- "For detailed patterns, load `references/common_patterns.md`"
- "When analyzing X, load `references/framework_patterns.md` and refer to section Y"

## Examples

### Create New Skill

```
/create-skill "api-testing" "Skill for testing REST APIs with automated test generation"
```

### Update Existing Skill

```
/create-skill "debugging" # Update existing skill
```

## Best Practices

- **Be Specific**: Clear descriptions help Claude know when to use the skill
- **Progressive Disclosure**: Keep SKILL.md lean, use references for details
- **Test Examples**: Ensure all examples work as documented
- **Iterate**: Improve based on real usage feedback

Follow the skill-creator skill methodology for creating effective, well-structured skills.
