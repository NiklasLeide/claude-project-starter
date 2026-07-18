# Decision Log — claude-project-starter

Record of key decisions made during the project. **Newest first.**

> The alternatives you *rejected* are as important as what you chose.
> Future sessions will read this — make the reasoning explicit.

---

## Format
```
### DEC-NNN: Title
**Date:** YYYY-MM-DD
**Decision:** What we chose
**Reasoning:** Why this option over the others
**Alternatives considered:** What was rejected and why
```

---

### DEC-010: Windows-only development environment
**Date:** 2026-07-18
**Decision:** Development moves entirely to Windows-native tooling. Scripts run via Git Bash (`C:\Program Files\Git\bin\bash.exe`); detached loops use the `schtasks` branch already in `templates/loop/guards.sh`; `new_project.py` and `projects.bat` target the Windows filesystem (`C:\Users\nikla\projects` and `\tools`) with no `/mnt/c` special-cases or `wsl` calls. Active repos are cloned to `C:`. WSL2 is decommissioned from the workflow (nothing is deleted from WSL — that is a human decision).
**Reasoning:** WSL2 crashed recurrently and repeatedly destroyed in-progress work (the DEC-009 convention fix was lost to one such crash before it was ever committed). Maintaining two environments also created a config-drift class of bug — code that worked on one filesystem broke on the other (e.g. `/mnt/c` paths, `python3` vs `python`, the cp1252 crash new_project.py hit the moment it ran on Windows). One environment removes both the crash exposure and the drift.
**Alternatives considered:** Repair the WSL config (rejected — the crash class remains; the failure was in WSL itself, not our config, and every crash risks losing work again); keep the dual environment and just harden it (rejected — the config-drift class of bug persists as long as two filesystems and two Python conventions coexist).

### DEC-009: Chat counterparts fetch conventions from the kit's public canonical copy
**Date:** 2026-07-18
**Decision:** The starter kit's root `shared-conventions.md` (public repo) is the canonical conventions source. `CLAUDE_PROJECT_INSTRUCTIONS.md` points every chat counterpart at its raw.githubusercontent.com URL. The plugin's copy (which reaches Claude Code) is kept identical via `scripts/sync-conventions.sh`, run at every plugin bump.
**Reasoning:** DEC-003 (chat fetches conventions from the project repo) and DEC-005 (conventions moved into the private plugin) contradicted each other — every new project's chat counterpart was blocked on arrival and needed manual pasting. One public URL restores the chat leg with zero per-repo copies and zero new sync burden beyond the bump routine, enforced by script rather than memory.
**Alternatives considered:** Copy the file into every project repo (reintroduces the N-repo sync burden DEC-005 killed); keep plugin-only (chat surfaces can never reach it); make the marketplace repo public (exposes the whole private plugin for one file).

