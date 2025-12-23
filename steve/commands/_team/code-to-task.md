---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: commands
---

# Convert code analysis to Linear tasks using full project context

## Purpose

This command performs **context-aware** analysis of your codebase to identify actionable work items. Unlike simple pattern matching for TODO comments, it uses:

- **Knowledge graph** to understand prior decisions and existing patterns
- **Git history** to identify code churn, recent changes, and ownership
- **File relationships** to understand dependencies and impact radius
- **Project architecture** to group related work logically
- **Semantic analysis** to understand code intent, not just markers

## Usage

```bash
# Full context-aware analysis
claude "Analyze the codebase for actionable tasks"

# Focused on specific area with context
claude "Find improvement opportunities in the authentication module"

# Analyze recent changes for follow-up work
claude "What tasks should we create based on recent commits?"

# Architecture-aware technical debt
claude "Identify technical debt considering our architecture patterns"
```

## Instructions

### 1. Gather Project Context

Before scanning code, build comprehensive understanding of the project:

#### 1.1 Git Context (Deep Analysis)

```bash
# Current state
git status --porcelain
git branch --show-current
git log -1 --format="%H %s"

# Recent activity (last 30 days)
git log --since="30 days ago" --pretty=format:"%h|%an|%ad|%s" --date=short

# File churn analysis (most changed files)
git log --since="30 days ago" --pretty=format: --name-only | sort | uniq -c | sort -rn | head -20

# Code ownership by directory
git shortlog -sn --all -- "src/"

# Active branches and their focus
git branch -a --sort=-committerdate | head -10

# Uncommitted work in progress
git diff --stat
git diff --cached --stat

# Recent merges to main (completed work)
git log main --merges --since="14 days ago" --pretty=format:"%s"
```

```python
async def gather_git_context():
    """Build comprehensive git context."""
    return {
        # Current state
        'current_branch': await run('git branch --show-current'),
        'uncommitted_changes': await run('git status --porcelain'),
        'head_commit': await run('git log -1 --format="%H %s"'),

        # Recent history
        'recent_commits': await parse_git_log(days=30),
        'merged_prs': await get_merged_prs(days=14),

        # Churn analysis
        'file_churn': await analyze_churn(days=30),
        'hotspot_files': await identify_hotspots(threshold=10),

        # Ownership mapping
        'ownership': await build_ownership_map(),
        'active_contributors': await get_active_contributors(days=30),

        # Work in progress
        'active_branches': await get_active_branches(),
        'stale_branches': await get_stale_branches(days=30),

        # Commit patterns
        'commit_types': await categorize_commits(days=30),
        'fix_frequency': await count_fix_commits(days=30),
        'revert_count': await count_reverts(days=30)
    }


async def analyze_churn(days: int = 30):
    """Identify files with high change frequency."""
    log = await run(f'git log --since="{days} days ago" --pretty=format: --name-only')
    files = [f for f in log.split('\n') if f.strip()]

    churn = Counter(files)
    return [
        {
            'file': file,
            'changes': count,
            'avg_changes_per_week': count / (days / 7),
            'is_hotspot': count > 10
        }
        for file, count in churn.most_common(50)
    ]


async def build_ownership_map():
    """Map files/directories to primary owners."""
    ownership = {}

    # Get ownership by directory
    dirs = await get_source_directories()
    for dir in dirs:
        contributors = await run(f'git shortlog -sn --all -- "{dir}"')
        parsed = parse_shortlog(contributors)
        if parsed:
            ownership[dir] = {
                'primary': parsed[0]['author'],
                'contributors': parsed[:3],
                'bus_factor': len([c for c in parsed if c['commits'] > 5])
            }

    return ownership


async def categorize_commits(days: int = 30):
    """Categorize recent commits by type."""
    commits = await parse_git_log(days=days)

    categories = {
        'features': [],
        'fixes': [],
        'refactors': [],
        'docs': [],
        'tests': [],
        'chores': [],
        'reverts': []
    }

    patterns = {
        'features': r'^(feat|feature|add|implement)',
        'fixes': r'^(fix|bugfix|hotfix|patch)',
        'refactors': r'^(refactor|restructure|reorganize|clean)',
        'docs': r'^(doc|docs|documentation)',
        'tests': r'^(test|tests|testing|spec)',
        'chores': r'^(chore|build|ci|deps)',
        'reverts': r'^(revert)'
    }

    for commit in commits:
        for category, pattern in patterns.items():
            if re.match(pattern, commit['message'], re.I):
                categories[category].append(commit)
                break

    return {
        cat: {
            'count': len(commits),
            'percentage': len(commits) / len(commits) * 100 if commits else 0,
            'recent': commits[:5]
        }
        for cat, commits in categories.items()
    }
```

