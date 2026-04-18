# Changelog — claude-project-starter

Format: `[YYYY-MM-DD] type: description`
Types: `feat` | `fix` | `refactor` | `docs` | `chore` | `perf`

---

[2026-04-18] feat: add "Inline artifacts in briefs" convention to shared-conventions — chat-produced files go inline in briefs, not as external references
[2026-04-18] feat: generate .claude/shared-conventions.md per project — centralizes commit rule, DoD, communication, brief format, mode-switch, context management
[2026-04-18] refactor: slim CLAUDE.md template — removed duplicated sections, added @.claude/shared-conventions.md reference
[2026-04-18] refactor: shrink create_global_claude_md() to stub pointing to per-project shared-conventions
[2026-04-18] feat: opt-in RESEARCH_AGENT.md generation — new question in collect_info(), template with [FILL IN] sections
[2026-04-18] feat: add CLAUDE_PROJECT_INSTRUCTIONS.md to starter kit repo root — universal Claude Project paste-target
[2026-04-18] feat: finish() prints Claude Project setup step with paste instructions
[2026-03-23] feat: auto-place Tauri projects in /mnt/c/Users/nikla/projects/
[2026-03-23] feat: projects.bat scans ~/projects/, /mnt/c/.../projects/, ~/tools/, ~/lifecoach-app-repo
[2026-03-23] fix: projects.bat silent crash from unescaped bash in for /f
[2026-03-23] feat: projects.bat — Windows launcher to pick or create projects
[2026-03-15] feat: commit.sh enforcement script added to project template
[2026-03-15] fix: switch to classic GitHub tokens to fix 403 on repo creation
[2026-03-15] feat: add Tauri, Spring Boot, Vert.x stack presets
[2026-03-15] feat: parkhere and resume slash commands, MAINTENANCE.md template
[2026-03-15] docs: add CLAUDE.md so kit is self-describing for future sessions
[2026-03-15] fix: finish screen now guides to VS Code, not just terminal
[2026-03-15] fix: use python3 in alias, python not available by default on Ubuntu WSL2
[2026-03-15] fix: correct WSL2 cp path in SETUP_GUIDE, use /mnt/c/ instead of ~/Downloads
[2026-01-01] chore: initial commit — project starter kit v2
