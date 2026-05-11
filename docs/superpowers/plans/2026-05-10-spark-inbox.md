# Spark Inbox Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a pre-board Spark Inbox so Trey and Joe can capture raw thoughts without cluttering the operational board.

**Architecture:** Store sparks in `data/sparks.json`, separate from `data/board.json`. Add terminal commands and small HTTP endpoints so the same state is available from the command chat and the board overlay. The board overlay gets two tabs: Spark Inbox and Work Board.

**Tech Stack:** Python standard library, existing WebSocket command handler, existing single-file HUD JavaScript, `unittest`.

---

### Task 1: Spark Data Model And Commands

**Files:**
- Create: `engine/sparks.py`
- Modify: `engine/commands.py`
- Test: `tests/test_spark_inbox.py`

- [ ] Write failing tests for `spark`, `sparks`, and `promote <spark> to idea`.
- [ ] Implement JSON load/save/add/promote helpers in `engine/sparks.py`.
- [ ] Wire `spark`, `sparks`, and `promote` commands into `engine/commands.py`.
- [ ] Verify promoted sparks create Ideas board cards but raw sparks stay out of `data/board.json`.

### Task 2: Spark HTTP API

**Files:**
- Modify: `engine/server.py`
- Test: `tests/test_spark_inbox.py`

- [ ] Add `/api/sparks`, `/api/sparks/add`, `/api/sparks/promote`, and `/api/sparks/delete`.
- [ ] Include open spark count in the pulse payload.
- [ ] Verify API promotion returns both updated sparks and updated board payload.

### Task 3: Board Overlay Spark Tab

**Files:**
- Modify: `engine/static/index.html`
- Test: `tests/test_visual_board.py`

- [ ] Add Board overlay tabs for Spark Inbox and Work Board.
- [ ] Add Spark form/list/promote/delete controls.
- [ ] Keep Work Board columns unchanged.
- [ ] Verify static hooks and command routing are present.

### Task 4: Remote Trey Worktree Verification

**Files:**
- Remote worktree: `D:\The_Compound_Worktrees\Trey`

- [ ] Copy changes into Trey worktree.
- [ ] Run focused Spark tests.
- [ ] Run full Windows test suite.
- [ ] Start Trey dev HUD on port `8766` and verify health/API responses.
