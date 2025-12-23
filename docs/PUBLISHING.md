# Publishing Guide

How to distribute Steve components via GitHub Gists for sharing and installation.

## Overview

Steve uses GitHub Gists as a distribution mechanism for components. This approach provides:

- **Easy sharing** - Single URL for each component
- **Version tracking** - Gist history shows changes
- **No package registry** - Direct from GitHub to user
- **Simple installation** - One command to install

## Prerequisites

### GitHub Token

A GitHub token with `gist` scope is required for publishing.

**Option 1: Environment Variable**

```bash
export GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxx"
```

**Option 2: Git Config**

```bash
git config --global github.token "ghp_xxxxxxxxxxxxxxxxxxxx"
```

**Creating a Token:**

1. Go to GitHub Settings > Developer settings > Personal access tokens
2. Generate new token (classic)
3. Select `gist` scope
4. Copy and store securely

### Dependencies

Install required Python packages:

```bash
uv sync
```

## Publishing Workflow

### Step 1: Prepare Component

Ensure the component is ready for publishing:

```bash
# Validate component structure
# Agent: has frontmatter with name, description
# Skill: has SKILL.md with frontmatter
# Command: has description in frontmatter
# Hook: has matching .py and .md files
```

### Step 2: Run Security Check

```bash
uv run scripts/detect_secrets.py --scan
```

Verify no secrets are present in the component.

### Step 3: Publish to Gist

```bash
# Publish a single component
uv run scripts/publish_to_gist.py steve/agents/domain/my-agent.md

# Publish as public gist
uv run scripts/publish_to_gist.py steve/agents/domain/my-agent.md --public

# Update existing gist
uv run scripts/publish_to_gist.py steve/agents/domain/my-agent.md --update
```

### Step 4: Verify Publication

The script will:

1. Create or update a GitHub Gist
2. Add `gist_url` to component frontmatter
3. Update `.gist-registry.json`
4. Print the gist URL

```text
Creating new gist...
Gist published: https://gist.github.com/username/abc123def456
Registry updated: .gist-registry.json
```

## Publishing Scripts

### publish_to_gist.py

Publishes individual components to GitHub Gists.

**Usage:**

```bash
uv run scripts/publish_to_gist.py <component-path> [options]
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `component-path` | Path to component file (relative to repo root) |

**Options:**

| Option | Description |
|--------|-------------|
| `--public` | Make gist publicly visible |
| `--update` | Update existing gist instead of creating new |

**Examples:**

```bash
# Publish new agent
uv run scripts/publish_to_gist.py steve/agents/development/code-reviewer.md

# Update existing skill
uv run scripts/publish_to_gist.py steve/skills/testing/SKILL.md --update

# Publish public command
uv run scripts/publish_to_gist.py steve/commands/git/clean-branches.md --public
```

**What It Does:**

1. Reads component file content
2. Creates/updates GitHub Gist via API
3. Extracts gist ID from response
4. Calls `add_metadata.py` to add `gist_url` to frontmatter
5. Updates `.gist-registry.json` with component entry

### publish_registry.py

Publishes the component registry as a gist for remote discovery.

**Usage:**

```bash
uv run scripts/publish_registry.py [options]
```

**Options:**

| Option | Description |
|--------|-------------|
| `--public` | Make registry gist public |
| `--update` | Update existing registry gist |

**Examples:**

```bash
# Publish new registry
uv run scripts/publish_registry.py --public

# Update existing registry
uv run scripts/publish_registry.py --update
```

**What It Does:**

1. Reads `.gist-registry.json`
2. Creates/updates Gist with registry content
3. Saves gist URL to `.gist-registry-url`
4. Prints remote usage instructions

## Registry System

### .gist-registry.json

The registry tracks all published components:

```json
{
  "version": "1.0.0",
  "description": "Registry of components published to GitHub Gists",
  "components": {
    "agents/development/code-reviewer.md": {
      "name": "code-reviewer",
      "type": "agent",
      "domain": "development",
      "path": "agents/development/code-reviewer.md",
      "gist_url": "https://gist.github.com/user/abc123",
      "gist_id": "abc123",
      "description": "Reviews code for quality issues",
      "tools": "Read, Grep, Glob",
      "model": "sonnet",
      "published_at": "2025-01-15T10:30:00Z",
      "updated_at": "2025-01-15T10:30:00Z"
    }
  }
}
```

### Registry Fields

| Field | Description |
|-------|-------------|
| `name` | Component name from frontmatter |
| `type` | Component type: agent, skill, command, hook |
| `domain` | Subdirectory/category |
| `path` | Relative path in repository |
| `gist_url` | Published gist URL |
| `gist_id` | Gist ID for API operations |
| `description` | Component description |
| `tools` | (Agents) Available tools |
| `model` | (Agents) Model specification |
| `published_at` | Initial publication timestamp |
| `updated_at` | Last update timestamp |

### Publishing the Registry

After publishing components, publish the registry for remote access:

```bash
# Initial publication
uv run scripts/publish_registry.py --public

