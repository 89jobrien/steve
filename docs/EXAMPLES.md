# Examples and Tutorials

Practical examples demonstrating how to use Steve components effectively in real-world scenarios.

## Quick Start Examples

### Example 1: Code Review Workflow

Review code for quality issues using the code-reviewer agent.

**Command:**

```text
/dev:review-code src/main.py
```

**What happens:**

1. Command invokes `code-reviewer` agent
2. Agent loads `code-review` and `meta-cognitive-reasoning` skills
3. Agent reads target file using `Read, Grep, Glob` tools
4. Generates structured feedback with line references

**Expected output:**

```text
## Code Review: src/main.py

### Security Issues (High Priority)
- Line 42: SQL query uses string concatenation - vulnerable to injection
- Line 78: API key hardcoded - should use environment variable

### Performance Issues (Medium Priority)
- Line 156: N+1 query pattern in loop - batch database calls

### Code Quality (Low Priority)
- Line 23: Function exceeds 50 lines - consider splitting
```

### Example 2: Test-Driven Development

Write tests using TDD methodology.

**Command:**

```text
/test:test src/auth.py
```

**What happens:**

1. Command invokes `pytest-tdd-expert` agent
2. Agent loads `testing`, `tdd-pytest`, and `tool-presets` skills
3. Agent analyzes target code for testable behaviors
4. Creates test file with comprehensive coverage

**Process:**

```text
1. Read src/auth.py to understand functionality
2. Identify testable behaviors:
   - User authentication
   - Token generation
   - Password validation
3. Write failing tests first (Red phase)
4. Run tests to confirm they fail
5. Guide implementation (Green phase)
6. Refactor for quality (Refactor phase)
```

### Example 3: Research with Parallel Agents

Conduct comprehensive research on a topic.

**Command:**

```text
/research quantum computing applications in healthcare
```

**What happens:**

1. `research-orchestrator-v2` plans research strategy
2. Delegates to specialized researchers in parallel:
   - `academic-researcher` - scholarly sources
   - `technical-researcher` - implementation details
   - `data-analyst` - statistics and trends
3. `fact-checker` validates claims
4. `research-synthesizer` consolidates findings
5. `report-generator` creates final report

**Output structure:**

```text
# Research Report: Quantum Computing in Healthcare

## Executive Summary
[Key findings and conclusions]

## Methodology
[Research approach and sources]

## Findings
### Academic Research
[Peer-reviewed papers and citations]

### Technical Implementations
[Current systems and projects]

### Market Analysis
[Industry trends and projections]

## Conclusions
[Synthesized insights]

## References
[Full citation list]
```

## Agent Composition Examples

### Example 4: Multi-Agent Code Quality Pipeline

Combine multiple agents for comprehensive code quality checks.

**Setup:**

```text
1. code-reviewer - Quality analysis
2. security-engineer - Security audit
3. performance-profiler - Performance check
4. test-engineer - Test coverage
```

**Workflow:**

```markdown
## Task

Run comprehensive quality analysis on the authentication module.

## Process

1. Use code-reviewer agent to analyze code quality in src/auth/
2. Use security-engineer agent to audit for vulnerabilities
3. Use performance-profiler agent to identify bottlenecks
4. Use test-engineer agent to assess test coverage

## Output

Consolidate findings into a single quality report with:
- Prioritized issues by severity
- Actionable recommendations
- Estimated effort to address
```

**Parallel execution:**

```text
Launch all four agents simultaneously for faster results.
Each agent operates independently with its own tools and skills.
```

### Example 5: Database Migration Workflow

Plan and execute a database migration safely.

**Agents involved:**

```text
database-architect - Schema design decisions
database-optimizer - Query performance
database-admin - Operational procedures
```

**Workflow:**

```text
Phase 1: Planning
- database-architect analyzes current schema
- database-architect designs target schema
- database-optimizer reviews query impact

Phase 2: Migration Script
- database-admin creates migration script
- database-admin adds rollback procedures
- database-optimizer adds index strategies

Phase 3: Validation
- database-admin tests migration locally
- database-optimizer profiles performance
- database-architect reviews final schema
```

## Skill Usage Examples

### Example 6: Using Testing Skill

The `testing` skill provides comprehensive test methodology.

**Skill content includes:**

- Test strategy framework
- Framework-agnostic patterns
- Coverage requirements
- CI/CD integration

**Agent configuration:**

```yaml
---
name: my-test-agent
description: Custom testing agent for my project
tools: Read, Write, Edit, Bash, Grep, Glob
skills: testing, global-standards
---
```

**How skills load:**

