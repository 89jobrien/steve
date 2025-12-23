# Skills

Reusable skills with optional bundled resources.

## Structure

Each skill lives in its own directory:

```
skill-name/
├── SKILL.md          # Main skill definition (required)
├── references/       # Documentation references (optional)
├── scripts/          # Executable code (optional)
└── assets/           # Output files/examples (optional)
```

## File Format

Skills use YAML frontmatter followed by markdown content:

```yaml
---
name: skill-name
description: Third-person description: "This skill should be used when..."
---
```

## Content Structure

Skills should include:

1. **When to Use** - Clear trigger conditions
2. **What This Skill Does** - Capabilities list
3. **Core Principles** - Domain frameworks (non-obvious knowledge)
4. **Workflow** - Step-by-step process
5. **Best Practices** - Do's
6. **Anti-Patterns** - Don'ts
7. **Examples** - Concrete usage scenarios

## Naming Conventions

- Use `kebab-case` for skill names (e.g., `code-context-finder`, `tdd-pytest`)
- Names should be descriptive and indicate the skill's purpose
- Keep names concise but clear

## Required Files

- **`SKILL.md`**: Main skill definition with YAML frontmatter

## Optional Files

- **`references/`**: Documentation, templates, or reference materials
- **`scripts/`**: Executable Python, shell, or other scripts
- **`assets/`**: Example outputs, templates, or generated files
- **`README.md`**: Additional documentation (if needed)

## Bundled Resources

Skills can include bundled resources:

- **Scripts**: Executable code that implements the skill
- **References**: Documentation, templates, or guides
- **Assets**: Example outputs or generated files

## Creating New Skills

1. Create a new directory with kebab-case name
2. Create `SKILL.md` with YAML frontmatter
3. Use the template from `steve/templates/AGENT_SKILL.template.md`
4. Add bundled resources as needed
5. Follow the content structure guidelines

## Examples

See existing skills for reference patterns:

- `code-context-finder/` - Skill with references
- `dead-code-removal/` - Skill with scripts
- `skill-creator/` - Complex skill with multiple resources
