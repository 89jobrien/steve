---
status: DEPRECATED
deprecated_in: "2026-01-20"
name: python-uv
description: "Use UV for Python dependency management. Use when setting up Python projects, creating Dockerfiles for Python apps, or managing dependencies & `pyproject.toml` files. UV provides deterministic resolution, speed, and reproducibility."
user-invocable: false
---


# Python UV Package Management

## Core Principle

**UV is the modern standard for Python dependency management.** It provides deterministic resolution, 10-100x speed improvement over pip, and built-in virtual environment management.

## When to Use This Skill

- Setting up new Python projects
- Managing Python dependencies
- Running `.py` files and commands
- Running python tools like `pytest` and `ruff`
- Creating Dockerfiles for Python applications
- CI/CD pipelines for Python
- Migrating from pip/poetry to UV

## Why UV Over Alternatives

```
Speed comparison (20 dependencies, cold install):
- pip install: 120-180 seconds
- uv sync: 15-20 seconds (10x faster)

With cache:
- pip install (cached): 60-90 seconds
- uv sync (cached): 2-5 seconds (30x faster)

Additional benefits:
- Deterministic resolution (lockfile guarantees exact versions)
- Built-in virtual environment management
- Docker cache-friendly (separate download/install phases)
- Drop-in pip compatibility
- Cross-platform lockfiles
```

## Standard Workflow

### Project Setup

```bash
# Initialize new project (creates pyproject.toml)
uv init

# Or add UV to existing project with pyproject.toml
uv lock  # Generate uv.lock from pyproject.toml
```

### Daily Development

```bash
# Install all dependencies (creates/updates venv)
uv sync

# Install without dev dependencies
uv sync --no-dev

# Add runtime dependency
uv add boto3>=1.40.0

# Add dev dependency
uv add --dev pytest>=8.0.0

# Remove dependency
uv remove boto3

# Update lockfile (resolve latest within constraints)
uv lock --upgrade

# Run command in virtual environment
uv run pytest tests/
uv run python -m myapp
uv run mypy src/
```

### Lockfile Management

```bash
# Generate/update lockfile
uv lock

# Update all dependencies to latest (within constraints)
uv lock --upgrade

# Update specific package
uv lock --upgrade-package boto3

# Verify lockfile is in sync (CI check)
uv lock --check
```

## Docker Integration Pattern

### Standard Dockerfile Structure

```dockerfile
FROM python:3.12-slim AS builder

WORKDIR /app

# Copy UV from official image (always current)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files FIRST (layer caching)
COPY pyproject.toml uv.lock ./

# Install with cache mount (fast rebuilds)
RUN --mount=type=cache,target=/root/.cache/uv,sharing=locked \
    uv sync --frozen

# Copy source code AFTER dependencies (cache-friendly)
COPY src/ ./src/

# ... rest of build
```

### The --frozen Discipline

```
CRITICAL: Different flags for different contexts

Development (local):
  uv sync          # May update uv.lock if out of sync

CI/Docker (production):
  uv sync --frozen # FAILS if uv.lock doesn't match pyproject.toml

Why --frozen in Docker/CI:
- Ensures lockfile is committed and current
- Prevents silent dependency changes during build
- Build failure = lockfile drift (intentional safety)
- Reproducible builds guaranteed
```

### Multi-Stage with UV

```dockerfile
# STAGE 1: Builder (with dev deps for testing)
FROM python:3.12-slim AS builder

WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Install ALL dependencies (including dev)
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv,sharing=locked \
    uv sync --frozen

# Copy source and tests
COPY src/ ./src/
COPY tests/ ./tests/

# Run tests during build
RUN uv run pytest tests/

# Build wheel
RUN uv build

# STAGE 2: Runtime (production deps only)
FROM python:3.12-slim

WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Install ONLY runtime dependencies
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv,sharing=locked \
    uv sync --frozen --no-dev --no-install-project

# Install built wheel from builder
COPY --from=builder /app/dist/*.whl ./
RUN uv pip install *.whl && rm *.whl

ENV PATH="/app/.venv/bin:$PATH"
ENTRYPOINT ["python", "-m", "myapp"]
```

