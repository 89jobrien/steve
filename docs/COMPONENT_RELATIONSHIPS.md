# Component Relationships

This document maps the relationships between agents, skills, commands, and hooks in the Steve component library.

## Overview

Components in Steve are designed to work together:

- **Agents** reference **skills** for domain expertise
- **Commands** invoke **agents** for task execution
- **Hooks** trigger on tool events to enhance workflows

```text
Commands ──invoke──> Agents ──reference──> Skills
                        │
                        └──use──> Tools

Hooks ──trigger on──> Tool Events
```

## Skill Usage by Domain

### Machine Learning Skills

| Skill | Purpose | Used By |
|-------|---------|---------|
| `machine-learning` | ML patterns and best practices | `computer-vision-engineer`, `data-scientist`, `ml-engineer`, `mlops-engineer`, `nlp-engineer`, `ai-engineer`, `model-evaluator` |
| `prompt-optimization` | LLM prompt engineering | `ai-engineer`, `prompt-engineer`, `environment-improver` |
| `ai-ethics` | Responsible AI development | `ai-ethics-advisor` |

### Testing Skills

| Skill | Purpose | Used By |
|-------|---------|---------|
| `testing` | Test strategy and automation | `test-engineer`, `test-automator`, `integration-tester`, `golang-pro`, `parallel-tdd-expert`, `validation-enforcer` |
| `tdd-pytest` | Python TDD with pytest | `pytest-tdd-expert`, `parallel-tdd-expert`, `environment-improver` |
| `golang-testing` | Go testing patterns | `golang-pro` |

### Performance Skills

| Skill | Purpose | Used By |
|-------|---------|---------|
| `performance` | Application performance | `react-performance-optimizer`, `performance-profiler`, `load-testing-specialist`, `web-vitals-optimizer`, `fullstack-developer`, `backend-architect` |
| `database-optimization` | Query and schema optimization | `database-optimizer`, `database-architect`, `data-engineer`, `mlops-engineer` |
| `golang-performance` | Go performance patterns | `golang-pro` |

### Infrastructure Skills

| Skill | Purpose | Used By |
|-------|---------|---------|
| `cloud-infrastructure` | AWS/Azure/GCP patterns | `cloud-architect`, `devops-engineer`, `security-engineer`, `deployment-engineer`, `network-engineer` |
| `devops-runbooks` | Operational procedures | `devops-engineer`, `devops-troubleshooter`, `deployment-engineer`, `monitoring-specialist` |
| `network-engineering` | Network architecture | `network-engineer` |

### Code Quality Skills

| Skill | Purpose | Used By |
|-------|---------|---------|
| `code-review` | Code review methodology | `code-reviewer` |
| `global-standards` | Coding standards | `environment-improver`, `validation-enforcer`, `test-engineer` |
| `meta-cognitive-reasoning` | Evidence-based analysis | `code-reviewer`, `debugger`, `error-detective`, `triage-expert`, `security-engineer`, `devops-troubleshooter`, `research-synthesizer` |

### Documentation Skills

| Skill | Purpose | Used By |
|-------|---------|---------|
| `documentation` | Technical writing | `technical-writer`, `api-documenter`, `changelog-generator` |
| `design-docs` | Architecture documentation | (deprecated, use `documentation`) |
| `migrations` | Migration guides | (deprecated, use `documentation`) |

### Development Skills

| Skill | Purpose | Used By |
|-------|---------|---------|
| `developer-experience` | DX optimization | `dx-optimizer`, `devops-engineer`, `cli-expert` |
| `skill-creator` | Creating new skills | `skill-creator-expert`, `skill-extractor`, `environment-improver` |
| `context-management` | Multi-agent context | `context-manager`, `memory-manager` |
| `command-optimization` | CLI development | `cli-expert`, `command-expert` |

### Security Skills

| Skill | Purpose | Used By |
|-------|---------|---------|
| `security-audit` | Security assessment | `security-engineer`, `code-reviewer` |
| `security-engineering` | Security infrastructure | `security-engineer`, `cloud-architect` |

### Research Skills

