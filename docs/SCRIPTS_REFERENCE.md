# Scripts Reference

Complete API reference for the management scripts in the Steve repository.

## Overview

The `scripts/` directory contains Python utilities for managing Claude Code components. All scripts use `uv run` for
execution.

| Script | Purpose |
|--------|---------|
| `build_index.py` | Generate component index |
| `list_components.py` | List and search components |
| `install_component.py` | Install component by name |
| `install_from_gist.py` | Install from GitHub Gist |
| `publish_to_gist.py` | Publish component to Gist |
| `publish_registry.py` | Publish registry to Gist |
| `add_metadata.py` | Update component frontmatter |
| `detect_secrets.py` | Scan for secrets |
| `python_to_markdown.py` | Convert Python to Markdown |

## build_index.py

Scans the repository and generates a JSON index of all components.

### Usage

```bash
uv run scripts/build_index.py [--output FILE]
```

### Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--output` | Output file path | `index.json` |

### Output Format

```json
{
  "version": "1.0.0",
  "generated_at": "2025-01-15T10:30:00Z",
  "agents": [...],
  "commands": [...],
  "skills": [...],
  "hooks": [...],
  "templates": [...]
}
```

### Component Metadata

Each component type includes specific fields:

**Agents:**

```json
{
  "name": "code-reviewer",
  "description": "Reviews code for quality",
  "domain": "code-quality",
  "path": "agents/code-quality/code-reviewer.md",
  "tools": "Read, Grep, Glob",
  "model": "sonnet",
  "color": "cyan",
  "skills": ["code-review"]
}
```

**Skills:**

```json
{
  "name": "code-review",
  "description": "Code review methodology",
  "domain": "quality",
  "path": "skills/code-review/SKILL.md",
  "has_references": true,
  "has_scripts": false,
  "has_assets": false
}
```

**Commands:**

```json
{
  "name": "review-code",
  "description": "Review code quality",
  "domain": "dev",
  "path": "commands/dev/review-code.md"
}
```

**Hooks:**

```json
{
  "name": "lint_changed",
  "description": "Lint modified files",
  "domain": "analyzers",
  "path": "hooks/analyzers/lint_changed.py"
}
```

### Key Functions

```python
def build_index(repo_root: Path) -> dict[str, Any]:
    """Build complete component index."""

def scan_directory(
    directory: Path,
    component_type: str,
    extract_metadata: Callable
) -> list[dict]:
    """Scan directory for components."""

def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Extract YAML frontmatter from markdown file."""
```

### Example

```bash
# Generate index.json in repository root
uv run scripts/build_index.py

# Generate index to custom location
uv run scripts/build_index.py --output dist/components.json
```

## list_components.py

Lists and filters components from local or remote registry.

### Usage

```bash
uv run scripts/list_components.py [OPTIONS]
```

### Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--type TYPE` | Filter by type (agent/command/skill/hook) | All types |
| `--domain DOMAIN` | Filter by domain | All domains |
| `--search QUERY` | Search in name/description | None |
| `--from-registry` | Use remote registry | Local |
| `--json` | Output as JSON | Table format |

### Key Functions

```python
def load_local_registry() -> dict:
    """Load .gist-registry.json from repository root."""

def load_remote_registry(registry_url: str) -> dict:
    """Fetch registry from GitHub Gist."""

def filter_components(
    registry: dict,
    component_type: str | None,
    domain: str | None,
    search: str | None
) -> list[dict]:
    """Filter components by criteria."""
```

### Example

```bash
# List all agents
uv run scripts/list_components.py --type agent

# Search for security-related components
uv run scripts/list_components.py --search security

# List commands in dev domain
uv run scripts/list_components.py --type command --domain dev

# List from remote registry as JSON
uv run scripts/list_components.py --from-registry --json
```

## install_component.py

Installs a component by name from local or remote registry.

### Usage

```bash
uv run scripts/install_component.py NAME [OPTIONS]
```

### Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `NAME` | Component name (required) | - |
| `--type TYPE` | Component type filter | Auto-detect |
| `--domain DOMAIN` | Domain filter | Any |
| `--from-registry` | Use remote registry | Local |
| `--target PATH` | Installation target | `~/.claude/` |

### Resolution Process

1. Load registry (local `.gist-registry.json` or remote)
2. Case-insensitive name matching
3. Apply type/domain filters if specified
4. If multiple matches, list candidates and exit
5. Delegate to `install_from_gist.py` with resolved URL

### Key Functions

```python
def find_component(
    registry: dict,
    name: str,
    component_type: str | None,
    domain: str | None
) -> dict | None:
    """Find component by name with optional filters."""

def install_component(component: dict, target_path: Path) -> None:
    """Install component using gist URL."""
```

### Example

