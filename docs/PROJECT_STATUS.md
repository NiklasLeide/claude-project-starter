# Project Status — claude-project-starter

> **Last updated:** 2026-07-18
> **Current focus:** MÅL 8 — Windows-only dev environment (WSL decommissioned). One human check (bat→N→VS Code→claude→commit) remains before close. FRYSREGELN still gates MÅL 4–6.

---

## Goals

| # | Goal | Done when | Depends on | Status |
|---|------|-----------|------------|--------|
| 1 | Goal-based workflow (kit + plugin v1.2.0) | See MÅL 1 below | — | ✅ |
| 2 | Loop guardrail library (`templates/loop/`) | See MÅL 2 below | 1 | ✅ |
| 3 | v3 standard loop template (`run-loop.sh` + plugin v1.3.0) | See MÅL 3 below | 2 | ✅ |
| 8 | Windows-only development environment | See MÅL 8 below | — | 🚧 |

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

## MÅL 2 — Loop guardrail library

**Outcome:** The kit ships a generalized, project-agnostic loop guardrail library (`templates/loop/`: lib.js, guards.sh, loop.env.example, test-guards.sh, README.md) installed opt-in by `new_project.py` as `scripts/loop/`, so the next loop never reinvents val26's guards. Includes two backlog fixes: commit.sh silent staging and stale SessionStart mentions.

**Budget:** One focused session (built in Cowork cloud, delivered as PR).

**Depends on:** MÅL 1.

**Done when:**
- [x] Scratch project with loop tooling = yes has complete `scripts/loop/`; with no, the directory is absent
- [x] `test-guards.sh` green in the kit repo AND in a generated scratch project (47 checks: fail-closed exit 4, budget gate before calls, per-step caps, HEAD-guard self-heal + incident log + two strikes, branch/sandbox guards, mtime-scoped limit detection, retry never touches semantic codes, resume guard, scope-conflict escalation)
- [x] Detached launch survives parent death — Linux/setsid branch, automated test
- [x] Detached launch Windows/schtasks branch verified manually once; result noted in TROUBLESHOOTING — verified 2026-07-18 via Windows Git Bash at Niklas's direction (see TROUBLESHOOTING)
- [x] `scripts/loop/README.md` documents the exit-code contract (table) and the guard catalog
- [x] Loop entrypoints export `CLAUDE_CODE_DISABLE_1M_CONTEXT=1` (guard test 12)
- [x] `./commit.sh` in a repo without `src/` stages docs changes and prints what was staged (guard test 13; root commit.sh + both generator templates fixed)
- [x] `grep -ri "SessionStart" README.md new_project.py` → 0 hits
- [x] DEC-007 logged (executable templates as real files, amending DEC-002) with rejected alternative
- [x] Run DoD review (goal closure) — dod-reviewer ran 2026-07-18: all Done-when + DoD items ✓, GOAL READY TO CLOSE

---

## MÅL 3 — v3 standard loop template

**Outcome:** The kit ships the v3 loop as its standard template on top of the MÅL 2 guardrail library: `templates/loop/run-loop.sh` (single draft → deterministic verify → ONE fix round → deterministic re-verify → deliver), prompt skeletons, a working example validator, model cost routing via env, Loopability check in the plugin conventions (v1.3.0), and a live pilot run proven within budget.

**Budget:** One focused local session + $5 cap for the live pilot.

**Depends on:** MÅL 2.

**Done when:**
- [x] Scratch project with loop tooling = yes contains `scripts/loop/run-loop.sh`, `prompts/` (both skeletons) and `validate-example.js`; with no, `scripts/loop/` is absent — verified 2026-07-18 by driving `create_loop_tooling()` both ways
- [x] `test-guards.sh` green in the kit repo AND in the generated scratch project, including case 14 (58 checks)
- [x] Case 14 (dry-run with `LOOP_CLAUDE_BIN` stub): step order held (one draft, then one fix), `step_budget_gate` stops an over-cap step before the second paid call, report written, `git log` unchanged after the run
- [x] Plugin shared-conventions contains §"Loopability check"; `/project:scope` mentions the check for loop-executed goals; v1.3.0 pushed (e669be5) and `claude plugin list` shows project@niklas-marketplace 1.3.0 after `claude plugin update`
- [x] Pilot run: `docs/STACKS.md` generated and validator-green (9 presets derived, none missing, scope clean), total $0.154175 ≤ $5.00, per-step costs in `.loop/report.md`, HEAD untouched by the loop (commit a3d56da made outside the loop body)
- [x] `grep -riE "dubbelutkast|double.draft|diverge" templates/` → 0 hits
- [x] DEC-008 logged (model routing defaults) with rejected alternatives
- [x] Run DoD review (goal closure) — dod-reviewer ran 2026-07-18: all Done-when + DoD items ✓, GOAL READY TO CLOSE

---

## MÅL 8 — Windows-only development environment

**Outcome:** The entire kit workflow runs on clean Windows (Git Bash for
scripts, `schtasks` for detached loops, `python` not `python3`); WSL2 can be
shut down for good. Active repos live on the Windows filesystem with push
rights; `projects.bat` and `new_project.py` carry no WSL paths or `wsl`
invocations. Triggered by recurring WSL2 crashes that repeatedly took work
(the DEC-009 convention fix among them).

**Budget:** One local Claude Code session on Windows.

**Depends on:** —

**Done when:**
- [x] WSL inventory reported — each WSL repo's uncommitted/unpushed state surfaced (the aborted DEC-009 fix in `~/tools/claude-project-starter`; no unpushed commits anywhere; all active work already on GitHub)
- [x] Active repos on `C:` with push rights — `niklas-marketplace` + `spelledarverktyg` cloned; `git push --dry-run` clean for all five C: repos
- [x] `projects.bat` contains no `wsl` — lists `C:\Users\nikla\projects` + `\tools` via `dir /b`, N/U/number, `pause` on every error path
- [x] `new_project.py` generates on Windows and `test-guards.sh` is green (kit + generated scratch, 58 checks each) — surfaced and fixed a real Windows-only crash (cp1252 `UnicodeEncodeError`); `DEFAULT_PROJECTS_DIR` drops the `/mnt/c` Tauri special-case
- [ ] **[Niklas]** End-to-end chain `projects.bat → N → VS Code → claude → commit` completes without WSL (interactive; single human check)
- [x] DEC-010 logged with rejected alternatives
- [ ] Run DoD review (goal closure) — dod-reviewer verifies Done-when + DoD

---

## Goal backlog (not yet refined)
- MÅL 6 — monitoring routine (formerly "Sprint 6 — Routines"). Runs the RESEARCH_AGENT monitoring methodology automatically.

> FRYSREGELN (from the MÅL 3 brief): the v3 template must be run for real on an actual project before MÅL 4–6 are opened.

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
