# Development Guide

Complete guide for creating new Claude Code components in the Steve library.

## Overview

Steve components extend Claude Code's capabilities:

| Component | Purpose | Location |
|-----------|---------|----------|
| Agents | Specialized sub-agents for specific tasks | `agents/{domain}/` |
| Skills | Reusable domain expertise | `skills/{name}/` |
| Commands | Slash commands for workflows | `commands/{category}/` |
| Hooks | Event-driven automation | `hooks/{type}/` |

## Creating Agents

### Using Templates

```bash
# Copy the template
cp templates/AGENT_PLAYBOOK.template.md agents/domain/my-agent.md

# Edit the file
```

### Agent Structure

```markdown
---
name: my-agent
description: Action-oriented description with relevant keywords
tools: Read, Write, Edit, Grep, Glob
model: sonnet
skills: skill1, skill2
---

## Purpose

Clear statement of what this agent does and when to use it.

## Instructions

### Phase 1: Analysis

1. Read and understand the target
2. Identify key areas of focus
3. Plan the approach

### Phase 2: Execution

1. Apply methodology
2. Document findings
3. Generate output

## Best Practices

- Guideline 1
- Guideline 2

## Output Format

Description of expected output structure.
```

### Frontmatter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Unique identifier (kebab-case) |
| `description` | Yes | What agent does (used for selection) |
| `tools` | Recommended | Comma-separated tool list |
| `model` | Optional | `haiku`, `sonnet`, or `opus` |
| `skills` | Optional | Comma-separated skill references |
| `color` | Optional | Terminal color for output |

### Tool Selection Guide

**Read-only agents:**

```yaml
tools: Read, Grep, Glob
```

Use for: Analysis, review, research

**Modification agents:**

```yaml
tools: Read, Write, Edit, Grep, Glob
```

Use for: Code generation, refactoring, fixes

**Full-access agents:**

```yaml
tools: Read, Write, Edit, Bash, Grep, Glob
```

Use for: Testing, deployment, system tasks

**Orchestration agents:**

```yaml
tools: Task, Read
```

Use for: Coordinating other agents

### Model Selection Guide

| Model | Use Case | Cost | Speed |
|-------|----------|------|-------|
| `haiku` | Simple formatting, quick lookups | Low | Fast |
| `sonnet` | Most development tasks | Medium | Medium |
| `opus` | Complex reasoning, research | High | Slower |

### Writing Effective Descriptions

**Good descriptions:**

```yaml
# Specific with keywords
description: >-
  Reviews Python and JavaScript code for security vulnerabilities,
  performance issues, and best practice violations. Provides actionable
  feedback with line references.

# Clear scope
description: >-
  Optimizes PostgreSQL queries by analyzing execution plans, suggesting
  indexes, and rewriting inefficient patterns.
```

**Poor descriptions:**

```yaml
# Too vague
description: Helps with code

# Too broad
description: Does everything related to development
```

### Referencing Skills

Skills provide reusable expertise:

```yaml
---
name: my-reviewer
skills: code-review, security-audit
---

## Instructions

Apply the code-review methodology to analyze the target code.
Use security-audit guidelines to identify vulnerabilities.
```

### Example: Complete Agent

```markdown
---
name: api-designer
description: >-
  Designs RESTful APIs following best practices for resource naming,
  HTTP methods, status codes, versioning, and documentation. Creates
  OpenAPI specifications.
tools: Read, Write, Edit, Grep, Glob
model: sonnet
skills: documentation
---

## Purpose

Design consistent, well-documented REST APIs that follow industry
standards and are easy for developers to consume.

## Instructions

### 1. Analyze Requirements

- Read existing code to understand data models
- Identify resources and relationships
- Note authentication requirements

### 2. Design Endpoints

For each resource:

- Use plural nouns (`/users`, not `/user`)
- Apply standard HTTP methods (GET, POST, PUT, DELETE)
- Design consistent URL patterns

### 3. Define Responses

- Use appropriate status codes
- Design consistent error format
- Include pagination for collections

### 4. Generate Documentation

- Create OpenAPI specification
- Add examples for each endpoint
- Document authentication

## Best Practices

- Use kebab-case for multi-word paths
- Version APIs in URL (`/v1/users`)
- Return consistent error structures
- Support filtering and sorting

## Output Format

Provide:
1. Endpoint summary table
2. OpenAPI specification (YAML)
3. Example requests/responses
```

