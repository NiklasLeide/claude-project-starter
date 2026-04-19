# Project Status — claude-project-starter

> **Last updated:** 2026-04-19
> **Current phase:** Workflow modernization
> **Status:** Sprint 5 closed; Sprint 6 (Routines) up next

---

## Sprint history

| Sprint | Theme | Status | Key output |
|--------|-------|--------|------------|
| 1 | Baseline unification | ✅ Closed | `shared-conventions.md`, slimmed `CLAUDE.md`, `CLAUDE_PROJECT_INSTRUCTIONS.md`, user-level `~/.claude/CLAUDE.md` stubs (f6a026d) |
| 2 | Validate Claude Code on the web | ✅ Closed | val26 cloud environment created, read-tested; no code changes |
| 3 | DoD enforcement | ✅ Closed | `dod-reviewer` + `code-researcher` sub-agents, local SessionStart hook, CHANGELOG GitHub Action, sprint-closure convention, task 0.3 "Run DoD review" in generated PROJECT_STATUS template (672c4d0) |
| 4 | Plugin packaging | ✅ Closed | `niklas-marketplace` + `project` plugin v1.0.2 (conventions, agents, hooks, commands); val26 migrated as pilot. Known issue: SessionStart hook output not visible — tracked for v1.0.3 (dc4c4c6 → 497ec08; marketplace cc61676 + 6c35ef8) |
| 5 | MCPs | ✅ Closed | Plugin v1.1.1 ships Context7 + GitHub MCPs as universal defaults (`.mcp.json`); Tauri preset owns rust-analyzer-lsp; user settings cleaned; `github-mcp-server` v1.0.0 binary installed on both WSL2 and Windows. SQLite MCP deferred (533a2af, 113040f) |
| 6 | Routines | ⏸️ Planned | Brief after Sprint 5 closes |

---

## Sprint 5 — MCPs

| # | Task | Status |
|---|------|--------|
| 5.1 | Add Context7 MCP to plugin as default for every project | ✅ shipped in v1.1.0 (`plugins/project/.mcp.json`, stdio via `npx`). Verified in val26. |
| 5.2 | Add official GitHub MCP to plugin as default for every project | ✅ shipped in v1.1.1 (local binary-stdio; v1.1.0's remote HTTP dropped — Copilot endpoint requires OAuth+DCR unsupported by Claude Code). Verified in val26 with real PR query. |
| 5.3 | Add SQLite MCP to plugin for Python/FastAPI+SQLite preset only | ⏸️ deferred — modelcontextprotocol/servers SQLite impl archived, no trustworthy replacement yet |
| 5.4 | Move rust-analyzer-lsp from user settings to Tauri preset plugin declarations | ✅ generator writes superpowers-marketplace + rust-analyzer-lsp for Tauri stack; removed from both user-level `settings.json` files |
| 5.5 | Bump plugin to v1.1.0 and verify in val26 | ✅ closed with v1.1.1 (v1.1.0 shipped with broken GitHub MCP, v1.1.1 fixed to binary-stdio). Both MCPs confirmed connected in val26 and responding to real queries. |
| 5.6 | Run DoD review for this sprint | ✅ dod-reviewer ran, see sprint-close commit |

### Known follow-ups from Sprint 5

- **Plugin SessionStart hook visibility** (carried from Sprint 4) — v1.0.3 work item; not addressed in Sprint 5.

---

## Blockers
- _None_

## Known issues carried forward
- Plugin SessionStart hook output not visible in transcript despite clean load — see `docs/TROUBLESHOOTING.md`. Tracked for plugin v1.0.3.

---

## Backlog
- [ ] Add more stack presets as new projects use them
- [ ] Consider sorting `projects.bat` list alphabetically
- [ ] Consider a `/project:retro` slash command for sprint retrospectives
- [ ] Template improvements based on lessons from future projects

---
> Update after each sprint close. One row per sprint in the history table; tick the task table as Sprint 5 progresses.