```bash
# Install code-reviewer agent
uv run scripts/install_component.py code-reviewer

# Install with type disambiguation
uv run scripts/install_component.py lint --type hook

# Install from remote registry
uv run scripts/install_component.py debugger --from-registry

# Install to custom location
uv run scripts/install_component.py code-review --target ./my-claude/
```

## install_from_gist.py

Downloads and installs a component from a GitHub Gist URL.

### Usage

```bash
uv run scripts/install_from_gist.py URL [OPTIONS]
```

### Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `URL` | GitHub Gist URL (required) | - |
| `--target-path PATH` | Override auto-detection | Auto-detect |
| `--force` | Overwrite existing files | Prompt |

### Auto-Detection Logic

The script determines installation path based on:

1. **Filename extension:**
   - `.py` files go to `hooks/`
   - `.md` files analyzed further

2. **Frontmatter type field** (if present)

3. **Content patterns:**
   - Contains `skills:` field -> `agents/`
   - Contains `allowed-tools:` field -> `commands/`
   - Contains `SKILL.md` -> `skills/`

4. **Domain extraction** from path or frontmatter

### Key Functions

```python
def fetch_gist(gist_url: str) -> dict:
    """Fetch gist metadata and files from GitHub API."""

def determine_target_path(
    filename: str,
    content: str,
    repo_root: Path
) -> Path:
    """Auto-detect appropriate installation path."""

def install_file(content: str, target_path: Path, force: bool) -> None:
    """Write content to target path."""
```

### Example

```bash
# Install from Gist URL (auto-detect path)
uv run scripts/install_from_gist.py https://gist.github.com/user/abc123

# Install to specific path
uv run scripts/install_from_gist.py https://gist.github.com/user/abc123 \
    --target-path ~/.claude/agents/custom/

# Force overwrite existing
uv run scripts/install_from_gist.py https://gist.github.com/user/abc123 --force
```

## publish_to_gist.py

Publishes a component to GitHub Gist and updates the local registry.

### Usage

```bash
uv run scripts/publish_to_gist.py PATH [OPTIONS]
```

### Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `PATH` | Component file path (required) | - |
| `--public` | Create public gist | Secret |
| `--update` | Update existing gist | Create new |
| `--description TEXT` | Gist description | Auto-generate |

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GITHUB_TOKEN` | GitHub personal access token | Yes |

The token can also be set via `git config github.token`.

### Workflow

1. Read component file and parse frontmatter
2. Create or update GitHub Gist via API
3. Update component frontmatter with `gist_url`
4. Update `.gist-registry.json` with component metadata

### Registry Entry Format

```json
{
  "name": "code-reviewer",
  "type": "agent",
  "domain": "code-quality",
  "path": "agents/code-quality/code-reviewer.md",
  "gist_url": "https://gist.github.com/user/abc123",
  "gist_id": "abc123",
  "description": "Reviews code for quality",
  "tools": "Read, Grep, Glob",
  "model": "sonnet",
  "published_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z"
}
```

### Key Functions

```python
def create_gist(
    content: str,
    filename: str,
    description: str,
    public: bool
) -> dict:
    """Create new GitHub Gist."""

def update_gist(gist_id: str, content: str, filename: str) -> dict:
    """Update existing GitHub Gist."""

def update_registry(
    component_path: Path,
    gist_url: str,
    gist_id: str,
    metadata: dict
) -> None:
    """Add/update component in .gist-registry.json."""
```

### Example

```bash
# Publish agent as secret gist
uv run scripts/publish_to_gist.py agents/code-quality/code-reviewer.md

# Publish as public gist
uv run scripts/publish_to_gist.py agents/debugger.md --public

# Update existing gist
uv run scripts/publish_to_gist.py agents/debugger.md --update

# With custom description
uv run scripts/publish_to_gist.py commands/dev/review-code.md \
    --description "Code review slash command for Claude Code"
```

## publish_registry.py

Publishes the `.gist-registry.json` file to GitHub Gist for remote access.

### Usage

```bash
uv run scripts/publish_registry.py [OPTIONS]
```

### Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--public` | Create public gist | Secret |
| `--update` | Update existing gist | Create new |

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GITHUB_TOKEN` | GitHub personal access token | Yes |

### Workflow

1. Read `.gist-registry.json` from repository root
2. Create or update GitHub Gist
3. Output the gist URL for sharing

### Key Functions

```python
def get_existing_gist_id() -> str | None:
    """Check if registry gist already exists."""

def create_gist(content: str, public: bool) -> dict:
    """Create new registry gist."""

def update_gist(gist_id: str, content: str) -> dict:
    """Update existing registry gist."""
```

### Example

```bash
# Publish registry as secret gist
uv run scripts/publish_registry.py

