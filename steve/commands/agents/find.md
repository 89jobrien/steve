---
description: Find the best agent for a specific task or problem
allowed-tools: Bash, Read, Grep, Task
argument-hint: '[task description]'
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: commands
name: find
---

# Find Agent for Task

Find the most appropriate agent(s) for a specific task or problem.

## Arguments

- `[task description]`: Describe what you need help with

## Common Task Mappings

| Task Type | Recommended Agent(s) |
|-----------|---------------------|
| Code review | `code-reviewer`, `architect-reviewer` |
| Debugging errors | `debugger`, `error-detective`, `triage-expert` |
| Database optimization | `database-optimizer`, `database-expert` |
| Writing tests | `test-engineer`, `pytest-tdd-expert` |
| Performance issues | `performance-profiler`, `performance-engineer` |
| Security audit | `security-engineer`, `code-reviewer` |
| API design | `backend-architect`, `api-documenter` |
| React/frontend | `frontend-developer`, `react-performance-optimizer` |
| Docker/containers | `deployment-engineer`, `docker-expert` |
| Git issues | `git-expert` |
| Documentation | `technical-writer`, `documentation-expert` |
| Research | `technical-researcher`, `research-orchestrator` |
| Refactoring | `refactoring-expert` |
| TypeScript | `typescript-expert`, `typescript-pro` |
| Python | `python-pro`, `pytest-tdd-expert` |
| CI/CD | `github-actions-expert`, `deployment-engineer` |
| Cloud/AWS | `cloud-architect`, `devops-engineer` |
| ML/AI | `ml-engineer`, `data-scientist`, `ai-engineer` |

## Instructions

Based on the task "$ARGUMENTS", recommend the most appropriate agent(s).

1. Parse the task description to identify key concepts
2. Match against agent descriptions and skills
3. Recommend 1-3 best-fit agents with reasoning
4. Show how to invoke: `Use the Task tool with subagent_type="agent-name"`

## Output Format

```
## Recommended Agent(s) for: [task]

### Primary: agent-name
- Why: [reason based on agent description]
- Skills: [relevant skills]
- Invoke: Task(subagent_type="agent-name", prompt="...")

### Alternative: other-agent
- Why: [reason]
```
