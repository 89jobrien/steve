# Component Discovery & Installation System

The steve repository includes a complete system for discovering, publishing, and installing individual components via GitHub Gists.

## How It Works

### Automatic Linking

When you publish a component using `publish_to_gist.py`, the system automatically:

1. **Creates/updates the Gist** - Publishes component content to GitHub Gist
2. **Updates component frontmatter** - Adds `gist_url` field to the component file
3. **Updates local registry** - Adds entry to `.gist-registry.json` with metadata

### Registry System

The `.gist-registry.json` file tracks all published components with:

- Component name, type, and domain
- Gist URL and ID
- Description and metadata
- Publication timestamps

The registry can be published as a Gist itself for remote discovery.

## Workflows

### Publishing Components

**1. Publish individual component:**

```bash
python scripts/publish_to_gist.py steve/agents/core/meta.md --public
```

This automatically:

- Creates a Gist with the component content
- Updates the component file with `gist_url` in frontmatter
- Updates `.gist-registry.json` with component metadata

**2. Update existing component:**

```bash
python scripts/publish_to_gist.py steve/agents/core/meta.md --update
```

**3. Publish the registry (for remote access):**

```bash
python scripts/publish_registry.py --public
```

This creates a Gist containing the registry that others can use to discover components.

### Discovering Components

**List all components:**

```bash
python scripts/list_components.py
```

**Filter by type:**

```bash
python scripts/list_components.py --type agent
python scripts/list_components.py --type skill
```

**Filter by domain:**

```bash
python scripts/list_components.py --domain core
python scripts/list_components.py --domain development
```

**Search components:**

```bash
python scripts/list_components.py --search "code review"
```

**From remote registry:**

```bash
python scripts/list_components.py --from-registry --registry-url <gist-url>
```

### Installing Components

**Install by name (from local registry):**

```bash
python scripts/install_component.py code-reviewer
```

**Install with filters:**

```bash
python scripts/install_component.py meta --type agent --domain core
```

**Install from remote registry:**

```bash
python scripts/install_component.py code-reviewer --from-registry --registry-url <gist-url>
```

**Install directly from Gist URL:**

```bash
python scripts/install_from_gist.py <gist-url>
```

## Registry Format

The `.gist-registry.json` file structure:

```json
{
  "version": "1.0.0",
  "description": "Registry of components published to GitHub Gists",
  "components": {
    "agents/core/meta.md": {
      "name": "meta",
      "type": "agent",
      "domain": "core",
      "path": "agents/core/meta.md",
      "gist_url": "https://gist.github.com/...",
      "gist_id": "...",
      "description": "...",
      "published_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z",
      "tools": "Read, Write, Grep",
      "model": "opus",
      "color": "cyan"
    }
  }
}
```

## Benefits

### For Component Authors

- **Automatic tracking** - Registry updates automatically when publishing
- **Easy updates** - Update components and registry in one command
- **Shareable** - Publish registry Gist for others to discover your components

### For Component Users

- **Discovery** - Search and list available components
- **Easy installation** - Install by name, no need to know Gist URLs
- **Remote access** - Use remote registries to discover components from other sources
- **Type safety** - Filter by type and domain to find exactly what you need

## Example: Complete Workflow

### Publishing a New Component

```bash
# 1. Create your component
# (edit steve/agents/core/my-agent.md)

# 2. Publish to Gist
python scripts/publish_to_gist.py steve/agents/core/my-agent.md --public

# Output:
# ✓ Gist published: https://gist.github.com/...
# ✓ Registry updated: .gist-registry.json

# 3. Publish registry (optional, for sharing)
python scripts/publish_registry.py --public

# Output:
# ✓ Registry published: https://gist.github.com/...
```

### Installing a Component

```bash
# 1. Discover components
python scripts/list_components.py --type agent

# Output:
# Found 5 component(s):
#   meta (agent)
#     Domain: core
#     Generates complete Claude Code sub-agent configuration files...
#     Gist: https://gist.github.com/...

# 2. Install by name
python scripts/install_component.py meta

# Output:
# Installing meta from https://gist.github.com/...
# ✓ Installed: steve/agents/core/meta.md
```

## Remote Registry Usage

You can use registries from other sources:

```bash
# List components from someone else's registry
python scripts/list_components.py \
  --from-registry \
  --registry-url https://gist.github.com/username/registry-gist-id

# Install from their registry
python scripts/install_component.py component-name \
  --from-registry \
  --registry-url https://gist.github.com/username/registry-gist-id
```

This enables:

- Community component sharing
- Curated component collections
- Version-specific registries
- Team-specific component sets

## Files

- **`.gist-registry.json`** - Local registry (tracked in git)
- **`.gist-registry-url`** - URL of published registry (gitignored)
- **`scripts/publish_to_gist.py`** - Publish component + auto-update registry
- **`scripts/publish_registry.py`** - Publish registry as Gist
- **`scripts/list_components.py`** - List/search components
- **`scripts/install_component.py`** - Install by name from registry
- **`scripts/install_from_gist.py`** - Install directly from Gist URL

## Notes

- The registry is automatically updated when publishing components
- Component frontmatter includes `gist_url` for direct linking
- Registry can be published as a Gist for remote discovery
- All scripts support both local and remote registries
