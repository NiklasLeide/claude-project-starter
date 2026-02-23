#!/usr/bin/env python3
"""
new_project.py — Niklas's Project Starter Kit
Bootstraps a new project: folder structure, all .mds, Claude Code slash commands,
GitHub repo + labels + project board + milestone.

Requirements: pip install requests  (only if using GitHub features)
GitHub token:  set GITHUB_TOKEN env var  OR  gh auth token  will be used
"""

import os
import sys
import json
import shutil
import subprocess
import datetime
from pathlib import Path

# ── Try to import requests, guide user if missing ──────────────
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# ── Config — edit these defaults ──────────────────────────────
DEFAULT_GITHUB_USER = "niklasleide"
DEFAULT_PROJECTS_DIR = str(Path.home() / "projects")

# ── Stack presets ──────────────────────────────────────────────
STACK_PRESETS = {
    "1": ("Python / FastAPI", "Python, FastAPI, Pydantic, uvicorn"),
    "2": ("Python / FastAPI + SQLite", "Python, FastAPI, SQLAlchemy, SQLite"),
    "3": ("Python / Script/CLI", "Python, argparse/click"),
    "4": ("Node.js / TypeScript", "Node.js, TypeScript, Express"),
    "5": ("Node.js / Next.js", "Node.js, TypeScript, Next.js, React"),
    "6": ("Other / Mixed", None),  # will ask
}

# ── GitHub labels ──────────────────────────────────────────────
GITHUB_LABELS = [
    ("feature",    "0e8a16", "New functionality"),
    ("bug",        "d73a4a", "Something is broken"),
    ("decision",   "0052cc", "Architectural or technical decision needed"),
    ("tech-debt",  "e4e669", "Code quality / refactor needed"),
    ("blocked",    "b60205", "Cannot proceed without resolution"),
    ("question",   "cc317c", "Needs clarification"),
    ("wontfix",    "eeeeee", "Not going to fix"),
    ("scope-creep","f9d0c4", "Out of current scope — log and defer"),
]

