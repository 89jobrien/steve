---
status: DEPRECATED
deprecated_in: "2026-01-20"
---
# n8n CLI Commands Reference

This document provides a comprehensive reference for n8n command-line interface operations, including official n8n CLI commands and third-party tools.

## Official n8n CLI Commands

The n8n CLI is built into the n8n application and provides commands for workflow management, credential handling, and instance administration.

### Running CLI Commands

**Local Installation:**

```bash
n8n <command> [options]
```

**Docker:**

```bash
docker exec -u node -it <n8n-container-name> n8n <command> [options]
```

**Docker Compose:**

```bash
docker compose exec n8n n8n <command> [options]
```

### Workflow Management

#### Export Workflows

Export workflows to JSON files for backup, version control, or migration.

```bash
# Export single workflow by ID
n8n export:workflow --id=<workflow_id> --output=workflow.json

# Export all workflows to separate files
n8n export:workflow --backup --output=backups/latest/

# Export all workflows to a single file
n8n export:workflow --all --output=all_workflows.json

# Export workflow without credential data
n8n export:workflow --id=<workflow_id> --output=workflow.json --decrypted
```

**Options:**

| Option | Description |
|--------|-------------|
| `--id` | Workflow ID to export |
| `--all` | Export all workflows |
| `--backup` | Export as separate files (one per workflow) |
| `--output` | Output file or directory path |
| `--decrypted` | Export without encrypted credential data |

#### Import Workflows

Import workflows from JSON files.

```bash
# Import single workflow
n8n import:workflow --input=workflow.json

# Import multiple workflows from separate files
n8n import:workflow --separate --input=backups/latest/

# Import with credential updates
n8n import:workflow --input=workflow.json --userId=<user_id>
```

**Options:**

| Option | Description |
|--------|-------------|
| `--input` | Input file or directory path |
| `--separate` | Import from separate files in directory |
| `--userId` | User ID to assign workflows to |

#### Execute Workflows

Execute a workflow directly from the command line.

```bash
# Execute workflow by ID
n8n execute --id=<workflow_id>

# Execute with input data
n8n execute --id=<workflow_id> --rawInput='{"key": "value"}'

# Execute from file
n8n execute --file=workflow.json
```

**Options:**

| Option | Description |
|--------|-------------|
| `--id` | Workflow ID to execute |
| `--file` | Execute workflow from JSON file |
| `--rawInput` | JSON string to pass as input data |

#### Update Workflow Status

Activate or deactivate workflows.

```bash
# Deactivate a specific workflow
n8n update:workflow --id=<workflow_id> --active=false

# Activate a specific workflow
n8n update:workflow --id=<workflow_id> --active=true

# Activate all workflows
n8n update:workflow --all --active=true

# Deactivate all workflows
n8n update:workflow --all --active=false
```

### Credential Management

#### Export Credentials

```bash
# Export all credentials
n8n export:credentials --backup --output=credentials/

# Export specific credential by ID
n8n export:credentials --id=<credential_id> --output=credential.json

# Export decrypted credentials (requires ENCRYPTION_KEY)
n8n export:credentials --backup --output=credentials/ --decrypted
```

#### Import Credentials

```bash
# Import credentials
n8n import:credentials --input=credentials/

# Import with user assignment
n8n import:credentials --input=credentials/ --userId=<user_id>
```

### User Management

```bash
# Reset user password
n8n user-management:reset

# List users (when using user management)
n8n user-management:list
```

### Database Operations

```bash
# Run database migrations
n8n db:revert

# Check database status
n8n db:check
```

### Instance Information

```bash
# Get n8n version
n8n --version

# Get help
n8n --help

# Get help for specific command
n8n export:workflow --help
```

## Third-Party CLI Tool: n8n-cli

