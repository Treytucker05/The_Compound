# COMPOUND_APPROACH - Trey Readme

## What To Do (Simple)

### 1) Start It
1. Open `C:\COMPOUND_APPROACH`
2. Run `start_portal.bat`
3. In launcher, select profile: **Trey**
4. Let auto-launch run (engine + HUD + vault)

### 2) Follow Onboarding
1. In the HUD (browser), enter your name
2. Follow the **Interactive Onboarding** steps
3. If onboarding does not show, click **Guide Me**

### 3) Core Commands You Need
- `board` -> See active work
- `add <task>` -> Add a task
- `working on <task>` -> Claim a task
- `done <task> -- <result>` -> Log completion
- `ask Joe <question>` -> Leave Joe a Radio Inbox question
- `inbox` -> See open questions and replies
- `reply <id> <message>` -> Reply to a Radio Inbox thread
- `resolve <id> <note>` -> Close a Radio Inbox thread
- `help` -> Full command list

### 4) Core Files To Check
- Mission context: `vault/03_SHARED/PORTAL_MISSIONS.md`
- Shared board mirror: `vault/03_SHARED/OPERATIONAL_BOARD.md`
- Decisions + feedback: `vault/03_SHARED/DECISION_LOG.md`

### 5) If Something Breaks
Run:

```powershell
cd C:\COMPOUND_APPROACH
scripts\setup.bat
start_portal.bat
```

---

## Main Connections (How It Fits Together)

- **Launcher** (`launcher/`) is control: starts services and opens tools.
- **Engine** (`engine/`) is operations: text command world + live board state.
- **HUD** (`engine/static/index.html`) is interaction: terminal left, context right.
- **Vault** (`vault/`) is memory: missions, decisions, docs.
- **Board Data** (`data/board.json`) auto-syncs to:
  - `vault/03_SHARED/OPERATIONAL_BOARD.md`

Operational loop:
`board` -> choose task -> `working on` -> ship work -> `done` -> update decisions.

---

## Project Potential (Why This Matters)

This can become a shared operating system for focused collaboration:

1. **One workspace, two operators**
- Separate profiles, shared execution surface.

2. **Fast action + persistent memory**
- Terminal speed for doing work.
- Vault structure for retaining context and decisions.

3. **Lower coordination friction**
- Shared board and command history reduce handoff confusion.

4. **Better iteration quality**
- Decisions, scores, and feedback loops make refinement concrete.

5. **Scales into a serious build environment**
- Current version already supports daily execution.
- Can evolve into a truth-grounded, AI-assisted operational environment without changing the core workflow.

---

If you only do one thing each session:
Open `board`, claim one task, finish one task, and leave the next best action clear.