#### 1.2 Project Context (Structure & Patterns)

```python
async def gather_project_context():
    """Build comprehensive project understanding."""
    return {
        # Documentation
        'claude_md': await parse_claude_md(),
        'readme': await parse_readme(),
        'architecture_docs': await find_architecture_docs(),
        'adrs': await find_adrs(),

        # Project structure
        'project_type': await detect_project_type(),
        'tech_stack': await detect_tech_stack(),
        'modules': await identify_modules(),
        'entry_points': await find_entry_points(),

        # Dependencies
        'dependencies': await parse_dependencies(),
        'internal_deps': await build_internal_dep_graph(),
        'outdated_deps': await check_outdated_deps(),

        # Quality indicators
        'test_coverage': await get_test_coverage(),
        'lint_config': await parse_lint_config(),
        'ci_config': await parse_ci_config(),

        # Conventions
        'conventions': await extract_conventions(),
        'patterns': await identify_patterns()
    }


async def parse_claude_md():
    """Extract actionable information from CLAUDE.md."""
    content = await read_if_exists('CLAUDE.md')
    if not content:
        return None

    return {
        'raw': content,
        'rules': extract_rules(content),
        'conventions': extract_conventions(content),
        'file_boundaries': extract_file_boundaries(content),
        'tech_stack': extract_tech_stack_info(content),
        'workflows': extract_workflows(content)
    }


async def detect_project_type():
    """Detect project type from structure and config files."""
    indicators = {
        'nextjs': ['next.config.js', 'next.config.ts', 'app/', 'pages/'],
        'react': ['src/App.tsx', 'src/App.jsx', 'create-react-app'],
        'python': ['pyproject.toml', 'setup.py', 'requirements.txt'],
        'node': ['package.json', 'node_modules/'],
        'go': ['go.mod', 'go.sum'],
        'rust': ['Cargo.toml', 'Cargo.lock'],
        'monorepo': ['packages/', 'apps/', 'lerna.json', 'pnpm-workspace.yaml']
    }

    detected = []
    for project_type, files in indicators.items():
        for file in files:
            if await file_exists(file):
                detected.append(project_type)
                break

    return detected


async def identify_modules():
    """Identify logical modules in the codebase."""
    modules = []

    # Check for explicit module boundaries
    src_dirs = await glob('src/*/')
    for dir in src_dirs:
        if await is_module_boundary(dir):
            modules.append({
                'name': Path(dir).name,
                'path': dir,
                'type': await classify_module(dir),
                'exports': await find_exports(dir),
                'dependencies': await find_module_deps(dir)
            })

    return modules


async def extract_conventions():
    """Extract coding conventions from project config and docs."""
    conventions = []

    # From CLAUDE.md
    if claude_md := await read_if_exists('CLAUDE.md'):
        conventions.extend(parse_conventions_from_markdown(claude_md))

    # From ESLint/Prettier
    if eslint := await read_if_exists('.eslintrc.json'):
        conventions.extend(parse_eslint_conventions(eslint))

    # From pyproject.toml
    if pyproject := await read_if_exists('pyproject.toml'):
        conventions.extend(parse_python_conventions(pyproject))

    # From editorconfig
    if editorconfig := await read_if_exists('.editorconfig'):
        conventions.extend(parse_editorconfig(editorconfig))

    return conventions


async def identify_patterns():
    """Identify established patterns in the codebase."""
    patterns = []

    # Error handling pattern
    error_samples = await grep_codebase(r'catch|except|Error', limit=20)
    patterns.append({
        'name': 'error_handling',
        'examples': error_samples,
        'detected_style': classify_error_handling(error_samples)
    })

    # API patterns
    api_samples = await grep_codebase(r'fetch|axios|request', limit=20)
    patterns.append({
        'name': 'api_calls',
        'examples': api_samples,
        'detected_style': classify_api_pattern(api_samples)
    })

    # State management
    state_samples = await grep_codebase(r'useState|useReducer|redux|zustand', limit=20)
    patterns.append({
        'name': 'state_management',
        'examples': state_samples,
        'detected_style': classify_state_pattern(state_samples)
    })

    return patterns
```

