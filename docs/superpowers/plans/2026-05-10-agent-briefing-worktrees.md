# Agent Briefing Worktrees Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an in-HUD and repo-level Agent Briefing that tells Trey/Joe agents which worktree, branch, port, push, merge, and conflict workflow to use.

**Architecture:** Add a small pure Python `engine/agent_briefing.py` module that owns profile-specific briefing data and renders prompt/markdown text. `engine/server.py` exposes the data through `/api/agent-briefing`; `engine/static/index.html` renders it after login and from a persistent button. Scripts start side dev servers on 8766/8767 while live 8765 stays running.

**Tech Stack:** Python stdlib, existing websockets server HTTP hook, single-file HTML/JS HUD, Windows PowerShell/CMD launch scripts, unittest.

---

### Task 1: Agent Briefing Data

**Files:**
- Create: `engine/agent_briefing.py`
- Test: `tests/test_agent_briefing.py`

- [ ] **Step 1: Write failing tests**
  - Test `briefing_for_actor("Trey")` returns path `D:\The_Compound_Worktrees\Trey`, branch `trey/workspace`, dev port `8766`, live port `8765`, and prompt text containing `git push`.
  - Test `briefing_for_actor("Joe")` returns path `D:\The_Compound_Worktrees\Joe`, branch `joe/workspace`, and dev port `8767`.

- [ ] **Step 2: Verify RED**
  - Run `python -m unittest tests.test_agent_briefing`.
  - Expected: import failure for missing `agent_briefing`.

- [ ] **Step 3: Implement minimal module**
  - Add profile config, prompt rendering, and markdown rendering.

- [ ] **Step 4: Verify GREEN**
  - Run `python -m unittest tests.test_agent_briefing`.
  - Expected: tests pass.

### Task 2: Server Endpoint And HUD

**Files:**
- Modify: `engine/server.py`
- Modify: `engine/static/index.html`
- Test: `tests/test_agent_briefing.py`

- [ ] **Step 1: Write failing tests**
  - Test `server.agent_briefing_payload("Trey")` exposes the Trey briefing.
  - Test HUD contains `data-testid="agent-brief-button"`, `data-testid="agent-brief-overlay"`, and `/api/agent-briefing`.

- [ ] **Step 2: Verify RED**
  - Run `python -m unittest tests.test_agent_briefing`.

- [ ] **Step 3: Implement endpoint and UI**
  - Add `/api/agent-briefing`.
  - Add top button, overlay, copy button, and login-time display.

- [ ] **Step 4: Verify GREEN**
  - Run `python -m unittest tests.test_agent_briefing`.

### Task 3: Docs And Dev Scripts

**Files:**
- Create: `AGENTS.md`
- Create: `vault/03_SHARED/AGENT_BRIEFING.md`
- Create: `scripts/Start-WorktreeDev.ps1`
- Create: `Start_Trey_Dev_Compound.cmd`
- Create: `Start_Joe_Dev_Compound.cmd`
- Test: `tests/test_agent_briefing.py`

- [ ] **Step 1: Write failing tests**
  - Test docs include the worktree paths and merge/conflict rules.
  - Test dev scripts use ports `8766` and `8767`, not `8765`.

- [ ] **Step 2: Verify RED**
  - Run `python -m unittest tests.test_agent_briefing`.

- [ ] **Step 3: Add docs and scripts**
  - Write copyable agent instructions.
  - Add script wrappers for Trey/Joe side servers.

- [ ] **Step 4: Verify full suite**
  - Run `python -m unittest discover -s tests`.
  - Start Trey dev server on 8766 while live 8765 remains separate.
