# Product Guidelines

## Tone and Voice
- **Professional and Technical:** Use precise, clear, and objective language. Avoid colloquialisms or fluff.
- **Concise and Direct:** Prioritize brevity. Focus on providing the necessary information as quickly as possible.

## Documentation Standards
- **Standardized Header Hierarchy:** Always use `#` for the main title and `##` for primary sections.
- **Markdown Consistency:** Ensure all documentation follows the professional and technical tone established for the project.

## Component Organization and Naming
- **Kebab-Case Enforcement:** All file names, component names, and IDs must use `kebab-case` (e.g., `my-new-agent.md`).
- **Domain-First Structure:** Components must be organized within their respective domain-specific directories (e.g., `steve/agents/development/`) to maintain a clean and discoverable repository.
- **Mandatory YAML Frontmatter:** Every component file (`.md`) must start with a valid YAML frontmatter block containing metadata like `name` and `description` to support automated indexing.

## Quality and Security
- **Code Stability:** New Python utilities and scripts must be accompanied by unit tests, aiming for a minimum of 80% coverage.
- **Security First:** All contributions must be scanned and pass the `detect_secrets` check to prevent the accidental commitment of credentials.
- **Strict Linting and Typing:** Code must adhere to the `ruff` and `mypy` configurations specified in the project's `pyproject.toml`.
