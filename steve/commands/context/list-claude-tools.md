---
allowed-tools: Bash, Read
argument-hint: ' No arguments required'
description: Shortcut to see all available Claude tools
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: commands
name: list-claude-tools
---

# All Tools

Display All Available Development Tools

## Instructions

Display all available tools from your system prompt in the following format:

1. **List each tool** with its TypeScript function signature
2. **Include the purpose** of each tool as a suffix
3. **Use double line breaks** between tools for readability
4. **Format as bullet points** for clear organization

The output should help developers understand:

- What tools are available in the current Claude Code session
- The exact function signatures for reference
- The primary purpose of each tool

This command is useful for:

- Quick reference of available capabilities
- Understanding tool signatures
- Planning which tools to use for specific tasks

### Example format

```typescript
• functionName(parameters: Type): ReturnType - Purpose of the tool

• anotherFunction(params: ParamType): ResultType - What this tool does
```
