---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: commands
---

---

allowed-tools: Bash(git branch:*), Bash(git checkout:*), Bash(git push:*), Bash(git merge:*), Bash(git remote:*), Bash(git for-each-ref:*), Bash(git reflog:*), Bash(gh:*), Read, Grep
argument-hint: [--dry-run] | [--force] | [--remote-only] | [--local-only]
description: Use PROACTIVELY to clean up merged branches, stale remotes, and organize branch structure
---

# Git Branch Cleanup

Clean up merged branches and organize repository structure: $ARGUMENTS

## Current Repository State

- Current branch: !`git branch --show-current`
- All branches: !`git branch -a`
- Recent branches: !`git for-each-ref --count=10 --sort=-committerdate refs/heads/ --format='%(refname:short) - %(committerdate:relative)'`
- Merged branches: !`git branch --merged main 2>/dev/null || git branch --merged master 2>/dev/null || echo "No main/master branch found"`

## Command Modes

| Mode | Flag | Behavior |
|------|------|----------|
| Interactive | (default) | Show analysis, confirm each deletion |
| Dry Run | `--dry-run` | Show what would be deleted, no changes |
| Force | `--force` | Delete merged branches without confirmation |
| Remote Only | `--remote-only` | Only clean remote-tracking branches |
| Local Only | `--local-only` | Only clean local branches |

## Cleanup Workflow

### 1. Pre-Cleanup Safety

```bash
git status
git stash push -m "Backup before branch cleanup" 2>/dev/null || true
```

### 2. Identify Branches

```bash
git branch --merged main | grep -v "main\|master\|develop\|\*"
git branch -r --merged main | grep -v "main\|master\|develop\|HEAD"
git for-each-ref --format='%(refname:short) %(committerdate:short)' refs/heads --sort=committerdate
```

### 3. Protected Branches

Never delete: `main`, `master`, `develop`, `staging`, `production`, `release/*`, current branch

### 4. Local Branch Cleanup

```bash
git branch --merged main | grep -v "main\|master\|develop\|\*" | xargs -n 1 git branch -d
```

### 5. Remote Branch Cleanup

```bash
git remote prune origin
git push origin --delete branch-name
```

### 6. Verification

```bash
git branch -a
git remote show origin
```

## Recovery

```bash
git reflog --no-merges --since="2 weeks ago"
git checkout -b recovered-branch <commit-hash>
```

## Output Format

```
Branch Cleanup Summary:
Deleted 3 merged feature branches
Removed 5 stale remote references
Repository now has 8 active branches (was 18)

Recovery Commands:
git checkout -b feature/user-auth 1a2b3c4d
```

## GitHub Integration

If `gh` CLI available:

- Check PR status before deleting
- Verify branches merged in web interface
- Clean up both local and remote consistently
