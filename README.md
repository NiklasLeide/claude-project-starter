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
├── CLAUDE.md                    ← Claude's brain (lean, <150 lines)
├── .gitignore
├── .env.example
├── docs/
│   ├── DECISIONS.md             ← ADR log (the WHY)
│   ├── PROJECT_STATUS.md        ← current sprint + blockers
│   ├── TROUBLESHOOTING.md       ← issues + fixes
│   ├── CHANGELOG.md             ← what changed + when
│   └── ROADMAP.md               ← features, prioritized
└── .claude/commands/
    ├── brief.md                 ← /project:brief
    ├── status.md                ← /project:status
    ├── decide.md                ← /project:decide
    ├── review.md                ← /project:review
    ├── log.md                   ← /project:log
    └── scope.md                 ← /project:scope
```

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

## The philosophy baked in

**Non-sycophantic Claude:** CLAUDE.md explicitly instructs Claude to challenge decisions, flag scope creep, and skip flattery. `/project:decide` forces the conversation before the ADR is written.

**Token efficiency:**
- CLAUDE.md under 150 lines
- Docs referenced via `@path` — not inlined into context
- `/project:brief` loads only what's needed per session
- One-feature-per-session boundary enforced by Claude

**Decision trail:** DECISIONS.md logs what you chose AND what you rejected. The rejected alternatives are the valuable part.

## First session

```bash
cd your-project
claude
/project:brief
# Claude reads status, then asks what you're building today
# Describe your first feature
# Claude will ask critical questions before writing code
```

## Make it a global command (WSL2)

```bash
# Put the script somewhere permanent
mkdir -p ~/tools/project-starter
cp new_project.py ~/tools/project-starter/

# Add alias to ~/.bashrc
echo 'alias newproject="python ~/tools/project-starter/new_project.py"' >> ~/.bashrc
source ~/.bashrc

# Now anywhere:
newproject
```

## Lessons applied from the lifecoach project

- Don't inline docs in CLAUDE.md — use `@path` references to preserve tokens
- CLAUDE.md over 150 lines = instruction quality degrades, Claude starts ignoring things
- ADRs without the alternatives column are nearly useless — the template forces this
- `/project:brief` at session start beats copy-pasting context every time
- `## What Claude Gets Wrong` section in CLAUDE.md is the highest-ROI section — fill it in after 2-3 sessions
- Changelog + status update at session *end* not beginning — otherwise it never happens
