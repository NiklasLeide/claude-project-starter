# claude-project-starter

A Python script that bootstraps new coding projects with Claude Code, GitHub, and all .mds pre-configured.

**Repo:** github.com/NiklasLeide/claude-project-starter
**Run with:** `newproject` (alias) or `python3 new_project.py`

## What this kit does
1. Asks ~8 questions about the new project
2. Creates folder structure + all .md files from templates
3. Sets up 6 Claude Code slash commands
4. Creates GitHub repo, labels, milestone, project board
5. Guides to VS Code to start working

## How to improve it
All templates live inside `new_project.py` as Python strings:
- `create_docs()` — CLAUDE.md, DECISIONS.md, PROJECT_STATUS.md, TROUBLESHOOTING.md, CHANGELOG.md, ROADMAP.md templates
- `create_commands()` — the 6 slash command templates
- `finish()` — the end screen shown after setup
- `setup_github()` — GitHub API calls
- `STACK_PRESETS` — stack options shown during setup
- `GITHUB_LABELS` — labels created on every new repo

## When to improve it
After finishing a project, ask:
- Did Claude keep making the same mistake? → update CLAUDE.md template
- Hit a WSL2/env issue not in TROUBLESHOOTING? → add it to that template
- Missing a slash command? → add to create_commands()
- New stack you'll use again? → add to STACK_PRESETS

## Commit convention
improvement: what changed and why
fix: what was broken
template: changes to generated file content
lesson: something learned from a real project
