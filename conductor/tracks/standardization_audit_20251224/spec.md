# Specification: Standardization Audit and Component Stabilization

## Context

The project `steve` has a substantial number of components (377+) including agents, commands, skills, hooks, and templates. To ensure long-term maintainability and automation readiness, all components must adhere to strict naming conventions (`kebab-case`), file structure (YAML frontmatter), and code quality standards (`ruff`, `mypy`).

## Goals

1. **Audit Naming Conventions:** Identify and rename any component files that do not follow the `kebab-case` convention.
2. **Verify Metadata:** Ensure every markdown component file has valid YAML frontmatter with at least `name` and `description` fields.
3. **Code Quality Check:** Run `ruff` and `mypy` across the codebase and fix identifying issues, prioritizing the `scripts/` and `steve/helpers/` directories.
4. **Update Index:** Rebuild the component index to reflect any changes.

## Out of Scope

- Major refactoring of agent logic or behavior.
- Adding new features or components.

## Success Criteria

- All component file names are in `kebab-case`.
- All `.md` component files contain valid YAML frontmatter.
- `ruff` and `mypy` report zero errors for `scripts/` and `steve/helpers/`.
- `uv run scripts/build_index.py` executes successfully without warnings related to malformed components.
