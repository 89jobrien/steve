# Using Hooks

Hooks are automated scripts that run in response to Claude Code events. This guide explains how to configure
and use hooks for automated workflows.

## What is a Hook?

A hook is a Python script (with optional markdown documentation) that executes automatically when specific
events occur in Claude Code:

- **PreToolUse** - Before a tool executes
- **PostToolUse** - After a tool executes
- **SessionStart** - When a session begins
- **SessionEnd** - When a session ends
- **UserPrompt** - When a user submits a prompt

Hooks enable automated code analysis, quality checks, and workflow automation.

## Hook Types

### Analyzers

Hooks that analyze code when files change:

| Hook | Trigger | Purpose |
|------|---------|---------|
| `lint_changed` | PostToolUse (Write/Edit) | Lint modified files |
| `typecheck_changed` | PostToolUse (Write/Edit) | Type check modified files |
| `test_changed` | PostToolUse (Write/Edit) | Run tests for modified files |
| `security_audit` | PostToolUse (Write/Edit) | Security scan on changes |
| `complexity_checker` | PostToolUse (Write/Edit) | Check code complexity |
| `todo_tracker` | PostToolUse (Write/Edit) | Track TODOs in code |

### Context Hooks

Hooks that provide context and information:

| Hook | Trigger | Purpose |
|------|---------|---------|
| `jit_context` | UserPrompt | Just-in-time context loading |
| `context_injector` | SessionStart | Inject relevant context |
| `project_detector` | SessionStart | Detect project type |
| `related_files` | PreToolUse (Read) | Find related files |
| `codebase_map` | SessionStart | Generate codebase overview |
| `recent_changes` | SessionStart | Show recent git changes |

### Lifecycle Hooks

Hooks for session lifecycle events:

| Hook | Trigger | Purpose |
|------|---------|---------|
| `session_start` | SessionStart | Initialize session |
| `session_end` | SessionEnd | Cleanup and summary |
| `session_summary` | SessionEnd | Generate session summary |
| `create_checkpoint` | SessionEnd | Save session checkpoint |
| `knowledge_update` | SessionEnd | Update knowledge graph |
| `metrics_collector` | SessionEnd | Collect session metrics |

### Workflow Hooks

Hooks for workflow automation:

| Hook | Trigger | Purpose |
|------|---------|---------|
| `pre_tool_use` | PreToolUse | Validate before tool execution |
| `post_tool_use` | PostToolUse | Actions after tool execution |
| `todo_sync` | PostToolUse | Sync TODO items |
| `commit_suggester` | PostToolUse (Write/Edit) | Suggest commits |

## Configuring Hooks

### Settings Structure

Hooks are configured in `~/.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [...],
    "PostToolUse": [...],
    "SessionStart": [...],
    "SessionEnd": [...],
    "UserPrompt": [...]
  }
}
```

### Hook Configuration

Each hook entry has:

```json
{
  "matcher": "Write|Edit",
  "command": "python ~/.claude/hooks/analyzers/lint_changed.py $FILE",
  "timeout": 30000
}
```

| Field | Description |
|-------|-------------|
| `matcher` | Regex pattern to match tool names (optional) |
| `command` | Shell command to execute |
| `timeout` | Maximum execution time in ms (optional) |

### Environment Variables

Hooks receive context via environment variables:

| Variable | Description |
|----------|-------------|
| `$FILE` | Path to the affected file |
| `$TOOL` | Name of the tool being used |
| `$SESSION_ID` | Current session identifier |
| `$WORKING_DIR` | Current working directory |

## Installing Hooks

### Step 1: Copy Hook Files

```bash
# Copy Python script and documentation
cp steve/hooks/analyzers/lint_changed.py ~/.claude/hooks/analyzers/
cp steve/hooks/analyzers/lint_changed.md ~/.claude/hooks/analyzers/
```

### Step 2: Register in Settings

Edit `~/.claude/settings.json`:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "command": "python ~/.claude/hooks/analyzers/lint_changed.py $FILE"
      }
    ]
  }
}
```

### Step 3: Verify Installation

Test the hook manually:

```bash
python ~/.claude/hooks/analyzers/lint_changed.py test_file.py
```

## Common Hook Configurations

### Lint on Save

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "command": "python ~/.claude/hooks/analyzers/lint_changed.py $FILE"
      }
    ]
  }
}
```

### Type Check on Save

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "command": "python ~/.claude/hooks/analyzers/typecheck_changed.py $FILE"
      }
    ]
  }
}
```

### Session Context Loading

```json
{
  "hooks": {
    "SessionStart": [
      {
        "command": "python ~/.claude/hooks/context/context_injector.py"
      },
      {
        "command": "python ~/.claude/hooks/context/project_detector.py"
      }
    ]
  }
}
```

### Full Quality Pipeline

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "command": "python ~/.claude/hooks/analyzers/lint_changed.py $FILE"
      },
      {
        "matcher": "Write|Edit",
        "command": "python ~/.claude/hooks/analyzers/typecheck_changed.py $FILE"
      },
      {
        "matcher": "Write|Edit",
        "command": "python ~/.claude/hooks/analyzers/security_audit.py $FILE"
      }
    ],
    "SessionStart": [
      {
        "command": "python ~/.claude/hooks/context/context_injector.py"
      }
    ],
    "SessionEnd": [
      {
        "command": "python ~/.claude/hooks/lifecycle/session_summary.py"
      }
    ]
  }
}
```

