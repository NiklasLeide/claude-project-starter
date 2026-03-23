# Roadmap — claude-project-starter

> Keep this honest. If something's not happening, move it to Deferred — don't leave it rotting in Next.

## Done
- [x] Core project scaffolding (folders, docs, .gitignore, .env.example)
- [x] 9 stack presets (Python, Node, Tauri, Spring Boot, Vert.x)
- [x] GitHub integration (repo, labels, milestone, project board)
- [x] 8 slash commands (brief, status, decide, review, log, scope, parkhere, resume)
- [x] commit.sh enforcement script in template
- [x] MAINTENANCE.md template
- [x] CLAUDE.md for this repo itself
- [x] projects.bat Windows launcher (multi-directory scanning, dedup)
- [x] Tauri projects auto-default to Windows filesystem

## Next
- [ ] Add stack presets as new project types emerge
- [ ] Template refinements based on lessons from real projects
- [ ] Consider adding a `/project:retro` slash command for sprint retrospectives

## Later / Stretch
- [ ] Interactive stack-specific setup (e.g. auto-run `npm init` for Node projects)
- [ ] Auto-detect existing project structure and skip conflicting steps

## Deferred / Won't Do
- Jinja2 templates — adds a dependency for no real gain; inline strings are fine for this scale
- Web UI — this is a CLI tool for devs, a UI adds complexity without value

---