# ── Colors ─────────────────────────────────────────────────────
class C:
    CYAN   = "\033[96m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    RED    = "\033[91m"
    BOLD   = "\033[1m"
    DIM    = "\033[2m"
    RESET  = "\033[0m"

def header(text):  print(f"\n{C.CYAN}{C.BOLD}▶ {text}{C.RESET}")
def ok(text):      print(f"  {C.GREEN}✓{C.RESET} {text}")
def warn(text):    print(f"  {C.YELLOW}⚠{C.RESET}  {text}")
def err(text):     print(f"  {C.RED}✗{C.RESET}  {text}"); sys.exit(1)
def ask(text):     return input(f"\n{C.BOLD}{text}{C.RESET}\n> ").strip()
def dim(text):     print(f"{C.DIM}{text}{C.RESET}")

# ── Helpers ────────────────────────────────────────────────────
def run(cmd, cwd=None, check=True):
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if check and result.returncode != 0:
        warn(f"Command failed: {cmd}\n{result.stderr.strip()}")
    return result

def get_github_token():
    """Check env var and gh CLI. If neither found, guide the user interactively."""
    # 1. Environment variable
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        ok("GitHub token found in GITHUB_TOKEN env var")
        return token

    # 2. gh CLI
    result = run("gh auth token", check=False)
    if result.returncode == 0 and result.stdout.strip():
        ok("GitHub token found via gh CLI")
        return result.stdout.strip()

    # 3. Not found — guide the user
    print(f"""
{C.YELLOW}{C.BOLD}No GitHub token found.{C.RESET}

To connect this script to GitHub you need a Personal Access Token (PAT).
Here's how to create one — takes about 60 seconds:

  {C.BOLD}Step 1:{C.RESET} Open this URL in your browser:
          {C.CYAN}https://github.com/settings/tokens?type=beta{C.RESET}
          (Fine-grained tokens — more secure than classic tokens)

  {C.BOLD}Step 2:{C.RESET} Click {C.BOLD}"Generate new token"{C.RESET}

  {C.BOLD}Step 3:{C.RESET} Fill in:
          • Token name: {C.DIM}project-starter-kit{C.RESET}
          • Expiration: {C.DIM}No expiration{C.RESET} (or 1 year — your call)
          • Repository access: {C.DIM}All repositories{C.RESET}

  {C.BOLD}Step 4:{C.RESET} Under {C.BOLD}Permissions → Repository permissions{C.RESET}, set:
          • Contents:       {C.DIM}Read and write{C.RESET}
          • Issues:         {C.DIM}Read and write{C.RESET}
          • Metadata:       {C.DIM}Read-only (auto-set){C.RESET}

  {C.BOLD}Step 5:{C.RESET} Under {C.BOLD}Permissions → Account permissions{C.RESET}, set:
          • Projects:       {C.DIM}Read and write{C.RESET}  ← needed for Project boards

  {C.BOLD}Step 6:{C.RESET} Click {C.BOLD}"Generate token"{C.RESET} and {C.YELLOW}copy it immediately{C.RESET}
          (GitHub only shows it once)
""")

    token_input = input(f"{C.BOLD}Paste your token here (or press Enter to skip GitHub setup):{C.RESET}\n> ").strip()

    if not token_input:
        warn("Skipping GitHub setup — you can re-run with GITHUB_TOKEN set later.")
        return None

    # Validate token works before saving
    print("  Validating token...")
    test = requests.get(
        "https://api.github.com/user",
        headers={"Authorization": f"Bearer {token_input}", "Accept": "application/vnd.github+json"}
    )
    if test.status_code != 200:
        warn(f"Token validation failed ({test.status_code}) — check the token and try again.")
        warn("Skipping GitHub setup.")
        return None

    github_login = test.json().get("login", "unknown")
    ok(f"Token valid — authenticated as: {github_login}")

    # Offer to save to .bashrc
    save = input(f"\n{C.BOLD}Save token to ~/.bashrc so you never need to paste it again? (y/n):{C.RESET}\n> ").strip().lower()
    if save == "y":
        bashrc = Path.home() / ".bashrc"
        export_line = f'\nexport GITHUB_TOKEN="{token_input}"  # Added by project-starter-kit\n'
        with open(bashrc, "a") as f:
            f.write(export_line)
        ok(f"Saved to ~/.bashrc")
        print(f"  {C.DIM}Run 'source ~/.bashrc' after this script to activate it in your current shell.{C.RESET}")
    else:
        print(f"  {C.DIM}Not saved. To avoid this prompt next time, add to ~/.bashrc:{C.RESET}")
        print(f"  {C.DIM}export GITHUB_TOKEN=\"{token_input[:8]}...\"  # (your full token){C.RESET}")

    return token_input

def github_api(method, path, token, data=None):
    url = f"https://api.github.com{path}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    resp = getattr(requests, method)(url, headers=headers, json=data)
    return resp

# ── Step 1: Collect project info ───────────────────────────────
def collect_info():
    print(f"\n{C.CYAN}{C.BOLD}╔══════════════════════════════════════════╗")
    print(f"║    Niklas's Project Starter Kit v2.0    ║")
    print(f"╚══════════════════════════════════════════╝{C.RESET}\n")

    # Project name
    name_raw = ask("Project name (e.g. 'my cool app' or 'my-cool-app'):")
    if not name_raw:
        err("Project name is required.")
    project_name = name_raw.lower().replace(" ", "-").replace("_", "-")
    if name_raw != project_name:
        print(f"  {C.DIM}Normalized to: {project_name}{C.RESET}")

    # Description
    desc = ask("One-sentence description (you'll thank yourself later):")
    if not desc:
        desc = "[No description provided — fill this in CLAUDE.md]"

    # Stack
    print(f"\n{C.BOLD}Tech stack:{C.RESET}")
    for k, (label, _) in STACK_PRESETS.items():
        print(f"  {k}) {label}")
    stack_choice = ask("Choose a preset number, or press Enter to type freely:") or "6"
    
    if stack_choice in STACK_PRESETS and STACK_PRESETS[stack_choice][1]:
        tech_stack = STACK_PRESETS[stack_choice][1]
        ok(f"Stack: {tech_stack}")
    else:
        tech_stack = ask("Describe your stack:")
        if not tech_stack:
            tech_stack = "TBD"

    # GitHub
    github_user_input = ask(f"GitHub username (Enter to use '{DEFAULT_GITHUB_USER}'):")
    github_user = github_user_input or DEFAULT_GITHUB_USER

    # Target directory
    default_dir = os.path.join(DEFAULT_PROJECTS_DIR, project_name)
    dir_input = ask(f"Project directory (Enter for {default_dir}):")
    target_dir = dir_input or default_dir
    target_dir = os.path.expanduser(target_dir)

    # GitHub options
    print(f"\n{C.BOLD}GitHub setup:{C.RESET}")
    create_github = ask("Create GitHub repo? (y/n):").lower() == "y"
    private_repo = False
    create_board = False
    milestone_name = "MVP v0.1"
    if create_github:
        private_repo = ask("Private repo? (y/n):").lower() == "y"
        create_board  = ask("Create GitHub Project board? (y/n):").lower() == "y"
        ms_input = ask("Initial milestone name (Enter for 'MVP v0.1'):")
        milestone_name = ms_input or "MVP v0.1"

    # Summary
    print(f"\n{C.CYAN}{C.BOLD}── Summary ────────────────────────────────{C.RESET}")
    print(f"  Name:        {project_name}")
    print(f"  Description: {desc}")
    print(f"  Stack:       {tech_stack}")
    print(f"  GitHub:      github.com/{github_user}/{project_name}")
    print(f"  Directory:   {target_dir}")
    if create_github:
        print(f"  Repo:        {'private' if private_repo else 'public'}")
        print(f"  Milestone:   {milestone_name}")
    print(f"{C.CYAN}{C.BOLD}───────────────────────────────────────────{C.RESET}")

    confirm = ask("Looks good? (y/n):").lower()
    if confirm != "y":
        err("Aborted.")

    return {
        "project_name": project_name,
        "desc": desc,
        "tech_stack": tech_stack,
        "github_user": github_user,
        "target_dir": target_dir,
        "create_github": create_github,
        "private_repo": private_repo,
        "create_board": create_board,
        "milestone_name": milestone_name,
        "today": datetime.date.today().isoformat(),
    }

# ── Step 2: Create folder structure ───────────────────────────
def create_structure(cfg):
    header("Creating project structure")
    dirs = [
        cfg["target_dir"],
        os.path.join(cfg["target_dir"], "docs"),
        os.path.join(cfg["target_dir"], ".claude", "commands"),
    ]
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)
    ok(f"Folders created at {cfg['target_dir']}")