#### 1.3 Knowledge Graph Context

```python
async def gather_memory_context():
    """Query knowledge graph for relevant context."""
    return {
        # Architectural decisions
        'decisions': await memory.search(
            query="architectural decision OR ADR OR design decision",
            limit=20
        ),

        # Known technical debt
        'tracked_debt': await memory.search(
            query="technical debt OR tech debt OR known issue",
            limit=30
        ),

        # Previous analyses
        'prior_analyses': await memory.search(
            query="code analysis session OR task creation",
            limit=10
        ),

        # Team conventions
        'conventions': await memory.search(
            query="convention OR coding standard OR pattern",
            limit=20
        ),

        # Related entities
        'modules': await memory.search(
            query="module OR component OR service",
            entity_type="code_module",
            limit=50
        )
    }
```

#### 1.4 Combined Context Builder

```python
async def build_full_context(scope: str = None):
    """Build complete context for analysis."""

    # Gather all context sources in parallel
    git_ctx, project_ctx, memory_ctx = await asyncio.gather(
        gather_git_context(),
        gather_project_context(),
        gather_memory_context()
    )

    # Merge and enrich
    context = {
        'git': git_ctx,
        'project': project_ctx,
        'memory': memory_ctx,
        'scope': scope,

        # Derived insights
        'insights': {
            'high_risk_areas': identify_high_risk(git_ctx, project_ctx),
            'active_work': identify_active_work(git_ctx),
            'stale_areas': identify_stale_areas(git_ctx),
            'convention_gaps': find_convention_gaps(project_ctx),
            'ownership_gaps': find_ownership_gaps(git_ctx)
        }
    }

    # Add cross-references
    context['cross_refs'] = {
        'debt_to_files': map_debt_to_files(memory_ctx, git_ctx),
        'decisions_to_code': map_decisions_to_code(memory_ctx, project_ctx),
        'owners_to_modules': map_owners_to_modules(git_ctx, project_ctx)
    }

    return context


def identify_high_risk(git_ctx, project_ctx):
    """Identify high-risk areas based on multiple signals."""
    high_risk = []

    # High churn + low coverage
    hotspots = git_ctx.get('hotspot_files', [])
    coverage = project_ctx.get('test_coverage', {})

    for hotspot in hotspots:
        file_coverage = coverage.get(hotspot['file'], 100)
        if file_coverage < 50:
            high_risk.append({
                'file': hotspot['file'],
                'reason': 'High churn with low test coverage',
                'churn': hotspot['changes'],
                'coverage': file_coverage,
                'risk_score': (hotspot['changes'] * (100 - file_coverage)) / 100
            })

    # Many fixes in same area
    fix_locations = [c['files'] for c in git_ctx.get('commit_types', {}).get('fixes', {}).get('recent', [])]
    fix_counts = Counter(flatten(fix_locations))
    for file, count in fix_counts.most_common(10):
        if count >= 3:
            high_risk.append({
                'file': file,
                'reason': f'{count} bug fixes in last 30 days',
                'risk_score': count * 10
            })

    return sorted(high_risk, key=lambda x: x['risk_score'], reverse=True)
```

