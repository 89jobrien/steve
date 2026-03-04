---
status: DEPRECATED
deprecated_in: "2026-01-20"
---
# n8n Workflow JSON Structure Reference

This document provides a comprehensive reference for the n8n workflow JSON format, essential for programmatic workflow creation, export/import operations, and version control.

## JSON Structure Overview

An n8n workflow JSON file contains four main components:

```json
{
  "name": "Workflow Name",
  "nodes": [],
  "connections": {},
  "settings": {},
  "staticData": null,
  "tags": [],
  "meta": {}
}
```

## Top-Level Properties

| Property | Type | Description |
|----------|------|-------------|
| `name` | string | Workflow display name |
| `nodes` | array | List of node configurations |
| `connections` | object | Node connection mappings |
| `settings` | object | Workflow-level settings |
| `staticData` | object/null | Persistent data across executions |
| `tags` | array | Tag references (IDs) |
| `meta` | object | Metadata (template info, etc.) |
| `active` | boolean | Whether workflow is active (API response only) |
| `id` | string | Workflow ID (API response only) |
| `createdAt` | string | Creation timestamp (API response only) |
| `updatedAt` | string | Last update timestamp (API response only) |

## Nodes Array

Each node in the `nodes` array has this structure:

```json
{
  "id": "unique-node-id",
  "name": "Node Display Name",
  "type": "n8n-nodes-base.httpRequest",
  "typeVersion": 4.2,
  "position": [250, 300],
  "parameters": {},
  "credentials": {},
  "disabled": false,
  "notesInFlow": false,
  "notes": ""
}
```

### Node Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `id` | string | Yes | Unique identifier (UUID format recommended) |
| `name` | string | Yes | Display name (must be unique in workflow) |
| `type` | string | Yes | Node type identifier |
| `typeVersion` | number | Yes | Version of the node type |
| `position` | [x, y] | Yes | Canvas position coordinates |
| `parameters` | object | Yes | Node-specific configuration |
| `credentials` | object | No | Credential references |
| `disabled` | boolean | No | Whether node is disabled |
| `notesInFlow` | boolean | No | Show notes on canvas |
| `notes` | string | No | Node notes/documentation |

### Common Node Types

```text
Triggers:
- n8n-nodes-base.webhook
- n8n-nodes-base.scheduleTrigger
- n8n-nodes-base.manualTrigger

Core:
- n8n-nodes-base.httpRequest
- n8n-nodes-base.code
- n8n-nodes-base.set
- n8n-nodes-base.if
- n8n-nodes-base.switch
- n8n-nodes-base.merge
- n8n-nodes-base.splitInBatches
- n8n-nodes-base.respondToWebhook

Integrations:
- n8n-nodes-base.jira
- n8n-nodes-base.slack
- n8n-nodes-base.googleSheets
- n8n-nodes-base.airtable
```

### Node Examples

#### Webhook Node

```json
{
  "id": "webhook-1",
  "name": "Webhook",
  "type": "n8n-nodes-base.webhook",
  "typeVersion": 2,
  "position": [250, 300],
  "webhookId": "abc-123-def",
  "parameters": {
    "path": "get-jira-ticket",
    "httpMethod": "POST",
    "responseMode": "responseNode",
    "options": {
      "rawBody": false
    }
  }
}
```

#### HTTP Request Node

```json
{
  "id": "http-request-1",
  "name": "HTTP Request",
  "type": "n8n-nodes-base.httpRequest",
  "typeVersion": 4.2,
  "position": [450, 300],
  "parameters": {
    "method": "GET",
    "url": "https://api.example.com/data",
    "authentication": "genericCredentialType",
    "genericAuthType": "httpHeaderAuth",
    "sendHeaders": true,
    "headerParameters": {
      "parameters": [
        {
          "name": "Accept",
          "value": "application/json"
        }
      ]
    },
    "options": {
      "timeout": 30000,
      "response": {
        "response": {
          "responseFormat": "json"
        }
      }
    }
  },
  "credentials": {
    "httpHeaderAuth": {
      "id": "1",
      "name": "My API Key"
    }
  }
}
```

#### Jira Node

```json
{
  "id": "jira-1",
  "name": "Jira",
  "type": "n8n-nodes-base.jira",
  "typeVersion": 1,
  "position": [450, 300],
  "parameters": {
    "resource": "issue",
    "operation": "get",
    "issueKey": "={{ $json.ticket_id }}"
  },
  "credentials": {
    "jiraSoftwareCloudApi": {
      "id": "2",
      "name": "Jira Credentials"
    }
  }
}
```

#### Code Node

```json
{
  "id": "code-1",
  "name": "Transform Data",
  "type": "n8n-nodes-base.code",
  "typeVersion": 2,
  "position": [650, 300],
  "parameters": {
    "jsCode": "const items = $input.all();\n\nreturn items.map(item => {\n  return {\n    json: {\n      processed: true,\n      data: item.json\n    }\n  };\n});"
  }
}
```