# ── Step 3: Write all .md files ───────────────────────────────
def write_file(path, content):
    Path(path).write_text(content, encoding="utf-8")
    ok(os.path.relpath(path, path.split("docs")[0].rstrip("/\\")))

def create_docs(cfg):
    header("Generating documentation files")
    d = cfg["target_dir"]
    p = cfg["project_name"]
    today = cfg["today"]
    stack = cfg["tech_stack"]
    user = cfg["github_user"]
    desc = cfg["desc"]

    # ── CLAUDE.md ──────────────────────────────────────────────
    write_file(os.path.join(d, "CLAUDE.md"), f"""\
# {p}

{desc}

**Stack:** {stack}
**Started:** {today}
**GitHub:** github.com/{user}/{p}

## Session Start — ALWAYS do this first
1. Read `@docs/PROJECT_STATUS.md` — understand current state
2. Read `@docs/DECISIONS.md` — don't propose changes that contradict past decisions
3. Check `@docs/TROUBLESHOOTING.md` before proposing solutions to errors

These files ARE Claude's memory between sessions. Keep them accurate.

## Commands
```bash
# Fill in your run/test/build commands here after setup
# e.g.:
# python -m uvicorn main:app --reload   ← start dev server
# pytest tests/                         ← run tests
# python scripts/setup.py               ← first-time setup
```

## Architecture
See `@docs/DECISIONS.md` for all architectural decisions and reasoning.
**Do not make architectural choices without consulting this file first.**

## Directory Structure
```
{p}/
├── CLAUDE.md              ← you are here (keep under 150 lines)
├── docs/
│   ├── DECISIONS.md       ← decision log — WHY choices were made
│   ├── PROJECT_STATUS.md  ← sprint tasks, blockers, what's working
│   ├── TROUBLESHOOTING.md ← known issues grouped by category
│   ├── CHANGELOG.md       ← what changed and when
│   └── ROADMAP.md         ← sprints and feature backlog
└── .claude/commands/      ← custom slash commands
```

## Commit Rule (non-negotiable)
**After every completed task:** `git add`, `git commit`, `git push`.
Every commit must include updated `PROJECT_STATUS.md` if tasks changed state.
If a decision was made: update `DECISIONS.md`.
If a bug was hit and fixed: update `TROUBLESHOOTING.md`.

Use `./commit.sh` if it exists — it walks through the checklist.

## Coding Conventions
- Prefer simple and readable over clever
- Add comments for non-obvious logic — future sessions have no memory
- All errors logged, never silently swallowed
- Environment variables via `.env` (never committed — use `.env.example`)
- When a pattern exists in the codebase, follow it; ask before deviating

## Claude's Role
You are a **critical friend**, not a yes-machine.

- Challenge architectural decisions before implementing — ask "is there a simpler way?"
- Flag scope creep: "do we actually need this in the current sprint?"
- Point out technical debt being introduced
- Don't rely on reminding me to do things — if something must happen every time, suggest we automate or enforce it with tooling (lesson from a past project: prompts get forgotten, hooks don't)
- Be direct. Skip flattery. If something is wrong, say so.
- If context window is >70% full, say so and suggest /compact before continuing
- Scope each session to ONE feature or ONE bug — push back if asked to do more

## What Claude Gets Wrong on This Project
<!-- HIGHEST VALUE SECTION — fill in after your first 2-3 sessions -->
<!-- Example: "Tends to create new files instead of extending existing ones" -->
- TBD
""")

    # ── DECISIONS.md ───────────────────────────────────────────
    write_file(os.path.join(d, "docs", "DECISIONS.md"), f"""\
# Decision Log — {p}

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

### DEC-001: Initial Stack Choice
**Date:** {today}
**Decision:** {stack}
**Reasoning:** [Fill in — why this stack for this project?]
**Alternatives considered:** [Fill in — what did you rule out and why?]

---
""")

    # ── PROJECT_STATUS.md ──────────────────────────────────────
    write_file(os.path.join(d, "docs", "PROJECT_STATUS.md"), f"""\
# Project Status — {p}

> **Last updated:** {today}
> **Current sprint:** Sprint 0 – Setup
> **Sprint dates:** {today} → TBD

---

## Current Sprint: Sprint 0 – Setup

| # | Task | Status | Notes |
|---|------|--------|-------|
| 0.1 | Define first feature | ⬜ Todo | |
| 0.2 | Create first GitHub issue | ⬜ Todo | |

**Status legend:** ⬜ Todo | 🔄 In Progress | ✅ Done | 🚫 Blocked | ⏸️ Paused

---

## What's Working Now
_Nothing yet — fill this in as components come online._

```bash
# Add runnable commands here as they become available
# e.g.: python main.py    ← starts the app
```

---

## Blockers
_None_

---

## Sprint Backlog

### Sprint 1 – [Name] (Target: TBD)
- [ ] [Feature/task]

### Sprint 2 – [Name] (Target: TBD)
- [ ] [Feature/task]

---

## Key Metrics to Track
<!-- What does "working" actually mean for this project? Define it here. -->
- TBD

---
> Update this at the **end** of each Claude Code session, not the beginning.
> Move completed tasks to ✅ Done. Keep Blockers current.
""")

    # ── TROUBLESHOOTING.md ─────────────────────────────────────
    write_file(os.path.join(d, "docs", "TROUBLESHOOTING.md"), f"""\
# Troubleshooting — {p}

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

## WSL2 / Environment

### WSL2: permission errors on /mnt/c/
**Symptom:** Permission errors running scripts or tools on files under `/mnt/c/`.
**Cause:** Windows filesystem mounted at `/mnt/c/` doesn't support Linux permissions.
**Solution:** Keep the project on the native WSL filesystem (`~/projects/`). Only use `/mnt/c/` for dropping files from Windows.

### git init fails or behaves unexpectedly
**Symptom:** `git init` or git operations fail on `/mnt/c/`.
**Cause:** Same filesystem permission issue as above.
**Solution:** Keep the git repo on native WSL: `~/projects/{p}`.

### Python venv fails
**Symptom:** `python -m venv` fails or venv doesn't work.
**Cause:** Symlinks and permissions broken on mounted Windows filesystem.
**Solution:** Create venv on native WSL: `python3 -m venv ~/venv-{p}`

---

## Claude Code

### Claude Code auto-update fails on startup
**Symptom:** Warning on startup that Claude Code failed to auto-update.
**Cause:** Global npm packages need sudo; auto-updater doesn't use it.
**Solution:** `sudo npm install -g @anthropic-ai/claude-code`
Not critical — Claude Code still works, it's just a warning.

### Claude Code forgets to update PROJECT_STATUS.md
**Symptom:** Tasks get done but PROJECT_STATUS.md stays stale.
**Cause:** Prompt-based rules in CLAUDE.md get missed when Claude is focused on code.
**Solution:** Don't rely on prompts — enforce with tooling. Use a `commit.sh` script
or git hooks that check documentation is updated before pushing.
**General principle:** If something needs to happen every time, automate it. Never rely on Claude remembering.

---

## Git / GitHub

### npm global install needs sudo
**Symptom:** `npm install -g` fails with permission errors.
**Solution:** `sudo npm install -g <package>`

---
## {stack.split(',')[0].strip()} / App

_Add issues here as you encounter them._

---
""")

    # ── CHANGELOG.md ───────────────────────────────────────────
    write_file(os.path.join(d, "docs", "CHANGELOG.md"), f"""\
# Changelog — {p}

Format: `[YYYY-MM-DD] type: description`
Types: `feat` | `fix` | `refactor` | `docs` | `chore` | `perf`

---

[{today}] chore: project initialized via starter kit
""")

    # ── ROADMAP.md ─────────────────────────────────────────────
    write_file(os.path.join(d, "docs", "ROADMAP.md"), f"""\
# Roadmap — {p}

> Keep this honest. If something's not happening, move it to Deferred — don't leave it rotting in Next.

## Now (Sprint 0 — Setup)
- [ ] Define first feature
- [ ] Get to a working "hello world" end-to-end

## Sprint 1 — [Name]
- [ ] [Feature]

## Sprint 2 — [Name]
- [ ] [Feature]

## Later / Stretch
_TBD_

## Deferred / Won't Do
_Decisions against features — include a one-line reason so you don't revisit them_

---
""")

    # ── .gitignore ─────────────────────────────────────────────
    write_file(os.path.join(d, ".gitignore"), """\
.env
.env.*
.env.local
__pycache__/
*.pyc
*.pyo
.venv/
venv/
node_modules/
.DS_Store
*.log
dist/
build/
.pytest_cache/
.mypy_cache/
*.egg-info/
.coverage
htmlcov/
""")
    ok(".gitignore")

    # ── .env.example ───────────────────────────────────────────
    write_file(os.path.join(d, ".env.example"), """\
# Copy this to .env and fill in real values
# NEVER commit .env to git

# Example:
# API_KEY=your_key_here
# DATABASE_URL=sqlite:///./app.db
""")
    ok(".env.example")

