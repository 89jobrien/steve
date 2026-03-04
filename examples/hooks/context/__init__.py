"""UserPromptSubmit context hooks.

Context hooks run when the user submits a prompt and can:
- Inject relevant context via stdout
- Analyze the prompt for keywords
- Provide project-specific information

Available context hooks:
- context_injector: Injects relevant file context
- session_logger: Logs session activity
- recent_changes: Shows recent git changes
- related_files: Finds files related to prompt
- project_detector: Detects project type and provides hints
- codebase_map: Generates codebase structure overview
"""