#### Respond to Webhook Node

```json
{
  "id": "respond-1",
  "name": "Respond to Webhook",
  "type": "n8n-nodes-base.respondToWebhook",
  "typeVersion": 1.1,
  "position": [850, 300],
  "parameters": {
    "respondWith": "json",
    "responseBody": "={{ $json }}",
    "options": {
      "responseCode": 200,
      "responseHeaders": {
        "entries": [
          {
            "name": "Content-Type",
            "value": "application/json"
          }
        ]
      }
    }
  }
}
```

#### IF Node

```json
{
  "id": "if-1",
  "name": "Check Condition",
  "type": "n8n-nodes-base.if",
  "typeVersion": 2,
  "position": [450, 300],
  "parameters": {
    "conditions": {
      "options": {
        "caseSensitive": true,
        "leftValue": "",
        "typeValidation": "strict"
      },
      "conditions": [
        {
          "id": "condition-1",
          "leftValue": "={{ $json.status }}",
          "rightValue": "active",
          "operator": {
            "type": "string",
            "operation": "equals"
          }
        }
      ],
      "combinator": "and"
    },
    "options": {}
  }
}
```

## Connections Object

The `connections` object maps node outputs to inputs:

```json
{
  "connections": {
    "Webhook": {
      "main": [
        [
          {
            "node": "Jira",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Jira": {
      "main": [
        [
          {
            "node": "Respond to Webhook",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  }
}
```

### Connection Structure

```json
{
  "Source Node Name": {
    "main": [
      [
        {
          "node": "Target Node Name",
          "type": "main",
          "index": 0
        }
      ]
    ]
  }
}
```

- **Key**: Source node's display name
- **main**: Array of output ports (index 0 = first output)
- **node**: Target node's display name
- **type**: Connection type (usually "main")
- **index**: Target input port index

### Multiple Outputs (IF Node)

```json
{
  "Check Condition": {
    "main": [
      [
        {
          "node": "True Branch",
          "type": "main",
          "index": 0
        }
      ],
      [
        {
          "node": "False Branch",
          "type": "main",
          "index": 0
        }
      ]
    ]
  }
}
```

### Multiple Connections from Same Output

```json
{
  "Webhook": {
    "main": [
      [
        {
          "node": "Process A",
          "type": "main",
          "index": 0
        },
        {
          "node": "Process B",
          "type": "main",
          "index": 0
        }
      ]
    ]
  }
}
```

## Settings Object

```json
{
  "settings": {
    "executionOrder": "v1",
    "saveManualExecutions": true,
    "callerPolicy": "workflowsFromSameOwner",
    "errorWorkflow": "error-handler-workflow-id",
    "timezone": "America/New_York",
    "executionTimeout": 3600
  }
}
```

### Settings Properties

| Property | Type | Description |
|----------|------|-------------|
| `executionOrder` | string | "v0" (legacy) or "v1" (recommended) |
| `saveManualExecutions` | boolean | Save manual test runs |
| `callerPolicy` | string | Who can call this workflow |
| `errorWorkflow` | string | ID of error handling workflow |
| `timezone` | string | Timezone for scheduled triggers |
| `executionTimeout` | number | Timeout in seconds |

## Static Data

The `staticData` property stores persistent data across executions:

```json
{
  "staticData": {
    "lastProcessedId": "12345",
    "counter": 42,
    "cache": {
      "key1": "value1"
    }
  }
}
```

## Expressions

n8n uses expressions for dynamic values, wrapped in `={{ }}`:

```json
{
  "parameters": {
    "url": "https://api.example.com/users/{{ $json.userId }}",
    "body": "={{ JSON.stringify($json.data) }}",
    "headers": {
      "Authorization": "Bearer {{ $env.API_TOKEN }}"
    }
  }
}
```

### Expression Variables

| Variable | Description |
|----------|-------------|
| `$json` | Current item's JSON data |
| `$input` | Input data helper |
| `$node["Name"]` | Access another node's data |
| `$env` | Environment variables |
| `$execution` | Execution metadata |
| `$workflow` | Workflow metadata |
| `$today` | Current date |
| `$now` | Current timestamp |

## Complete Example

