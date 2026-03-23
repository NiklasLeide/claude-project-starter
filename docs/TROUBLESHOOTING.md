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
