# Putting the Starter Kit on GitHub

One-time setup. After this, improving the kit = edit → commit → push. That's it.

---

## Step 1 — Move the kit to a permanent home on WSL2

The zip was downloaded on Windows, so it lives on the Windows filesystem — not WSL2. You need to copy it across using the `/mnt/c/` path.

```bash
mkdir -p ~/tools

# Your Windows Downloads folder is visible from WSL2 at /mnt/c/Users/nikla/Downloads/
cp -r /mnt/c/Users/nikla/Downloads/project-starter-v2 ~/tools/claude-project-starter
```

> If that fails, check the exact folder name first:
> ```bash
> ls /mnt/c/Users/nikla/Downloads/ | grep project
> ```

```bash
cd ~/tools/claude-project-starter
```

> **Why `~/tools/` and not just leaving it in Downloads?**
> The Windows filesystem at `/mnt/c/` doesn't support Linux permissions, symlinks, or git properly.
> Always work on native WSL2 filesystem (`~/`) — this is the same issue documented in TROUBLESHOOTING.md.

---

## Step 2 — Initialize git

```bash
cd ~/tools/claude-project-starter
git init
git add .
git commit -m "chore: initial commit — project starter kit v2"
```

---

## Step 3 — Create the GitHub repo

```bash
gh repo create niklasleide/claude-project-starter \
  --private \
  --description "Personal project bootstrapper — Claude Code, GitHub, all .mds" \
  --source=. \
  --remote=origin \
  --push
```

> If you don't have `gh` installed: `sudo apt install gh` then `gh auth login`

Done. Your kit is now at: **github.com/niklasleide/claude-project-starter**

---

## Step 4 — Add the global alias so you can run it from anywhere

```bash
echo 'alias newproject="python3 ~/tools/claude-project-starter/new_project.py"' >> ~/.bashrc
source ~/.bashrc
```

Test it:
```bash
newproject
```

---

## Step 5 — Install the requests dependency (if not done yet)

```bash
pip install requests
```

---

## Workflow for improving the kit over time

Every time you finish a project and think *"I wish the starter had done X"* — update it here:

```bash
cd ~/tools/claude-project-starter

# Make your changes to new_project.py or README.md

git add .
git commit -m "improvement: [what you changed and why]"
git push
```

Good commit messages to use:
```
improvement: add Python venv auto-creation to structure step
fix: GitHub board creation was failing for private repos
template: add FastAPI-specific troubleshooting entries
lesson: add new WSL2 issue from [project name]
```

---

## What's worth improving after each project

After finishing or abandoning a project, ask yourself:

| Question | File to update |
|----------|---------------|
| Did Claude keep making the same mistake? | `new_project.py` → CLAUDE.md template, "What Claude Gets Wrong" section |
| Did I hit a WSL2/env issue not in the template? | `new_project.py` → TROUBLESHOOTING.md template |
| Did I make a stack decision I'll make again? | `new_project.py` → STACK_PRESETS or DECISIONS.md template |
| Was a slash command missing or wrong? | `new_project.py` → the relevant command in `create_commands()` |
| Was the GitHub setup wrong or missing something? | `new_project.py` → `setup_github()` or `GITHUB_LABELS` |

---

## Final structure on your machine

```
~/tools/claude-project-starter/     ← the kit itself, on GitHub
    new_project.py
    README.md
    SETUP_GUIDE.md                ← this file

~/projects/                       ← where new projects get created
    my-first-project/
    my-second-project/
    ...
```

Run `newproject` from anywhere → new project appears in `~/projects/`.