```text
1. Agent starts with prompt containing agent instructions
2. Claude loads skill content from ~/.claude/skills/testing/SKILL.md
3. If skill has references/, those are available on demand
4. Agent applies skill methodology to task
```

### Example 7: Using Machine Learning Skill

The `machine-learning` skill provides ML patterns and best practices.

**Used by agents:**

- `ai-engineer`
- `ml-engineer`
- `data-scientist`
- `nlp-engineer`

**Skill provides:**

```text
- Model selection guidance
- Training pipeline patterns
- Evaluation metrics
- Deployment strategies
- MLOps practices
```

**Example task:**

```text
User: "Help me choose between Random Forest and XGBoost for my classification task"

Agent (with machine-learning skill) responds with:
- Comparison of algorithms
- Decision criteria based on data characteristics
- Performance considerations
- Implementation recommendations
```

### Example 8: Creating a Custom Skill

Build a reusable skill for your domain.

**Directory structure:**

```text
skills/
└── my-methodology/
    ├── SKILL.md
    ├── references/
    │   ├── patterns.md
    │   └── examples.md
    └── scripts/
        └── validate.py
```

**SKILL.md content:**

```markdown
---
name: my-methodology
description: Custom methodology for domain-specific tasks
---

## When to Use

Use this skill when working on [specific domain] tasks that require [specific approach].

## Methodology

### Phase 1: Analysis

1. Identify requirements
2. Map dependencies
3. Assess risks

### Phase 2: Implementation

1. Apply pattern A for scenario X
2. Apply pattern B for scenario Y
3. Validate against checklist

### Phase 3: Verification

- [ ] All requirements met
- [ ] No regressions introduced
- [ ] Documentation updated

## Examples

See `references/examples.md` for detailed examples.
```

## Command Examples

### Example 9: Git Branch Cleanup

Clean up merged and stale branches.

**Command:**

```text
/git:clean-branches
```

**What it does:**

```text
1. Fetches latest from remote
2. Identifies merged branches
3. Identifies stale remote-tracking branches
4. Lists branches for deletion
5. Prompts for confirmation
6. Deletes approved branches
```

**Options:**

```text
/git:clean-branches --dry-run        # Preview only
/git:clean-branches --force          # Skip confirmation
/git:clean-branches --remote-only    # Only remote branches
/git:clean-branches --local-only     # Only local branches
```

### Example 10: Architecture Review

Review code architecture for patterns and issues.

**Command:**

```text
/dev:review-architecture --modules
```

**Scope options:**

```text
--modules      Review module organization
--patterns     Analyze design patterns
--dependencies Review dependency structure
--security     Security architecture review
```

**Output:**

```text
## Architecture Review

### Module Organization
- src/auth/ - Well-structured, single responsibility
- src/utils/ - Too many unrelated helpers (smell: grab-bag)
- src/services/ - Good dependency injection pattern

### Pattern Analysis
- Repository pattern used consistently in data layer
- Missing: Service layer abstraction
- Anti-pattern: Business logic in controllers

### Recommendations
1. Extract utility functions into domain-specific modules
2. Add service layer between controllers and repositories
3. Implement dependency injection container
```

## Hook Examples

### Example 11: Linting Hook

Automatically lint files after write operations.

**Registration (settings.json):**

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "command": "python ~/.claude/hooks/analyzers/lint_changed.py $FILE",
        "timeout": 10000
      }
    ]
  }
}
```

**Hook script (lint_changed.py):**

```python
#!/usr/bin/env python3
import sys
import subprocess
from pathlib import Path

SUPPORTED = {".py", ".js", ".ts", ".tsx"}

def main():
    file_path = sys.argv[1] if len(sys.argv) > 1 else None
    if not file_path:
        return

    suffix = Path(file_path).suffix
    if suffix not in SUPPORTED:
        return

    if suffix == ".py":
        result = subprocess.run(
            ["ruff", "check", file_path],
            capture_output=True,
            text=True
        )
        if result.stdout:
            print(f"Lint results for {file_path}:")
            print(result.stdout)

if __name__ == "__main__":
    main()
```

### Example 12: Context Injection Hook

Load relevant context at session start.

**Registration:**

```json
{
  "hooks": {
    "SessionStart": [
      {
        "command": "python ~/.claude/hooks/context/context_injector.py"
      }
    ]
  }
}
```

**What it provides:**

```text
- Project type detection
- Relevant file suggestions
- Recent changes summary
- Active branch information
```

### Example 13: Security Guard Hook

Check for secrets before allowing writes.

**Registration:**

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit",
        "command": "python ~/.claude/hooks/guards/check_secrets.py $FILE"
      }
    ]
  }
}
```

**Behavior:**

