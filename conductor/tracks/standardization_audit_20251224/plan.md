# Plan: Standardization Audit and Component Stabilization

## Phase 1: Naming Convention and Metadata Audit

- [x] Task: Audit file names for `kebab-case` violations in `steve/agents`, `steve/skills`, and `steve/commands`. (audit)
- [x] Task: Rename identified files to compliant `kebab-case` names. (deb59d7)
- [x] Task: Fix Metadata for Agents (Merge blocks, ensure name/description). (manual)
- [~] Task: Fix Metadata for Commands (Ensure name/description from content).
- [ ] Task: Fix Metadata for Hooks (Ensure name/description).
- [ ] Task: Fix Metadata for Skills (Ensure name/description in SKILL.md).
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