## Creating Skills

### Skill Structure

```text
skill-name/
├── SKILL.md           # Required: Main definition
├── references/        # Optional: Supporting documentation
│   ├── patterns.md
│   └── examples.md
├── scripts/           # Optional: Helper code
│   └── validate.py
└── assets/            # Optional: Generated outputs
```

### SKILL.md Template

```markdown
---
name: skill-name
description: What expertise this skill provides
---

## When to Use

Clear criteria for when this skill applies:

- Scenario 1
- Scenario 2
- Scenario 3

## Methodology

### Step 1: Title

Description of first step.

### Step 2: Title

Description of second step.

### Step 3: Title

Description of third step.

## Checklists

### Quality Checklist

- [ ] Item 1
- [ ] Item 2
- [ ] Item 3

### Completion Checklist

- [ ] Item 1
- [ ] Item 2

## Examples

### Example 1: Scenario

```text
Input: ...
Process: ...
Output: ...
```

### Example 2: Scenario

```text
Input: ...
Process: ...
Output: ...
```

## References

For detailed patterns, see `references/patterns.md`.

```

### Progressive Disclosure

Keep SKILL.md focused. Move details to `references/`:

**SKILL.md (focused):**

```markdown
## Methodology

1. Identify the pattern category
2. Apply the appropriate transformation
3. Validate the result

For the complete pattern catalog, see `references/patterns.md`.
```

**references/patterns.md (detailed):**

```markdown
# Pattern Catalog

## Category 1: Structural Patterns

### Pattern 1.1: Name

Description...
Example...

### Pattern 1.2: Name

Description...
Example...

## Category 2: Behavioral Patterns

...
```

### Example: Complete Skill

```markdown
---
name: api-versioning
description: Strategies and patterns for API version management
---

## When to Use

Apply this skill when:

- Designing new APIs that may evolve
- Planning breaking changes to existing APIs
- Migrating clients between API versions
- Deprecating old API versions

## Methodology

### 1. Choose Versioning Strategy

**URL Path Versioning:**

```text
/v1/users
/v2/users
```

Best for: Clear separation, easy routing

**Header Versioning:**

```text
Accept: application/vnd.api+json;version=1
```

Best for: Clean URLs, content negotiation

**Query Parameter:**

```text
/users?version=1
```

Best for: Simple implementation, debugging

### 2. Plan Version Lifecycle

1. **Active**: Current recommended version
2. **Deprecated**: Still works, migration encouraged
3. **Sunset**: End-of-life date announced
4. **Retired**: No longer available

### 3. Implement Compatibility

- Support N and N-1 versions minimum
- Provide migration guides
- Use deprecation headers
- Log version usage for planning

## Checklists

### New Version Checklist

- [ ] Document all breaking changes
- [ ] Create migration guide
- [ ] Update API documentation
- [ ] Announce deprecation timeline
- [ ] Set up version metrics

### Deprecation Checklist

- [ ] Add deprecation headers
- [ ] Notify API consumers
- [ ] Provide migration support
- [ ] Set sunset date

## Examples

### Adding a New Field (Non-breaking)

```json
// v1 response (unchanged)
{"id": 1, "name": "Alice"}

// v1 response (with new field)
{"id": 1, "name": "Alice", "email": "alice@example.com"}
```

### Renaming a Field (Breaking)

```json
// v1 response
{"userName": "alice"}

// v2 response
{"username": "alice"}
```

Requires new version due to field name change.

```

## Creating Commands

### Command Structure

```markdown
---
description: What this command does
argument-hint: [file-path] | [--option] | [value]
allowed-tools: Read, Write, Edit
---

## Task

Clear statement of what this command accomplishes.

## Process

1. Step one
2. Step two
3. Step three

## Output

Description of expected output.

## Examples

### Basic Usage

```text
/category:command-name file.py
```

### With Options

```text
/category:command-name --verbose src/
```

```

### Frontmatter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `description` | Yes | Command purpose |
| `argument-hint` | Recommended | Expected arguments |
| `allowed-tools` | Optional | Tool restrictions |

### Namespace Organization

Commands in subdirectories use namespace:

