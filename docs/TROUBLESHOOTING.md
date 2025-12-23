# Troubleshooting

Solutions for common issues when using Steve components with Claude Code.

## Quick Diagnostics

Before diving into specific issues, run these checks:

```bash
# Verify component files exist
ls -la ~/.claude/agents/
ls -la ~/.claude/skills/
ls -la ~/.claude/commands/

# Check settings file syntax
cat ~/.claude/settings.json | python -m json.tool

# Verify file permissions
ls -la ~/.claude/settings.json
```

## Component Discovery Issues

### Components Not Found

**Symptom:** Claude doesn't find your installed agents, skills, or commands.

**Causes and Solutions:**

1. **Files in wrong location:**

   ```bash
   # Verify correct paths
   ~/.claude/agents/agent-name.md      # Agents
   ~/.claude/skills/skill-name/SKILL.md # Skills
   ~/.claude/commands/command.md        # Commands
   ```

2. **Invalid frontmatter syntax:**

   ```yaml
   # Correct YAML frontmatter
   ---
   name: agent-name
   description: What this agent does
   tools: Read, Write, Edit
   ---
   ```

   Common syntax errors:
   - Missing `---` delimiters
   - Incorrect indentation
   - Unquoted special characters

3. **Name mismatch:**
   The `name` field must be unique and match how you reference it.

4. **Session not reloaded:**
   Restart Claude Code after adding new components.

### Agent Not Being Selected

**Symptom:** You request an agent but a different one is selected.

**Solutions:**

1. **Be more specific in your request:**

   ```text
   # Vague - may match multiple agents
   "Review my code"

   # Specific - matches code-reviewer
   "Use the code-reviewer agent to review src/main.py"
   ```

2. **Improve agent description:**

   ```yaml
   # Too generic
   description: Reviews code

   # Specific with keywords
   description: Reviews Python code for quality, security vulnerabilities, and best practices
   ```

3. **Check for description conflicts:**
   Multiple agents with similar descriptions compete. Differentiate them.

### Skill Not Loading

**Symptom:** Agent runs but doesn't use expected skill expertise.

**Solutions:**

1. **Verify skill reference:**

   ```yaml
   # In agent frontmatter
   skills: code-review, testing
   ```

2. **Check skill directory structure:**

   ```text
   ~/.claude/skills/
   └── code-review/
       └── SKILL.md    # Required file
   ```

3. **Verify skill name matches:**
   The directory name must match the `skills:` reference exactly.

## Command Issues

### Slash Command Not Working

**Symptom:** `/command` doesn't execute or shows error.

**Solutions:**

1. **Check file extension:**

   ```bash
   # Must be .md extension
   ~/.claude/commands/my-command.md
   ```

2. **Verify namespace:**

   ```text
   # Root command
   /my-command -> ~/.claude/commands/my-command.md

   # Namespaced command
   /dev:review -> ~/.claude/commands/dev/review.md
   ```

3. **Check frontmatter:**

   ```yaml
   ---
   description: What this command does
   allowed-tools: Read, Write, Edit
   argument-hint: [file-path] | [--verbose]
   ---
   ```

### Command Arguments Not Parsed

**Symptom:** Arguments passed to command are ignored.

**Solutions:**

1. **Use `$ARGUMENTS` placeholder:**

   ```markdown
   Review the code at $ARGUMENTS
   ```

2. **Document expected format:**

   ```yaml
   argument-hint: [file-path] | [commit-hash]
   ```

3. **Handle missing arguments:**

   ```markdown
   If no file path provided, ask the user to specify one.
   ```

## Hook Issues

### Hook Not Running

**Symptom:** Hook doesn't trigger on expected events.

**Solutions:**

1. **Verify registration in settings.json:**

   ```json
   {
     "hooks": {
       "PostToolUse": [
         {
           "matcher": "Write|Edit",
           "command": "python ~/.claude/hooks/lint.py $FILE"
         }
       ]
     }
   }
   ```

