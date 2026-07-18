# Niklas's Project Starter Kit v2

One script. Under 2 minutes. Ready to code.

## What it does

1. Asks ~8 questions — name, description, stack, GitHub prefs
2. Creates the full folder + doc structure
3. Writes lean, pre-filled `.md` files (CLAUDE.md, DECISIONS.md, PROJECT_STATUS.md, TROUBLESHOOTING.md, CHANGELOG.md, ROADMAP.md)
4. Installs 6 custom Claude Code slash commands
5. Runs `git init` + initial commit
6. Creates GitHub repo, cleans up default labels, adds custom labels, creates milestone, creates Project board

## Requirements

```bash
# Python 3.7+ (you have this)
pip install requests         # for GitHub API calls

# GitHub auth — one of:
export GITHUB_TOKEN=ghp_...  # personal access token
# OR:
gh auth login                # if you have gh CLI installed
```

**GitHub token needs:** `repo`, `project` scopes.  
Create at: https://github.com/settings/tokens

## Usage

```bash
python new_project.py
```

That's it. Answer the questions, confirm, done.

## What gets created

```
your-project/
├── CLAUDE.md                    ← Claude's brain (references shared-conventions via plugin)
├── RESEARCH_AGENT.md            ← (optional) domain research methodology template
├── .gitignore
├── .env.example
├── commit.sh                    ← enforced commit workflow
├── docs/
│   ├── DECISIONS.md             ← ADR log (the WHY)
│   ├── PROJECT_STATUS.md        ← goals + blockers
│   ├── TROUBLESHOOTING.md       ← issues + fixes
│   ├── CHANGELOG.md             ← what changed + when
│   └── ROADMAP.md               ← features, prioritized
├── .claude/
│   └── settings.json            ← declares project plugin
└── .github/workflows/
    └── changelog-check.yml      ← blocks PRs if src/ changed without CHANGELOG
```

The plugin (`project@niklas-marketplace`) provides:
- `shared-conventions.md` — commit rule, DoD, goal closure, communication, brief format
- Slash commands — /project:brief, :status, :decide, :review, :log, :scope, :init, :resume, :parkhere
- Sub-agents — dod-reviewer (goal closure verification), code-researcher (tactical API research)
- Universal MCPs — Context7 (up-to-date library docs via `npx`), GitHub (remote HTTP, auth via `${GITHUB_TOKEN}`)

Tauri projects also get `rust-analyzer-lsp@claude-plugins-official` (from `superpowers-marketplace`) declared in their generated `.claude/settings.json` — non-Tauri projects do not.

**Plugin bump routine:** the root `shared-conventions.md` here is canonical (chat counterparts fetch it by raw URL). Before every plugin version bump, run `bash scripts/sync-conventions.sh <marketplace-path> --push-to-plugin` so the plugin ships the same text; the check mode (no flag) exits 1 on drift.

## GitHub labels created

| Label | Color | Purpose |
|-------|-------|---------|
| `feature` | green | New functionality |
| `bug` | red | Something broken |
| `decision` | blue | Architectural choice needed |
| `tech-debt` | yellow | Refactor needed |
| `blocked` | dark red | Cannot proceed |
| `question` | pink | Needs clarification |
| `wontfix` | grey | Not going to fix |
| `scope-creep` | light pink | Out of current scope |

## Slash commands

| Command | What it does |
|---------|-------------|
| `/project:brief` | Token-efficient session start. Reads status + last decisions, asks what you're building today |
| `/project:status` | Read-only overview of phase, in-progress, blockers, next |
| `/project:decide` | Claude challenges your decision BEFORE logging the ADR — plays devil's advocate |
| `/project:review` | Critical code review: simpler alternatives? tech debt? scope creep? |
| `/project:log` | Updates CHANGELOG.md + PROJECT_STATUS.md from recent git changes |
| `/project:scope` | Scopes a new feature, asks minimum viable version, drafts GitHub issue |

## Plugin dependency

Generated projects depend on the `project` plugin from the
`niklas-marketplace` private marketplace (GitHub: NiklasLeide/niklas-marketplace).

For Claude Code to fetch the plugin, you need GitHub authentication:
- `gh auth login` (recommended), or
- `GITHUB_TOKEN` env var with `repo` scope

The plugin is declared in each project's `.claude/settings.json`. Claude Code
syncs it automatically on startup.

## The philosophy baked in

**Non-sycophantic Claude:** CLAUDE.md explicitly instructs Claude to challenge decisions, flag scope creep, and skip flattery. `/project:decide` forces the conversation before the ADR is written.

**Token efficiency:**
- CLAUDE.md under 150 lines
- Docs referenced via `@path` — not inlined into context
- `/project:brief` loads only what's needed per session
- One-feature-per-session boundary enforced by Claude

**Decision trail:** DECISIONS.md logs what you chose AND what you rejected. The rejected alternatives are the valuable part.

**Plugin-based conventions:** Shared conventions, slash commands, and sub-agents live in a centralized plugin. Updating the plugin version propagates improvements to all projects — no manual file copying.

**Enforceable goal closure:** Work is defined as goals with binary Done-when conditions. The final Done-when item of every goal is "Run DoD review (goal closure)" — the `dod-reviewer` sub-agent verifies each condition plus the DoD checklist. Goals cannot be closed with open gaps.

**Layered enforcement:** `commit.sh` blocks commits without CHANGELOG updates. The GitHub Action blocks PRs with the same rule. The goal closure review catches anything that slipped through.

**Loop guardrails (opt-in):** `scripts/loop/` ships code-enforced guards for autonomous Claude loops — budget caps checked before every call, fail-closed cost parsing, HEAD-guard with self-healing tamper handling, mtime-scoped limit detection, semantic exit codes, detached launch, resume guard — plus a test suite (`test-guards.sh`) that simulates every failure mode. Enforcement in code, not configuration: proven in val26's production loops (July 2026).

## First session

```bash
cd your-project
claude
/project:brief
# Claude reads status, then asks what you're building today
# Describe your first feature
# Claude will ask critical questions before writing code
```

## Make it a global command (Windows)

The kit lives at `C:\Users\nikla\tools\claude-project-starter`. Development is
Windows-native (DEC-010) — scripts run under Git Bash, no WSL involved.

The launcher is `projects.bat` (pin it to the taskbar or a Start-menu
shortcut). It lists every project under `C:\Users\nikla\projects` and
`C:\Users\nikla\tools`, then:

- a **number** opens that project in VS Code
- **N** starts a new project (`python new_project.py`)
- **U** updates a project (`python new_project.py --update <path>`)

To run the generator directly:

```bat
python C:\Users\nikla\tools\claude-project-starter\new_project.py
```

## Lessons applied from the lifecoach project

- Don't inline docs in CLAUDE.md — use `@path` references to preserve tokens
- CLAUDE.md over 150 lines = instruction quality degrades, Claude starts ignoring things
- ADRs without the alternatives column are nearly useless — the template forces this
- `/project:brief` at session start beats copy-pasting context every time
- `## What Claude Gets Wrong` section in CLAUDE.md is the highest-ROI section — fill it in after 2-3 sessions
- Changelog + status update at session *end* not beginning — otherwise it never happens