### 2. Semantic Code Analysis

Analyze code for actionable items using semantic understanding:

```python
class ContextAwareAnalyzer:
    def __init__(self, context):
        self.context = context
        self.findings = []

    async def analyze(self, scope: str = None):
        """Perform context-aware analysis."""

        # 1. Analyze code patterns against conventions
        await self.check_convention_violations()

        # 2. Identify incomplete implementations
        await self.find_incomplete_code()

        # 3. Detect architectural drift
        await self.detect_architecture_drift()

        # 4. Find high-churn problem areas
        await self.analyze_code_churn()

        # 5. Check for missing tests in critical paths
        await self.find_untested_critical_paths()

        # 6. Identify outdated patterns
        await self.find_outdated_patterns()

        # 7. Standard marker scan (enriched with context)
        await self.scan_markers_with_context()

        return self.findings

    async def check_convention_violations(self):
        """Compare code against documented conventions."""
        conventions = self.context['docs'].get('claude_md', {})

        for convention in parse_conventions(conventions):
            violations = await find_violations(convention)
            for v in violations:
                self.findings.append({
                    'type': 'convention_violation',
                    'title': f"Convention: {convention.name}",
                    'description': v.description,
                    'context': {
                        'convention_source': 'CLAUDE.md',
                        'expected': convention.pattern,
                        'found': v.actual
                    },
                    'priority': 'medium',
                    'file_path': v.file,
                    'line_number': v.line
                })

    async def find_incomplete_code(self):
        """Detect incomplete implementations semantically."""
        patterns = [
            # Functions that throw "not implemented"
            r'raise\s+NotImplementedError',
            r'throw\s+new\s+Error\(["\']not implemented',

            # Empty function bodies
            r'(def|function)\s+\w+[^{]*{\s*}',
            r'(def|function)\s+\w+[^:]*:\s*pass\s*$',

            # Placeholder returns
            r'return\s+(None|null|undefined)\s*#?\s*(placeholder|todo|fixme)?',

            # Stub implementations
            r'#\s*stub|//\s*stub|/\*\s*stub',
        ]

        for pattern in patterns:
            matches = await grep_codebase(pattern)
            for match in matches:
                # Enrich with git context
                last_modified = await git_blame(match.file, match.line)

                self.findings.append({
                    'type': 'incomplete_implementation',
                    'title': f"Incomplete: {match.function_name or match.file}",
                    'description': 'Implementation appears incomplete',
                    'context': {
                        'last_modified': last_modified,
                        'code_snippet': match.context,
                        'related_tests': await find_related_tests(match.file)
                    },
                    'priority': 'high' if in_critical_path(match) else 'medium',
                    'file_path': match.file,
                    'line_number': match.line
                })

    async def detect_architecture_drift(self):
        """Identify code that violates architectural patterns."""
        arch_patterns = self.context.get('architecture_patterns', [])

        violations = []

        # Check layer violations (e.g., UI importing database directly)
        layer_violations = await check_layer_boundaries()
        violations.extend(layer_violations)

        # Check for circular dependencies
        circular_deps = await find_circular_dependencies()
        violations.extend(circular_deps)

        # Check module boundary violations
        boundary_violations = await check_module_boundaries()
        violations.extend(boundary_violations)

        for v in violations:
            self.findings.append({
                'type': 'architecture_drift',
                'title': f"Architecture: {v.rule_name}",
                'description': v.explanation,
                'context': {
                    'expected_pattern': v.expected,
                    'actual': v.found,
                    'impact': v.impact_analysis
                },
                'priority': 'high',
                'file_path': v.file,
                'line_number': v.line
            })

    async def analyze_code_churn(self):
        """Find files with high change frequency indicating problems."""
        churn_data = self.context['git']['file_churn']

        hotspots = [f for f in churn_data if f.changes > 10 and f.days < 30]

        for hotspot in hotspots:
            # Analyze why this file changes so much
            recent_commits = await git_log_file(hotspot.path, limit=10)
            patterns = analyze_commit_patterns(recent_commits)

            if patterns.indicates_problem:
                self.findings.append({
                    'type': 'code_churn',
                    'title': f"High Churn: {hotspot.path}",
                    'description': f"Modified {hotspot.changes} times in {hotspot.days} days",
                    'context': {
                        'commit_patterns': patterns.summary,
                        'likely_cause': patterns.diagnosis,
                        'suggested_action': patterns.recommendation
                    },
                    'priority': 'medium',
                    'file_path': hotspot.path
                })

    async def find_untested_critical_paths(self):
        """Identify critical code paths without test coverage."""
        coverage = self.context['structure'].get('test_coverage', {})
        critical_files = identify_critical_files(self.context['structure'])

        for file in critical_files:
            file_coverage = coverage.get(file, 0)
            if file_coverage < 50:
                self.findings.append({
                    'type': 'missing_tests',
                    'title': f"Low Coverage: {file}",
                    'description': f"Critical file has only {file_coverage}% test coverage",
                    'context': {
                        'current_coverage': file_coverage,
                        'why_critical': explain_criticality(file),
                        'suggested_tests': suggest_test_cases(file)
                    },
                    'priority': 'high',
                    'file_path': file
                })

    async def find_outdated_patterns(self):
        """Detect deprecated patterns based on project evolution."""

        # Check knowledge graph for pattern migrations
        migrations = await memory.search("deprecated pattern OR migration")

        for migration in migrations:
            old_pattern = migration.old_pattern
            new_pattern = migration.new_pattern

            usages = await grep_codebase(old_pattern)
            if usages:
                self.findings.append({
                    'type': 'outdated_pattern',
                    'title': f"Outdated: {migration.name}",
                    'description': f"Found {len(usages)} usages of deprecated pattern",
                    'context': {
                        'old_pattern': old_pattern,
                        'new_pattern': new_pattern,
                        'migration_guide': migration.guide,
                        'locations': [u.location for u in usages]
                    },
                    'priority': 'medium',
                    'files_affected': len(set(u.file for u in usages))
                })

    async def scan_markers_with_context(self):
        """Scan TODO/FIXME markers but enrich with context."""
        markers = await grep_codebase(r'TODO|FIXME|HACK|XXX|OPTIMIZE')

        for marker in markers:
            # Skip if already tracked in Linear
            if await is_tracked_in_linear(marker):
                continue

            # Enrich with git context
            blame = await git_blame(marker.file, marker.line)

            # Determine priority from context
            priority = self.calculate_priority(marker, blame)

            # Group with related markers
            related = self.find_related_markers(marker, markers)

            self.findings.append({
                'type': marker.type.lower(),
                'title': marker.text,
                'description': marker.full_comment,
                'context': {
                    'author': blame.author,
                    'age_days': blame.age_days,
                    'related_markers': [r.location for r in related],
                    'file_criticality': get_file_criticality(marker.file),
                    'in_active_development': is_recently_changed(marker.file)
                },
                'priority': priority,
                'file_path': marker.file,
                'line_number': marker.line
            })

    def calculate_priority(self, marker, blame):
        """Calculate priority based on multiple factors."""
        score = 0

        # Type-based priority
        if 'SECURITY' in marker.text.upper():
            score += 40
        elif marker.type in ['FIXME', 'HACK', 'XXX']:
            score += 20
        elif marker.type == 'TODO':
            score += 10

        # Age penalty (older = higher priority)
        if blame.age_days > 180:
            score += 15
        elif blame.age_days > 90:
            score += 10
        elif blame.age_days > 30:
            score += 5

        # Critical path bonus
        if self.is_critical_path(marker.file):
            score += 15

        # High churn area bonus
        if marker.file in self.high_churn_files:
            score += 10

        # Map score to priority
        if score >= 40:
            return 'urgent'
        elif score >= 25:
            return 'high'
        elif score >= 15:
            return 'medium'
        return 'low'
```