```text
commands/
├── dev/
│   └── review-code.md     # /dev:review-code
├── git/
│   └── clean-branches.md  # /git:clean-branches
└── test/
    └── run.md             # /test:run
```

### Using $ARGUMENTS

The `$ARGUMENTS` placeholder captures user input:

```markdown
## Task

Review the code at $ARGUMENTS for quality issues.

If no path provided, ask the user to specify one.
```

### Example: Complete Command

```markdown
---
description: Generate API documentation from code
argument-hint: [source-path] | [--format openapi|markdown]
allowed-tools: Read, Write, Grep, Glob
---

## Task

Generate comprehensive API documentation from the source code at $ARGUMENTS.

## Process

1. **Scan Source Code**
   - Find all route definitions
   - Extract endpoint metadata
   - Identify request/response schemas

2. **Generate Documentation**
   - Create endpoint summaries
   - Document parameters
   - Add example requests/responses

3. **Output Results**
   - Write to `docs/api/` directory
   - Create index file
   - Generate OpenAPI spec if requested

## Output

Provide:
- Summary of documented endpoints
- Location of generated files
- Any warnings or issues found

## Examples

### Document Single Module

```text
/docs:generate-api src/routes/users.py
```

### Document Entire API

```text
/docs:generate-api src/routes/
```

### Generate OpenAPI Spec

```text
/docs:generate-api src/routes/ --format openapi
```

```

## Creating Hooks

### Hook Types

| Type | Trigger | Use Case |
|------|---------|----------|
| `PreToolUse` | Before tool executes | Validation, guards |
| `PostToolUse` | After tool executes | Analysis, logging |
| `SessionStart` | Session begins | Context loading |
| `SessionEnd` | Session ends | Cleanup, summary |
| `UserPrompt` | User sends message | Context injection |

### Hook Structure

**Python file (hook_name.py):**

```python
#!/usr/bin/env python3
"""Brief description of what this hook does."""

import sys
from pathlib import Path

# Configuration
SUPPORTED_EXTENSIONS = {".py", ".js", ".ts"}
TIMEOUT_SECONDS = 10

def main():
    """Main entry point."""
    # Get file path from argument
    file_path = sys.argv[1] if len(sys.argv) > 1 else None

    if not file_path:
        return

    # Early exit for unsupported files
    if Path(file_path).suffix not in SUPPORTED_EXTENSIONS:
        return

    # Process file
    process_file(file_path)

def process_file(file_path: str) -> None:
    """Process the target file."""
    print(f"Processing {file_path}...")
    # Implementation here

if __name__ == "__main__":
    main()
```

**Documentation file (hook_name.md):**

```markdown
---
name: hook_name
description: What this hook does
trigger: PostToolUse
matcher: Write|Edit
---

## Purpose

Why this hook exists and what problem it solves.

## Configuration

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "command": "python ~/.claude/hooks/type/hook_name.py $FILE",
        "timeout": 10000
      }
    ]
  }
}
```

## Behavior

What happens when the hook triggers:

1. Step one
2. Step two
3. Step three

## Output

Description of hook output.

```

### Registration in settings.json

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit",
        "command": "python ~/.claude/hooks/guards/check_secrets.py $FILE"
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "command": "python ~/.claude/hooks/analyzers/lint_changed.py $FILE",
        "timeout": 10000
      }
    ],
    "SessionStart": [
      {
        "command": "python ~/.claude/hooks/lifecycle/session_start.py"
      }
    ],
    "SessionEnd": [
      {
        "command": "python ~/.claude/hooks/lifecycle/session_end.py"
      }
    ]
  }
}
```

### Matcher Patterns

```json
// Match single tool
"matcher": "Write"

// Match multiple tools (OR)
"matcher": "Write|Edit"

// Match any tool (omit matcher)
// No "matcher" field
```

### Best Practices for Hooks

**Performance:**

```python
# Early exit for unsupported files
SUPPORTED = {".py", ".js", ".ts"}

def main():
    file_path = sys.argv[1]
    if Path(file_path).suffix not in SUPPORTED:
        return  # Quick exit
```

**Error handling:**

```python
def main():
    try:
        process_file(sys.argv[1])
    except FileNotFoundError as e:
        print(f"File not found: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
```

**Informative output:**

```python
# Good: Informative
print(f"Linting {file_path}...")
print(f"Found {len(issues)} issues")

# Avoid: Silent or cryptic
print("done")
```

