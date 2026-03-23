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
