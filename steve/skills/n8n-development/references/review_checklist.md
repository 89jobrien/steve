---
status: DEPRECATED
deprecated_in: "2026-01-20"
---
# Code Review Checklist

## Pre-Submission Checklist

### Testing
- [ ] All tests pass: `uv run pytest`
- [ ] Test coverage meets target (80%+): `uv run pytest --cov=nathan --cov-report=term-missing`
- [ ] New functionality has corresponding tests
- [ ] Integration tests for workflow changes
- [ ] Edge cases and error conditions tested
- [ ] Mocked external dependencies appropriately

### Code Quality
- [ ] Linting passes: `uvx ruff check .`
- [ ] Code formatted: `uvx ruff format .`
- [ ] No commented-out code or debug statements
- [ ] Clear variable and function names
- [ ] DRY principle followed (no duplicated code)
- [ ] Single responsibility principle maintained

### Documentation
- [ ] Docstrings for all new functions/classes
- [ ] Type hints for all parameters and returns
- [ ] Complex logic has inline comments
- [ ] README updated if adding new features
- [ ] API documentation updated if changing interfaces
- [ ] Usage examples provided for new functionality

### Error Handling
- [ ] All HTTP calls wrapped in try/except
- [ ] Timeout handling implemented
- [ ] Clear, actionable error messages
- [ ] Proper logging at appropriate levels
- [ ] Graceful degradation where applicable
- [ ] No silent failures

### Async Patterns
- [ ] Using httpx for HTTP calls (not requests)
- [ ] Async context managers used properly
- [ ] No blocking I/O in async functions
- [ ] Proper use of asyncio.gather() for parallel operations
- [ ] Timeouts configured for all external calls

### n8n Specific
- [ ] Webhook contract documented
- [ ] Request/response schemas defined with Pydantic
- [ ] Workflow JSON exported to correct directory
- [ ] Registry entry added to workflow_registry.yaml
- [ ] Shared secret authentication implemented
- [ ] Consistent error response format

### Security
- [ ] No hardcoded secrets or credentials
- [ ] Environment variables used for configuration
- [ ] Input validation at all boundaries
- [ ] SQL injection prevention (if applicable)
- [ ] XSS prevention (if applicable)
- [ ] Secrets not logged

### Performance
- [ ] No unnecessary database queries
- [ ] Efficient data structures used
- [ ] Pagination implemented for large datasets
- [ ] Caching considered where appropriate
- [ ] Resource cleanup (close connections, files)

## Commit Message Review

### Format
- [ ] Follows conventional commits format
- [ ] Subject line under 50 characters
- [ ] Imperative mood in subject line
- [ ] Body explains why, not what
- [ ] References related issues/tickets

### Conventional Commit Types
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation only changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code change that neither fixes a bug nor adds a feature
- `perf:` Performance improvement
- `test:` Adding or updating tests
- `chore:` Changes to build process or auxiliary tools
- `ci:` CI/CD configuration changes

## Pull Request Review

### PR Description
- [ ] Clear title describing the change
- [ ] Summary of what changed and why
- [ ] Links to related issues/tickets
- [ ] Breaking changes noted
- [ ] Migration steps provided if needed

### PR Content
- [ ] Single logical change per PR
- [ ] No unrelated changes mixed in
- [ ] Appropriate size (prefer smaller PRs)
- [ ] Base branch is correct
- [ ] No merge conflicts

## Workflow Testing Checklist

### Unit Tests
- [ ] Test each workflow parameter
- [ ] Test required vs optional parameters
- [ ] Test parameter type validation
- [ ] Test error responses
- [ ] Test timeout scenarios

### Integration Tests
- [ ] Test against running n8n instance
- [ ] Test webhook authentication
- [ ] Test complete workflow execution
- [ ] Test error propagation
- [ ] Test concurrent executions

### Template Tests
- [ ] Variable substitution works correctly
- [ ] Invalid variables caught
- [ ] Template syntax validation
- [ ] Output format validation
- [ ] Edge cases (empty values, special characters)

## Common Issues to Check

### Python Specific
- [ ] No mutable default arguments
- [ ] Context managers used for resources
- [ ] Proper exception hierarchy
- [ ] No bare except clauses
- [ ] f-strings used for formatting (Python 3.6+)

### Async Specific
- [ ] No synchronous I/O in async functions
- [ ] Proper cancellation handling
- [ ] No fire-and-forget tasks
- [ ] Proper exception propagation in gathered tasks
- [ ] Resource cleanup in finally blocks

### n8n Workflow Specific
- [ ] Idempotent operations where possible
- [ ] Proper retry logic for transient failures
- [ ] Rate limiting considered
- [ ] Webhook URL validation
- [ ] Response size limits handled

## Post-Review Actions

- [ ] Address all review comments
- [ ] Re-run tests after changes
- [ ] Update documentation if changes made
- [ ] Squash commits if requested
- [ ] Verify CI/CD passes
- [ ] Request re-review if significant changes made