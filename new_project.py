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
WINDOWS_PROJECTS_DIR = "/mnt/c/Users/nikla/projects"

# ── Stack presets ──────────────────────────────────────────────
STACK_PRESETS = {
    "1": ("Python / FastAPI", "Python, FastAPI, Pydantic, uvicorn"),
    "2": ("Python / FastAPI + SQLite", "Python, FastAPI, SQLAlchemy, SQLite"),
    "3": ("Python / Script/CLI", "Python, argparse/click"),
    "4": ("Node.js / TypeScript", "Node.js, TypeScript, Express"),
    "5": ("Node.js / Next.js", "Node.js, TypeScript, Next.js, React"),
    "6": ("React / Tauri desktop app", "React 19, TypeScript, Vite, Tailwind CSS, Tauri"),
    "7": ("Java / Spring Boot", "Java 21, Spring Boot 3, Maven, Docker"),
    "8": ("Java / Vert.x", "Java 21, Vert.x, Maven, Docker"),
    "9": ("Other / Mixed", None),  # will ask
}

# ── Test command per stack ────────────────────────────────────
STACK_TEST_COMMANDS = {
    "1": "pytest",                    # Python / FastAPI
    "2": "pytest",                    # Python / FastAPI + SQLite
    "3": "pytest",                    # Python / Script/CLI
    "4": "npx jest",                  # Node.js / TypeScript
    "5": "npx jest",                  # Node.js / Next.js
    "6": "npx vitest",               # React / Tauri desktop app
    "7": "mvn test",                  # Java / Spring Boot
    "8": "mvn test",                  # Java / Vert.x
    "9": None,                        # Other — filled in by /project:init
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
          {C.CYAN}https://github.com/settings/tokens{C.RESET}
          (Classic tokens — more reliable for repo creation)

  {C.BOLD}Step 2:{C.RESET} Click {C.BOLD}"Generate new token (classic)"{C.RESET}

  {C.BOLD}Step 3:{C.RESET} Fill in:
          • Note: {C.DIM}project-starter-kit{C.RESET}
          • Expiration: {C.DIM}No expiration{C.RESET} (or 1 year — your call)

  {C.BOLD}Step 4:{C.RESET} Under {C.BOLD}Select scopes{C.RESET}, tick:
          • {C.DIM}repo{C.RESET}          ← full repo access (creates repos, issues, labels)
          • {C.DIM}project{C.RESET}       ← needed for GitHub Project boards

  {C.BOLD}Step 5:{C.RESET} Click {C.BOLD}"Generate token"{C.RESET} and {C.YELLOW}copy it immediately{C.RESET}
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

    # Target directory — Tauri projects go to Windows filesystem
    projects_base = WINDOWS_PROJECTS_DIR if stack_choice == "6" else DEFAULT_PROJECTS_DIR
    default_dir = os.path.join(projects_base, project_name)
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

    # Research agent
    research_agent = ask("Does this project need a domain research agent? (y/n):").lower() == "y"

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
    if research_agent:
        print(f"  Research:    RESEARCH_AGENT.md will be generated")
    print(f"{C.CYAN}{C.BOLD}───────────────────────────────────────────{C.RESET}")

    confirm = ask("Looks good? (y/n):").lower()
    if confirm != "y":
        err("Aborted.")

    test_cmd = STACK_TEST_COMMANDS.get(stack_choice)

    return {
        "project_name": project_name,
        "desc": desc,
        "tech_stack": tech_stack,
        "test_cmd": test_cmd,
        "github_user": github_user,
        "target_dir": target_dir,
        "create_github": create_github,
        "private_repo": private_repo,
        "create_board": create_board,
        "milestone_name": milestone_name,
        "research_agent": research_agent,
        "today": datetime.date.today().isoformat(),
    }

# ── Step 1b: Create global ~/.claude/CLAUDE.md ───────────────
def create_global_claude_md():
    header("Global Claude Code settings")
    claude_dir = Path.home() / ".claude"
    claude_dir.mkdir(parents=True, exist_ok=True)
    global_md = claude_dir / "CLAUDE.md"

    if global_md.exists():
        warn("~/.claude/CLAUDE.md already exists — skipping (not overwriting)")
        return

    global_md.write_text("""\
# Global Claude Code Settings

Conventions (commit rule, Definition of Done, communication style, brief format) now live per-project in `.claude/shared-conventions.md`. That file is generated by the starter kit and committed to each repo. This global file is for overrides that truly apply to ALL projects and don't fit in the per-project file.
""", encoding="utf-8")
    ok("~/.claude/CLAUDE.md created with global settings")

# ── Step 2: Create folder structure ───────────────────────────
def create_structure(cfg):
    header("Creating project structure")
    dirs = [
        cfg["target_dir"],
        os.path.join(cfg["target_dir"], "docs"),
        os.path.join(cfg["target_dir"], ".claude"),
    ]
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)

    # commit.sh — enforced commit workflow
    commit_sh_path = os.path.join(cfg["target_dir"], "commit.sh")
    Path(commit_sh_path).write_text(
'''#!/bin/bash
# commit.sh — enforced commit workflow
# Usage: ./commit.sh "your commit message"
# Stages all tracked/new files (relies on .gitignore). Blocks commit if CHANGELOG not updated with src/ changes.

set -e

if [ -z "$1" ]; then
  echo 'Usage: ./commit.sh "commit message"' && exit 1
fi

git add -A

SRC_CHANGED=$(git diff --cached --name-only | grep "^src/" || true)
CHANGELOG_CHANGED=$(git diff --cached --name-only | grep "CHANGELOG.md" || true)

if [ -n "$SRC_CHANGED" ] && [ -z "$CHANGELOG_CHANGED" ]; then
  echo "ERROR: src/ changed but CHANGELOG.md was not updated. Update it first."
  exit 1
fi

git commit -m "$1" && git push
''', encoding="utf-8")
    import stat as stat_mod
    os.chmod(commit_sh_path, os.stat(commit_sh_path).st_mode | stat_mod.S_IEXEC | stat_mod.S_IXGRP | stat_mod.S_IXOTH)
    ok("commit.sh")
    ok(f"Folders created at {cfg['target_dir']}")

