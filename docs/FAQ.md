# Frequently Asked Questions

Common questions about Steve and Claude Code components.

## General Questions

### What is Steve?

Steve is a collection of reusable components for Claude Code, including agents, skills, commands, hooks, and
templates. It provides specialized AI assistants, automated workflows, and domain expertise that extend Claude
Code's capabilities.

### What is Claude Code?

Claude Code is Anthropic's CLI tool for AI-assisted development. It allows Claude to read, write, and execute code
in your development environment. Steve components enhance Claude Code with specialized agents and automation.

### Do I need Steve to use Claude Code?

No. Claude Code works without Steve. Steve provides optional enhancements - specialized agents, reusable skills,
automated workflows, and templates that make common tasks easier.

### Is Steve official?

No. Steve is an independent component library, not an official Anthropic product. It's designed to work with Claude
Code but is maintained separately.

## Installation Questions

### Where do I install components?

Components are installed to `~/.claude/`:

```text
~/.claude/
├── agents/      # Agent configurations
├── skills/      # Skill bundles
├── commands/    # Slash commands
├── hooks/       # Automation hooks
└── settings.json
```

### How do I install a single agent?

Copy the agent file to your agents directory:

```bash
cp steve/agents/code-quality/code-reviewer.md ~/.claude/agents/
```

### How do I install a skill?

Copy the entire skill directory:

```bash
cp -r steve/skills/code-review ~/.claude/skills/
```

### How do I update components?

Pull the latest changes and re-copy:

```bash
cd steve
git pull
cp steve/agents/code-quality/code-reviewer.md ~/.claude/agents/
```

### Can I install from a URL?

Yes, using the gist installer:

```bash
uv run scripts/install_from_gist.py https://gist.github.com/user/abc123
```

## Agent Questions

### How do I invoke an agent?

Request the agent naturally in your conversation:

```text
Use the code-reviewer agent to review src/main.py
```

Or be explicit about the Task tool:

```text
Invoke the debugger agent to investigate the error
```

### Which agent should I use?

Use the agent finder:

```text
/agents:find I need to optimize database queries
```

Or search by keyword:

```text
/agents:search security
```

### Can I use multiple agents together?

Yes. You can chain agents:

```text
1. Use code-reviewer to review the changes
2. Use test-engineer to write tests
3. Use documentation-expert to update docs
```

### Why isn't my agent being selected?

Check:

1. The agent file exists in `~/.claude/agents/`
2. The `name` field in frontmatter matches your request
3. The `description` is specific enough for Claude to match
4. Restart Claude Code to reload configurations

### Can agents invoke other agents?

Yes, if they have the `Task` tool:

```yaml
tools: Task, Read
```

### How do I limit what an agent can do?

Restrict tools in frontmatter:

```yaml
# Read-only agent
tools: Read, Grep, Glob

# Can modify code
tools: Read, Write, Edit, Grep, Glob

# Full access
tools: All tools
```

## Skill Questions

### What's the difference between agents and skills?

- **Agents** are task executors with specific tools and models
- **Skills** are knowledge bundles that agents reference

An agent does work. A skill provides expertise.

### How do agents use skills?

Agents reference skills in frontmatter:

```yaml
skills: code-review, testing
```

When the agent is invoked, Claude Code loads the referenced skills automatically.

### Can I use a skill without an agent?

Yes. Reference the skill directly:

```text
Using the code-review skill methodology, review src/auth.py
```

### Why isn't my skill loading?

Check:

1. The skill directory exists in `~/.claude/skills/`
2. The directory contains `SKILL.md`
3. The agent's `skills:` field matches the skill name exactly
4. The skill name uses correct casing

### Can skills have code?

Yes. Skills can include a `scripts/` directory:

```text
my-skill/
├── SKILL.md
└── scripts/
    └── analyze.py
```

## Command Questions

### How do I run a command?

Use slash syntax:

```text
/dev:review-code src/main.py
```

### What's the difference between `/command` and `/category:command`?

- `/command` - Root-level command (no subdirectory)
- `/category:command` - Namespaced command (in subdirectory)

### How do I see available commands?

Commands are listed in your conversation when you type `/`. You can also check:

```bash
ls ~/.claude/commands/
```

### Why isn't my command working?

Check:

1. The file exists in `~/.claude/commands/`
2. The file has `.md` extension
3. For namespaced commands, the directory structure matches
4. The file has valid frontmatter

### Can commands accept arguments?

Yes. Arguments follow the command:

```text
/dev:review-code src/main.py --verbose
```

The command's frontmatter can specify expected arguments:

