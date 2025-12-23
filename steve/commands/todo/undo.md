---
allowed-tools: Bash
argument-hint: ' <id>'
description: Mark completed todo <id> as incomplete in SQLite DB.
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: commands
---

# Undo Todo Completion

Mark a completed todo as incomplete (pending) in the SQLite database.

## Usage

```bash
/todo:undo <id>
```

## Instructions

1. Parse the todo ID from arguments
2. Run the update command to change status back to "pending"
3. Confirm the change to the user

## Command

!cd /Users/joe/Documents/Projects/joecc && uv run python -m joecc.storage.cli todo update $ID --status pending

## Examples

```bash
# Mark todo #42 as incomplete
cd /Users/joe/Documents/Projects/joecc && uv run python -m joecc.storage.cli todo update 42 --status pending

# Or mark as in_progress instead
cd /Users/joe/Documents/Projects/joecc && uv run python -m joecc.storage.cli todo update 42 --status in_progress
```

## Status Options

- `pending` - Not started (default for undo)
- `in_progress` - Currently working on
- `completed` - Done

## Feedback

After updating, show:

```
Undid completion for todo #<id> - status changed to pending
```

## Notes

- The `completed_at` timestamp is preserved for historical record
- Use `/todo:list` to see all todos and their current status
