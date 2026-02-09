# Week 4 Assignment — Super Simple Step-by-Step Guide

You need to build **2 automations** and use them to improve the starter app. This guide assumes you know nothing.

---

## Step 0: Get the Week 4 Starter App

**If you don't have a `week4/` folder yet:**

1. Go to: https://github.com/mihail911/modern-software-dev-assignments
2. Download the repo as ZIP (green "Code" button → "Download ZIP")
3. Unzip it
4. Copy the `week4` folder into your course repo: `/Users/abhisheksinghal/course/`

**Or** if your course repo is a fork of that repo, run:

```bash
cd /Users/abhisheksinghal/course
git pull origin master
```

---

## Step 1: Run the Starter App (Do This First!)

1. Open terminal
2. Activate conda: `conda activate cs146s` (or whatever env you use)
3. Go to week4: `cd week4`
4. Run: `make run`
5. Open http://localhost:8000 in your browser
6. Open http://localhost:8000/docs for API docs

**If `make run` fails:** Install dependencies first. Check if there's a `requirements.txt` or `pyproject.toml` in week4 and run `pip install -e .` or similar.

---

## Step 2: Pick Your 2 Automations (Easiest Options)

You need **at least 2** of these. Easiest for beginners:

| Option | What it is | Difficulty |
|--------|------------|------------|
| **A) Slash command** | A custom `/command` you type in Cursor | Easy |
| **B) CLAUDE.md** | A file that tells Cursor how to behave in this project | Easy |
| **C) SubAgents** | Two AI agents working together | Harder |

**Recommended:** Do **A** (slash command) + **B** (CLAUDE.md). Skip SubAgents unless you're comfortable.

---

## Step 3: Build Automation #1 — A Slash Command

A slash command = a reusable workflow. When you type `/tests` (or whatever you name it), Cursor runs a predefined set of steps.

### 3a. Create the folder

```bash
cd /Users/abhisheksinghal/course
mkdir -p .claude/commands
```

### 3b. Create a file for your slash command

Create a file: `.claude/commands/tests.md`

**What to put in it** (copy-paste this):

```markdown
# Run tests with pytest

When the user invokes this command, do the following:

1. Run pytest on the week4 backend tests:
   ```
   cd week4 && pytest -q backend/tests --maxfail=1 -x
   ```
2. If tests pass, optionally run with coverage:
   ```
   cd week4 && pytest backend/tests --cov=backend --cov-report=term-missing
   ```
3. Summarize results: pass/fail, which tests ran, any failures.
4. If there are failures, suggest next steps (e.g., "Fix the assertion in test_xyz").
```

**How to use it:** In Cursor chat, type `/tests` and send. Cursor will follow these instructions.

---

## Step 4: Build Automation #2 — CLAUDE.md

`CLAUDE.md` is a file Cursor reads when you start a chat. It tells Cursor how to behave in this project.

### 4a. Create the file

Create a file: `/Users/abhisheksinghal/course/CLAUDE.md` (in the root of your repo)

**What to put in it** (copy-paste this, edit as needed):

```markdown
# Project Context for Claude

## Codebase structure
- `week4/` — Developer command center app (FastAPI + SQLite)
  - `backend/` — FastAPI app, routers in `backend/app/routers`
  - `frontend/` — Static UI
  - `data/` — SQLite DB + seed files
  - `docs/` — TASKS for agent-driven workflows

## How to run
- From `week4/`: `make run` (starts app on http://localhost:8000)
- Tests: `make test` (from week4)
- Format: `make format`, Lint: `make lint`

## When adding code
1. Write a failing test first (TDD)
2. Implement the feature
3. Run `make format` and `make lint` before committing
4. Use black + ruff (pre-commit is configured)
```

**How it works:** Cursor automatically reads this file when you open a chat in this project. No need to type anything special.

---

## Step 5: Document in writeup.md

Open `week4/writeup.md` and fill in the sections. The starter may already have a template.

You need to document:

1. **Design inspiration** — e.g., "I followed the assignment examples for slash commands and CLAUDE.md"
2. **Design of each automation** — What it does, inputs, outputs, steps
3. **How to run it** — Exact commands (e.g., "Type `/tests` in Cursor chat")
4. **Before vs after** — e.g., "Before: I manually ran pytest. After: I type /tests and get a summary."
5. **How you used it** (Part II) — Leave this for later, after you do Step 6

---

## Step 6: Use Your Automations (Part II)

Now actually **use** them to improve the week4 app.

**Example for the /tests command:**
- Add a new API endpoint in the week4 backend
- Use `/tests` to run tests and verify
- In writeup, write: "I used /tests to verify my new endpoint after adding it"

**Example for CLAUDE.md:**
- Ask Cursor to add a new feature (e.g., "Add a GET /status endpoint")
- Because of CLAUDE.md, Cursor will know to write a test first, then implement, then run format/lint
- In writeup, write: "CLAUDE.md guided Cursor to follow TDD when I asked for a new endpoint"

---

## Step 7: Add a Second Slash Command (Optional but Recommended)

If you want a second slash command instead of (or in addition to) CLAUDE.md:

Create `.claude/commands/docs-sync.md`:

```markdown
# Sync API docs

When invoked, do the following:

1. Read the OpenAPI spec from the running app: GET http://localhost:8000/openapi.json
   (Or read from week4 if app isn't running)
2. Compare with docs/API.md (if it exists)
3. Update docs/API.md with any new/changed routes
4. List a diff-like summary of what changed
```

---

## Checklist Before Submitting

- [ ] `week4/` folder exists and `make run` works
- [ ] At least 2 automations built (slash commands and/or CLAUDE.md)
- [ ] `writeup.md` filled out with design, how to run, before/after
- [ ] Part II: Described how you used each automation to enhance the app
- [ ] Pushed to your remote repo
- [ ] Added brentju and febielin as collaborators on your repo
- [ ] Submitted on Gradescope

---

## Quick Reference

| Task | Command |
|------|---------|
| Run app | `cd week4 && make run` |
| Run tests | `cd week4 && make test` |
| Format code | `cd week4 && make format` |
| Lint | `cd week4 && make lint` |
| Use slash command | Type `/tests` (or your command name) in Cursor chat |

---

## Troubleshooting

**"I don't have .claude/commands"**  
- Create it: `mkdir -p .claude/commands`
- Slash commands go in Cursor's Claude Code, not necessarily in all Cursor setups. If you're using **Cursor IDE**, check: Project Settings → Features → Slash commands. The `.claude/commands/` folder is for **Claude Code** (the CLI). For Cursor, you may use `.cursor/rules/` or similar. Check your course/docs for Cursor-specific setup.

**"make run fails"**  
- Ensure conda env is active
- Check `week4/Makefile` for what `make run` does
- Install deps: `pip install -r requirements.txt` or `pip install -e .`

**"Where is CLAUDE.md read?"**  
- In Claude Code / Cursor, it's typically at repo root. Cursor may use `AGENTS.md` or `.cursor/` rules instead—check your Cursor version and docs.
