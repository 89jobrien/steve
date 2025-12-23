#!/usr/bin/env bash
set -euo pipefail

# Claude Workspace Component Search
# Search across agents, skills, and commands

CLAUDE_DIR="${HOME}/.claude"
BLUE='\033[0;34m'
GREEN='\033[0;32m'
NC='\033[0m'

usage() {
    echo "Usage: $0 <pattern> [type]"
    echo ""
    echo "Arguments:"
    echo "  pattern   Search pattern (regex supported)"
    echo "  type      Optional: agents, skills, commands, all (default: all)"
    echo ""
    echo "Examples:"
    echo "  $0 database           # Search all components for 'database'"
    echo "  $0 'test.*expert' agents  # Search agents for pattern"
    exit 1
}

if [[ $# -lt 1 ]]; then
    usage
fi

pattern="$1"
search_type="${2:-all}"

search_dir() {
    local dir="$1"
    local label="$2"

    if [[ ! -d "$dir" ]]; then
        return
    fi

    echo -e "${BLUE}=== $label ===${NC}"
    local results
    results=$(grep -rl "$pattern" "$dir" --include="*.md" 2>/dev/null || true)

    if [[ -z "$results" ]]; then
        echo "  No matches"
    else
        echo "$results" | while read -r file; do
            local name
            name=$(grep "^name:" "$file" 2>/dev/null | head -1 | sed 's/name: //' || basename "$file")
            local rel_path="${file#$CLAUDE_DIR/}"
            echo -e "  ${GREEN}$name${NC} ($rel_path)"
        done
    fi
    echo ""
}

echo "Searching for: $pattern"
echo ""

case "$search_type" in
    agents)
        search_dir "$CLAUDE_DIR/agents" "Agents"
        ;;
    skills)
        search_dir "$CLAUDE_DIR/skills" "Skills"
        ;;
    commands)
        search_dir "$CLAUDE_DIR/commands" "Commands"
        ;;
    all)
        search_dir "$CLAUDE_DIR/agents" "Agents"
        search_dir "$CLAUDE_DIR/skills" "Skills"
        search_dir "$CLAUDE_DIR/commands" "Commands"
        ;;
    *)
        echo "Unknown type: $search_type"
        usage
        ;;
esac
