# Plan: Standardization Audit and Component Stabilization

## Phase 1: Naming Convention and Metadata Audit
- [ ] Task: Audit file names for `kebab-case` violations in `steve/agents`, `steve/skills`, and `steve/commands`.
- [ ] Task: Rename identified files to compliant `kebab-case` names.
- [ ] Task: Audit all `.md` component files for valid YAML frontmatter.
- [ ] Task: Add or fix missing frontmatter in identified files.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Naming Convention and Metadata Audit' (Protocol in workflow.md)

## Phase 2: Code Quality Stabilization
- [ ] Task: Run `ruff check scripts/ steve/helpers/` and identify violations.
- [ ] Task: Fix linting errors in `scripts/` and `steve/helpers/`.
- [ ] Task: Run `mypy scripts/ steve/helpers/` and identify type errors.
- [ ] Task: Fix type errors in `scripts/` and `steve/helpers/`.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Code Quality Stabilization' (Protocol in workflow.md)

## Phase 3: Final Verification
- [ ] Task: Rebuild the component index using `uv run scripts/build_index.py`.
- [ ] Task: Run the full test suite `uv run pytest` to ensure no regressions.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Final Verification' (Protocol in workflow.md)