| Skill | Purpose | Used By |
|-------|---------|---------|
| `lead-research-assistant` | Research methodology | `research-orchestrator-v2`, `research-coordinator`, `academic-researcher`, `technical-researcher`, `fact-checker`, `data-analyst` |
| `technical-research` | Technical investigation | `technical-researcher` |

### Web Development Skills

| Skill | Purpose | Used By |
|-------|---------|---------|
| `nextjs-architecture` | Next.js patterns | `nextjs-expert`, `nextjs-architecture-expert` |
| `web-accessibility` | WCAG compliance | `web-accessibility-checker`, `frontend-developer`, `css-expert` |
| `seo-analysis` | SEO optimization | `seo-analyzer` |
| `url-analysis` | URL validation | `url-context-validator`, `url-link-extractor` |

### Scripting Skills

| Skill | Purpose | Used By |
|-------|---------|---------|
| `python-scripting` | Python patterns | `data-scientist`, `mlops-engineer`, `parallel-tdd-expert` |
| `shell-scripting` | Bash/shell scripts | `shell-scripting-pro`, `git-expert` |
| `golang-enterprise-patterns` | Go architecture | `golang-pro` |

### Workflow Skills

| Skill | Purpose | Used By |
|-------|---------|---------|
| `git-workflow` | Git patterns | `git-expert` |
| `agile-ceremonies` | Sprint management | (standalone skill) |
| `jira` | Jira integration | (standalone skill) |
| `n8n` | n8n workflows | `n8n-workflow-expert` |

### Analysis Skills

| Skill | Purpose | Used By |
|-------|---------|---------|
| `action-item-organizer` | Extract action items | `todo-organizer` |
| `dead-code-removal` | Remove unused code | `unused-code-cleaner` |
| `ai-code-cleanup` | Remove AI slop | `slop-remover` |
| `debugging` | Debug methodology | `debugger`, `error-detective` |

### Specialized Skills

| Skill | Purpose | Used By |
|-------|---------|---------|
| `tool-presets` | Tool configuration | `docker-expert`, `test-automator`, `performance-engineer`, `code-reviewer` |
| `mcp-integration` | MCP server patterns | `mcp-expert` |
| `claude-hooks` | Hook development | (standalone skill) |
| `cocoindex` | Data pipelines | (standalone skill) |

## Agent Categories

### Code Quality Agents

```text
code-reviewer
    └── skills: code-review, meta-cognitive-reasoning

code-linter
    └── skills: (none - uses external tools)

refactoring-expert
    └── skills: (none - pattern-based)

slop-remover
    └── skills: ai-code-cleanup
```

### Testing Agents

```text
test-engineer
    └── skills: testing, global-standards

test-automator
    └── skills: testing, tool-presets

pytest-tdd-expert
    └── skills: testing, tool-presets, tdd-pytest

parallel-tdd-expert
    └── skills: testing, tdd-pytest, python-scripting
```

### Database Agents

```text
database-architect
    └── skills: database-optimization, cloud-infrastructure

database-optimizer
    └── skills: database-optimization

database-admin
    └── skills: database-optimization, tool-presets
```

### DevOps Agents

```text
devops-engineer
    └── skills: developer-experience, cloud-infrastructure, devops-runbooks

deployment-engineer
    └── skills: devops-runbooks, testing

cloud-architect
    └── skills: cloud-infrastructure, security-engineering, devops-runbooks

monitoring-specialist
    └── skills: performance, devops-runbooks
```

### Research Agents

```text
research-orchestrator-v2
    └── skills: lead-research-assistant, tool-presets

research-coordinator
    └── skills: lead-research-assistant

academic-researcher
    └── skills: lead-research-assistant, meta-cognitive-reasoning

technical-researcher
    └── skills: lead-research-assistant
```

### AI/ML Agents

```text
ai-engineer
    └── skills: machine-learning, prompt-optimization

ml-engineer
    └── skills: machine-learning, python-scripting, database-optimization

data-scientist
    └── skills: machine-learning

nlp-engineer
    └── skills: machine-learning
```

### Frontend Agents

