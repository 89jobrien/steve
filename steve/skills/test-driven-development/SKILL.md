---
status: DEPRECATED
deprecated_in: "2026-01-20"
name: test-driven-development
description: Apply TDD methodology with Red-Green-Refactor cycle. Use when implementing features, fixing bugs, or when user says "TDD", "test first", "test-driven". Ensures code quality through disciplined test-first development.
user-invocable: true
---


# Test-Driven Development (TDD)

## Core Principle

**Write tests before code. Always.** TDD is not about testing—it's about design through small, disciplined steps.

## When to Use This Skill

- User explicitly requests TDD ("use TDD", "test first", "test-driven")
- Implementing new features
- Fixing bugs (write failing test that reproduces bug first)
- Refactoring existing code (ensure tests exist first)

## The Three Laws (Never Violate)

1. Write **NO production code** without a failing test first
2. Write **only enough test** to demonstrate one failure
3. Write **only enough code** to pass that test

## Protocol

### Phase 1: RED - Write Failing Test

```
□ Write ONE test that defines desired behavior
□ Run test - verify it FAILS
□ Verify it fails for the RIGHT reason (not syntax error)
□ DO NOT write implementation yet

Evidence required: Show test output with failure message
```

### Phase 2: GREEN - Minimal Implementation

```
□ Write MINIMAL code to make test pass
□ Resist urge to add extra features
□ Run test - verify it PASSES
□ If test still fails, fix implementation (not test)

Evidence required: Show test output with pass
```

### Phase 3: REFACTOR - Clean Code

```
□ Remove code duplication (DRY)
□ Improve naming for clarity
□ Extract complex logic into functions
□ Run ALL tests - must stay green throughout
□ Check test coverage on changed lines

Evidence required: Show all tests still passing after refactor
```

### Cycle Complete → Repeat

After REFACTOR, start new RED phase for next behavior.

## Common Mistakes to Avoid

### Writing Multiple Tests at Once

```
❌ WRONG: Test entire feature in one go
✅ CORRECT: One test at a time. Pass it. Refactor. Next test.
```

### Skipping Refactor Phase

```
❌ WRONG: "Tests pass, ship it!"
✅ CORRECT: ALWAYS refactor. Clean code is the goal.
```

### Implementation Before Test

```
❌ WRONG: Write code, then add tests after
✅ CORRECT: If code exists before test, delete it and start with test
```

### Over-Engineering in GREEN

```
❌ WRONG: Add error handling, edge cases, optimizations
✅ CORRECT: Simplest thing that makes THIS test pass
```

## Workflow Example

```
Task: "Add user login feature"

RED Phase:
1. Write test: test_login_with_valid_credentials()
2. Run: pytest -v → FAILED (no login function exists)
3. Evidence: "FAILED - AttributeError: 'User' has no 'login'"

GREEN Phase:
4. Write minimal login() method
5. Run: pytest -v → PASSED
6. Evidence: "1 passed in 0.03s"

REFACTOR Phase:
7. Extract password hashing to separate function
8. Improve variable names
9. Run: pytest -v → PASSED (still)
10. Evidence: "1 passed in 0.02s"

Next cycle: test_login_with_invalid_credentials()
```

## Test Patterns

### Arrange-Act-Assert (AAA)

```python
def test_user_can_login():
    # Arrange
    user = User(email="test@example.com", password="secret")

    # Act
    result = user.login("secret")

    # Assert
    assert result.success is True
    assert result.token is not None
```

### Given-When-Then (BDD style)

```python
def test_login_with_wrong_password():
    # Given a registered user
    user = create_user(password="correct")

    # When they attempt login with wrong password
    result = user.login("wrong")

    # Then login should fail
    assert result.success is False
    assert "Invalid password" in result.error
```

## Anti-Patterns

```
❌ Write test that passes immediately (test proves nothing)
❌ Test implementation details instead of behavior
❌ Skip tests for "simple" code
❌ Write tests after implementation "because we're in a hurry"
❌ Large tests that verify many things at once

✅ Each test verifies ONE behavior
✅ Test names describe the behavior being tested
✅ Tests are independent (no shared state)
✅ Tests run fast (mock external dependencies)
```

## Integration with Other Skills

- **pre-task-checkpoint**: Run checkpoint before each RED phase to frame what behavior to test
- **evidence-reasoning**: Show actual test output, never claim "tests pass" without evidence
- **completion-discipline**: Each GREEN phase requires evidence of passing test
- **verification-calibration**: Match test rigor to feature stakes (🔴 critical features need comprehensive tests)
- **clarifying-questions**: Clarify expected behavior BEFORE writing test

## Self-Check

```
Before moving from RED to GREEN:
[ ] Test actually fails?
[ ] Fails for the right reason?
[ ] Test name describes behavior?

Before moving from GREEN to REFACTOR:
[ ] Test passes?
[ ] Implementation is minimal?
[ ] No premature optimization?

Before starting next cycle:
[ ] Code is clean?
[ ] All tests still pass?
[ ] Ready for next behavior?
```

## Meta-Principle

```
TDD is a DESIGN technique, not a testing technique.

The cycle never changes: RED → GREEN → REFACTOR → Repeat

Writing tests first forces you to think about:
- What behavior do I need?
- How will I know it works?
- What's the simplest implementation?

This produces better-designed, more maintainable code.
```
