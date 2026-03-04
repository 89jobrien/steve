#!/usr/bin/env bash
# ~/.claude/hooks/validate-code.sh - AWAKE: No timeouts, uv-fast Python, LSP-direct

set -euo pipefail

detect_lang() {
  local ext="${1##*.}"
  case "$ext" in
    rs) echo rust ;;
    py) echo python ;;
    js|ts|jsx|tsx) echo javascript ;;
    sh|bash) echo bash ;;
    toml|yaml|yml|json) echo config ;;
    md) echo markdown ;;
    *) echo unknown ;;
  esac
}

search_pattern() {
  local pattern="$1"
  shift
  if command -v rg >/dev/null 2>&1; then
    rg -n -i -e "$pattern" -- "$@" >/dev/null 2>&1
  else
    grep -n -i -E -- "$pattern" "$@" >/dev/null 2>&1
  fi
}

validate() {
  local lang="$1"
  shift
  local files=("$@")
  local issues=()

  case "$lang" in
    rust)
      cargo check "${files[@]}" >/dev/null 2>&1 || issues+=("cargo")
      cargo fmt -- --check "${files[@]}" >/dev/null 2>&1 || issues+=("fmt")
      search_pattern 'api_key|secret|unwrap' "${files[@]}" && issues+=("secrets")
      bacon check "${files[@]}" >/dev/null 2>&1 || true
      ;;
    python)
      uvx ruff check --quiet "${files[@]}" >/dev/null 2>&1 || issues+=("ruff")
      uvx ruff format --check "${files[@]}" >/dev/null 2>&1 || issues+=("ruff-format")
      uvx ty "${files[@]}" >/dev/null 2>&1 || issues+=("ty")
      search_pattern 'os\.system|exec|eval' "${files[@]}" && issues+=("dangerous")
      ;;
    javascript)
      npx eslint --quiet -- "${files[@]}" >/dev/null 2>&1 || issues+=("eslint")
      search_pattern 'process\.env.*secret' "${files[@]}" && issues+=("secrets")
      ;;
    bash)
      shellcheck -e SC2034 -- "${files[@]}" >/dev/null 2>&1 || issues+=("shellcheck")
      shfmt -ln -i 2 -d -- "${files[@]}" >/dev/null 2>&1 || issues+=("shfmt")
      ;;
    config)
      for f in "${files[@]}"; do
        case "${f##*.}" in
          json) jq empty "$f" >/dev/null 2>&1 || issues+=("json") ;;
          yml|yaml) yamllint --format parsable "$f" >/dev/null 2>&1 || issues+=("yaml") ;;
          toml) taplo lint "$f" >/dev/null 2>&1 || issues+=("toml") ;;
        esac
      done
      ;;
  esac

  if [[ ${#issues[@]} -eq 0 ]]; then
    jq -cn --arg lang "$lang" '{"ok":true,"lang":$lang,"reason":"ok"}'
    return 0
  fi

  jq -cn --arg lang "$lang" --arg reason "${issues[*]}" '{"ok":false,"lang":$lang,"reason":$reason}'
  return 1
}

files=()

# Try to get file from Claude Code hook payload (PostToolUse hook)
if [[ -t 0 ]]; then
  # No stdin, fall back to git or CHANGED_FILES
  if [[ -n "${CHANGED_FILES:-}" ]]; then
    while IFS= read -r line; do
      [[ -n "$line" ]] && files+=("$line")
    done <<< "$CHANGED_FILES"
  else
    while IFS= read -r line; do
      [[ -n "$line" ]] && files+=("$line")
    done < <(git diff --name-only --cached 2>/dev/null || true)
    if [[ ${#files[@]} -eq 0 ]]; then
      while IFS= read -r line; do
        [[ -n "$line" ]] && files+=("$line")
      done < <(git diff --name-only HEAD~1 2>/dev/null || true)
    fi
  fi
else
  # Read JSON payload from stdin (Claude Code hook)
  payload=$(cat)
  if command -v jq >/dev/null 2>&1; then
    file_path=$(echo "$payload" | jq -r '.tool_input.file_path // empty' 2>/dev/null || true)
    if [[ -n "$file_path" ]]; then
      files+=("$file_path")
    fi
  fi
fi

if [[ ${#files[@]} -eq 0 ]]; then
  echo '{"ok": true, "reason": "No changes detected"}'
  exit 0
fi

# Group files by language (bash 3.2 compatible - no associative arrays)
rust_files=()
python_files=()
javascript_files=()
bash_files=()
config_files=()
markdown_files=()

for file in "${files[@]}"; do
  [[ -f "$file" ]] || continue
  lang=$(detect_lang "$file")
  case "$lang" in
    rust) rust_files+=("$file") ;;
    python) python_files+=("$file") ;;
    javascript) javascript_files+=("$file") ;;
    bash) bash_files+=("$file") ;;
    config) config_files+=("$file") ;;
    markdown) markdown_files+=("$file") ;;
  esac
done

# Check if we have any files to validate
total_files=$((${#rust_files[@]} + ${#python_files[@]} + ${#javascript_files[@]} + ${#bash_files[@]} + ${#config_files[@]} + ${#markdown_files[@]}))
if [[ $total_files -eq 0 ]]; then
  echo '{"ok": true, "reason": "No valid files"}'
  exit 0
fi

results=()
all_ok=true

# Validate each language group
if [[ ${#rust_files[@]} -gt 0 ]]; then
  if result=$(validate rust "${rust_files[@]}"); then
    results+=("$result")
  else
    results+=("$result")
    all_ok=false
  fi
fi

if [[ ${#python_files[@]} -gt 0 ]]; then
  if result=$(validate python "${python_files[@]}"); then
    results+=("$result")
  else
    results+=("$result")
    all_ok=false
  fi
fi

if [[ ${#javascript_files[@]} -gt 0 ]]; then
  if result=$(validate javascript "${javascript_files[@]}"); then
    results+=("$result")
  else
    results+=("$result")
    all_ok=false
  fi
fi

if [[ ${#bash_files[@]} -gt 0 ]]; then
  if result=$(validate bash "${bash_files[@]}"); then
    results+=("$result")
  else
    results+=("$result")
    all_ok=false
  fi
fi

if [[ ${#config_files[@]} -gt 0 ]]; then
  if result=$(validate config "${config_files[@]}"); then
    results+=("$result")
  else
    results+=("$result")
    all_ok=false
  fi
fi

final_json=$(printf '%s\n' "${results[@]}" | jq -s '{
  ok: (all(.ok)),
  reason: (map("\(.lang):\(.reason)") | join(", "))
}')
echo "$final_json"

if $all_ok; then
  exit 0
fi
exit 1