## Writing Custom Hooks

### Basic Hook Structure

```python
#!/usr/bin/env python3
"""
Hook description.

Trigger: PostToolUse (Write|Edit)
Purpose: What this hook does
"""

import os
import sys


def main():
    """Main hook logic."""
    file_path = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("FILE")

    if not file_path:
        return

    # Hook logic here
    print(f"Processing: {file_path}")

    # Return non-zero to indicate failure
    # sys.exit(1)


if __name__ == "__main__":
    main()
```

### Hook with Output

Hooks can output messages that appear in Claude Code:

```python
import json

def output_message(message: str, level: str = "info"):
    """Output structured message."""
    print(json.dumps({
        "type": level,
        "message": message
    }))

# Usage
output_message("Linting passed", "success")
output_message("Found 3 issues", "warning")
output_message("Critical error", "error")
```

### Hook with File Filtering

```python
from pathlib import Path

SUPPORTED_EXTENSIONS = {".py", ".js", ".ts"}

def should_process(file_path: str) -> bool:
    """Check if file should be processed."""
    path = Path(file_path)
    return path.suffix in SUPPORTED_EXTENSIONS

def main():
    file_path = sys.argv[1]

    if not should_process(file_path):
        return  # Skip unsupported files

    # Process file
```

### Hook with External Tools

```python
import subprocess

def run_linter(file_path: str) -> tuple[int, str]:
    """Run linter on file."""
    result = subprocess.run(
        ["ruff", "check", file_path],
        capture_output=True,
        text=True
    )
    return result.returncode, result.stdout

def main():
    file_path = sys.argv[1]
    code, output = run_linter(file_path)

    if code != 0:
        print(f"Linting issues:\n{output}")
        sys.exit(1)
```

## Hook Patterns

### The Guard Pattern

Hooks that prevent problematic changes:

```python
def check_for_secrets(file_path: str) -> bool:
    """Check for hardcoded secrets."""
    with open(file_path) as f:
        content = f.read()

    patterns = ["API_KEY=", "password=", "secret="]
    for pattern in patterns:
        if pattern in content:
            return False
    return True

def main():
    file_path = sys.argv[1]
    if not check_for_secrets(file_path):
        print("ERROR: Potential secrets detected!")
        sys.exit(1)
```

### The Reporter Pattern

Hooks that generate reports:

```python
def generate_report(file_path: str) -> dict:
    """Generate analysis report."""
    return {
        "file": file_path,
        "lines": count_lines(file_path),
        "complexity": calculate_complexity(file_path),
        "issues": find_issues(file_path)
    }

def main():
    file_path = sys.argv[1]
    report = generate_report(file_path)
    print(json.dumps(report, indent=2))
```

### The Context Pattern

Hooks that provide context:

```python
def gather_context() -> dict:
    """Gather project context."""
    return {
        "project_type": detect_project_type(),
        "recent_changes": get_recent_changes(),
        "active_branch": get_current_branch(),
        "test_status": get_test_status()
    }

def main():
    context = gather_context()
    print(json.dumps(context, indent=2))
```

## Hook Best Practices

### Performance

1. **Keep hooks fast** - Hooks run synchronously
2. **Filter early** - Skip files that don't need processing
3. **Use timeouts** - Prevent hanging hooks
4. **Cache results** - Avoid redundant work

### Reliability

1. **Handle errors gracefully** - Don't crash on edge cases
2. **Provide clear output** - Users should understand what happened
3. **Exit codes matter** - Non-zero indicates failure
4. **Log for debugging** - Include debug information

### Security

1. **Validate inputs** - Don't trust file paths blindly
2. **Avoid shell injection** - Use subprocess safely
3. **Limit permissions** - Run with minimal privileges
4. **Don't expose secrets** - Be careful with output

## Troubleshooting

### Hook Not Running

1. Check hook is registered in `settings.json`
2. Verify matcher pattern matches the tool
3. Check Python script is executable
4. Look for errors in Claude Code logs

### Hook Running Too Slowly

1. Add timeout to configuration
2. Optimize hook logic
3. Add early filtering
4. Consider async execution

### Hook Output Not Showing

1. Ensure hook prints to stdout
2. Check output format
3. Verify hook doesn't exit early
4. Test hook manually

### Hook Blocking Operations

1. Check for infinite loops
2. Add timeout configuration
3. Review external tool calls
4. Consider background execution

## See Also

- [Component Catalog](COMPONENT_CATALOG.md#hooks) - Browse all hooks
- [Installation](INSTALLATION.md) - Install new hooks
- [Development](DEVELOPMENT.md) - Create custom hooks
- [Troubleshooting](TROUBLESHOOTING.md) - Common issues