### 3. Intelligent Task Grouping

Group findings by logical relationships, not just file location:

```python
class ContextAwareGrouper:
    def __init__(self, context, findings):
        self.context = context
        self.findings = findings

    def group(self):
        """Group findings into coherent tasks."""
        groups = {
            'by_feature': self.group_by_feature(),
            'by_epic': self.group_by_epic(),
            'by_owner': self.group_by_owner(),
            'by_dependency': self.group_by_dependency()
        }

        return self.select_best_grouping(groups)

    def group_by_feature(self):
        """Group by feature/module boundaries."""
        modules = self.context['structure']['modules']
        groups = defaultdict(list)

        for finding in self.findings:
            module = self.get_module(finding['file_path'], modules)
            groups[module].append(finding)

        return groups

    def group_by_epic(self):
        """Group by existing Linear epics/projects."""
        existing_epics = self.context.get('linear_epics', [])
        groups = defaultdict(list)

        for finding in self.findings:
            matching_epic = self.match_to_epic(finding, existing_epics)
            if matching_epic:
                groups[matching_epic.id].append(finding)
            else:
                groups['unassigned'].append(finding)

        return groups

    def group_by_owner(self):
        """Group by code ownership from git history."""
        ownership = self.context['git']['authors']
        groups = defaultdict(list)

        for finding in self.findings:
            owner = ownership.get(finding['file_path'], 'unowned')
            groups[owner].append(finding)

        return groups

    def group_by_dependency(self):
        """Group related items by code dependencies."""
        dep_graph = self.context['structure']['dependencies']
        groups = []
        seen = set()

        for finding in self.findings:
            if finding['file_path'] in seen:
                continue

            # Find all related files via dependency graph
            related_files = dep_graph.get_connected(finding['file_path'])
            related_findings = [
                f for f in self.findings
                if f['file_path'] in related_files
            ]

            if len(related_findings) > 1:
                groups.append({
                    'type': 'dependency_group',
                    'root': finding,
                    'related': related_findings,
                    'reason': 'Files are interconnected via imports'
                })
                seen.update(f['file_path'] for f in related_findings)

        return groups
```