```text
1. Scans content for potential secrets
2. Blocks write if secrets detected
3. Reports specific findings
4. Suggests remediation
```

## End-to-End Workflows

### Example 14: New Feature Development

Complete workflow from planning to PR.

**Step 1: Plan the implementation**

```text
Use EnterPlanMode to design the feature architecture
```

**Step 2: Write tests first (TDD)**

```text
/test:test feature-description
```

**Step 3: Implement feature**

```text
Code implementation with agent assistance
```

**Step 4: Review code**

```text
/dev:review-code src/feature/
```

**Step 5: Run test suite**

```text
/test:run --coverage
```

**Step 6: Create PR**

```text
/git:create-pr
```

**Full sequence:**

```text
1. /quick-plan [feature requirements]
2. /test:test [feature module]
3. Implement code to pass tests
4. /dev:review-code [feature path]
5. /test:run --coverage
6. /analyze-codebase (parallel quality checks)
7. /git:clean-branches (cleanup first)
8. /git:create-pr
```

### Example 15: Bug Investigation

Systematic approach to debugging.

**Step 1: Triage**

```text
Use triage-expert agent to gather context:
- Error messages
- Stack traces
- Recent changes
- Related code
```

**Step 2: Debug**

```text
Use debugger agent with debugging skill:
- Reproduce issue
- Add instrumentation
- Identify root cause
```

**Step 3: Fix**

```text
Implement fix with test coverage
```

**Step 4: Validate**

```text
/test:run to verify fix
/dev:review-code to ensure quality
```

### Example 16: Documentation Update

Keep docs in sync with code.

**Step 1: Identify gaps**

```text
/docs:update-docs --sync
```

**Step 2: Generate documentation**

```text
Use documentation-expert agent:
- API documentation
- Architecture updates
- README improvements
```

**Step 3: Review**

```text
Validate accuracy against code
Check for broken links
Verify examples work
```

## Advanced Patterns

### Example 17: Custom Agent Composition

Create a specialized workflow by combining agents.

**Scenario:** Review PR with multiple perspectives

```text
1. code-reviewer - Code quality
2. security-engineer - Security issues
3. test-engineer - Test coverage
4. technical-writer - Documentation quality
```

**Orchestration:**

```markdown
## PR Review: #{pr_number}

### Process

1. Fetch PR diff and changed files
2. Launch parallel reviews:
   - code-reviewer on all changed code
   - security-engineer on security-sensitive files
   - test-engineer to assess test coverage
   - technical-writer on documentation changes
3. Consolidate findings
4. Prioritize issues
5. Generate summary

### Output

Structured review with:
- Blocking issues (must fix)
- Suggestions (should fix)
- Nitpicks (could fix)
```

### Example 18: Research to Implementation Pipeline

From research to working code.

**Phase 1: Research**

```text
/research [technology or approach]
```

**Phase 2: Design**

```text
Use architect-reviewer to design solution based on research
```

**Phase 3: Implementation**

```text
Use appropriate specialist agent:
- frontend-developer for UI
- backend-architect for API
- database-architect for data layer
```

**Phase 4: Integration**

```text
Use fullstack-developer to integrate components
```

**Phase 5: Testing**

```text
/test:test [implementation]
```

### Example 19: Automated Cleanup

Regular maintenance workflow.

**Weekly cleanup script:**

```text
1. /git:clean-branches           # Remove merged branches
2. /util:update-dependencies     # Check for updates
3. /test:report                  # Generate test coverage report
4. /dev:remove-ai-slop           # Clean AI-generated bloat
```

**Monthly audit:**

```text
1. /analyze-codebase             # Full quality analysis
2. /dev:review-architecture      # Architecture review
3. Security audit with security-engineer
4. Performance review with performance-profiler
```

## Troubleshooting Examples

### Example 20: Debugging Hook Issues

When hooks aren't working as expected.

**Check registration:**

```bash
cat ~/.claude/settings.json | python -m json.tool
```

**Test hook manually:**

```bash
python ~/.claude/hooks/analyzers/lint_changed.py /path/to/file.py
```

**Check matcher pattern:**

```json
{
  "matcher": "Write|Edit",
  "command": "..."
}
```

**Common fixes:**

1. Verify Python path is correct
2. Check file permissions
3. Add timeout if script is slow
4. Add error handling to script

## See Also

- [Using Agents](USING_AGENTS.md) - Agent invocation details
- [Using Commands](USING_COMMANDS.md) - Command reference
- [Using Hooks](USING_HOOKS.md) - Hook configuration
- [Best Practices](BEST_PRACTICES.md) - Quality guidelines
- [Troubleshooting](TROUBLESHOOTING.md) - Common issues
