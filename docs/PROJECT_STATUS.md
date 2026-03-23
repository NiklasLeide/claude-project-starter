# Project Status — claude-project-starter

> **Last updated:** 2026-03-23
> **Current phase:** Stable / Iterative improvement
> **Status:** Active tool, improved after each real project

---

## What's Working Now

Everything. This is a mature tool in active use.

```bash
newproject                    # run the starter kit (alias)
python3 new_project.py        # alternative
./projects.bat                # Windows launcher — pick or create projects
```

### Features
- Interactive project setup (~8 questions)
- 9 stack presets (Python, Node, Tauri, Spring Boot, Vert.x, etc.)
- Full doc scaffold: CLAUDE.md, DECISIONS.md, PROJECT_STATUS.md, TROUBLESHOOTING.md, CHANGELOG.md, ROADMAP.md, MAINTENANCE.md
- 8 Claude Code slash commands (brief, status, decide, review, log, scope, parkhere, resume)
- GitHub repo creation with custom labels, milestone, project board
- commit.sh enforcement script
- Tauri projects auto-placed on Windows filesystem
- projects.bat: Windows batch launcher scanning 4 project directories

---

## Recent Improvements (latest first)

| Date | Change | Source |
|------|--------|--------|
| 2026-03-23 | Tauri projects auto-default to /mnt/c/.../projects/ | Stack usage |
| 2026-03-23 | projects.bat scans ~/projects/, /mnt/c/.../projects/, ~/tools/, ~/lifecoach-app-repo | Workflow need |
| 2026-03-23 | projects.bat created — Windows launcher for projects | Workflow need |
| 2026-03-15 | commit.sh enforcement added to template | Lesson from eventplanner |
| 2026-03-15 | Classic GitHub tokens, Tauri/Spring Boot/Vert.x presets | Bug fix + expansion |
| 2026-03-15 | parkhere + resume slash commands, MAINTENANCE.md template | Maintenance workflow |

---

## Blockers
_None_

---

## Backlog
- [ ] Add more stack presets as new projects use them
- [ ] Consider sorting projects.bat list alphabetically
- [ ] Template improvements based on lessons from future projects

---
> Update this after each improvement session.