### 4. Context-Enriched Task Creation

Create tasks with full context for actionability:

```python
async def create_enriched_tasks(grouped_findings, context):
    """Create Linear tasks with rich context."""
    created = []

    for group in grouped_findings:
        # Check if similar work is already tracked
        existing = await linear.search(
            f"{group.title} OR {group.primary_file}"
        )
        if existing:
            # Add as comment to existing task instead
            await linear.add_comment(
                existing[0].id,
                format_as_update(group)
            )
            continue

        # Build rich description
        description = build_rich_description(group, context)

        # Create task with context
        task = await linear.create_task({
            'title': group.title,
            'description': description,
            'priority': group.priority,
            'labels': derive_labels(group, context),
            'assignee': suggest_assignee(group, context),
            'estimate': estimate_from_context(group, context),
            'project': match_to_project(group, context)
        })

        created.append(task)

    return created


def build_rich_description(group, context):
    """Build description with full context."""
    sections = []

    # Summary
    sections.append(f"## Summary\n{group.summary}")

    # Context from knowledge graph
    if related_decisions := context.get('related_decisions'):
        sections.append("## Related Decisions")
        for decision in related_decisions:
            sections.append(f"- {decision.title}: {decision.summary}")

    # Code locations with snippets
    sections.append("## Affected Code")
    for finding in group.findings[:5]:  # Limit to 5 locations
        sections.append(f"### `{finding['file_path']}:{finding['line_number']}`")
        sections.append(f"```\n{finding.get('code_snippet', '')}\n```")

    if len(group.findings) > 5:
        sections.append(f"*...and {len(group.findings) - 5} more locations*")

    # Git context
    sections.append("## History")
    sections.append(f"- Last modified: {group.last_modified}")
    sections.append(f"- Primary contributors: {', '.join(group.contributors)}")
    sections.append(f"- Change frequency: {group.churn_level}")

    # Dependencies and impact
    if group.dependencies:
        sections.append("## Impact Analysis")
        sections.append(f"Files that depend on this: {len(group.dependents)}")
        sections.append(f"Files this depends on: {len(group.dependencies)}")

    # Suggested approach
    if suggestion := generate_approach_suggestion(group, context):
        sections.append(f"## Suggested Approach\n{suggestion}")

    return "\n\n".join(sections)


def suggest_assignee(group, context):
    """Suggest assignee based on ownership and expertise."""
    # Primary contributor to affected files
    contributors = group.contributors

    # Check current workload
    for contributor in contributors:
        if get_workload(contributor) < THRESHOLD:
            return contributor

    return None  # Let team lead assign
```