# ── Step 3: Write all .md files ───────────────────────────────
def write_file(path, content):
    Path(path).write_text(content, encoding="utf-8")
    ok(os.path.relpath(path, path.split("docs")[0].rstrip("/\\")))

def create_research_agent(cfg):
    """Write RESEARCH_AGENT.md template into the generated project (opt-in)."""
    if not cfg.get("research_agent"):
        return
    d = cfg["target_dir"]
    p = cfg["project_name"]
    header("Generating RESEARCH_AGENT.md template")
    write_file(os.path.join(d, "RESEARCH_AGENT.md"), f"""\
# Research Agent: {p}

> This file defines the research methodology for this project when Claude chat operates in research mode. It is fetched by the Claude Project instructions at session start.
>
> **Sections marked `[FILL IN]` are project-specific and must be customized per project. Everything else is standardized scaffolding from the starter kit.**

---

## [FILL IN] What this project is

One paragraph describing what the project does, who it's for, and what the data/content is. Include:
- Stack and hosting
- Primary audience
- What data is produced, where it lives (e.g., `data/positions.json`)
- Sister projects if any (same owner, related methodology)

---

## [FILL IN] The non-negotiable principle

One paragraph stating the domain-specific correctness rule that can never be violated. This is the hard constraint that distinguishes research mode from sparring mode. If it's violated, the project's credibility is damaged — possibly permanently.

State it as a single rule, then 1-2 sentences explaining why it matters and what the failure mode looks like.

---

## The workflow (standardized)

This seven-step workflow applies to every research task regardless of project. Project-specific details (sources, evaluation criteria) are elsewhere in this file; the process itself is fixed.

### 1. Discuss and understand the need

Before research begins, understand what's being asked and why. Ask:
- What's the specific question we're answering?
- What are the edges of this question — what's in scope, what's not?
- Is there a risk we're oversimplifying a nuanced topic?
- Is this a question with clear positions, or mostly rhetoric?

**Never jump straight to research.** A misunderstood question produces well-sourced but useless answers.

### 2. Research — gather from authoritative sources

Search according to the source hierarchy below (see [FILL IN] Source hierarchy). Strategy:
- Start with primary sources — the subject's own words/actions
- Cross-verify against secondary sources — what the subject actually does vs. says
- Use context sources for framing, not conclusions
- Fetch full pages (not just search snippets) — snippets usually lack the nuance needed
- Avoid the Avoid list (see [FILL IN] below) as primary sources

For each item researched, capture:
- The subject's position in their own words (short quote or close paraphrase)
- A neutral 1-2 sentence summary
- Any project-specific fields (see [FILL IN] Data schema per item)
- Source: URL + document type
- Confidence: clear / partially unclear / unclear

### 3. Fact-check — doubt everything

Every finding gets verified:
- Does the stated position match observed behavior (votes, actions, implementations)?
- Has the subject changed position recently? If so, use the latest — and note the change.
- Are there internal contradictions (individual statements diverging from official position)?
- Is this current active position or stale wording never updated?

**"Unclear" is a valid conclusion.** Never force a certainty that isn't there.

Mark unverifiable items as `unclear: true` with an explanation.

### 4. [FILL IN] Evaluate per project-specific criteria

This step varies per project. Describe what "evaluating" means here:
- If the project produces structured data (positions on a scale, ratings, categorizations), describe the scale and how placement is justified.
- If the project produces summaries, describe the evaluation criteria (completeness, neutrality, citation density).
- Give at least one worked example of an evaluation with its justification.

### 5. Structure the data

Present findings in a clear structure for review **before** anything is written to the project's data files. The specific structure depends on the project (see [FILL IN] Output format), but it must be:
- Scannable at a glance
- Organized so differences and similarities are obvious
- Complete with sources inline
- Flagged with confidence levels

### 6. Review — Niklas approves

**No data is written to the project's files without Niklas approving it first.**

Present the structured findings and ask specifically:
- Do the summaries match your understanding?
- Is the evaluation (step 4) reasonable?
- Is any nuance missing?
- Are the labels/categorizations neutral enough (if applicable)?

### 7. Produce a Claude Code brief

Once approved, produce a Claude Code brief using the standardized format from `shared-conventions.md`. The brief should be directly ingestable by Claude Code with no additional explanation.

---

## [FILL IN] Source hierarchy

Define three tiers of sources for this project:

**Primary sources (what the subject officially says/is):**
- List 3-5 source types. These are ground truth.

**Secondary sources (what the subject actually does):**
- List 3-5 source types. Used for cross-verification with primary.

**Context sources (for understanding, not conclusions):**
- List 2-3 source types. Used to frame questions, not to establish facts.

**Avoid as primary sources:**
- List source types that are common but unreliable (e.g., news articles alone, social media, biased aggregators).

Include concrete search strategies: site-specific queries, known URL patterns, tool-specific tips.

---

## [FILL IN] Output format

Describe the shape of the data being produced. Include:
- Schema per item (required fields, optional fields)
- Any validation rules
- How unclear cases are marked
- Example of one complete entry

---

## Handling hard cases (partially standardized)

Below are common edge cases. Project-specific cases go under [FILL IN] at the end.

### The subject has no clear position
Mark `unclear: true`. Summarize what exists: "No position stated in current materials. [Related document] mentions topic briefly but without concrete stance."

### The subject says one thing but does another
Default: use the stated position (official). Note the discrepancy in a comment field. Divergence between stated and actual is a separate analysis dimension, not the default one.

### The subject recently changed position
Use the latest. Note the change in the source field: "Position changed in [year] — previously [X], now [Y]."

### A question doesn't fit the project's evaluation framework
Not every question has the structure the project assumes. If forcing a fit would distort, flag it explicitly rather than producing a misleading output. Propose a reframing of the question or a split into sub-questions.

### [FILL IN] Project-specific hard cases
Add cases specific to this project's domain. Include worked examples where possible.

---

## Monitoring process (Bevakningsprocess)

This section defines scheduled monitoring. It is the basis for the Sprint 6 Routine that runs this methodology automatically.

Monitoring steps:
1. Check for new authoritative source material per [FILL IN — e.g., "per policy area", "per tracked entity"]
2. Check for updates to existing tracked items: [FILL IN — what updates? conferences, releases, legislative sessions, etc.]
3. Compile changes with:
   - What changed
   - Which item/subject it affects
   - Source
   - Recommended action: update position / monitor further / no action
4. Niklas approves before the project's data files are changed

**Frequency:** [FILL IN — weekly, monthly, per event?]

---

## Role division

| Who | Does what |
|---|---|
| Research agent (this role) | Searches sources, fact-checks, structures data, evaluates per project criteria, produces Claude Code briefs |
| Claude Code | Implements based on explicit briefs |
| Niklas | Approves findings, verifies correctness (especially the non-negotiable principle), tests, deploys, decides |

**The research agent must:**
- Never assume a position without a source
- Never invent or exaggerate
- Always mark uncertainty
- Always ask Niklas in doubtful cases
- Act as critical friend — challenge interpretations, suggest nuances
- Be transparent about methodology behind every judgment
""")