```text
nextjs-expert
    └── skills: nextjs-architecture, performance

frontend-developer
    └── skills: web-accessibility, performance

css-expert
    └── skills: web-accessibility

react-performance-optimizer
    └── skills: performance, testing
```

### Documentation Agents

```text
technical-writer
    └── skills: documentation

api-documenter
    └── skills: documentation

documentation-expert
    └── skills: documentation, database-optimization, cloud-infrastructure
```

## Command-Agent Mappings

Commands often invoke specific agents:

| Command | Invokes Agent |
|---------|---------------|
| `/dev:review-code` | `code-reviewer` |
| `/dev:review-architecture` | `architect-reviewer` |
| `/test:test` | `test-engineer` or `pytest-tdd-expert` |
| `/test:run` | `test-automator` |
| `/git:clean-branches` | `git-expert` |
| `/research` | `research-orchestrator-v2` |
| `/analyze-codebase` | Multiple (parallel) |

## Hook Categories

### Analyzer Hooks

Triggered on `PostToolUse` for `Write|Edit`:

| Hook | Purpose |
|------|---------|
| `lint_changed` | Run linter on modified files |
| `typecheck_changed` | Type check modified files |
| `test_changed` | Run tests for modified files |
| `security_audit` | Security scan on changes |
| `complexity_checker` | Check code complexity |

### Context Hooks

| Hook | Trigger | Purpose |
|------|---------|---------|
| `jit_context` | UserPrompt | Load relevant context |
| `context_injector` | SessionStart | Inject project context |
| `project_detector` | SessionStart | Detect project type |
| `related_files` | PreToolUse (Read) | Find related files |

### Lifecycle Hooks

| Hook | Trigger | Purpose |
|------|---------|---------|
| `session_start` | SessionStart | Initialize session |
| `session_end` | SessionEnd | Cleanup and summary |
| `session_summary` | SessionEnd | Generate session summary |
| `knowledge_update` | SessionEnd | Update knowledge graph |

## Composing Components

### Example: Code Review Workflow

```text
User: "/dev:review-code src/main.py"
         │
         ▼
    [review-code command]
         │
         └──invokes──> [code-reviewer agent]
                            │
                            ├──loads──> [code-review skill]
                            ├──loads──> [meta-cognitive-reasoning skill]
                            │
                            └──uses tools──> Read, Grep, Glob
```

### Example: Test-Driven Development

```text
User: "/test:test src/auth.py"
         │
         ▼
    [test command]
         │
         └──invokes──> [pytest-tdd-expert agent]
                            │
                            ├──loads──> [testing skill]
                            ├──loads──> [tdd-pytest skill]
                            ├──loads──> [tool-presets skill]
                            │
                            └──uses tools──> Read, Write, Edit, Bash
```

### Example: Research Pipeline

```text
User: "/research quantum computing"
         │
         ▼
    [research command]
         │
         └──invokes──> [research-orchestrator-v2]
                            │
                            ├──loads──> [lead-research-assistant skill]
                            │
                            └──delegates to:
                                ├── [academic-researcher]
                                ├── [technical-researcher]
                                └── [fact-checker]
```

## Finding Related Components

### By Skill

To find all agents using a skill:

```bash
# Search index for skill references
grep -l "skills.*testing" agents/**/*.md
```

### By Domain

Components are organized by domain:

```text
agents/
├── ai-specialists/     # AI/ML agents
├── code-quality/       # Review, linting agents
├── database/           # DB agents
├── development/        # Dev workflow agents
├── devops/             # Infrastructure agents
├── documentation/      # Writing agents
├── research/           # Research agents
└── web-tools/          # Web development agents
```

### By Tool Requirements

To find agents with specific tool access:

```bash
# Find agents with Write access
grep -l "tools:.*Write" agents/**/*.md

# Find read-only agents
grep -l "tools: Read, Grep, Glob$" agents/**/*.md
```

## See Also

- [Component Catalog](COMPONENT_CATALOG.md) - Browse all components
- [Using Agents](USING_AGENTS.md) - Agent invocation
- [Using Skills](USING_SKILLS.md) - Skill usage
- [Architecture](ARCHITECTURE.md) - System design