2. **Check matcher pattern:**

   ```json
   // Matches Write OR Edit
   "matcher": "Write|Edit"

   // Matches only Write
   "matcher": "Write"

   // Matches any tool (no matcher needed)
   // Omit the matcher field entirely
   ```

3. **Test hook manually:**

   ```bash
   python ~/.claude/hooks/lint.py /path/to/test.py
   ```

4. **Check Python path:**

   ```bash
   which python
   # or use explicit path
   "command": "/usr/bin/python3 ~/.claude/hooks/lint.py $FILE"
   ```

### Hook Running But No Output

**Symptom:** Hook executes but nothing appears in Claude Code.

**Solutions:**

1. **Ensure output goes to stdout:**

   ```python
   # This appears in Claude Code
   print("Linting results: passed")

   # This does NOT appear
   import logging
   logging.info("Linting results")  # Goes to stderr by default
   ```

2. **Check script exit:**

   ```python
   # Script may exit early
   if not should_process(file_path):
       return  # Silent exit

   # Add feedback
   if not should_process(file_path):
       print(f"Skipping {file_path}")
       return
   ```

### Hook Running Too Slowly

**Symptom:** Operations feel sluggish when hooks are enabled.

**Solutions:**

1. **Add timeout:**

   ```json
   {
     "matcher": "Write",
     "command": "python ~/.claude/hooks/lint.py $FILE",
     "timeout": 5000
   }
   ```

2. **Filter files early:**

   ```python
   SUPPORTED = {".py", ".js", ".ts"}

   def main():
       file_path = sys.argv[1]
       if Path(file_path).suffix not in SUPPORTED:
           return  # Skip unsupported files quickly
   ```

3. **Optimize external tool calls:**

   ```python
   # Slow: Run linter on every file
   subprocess.run(["ruff", "check", file_path])

   # Fast: Only lint if file changed recently
   if file_modified_recently(file_path):
       subprocess.run(["ruff", "check", file_path])
   ```

### Hook Blocking Operations

**Symptom:** Claude Code hangs or operations never complete.

**Solutions:**

1. **Check for infinite loops:**

   ```python
   # Bug: Loop never exits
   while True:
       process_data()

   # Fix: Add exit condition
   while not done:
       done = process_data()
   ```

2. **Add timeout to subprocesses:**

   ```python
   result = subprocess.run(
       ["external-tool", file_path],
       timeout=10,  # Seconds
       capture_output=True
   )
   ```

3. **Check network calls:**

   ```python
   import requests

   # May hang on slow network
   response = requests.get(url)

   # Better: Add timeout
   response = requests.get(url, timeout=5)
   ```

## Installation Issues

### Script Fails to Install Component

**Symptom:** `install_component.py` or `install_from_gist.py` fails.

**Solutions:**

1. **Check GitHub token:**

   ```bash
   # Set token
   export GITHUB_TOKEN=ghp_xxxxxxxxxxxx

   # Or via git config
   git config --global github.token ghp_xxxxxxxxxxxx
   ```

2. **Verify gist URL format:**

   ```bash
   # Correct format
   https://gist.github.com/username/abc123def456

   # Wrong: Missing gist ID
   https://gist.github.com/username/
   ```

3. **Check network connectivity:**

   ```bash
   curl -I https://api.github.com
   ```

### Registry Not Found

**Symptom:** `--from-registry` option fails.

**Solutions:**

1. **Check local registry exists:**

   ```bash
   cat .gist-registry.json
   ```

2. **Verify remote registry URL:**

   ```bash
   # The registry gist must be accessible
   curl https://gist.githubusercontent.com/user/gist_id/raw
   ```

3. **Rebuild registry if corrupted:**

   ```bash
   uv run scripts/build_index.py
   ```

## Configuration Issues

### Settings File Invalid

**Symptom:** Claude Code reports settings error on startup.