# Publish as public for sharing
uv run scripts/publish_registry.py --public

# Update existing registry gist
uv run scripts/publish_registry.py --update
```

## add_metadata.py

Updates YAML frontmatter in component files with additional metadata.

### Usage

```bash
uv run scripts/add_metadata.py PATH [OPTIONS]
```

### Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `PATH` | Component file path (required) | - |
| `--gist-url URL` | Add gist_url field | - |
| `--key KEY VALUE` | Add custom key-value pair | - |

### Key Functions

```python
def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Parse YAML frontmatter from markdown content."""

def update_frontmatter(
    content: str,
    updates: dict[str, Any]
) -> str:
    """Update frontmatter with new values."""
```

### Example

```bash
# Add gist URL to component
uv run scripts/add_metadata.py agents/debugger.md \
    --gist-url https://gist.github.com/user/abc123

# Add custom metadata
uv run scripts/add_metadata.py agents/debugger.md \
    --key version 1.2.0

# Add multiple fields
uv run scripts/add_metadata.py agents/debugger.md \
    --gist-url https://gist.github.com/user/abc123 \
    --key author "Joe Developer"
```

## detect_secrets.py

Scans the repository for potential secrets using the detect-secrets library.

### Usage

```bash
uv run scripts/detect_secrets.py [OPTIONS]
```

### Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--baseline` | Generate baseline file | Scan only |
| `--scan` | Scan against baseline | - |
| `--output FILE` | Baseline file path | `.secrets.baseline` |

### Workflow

**Creating baseline:**

1. Scan repository for secrets
2. Review detected secrets
3. Mark false positives in baseline
4. Commit baseline file

**Scanning:**

1. Load baseline file
2. Scan repository
3. Report new secrets not in baseline
4. Exit non-zero if new secrets found

### Key Functions

```python
def generate_baseline(repo_root: Path, output_file: Path) -> None:
    """Generate new secrets baseline file."""

def scan_repository(repo_root: Path, baseline_file: Path) -> list[dict]:
    """Scan repository and return new secrets."""
```

### Example

```bash
# Generate initial baseline
uv run scripts/detect_secrets.py --baseline

# Scan for new secrets
uv run scripts/detect_secrets.py --scan

# Custom baseline location
uv run scripts/detect_secrets.py --baseline --output .secrets.json
```

## python_to_markdown.py

Converts Python files to Markdown format with syntax highlighting.

### Usage

```bash
uv run scripts/python_to_markdown.py INPUT [OUTPUT]
```

### Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `INPUT` | Python file path (required) | - |
| `OUTPUT` | Markdown output path | `{input}.md` |

### Output Format

```markdown
# Script Title

```python
# Python code here
```

```

The title is generated from the filename using title case conversion.

### Key Functions

```python
def filename_to_title(filename: str) -> str:
    """Convert kebab-case/snake_case filename to Title Case."""

def python_to_markdown(input_file: str, output_file: str | None) -> None:
    """Convert Python file to Markdown."""
```

### Example

```bash
# Convert with auto-generated output name
uv run scripts/python_to_markdown.py hooks/analyzers/lint_changed.py
# Creates: hooks/analyzers/lint_changed.md

# Convert with custom output
uv run scripts/python_to_markdown.py myscript.py docs/myscript-reference.md
```

## Common Patterns

### Error Handling

All scripts follow consistent error handling:

```python
def main():
    try:
        # Script logic
        pass
    except FileNotFoundError as e:
        print(f"Error: File not found: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: Invalid input: {e}", file=sys.stderr)
        sys.exit(2)
```

### Environment Variables

Scripts that interact with GitHub require authentication:

```bash
# Option 1: Environment variable
export GITHUB_TOKEN=ghp_xxxxxxxxxxxx

# Option 2: Git config
git config --global github.token ghp_xxxxxxxxxxxx
```

### Path Resolution

Scripts handle paths consistently:

```python
from pathlib import Path

# Repository root detection
repo_root = Path(__file__).parent.parent

# User config directory
config_dir = Path.home() / ".claude"

# Relative to absolute
absolute_path = Path(user_input).resolve()
```

## Dependencies

Scripts require these Python packages (defined in `pyproject.toml`):

| Package | Purpose |
|---------|---------|
| `pyyaml` | YAML frontmatter parsing |
| `requests` | GitHub API interactions |
| `detect-secrets` | Secrets scanning |
| `rich` | Terminal formatting (optional) |

Install with:

```bash
uv sync
```

## See Also

- [Installation](INSTALLATION.md) - Using scripts for installation
- [Publishing](PUBLISHING.md) - Publishing workflow
- [Development](DEVELOPMENT.md) - Creating new components
- [Contributing](CONTRIBUTING.md) - Contribution guidelines
