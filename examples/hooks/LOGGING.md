# Centralized Hook Logging System

## Overview

All hooks use a centralized structured logging system that writes to a single JSONL log file per day. This provides consistent, queryable logs across all hook executions.

## Log Location

**Central Log Sink:** `~/logs/claude-code/hook_logs/hooks_YYYYMMDD.jsonl`

- One file per day (rotates automatically at midnight)
- Override with `CLAUDE_HOOK_LOG_DIR` environment variable
- JSONL format (one JSON object per line)

## Log Types

### 1. Hook Invocation Logs (Automatic)

Automatically logged by the `hook_invocation()` context manager:

```python
from hook_logging import hook_invocation

with hook_invocation("my_hook_name") as inv:
    inv.set_payload(payload)
    # Your hook logic here
```

**Log fields:**
- `timestamp`: ISO 8601 timestamp
- `hook_name`: Name of the hook
- `pid`: Process ID
- `session_id`: Claude session ID (or PID if not available)
- `duration_ms`: Execution time in milliseconds
- `exit_code`: Exit code (0 for success)
- `ok`: Boolean success flag
- `tool_name`: Tool being used (if applicable)
- `cwd`: Working directory
- `error_type`: Exception type (if error occurred)
- `error`: Error message (if error occurred)

### 2. Structured Error Logs

For explicit error logging in hook code:

```python
from hook_logging import log_error

log_error(
    "Failed to validate input",
    hook_name="my_hook",
    error=exception_obj,  # Optional
    context={"file_path": path, "validation_rule": rule}  # Optional
)
```

**Log fields:**
- `timestamp`: ISO 8601 timestamp
- `level`: "ERROR"
- `hook_name`: Name of the hook
- `message`: Human-readable error message
- `pid`: Process ID
- `session_id`: Claude session ID
- `error_type`: Exception type (if error provided)
- `error`: Error message (if error provided)
- `context`: Additional context dict (if provided)

### 3. Structured Info Logs

For informational logging:

```python
from hook_logging import log_info

log_info(
    "Successfully validated 15 files",
    hook_name="my_hook",
    context={"file_count": 15, "validation_time_ms": 234}
)
```

**Log fields:**
- `timestamp`: ISO 8601 timestamp
- `level`: "INFO"
- `hook_name`: Name of the hook
- `message`: Human-readable message
- `pid`: Process ID
- `session_id`: Claude session ID
- `context`: Additional context dict (if provided)

## Usage in Hooks

### Basic Hook with Structured Logging

```python
#!/usr/bin/env python3
import claude_hooks
from hook_logging import log_error, log_info

def handler(payload: claude_hooks.HookPayload) -> claude_hooks.HookResponse:
    hook_name = "my_validation_hook"

    try:
        # Your validation logic
        if not validate(payload.tool_input):
            log_error(
                "Validation failed",
                hook_name=hook_name,
                context={"tool": payload.tool_name}
            )
            return claude_hooks.HookResponse(
                allow=False,
                reason="Validation failed"
            )

        log_info(
            "Validation succeeded",
            hook_name=hook_name,
            context={"tool": payload.tool_name}
        )
        return claude_hooks.HookResponse(allow=True)

    except Exception as e:
        log_error(
            "Unexpected error in validation",
            hook_name=hook_name,
            error=e
        )
        return claude_hooks.HookResponse(allow=True)  # Fail open

if __name__ == "__main__":
    claude_hooks.run(handler)
```

### Hook with Invocation Tracking

```python
#!/usr/bin/env python3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from hook_logging import hook_invocation
import claude_hooks

def handler(payload: claude_hooks.HookPayload) -> claude_hooks.HookResponse:
    # Your logic here
    return claude_hooks.HookResponse(allow=True)

if __name__ == "__main__":
    with hook_invocation("my_hook_name") as inv:
        inv.set_payload({"tool_name": "Write", "cwd": "/path"})
        claude_hooks.run(handler)
```

## Querying Logs

### View today's logs

```bash
cat ~/logs/claude-code/hook_logs/hooks_$(date +%Y%m%d).jsonl
```

### Find all errors

```bash
grep '"level":"ERROR"' ~/logs/claude-code/hook_logs/hooks_*.jsonl
```

### Find errors from specific hook

```bash
jq 'select(.hook_name == "secret_scanner" and .ok == false)' \
  ~/logs/claude-code/hook_logs/hooks_*.jsonl
```

### Analyze hook performance

```bash
jq 'select(.hook_name == "lint_changed") | {duration_ms, ok}' \
  ~/logs/claude-code/hook_logs/hooks_*.jsonl
```

### Session-based analysis

```bash
# All logs from a specific session
jq --arg sid "abc123" 'select(.session_id == $sid)' \
  ~/logs/claude-code/hook_logs/hooks_*.jsonl
```

## Stderr Breadcrumbs

In addition to JSONL logs, the system writes short breadcrumb messages to stderr for immediate visibility:

**Hook invocation breadcrumbs:**
```
[HookLog] hook=secret_scanner tool=Write file=/path/to/file.py ok dur_ms=12 exit=0
```

**Error breadcrumbs:**
```
[HookError] hook=my_hook msg=Validation failed error=ValueError
```

These are visible in real-time during hook execution without needing to read log files.

## Best Practices

1. **Always include hook_name**: Makes logs searchable and identifiable
2. **Use context for structured data**: Better than embedding data in message strings
3. **Log errors with exceptions**: Include the exception object for full stack trace
4. **Fail open on errors**: Hooks should allow operations to proceed on unexpected errors
5. **Keep messages concise**: Long messages are truncated; use context for details
6. **Use INFO sparingly**: Only log significant events to avoid noise

## Error Handling

The logging system is designed to **never break hook execution**:

- All logging operations are wrapped in try/except
- Failed log writes are silently ignored
- Hooks continue executing even if logging fails
- Fallback stderr output if logging module unavailable

This ensures hooks remain reliable even if the logging infrastructure has issues.