```yaml
argument-hint: [file-path] | [--verbose]
```

## Hook Questions

### What triggers hooks?

Hooks respond to Claude Code events:

| Event | When |
|-------|------|
| PreToolUse | Before a tool executes |
| PostToolUse | After a tool executes |
| SessionStart | When a session begins |
| SessionEnd | When a session ends |
| UserPrompt | When you send a message |

### How do I enable a hook?

1. Copy the hook script to `~/.claude/hooks/`
2. Register in `settings.json`:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "command": "python ~/.claude/hooks/analyzers/lint.py $FILE"
      }
    ]
  }
}
```

### Why isn't my hook running?

Check:

1. Hook is registered in `settings.json`
2. Matcher pattern matches the tool name
3. Python script is executable
4. Test manually: `python ~/.claude/hooks/analyzers/lint.py test.py`

### Can I disable a hook temporarily?

Remove or comment out the hook entry in `settings.json`.

### How do I debug a hook?

Test it manually with sample input:

```bash
python ~/.claude/hooks/analyzers/lint.py /path/to/file.py
```

Check the output and exit code.

### Are hooks blocking?

Yes, hooks run synchronously. Use the `timeout` field to prevent hanging:

```json
{
  "matcher": "Write",
  "command": "python script.py",
  "timeout": 5000
}
```

## Template Questions

### What are templates for?

Templates provide scaffolding for creating new components:

- `SUBAGENT.template.md` - New agents
- `AGENT_SKILL.template.md` - New skills
- `SLASH_COMMAND.template.md` - New commands
- `CLAUDE_HOOK.template.md` - New hooks

### How do I use a template?

Copy and customize:

```bash
cp steve/templates/SUBAGENT.template.md ~/.claude/agents/my-agent.md
```

Or use meta commands:

```text
/meta:create-subagent code analyzer for Python
```

## Configuration Questions

### Where are settings stored?

- `~/.claude/settings.json` - Project settings (hooks, permissions)
- `~/.claude/settings.local.json` - Local overrides (not synced)
- `~/.claude.json` - User global settings

### How do I override agent models?

In `settings.json`:

```json
{
  "agentModelOverrides": {
    "code-reviewer": "opus",
    "debugger": "sonnet"
  }
}
```

### Can I disable specific tools for all agents?

This is configured in Claude Code settings, not Steve. Check Claude Code documentation.

## Troubleshooting Questions

### Claude isn't finding my components

1. Verify files are in the correct directories
2. Check frontmatter syntax (valid YAML)
3. Restart Claude Code to reload configurations
4. Check file permissions are readable

### An agent produces poor results

1. Improve the description for better matching
2. Add more specific instructions in the body
3. Reference appropriate skills
4. Try a more capable model (`opus`)

### A hook is slowing things down

1. Add a timeout to the configuration
2. Optimize the hook script
3. Add early filtering to skip unnecessary files
4. Consider making it async

### Commands aren't expanding correctly

1. Check frontmatter syntax
2. Verify no special characters in content
3. Test with simpler arguments first
4. Check for nested quote issues

## Performance Questions

### How do I make agents faster?

1. Use `haiku` model for simple tasks
2. Restrict to necessary tools only
3. Reference only needed skills
4. Keep instructions concise

### How do I reduce token usage?

1. Keep skill content focused
2. Use references/ for verbose documentation
3. Avoid redundant instructions
4. Be specific in agent descriptions

### Are there limits on components?

No hard limits, but practical considerations:

- Many agents can slow agent selection
- Large skills increase context usage
- Many hooks can slow tool execution

## Advanced Questions

### Can I create agents that invoke other agents?

Yes. Grant the `Task` tool:

```yaml
tools: Task, Read
```

The agent can then invoke other agents.

### Can hooks modify Claude's behavior?

Hooks can:

- Block operations (non-zero exit code)
- Inject information (stdout)
- Log events

Hooks cannot directly modify Claude's reasoning.

### Can I version control my configuration?

Yes. The recommended approach:

1. Keep components in a git repository (like Steve)
2. Copy to `~/.claude/` for installation
3. Exclude `settings.local.json` from version control

### How do I share components?

Options:

1. Publish to GitHub Gist
2. Share the repository
3. Copy individual files

See [Publishing](PUBLISHING.md) for details.

## See Also

- [Getting Started](GETTING_STARTED.md) - Quick start guide
- [Troubleshooting](TROUBLESHOOTING.md) - Common issues
- [Component Catalog](COMPONENT_CATALOG.md) - Browse all components
- [Architecture](ARCHITECTURE.md) - Design decisions
