#!/usr/bin/env python3
import claude_hooks


def handler(payload: claude_hooks.HookPayload) -> claude_hooks.HookResponse:
    """
    GAW Hook Handler
    - Use payload.tool_name to check the tool
    - Use payload.tool_input to check arguments
    """

    # Example: Block dangerous commands
    if payload.tool_name == 'Bash':
        cmd = payload.tool_input.get('command', '')
        if 'rm -rf' in cmd:
            return claude_hooks.HookResponse(
                allow=False,
                reason=f"Dangerous command blocked: {cmd}",
                system_message="Security: rm -rf is prohibited."
            )

    return claude_hooks.HookResponse(allow=True)

if __name__ == "__main__":
    claude_hooks.run(handler)
