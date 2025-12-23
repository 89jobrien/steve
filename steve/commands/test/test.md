---
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
argument-hint: ' [file-path] | [component-name] | [description]'
description: Write tests using TDD methodology. Context-aware analysis of conversation
  history to determine what to test, or accepts a path/description. Framework-agnostic
  (detects pytest, Jest, Vitest, etc.).
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: commands
---

# Write Tests (TDD)

Write tests following strict Test-Driven Development methodology. Automatically detects test framework and follows appropriate conventions.

## Arguments

`$ARGUMENTS` - Optional path to file/function to test, or description of what to test.

Examples:

- `/test:test` - Context-aware, uses conversation history
- `/test:test src/auth.py` - Test specific file
- `/test:test the login function` - Test by description
- `/test:test --unit` - Focus on unit tests only
- `/test:test --integration` - Focus on integration tests

## Instructions

### 1. Detect Test Framework

Identify the testing framework in use:

**Python:**

- Check for `pytest` in dependencies
- Look for `pyproject.toml` with `[tool.pytest.ini_options]`
- Check for `pytest.ini` or `setup.cfg`

**JavaScript/TypeScript:**

- Check `package.json` for `jest`, `vitest`, `mocha`
- Look for `jest.config.*`, `vitest.config.*`
- Check test scripts in `package.json`

**Other:**

- Detect Go tests (`*_test.go`)
- Detect Rust tests (`#[cfg(test)]`)

### 2. Determine What to Test

**If arguments provided:**

- Parse `$ARGUMENTS` for file path or description
- Read the target file/function
- Check for existing tests

**If no arguments (context-aware mode):**

- Review the conversation history for:
  - Code that was just written or modified
  - Features being discussed
  - Bug fixes in progress
  - User requests for specific functionality
- Identify the most relevant code to test

**If unclear, ask clarifying questions:**

- "I see you're working on X. Should I write tests for [specific function/class]?"
- "What specific behavior would you like me to test?"
- "Should I focus on unit tests, integration tests, or both?"
- "Are there specific edge cases you're concerned about?"

### 3. Analyze the Code

Once target is identified:

- Read the source file(s)
- Identify public functions/methods to test
- Note dependencies that need mocking
- Identify edge cases and error conditions
- Check for existing tests to avoid duplication
- Review existing test patterns in the project

### 4. Follow TDD Workflow

**Step 1: RED - Write Failing Test**:

```text
I'll write a failing test first. Here's what I'm testing:
- Function: X
- Expected behavior: Y
- Edge case: Z
```

Write the test following framework conventions:

**Python (pytest):**

```python
def test_function_does_expected_thing():
    result = function(input)
    assert result == expected
```

**JavaScript/TypeScript (Jest/Vitest):**

```javascript
describe('function', () => {
  it('does expected thing', () => {
    const result = function(input);
    expect(result).toBe(expected);
  });
});
```

Run and show failure:

**Python:**

```bash
uv run pytest tests/test_file.py::test_function_does_expected_thing -v
```

**JavaScript/TypeScript:**

```bash
npm test -- tests/test_file.test.js
```

Show the failing output as evidence.

**Step 2: GREEN - Implement (if needed)**:

If the implementation doesn't exist or is incomplete:

- Write minimal code to make the test pass
- Run test and show passing output

If implementation already exists:

- Verify test passes
- If it fails, discuss with user whether test or implementation needs adjustment

**Step 3: REFACTOR**:

- Review test for clarity
- Check for duplication with other tests
- Consider parametrization for similar test cases
- Ensure proper fixture/setup usage
- Improve test names and organization

### 5. Test Categories to Consider

**Happy Path:**

- Normal inputs produce expected outputs
- Standard use cases work correctly

**Edge Cases:**

- Empty inputs (None, "", [], {})
- Boundary values (0, -1, MAX_INT)
- Single element collections
- Very large inputs
- Null/undefined handling

**Error Handling:**

- Invalid inputs raise appropriate exceptions
- Error messages are helpful
- Cleanup happens on failure

**Async (if applicable):**

- Concurrent operations
- Timeout handling
- Cancellation behavior

**Integration:**

- Component interactions
- API integration (with mocks)
- Service layer integration
- End-to-end workflows

### 6. Framework-Specific Patterns

**Python (pytest):**

- Use fixtures for setup: `@pytest.fixture`
- Parametrize similar tests: `@pytest.mark.parametrize`
- Test exceptions: `with pytest.raises(ValueError)`
- Async tests: `@pytest.mark.asyncio`
- Mock with: `pytest-mock` or `unittest.mock`

**JavaScript/TypeScript (Jest):**

- Use `describe` blocks for organization
- Mock modules: `jest.mock()`
- Mock functions: `jest.fn()`
- Test async: `async/await` or `.resolves/.rejects`
- Snapshot tests: `toMatchSnapshot()`

**JavaScript/TypeScript (Vitest):**

- Similar to Jest but use `vi` instead of `jest`
- Mock modules: `vi.mock()`
- Mock functions: `vi.fn()`
- Use `describe` and `it` blocks

### 7. Output Format

For each test written:

```text
## Test: test_function_name

**Testing:** [function/method name]
**Behavior:** [what the test verifies]
**Framework:** [pytest/jest/vitest]

**Test Code:**
[Show the test code]

**Result:** RED (failing) / GREEN (passing)

**Output:**
[Show test framework output]
```

### 8. Summary

After writing tests:

```text
Tests Written: N
- test_function_happy_path
- test_function_empty_input
- test_function_raises_on_invalid

Framework: [detected framework]
Coverage Impact: +X% (estimated)

Next Steps:
- [ ] Additional edge cases to consider
- [ ] Integration tests needed
- [ ] Mock dependencies for isolation
```

## Best Practices

- One assertion concept per test (can have multiple asserts for same concept)
- Descriptive test names that explain the behavior
- Use fixtures/setup for common test data
- Parametrize similar test cases
- Mock external dependencies
- Test behavior, not implementation details
- Follow AAA pattern (Arrange, Act, Assert)
- Keep tests isolated and independent
- Use appropriate test markers/tags for organization
