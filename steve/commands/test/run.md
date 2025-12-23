---
allowed-tools: Bash, Read, Grep
argument-hint: ' [--watch] | [--coverage] | [--file PATH] | [--pattern PATTERN]'
description: Run tests with framework detection. Supports pytest, Jest, Vitest, and
  other common test frameworks. Shows pass/fail summary and coverage metrics.
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: commands
---

# Run Tests

Execute the test suite with coverage reporting. Automatically detects and uses the appropriate test framework.

## Instructions

### 1. Detect Test Framework

Identify the testing framework:

**Python:**

- Check for `pytest` command or in `pyproject.toml`
- Look for `uv` or `pip` environment

**JavaScript/TypeScript:**

- Check `package.json` for test scripts
- Detect `jest`, `vitest`, `mocha`, etc.

**Other:**

- Detect Go: `go test`
- Detect Rust: `cargo test`

### 2. Locate Project Root

Find the directory containing test configuration:

- Start from current working directory
- Search parent directories if needed
- Look for `pyproject.toml`, `package.json`, `go.mod`, `Cargo.toml`

### 3. Run Tests with Coverage

Execute tests with comprehensive flags based on framework:

**Python (pytest with uv):**

```bash
uv run pytest -v --tb=short --cov --cov-report=term-missing
```

**Python (pytest with pip):**

```bash
pytest -v --tb=short --cov --cov-report=term-missing
```

**JavaScript/TypeScript (Jest):**

```bash
npm test -- --coverage --verbose
```

**JavaScript/TypeScript (Vitest):**

```bash
npm test -- --run --coverage
```

**Go:**

```bash
go test -v -cover ./...
```

**Rust:**

```bash
cargo test -- --nocapture
```

### 4. Handle User Options

If the user adds flags, pass them through or interpret:

- `--watch` - Run in watch mode (Jest/Vitest)
- `--coverage` / `--no-cov` - Toggle coverage
- `--file PATH` - Run specific test file
- `--pattern PATTERN` - Run tests matching pattern
- `-x` / `--fail-fast` - Stop on first failure
- `-k PATTERN` - Run tests matching pattern (pytest)

### 5. Capture Results

Record:

- Total tests run
- Passed count
- Failed count
- Skipped count
- Error count
- Total duration
- Coverage percentage (if available)
- Files with low coverage

### 6. Handle Failures

If tests fail:

- Show the failing test names
- Show abbreviated error messages
- Suggest running specific failed tests for debugging:

**Python:**

```bash
uv run pytest tests/test_file.py::test_name -v --tb=long
```

**JavaScript/TypeScript:**

```bash
npm test -- tests/test_file.test.js -t "test name"
```

### 7. Output Format

```text
Test Run Complete

Framework: [pytest/jest/vitest/go/cargo]
Status: PASSED / FAILED
Duration: X.XXs

Results:
  Passed:  N
  Failed:  M
  Skipped: K
  Errors:  J
  ─────────
  Total:   N+M+K+J

Coverage: XX.X% (if available)

[If failures exist:]
Failed Tests:
  - tests/test_file.py::test_name - AssertionError: ...
  - tests/test_other.py::test_other - ValueError: ...

[If coverage below threshold:]
Coverage Below Threshold:
  - src/module.py: 65% (threshold: 80%)
  - src/utils.py: 72% (threshold: 80%)

Run failed tests only:
  [framework-specific command]
```

### 8. Quick Commands Reference

Show at end for convenience:

**Python (pytest):**

```text
Quick Commands:
  uv run pytest                    # Run all
  uv run pytest --lf               # Run last failed
  uv run pytest -x                 # Stop on first failure
  uv run pytest -k "pattern"       # Run matching tests
  uv run pytest --cov-report=html  # Generate HTML report
```

**JavaScript/TypeScript (Jest):**

```text
Quick Commands:
  npm test                         # Run all
  npm test -- --watch              # Watch mode
  npm test -- --coverage           # With coverage
  npm test -- -t "pattern"         # Run matching tests
```

**JavaScript/TypeScript (Vitest):**

```text
Quick Commands:
  npm test                         # Run all
  npm test -- --ui                 # UI mode
  npm test -- --coverage           # With coverage
  npm test -- -t "pattern"         # Run matching tests
```

## Options

If the user adds flags to the command, pass them through:

- `/test:run --watch` - Watch mode (Jest/Vitest)
- `/test:run --coverage` - Include coverage
- `/test:run --file tests/specific.test.js` - Run specific file
- `/test:run -k auth` - Run tests matching "auth" (pytest)
- `/test:run -x` - Stop on first failure