```json
{
  "name": "Get Jira Ticket",
  "nodes": [
    {
      "id": "webhook-1",
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 2,
      "position": [250, 300],
      "webhookId": "get-jira-ticket",
      "parameters": {
        "path": "get-jira-ticket",
        "httpMethod": "POST",
        "responseMode": "responseNode",
        "options": {}
      }
    },
    {
      "id": "jira-1",
      "name": "Get Issue",
      "type": "n8n-nodes-base.jira",
      "typeVersion": 1,
      "position": [450, 300],
      "parameters": {
        "resource": "issue",
        "operation": "get",
        "issueKey": "={{ $json.body.ticket_id }}"
      },
      "credentials": {
        "jiraSoftwareCloudApi": {
          "id": "1",
          "name": "Jira API"
        }
      }
    },
    {
      "id": "respond-1",
      "name": "Respond",
      "type": "n8n-nodes-base.respondToWebhook",
      "typeVersion": 1.1,
      "position": [650, 300],
      "parameters": {
        "respondWith": "json",
        "responseBody": "={{ { success: true, data: $json } }}",
        "options": {}
      }
    }
  ],
  "connections": {
    "Webhook": {
      "main": [
        [
          {
            "node": "Get Issue",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Get Issue": {
      "main": [
        [
          {
            "node": "Respond",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  },
  "settings": {
    "executionOrder": "v1"
  },
  "staticData": null
}
```

## Credential References

Credentials are referenced by ID and name, but never include actual secrets:

```json
{
  "credentials": {
    "jiraSoftwareCloudApi": {
      "id": "1",
      "name": "Jira Credentials"
    }
  }
}
```

After importing a workflow, credential references must be updated to match the target n8n instance's credential IDs.

## Validation Rules

### Node IDs

- Must be unique within the workflow
- Recommended format: UUID or descriptive slug

### Node Names

- Must be unique within the workflow
- Used in connections object as keys
- Displayed on the canvas

### Connections

- Source and target node names must exist in nodes array
- Output index must be valid for the source node type
- Input index must be valid for the target node type

### TypeVersion

- Must match a valid version for the node type
- Newer typeVersions may have different parameter schemas

## Python Workflow Builder

```python
import json
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

@dataclass
class Node:
    """n8n workflow node."""
    name: str
    type: str
    type_version: float
    position: tuple[int, int]
    parameters: Dict[str, Any] = field(default_factory=dict)
    credentials: Optional[Dict[str, Any]] = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_dict(self) -> dict:
        """Convert to n8n JSON format."""
        result = {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "typeVersion": self.type_version,
            "position": list(self.position),
            "parameters": self.parameters
        }
        if self.credentials:
            result["credentials"] = self.credentials
        return result

@dataclass
class Workflow:
    """n8n workflow builder."""
    name: str
    nodes: List[Node] = field(default_factory=list)
    connections: Dict[str, Any] = field(default_factory=dict)
    settings: Dict[str, Any] = field(
        default_factory=lambda: {"executionOrder": "v1"}
    )

    def add_node(self, node: Node) -> "Workflow":
        """Add a node to the workflow."""
        self.nodes.append(node)
        return self

    def connect(
        self,
        source: str,
        target: str,
        source_output: int = 0,
        target_input: int = 0
    ) -> "Workflow":
        """Connect two nodes."""
        if source not in self.connections:
            self.connections[source] = {"main": []}

        # Ensure enough output slots
        while len(self.connections[source]["main"]) <= source_output:
            self.connections[source]["main"].append([])

        self.connections[source]["main"][source_output].append({
            "node": target,
            "type": "main",
            "index": target_input
        })
        return self

    def to_dict(self) -> dict:
        """Convert to n8n JSON format."""
        return {
            "name": self.name,
            "nodes": [n.to_dict() for n in self.nodes],
            "connections": self.connections,
            "settings": self.settings,
            "staticData": None
        }

    def to_json(self, indent: int = 2) -> str:
        """Export as JSON string."""
        return json.dumps(self.to_dict(), indent=indent)


# Usage example
workflow = Workflow(name="Get Jira Ticket")

webhook = Node(
    name="Webhook",
    type="n8n-nodes-base.webhook",
    type_version=2,
    position=(250, 300),
    parameters={
        "path": "get-jira-ticket",
        "httpMethod": "POST",
        "responseMode": "responseNode"
    }
)

jira = Node(
    name="Get Issue",
    type="n8n-nodes-base.jira",
    type_version=1,
    position=(450, 300),
    parameters={
        "resource": "issue",
        "operation": "get",
        "issueKey": "={{ $json.body.ticket_id }}"
    },
    credentials={
        "jiraSoftwareCloudApi": {"id": "1", "name": "Jira API"}
    }
)

respond = Node(
    name="Respond",
    type="n8n-nodes-base.respondToWebhook",
    type_version=1.1,
    position=(650, 300),
    parameters={
        "respondWith": "json",
        "responseBody": "={{ { success: true, data: $json } }}"
    }
)

workflow.add_node(webhook).add_node(jira).add_node(respond)
workflow.connect("Webhook", "Get Issue")
workflow.connect("Get Issue", "Respond")

print(workflow.to_json())
```

## Related Documentation

- [n8n CLI Commands](./cli_commands.md)
- [n8n REST API](./rest_api.md)
- [Common Patterns](./common_patterns.md)