**Solutions:**

1. **Validate JSON syntax:**

   ```bash
   cat ~/.claude/settings.json | python -m json.tool
   ```

2. **Common JSON errors:**

   ```json
   // Wrong: Trailing comma
   {
     "hooks": {},
   }

   // Correct: No trailing comma
   {
     "hooks": {}
   }
   ```

3. **Reset to defaults:**

   ```bash
   # Backup current
   cp ~/.claude/settings.json ~/.claude/settings.json.bak

   # Create minimal valid settings
   echo '{}' > ~/.claude/settings.json
   ```

### Model Override Not Working

**Symptom:** Agent uses wrong model despite override.

**Solutions:**

1. **Check override syntax:**

   ```json
   {
     "agentModelOverrides": {
       "code-reviewer": "opus",
       "debugger": "sonnet"
     }
   }
   ```

2. **Verify agent name matches exactly:**

   ```yaml
   # Agent file
   name: code-reviewer

   # Settings must match
   "code-reviewer": "opus"
   ```

## Performance Issues

### High Token Usage

**Symptom:** Conversations consume many tokens quickly.

**Solutions:**

1. **Reduce skill content:**
   - Move verbose documentation to `references/`
   - Keep `SKILL.md` focused on essential methodology

2. **Use appropriate models:**

   ```yaml
   # For simple tasks
   model: haiku

   # For complex analysis
   model: opus
   ```

3. **Limit tool access:**

   ```yaml
   # Full access (may be chatty)
   tools: All tools

   # Restricted (more focused)
   tools: Read, Grep, Glob
   ```

### Slow Agent Responses

**Symptom:** Agents take long to respond.

**Solutions:**

1. **Use lighter model:**

   ```yaml
   model: haiku  # Fast
   # model: opus  # Slower but more capable
   ```

2. **Reduce referenced skills:**

   ```yaml
   # Many skills = slower loading
   skills: skill1, skill2, skill3, skill4, skill5

   # Focused = faster
   skills: skill1, skill2
   ```

3. **Optimize descriptions:**
   Shorter, more specific descriptions help agent selection.

## Common Error Messages

### "No matching component found"

**Cause:** Component name doesn't match any in registry.

**Fix:**

```bash
# List available components
uv run scripts/list_components.py --search keyword

# Check exact name
uv run scripts/list_components.py --type agent
```

### "Invalid frontmatter"

**Cause:** YAML syntax error in component file.

**Fix:**

```bash
# Validate YAML
python -c "import yaml; yaml.safe_load(open('file.md').read().split('---')[1])"
```

### "Permission denied"

**Cause:** File permissions prevent access.

**Fix:**

```bash
# Make readable
chmod 644 ~/.claude/agents/my-agent.md

# Make directory accessible
chmod 755 ~/.claude/agents/
```

### "GitHub API rate limit exceeded"

**Cause:** Too many API requests without authentication.

**Fix:**

```bash
# Set GitHub token
export GITHUB_TOKEN=ghp_xxxxxxxxxxxx
```

### "Hook timeout exceeded"

**Cause:** Hook script took too long.

**Fix:**

```json
{
  "matcher": "Write",
  "command": "python hook.py",
  "timeout": 30000
}
```

## Getting Help

### Debugging Steps

1. **Check file locations and permissions**
2. **Validate YAML/JSON syntax**
3. **Test components manually**
4. **Review Claude Code logs**
5. **Restart Claude Code**

### Reporting Issues

When reporting issues, include:

1. Component file contents (with sensitive data removed)
2. Relevant `settings.json` configuration
3. Error messages (exact text)
4. Steps to reproduce
5. Claude Code version

### Resources

- [FAQ](FAQ.md) - Common questions
- [Architecture](ARCHITECTURE.md) - System design
- [Scripts Reference](SCRIPTS_REFERENCE.md) - Script documentation
- GitHub Issues - Report bugs
