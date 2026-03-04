---
status: DEPRECATED
deprecated_in: "2026-01-20"
---
# n8n REST API Reference

This document provides a comprehensive reference for the n8n REST API, enabling programmatic management of workflows, executions, credentials, and other n8n resources.

## API Overview

n8n provides a public REST API for performing GUI tasks programmatically. The API is available at:

```text
https://<your-n8n-instance>/api/v1/
```

### Authentication

All API requests require authentication via API key:

```bash
# Header-based authentication
curl -H "X-N8N-API-KEY: your-api-key" \
     https://your-n8n.example.com/api/v1/workflows
```

### API Key Generation

1. Open n8n UI
2. Go to **Settings** > **API**
3. Click **Create API Key**
4. Copy and securely store the key

## Workflows API

### List Workflows

```bash
GET /api/v1/workflows
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `active` | boolean | Filter by active status |
| `limit` | integer | Results per page (default: 100, max: 250) |
| `cursor` | string | Pagination cursor |
| `tags` | string | Filter by tag ID |

**Example:**

```bash
curl -H "X-N8N-API-KEY: your-api-key" \
     "https://your-n8n.example.com/api/v1/workflows?active=true&limit=10"
```

**Response:**

```json
{
  "data": [
    {
      "id": "1",
      "name": "My Workflow",
      "active": true,
      "createdAt": "2024-01-01T00:00:00.000Z",
      "updatedAt": "2024-01-02T00:00:00.000Z",
      "tags": []
    }
  ],
  "nextCursor": "eyJpZCI6IjIifQ=="
}
```

### Get Workflow

```bash
GET /api/v1/workflows/{id}
```

**Example:**

```bash
curl -H "X-N8N-API-KEY: your-api-key" \
     "https://your-n8n.example.com/api/v1/workflows/1"
```

**Response:**

```json
{
  "id": "1",
  "name": "My Workflow",
  "active": true,
  "nodes": [...],
  "connections": {...},
  "settings": {...},
  "staticData": null,
  "createdAt": "2024-01-01T00:00:00.000Z",
  "updatedAt": "2024-01-02T00:00:00.000Z"
}
```

### Create Workflow

```bash
POST /api/v1/workflows
```

**Request Body:**

```json
{
  "name": "New Workflow",
  "nodes": [
    {
      "parameters": {},
      "id": "start",
      "name": "Start",
      "type": "n8n-nodes-base.start",
      "typeVersion": 1,
      "position": [250, 300]
    }
  ],
  "connections": {},
  "settings": {
    "executionOrder": "v1"
  }
}
```

**Example:**

```bash
curl -X POST \
     -H "X-N8N-API-KEY: your-api-key" \
     -H "Content-Type: application/json" \
     -d '{"name": "New Workflow", "nodes": [...], "connections": {}}' \
     "https://your-n8n.example.com/api/v1/workflows"
```

### Update Workflow

```bash
PATCH /api/v1/workflows/{id}
```

**Request Body:**

```json
{
  "name": "Updated Workflow Name",
  "active": false
}
```

**Example:**

```bash
curl -X PATCH \
     -H "X-N8N-API-KEY: your-api-key" \
     -H "Content-Type: application/json" \
     -d '{"name": "Updated Name"}' \
     "https://your-n8n.example.com/api/v1/workflows/1"
```

### Delete Workflow

```bash
DELETE /api/v1/workflows/{id}
```

**Example:**

```bash
curl -X DELETE \
     -H "X-N8N-API-KEY: your-api-key" \
     "https://your-n8n.example.com/api/v1/workflows/1"
```

### Activate Workflow

```bash
POST /api/v1/workflows/{id}/activate
```

**Example:**

```bash
curl -X POST \
     -H "X-N8N-API-KEY: your-api-key" \
     "https://your-n8n.example.com/api/v1/workflows/1/activate"
```

### Deactivate Workflow

```bash
POST /api/v1/workflows/{id}/deactivate
```

**Example:**

```bash
curl -X POST \
     -H "X-N8N-API-KEY: your-api-key" \
     "https://your-n8n.example.com/api/v1/workflows/1/deactivate"
```

## Executions API

### List Executions

```bash
GET /api/v1/executions
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `workflowId` | string | Filter by workflow ID |
| `status` | string | Filter by status: `error`, `success`, `waiting` |
| `limit` | integer | Results per page (default: 100) |
| `cursor` | string | Pagination cursor |
| `includeData` | boolean | Include execution data (default: false) |

**Example:**

```bash
curl -H "X-N8N-API-KEY: your-api-key" \
     "https://your-n8n.example.com/api/v1/executions?workflowId=1&status=error"
```

### Get Execution

```bash
GET /api/v1/executions/{id}
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `includeData` | boolean | Include full execution data |

**Example:**

```bash
curl -H "X-N8N-API-KEY: your-api-key" \
     "https://your-n8n.example.com/api/v1/executions/123?includeData=true"
```

### Delete Execution

```bash
DELETE /api/v1/executions/{id}
```

**Example:**

```bash
curl -X DELETE \
     -H "X-N8N-API-KEY: your-api-key" \
     "https://your-n8n.example.com/api/v1/executions/123"