# ── Step 4: Claude slash commands ─────────────────────────────
def create_commands(cfg):
    header("Creating Claude Code slash commands")
    cmd_dir = os.path.join(cfg["target_dir"], ".claude", "commands")

    commands = {
        "brief.md": """\
Session start. Do this silently — read but do not output full file contents:
1. Read @docs/PROJECT_STATUS.md
2. Read @docs/DECISIONS.md (last 3 entries only)
3. Read @docs/TROUBLESHOOTING.md (headings only — know what categories exist)

Then give me exactly this, in under 120 words:
- Current sprint and what's in progress
- Last decision made (one line)
- Any active blockers
- What "What's Working Now" says I can run

Then ask: "What are we working on today?"

Do not start coding. Do not summarise files back to me in full.
We are conserving context — one feature per session.
""",

        "status.md": """\
Read @docs/PROJECT_STATUS.md and @docs/ROADMAP.md silently.

Report:
- Current sprint name and dates
- Tasks in progress (🔄) and blocked (🚫)
- What's next up in the backlog
- Any metrics defined and their current state

Do not start coding. This is read-only.
""",

        "decide.md": """\
I need to make a technical or architectural decision.

Before I describe it, confirm you have read @docs/DECISIONS.md so you know what's already been decided.

Then:
1. Ask me to describe the decision and my preferred option
2. Ask what alternatives I've already considered and dismissed
3. Challenge my preferred option — what could go wrong? What does it make harder later?
4. Ask: is there a simpler option I haven't mentioned?

Only after that conversation, help me write a new entry for @docs/DECISIONS.md.
Use the existing format in that file (DEC-NNN, Date, Decision, Reasoning, Alternatives considered).
Newest entries go at the TOP of the file.

Do not validate my first instinct. Your job is to make me think harder before committing.
""",

        "review.md": """\
Review the most recent code changes critically.

First run: `git diff HEAD~1 --name-only` to see what changed.

For each significant file changed:
1. Is there a simpler approach?
2. What technical debt is this introducing?
3. Missing error handling or edge cases?
4. Does this align with @docs/DECISIONS.md — are we drifting from agreed architecture?
5. Anything that should go in @docs/TROUBLESHOOTING.md?

Be specific. No filler. If something is fine, say so in one word and move on.
Flag scope creep if you see it.
""",

        "log.md": """\
End-of-session update. Do all of these:

1. Run `git diff HEAD~1 --stat` to see what changed this session
2. Update @docs/CHANGELOG.md — add one line per logical change:
   Format: [YYYY-MM-DD] type: description
3. Update @docs/PROJECT_STATUS.md:
   - Change task statuses (⬜/🔄/✅) to reflect reality
   - Update "Last updated" date
   - Update "What's Working Now" if new things are runnable
4. If a new decision was made this session: remind me to run /project:decide before closing
5. If a new bug was hit and fixed: add it to @docs/TROUBLESHOOTING.md

Then: `git add docs/ && git commit -m "docs: session update [date]" && git push`
""",

        "scope.md": """\
I want to add a new feature or task. Before I describe it:

1. Ask me to describe the feature
2. Ask: which sprint does this belong in — current or future?
3. Ask: what existing code does this touch or risk breaking?
4. Ask: what's the minimum version that delivers real value? (push me to cut scope)
5. Ask: is this in @docs/ROADMAP.md already, or new?

Then help me:
- Write a GitHub issue: title, description, acceptance criteria, label suggestions
- Add it to the correct sprint in @docs/PROJECT_STATUS.md
- Add it to @docs/ROADMAP.md if it's not there

Challenge scope. One session = one focused thing.
""",
    }

    for fname, content in commands.items():
        write_file(os.path.join(cmd_dir, fname), content)

    ok("5 slash commands created")
    print(f"  {C.DIM}/project:brief   — token-efficient session start")
    print(f"  /project:status  — read-only project overview")
    print(f"  /project:decide  — guided ADR (Claude challenges first)")
    print(f"  /project:review  — critical code review")
    print(f"  /project:log     — update changelog + status")
    print(f"  /project:scope   — new feature scoping + issue draft{C.RESET}")