# After adding new components
uv run scripts/publish_registry.py --update
```

## Installation Methods

### From Gist URL

Install a component directly from its gist URL:

```bash
uv run scripts/install_from_gist.py https://gist.github.com/user/abc123
```

The script auto-detects component type and installs to the correct location.

**With Custom Path:**

```bash
uv run scripts/install_from_gist.py https://gist.github.com/user/abc123 \
    --target-path steve/agents/custom/my-agent.md
```

### From Registry

Use the registry for component discovery and installation:

```bash
# List available components
uv run scripts/list_components.py --from-registry --registry-url <registry-gist-url>

# Install by name
uv run scripts/install_component.py code-reviewer --from-registry --registry-url <registry-gist-url>
```

### Direct Copy

For local installation without gists:

```bash
# Copy agent to Claude config
cp steve/agents/domain/my-agent.md ~/.claude/agents/

# Copy skill with references
cp -r steve/skills/my-skill/ ~/.claude/skills/

# Copy command
cp steve/commands/category/my-command.md ~/.claude/commands/category/
```

## Gist Visibility

### Private Gists (Default)

- Only accessible to creator
- Require authentication to access
- Ideal for personal or team components

```bash
uv run scripts/publish_to_gist.py component.md
```

### Public Gists

- Accessible to anyone
- Discoverable via GitHub
- Ideal for community sharing

```bash
uv run scripts/publish_to_gist.py component.md --public
```

### Changing Visibility

Gist visibility cannot be changed after creation. To make a private gist public:

1. Delete the private gist on GitHub
2. Remove `gist_url` from component frontmatter
3. Republish with `--public` flag

## Updating Published Components

### Update Workflow

```bash
# 1. Make changes to component
vim steve/agents/domain/my-agent.md

# 2. Run quality checks
uv run scripts/detect_secrets.py --scan

# 3. Update gist
uv run scripts/publish_to_gist.py steve/agents/domain/my-agent.md --update

# 4. Update registry
uv run scripts/publish_registry.py --update
```

### What Gets Updated

- Gist content is replaced
- Component `updated_at` timestamp changes
- Registry entry is updated
- Gist revision history preserved

### Version History

GitHub Gists maintain revision history automatically. Users can:

- View all revisions on gist page
- Compare changes between versions
- Access specific revision URLs

## Batch Publishing

### Publish All Agents

```bash
for f in steve/agents/**/*.md; do
    uv run scripts/publish_to_gist.py "$f" --public
done
```

### Publish by Type

```bash
# All skills
for f in steve/skills/*/SKILL.md; do
    uv run scripts/publish_to_gist.py "$f"
done

# All commands
for f in steve/commands/**/*.md; do
    uv run scripts/publish_to_gist.py "$f"
done
```

### Update All

```bash
for f in steve/agents/**/*.md steve/skills/*/SKILL.md steve/commands/**/*.md; do
    uv run scripts/publish_to_gist.py "$f" --update
done

uv run scripts/publish_registry.py --update
```

## Frontmatter Updates

Publishing adds `gist_url` to component frontmatter:

**Before:**

```yaml
---
name: code-reviewer
description: Reviews code for quality issues
tools: Read, Grep, Glob
---
```

**After:**

```yaml
---
name: code-reviewer
description: Reviews code for quality issues
tools: Read, Grep, Glob
gist_url: https://gist.github.com/user/abc123def456
---
```

## Troubleshooting

### Authentication Errors

```text
Error: GITHUB_TOKEN not found
```

**Solution:** Set token via environment variable or git config.

### Rate Limiting

```text
Error: 403 rate limit exceeded
```

**Solution:** Wait for rate limit reset or use authenticated requests.

### Gist Not Found

```text
Error: 404 Not Found
```

**Causes:**

- Gist was deleted
- Wrong gist ID in URL
- Private gist accessed without auth

**Solution:** Republish or check URL.

### Registry Out of Sync

If registry doesn't match published gists:

```bash
# Rebuild index
uv run scripts/build_index.py

# Republish registry
uv run scripts/publish_registry.py --update
```

## Best Practices

### Before Publishing

1. **Test component locally** - Verify it works correctly
2. **Run security scan** - No secrets in content
3. **Check description** - Clear and accurate
4. **Verify frontmatter** - All required fields present

### Naming and Organization

- Use descriptive names that indicate purpose
- Place in appropriate domain/category directory
- Follow naming conventions (kebab-case)

### Documentation

- Include usage examples in component
- Document any dependencies
- Note required tools or skills

### Maintenance

- Update gists when components change
- Keep registry in sync
- Respond to user feedback

## Sharing Components

### Sharing a Single Component

1. Publish to gist
2. Share the gist URL
3. Recipient installs with `install_from_gist.py`

### Sharing Multiple Components

1. Publish all components
2. Publish registry
3. Share registry gist URL
4. Recipients browse and install from registry

### Community Distribution

For public distribution:

1. Publish all components as public gists
2. Publish registry as public gist
3. Document in README
4. Share registry URL in community channels

## See Also

- [Installation Guide](INSTALLATION.md) - Installing components
- [Scripts Reference](SCRIPTS_REFERENCE.md) - Script API details
- [Contributing Guide](CONTRIBUTING.md) - Contribution workflow
- [Development Guide](DEVELOPMENT.md) - Creating components
