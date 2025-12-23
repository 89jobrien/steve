---
allowed-tools: Bash, Read
argument-hint: ' [context] | [file-path] | [fuckin-anything]'
description: Load context for a new agent session by analyzing codebase structure,
  documentation and README
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: commands
---

# Prime

## Current State

- Git status: !`git status --porcelain`
- Recent changes: !`git diff --stat`
- Repository info: !`git log --oneline -5`
- Documentation exists: @docs/ or @README.md (if exists)

## Report

- Provide a summary of your understanding of the project

## Instructions

Initialize a new Claude Code session with comprehensive project context:

1. **Analyze Codebase Structure**
   - Run `git ls-files` to understand file organization and project layout
   - Execute directory tree commands (if available) for visual structure
   - Identify key directories and their purposes
   - Note the technology stack and frameworks in use

2. **Read Project Documentation**
   - Read README.md for project overview and setup instructions
   - Check for any additional documentation in docs/ or ai_docs/
   - Review any CONTRIBUTING.md or development guides
   - Look for architecture or design documents

3. **Understand Project Context**
   - Identify the project's primary purpose and goals
   - Note any special setup requirements or dependencies
   - Check for environment configuration needs
   - Review any CI/CD configuration files

4. **Provide Concise Overview**
   - Summarize the project's purpose in 2-3 sentences
   - List the main technologies and frameworks
   - Highlight any important setup steps
   - Note key areas of the codebase

This command helps establish context quickly when:

- Starting work on a new project
- Returning to a project after time away
- Onboarding new team members
- Preparing for deep technical work

The goal is to "prime" the AI assistant with essential project knowledge for more effective assistance.
