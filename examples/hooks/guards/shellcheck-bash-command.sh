#!/usr/bin/env bash
set -euo pipefail

files=$(git diff --cached --name-only -- '*.sh' ':!vendor/*')
[ -z "$files" ] && exit 0

shellcheck \
  --severity=warning \
  --enable=all \
  --exclude=SC1090,SC1091 \
  $files
