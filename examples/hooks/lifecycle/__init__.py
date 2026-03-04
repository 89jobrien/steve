"""Stop lifecycle hooks.

Lifecycle hooks run when a Claude Code session ends and can:
- Generate summaries and reports
- Collect metrics
- Suggest commits
- Update knowledge bases

Available lifecycle hooks:
- self_review: Reviews session changes
- check_todos: Checks for incomplete TODOs
- create_checkpoint: Creates git checkpoint
- session_summary: Generates session summary
- cleanup_handler: Cleans up temporary files
- commit_suggester: Suggests conventional commits
- metrics_collector: Collects session metrics
- knowledge_update: Updates knowledge graph
"""
