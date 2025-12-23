# Component Catalog

This catalog provides a searchable index of all components in the Steve repository. Use this to find the right
component for your task.

**Total Components:** 137 agents, 97 commands, 57 skills, 44 hooks, 27 templates

## Quick Navigation

- [Agents](#agents) - Specialized AI assistants by domain
- [Commands](#commands) - Slash commands by category
- [Skills](#skills) - Reusable expertise bundles
- [Hooks](#hooks) - Automated event handlers
- [Templates](#templates) - Scaffolds for new components

## Agents

Agents are specialized AI assistants configured for specific tasks. Each agent has defined tools, an optional model
preference, and may reference skills for domain expertise.

### Agent Domains Overview

| Domain | Count | Description |
|--------|-------|-------------|
| [ai-specialists](#ai-specialists) | 12 | AI/ML specialists and model experts |
| [code-quality](#code-quality) | 10 | Code review, linting, refactoring |
| [codebase-ready](#codebase-ready) | 3 | Codebase exploration and analysis |
| [core](#core) | 4 | Core system agents |
| [data-ai](#data-ai) | 8 | Data science and ML engineering |
| [database](#database) | 4 | Database design and optimization |
| [deep-research-team](#deep-research-team) | 17 | Research orchestration and synthesis |
| [development](#development) | 16 | Development workflows and tools |
| [devops-infrastructure](#devops-infrastructure) | 12 | CI/CD, deployment, infrastructure |
| [documentation](#documentation) | 4 | Technical writing and docs |
| [expert-advisors](#expert-advisors) | 6 | Domain expert consultants |
| [mcp](#mcp) | 12 | MCP server integrations |
| [programming-languages](#programming-languages) | 8 | Language-specific experts |
| [quality](#quality) | 9 | Testing and quality assurance |
| [utilitarian](#utilitarian) | 6 | Utility and helper agents |
| [web-tools](#web-tools) | 6 | Frontend, SEO, accessibility |

### ai-specialists

Agents specializing in AI, ML, and LLM applications.

| Agent | Description |
|-------|-------------|
| `ai-engineer` | LLM application and RAG system specialist |
| `ai-ethics-advisor` | AI ethics and responsible AI development |
| `ai-interview-market-researcher` | AI interview and hiring market research |
| `ai-interview-trend-analyst` | AI interviewing trends and future directions |
| `computer-vision-engineer` | Image analysis and visual AI applications |
| `hackathon-ai-strategist` | AI hackathon ideation and project evaluation |
| `ml-engineer` | ML pipelines and model deployment |
| `mlops-engineer` | ML infrastructure and operations |
| `model-evaluator` | AI model evaluation and benchmarking |
| `nlp-engineer` | NLP and text analytics |
| `prompt-engineer` | Prompt optimization for LLMs |
| `task-decomposition-expert` | Complex goal breakdown and orchestration |

### code-quality

Agents focused on code review, linting, and quality improvement.

| Agent | Description |
|-------|-------------|
| `architect-reviewer` | Architectural consistency and patterns |
| `code-linter` | Linting and static analysis |
| `code-reviewer` | Comprehensive code review |
| `migration-auditor` | Migration and upgrade path analysis |
| `refactoring-expert` | Systematic code refactoring |
| `slop-remover` | AI-generated code cleanup |
| `todo-organizer` | TODO extraction and organization |
| `triage-expert` | Initial problem diagnosis |
| `unused-code-cleaner` | Dead code detection and removal |
| `url-context-validator` | URL validation and context analysis |

### codebase-ready

Agents for codebase exploration and understanding.

| Agent | Description |
|-------|-------------|
| `context-aware-coder` | Knowledge graph and code relationship analysis |
| `memory-manager` | Knowledge graph management |
| `nia-oracle` | Remote codebase and documentation research |

### core

Core system agents for meta-operations.

| Agent | Description |
|-------|-------------|
| `meta` | Agent configuration file generator |
| `meta2` | New agent creation from descriptions |
| `skill-creator-expert` | Skill creation specialist |
| `skill-extractor` | Reusable pattern extraction from agents |

### data-ai

Data science, analytics, and ML specialists.

| Agent | Description |
|-------|-------------|
| `competitive-intelligence-analyst` | Competitive and market research |
| `data-analyst` | Quantitative analysis and data-driven research |
| `data-engineer` | ETL/ELT pipelines and data platforms |
| `data-scientist` | Data analysis and statistical modeling |
| `quant-analyst` | Quantitative finance and algo trading |
| `research-synthesizer` | Multi-source research consolidation |
| `search-specialist` | Advanced web research and synthesis |
| `technical-researcher` | Technical documentation and code analysis |

### database

Database design, optimization, and administration.

| Agent | Description |
|-------|-------------|
| `database-admin` | Database operations and backups |
| `database-architect` | Database design and architecture |
| `database-expert` | Cross-database performance specialist |
| `database-optimizer` | Query tuning and schema optimization |

### deep-research-team

Multi-agent research orchestration and synthesis.

| Agent | Description |
|-------|-------------|
| `academic-researcher` | Scholarly sources and peer-reviewed papers |
| `fact-checker` | Claim verification and source validation |
| `parallel-research-executor` | Concurrent research task execution |
| `quality-gate-validator` | Research artifact quality validation |
| `query-clarifier` | Research query analysis and clarification |
| `report-generator` | Research findings to final reports |
| `research-brief-generator` | Query to structured research brief |
| `research-coordinator` | Multi-specialist research planning |
| `research-orchestrator` | Comprehensive research workflow management |
| `research-orchestrator-v2` | Phased orchestration with parallel execution |
| `research-standards` | Research governance principles |
| `research-task-decomposer` | Parallelizable research task breakdown |

### development

General development workflow agents.

| Agent | Description |
|-------|-------------|
| `backend-architect` | Backend system architecture and API design |
| `cli-expert` | npm package CLI development |
| `cli-ui-designer` | Terminal-inspired UI design |
| `command-expert` | CLI command development |
| `debugger` | Error and test failure debugging |
| `dependency-manager` | Dependency analysis and updates |
| `docs-scraper` | Documentation fetching and saving |
| `documentation-expert` | Documentation creation and maintenance |
| `dx-optimizer` | Developer experience improvement |
| `error-detective` | Log analysis and error patterns |
| `fullstack-developer` | Full-stack application development |
| `log-analyzer` | Systematic log file analysis |
| `logging-specialist` | Logging infrastructure and debugging |
| `mcp-expert` | MCP integration patterns |
| `valerie` | Task and todo management |
| `worktree-subagent` | Git worktree creation |

### devops-infrastructure

CI/CD, deployment, and infrastructure automation.

| Agent | Description |
|-------|-------------|
| `cloud-architect` | Cloud infrastructure design (AWS/Azure/GCP) |
| `deployment-engineer` | CI/CD and deployment automation |
| `devops-engineer` | DevOps and infrastructure specialist |
| `devops-troubleshooter` | Production troubleshooting |
| `docker-expert` | Docker containerization and security |
| `dotti` | Dotfiles and configuration management |
| `git-expert` | Git workflows and repository management |
| `github-actions-expert` | GitHub Actions CI/CD optimization |
| `monitoring-specialist` | Monitoring and observability |
| `network-engineer` | Network connectivity and infrastructure |
| `security-engineer` | Security infrastructure and compliance |

### documentation

Technical writing and documentation specialists.

| Agent | Description |
|-------|-------------|
| `api-documenter` | OpenAPI specs and SDK generation |
| `changelog-generator` | Changelog and release notes |
| `llms-maintainer` | LLMs.txt roadmap file generation |
| `technical-writer` | User guides and tutorials |

### expert-advisors

Domain expert consultants for specialized guidance.

| Agent | Description |
|-------|-------------|
| `context-manager` | Multi-agent context orchestration |
| `environment-improver` | Development environment meta-improvement |
| `livekit-expert` | LiveKit and WebRTC real-time communication |
| `n8n-workflow-expert` | n8n workflow development |
| `temporal-python-pro` | Temporal workflow orchestration |

### mcp

MCP (Model Context Protocol) server integrations.

| Agent | Description |
|-------|-------------|
| `asana-expert` | Asana workspace and task management |
| `atlassian-expert` | Jira and Confluence integration |
| `claude-mem-expert` | Memory search and retrieval |
| `context7-docs-expert` | Library documentation fetching |
| `linear-expert` | Linear issue and project management |
| `mcp-best-practices-documenter` | MCP design patterns documentation |
| `mcp-browser-workflow-creator` | Browser automation workflows |
| `mcp-data-pipeline-creator` | Multi-source ETL pipeline design |
| `mcp-docker-expert` | MCP Docker server operations |
| `mcp-dynamic-discovery-specialist` | Adaptive MCP discovery workflows |
| `tavily-search-expert` | Web search and content extraction |

### programming-languages

Language-specific development experts.

| Agent | Description |
|-------|-------------|
| `bash-pro` | Defensive Bash scripting |
| `golang-pro` | Enterprise-level Go development |
| `nextjs-expert` | Next.js App Router and Server Components |
| `python-pro` | Idiomatic Python with advanced features |
| `rust-pro` | Idiomatic Rust with ownership patterns |
| `shell-scripting-pro` | Robust shell scripts and automation |
| `sql-pro` | Complex SQL and database design |
| `typescript-expert` | Advanced TypeScript patterns |
| `typescript-pro` | TypeScript with strict typing |

### quality

Testing, performance, and quality assurance.

| Agent | Description |
|-------|-------------|
| `convention-codifier` | Convention to lint rule transformation |
| `integration-tester` | System integration validation |
| `load-testing-specialist` | Load and stress testing |
| `parallel-tdd-expert` | Parallel TDD implementation |
| `performance-engineer` | Performance profiling and optimization |
| `performance-profiler` | Performance analysis and monitoring |
| `pytest-tdd-expert` | Python/pytest TDD specialist |
| `spec-first-implementer` | Spec-driven implementation |
| `test-automator` | Test suite creation and CI integration |
| `test-engineer` | Test strategy and automation |
| `test-gap-scanner` | Missing test coverage detection |
| `tdd-orchestrator` | TDD workflow coordination |
| `validation-enforcer` | Linting and type checking enforcement |

### utilitarian

Utility and helper agents.

| Agent | Description |
|-------|-------------|
| `css-expert` | CSS architecture and styling |
| `frontend-developer` | React applications and responsive design |
| `nextjs-architecture-expert` | Next.js best practices |
| `react-performance-optimization` | React performance optimization |
| `react-performance-optimizer` | React app performance tuning |
| `ui-ux-designer` | User-centered design and interfaces |
| `url-link-extractor` | URL and link extraction |
| `web-accessibility-checker` | WCAG compliance and accessibility |
| `web-vitals-optimizer` | Core Web Vitals optimization |

### web-tools

Frontend, SEO, and web accessibility.

| Agent | Description |
|-------|-------------|
| `seo-analyzer` | SEO analysis and optimization |

## Commands

Commands are slash-invoked workflows for common tasks. Invoke with `/category:command-name` or `/command-name`.

### Command Categories Overview

| Category | Count | Description |
|----------|-------|-------------|
| [_incoming](#_incoming) | 1 | Incoming/unsorted commands |
| [_team](#_team) | 2 | Team collaboration commands |
| [agents](#agents-commands) | 3 | Agent management |
| [context](#context) | 1 | Context management |
| [debug](#debug) | 1 | Debugging tools |
| [dev](#dev) | 6 | Development workflows |
| [docs](#docs) | 4 | Documentation generation |
| [git](#git) | 3 | Git operations |
| [memory](#memory) | 5 | Knowledge graph operations |
| [meta](#meta) | 3 | Meta-operations |
| [prompts](#prompts) | 1 | Prompt management |
| [setup](#setup) | 10 | Project setup |
| [skills](#skills-commands) | 2 | Skill management |
| [tdd](#tdd) | 5 | Test-driven development |
| [test](#test) | 4 | Testing workflows |
| [todo](#todo) | 6 | Todo management |
| [util](#util) | 3 | Utilities |

### _incoming

| Command | Description |
|---------|-------------|
| `research` | Deep research with parallel subagents |

### _team

| Command | Description |
|---------|-------------|
| `analyze-codebase` | Parallel code review, test audit, architecture analysis |
| `prep-for-standup` | Generate standup reports with activity analysis |

### agents-commands

| Command | Description |
|---------|-------------|
| `find` | Find best agent for a task |
| `list` | List available agents by category |
| `search` | Search agents by keyword |

### context

| Command | Description |
|---------|-------------|
| `list-claude-tools` | List all available Claude tools |
| `prime` | Load context for new agent session |

### debug

| Command | Description |
|---------|-------------|
| `debug` | Debug error messages |

### dev

| Command | Description |
|---------|-------------|
| `containerize-application` | Create production-ready Dockerfile |
| `design-rest-api` | Design RESTful API architecture |
| `remove-ai-slop` | Remove AI-generated code bloat |
| `review-architecture` | Architecture review with patterns analysis |
| `review-code` | Comprehensive code quality review |

### docs

| Command | Description |
|---------|-------------|
| `create-architecture-documentation` | Generate architecture docs with diagrams |
| `create-onboarding-guide` | Create developer onboarding guides |
| `create-prd` | Create Product Requirements Document |
| `update-docs` | Update project documentation |

### git

| Command | Description |
|---------|-------------|
| `clean-branches` | Clean merged and stale branches |
| `git-bisect-helper` | Guide git bisect for regressions |

### memory

| Command | Description |
|---------|-------------|
| `add` | Add entities to knowledge graph |
| `forget` | Remove from knowledge graph |
| `relate` | Create relationships in knowledge graph |
| `search` | Search knowledge graph |
| `view` | View knowledge graph entities |

### meta

| Command | Description |
|---------|-------------|
| `create-command` | Create new slash command |
| `create-skill` | Create new Claude skill |
| `create-subagent` | Create specialized AI subagent |

### prompts

| Command | Description |
|---------|-------------|
| `docs__scan_ask_write` | Scan and generate documentation |

### setup

| Command | Description |
|---------|-------------|
| `design-database-schema` | Design optimized database schemas |
| `implement-graphql-api` | Implement GraphQL API |
| `setup-ci-cd-pipeline` | Setup CI/CD pipeline |
| `setup-development-environment` | Setup development environment |
| `setup-docker-containers` | Setup Docker development environment |
| `setup-formatting` | Configure code formatting tools |
| `setup-linting` | Configure linting and quality tools |
| `setup-monorepo` | Configure monorepo structure |
| `setup-monitoring-observability` | Setup monitoring and observability |
| `setup-rate-limiting` | Implement API rate limiting |

### skills-commands

| Command | Description |
|---------|-------------|
| `list` | List available skills |
| `search` | Search skills by keyword |

### tdd

| Command | Description |
|---------|-------------|
| `quick-plan` | Create concise engineering plan |

### test

| Command | Description |
|---------|-------------|
| `init` | Initialize test configuration |
| `report` | Generate test audit and coverage report |
| `run` | Run tests with framework detection |
| `test` | Write tests using TDD methodology |

### todo

| Command | Description |
|---------|-------------|
| `add` | Add todo to SQLite DB |
| `complete` | Mark todo as completed |
| `due` | Set todo due date |
| `list` | List todos from SQLite DB |
| `remove` | Remove todo from DB |
| `undo` | Mark completed todo as incomplete |

### util

| Command | Description |
|---------|-------------|
| `audit-components` | Audit agents, skills, commands, hooks |
| `ultra-think` | Deep multi-dimensional analysis |
| `update-dependencies` | Update and modernize dependencies |

## Skills

Skills are bundles of domain expertise that agents can reference. They may include reference documentation,
helper scripts, and generated assets.

| Skill | Description | Resources |
|-------|-------------|-----------|
| `action-item-organizer` | Extract action items into prioritized checklists | refs |
| `agile-ceremonies` | Sprint management and agile ceremonies | refs |
| `ai-ethics` | Responsible AI development and ethics | refs |
| `claude-hooks` | Claude Code hooks configuration | refs |
| `cloud-infrastructure` | Cloud architecture for AWS/Azure/GCP | refs |
| `cocoindex` | CocoIndex data transformation pipelines | refs |
| `code-context-finder` | Knowledge graph and code relationship analysis | refs, scripts |
| `code-review` | Expert code review methodology | refs |
| `command-optimization` | CLI command development patterns | refs |
| `context-management` | Multi-agent context orchestration | refs |
| `database-optimization` | SQL query and database optimization | refs |
| `dead-code-removal` | Unused code detection and removal | scripts |
| `debugging` | Comprehensive debugging workflows | refs, scripts |
| `dependency-management` | Dependency updates and vulnerability scanning | refs, scripts |
| `design-docs` | (DEPRECATED) Use 'documentation' instead | refs |
| `developer-growth-analysis` | Analyze coding patterns for growth | - |
| `documentation` | Comprehensive documentation specialist | refs |
| `example-skill` | Example patterns for skill creation | refs |
| `file-organizer` | Intelligent file and folder organization | - |
| `git-commit-helper` | Generate commit messages from diffs | refs |
| `git-workflow` | Git workflow and PR management | refs |
| `global-standards` | Project-wide coding standards | - |
| `golang-enterprise-patterns` | Enterprise Go architecture patterns | - |
| `golang-performance` | Go performance optimization | - |
| `jira` | Jira Cloud integration and JQL | refs, scripts |
| `meta-cognitive-reasoning` | Evidence-based analysis and hypothesis testing | - |
| `migrations` | (DEPRECATED) Use 'documentation' instead | refs |
| `n8n` | n8n workflow automation patterns | refs, scripts, assets |
| `network-engineering` | Network architecture and troubleshooting | refs |
| `nextjs-architecture` | Next.js App Router and Server Components | - |
| `pdf-processing` | PDF text extraction and form filling | - |
| `performance` | Comprehensive performance optimization | - |
| `prompt-optimization` | LLM prompt optimization techniques | - |
| `python-scripting` | Python scripting with uv and PEP 723 | refs |
| `security-audit` | Security auditing and vulnerability assessment | - |
| `seo-analysis` | SEO analysis and optimization | - |
| `shell-scripting` | Shell scripting best practices | refs |
| `skill-creator` | Guide for creating effective skills | refs, scripts |
| `skill-share` | Create and share skills via Slack | - |
| `spec-driven-development` | SpecKit-based AI-assisted development | - |
| `technical-research` | Technical spike and research investigation | refs |
| `testing` | Comprehensive testing and TDD | refs, scripts |
| `tdd-pytest` | Python/pytest TDD specialist | - |
| `tool-presets` | Tool preset configurations | - |
| `web-accessibility` | WCAG compliance and accessibility | - |

## Hooks

Hooks run automatically in response to Claude Code events. They are organized by type.

### Hook Types Overview

| Type | Count | Description |
|------|-------|-------------|
| [analyzers](#analyzers) | 17 | Code analysis on file changes |
| [context](#context-hooks) | 8 | Context injection and management |
| [lifecycle](#lifecycle) | 9 | Session start/end events |
| [workflows](#workflows) | 7 | Multi-step workflow automation |
| [tests](#tests) | 1 | Test hooks |

### analyzers

Hooks that analyze code when files change.

| Hook | Description |
|------|-------------|
| `check_any_changed` | Check any changed files |
| `check_comment_replacement` | Detect comment replacement issues |
| `check_unused_parameters` | Find unused function parameters |
| `complexity_checker` | Check code complexity |
| `dependency_vuln_check` | Check dependency vulnerabilities |
| `git_diff_logger` | Log git diffs |
| `import_validator` | Validate imports |
| `lint_changed` | Lint changed files |
| `lint_project` | Lint entire project |
| `security_audit` | Security audit on changes |
| `test_changed` | Run tests for changed files |
| `test_project` | Run project tests |
| `todo_tracker` | Track TODOs in code |
| `typecheck_changed` | Type check changed files |
| `typecheck_on_save` | Type check on file save |
| `typecheck_project` | Type check entire project |

### context-hooks

Hooks for context injection and management.

| Hook | Description |
|------|-------------|
| `codebase_map` | Generate codebase map |
| `context_injector` | Inject relevant context |
| `jit_context` | Just-in-time context loading |
| `project_detector` | Detect project type |
| `recent_changes` | Show recent code changes |
| `related_files` | Find related files |
| `session_logger` | Log session activity |

### lifecycle

Hooks for session lifecycle events.

| Hook | Description |
|------|-------------|
| `check_todos` | Check pending TODOs |
| `cleanup_handler` | Clean up on session end |
| `commit_suggester` | Suggest commits |
| `create_checkpoint` | Create session checkpoint |
| `export_conversation` | Export conversation history |
| `knowledge_update` | Update knowledge graph |
| `metrics_collector` | Collect session metrics |
| `self_review` | Self-review changes |
| `session_summary` | Generate session summary |

### workflows

Hooks for multi-step workflow automation.

| Hook | Description |
|------|-------------|
| `post_tool_use` | After tool execution |
| `pre_tool_use` | Before tool execution |
| `session_end` | Session end workflow |
| `session_start` | Session start workflow |
| `subagent_stop` | Subagent completion |
| `todo_sync` | Sync TODO items |
| `user_prompt` | User prompt processing |

### tests

Test-related hooks.

| Hook | Description |
|------|-------------|
| `test_todo_sync` | Test TODO synchronization |

## Templates

Templates provide scaffolds for creating new components. Use these as starting points.

### Component Templates

| Template | Purpose |
|----------|---------|
| `AGENT_PLAYBOOK.template` | Agent operational playbook |
| `AGENT_SKILL.template` | New skill definition |
| `CLAUDE_HOOK.template` | New hook definition |
| `SLASH_COMMAND.template` | New slash command |
| `SUBAGENT.template` | New agent configuration |

### Documentation Templates

| Template | Purpose |
|----------|---------|
| `API_DOCUMENTATION.template` | API documentation |
| `ARCHITECTURE_DECISION_RECORD.template` | ADR for design decisions |
| `CHANGELOG.template` | Release changelog |
| `CODE_ANALYSIS.template` | Code analysis report |
| `COMPETITIVE_ANALYSIS.template` | Competitive analysis |
| `DEPENDENCY_AUDIT.template` | Dependency audit report |
| `DESIGN_SPEC.template` | Design specification |
| `INCIDENT_POSTMORTEM.template` | Incident postmortem |
| `MIGRATION_GUIDE.template` | Migration guide |
| `ONBOARDING_GUIDE.template` | Developer onboarding |
| `PERFORMANCE_ANALYSIS.template` | Performance analysis |
| `REFACTORING_PLAN.template` | Refactoring plan |
| `RESEARCH_REPORT.template` | Research report |
| `RUNBOOK.template` | Operational runbook |
| `SECURITY_AUDIT.template` | Security audit report |
| `TECHNICAL_SPIKE.template` | Technical investigation |
| `TESTING_REPORT.template` | Test coverage report |

### Workflow Templates

| Template | Purpose |
|----------|---------|
| `DAILY_STANDUP.template` | Daily standup notes |
| `GIT_COMMIT.template` | Git commit message |
| `PULL_REQUEST.template` | PR description |
| `RETROSPECTIVE.template` | Sprint retrospective |
| `TODO_LIST.template` | TODO list structure |

## Finding Components

### By Task

| Task | Recommended Component |
|------|-----------------------|
| Review my code | Agent: `code-reviewer` |
| Fix a bug | Agent: `debugger` |
| Write tests | Agent: `test-engineer` |
| Create PR | Command: `/git:create-pr` |
| Run tests | Command: `/test:run` |
| Database optimization | Agent: `database-optimizer` |
| Cloud architecture | Agent: `cloud-architect` |
| Research a topic | Agent: `research-orchestrator-v2` |

### By Domain

| Domain | Key Agents |
|--------|------------|
| Frontend | `frontend-developer`, `react-performance-optimizer`, `css-expert` |
| Backend | `backend-architect`, `database-expert`, `api-documenter` |
| DevOps | `devops-engineer`, `docker-expert`, `github-actions-expert` |
| AI/ML | `ai-engineer`, `ml-engineer`, `data-scientist` |
| Testing | `test-engineer`, `pytest-tdd-expert`, `integration-tester` |

## See Also

- [Getting Started](GETTING_STARTED.md) - Quick start guide
- [Using Agents](USING_AGENTS.md) - Detailed agent guide
- [Using Skills](USING_SKILLS.md) - Skills usage guide
- [Using Commands](USING_COMMANDS.md) - Commands guide
- [Using Hooks](USING_HOOKS.md) - Hooks automation guide