### DEC-008: v3 loop model routing defaults — Opus drafts, Haiku fixes
**Date:** 2026-07-18
**Decision:** `run-loop.sh` defaults to `LOOP_MODEL_DRAFT=claude-opus-4-8` and `LOOP_MODEL_FIX=claude-haiku-4-5-20251001`, both overridable per loop via `loop.env`. The expensive model makes the single draft; the cheap model runs the one fix round against exact validator findings.
**Reasoning:** In a single-draft pattern the draft carries all the quality — that is where model capability pays. The fix round is mechanical (a list of deterministic findings with the source of truth cited), which a cheap model handles; the pilot confirmed the asymmetry (Opus draft passed validators on the first try, $0.15). Env routing keeps the choice per loop, not per fork of the script.
**Alternatives considered:** Same mid-tier model for both steps (val26's pattern — rejected: pays mid-tier price for a mechanical fix step and under-invests in the draft, which the v3 pattern cannot iterate on); premium tier (Fable/Mythos) as default draft (rejected: cost not justified as a *template default*; individual loops can override when a task warrants it).

### DEC-007: Executable templates ship as real files, not inline strings
**Date:** 2026-07-17
**Decision:** The loop guardrail library lives as real files in `templates/loop/` which `new_project.py` copies into projects (like `commit.sh` behavior), amending DEC-002's "all templates as Python strings in one file" to cover document templates only.
**Reasoning:** Executable bash/js as Python string literals means escaping pain and — decisively — the kit could not run its own guard test suite. As real files, `bash templates/loop/test-guards.sh` runs green in the kit repo itself before any project inherits the guards. Trade-off: the single-file distribution promise of DEC-002 no longer holds for loop tooling; `create_loop_tooling()` degrades gracefully (warn + skip) when `templates/` is missing.
**Alternatives considered:** Inline strings per DEC-002 (untestable in-kit, unreadable escaping); a separate loops repo (yet another thing to version and clone; the kit is the natural home).

### DEC-006: Goals replace sprints as the unit of work
**Date:** 2026-07-17
**Decision:** The kit and the `project` plugin (v1.2.0) define work as **goals** with four mandatory fields — Outcome, Done when (binary verifiable conditions), Budget, Depends on. No sprints, no timeboxes. "Sprint closure" becomes "Goal closure": the `dod-reviewer` sub-agent verifies the goal's Done-when list plus the DoD checklist and answers GOAL READY TO CLOSE / GOAL NOT CLOSEABLE. Next goal is picked by friction reduction per effort. Decided in chat 2026-07-17; see `MÅL.md` in the Claude project "Development Project management" and the val26 handoff.
**Reasoning:** Sprint cadence was ceremony without benefit for a solo developer — sprint numbering and dates carried no information, and "sprint scope" was a weaker verification target than explicit binary Done-when conditions. Goals make closure machine-checkable and let priorities shift without re-planning a timebox.
**Alternatives considered:** Continued sprints (rejected — timebox ceremony adds friction, verification stays fuzzy); hybrid model with sprints wrapping goals (rejected — two units of work create ambiguity about which closure ritual applies; one enforcement point is the whole idea)

### DEC-005: Tauri projects default to Windows filesystem
**Date:** 2026-03-23
**Decision:** When stack preset 6 (Tauri) is selected, default project directory is `/mnt/c/Users/nikla/projects/` instead of `~/projects/`
**Reasoning:** Tauri desktop apps need the Windows filesystem for native builds; WSL2 native filesystem causes issues with Windows-side tooling
**Alternatives considered:** Always ask the user (adds friction); always use WSL filesystem (breaks Tauri builds)

### DEC-004: Classic GitHub tokens over fine-grained tokens
**Date:** 2026-03-15
**Decision:** Guide users to create classic Personal Access Tokens
**Reasoning:** Fine-grained tokens returned 403 on repo creation via the API; classic tokens work reliably
**Alternatives considered:** Fine-grained tokens (newer, more secure scoping, but broken for repo creation API)

### DEC-003: Commit enforcement via commit.sh instead of git hooks
**Date:** 2026-03-15
**Decision:** Use a `commit.sh` wrapper script instead of pre-commit hooks
**Reasoning:** Git hooks are invisible and confusing when they fail; a named script is explicit and discoverable. Lesson from eventplanner project: Claude forgets to update docs, so enforce it with tooling
**Alternatives considered:** Git pre-commit hook (invisible, harder to debug); relying on CLAUDE.md instructions (gets ignored under pressure)

### DEC-002: All templates as Python strings in one file
**Date:** 2026-01-01
**Decision:** Keep all templates inline in `new_project.py` as Python string literals
**Reasoning:** Single file is easy to distribute, alias, and understand. No template engine dependency. Copy one file, add one alias, done.
**Alternatives considered:** Jinja2 templates in separate files (adds dependency and complexity); YAML config (harder to read and maintain)

### DEC-001: Initial Stack Choice
**Date:** 2026-01-01
**Decision:** Python 3, single-file CLI script
**Reasoning:** Already available on WSL2, no compilation needed, fast to iterate. The script is a dev tool, not a product — simplicity wins.
**Alternatives considered:** Bash script (too painful for string templating and API calls); Node.js CLI (would need npm setup)

---
