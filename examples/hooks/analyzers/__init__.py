"""PostToolUse analyzer hooks.

Analyzers run after tool execution and can:
- Analyze changes made by tools
- Run linters and formatters
- Report warnings and suggestions

Available analyzers:
- lint_changed: Runs linter on changed files
- test_changed: Runs tests related to changed files
- typecheck_on_save: Type-checks modified files
- security_audit: Scans for security issues
- git_diff_logger: Logs git diffs for auditing
- dependency_vuln_check: Checks for vulnerable dependencies
- complexity_checker: Warns about complex code
- import_validator: Detects unused/circular imports
- todo_tracker: Tracks TODO/FIXME changes
- check_any_changed: Generic change detection
- check_comment_replacement: Detects comment-only changes
- check_unused_parameters: Finds unused function parameters
- lint_project: Lints entire project
- test_project: Runs full test suite
- typecheck_changed: Type-checks changed files
- typecheck_project: Type-checks entire project
"""