# ── Step 5: Git init ───────────────────────────────────────────
def init_git(cfg):
    header("Initializing git")
    d = cfg["target_dir"]
    run("git init -q", cwd=d)
    run("git add .", cwd=d)
    run('git commit -q -m "chore: project initialized via starter kit"', cwd=d)
    ok("Git repo initialized with initial commit")

# ── Step 6: GitHub setup ───────────────────────────────────────
def setup_github(cfg):
    header("Setting up GitHub")

    if not HAS_REQUESTS:
        print(f"""
{C.YELLOW}{C.BOLD}Missing dependency: 'requests'{C.RESET}

The GitHub setup requires the requests library. Fix it with:

  {C.CYAN}pip install requests{C.RESET}

Then re-run: {C.CYAN}python new_project.py{C.RESET}
""")
        return

    token = get_github_token()
    if not token:
        return

    user  = cfg["github_user"]
    name  = cfg["project_name"]
    desc  = cfg["desc"]
    priv  = cfg["private_repo"]

    # Create repo
    print(f"  Creating repo github.com/{user}/{name}...")
    resp = github_api("post", "/user/repos", token, {
        "name": name,
        "description": desc,
        "private": priv,
        "auto_init": False,
    })
    if resp.status_code == 201:
        ok(f"Repo created: github.com/{user}/{name}")
    elif resp.status_code == 422:
        warn(f"Repo already exists — skipping creation")
    else:
        warn(f"Repo creation failed ({resp.status_code}): {resp.json().get('message','')}")
        return

    # Push
    d = cfg["target_dir"]
    remote_url = f"https://github.com/{user}/{name}.git"
    run(f"git remote add origin {remote_url}", cwd=d, check=False)
    result = run("git push -u origin main", cwd=d, check=False)
    if result.returncode != 0:
        result = run("git push -u origin master", cwd=d, check=False)
    if result.returncode == 0:
        ok("Pushed to GitHub")
    else:
        warn("Could not push automatically — run: git push -u origin main")

    # Delete default labels
    print("  Cleaning up default GitHub labels...")
    existing = github_api("get", f"/repos/{user}/{name}/labels", token)
    if existing.status_code == 200:
        for label in existing.json():
            github_api("delete", f"/repos/{user}/{name}/labels/{requests.utils.quote(label['name'])}", token)

    # Create custom labels
    print("  Creating project labels...")
    for label_name, color, desc_l in GITHUB_LABELS:
        r = github_api("post", f"/repos/{user}/{name}/labels", token, {
            "name": label_name,
            "color": color,
            "description": desc_l,
        })
        if r.status_code in (201, 422):
            ok(f"Label: {label_name}")
        else:
            warn(f"Label '{label_name}' failed: {r.status_code}")

    # Create milestone
    milestone_name = cfg["milestone_name"]
    print(f"  Creating milestone '{milestone_name}'...")
    r = github_api("post", f"/repos/{user}/{name}/milestones", token, {
        "title": milestone_name,
        "description": "First working version",
    })
    if r.status_code == 201:
        ok(f"Milestone: {milestone_name}")
    else:
        warn(f"Milestone creation failed: {r.status_code}")

    # Create GitHub Project board (v2 via GraphQL)
    if cfg["create_board"]:
        print("  Creating GitHub Project board...")
        # Get user node ID first
        user_resp = github_api("get", f"/users/{user}", token)
        if user_resp.status_code == 200:
            owner_id = user_resp.json().get("node_id")
            gql_url = "https://api.github.com/graphql"
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }
            mutation = """
            mutation($ownerId: ID!, $title: String!) {
              createProjectV2(input: {ownerId: $ownerId, title: $title}) {
                projectV2 { url }
              }
            }
            """
            r = requests.post(gql_url, headers=headers, json={
                "query": mutation,
                "variables": {"ownerId": owner_id, "title": cfg["project_name"]},
            })
            if r.status_code == 200 and "errors" not in r.json():
                url = r.json()["data"]["createProjectV2"]["projectV2"]["url"]
                ok(f"Project board: {url}")
            else:
                warn("Project board creation failed — create manually at github.com")
        else:
            warn("Could not get user ID for project board creation")

