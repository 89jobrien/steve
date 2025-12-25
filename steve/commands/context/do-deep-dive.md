---
allowed-tools: Read, Write
description: Analyze directory structure and purpose
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: commands
name: do-deep-dive
---

# Directory Deep Dive

Analyze directory structure and purpose

## Instructions

1. **Target Directory**
   - Focus on the specified directory `$ARGUMENTS` or the current working directory

2. **Investigate Architecture**
   - Analyze the implementation principles and architecture of the code in this directory and its subdirectories
   - Look for:
     - Design patterns being used
     - Dependencies and their purposes
     - Key abstractions and interfaces
     - Naming conventions and code organization

3. **Create or Update Documentation**
   - Create a DEEP_DIVE.local.md file capturing this knowledge
   - If one already exists, update it with newly discovered information
   - Include:
     - Purpose and responsibility of this module
     - Key architectural decisions
     - Important implementation details
     - Common patterns used throughout the code
     - Any gotchas or non-obvious behaviors

4. **Ensure Proper Placement**
   - Place the DEEP_DIVE.local.md file in the directory being analyzed.
   - This ensures the context is loaded when working in that specific area