### 5. Memory Integration

Store findings and track progress in knowledge graph:

```python
async def update_knowledge_graph(findings, created_tasks):
    """Update knowledge graph with analysis results."""

    # Store analysis session
    session = await memory.create_entity({
        'type': 'code_analysis_session',
        'date': datetime.now().isoformat(),
        'findings_count': len(findings),
        'tasks_created': len(created_tasks),
        'scope': analysis_scope
    })

    # Store significant findings as entities
    for finding in findings:
        if finding['priority'] in ['urgent', 'high']:
            entity = await memory.create_entity({
                'type': 'technical_debt',
                'category': finding['type'],
                'location': f"{finding['file_path']}:{finding.get('line_number', '')}",
                'description': finding['title'],
                'priority': finding['priority'],
                'linear_task': finding.get('linear_task_id')
            })

            # Create relationship to session
            await memory.create_relation(
                session.id, 'identified', entity.id
            )

    # Update existing debt tracking
    for task in created_tasks:
        await memory.add_observation(
            entity_name=task.related_entity,
            observation=f"Task {task.id} created for this item"
        )
```

## Example Output

```text
Context-Aware Code Analysis
===========================

[1/4] Gathering Git Context...
-------------------------------
Branch: feature/user-dashboard
Uncommitted: 3 files modified
Last commit: abc1234 "Add user preferences API"

Recent Activity (30 days):
  - 127 commits by 5 contributors
  - 23 features, 34 fixes, 12 refactors
  - 8 reverts detected (potential instability)

File Churn Hotspots:
  1. src/api/auth.ts          - 23 changes (HIGH)
  2. src/services/user.ts     - 18 changes (HIGH)
  3. src/utils/validation.ts  - 15 changes (MEDIUM)

Code Ownership:
  src/api/       -> @alice (primary), @bob, @carol
  src/services/  -> @bob (primary), @alice
  src/utils/     -> @carol (primary)
  Bus factor risk: src/payments/ (single contributor)

Active Branches:
  - feature/payment-refunds (3 days old, 12 commits)
  - fix/auth-race-condition (1 day old, 4 commits)
  - refactor/user-service (stale: 45 days)

[2/4] Gathering Project Context...
-----------------------------------
Project Type: Next.js + Python backend (monorepo)
Tech Stack: TypeScript, React, FastAPI, PostgreSQL

Modules Detected:
  - api/         (REST endpoints, 45 files)
  - services/    (business logic, 32 files)
  - components/  (React UI, 78 files)
  - utils/       (shared utilities, 23 files)

From CLAUDE.md:
  - "Services should use repositories, not direct DB access"
  - "All API endpoints must have integration tests"
  - "Use zod for runtime validation"

Test Coverage:
  - Overall: 67%
  - Critical gaps: src/payments/ (12%), src/auth/ (34%)

[3/4] Querying Knowledge Graph...
----------------------------------
Found 15 related entities:
  - 5 architectural decisions (ADR-001 through ADR-005)
  - 7 tracked technical debt items
  - 3 previous analysis sessions

Related Decisions:
  - ADR-003: "Use repository pattern for data access"
  - ADR-005: "Migrate from REST to GraphQL (in progress)"

Already Tracked Debt:
  - "Refactor auth module" (Linear: ENG-234, assigned @alice)
  - "Add pagination to list endpoints" (Linear: ENG-256)

[4/4] Running Analysis...
--------------------------

Project Context Loaded:
- 15 architectural decisions from knowledge graph
- 127 recent commits analyzed
- 4 modules identified
- 2 existing Linear projects matched

Analysis Results
----------------

Found 34 actionable items:

ARCHITECTURE (3 items)
  [HIGH] Layer violation in UserService
         src/services/user.ts:45 imports database directly
         Violates: "Services should use repositories"
         Decision: ADR-007 (2024-01)
         Suggested: Inject UserRepository instead

  [HIGH] Circular dependency detected
         auth-module <-> user-module
         Impact: 8 files affected
         Root cause: shared types not extracted

  [MEDIUM] Module boundary violation
           api/routes imports from internal/

INCOMPLETE IMPLEMENTATIONS (5 items)
  [HIGH] NotImplementedError in PaymentProcessor.refund()
         src/payments/processor.py:234
         Age: 45 days (by @alice)
         Related tests exist but skip this method

  [HIGH] Stub implementation: exportToCSV()
         src/reports/exporter.ts:78
         In critical path: Yes (report generation)
         Blocking: 2 feature requests

CODE CHURN HOTSPOTS (2 items)
  [MEDIUM] src/api/auth.ts - 23 changes in 30 days
           Pattern: Bug fix -> revert -> fix cycle
           Diagnosis: Race condition not properly addressed
           Recommendation: Add integration test first

OUTDATED PATTERNS (4 items)
  [MEDIUM] Legacy error handling (12 usages)
           Old: try/catch with console.log
           New: ErrorBoundary + monitoring
           Migration guide: docs/error-handling.md

MISSING TEST COVERAGE (3 items)
  [HIGH] PaymentService - 12% coverage
         Critical file (handles money)
         Suggested tests: refund flow, partial payment

TODO/FIXME (17 items)
  [URGENT] SECURITY: SQL injection risk
           src/db/queries.ts:89 (age: 120 days)

  [HIGH] FIXME: Race condition (@bob, 60 days ago)
         src/sync/manager.ts:156
         In high-churn file

  [MEDIUM] TODO: Add pagination (8 related items)
           Grouped: All in api/routes/*.ts

Task Creation Summary
---------------------

Created 12 Linear tasks:
  - 2 added to "Security Hardening" project
  - 3 added to "Q1 Tech Debt" epic
  - 4 created as standalone (assigned by ownership)
  - 3 grouped as single "Add pagination" task

Skipped 22 items:
  - 15 already tracked in Linear
  - 4 in actively developed branches
  - 3 low-value (vague TODOs)

Knowledge Graph Updated:
  - 12 technical_debt entities created
  - Linked to analysis session for tracking

Recommendations
---------------
1. Schedule security review (2 urgent items)
2. Address auth.ts churn before adding features
3. Extract shared types to break circular dep
4. Consider dedicated pagination middleware
```

## Configuration

Create `.claude/code-to-task.json` to customize behavior:

```json
{
  "context_sources": {
    "knowledge_graph": true,
    "git_history_days": 30,
    "linear_integration": true
  },
  "analysis": {
    "include_architecture": true,
    "include_churn": true,
    "include_coverage": true,
    "marker_patterns": ["TODO", "FIXME", "HACK", "SECURITY"]
  },
  "grouping": {
    "strategy": "by_feature",
    "min_group_size": 2,
    "max_group_size": 10
  },
  "task_creation": {
    "auto_assign": true,
    "link_to_projects": true,
    "add_estimates": true
  },
  "filters": {
    "ignore_paths": ["node_modules", "vendor", "dist"],
    "min_priority": "low",
    "max_age_days": null
  }
}
```

## Tips

- Run after major refactoring to catch drift
- Use before sprint planning to identify hidden work
- Review knowledge graph connections for context
- Check git blame patterns for ownership
- Group related items to reduce task noise
- Link to existing epics when possible