**Idempotency:**

```python
# Good: Safe to run multiple times
def ensure_formatted(file_path):
    if is_formatted(file_path):
        return
    format_file(file_path)

# Avoid: Accumulates on each run
def add_header(file_path):
    with open(file_path, "r+") as f:
        content = f.read()
        f.seek(0)
        f.write(HEADER + content)  # Adds header every time
```

### Example: Complete Hook

**hooks/analyzers/complexity_checker.py:**

```python
#!/usr/bin/env python3
"""Check code complexity and warn about complex functions."""

import ast
import sys
from pathlib import Path

COMPLEXITY_THRESHOLD = 10
SUPPORTED_EXTENSIONS = {".py"}

def calculate_complexity(node: ast.AST) -> int:
    """Calculate cyclomatic complexity of a function."""
    complexity = 1
    for child in ast.walk(node):
        if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
            complexity += 1
        elif isinstance(child, ast.BoolOp):
            complexity += len(child.values) - 1
    return complexity

def analyze_file(file_path: str) -> list[dict]:
    """Analyze file for complex functions."""
    issues = []
    with open(file_path) as f:
        tree = ast.parse(f.read())

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            complexity = calculate_complexity(node)
            if complexity > COMPLEXITY_THRESHOLD:
                issues.append({
                    "function": node.name,
                    "line": node.lineno,
                    "complexity": complexity
                })

    return issues

def main():
    file_path = sys.argv[1] if len(sys.argv) > 1 else None
    if not file_path:
        return

    if Path(file_path).suffix not in SUPPORTED_EXTENSIONS:
        return

    issues = analyze_file(file_path)
    if issues:
        print(f"Complexity warnings in {file_path}:")
        for issue in issues:
            print(f"  Line {issue['line']}: {issue['function']}() "
                  f"has complexity {issue['complexity']} "
                  f"(threshold: {COMPLEXITY_THRESHOLD})")

if __name__ == "__main__":
    main()
```

**hooks/analyzers/complexity_checker.md:**

```markdown
---
name: complexity_checker
description: Warns about functions with high cyclomatic complexity
trigger: PostToolUse
matcher: Write|Edit
---

## Purpose

Identifies functions with high cyclomatic complexity that may be
difficult to test and maintain.

## Configuration

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "command": "python ~/.claude/hooks/analyzers/complexity_checker.py $FILE",
        "timeout": 5000
      }
    ]
  }
}
```

## Behavior

1. Parses Python files using AST
2. Calculates cyclomatic complexity for each function
3. Reports functions exceeding threshold (default: 10)

## Output

```text
Complexity warnings in src/main.py:
  Line 42: process_data() has complexity 15 (threshold: 10)
  Line 89: handle_request() has complexity 12 (threshold: 10)
```

```

## Testing Components

### Testing Agents

1. Copy to Claude config:

   ```bash
   cp agents/domain/my-agent.md ~/.claude/agents/
   ```

2. Test invocation:

   ```text
   Use the my-agent agent to [task description]
   ```

3. Verify:
   - Agent is selected correctly
   - Tools are available as specified
   - Skills are loaded
   - Output matches expectations

### Testing Skills

1. Create test agent referencing skill:

   ```yaml
   ---
   name: test-skill-agent
   skills: my-new-skill
   ---
   ```

2. Test skill content is applied

3. Verify references load on demand

### Testing Commands

1. Copy to Claude config:

   ```bash
   cp commands/category/my-command.md ~/.claude/commands/category/
   ```

2. Test invocation:

   ```text
   /category:my-command [arguments]
   ```

3. Verify:
   - Command expands correctly
   - Arguments are passed via $ARGUMENTS
   - Process executes as expected

### Testing Hooks

1. Test manually:

   ```bash
   python hooks/type/my_hook.py /path/to/test/file.py
   ```

2. Register and test with Claude Code

3. Verify:
   - Triggers on correct events
   - Output appears in Claude Code
   - Performance is acceptable

## See Also

- [Best Practices](BEST_PRACTICES.md) - Quality standards
- [Contributing](CONTRIBUTING.md) - Contribution workflow
- [Publishing](PUBLISHING.md) - Distribution guide
- [Architecture](ARCHITECTURE.md) - System design
