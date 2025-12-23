---
allowed-tools: Bash
argument-hint: ' <id>'
description: Remove todo <id> entirely from SQLite DB.
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: commands
---

# Remove Todo

Remove a todo <id> entirely from the SQLite database.

!cd /Users/joe/Documents/Projects/joecc && uv run python -m joecc.storage.cli delete $ID