def create_plugin_settings(cfg):
    """Write .claude/settings.json declaring the project plugin."""
    d = cfg["target_dir"]
    header("Configuring plugin")
    settings_path = os.path.join(d, ".claude", "settings.json")
    Path(settings_path).write_text(json.dumps({
        "extraKnownMarketplaces": {
            "niklas-marketplace": {
                "source": {
                    "source": "github",
                    "repo": "NiklasLeide/niklas-marketplace"
                }
            }
        },
        "enabledPlugins": {
            "project@niklas-marketplace": True
        }
    }, indent=2) + "\n", encoding="utf-8")
    ok(".claude/settings.json (plugin: project@niklas-marketplace)")

def create_github_workflow(cfg):
    """Write .github/workflows/changelog-check.yml into the generated project."""
    d = cfg["target_dir"]
    header("Creating GitHub Actions workflow")
    wf_dir = os.path.join(d, ".github", "workflows")
    Path(wf_dir).mkdir(parents=True, exist_ok=True)

    write_file(os.path.join(wf_dir, "changelog-check.yml"), """\
name: CHANGELOG check

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  check-changelog:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Check for src/ changes without CHANGELOG update
        run: |
          BASE_SHA="${{ github.event.pull_request.base.sha }}"
          HEAD_SHA="${{ github.event.pull_request.head.sha }}"

          SRC_CHANGED=$(git diff --name-only "$BASE_SHA" "$HEAD_SHA" | grep "^src/" || true)
          CHANGELOG_CHANGED=$(git diff --name-only "$BASE_SHA" "$HEAD_SHA" | grep "^docs/CHANGELOG.md" || true)

          if [ -n "$SRC_CHANGED" ] && [ -z "$CHANGELOG_CHANGED" ]; then
            echo "::error::src/ changed in this PR but docs/CHANGELOG.md was not updated."
            echo "Changed src/ files:"
            echo "$SRC_CHANGED" | sed 's/^/  /'
            echo ""
            echo "Add a CHANGELOG entry describing these changes and push again."
            exit 1
          fi

          echo "CHANGELOG check passed."
""")

