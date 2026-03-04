---
status: DEPRECATED
deprecated_in: "2026-01-20"
---
# Common n8n Development Patterns

## Workflow Registry Pattern

### Basic Usage

```python
from nathan.core.workflow_registry import N8NWorkflowRegistry, trigger_n8n_workflow

# List available workflows
registry = N8NWorkflowRegistry()
workflows = registry.list_all()

# Trigger a workflow
result = await trigger_n8n_workflow(
    workflow_url="http://localhost:5678/webhook/get-jira-ticket",
    parameters={"ticket_id": "PROJ-123"},
    shared_secret="your-secret",
)

if result.success:
    print(result.data)
else:
    print(f"Error: {result.error}")
```

### Registry Configuration

```yaml
# workflow_registry.yaml
workflows:
  - id: get-jira-ticket
    name: Get Jira Ticket
    webhook_path: /webhook/get-jira-ticket
    description: Fetch ticket details from Jira
    parameters:
      - name: ticket_id
        type: string
        required: true
        description: Jira ticket ID (e.g., PROJ-123)
```

## Template Rendering Pattern

### Basic Template Rendering

```python
from nathan.templating.api import render_template

rendered = render_template(
    template_path="templates/flows/jira-workflow.yaml",
    variables={"project_key": "PROJ", "issue_type": "Task"},
)

with open("output.json", "w") as f:
    f.write(rendered)
```

### Template with Validation

```python
from nathan.templating.api import render_template, validate_template

# Validate before rendering
is_valid = validate_template(
    template_path="templates/flows/jira-workflow.yaml",
    variables={"project_key": "PROJ", "issue_type": "Task"},
)

if is_valid:
    rendered = render_template(
        template_path="templates/flows/jira-workflow.yaml",
        variables={"project_key": "PROJ", "issue_type": "Task"},
    )
```

## Error Handling Patterns

### Comprehensive Error Handling

```python
from nathan.templating.exceptions import ValidationError, TemplateError
from nathan.core.exceptions import WorkflowExecutionError
import httpx

async def execute_workflow_safely(url: str, params: dict, secret: str):
    """Execute workflow with proper error handling."""
    try:
        result = await trigger_n8n_workflow(url, params, secret)
        if not result.success:
            raise WorkflowExecutionError(
                f"Workflow failed: {result.error}",
                status_code=result.status_code
            )
        return result.data
    except httpx.TimeoutException:
        logger.error(f"Workflow timed out: {url}")
        raise WorkflowExecutionError("Workflow execution timed out")
    except httpx.RequestError as e:
        logger.error(f"HTTP request failed: {e}")
        raise WorkflowExecutionError(f"HTTP request failed: {str(e)}")
    except ValidationError as e:
        logger.error(f"Validation failed: {e}")
        raise
```

### Retry Pattern with Exponential Backoff

```python
import asyncio
from typing import Optional

async def execute_with_retry(
    url: str,
    params: dict,
    secret: str,
    max_retries: int = 3,
    base_delay: float = 1.0,
) -> Optional[dict]:
    """Execute workflow with exponential backoff retry."""
    for attempt in range(max_retries):
        try:
            result = await trigger_n8n_workflow(url, params, secret)
            if result.success:
                return result.data

            # Don't retry on client errors (4xx)
            if 400 <= result.status_code < 500:
                raise WorkflowExecutionError(f"Client error: {result.error}")

        except httpx.TimeoutException:
            if attempt == max_retries - 1:
                raise

        # Exponential backoff
        delay = base_delay * (2 ** attempt)
        await asyncio.sleep(delay)

    return None
```

## Testing Patterns

### Mocking HTTP Calls

```python
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_trigger_workflow_success():
    """Test successful workflow trigger."""
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"success": True, "data": {"id": "123"}}

    with patch("httpx.AsyncClient.post", return_value=mock_response):
        result = await trigger_n8n_workflow(
            "http://localhost:5678/webhook/test",
            {"param": "value"},
            "secret"
        )

        assert result.success
        assert result.data["id"] == "123"
```

### Testing with Fixtures

```python
import pytest
from nathan.core.workflow_registry import N8NWorkflowRegistry

@pytest.fixture
def registry():
    """Provide a workflow registry instance."""
    return N8NWorkflowRegistry(config_path="tests/fixtures/test_registry.yaml")

@pytest.fixture
def mock_n8n_server():
    """Mock n8n server responses."""
    with patch("httpx.AsyncClient") as mock_client:
        mock_instance = AsyncMock()
        mock_client.return_value = mock_instance
        yield mock_instance

@pytest.mark.asyncio
async def test_list_workflows(registry):
    """Test listing available workflows."""
    workflows = registry.list_all()
    assert len(workflows) > 0
    assert all(w.id for w in workflows)
```

