---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: hook
---

# Init

```python
"""PreToolUse guard hooks.

Guards run before tool execution and can:
- Return 0 to allow the operation
- Return 1 to show a warning but allow
- Return 2 to block the operation

Available guards:
- dangerous_command_guard: Blocks dangerous shell commands
- branch_protection: Prevents pushes to protected branches
- secret_scanner: Detects secrets in file content
- file_protection: Protects sensitive files from modification
- large_file_guard: Warns/blocks large file operations
- path_validation: Validates paths are within project bounds
- readonly_guard: Protects lock files and generated code
"""
```