The [n8n-cli](https://github.com/edenreich/n8n-cli) is a community-developed tool for managing n8n workflows via the API.

### Installation

```bash
# Using curl (Linux/macOS)
curl -sSLf https://raw.github.com/edenreich/n8n-cli/main/install.sh | sh

# Using Homebrew
brew install edenreich/tap/n8n-cli

# Using Go
go install github.com/edenreich/n8n-cli@latest
```

### Configuration

```bash
# Set n8n instance URL
export N8N_BASE_URL=http://localhost:5678

# Set API key
export N8N_API_KEY=your-api-key
```

Or create a config file at `~/.n8n-cli.yaml`:

```yaml
base_url: http://localhost:5678
api_key: your-api-key
```

### Workflow Commands

```bash
# List all workflows
n8n workflows list

# Get workflow details
n8n workflows get <workflow_id>

# Sync workflows to local directory
n8n workflows sync --directory workflows/

# Refresh workflows from n8n to local directory
n8n workflows refresh --directory workflows/

# Push local workflows to n8n
n8n workflows push --directory workflows/

# Activate workflow
n8n workflows activate <workflow_id>

# Deactivate workflow
n8n workflows deactivate <workflow_id>

# Delete workflow
n8n workflows delete <workflow_id>
```

### Execution Commands

```bash
# List executions
n8n executions list

# Get execution details
n8n executions get <execution_id>

# Delete execution
n8n executions delete <execution_id>
```

## Common Patterns

### Backup Workflow

Create a backup script for n8n workflows:

```bash
#!/bin/bash
# backup-n8n.sh

BACKUP_DIR="backups/$(date +%Y-%m-%d)"
mkdir -p "$BACKUP_DIR"

# Export all workflows
n8n export:workflow --backup --output="$BACKUP_DIR/workflows/"

# Export all credentials (encrypted)
n8n export:credentials --backup --output="$BACKUP_DIR/credentials/"

echo "Backup completed to $BACKUP_DIR"
```

### CI/CD Integration

Deploy workflows from version control:

```bash
#!/bin/bash
# deploy-workflows.sh

# Deactivate all workflows before import
n8n update:workflow --all --active=false

# Import workflows from repository
n8n import:workflow --separate --input=workflows/

# Reactivate required workflows
n8n update:workflow --id=<workflow_id> --active=true

echo "Deployment completed"
```

### Development Workflow

Sync workflows between local development and n8n:

```bash
# Export workflow after editing in n8n UI
n8n export:workflow --id=<workflow_id> --output=nathan/workflows/jira/my-workflow.json

# Import workflow after editing JSON locally
n8n import:workflow --input=nathan/workflows/jira/my-workflow.json
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `N8N_HOST` | n8n instance hostname | localhost |
| `N8N_PORT` | n8n instance port | 5678 |
| `N8N_PROTOCOL` | HTTP or HTTPS | http |
| `N8N_API_KEY` | API key for authentication | - |
| `ENCRYPTION_KEY` | Key for credential encryption | - |
| `N8N_USER_FOLDER` | Path to n8n user data | ~/.n8n |

## Troubleshooting

### Common Issues

**Permission denied when running CLI in Docker:**

```bash
# Use the node user
docker exec -u node -it n8n n8n <command>
```

**Workflow import fails with credential errors:**

Exported workflows reference credentials by ID. After import, you may need to:

1. Re-create credentials in the target n8n instance
2. Update workflow nodes to use the new credential IDs
3. Or use the `--decrypted` flag and ensure the same `ENCRYPTION_KEY`

**Workflow not found:**

Ensure you're using the correct workflow ID (numeric ID, not the name):

```bash
# List workflows to get IDs
n8n export:workflow --all --output=/dev/stdout | jq '.[] | {id, name}'
```

## Related Documentation

- [Official n8n CLI Documentation](https://docs.n8n.io/hosting/cli-commands/)
- [n8n REST API Reference](./rest_api.md)
- [Workflow JSON Structure](./workflow_json_structure.md)