def create_docs(cfg):
    header("Generating documentation files")
    d = cfg["target_dir"]
    p = cfg["project_name"]
    today = cfg["today"]
    stack = cfg["tech_stack"]
    test_cmd = cfg.get("test_cmd")
    user = cfg["github_user"]
    desc = cfg["desc"]

    # Build test command line for CLAUDE.md
    if test_cmd:
        test_line = f"{test_cmd:<27}# run tests"
    else:
        test_line = "# [test command TBD — fill in via /project:init]"

    # ── CLAUDE.md ──────────────────────────────────────────────
    write_file(os.path.join(d, "CLAUDE.md"), f"""\
# {p}

{desc}

**Stack:** TBD ⚠️ — resolve this in first session
**Started:** {today}
**GitHub:** github.com/{user}/{p}

## Conventions

All conventions (commit rule, Definition of Done, communication style, brief format) live in:
@.claude/shared-conventions.md

Read that file at session start. Project-specific overrides below take precedence.

## Session Start — ALWAYS do this first
0. If Stack or Commands say TBD or unfilled — stop and resolve before anything else.
1. Read `@.claude/shared-conventions.md` — know the rules
2. Read `@docs/PROJECT_STATUS.md` — understand current state
3. Read `@docs/DECISIONS.md` — don't propose changes that contradict past decisions
4. Check `@docs/TROUBLESHOOTING.md` before proposing solutions to errors

These files ARE Claude's memory between sessions. Keep them accurate.

## Commands
```bash
# ⚠️ Run /dev command NOT YET FILLED IN — fill in via /project:init
{test_line}
./commit.sh "message"       # ALWAYS use this to commit — never bare git commit
```

## Design System (if applicable)
If this project has a UI, create a design tokens file as single source of truth
for colours, typography, spacing. All components import from it — no hardcoded
values in component files.

## Data Migration (if applicable)
If this project stores data locally, use a schema version number from day one.
Every data structure change gets a migration. Bump schema version with every migration.

## What Claude Gets Wrong on This Project
<!-- Update this as you discover patterns — highest-value section -->
- Forgets to update docs — enforced by commit.sh, but verify before committing
- Says "done" before verifying — always run tests/type-check before declaring done
- Burns tokens on planning when task is already scoped — just execute
- Creates giant files (>300 lines) — propose a split before implementing
- Drifts from visual specs over multiple sprints — use design tokens file as code
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
| 0.3 | Run DoD review for this sprint | ⬜ Todo | Use dod-reviewer sub-agent |

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

### Shell glob patterns fail on /mnt/c/ (e.g. git add *.md)
**Symptom:** `git add *.md` or similar glob commands silently do nothing or error on `/mnt/c/`.
**Cause:** Bash glob expansion behaves differently on the Windows-mounted filesystem. If no files match, the literal `*.md` is passed to git, which fails.
**Solution:** Use `git add -A` (stages everything, relies on `.gitignore`) instead of individual glob patterns. The project's `commit.sh` already does this.

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

    # ── MAINTENANCE.md ─────────────────────────────────────────
    write_file(os.path.join(d, "docs", "MAINTENANCE.md"), f"""\
# Maintenance — {p}

> Fill this in THE MOMENT you get the project running. Not later. Now.
> If you can't run the project from these instructions alone, they're not done yet.
> Run /project:resume when returning — it reads this file first.

## How to run this project

```bash
# 1. Navigate to project
cd {d}

# 2. Activate environment (if applicable)
# source ~/venv-{p}/bin/activate   ← Python venv
# nvm use 18                        ← Node version

# 3. Set up environment variables
cp .env.example .env
# Edit .env and fill in real values

# 4. Install dependencies
# pip install -r requirements.txt   ← Python
# npm install                        ← Node

# 5. Start the app
# [fill in your start command]
```

## Environment variables needed
| Variable | Where to get it | Required? |
|----------|----------------|-----------|
| `API_KEY` | [service dashboard] | Yes |

## Dependencies and versions
| Tool/Library | Version | Notes |
|-------------|---------|-------|
| Python/Node | [version] | |

## Data file locations
<!-- Where does this app store its data? -->
- _Fill in: e.g., %APPDATA%/com.myapp/data.json, ~/.config/myapp/, sqlite.db_

## Known environment quirks
<!-- Things that will bite you when setting up fresh -->
- [Fill in as you discover them]

## How to update dependencies safely
```bash
# Python:
pip list --outdated
pip install --upgrade [package]  # upgrade one at a time, test after each

# Node:
npm outdated
npm update [package]
```

## Last parked
<!-- Updated automatically by /project:parkhere -->
_Not yet parked_

---
> Update the "How to run" section the moment you figure out the setup.
> Do it while it's fresh — not when you're returning cold in 3 months.
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

# ── Step 4: Git init ──────────────────────────────────────────
def ensure_git_identity():
    """Check git user.name and user.email are set globally; prompt if not."""
    name = run("git config --global user.name", check=False).stdout.strip()
    email = run("git config --global user.email", check=False).stdout.strip()

    if not name:
        warn("Git user.name is not configured globally.")
        name = ask("Your full name for git commits:")
        if name:
            run(f'git config --global user.name "{name}"')
            ok(f"Set git user.name = {name}")
        else:
            err("Git user.name is required for commits.")

    if not email:
        warn("Git user.email is not configured globally.")
        email = ask("Your email for git commits:")
        if email:
            run(f'git config --global user.email "{email}"')
            ok(f"Set git user.email = {email}")
        else:
            err("Git user.email is required for commits.")

def init_git(cfg):
    header("Initializing git")
    ensure_git_identity()
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

    # Auto-launch VS Code
    print(f"\n  Opening {p} in VS Code...")
    run(f"code --new-window {d}", check=False)

    print(f"""
{C.BOLD}Global settings:{C.RESET}
  {C.CYAN}~/.claude/CLAUDE.md{C.RESET} — coding conventions, commit rule, Claude communication prefs
  (Applies to all projects. Project CLAUDE.md overrides where needed.)

{C.BOLD}Step 1 — Start Claude Code:{C.RESET}
  In the VS Code terminal that just opened:
  {C.CYAN}claude{C.RESET}

{C.BOLD}Step 2 — Run /project:init FIRST:{C.RESET}
  {C.CYAN}/project:init{C.RESET}
  {C.YELLOW}This is required before anything else.{C.RESET}
  It asks for your stack, run/test/dev commands, and writes them into CLAUDE.md
  and MAINTENANCE.md so every future session knows how to run your project.

{C.BOLD}Step 3 — Then start working:{C.RESET}
  {C.CYAN}/project:brief{C.RESET}
  Claude reads your docs and asks what you're building today.

{C.BOLD}Plugin:{C.RESET}
  {C.CYAN}project@niklas-marketplace{C.RESET}
  Provides: shared conventions, slash commands, sub-agents (dod-reviewer,
  code-researcher), SessionStart hook (DoD reminder)

{C.BOLD}Automation:{C.RESET}
  {C.CYAN}.github/workflows/changelog-check.yml{C.RESET}  Blocks PRs if src/ changed without CHANGELOG

{C.BOLD}GitHub:{C.RESET}
  {C.CYAN}https://github.com/{u}/{p}{C.RESET}

{C.BOLD}Claude chat counterpart (optional):{C.RESET}
  To enable the chat counterpart for this project:
  1. Create a Claude Project at {C.CYAN}claude.ai{C.RESET}
  2. Paste the contents of {C.CYAN}claude-project-starter/CLAUDE_PROJECT_INSTRUCTIONS.md{C.RESET}
  3. Set {C.CYAN}$REPO{C.RESET} to {C.CYAN}https://github.com/{u}/{p}{C.RESET}

{C.YELLOW}Tip: One feature per Claude session. /project:brief to start, /project:log to end.
Never paste file contents into Claude — use @path instead.{C.RESET}
""")

# ── Update mode ───────────────────────────────────────────────
def update_project(target_dir):
    """Re-generate slash commands and commit.sh for an existing project."""
    target_dir = os.path.expanduser(target_dir)
    if not os.path.isdir(target_dir):
        err(f"Directory not found: {target_dir}")

    claude_md = os.path.join(target_dir, "CLAUDE.md")
    if not os.path.isfile(claude_md):
        err(f"Not a starter-kit project (no CLAUDE.md): {target_dir}")

    project_name = os.path.basename(os.path.normpath(target_dir))
    print(f"\n{C.CYAN}{C.BOLD}Updating: {project_name}{C.RESET}")
    print(f"  {C.DIM}{target_dir}{C.RESET}\n")

    cfg = {
        "project_name": project_name,
        "target_dir": target_dir,
        "today": datetime.date.today().isoformat(),
    }

    # Re-generate plugin settings and GitHub workflow
    create_plugin_settings(cfg)
    create_github_workflow(cfg)

    # Re-generate commit.sh
    commit_sh_path = os.path.join(target_dir, "commit.sh")
    Path(commit_sh_path).write_text(
'''#!/bin/bash
# commit.sh — enforced commit workflow
# Usage: ./commit.sh "your commit message"
# Stages all tracked/new files (relies on .gitignore). Blocks commit if CHANGELOG not updated with src/ changes.

set -e

if [ -z "$1" ]; then
  echo 'Usage: ./commit.sh "commit message"' && exit 1
fi

git add -A

SRC_CHANGED=$(git diff --cached --name-only | grep "^src/" || true)
CHANGELOG_CHANGED=$(git diff --cached --name-only | grep "CHANGELOG.md" || true)

if [ -n "$SRC_CHANGED" ] && [ -z "$CHANGELOG_CHANGED" ]; then
  echo "ERROR: src/ changed but CHANGELOG.md was not updated. Update it first."
  exit 1
fi

git commit -m "$1" && git push
''', encoding="utf-8")
    import stat as stat_mod
    os.chmod(commit_sh_path, os.stat(commit_sh_path).st_mode | stat_mod.S_IEXEC | stat_mod.S_IXGRP | stat_mod.S_IXOTH)
    ok("commit.sh updated")

    # Update global CLAUDE.md
    create_global_claude_md()

    print(f"\n{C.GREEN}{C.BOLD}✓ {project_name} updated with latest starter kit templates.{C.RESET}")
    print(f"  {C.DIM}CLAUDE.md was NOT touched — plugin settings, workflow, and commit.sh were refreshed.{C.RESET}")

# ── Main ───────────────────────────────────────────────────────
def main():
    try:
        if len(sys.argv) >= 3 and sys.argv[1] == "--update":
            update_project(sys.argv[2])
            return
        cfg = collect_info()
        create_global_claude_md()
        create_structure(cfg)
        create_docs(cfg)
        create_research_agent(cfg)
        create_plugin_settings(cfg)
        create_github_workflow(cfg)
        init_git(cfg)
        if cfg["create_github"]:
            setup_github(cfg)
        finish(cfg)
    except KeyboardInterrupt:
        print(f"\n{C.YELLOW}Aborted.{C.RESET}")
        sys.exit(0)

if __name__ == "__main__":
    main()
