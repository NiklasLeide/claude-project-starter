# Maintenance — claude-project-starter

> This is a dev tool, not a long-running app. "Running" = executing the script.

## How to run this project

```bash
# Option 1: via alias (recommended)
newproject

# Option 2: directly
cd ~/tools/claude-project-starter
python3 new_project.py

# Option 3: Windows launcher
# Double-click projects.bat on Windows
```

## Environment variables needed
| Variable | Where to get it | Required? |
|----------|----------------|-----------|
| `GITHUB_TOKEN` | https://github.com/settings/tokens (classic, repo+project scopes) | Only for GitHub features |

## Dependencies and versions
| Tool/Library | Version | Notes |
|-------------|---------|-------|
| Python | 3.7+ | Pre-installed on WSL2 Ubuntu |
| requests | any | `pip install requests` — only needed for GitHub API |

## File locations
- Script: `~/tools/claude-project-starter/new_project.py`
- Alias: defined in `~/.bashrc` as `alias newproject="python3 ~/tools/claude-project-starter/new_project.py"`
- Windows launcher: `~/tools/claude-project-starter/projects.bat`

## Known environment quirks
- Use `python3` not `python` — Ubuntu WSL2 doesn't symlink `python` by default
- GitHub fine-grained tokens return 403 on repo creation — use classic tokens
- projects.bat must avoid complex bash inside `for /f` — cmd.exe eats pipes and parentheses

## Last parked
_Not yet parked_

---
> Update this when setup steps change.
