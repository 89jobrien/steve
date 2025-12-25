---
allowed-tools: Bash
argument-hint: ' <id> [due date]'
description: Set or update the due date for todo <id> in SQLite DB.
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: commands
name: due
---

# Set Due Date

Set or update the due date for a specific todo in the SQLite database.

## Usage

```bash
/todo:due <id> <date>
/todo:due <id> clear
```

## Instructions

1. Parse the todo ID from arguments
2. Parse the due date - convert natural language dates to YYYY-MM-DD format:
   - `tomorrow` -> next day's date
   - `next week` -> 7 days from now
   - `in 3 days` -> 3 days from now
   - `June 15` -> 2025-06-15 (or next occurrence)
   - `12/24/2025` -> 2025-12-24
3. Run the update command with the formatted date
4. Use "clear" to remove an existing due date

## Command

!cd /Users/joe/Documents/Projects/joecc && uv run python -m joecc.storage.cli todo update $ID --due $DUE_DATE

## Examples

```bash
# Set due date to specific date
cd /Users/joe/Documents/Projects/joecc && uv run python -m joecc.storage.cli todo update 42 --due 2025-12-31

# Clear/remove due date
cd /Users/joe/Documents/Projects/joecc && uv run python -m joecc.storage.cli todo update 42 --due clear
```

## Date Format

- Must be in YYYY-MM-DD format for the CLI
- Parse natural language dates (tomorrow, next week, etc.) and convert to YYYY-MM-DD
- Use "clear" keyword to remove an existing due date

## Feedback

After updating, show:

```
Set due date for todo #<id>: YYYY-MM-DD
```

Or if clearing:

```
Cleared due date for todo #<id>
```
