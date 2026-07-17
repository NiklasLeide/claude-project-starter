# Project Status — claude-project-starter

> **Last updated:** 2026-07-17
> **Current focus:** MÅL 1 closed — next goal not yet picked (see goal backlog)

---

## Goals

| # | Goal | Done when | Depends on | Status |
|---|------|-----------|------------|--------|
| 1 | Goal-based workflow (kit + plugin v1.2.0) | See MÅL 1 below | — | ✅ |

---

## MÅL 1 — Goal-based workflow (kit + plugin v1.2.0)

**Outcome:** Kit and `project` plugin define work as goals (Outcome / Done when / Budget / Depends on) instead of sprints; plugin v1.2.0 published.

**Budget:** One local Claude Code session.

**Depends on:** —

**Done when:**
- [x] Generated PROJECT_STATUS.md has a `## Goals` table with Done-when column; scratch project greps 0 hits for "sprint"
- [x] `grep -ri sprint` over kit `.md`/`.py` files gives 0 hits outside changelog/status history
- [x] Plugin shared-conventions has §"Goal closure"; §"Sprint closure" is gone
- [x] `dod-reviewer` verifies Done-when conditions and answers GOAL READY TO CLOSE / GOAL NOT CLOSEABLE
- [x] Plugin v1.2.0 published in marketplace (commit 043fe1b pushed); val26 `/plugin` shows v1.2.0 and `/project:scope` produces goal format — confirmed by Niklas 2026-07-17
- [x] Kit's own PROJECT_STATUS.md forward section is goal-based (sprint history kept as history)
- [x] New DEC logged with decision + rejected alternatives
- [x] Run DoD review (goal closure) — use dod-reviewer sub-agent

---

## Goal backlog (not yet refined)

- MÅL 2 — loop scripts / guardrails. Defined in `MÅL.md` (Claude project "Development Project management"). Brief after MÅL 1 closes.
- MÅL 3 — v3 templates. Defined in `MÅL.md`.
- MÅL 6 — monitoring routine (formerly "Sprint 6 — Routines"). Runs the RESEARCH_AGENT monitoring methodology automatically.

---

## Blockers
- _None_

## Known issues carried forward
- ~~Plugin SessionStart hook output not visible~~ — closed as abandoned-by-design in v1.1.2 (hook layer dropped); see `docs/TROUBLESHOOTING.md`.

---

## Sprint history (historical — workflow was sprint-based through v1.1.2)

| Sprint | Theme | Status | Key output |
|--------|-------|--------|------------|
| 1 | Baseline unification | ✅ Closed | `shared-conventions.md`, slimmed `CLAUDE.md`, `CLAUDE_PROJECT_INSTRUCTIONS.md`, user-level `~/.claude/CLAUDE.md` stubs (f6a026d) |
| 2 | Validate Claude Code on the web | ✅ Closed | val26 cloud environment created, read-tested; no code changes |
| 3 | DoD enforcement | ✅ Closed | `dod-reviewer` + `code-researcher` sub-agents, local SessionStart hook, CHANGELOG GitHub Action, sprint-closure convention, task 0.3 "Run DoD review" in generated PROJECT_STATUS template (672c4d0) |
| 4 | Plugin packaging | ✅ Closed | `niklas-marketplace` + `project` plugin v1.0.2 (conventions, agents, hooks, commands); val26 migrated as pilot. Known issue: SessionStart hook output not visible — tracked for v1.0.3 (dc4c4c6 → 497ec08; marketplace cc61676 + 6c35ef8) |
| 5 | MCPs | ✅ Closed | Plugin v1.1.1 ships Context7 + GitHub MCPs as universal defaults (`.mcp.json`); Tauri preset owns rust-analyzer-lsp; user settings cleaned; `github-mcp-server` v1.0.0 binary installed on both WSL2 and Windows. SQLite MCP deferred (533a2af, 113040f) |
| 6 | Routines | ⏸️ Re-scoped | Became MÅL 6 in the goal backlog above |

### Sprint 5 — MCPs (closed)

| # | Task | Status |
|---|------|--------|
| 5.1 | Add Context7 MCP to plugin as default for every project | ✅ shipped in v1.1.0 (`plugins/project/.mcp.json`, stdio via `npx`). Verified in val26. |
| 5.2 | Add official GitHub MCP to plugin as default for every project | ✅ shipped in v1.1.1 (local binary-stdio; v1.1.0's remote HTTP dropped — Copilot endpoint requires OAuth+DCR unsupported by Claude Code). Verified in val26 with real PR query. |
| 5.3 | Add SQLite MCP to plugin for Python/FastAPI+SQLite preset only | ⏸️ deferred — modelcontextprotocol/servers SQLite impl archived, no trustworthy replacement yet |
| 5.4 | Move rust-analyzer-lsp from user settings to Tauri preset plugin declarations | ✅ generator writes superpowers-marketplace + rust-analyzer-lsp for Tauri stack; removed from both user-level `settings.json` files |
| 5.5 | Bump plugin to v1.1.0 and verify in val26 | ✅ closed with v1.1.1 (v1.1.0 shipped with broken GitHub MCP, v1.1.1 fixed to binary-stdio). Both MCPs confirmed connected in val26 and responding to real queries. |
| 5.6 | Run DoD review for this sprint | ✅ dod-reviewer ran, see sprint-close commit |

---

## Backlog (small items, not goals)
- [ ] Add more stack presets as new projects use them
- [ ] Consider sorting `projects.bat` list alphabetically
- [ ] Consider a `/project:retro` slash command for goal retrospectives
- [ ] Template improvements based on lessons from future projects

---
> Update after each goal close. Tick the goal's Done-when boxes as conditions are verified.
