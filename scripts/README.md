# Scripts

Utility scripts for managing the steve repository.

## detect_secrets.py

Secrets detection script using `detect-secrets`.

### Installation

```bash
pip install detect-secrets
```

### Usage

**Generate baseline:**

```bash
python scripts/detect_secrets.py --baseline
```

**Scan for secrets:**

```bash
python scripts/detect_secrets.py --scan
```

**Both:**

```bash
python scripts/detect_secrets.py --baseline --scan
```

### Pre-commit Hook

Install pre-commit hooks to automatically check for secrets:

```bash
pip install pre-commit
pre-commit install
```

The hook will run `detect-secrets` before each commit.

### Baseline File

The `.secrets.baseline` file contains known false positives. When you add new code:

1. Run `detect_secrets.py --baseline` to update the baseline
2. Review any new findings
3. Commit the updated baseline

## build_index.py

Build index of all components in the repository.

### Usage

```bash
python scripts/build_index.py [--output index.json]
```

Generates a JSON index file with metadata about all agents, commands, skills, hooks, and templates.

## add_metadata.py

Add or update metadata in component files.

### Usage

```bash
python scripts/add_metadata.py <component-path> [--gist-url URL] [--key KEY VALUE]
```

Adds metadata like `gist_url` to component frontmatter.

## publish_to_gist.py

Publish a component to GitHub Gist.

### Installation

Requires `requests` library:

```bash
pip install requests
```

### Setup

Set GitHub token:

```bash
export GITHUB_TOKEN=your_token_here
# Or configure git:
git config --global github.token your_token_here
```

### Usage

**Create new gist:**

```bash
python scripts/publish_to_gist.py steve/agents/core/meta.md [--public]
```

**Update existing gist:**

```bash
python scripts/publish_to_gist.py steve/agents/core/meta.md --update
```

## install_from_gist.py

Install a component from a GitHub Gist.

### Installation

Requires `requests` and `pyyaml`:

```bash
pip install requests pyyaml
```

### Usage

```bash
python scripts/install_from_gist.py <gist-url> [--target-path path]
```

Downloads a component from a Gist and installs it in the appropriate location.

## list_components.py

List available components from the registry.

### Usage

**List all components:**

```bash
python scripts/list_components.py
```

**Filter by type:**

```bash
python scripts/list_components.py --type agent
```

**Search components:**

```bash
python scripts/list_components.py --search "code review"
```

**From remote registry:**

```bash
python scripts/list_components.py --from-registry --registry-url <gist-url>
```

## install_component.py

Install a component by name from the registry.

### Usage

**Install by name:**

```bash
python scripts/install_component.py code-reviewer
```

**With filters:**

```bash
python scripts/install_component.py meta --type agent --domain core
```

**From remote registry:**

```bash
python scripts/install_component.py <name> --from-registry --registry-url <gist-url>
```

## publish_registry.py

Publish the component registry to a GitHub Gist for remote access.

### Usage

**Publish registry:**

```bash
python scripts/publish_registry.py --public
```

**Update existing registry:**

```bash
python scripts/publish_registry.py --update
```

This creates a Gist containing `.gist-registry.json` that others can use to discover and install components.

## Component Discovery Workflow

### For Component Authors

1. **Publish individual components:**

   ```bash
   python scripts/publish_to_gist.py steve/agents/core/meta.md --public
   ```

   This automatically:
   - Creates/updates the Gist
   - Updates component frontmatter with `gist_url`
   - Updates `.gist-registry.json` locally

2. **Publish the registry:**

   ```bash
   python scripts/publish_registry.py --public
   ```

   This makes the registry available for others to discover components.

### For Component Users

1. **Discover components:**

   ```bash
   # From local registry
   python scripts/list_components.py --type agent

   # From remote registry
   python scripts/list_components.py --from-registry --registry-url <gist-url>
   ```

2. **Install components:**

   ```bash
   # By name (searches local registry)
   python scripts/install_component.py code-reviewer

   # From remote registry
   python scripts/install_component.py code-reviewer --from-registry --registry-url <gist-url>

   # Direct from Gist URL
   python scripts/install_from_gist.py <gist-url>
   ```

## Other Scripts

- `python_to_markdown.py` - Convert Python scripts to markdown documentation

## Installation

Install all Python dependencies:

```bash
pip install -r scripts/requirements.txt
```
