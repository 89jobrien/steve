#!/usr/bin/env bash
set -euo pipefail

# Claude Workspace Component Validator
# Validates agents, skills, and commands for required fields

CLAUDE_DIR="${HOME}/.claude"
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'

errors=0
warnings=0

echo -e "${BLUE}Claude Workspace Component Validator${NC}"
echo "======================================"
echo ""

# Validate agents
echo -e "${BLUE}Validating Agents...${NC}"
while IFS= read -r -d '' file; do
    name=$(basename "$file")

    if ! grep -q "^name:" "$file"; then
        echo -e "${RED}  [ERROR] Missing 'name:' in $file${NC}"
        ((errors++)) || true
    fi

    if ! grep -q "^description:" "$file"; then
        echo -e "${RED}  [ERROR] Missing 'description:' in $file${NC}"
        ((errors++)) || true
    fi

    if ! grep -q "^tools:" "$file"; then
        echo -e "${YELLOW}  [WARN] Missing 'tools:' in $file${NC}"
        ((warnings++)) || true
    fi
done < <(find "$CLAUDE_DIR/agents" -name "*.md" -type f -print0 2>/dev/null)

agent_count=$(find "$CLAUDE_DIR/agents" -name "*.md" -type f 2>/dev/null | wc -l | tr -d ' ')
echo -e "  Checked $agent_count agents"
echo ""

# Validate skill dependencies in agents
echo -e "${BLUE}Validating Skill Dependencies...${NC}"
skill_dep_errors=0
while IFS= read -r -d '' file; do
    # Extract skills field from frontmatter
    skills=$(awk '/^---$/{p++} p==1 && /^skills:/{print; exit}' "$file" | sed 's/skills: *//')

    if [[ -n "$skills" ]]; then
        # Split by comma and check each skill
        IFS=',' read -ra skill_array <<< "$skills"
        for skill in "${skill_array[@]}"; do
            skill=$(echo "$skill" | tr -d ' ')
            if [[ -n "$skill" && ! -d "$CLAUDE_DIR/skills/$skill" ]]; then
                echo -e "${RED}  [ERROR] Agent $(basename "$file") references missing skill: $skill${NC}"
                ((skill_dep_errors++)) || true
                ((errors++)) || true
            fi
        done
    fi
done < <(find "$CLAUDE_DIR/agents" -name "*.md" -type f -print0 2>/dev/null)

if [[ $skill_dep_errors -eq 0 ]]; then
    echo -e "${GREEN}  All skill dependencies valid${NC}"
else
    echo -e "  Found $skill_dep_errors missing skill references"
fi
echo ""

# Validate agent filename vs name consistency
echo -e "${BLUE}Validating Agent Naming...${NC}"
name_errors=0
while IFS= read -r -d '' file; do
    filename=$(basename "$file" .md)
    agent_name=$(awk '/^---$/{p++} p==1 && /^name:/{print $2; exit}' "$file")

    if [[ -n "$agent_name" && "$filename" != "$agent_name" ]]; then
        echo -e "${YELLOW}  [WARN] $file: filename '$filename' != name '$agent_name'${NC}"
        ((name_errors++)) || true
        ((warnings++)) || true
    fi
done < <(find "$CLAUDE_DIR/agents" -name "*.md" -type f -print0 2>/dev/null)

if [[ $name_errors -eq 0 ]]; then
    echo -e "${GREEN}  All agent names consistent${NC}"
else
    echo -e "  Found $name_errors naming inconsistencies"
fi
echo ""

# Validate skills
echo -e "${BLUE}Validating Skills...${NC}"
skill_count=0
while IFS= read -r -d '' dir; do
    skill_name=$(basename "$dir")
    ((skill_count++)) || true

    if [[ ! -f "$dir/SKILL.md" ]]; then
        echo -e "${RED}  [ERROR] Missing SKILL.md in $dir${NC}"
        ((errors++)) || true
    fi
done < <(find "$CLAUDE_DIR/skills" -mindepth 1 -maxdepth 1 -type d -print0 2>/dev/null)

echo -e "  Checked $skill_count skills"
echo ""

# Validate commands
echo -e "${BLUE}Validating Commands...${NC}"
while IFS= read -r -d '' file; do
    if ! grep -q "^description:" "$file"; then
        echo -e "${YELLOW}  [WARN] Missing 'description:' in $file${NC}"
        ((warnings++)) || true
    fi
done < <(find "$CLAUDE_DIR/commands" -name "*.md" -type f -print0 2>/dev/null)

cmd_count=$(find "$CLAUDE_DIR/commands" -name "*.md" -type f 2>/dev/null | wc -l | tr -d ' ')
echo -e "  Checked $cmd_count commands"
echo ""

# Summary
echo "======================================"
if [[ $errors -eq 0 && $warnings -eq 0 ]]; then
    echo -e "${GREEN}All components valid!${NC}"
else
    echo -e "Errors: ${RED}$errors${NC}, Warnings: ${YELLOW}$warnings${NC}"
fi

exit $errors