## pyproject.toml Structure

```toml
[project]
name = "myproject"
version = "0.1.0"
description = "Project description"
requires-python = ">=3.12"
dependencies = [
    "boto3~=1.40.52",      # Runtime deps
    "pydantic>=2.0.0,<3.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",       # Dev/test deps
    "mypy>=1.8.0",
    "ruff>=0.1.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.uv]
# UV-specific configuration (optional)
```

## Decision Framework

```
Q: When should I use pip instead of UV?
A: Rarely. UV handles all pip use cases faster.
   Exception: Legacy systems that can't install UV.

Q: How do I migrate from pip/requirements.txt?
A: 1. Create pyproject.toml with dependencies
   2. Run: uv lock
   3. Run: uv sync
   4. Delete requirements.txt

Q: How do I migrate from poetry?
A: 1. UV reads pyproject.toml (poetry format compatible)
   2. Run: uv lock (generates uv.lock)
   3. Run: uv sync
   4. Optionally remove poetry.lock

Q: When to use uv sync vs uv sync --frozen?
A: Development: uv sync (flexible)
   CI/Docker: uv sync --frozen (strict)

Q: How to handle private packages?
A: uv add package --index-url https://private.pypi/simple/
   Or configure in pyproject.toml [tool.uv.sources]
```

## CI/CD Patterns

### GitHub Actions

```yaml
- name: Install UV
  uses: astral-sh/setup-uv@v1

- name: Install dependencies
  run: uv sync --frozen

- name: Run tests
  run: uv run pytest tests/

- name: Type check
  run: uv run mypy src/
```

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: uv-lock-check
        name: Check uv.lock is in sync
        entry: uv lock --check
        language: system
        pass_filenames: false
```

## Anti-Patterns

```
❌ Using pip for new Python projects
   → UV is faster and more reliable

❌ Not using --frozen in Docker/CI
   → Silent dependency drift, unreproducible builds

❌ Committing without uv.lock
   → Loses reproducibility, different installs per machine

❌ Manual venv management (python -m venv)
   → UV handles this automatically

❌ Using requirements.txt with UV
   → Use pyproject.toml (modern standard)

❌ Ignoring uv.lock in .gitignore
   → Lockfile MUST be committed for reproducibility

✅ `uv` for all Python dependency management
✅ --frozen in all CI/Docker contexts
✅ Commit uv.lock alongside pyproject.toml
✅ Let UV manage virtual environments
✅ Use cache mounts in Docker for speed
```

## Integration with Other Skills

- **version-pinning**: Use for constraint strategy (~= vs >=)
- **docker-multistage**: UV integrates with multi-stage pattern
- **version-currency**: uv.lock is authoritative for version verification
- **container-boundary**: UV venv is container-local, not host

## Lockfile as Source of Truth

```
The uv.lock file contains:
- Exact version of every dependency (including transitive)
- SHA256 hashes for integrity verification
- Source URLs for each package
- Platform-specific resolutions

This provides:
- Reproducible builds across machines/time
- Security via tamper detection (hashes)
- Auditability (know exactly what's installed)
- Version verification (see version-currency skill)
```

## Meta-Principle

```
UV modernizes Python dependency management.

Old way (pip):
- Slow installs
- Non-deterministic resolution
- Manual venv management
- requirements.txt (limited metadata)

New way (UV):
- Fast installs (10-100x)
- Deterministic resolution (lockfile)
- Automatic venv management
- pyproject.toml (rich metadata)

For any new Python project: Start with UV.
For existing projects: Migrate to UV.

The --frozen flag is your CI/Docker safety net.
Never ship without it.
```
