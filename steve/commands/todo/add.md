---
allowed-tools: Bash
argument-hint: ' <description> [--priority low|medium|high] [--project <project>]
  [--tags <tags>]'
description: Add a todo to SQLite DB using joecc CLI.
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: commands
---

# Add Todo

Add a new todo to the SQLite database.

!cd /Users/joe/Documents/Projects/joecc && uv run python -m joecc.storage.cli add $DESCRIPTION --priority $PRIORITY --project $PROJECT --tags $TAGS

## Examples

```bash
cd /Users/joe/Documents/Projects/joecc && uv run python -m joecc.storage.cli todo add "Fix SetLevel() losing JSON config in logging.go" --priority 1 --project /Users/joe/Documents/GitHub/gaw --tags "bug,logging"
```

```bash
cd /Users/joe/Documents/Projects/joecc && uv run python -m joecc.storage.cli todo add "Add security tests for ValidatePathWithin()" --priority 1 --project /Users/joe/Documents/GitHub/gaw --tags "critical,testing,security"
```
