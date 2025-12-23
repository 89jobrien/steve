---
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
argument-hint: ' [--quick] | [--verbose] | [--fix]'
description: Generate or update TESTING_REPORT.local.md with comprehensive test audit,
  coverage analysis, and recommendations. Framework-agnostic (supports pytest, Jest,
  Vitest, etc.).
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: commands
---

# Generate Test Report

Create or update the `TESTING_REPORT.local.md` file with comprehensive test analysis. Automatically detects test framework and adapts reporting format.

## Instructions

### 1. Detect Test Framework

Identify the testing framework:

- Check for `pytest` (Python)
- Check for `jest` or `vitest` (JavaScript/TypeScript)
- Check for `go test` (Go)
- Check for `cargo test` (Rust)

### 2. Discover Test Files

Find all test files based on framework conventions:

**Python (pytest):**

```bash
find . -name "test_*.py" -o -name "*_test.py" | grep -v .venv | grep -v __pycache__
```

**JavaScript/TypeScript:**

```bash
find . -name "*.test.*" -o -name "*.spec.*" | grep -v node_modules
```

**Go:**

```bash
find . -name "*_test.go" | grep -v vendor
```

### 3. Run Tests with Full Coverage

Execute tests with JSON coverage output:

**Python (pytest):**

```bash
uv run pytest -v --tb=short --cov --cov-report=term-missing --cov-report=json
```

**JavaScript/TypeScript (Jest):**

```bash
npm test -- --coverage --coverageReporters=json --coverageReporters=text
```

**JavaScript/TypeScript (Vitest):**

```bash
npm test -- --run --coverage --reporter=json --reporter=verbose
```

Capture the full output for inclusion in report.

### 4. Audit Test Quality

For each test file, analyze:

**Structure:**

- Proper naming conventions
- Logical organization
- Appropriate use of classes vs functions (or describe blocks)
- Test file organization

**Best Practices:**

- Fixture/setup usage and scope
- Parametrization opportunities
- Proper markers/tags
- Shared test utilities (conftest.js, setup files)

**Assertions:**

- Every test has meaningful assertions
- Using framework helpers (raises, toThrow, approx)
- Testing both success and failure paths
- Assertion clarity

**Mocking:**

- External dependencies mocked
- Proper mock verification
- No over-mocking
- Mock cleanup

**Coverage Gaps:**

- Untested functions/methods
- Missing edge cases
- Error paths not covered
- Integration scenarios missing

### 5. Categorize Findings

Organize issues by severity:

**CRITICAL** (Must Fix):

- Tests without assertions
- Broken imports/fixtures
- Tests that always pass regardless of code
- Tests that crash the test runner

**HIGH** (Should Fix):

- Missing error handling tests
- Inadequate mocking
- Test interdependencies
- Coverage below threshold
- Flaky tests

**MEDIUM** (Improve):

- Parametrization opportunities
- Missing markers/tags
- Redundant test code
- Slow tests
- Test organization issues

**LOW** (Optional):

- Style inconsistencies
- Missing docstrings/comments
- Minor organization issues
- Naming improvements

### 6. Generate Report

Write to `TESTING_REPORT.local.md` in project root:

```markdown
# Test Quality Report

**Generated:** [YYYY-MM-DD HH:MM:SS]
**Project:** [absolute path]
**Framework:** [pytest/jest/vitest/go/cargo]
**Version:** [framework version]

---

## Test Execution Summary

**Status:** [PASSED/FAILED]
**Total Tests:** [N]
**Passed:** [N] | **Failed:** [N] | **Skipped:** [N] | **Errors:** [N]
**Duration:** [X.XXs]

### Command Executed
```text
[actual command used]
```

### Test Output

```text
[Full test output]
```

---

## Coverage Summary

**Overall Coverage:** [XX.X%]
**Threshold:** [XX%]
**Status:** [PASSING/FAILING]

### Coverage by Module

| Module | Statements | Missing | Coverage |
|--------|------------|---------|----------|
| src/module1.py | 100 | 5 | 95% |
| src/module2.py | 80 | 18 | 78% |

### Files Below Threshold

- `src/module2.py`: 78% (threshold: 80%)
  - Missing lines: 23-25, 45, 67-70

---

## Audit Findings

### CRITICAL (Must Fix)

**1. [Issue Title]**

- **File:** `tests/test_example.py:23`
- **Issue:** [Description]
- **Evidence:**

  ```[language]
  [Code snippet]
  ```

- **Fix:** [Recommendation]

### HIGH (Should Fix)

[Issues...]

### MEDIUM (Improvements)

[Issues...]

### LOW (Optional)

[Issues...]

---

## Recommendations

### Priority 1: Critical Fixes

1. [Action with file:line reference]

### Priority 2: Coverage Improvements

1. [Action with specific files]

### Priority 3: Test Quality

1. [Action with examples]

### Priority 4: Organization

1. [Action with suggestions]

---

## Test File Inventory

| File | Tests | Passed | Failed | Coverage |
|------|-------|--------|--------|----------|
| tests/test_config.py | 14 | 14 | 0 | 100% |
| tests/test_handlers.py | 34 | 34 | 0 | 95% |

---

## Next Steps

- [ ] Fix critical issues
- [ ] Improve coverage to [threshold]%
- [ ] Address high-priority findings
- [ ] Consider parametrizing similar tests

---

**Report Location:** [absolute path]/TESTING_REPORT.local.md

```text

### 7. Summary Output

After generating report, show concise summary:

```text

Test Report Generated

Framework: [detected framework]
Status: [PASSED/FAILED/NEEDS ATTENTION]
Coverage: XX.X%
Tests: N passed, M failed (K total)

Issues Found:
  Critical: N
  High: M
  Medium: K
  Low: J

Top 3 Actions:

1. [Most important action]
2. [Second priority]
3. [Third priority]

Full report: [path]/TESTING_REPORT.local.md

```

## Options

- `/test:report --quick` - Skip detailed audit, just run tests and summarize
- `/test:report --verbose` - Include all code snippets and full analysis
- `/test:report --fix` - Generate report and offer to fix critical issues