## Async Patterns

### Parallel Workflow Execution

```python
import asyncio
from typing import List, Dict

async def execute_parallel_workflows(
    workflows: List[Dict[str, any]],
    shared_secret: str
) -> List[dict]:
    """Execute multiple workflows in parallel."""
    tasks = [
        trigger_n8n_workflow(
            workflow["url"],
            workflow["params"],
            shared_secret
        )
        for workflow in workflows
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Process results
    successful_results = []
    for result in results:
        if isinstance(result, Exception):
            logger.error(f"Workflow failed: {result}")
        elif result.success:
            successful_results.append(result.data)
        else:
            logger.error(f"Workflow error: {result.error}")

    return successful_results
```

### Context Manager for HTTP Client

```python
import httpx
from contextlib import asynccontextmanager

@asynccontextmanager
async def n8n_client(base_url: str, timeout: float = 30.0):
    """Context manager for n8n HTTP client."""
    async with httpx.AsyncClient(
        base_url=base_url,
        timeout=httpx.Timeout(timeout),
        headers={"Content-Type": "application/json"}
    ) as client:
        yield client

# Usage
async def fetch_workflow_status(workflow_id: str):
    async with n8n_client("http://localhost:5678") as client:
        response = await client.get(f"/workflow/{workflow_id}")
        return response.json()
```

## Pydantic Models

### Request/Response Models

```python
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime

class WorkflowRequest(BaseModel):
    """Request model for workflow execution."""
    workflow_id: str = Field(..., description="Workflow identifier")
    parameters: Dict[str, Any] = Field(default_factory=dict)
    timeout: Optional[int] = Field(30, ge=1, le=300)

    @validator("workflow_id")
    def validate_workflow_id(cls, v):
        if not v or not v.strip():
            raise ValueError("workflow_id cannot be empty")
        return v.strip()

class WorkflowResponse(BaseModel):
    """Response model for workflow execution."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    status_code: int = 200
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
```

### Template Models

```python
from pydantic import BaseModel, Field
from typing import List, Dict, Any

class TemplateVariable(BaseModel):
    """Template variable definition."""
    name: str
    type: str = Field(..., regex="^(string|number|boolean|array|object)$")
    required: bool = True
    default: Optional[Any] = None
    description: Optional[str] = None

class TemplateSchema(BaseModel):
    """Template schema definition."""
    variables: List[TemplateVariable]
    version: str = "1.0.0"
    description: Optional[str] = None

    def validate_variables(self, provided: Dict[str, Any]) -> bool:
        """Validate provided variables against schema."""
        for var in self.variables:
            if var.required and var.name not in provided:
                raise ValidationError(f"Required variable '{var.name}' not provided")

            if var.name in provided:
                # Type validation logic here
                pass

        return True
```

## CLI Integration

### Click Command Pattern

```python
import click
from pathlib import Path

@click.command()
@click.argument("template_path", type=click.Path(exists=True))
@click.option("--variables", "-v", multiple=True, help="Variables as key=value")
@click.option("--output", "-o", type=click.Path(), help="Output file path")
def render(template_path: str, variables: tuple, output: str):
    """Render an n8n workflow template."""
    # Parse variables
    vars_dict = {}
    for var in variables:
        key, value = var.split("=", 1)
        vars_dict[key] = value

    # Render template
    try:
        rendered = render_template(template_path, vars_dict)

        if output:
            Path(output).write_text(rendered)
            click.echo(f"Template rendered to {output}")
        else:
            click.echo(rendered)
    except ValidationError as e:
        click.echo(f"Validation error: {e}", err=True)
        raise click.Exit(1)
```

## Integration Testing

### Testing n8n Workflows

```python
import pytest
import docker
from pathlib import Path

@pytest.fixture(scope="session")
def n8n_container():
    """Start n8n container for integration tests."""
    client = docker.from_env()

    # Start n8n container
    container = client.containers.run(
        "n8nio/n8n",
        ports={"5678/tcp": 5678},
        environment={
            "N8N_BASIC_AUTH_ACTIVE": "false",
            "N8N_HOST": "localhost",
        },
        detach=True,
        remove=True,
    )

    # Wait for n8n to be ready
    import time
    time.sleep(10)

    yield container

    # Cleanup
    container.stop()

@pytest.mark.integration
async def test_workflow_execution(n8n_container):
    """Test actual workflow execution."""
    result = await trigger_n8n_workflow(
        "http://localhost:5678/webhook/test",
        {"message": "test"},
        "test-secret"
    )

    assert result.success
    assert result.data["message"] == "test"
```