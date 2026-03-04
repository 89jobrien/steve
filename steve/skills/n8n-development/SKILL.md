---
status: DEPRECATED
deprecated_in: "2026-01-20"
name: n8n-development
description: n8n workflow development patterns, testing, validation, and best practices for building composable webhook workflows
user-invocable: true
---


# n8n Development Skill

This skill provides comprehensive guidance for developing, testing, and maintaining n8n webhook workflows integrated with Python services. It includes patterns for building composable workflows, template development, test-driven development practices, and complete development workflows.

## When to Use This Skill

Apply this skill when:

- Building new n8n webhook workflows
- Integrating n8n workflows with Python services
- Writing tests for workflow integrations
- Creating reusable workflow templates
- Debugging workflow execution issues
- Setting up development environments for n8n projects
- Following best practices for async patterns and error handling

## Core Development Principles

### Test-Driven Development

1. Start with a failing test to define expected behavior
2. Implement minimal code to make the test pass
3. Refactor while keeping tests green
4. Run tests with `uv run pytest`

### Workflow Development Process

1. Design the webhook contract (request/response schema)
2. Implement in n8n with error handling
3. Export JSON to `nathan/workflows/[category]/`
4. Add to registry (`workflow_registry.yaml`)
5. Write integration tests in `tests/workflows/[category]/`
6. Document with usage examples

### Template Development

1. Define variables using `${VAR_NAME}` syntax
2. Add validation via schema in template frontmatter
3. Test rendering using CLI
4. Document with usage examples in comments

## Essential Commands

```bash
# Core development
uv sync                                    # Install dependencies
uv run pytest                              # Run tests
uv run pytest --cov=nathan --cov-report=term-missing  # With coverage
uvx ruff check .                           # Lint
uvx ruff format .                          # Format

# n8n development
docker compose -f docker-compose.n8n.yml up -d  # Run n8n locally
uv run python -m nathan.scripts.n8n_workflow_registry --help  # Registry CLI
uv run python -m nathan.templating --help  # Template CLI
```

## Testing Guidelines

Test structure should mirror source in `tests/` directory with descriptive naming (`test_trigger_workflow_with_valid_parameters`). Use pytest fixtures for shared setup and mock external dependencies. Target 80%+ test coverage.

## Validation and Schemas

Use Pydantic models for API requests/responses and SQLModel for database models. Implement input validation at boundaries (API endpoints, CLI arguments) with clear, actionable error messages.

## Async Patterns

Use httpx for all HTTP calls with proper timeout handling. Always use try/except for HTTP calls and async with context managers for HTTP clients. Use `asyncio.gather()` for parallel operations.

## Reference Documents

Load these reference files when needed for specific tasks:

- **Common Patterns**: Load `references/common_patterns.md` for workflow registry, template rendering, and error handling code examples
- **Code Review**: Load `references/review_checklist.md` before submitting code for review
- **CLI Commands**: Load `references/cli_commands.md` for n8n command-line operations (export, import, execute workflows)
- **REST API**: Load `references/rest_api.md` for n8n REST API endpoints and Python client examples
- **Workflow JSON**: Load `references/workflow_json_structure.md` for understanding and building n8n workflow JSON files

## Commit Guidelines

Follow conventional commits format:
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `test:` for test additions/changes
- `refactor:` for code refactoring

Make atomic commits (one logical change per commit), test before committing, and include documentation updates with code changes.