# ── Step 7: Final output ───────────────────────────────────────
def finish(cfg):
    p = cfg["project_name"]
    d = cfg["target_dir"]
    u = cfg["github_user"]

    print(f"\n{C.GREEN}{C.BOLD}╔══════════════════════════════════════════════════╗")
    print(f"║  ✓ Ready: {p:<39}║")
    print(f"╚══════════════════════════════════════════════════╝{C.RESET}")

    print(f"""
{C.BOLD}Step 1 — Open in VS Code:{C.RESET}
  {C.CYAN}code {d}{C.RESET}
  (Opens VS Code connected to WSL2 — edit CLAUDE.md, docs/, everything from there)

{C.BOLD}Step 2 — Fill in CLAUDE.md:{C.RESET}
  Add your run/test/build commands under the Commands section.
  VS Code: Ctrl+P → type CLAUDE.md → open it.

{C.BOLD}Step 3 — Start Claude Code:{C.RESET}
  In VS Code: open the integrated terminal (Ctrl+`) then:
  {C.CYAN}claude{C.RESET}

{C.BOLD}Step 4 — First prompt:{C.RESET}
  {C.CYAN}/project:brief{C.RESET}
  Claude reads your docs and asks what you're building today.

{C.BOLD}Slash commands:{C.RESET}
  {C.CYAN}/project:brief{C.RESET}   Start-of-session briefing (token-efficient)
  {C.CYAN}/project:status{C.RESET}  Where are we / what's next
  {C.CYAN}/project:decide{C.RESET}  Guided decision + ADR log (Claude challenges you first)
  {C.CYAN}/project:review{C.RESET}  Critical code review
  {C.CYAN}/project:log{C.RESET}     Update changelog + status from git
  {C.CYAN}/project:scope{C.RESET}   Scope a new feature + draft GitHub issue

{C.BOLD}GitHub:{C.RESET}
  {C.CYAN}https://github.com/{u}/{p}{C.RESET}

{C.YELLOW}Tip: One feature per Claude session. /project:brief to start, /project:log to end.
Never paste file contents into Claude — use @path instead.{C.RESET}
""")

# ── Main ───────────────────────────────────────────────────────
def main():
    try:
        cfg = collect_info()
        create_structure(cfg)
        create_docs(cfg)
        create_commands(cfg)
        init_git(cfg)
        if cfg["create_github"]:
            setup_github(cfg)
        finish(cfg)
    except KeyboardInterrupt:
        print(f"\n{C.YELLOW}Aborted.{C.RESET}")
        sys.exit(0)

if __name__ == "__main__":
    main()
