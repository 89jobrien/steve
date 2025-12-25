---
allowed-tools: Bash
argument-hint: ' <id>'
description: Mark todo <id> as completed in SQLite DB.
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: commands
name: complete
---

# Complete Todo

Mark a todo <id> as completed in the SQLite database.

!cd /Users/joe/Documents/Projects/joecc && uv run python -m joecc.storage.cli done $ID
