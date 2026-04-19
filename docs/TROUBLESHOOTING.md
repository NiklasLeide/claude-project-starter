# Troubleshooting — claude-project-starter

Known issues and solutions. Check here before debugging. Add here when you fix something.

---

## Format
```
### Issue title
**Symptom:** What you observed
**Cause:** Why it happened
**Solution:** What fixed it
```

---

## GitHub API

### 403 on repo creation
**Symptom:** `github_api("post", "/user/repos", ...)` returns 403 Forbidden.
**Cause:** Fine-grained GitHub tokens don't work reliably for repo creation via the REST API.
**Solution:** Use classic Personal Access Tokens with `repo` and `project` scopes. Guide added to `get_github_token()`.

### Token not found
**Symptom:** Script says "No GitHub token found" even though `gh` is installed.
**Cause:** `gh auth token` not returning a token — user may not have run `gh auth login`.
**Solution:** Either run `gh auth login` or set `GITHUB_TOKEN` env var in `~/.bashrc`.

---

## Plugin

### SessionStart hook from plugin doesn't produce visible output
**Symptom:** After enabling `project@niklas-marketplace` v1.0.2 in a project's `.claude/settings.json`, the DoD reminder (meant to print at session start via `hooks/hooks.json`) does not appear in the Claude Code transcript. No "Failed to load hooks" error in `/plugin` once v1.0.2 loaded — the hook file parses and the plugin is enabled.
**What we know:**
- v1.0.0 wrapper structure: `{"description": ..., "hooks": {"SessionStart": [{"hooks": [...]}]}}` — missing `matcher`, did not fire.
- v1.0.1 flat structure: `{"SessionStart": [{"matcher": "startup", "hooks": [...]}]}` — failed to load (`invalid_type` on `hooks` path).
- v1.0.2 wrapper + matcher: `{"hooks": {"SessionStart": [{"matcher": "startup", "hooks": [...]}]}}` — loads without error but reminder text is not visible in session output.
- The hook command is `cat "${CLAUDE_PLUGIN_ROOT}/session-start-reminder.txt" 2>/dev/null || true` and the reminder file exists in the plugin cache.
**Next diagnostic steps (for v1.0.3 work item):**
1. Run `/plugin` in a fresh session and capture any hook-loading info to confirm the SessionStart hook is registered.
2. Replace the `cat` command with something that writes to a known log (e.g. `date >> /tmp/claude-hook.log`) to verify the hook actually fires — isolates "hook not firing" from "stdout not surfacing".
3. Check Claude Code docs/release notes for whether plugin-provided SessionStart stdout is currently piped to the transcript (may differ from project-local `.claude/settings.json` hooks).
4. If the hook fires but stdout is suppressed, consider switching to an `additionalContext` or `systemMessage` output type per hook schema instead of plain command stdout.
**Status:** Tracked as a v1.0.3 work item. Plugin is otherwise functional — slash commands, sub-agents, marketplace updates all work.

---

## WSL2 / Environment

### `python` command not found
**Symptom:** `python new_project.py` fails with "command not found".
**Cause:** Ubuntu WSL2 only has `python3` by default, no `python` symlink.
**Solution:** Use `python3 new_project.py` or the `newproject` alias (which uses python3).

### projects.bat opens but nothing happens
**Symptom:** Double-clicking projects.bat on Windows opens a cmd window that immediately closes or shows nothing.
**Cause:** Complex `wsl bash -c` commands with unescaped `(`, `)`, and `|` characters get parsed by cmd.exe as batch syntax before WSL receives them.
**Solution:** Use simple `wsl ls` calls in `for /f` loops instead of complex bash one-liners. Deduplicate in batch with `seen_` variables.

### `requests` module not installed
**Symptom:** GitHub setup fails with ImportError.
**Cause:** `requests` is not in Python's standard library.
**Solution:** `pip install requests`

---

## Batch File (projects.bat)

### Pipe and parentheses in for /f
**Symptom:** `for /f` with `wsl bash -c` containing `|` or `()` silently fails.
**Cause:** cmd.exe interprets these as batch operators before passing to WSL.
**Solution:** Avoid complex bash in `for /f`. Use multiple simple `wsl ls` calls instead.

---
