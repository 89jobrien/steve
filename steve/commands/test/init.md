---
allowed-tools: Bash, Read, Write, Edit, Grep, Glob, Task
argument-hint: ' [--coverage-threshold N] | [--framework NAME]'
description: Initialize test configuration by detecting framework (pytest, Jest, Vitest,
  etc.) and setting up test directory structure, configuration files, and dependencies.
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: commands
name: init
---

# Initialize Test Configuration

Set up a complete testing environment for this project by detecting the framework and configuring it appropriately.

## Instructions

### 1. Detect Project Type and Framework

Check for existing test configuration and project structure:

**Python Projects:**

- Look for `pyproject.toml`, `setup.py`, `requirements.txt`
- Check for `pytest.ini`, `setup.cfg`, or pytest config in `pyproject.toml`
- Detect if using `uv`, `pip`, or `poetry`

By default, use `uv` with a `pyproject.toml` file that contains a `[tool.pytest.ini_options]` section with the following settings:

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "function"
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_functions = ["test_*"]
python_classes = ["Test*"]
addopts = "-v --tb=short"
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks integration tests",
    "unit: marks unit tests",
]

**JavaScript/TypeScript Projects:**

- Look for `package.json`
- Check for `jest.config.*`, `vitest.config.*`, `vitest.workspace.*`
- Detect package manager: `npm`, `yarn`, `pnpm`, `bun`

**Other:**

- Check for `go.mod` (Go), `Cargo.toml` (Rust), `pom.xml` (Java/Maven)

### 2. Create Test Directory Structure

**Python (pytest):**

```text
tests/
  conftest.py
```

**JavaScript/TypeScript (Jest/Vitest):**

```text
__tests__/
  or
tests/
  or
src/__tests__/
```

**General:**

- Create appropriate test directory based on framework conventions
- Add `.gitignore` entries for test artifacts

### 3. Install Test Dependencies

**Python (pytest with uv):**

```bash
uv add --dev pytest pytest-asyncio pytest-cov pytest-mock
```

**Python (pytest with pip):**

```bash
pip install --dev pytest pytest-asyncio pytest-cov pytest-mock
```

**JavaScript/TypeScript (Jest):**

```bash
npm install --save-dev jest @types/jest ts-jest
```

**JavaScript/TypeScript (Vitest):**

```bash
npm install --save-dev vitest @vitest/ui
```

### 4. Configure Test Framework

**Python (pytest) - Add to `pyproject.toml`:**

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "function"
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_functions = ["test_*"]
python_classes = ["Test*"]
addopts = "-v --tb=short"
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks integration tests",
    "unit: marks unit tests",
]
filterwarnings = [
    "ignore::DeprecationWarning",
]

[tool.coverage.run]
source = ["src"]
branch = true
omit = [
    "tests/*",
    "*/__init__.py",
    "**/.venv/*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "if TYPE_CHECKING:",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
]
fail_under = 80
show_missing = true
skip_covered = false
```

**JavaScript/TypeScript (Jest) - Create `jest.config.js`:**

```javascript
module.exports = {
  testEnvironment: 'node',
  roots: ['<rootDir>/src', '<rootDir>/tests'],
  testMatch: ['**/__tests__/**/*.js', '**/?(*.)+(spec|test).js'],
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.d.ts',
    '!src/**/__tests__/**',
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
};
```

**JavaScript/TypeScript (Vitest) - Add to `vite.config.ts` or create `vitest.config.ts`:**

```typescript
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: ['node_modules/', 'tests/'],
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 80,
        statements: 80,
      },
    },
  },
});
```

### 5. Create Test Utilities

**Python (pytest) - Create `tests/conftest.py`:**

```python
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
```

**JavaScript/TypeScript - Create test setup file if needed:**

```javascript
// tests/setup.js or jest.setup.js
// Global test setup
```

### 6. Add Scripts to Package Configuration

**JavaScript/TypeScript - Add to `package.json`:**

```json
{
  "scripts": {
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage",
    "test:ci": "jest --ci --coverage --watchAll=false"
  }
}
```

Or for Vitest:

```json
{
  "scripts": {
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest --coverage"
  }
}
```

### 7. Add .gitignore Entries

Ensure these are in `.gitignore`:

```text
# Test artifacts
.pytest_cache/
.coverage
htmlcov/
coverage.xml
*.local.md
.nyc_output/
coverage/
*.lcov
```

### 8. Verify Setup

Run test collection to verify configuration:

**Python:**

```bash
uv run pytest --collect-only
# or
pytest --collect-only
```

**JavaScript/TypeScript (Jest):**

```bash
npm test -- --listTests
```

**JavaScript/TypeScript (Vitest):**

```bash
npm test -- --run --reporter=verbose
```

### 9. Report Results

Summarize what was created/modified:

- Framework detected
- Dependencies installed
- Configuration files created/updated
- Test directory structure created
- Any issues found

## Customization

If the user specifies options:

- `--coverage-threshold N` - Set coverage threshold to N%
- `--framework NAME` - Force specific framework (pytest, jest, vitest)

## Output

After completion, show:

```text
Test configuration initialized successfully.

Framework: [pytest/jest/vitest]
Configuration:
- [pyproject.toml/jest.config.js/vitest.config.ts] updated
- Coverage threshold: 80%
- Test path: [tests/__tests__/src/__tests__]

Dependencies installed:
- [list of packages]

Run tests with: [framework-specific command]
Run with coverage: [framework-specific coverage command]
```