```

## Credentials API

### List Credentials

```bash
GET /api/v1/credentials
```

**Example:**

```bash
curl -H "X-N8N-API-KEY: your-api-key" \
     "https://your-n8n.example.com/api/v1/credentials"
```

**Response:**

```json
{
  "data": [
    {
      "id": "1",
      "name": "Jira API",
      "type": "jiraApi",
      "createdAt": "2024-01-01T00:00:00.000Z",
      "updatedAt": "2024-01-02T00:00:00.000Z"
    }
  ]
}
```

### Create Credential

```bash
POST /api/v1/credentials
```

**Request Body:**

```json
{
  "name": "My Jira Credential",
  "type": "jiraApi",
  "data": {
    "email": "user@example.com",
    "apiToken": "your-token",
    "domain": "yourcompany.atlassian.net"
  }
}
```

### Delete Credential

```bash
DELETE /api/v1/credentials/{id}
```

## Tags API

### List Tags

```bash
GET /api/v1/tags
```

### Create Tag

```bash
POST /api/v1/tags
```

**Request Body:**

```json
{
  "name": "production"
}
```

## Webhooks

### Trigger Webhook

Webhooks are not part of the REST API but are workflow-specific endpoints:

```bash
POST /webhook/{webhook-path}
```

**Example with shared secret:**

```bash
curl -X POST \
     -H "Content-Type: application/json" \
     -H "X-N8N-SECRET: your-shared-secret" \
     -d '{"ticket_id": "PROJ-123"}' \
     "https://your-n8n.example.com/webhook/get-jira-ticket"
```

### Test Webhook

For development/testing, n8n provides test webhook endpoints:

```bash
POST /webhook-test/{webhook-path}
```

Test webhooks are only active when the workflow editor is open and listening.

## Python Client Example

```python
import httpx
from typing import Optional
from dataclasses import dataclass

@dataclass
class N8NClient:
    """Client for n8n REST API."""

    base_url: str
    api_key: str
    timeout: float = 30.0

    async def list_workflows(
        self,
        active: Optional[bool] = None,
        limit: int = 100
    ) -> dict:
        """List all workflows."""
        params = {"limit": limit}
        if active is not None:
            params["active"] = str(active).lower()

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/api/v1/workflows",
                headers={"X-N8N-API-KEY": self.api_key},
                params=params
            )
            response.raise_for_status()
            return response.json()

    async def get_workflow(self, workflow_id: str) -> dict:
        """Get workflow by ID."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/api/v1/workflows/{workflow_id}",
                headers={"X-N8N-API-KEY": self.api_key}
            )
            response.raise_for_status()
            return response.json()

    async def create_workflow(self, workflow_data: dict) -> dict:
        """Create a new workflow."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/api/v1/workflows",
                headers={
                    "X-N8N-API-KEY": self.api_key,
                    "Content-Type": "application/json"
                },
                json=workflow_data
            )
            response.raise_for_status()
            return response.json()

    async def activate_workflow(self, workflow_id: str) -> dict:
        """Activate a workflow."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/api/v1/workflows/{workflow_id}/activate",
                headers={"X-N8N-API-KEY": self.api_key}
            )
            response.raise_for_status()
            return response.json()

    async def trigger_webhook(
        self,
        webhook_path: str,
        data: dict,
        shared_secret: Optional[str] = None
    ) -> dict:
        """Trigger a webhook workflow."""
        headers = {"Content-Type": "application/json"}
        if shared_secret:
            headers["X-N8N-SECRET"] = shared_secret

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/webhook/{webhook_path}",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            return response.json()


# Usage example
async def main():
    client = N8NClient(
        base_url="http://localhost:5678",
        api_key="your-api-key"
    )

    # List active workflows
    workflows = await client.list_workflows(active=True)
    print(f"Found {len(workflows['data'])} active workflows")

    # Trigger webhook
    result = await client.trigger_webhook(
        webhook_path="get-jira-ticket",
        data={"ticket_id": "PROJ-123"},
        shared_secret="your-shared-secret"
    )
    print(f"Webhook result: {result}")
```

## Error Handling

### Common HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Invalid or missing API key |
| 404 | Not Found - Resource doesn't exist |
| 500 | Internal Server Error |

### Error Response Format

```json
{
  "code": 404,
  "message": "Workflow not found",
  "hint": "The workflow with ID '123' does not exist"
}
```

## Rate Limiting

n8n does not have built-in rate limiting on the REST API, but consider implementing client-side rate limiting for production use:

```python
import asyncio
from functools import wraps

def rate_limit(calls_per_second: float = 10):
    """Rate limit decorator for async functions."""
    min_interval = 1.0 / calls_per_second
    last_call = [0.0]

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            elapsed = asyncio.get_event_loop().time() - last_call[0]
            if elapsed < min_interval:
                await asyncio.sleep(min_interval - elapsed)
            last_call[0] = asyncio.get_event_loop().time()
            return await func(*args, **kwargs)
        return wrapper
    return decorator
```

## Related Documentation

- [n8n CLI Commands](./cli_commands.md)
- [Workflow JSON Structure](./workflow_json_structure.md)
- [Official n8n API Docs](https://docs.n8n.io/api/)
