# Changelog — claude-project-starter

Format: `[YYYY-MM-DD] type: description`
Types: `feat` | `fix` | `refactor` | `docs` | `chore` | `perf`

---

[2026-04-19] docs: Sprint 5 follow-up — `github-mcp-server` v1.0.0 binary installed on Windows in parallel; both platforms ready.
[2026-04-19] chore: close Sprint 5 — plugin v1.1.1 ships Context7 + GitHub MCPs as universal defaults; Tauri preset owns rust-analyzer-lsp; user settings cleaned.
[2026-04-19] fix: plugin v1.1.1 — GitHub MCP switched from remote HTTP to local binary-stdio (`github-mcp-server stdio`, PAT via `GITHUB_PERSONAL_ACCESS_TOKEN`). Remote endpoint `api.githubcopilot.com/mcp/` requires OAuth with Dynamic Client Registration, which Claude Code's MCP client doesn't support. Adds prereq: install `github-mcp-server` binary on PATH per machine (Linuxbrew / release tarball / Windows zip).
[2026-04-19] feat: Sprint 5 — plugin v1.1.0 adds Context7 + GitHub as universal MCPs (.mcp.json at plugin root). SQLite MCP deferred (modelcontextprotocol/servers implementation archived, no trusted replacement yet).
[2026-04-19] feat: new_project.py — Tauri preset now writes superpowers-marketplace + rust-analyzer-lsp@claude-plugins-official into project settings.json. Non-Tauri projects no longer carry rust-analyzer.
[2026-04-19] docs: PROJECT_STATUS.md — catch up sprint tracking through Sprint 4 (baseline unification, cloud validation, DoD enforcement, plugin packaging), open Sprint 5 (MCPs) with task table, note Sprint 6 (routines) as planned
[2026-04-19] chore: close Sprint 4 — plugin-based conventions shipped (v1.0.2). Known issue: SessionStart hook doesn't produce visible output despite loading cleanly; tracked in TROUBLESHOOTING.md as v1.0.3 work item. Slash commands, sub-agents, marketplace updates all functional.
[2026-04-19] fix: plugin v1.0.2 — restore outer "hooks" wrapper in hooks/hooks.json (v1.0.1 over-corrected; Claude Code's loader requires the wrapper WITH the matcher field)
[2026-04-19] fix: rename plugin claude-project-starter → project (v1.0.1) for shorter slash command prefix (/project:brief vs /claude-project-starter:brief)
[2026-04-19] fix: correct hooks/hooks.json structure (add matcher "startup") so SessionStart DoD reminder fires
[2026-04-19] feat: create niklas-marketplace repo with claude-project-starter plugin v1.0.0
[2026-04-19] refactor: move shared-conventions, sub-agents, hooks, slash commands from per-project generation to plugin
[2026-04-19] feat: new_project.py generates .claude/settings.json with plugin declaration instead of inline content
[2026-04-19] refactor: remove create_shared_conventions(), create_agents(), create_settings_and_hook(), create_commands() from new_project.py
[2026-04-19] feat: migrate claude-project-starter's own .claude/ to use plugin
[2026-04-18] feat: add dod-reviewer sub-agent — verifies Definition of Done at sprint close via task-in-plan enforcement
[2026-04-18] feat: add code-researcher sub-agent — tactical API/library research during implementation
[2026-04-18] feat: add SessionStart hook with DoD reminder (.claude/settings.json + session-start-reminder.txt)
[2026-04-18] feat: add GitHub Action changelog-check.yml — blocks PRs if src/ changed without CHANGELOG update
[2026-04-18] feat: add "Sprint closure" convention to shared-conventions.md — every sprint ends with DoD review task
[2026-04-18] feat: Sprint 0 template now includes "Run DoD review" as task 0.3
[2026-04-18] feat: /project:scope now instructs Claude to include DoD review task in every new sprint plan
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
