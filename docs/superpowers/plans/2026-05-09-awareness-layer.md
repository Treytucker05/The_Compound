# Awareness Layer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the next four awareness features for the shared Trey/Joe Compound HUD in one TDD batch.

**Architecture:** Keep the existing Python websocket/http server and single-file HUD. Add small pure helpers for radio attention, board blocked state, mission parsing, and pulse payloads, then render those payloads in the dashboard.

**Tech Stack:** Python standard library, existing `websockets` server, plain HTML/CSS/JS, `unittest`, Chrome live HUD verification.

---

### Task 1: Awareness Tests

**Files:**
- Create: `tests/test_awareness_layer.py`

- [ ] Write tests for radio attention, blocked board fields, mission parsing, and pulse payload awareness fields.
- [ ] Run `python -m unittest discover -s tests -p test_awareness_layer.py`.
- [ ] Expected: tests fail because helpers and commands do not exist yet.

### Task 2: Radio Attention

**Files:**
- Modify: `engine/radio.py`
- Modify: `engine/server.py`

- [ ] Add `thread_needs_attention`, `needs_attention_threads`, and actor-aware radio summary fields.
- [ ] Include `needs_attention_count` and `needs_attention_threads` in `/api/radio`.
- [ ] Run the awareness tests until the radio tests pass.

### Task 3: Board Active And Blocked State

**Files:**
- Modify: `engine/board.py`
- Modify: `engine/commands.py`
- Modify: `engine/server.py`
- Modify: `engine/vault_sync.py`

- [ ] Add `block_item`, `unblock_item`, `active_items`, and `blocked_items`.
- [ ] Add terminal commands `blocked <item> -- <reason>`, `blocked on <item> -- <reason>`, and `unblocked <item> -- <note>`.
- [ ] Add blocked fields to board API update handling and markdown mirror formatting.
- [ ] Run the awareness tests until board tests pass.

### Task 4: Missions

**Files:**
- Create: `engine/missions.py`
- Modify: `engine/commands.py`
- Modify: `engine/server.py`

- [ ] Parse `vault/03_SHARED/PORTAL_MISSIONS.md` current mission stack.
- [ ] Add `missions` terminal command.
- [ ] Include mission summaries in pulse payload.
- [ ] Run the awareness tests until missions tests pass.

### Task 5: HUD Rendering

**Files:**
- Modify: `engine/static/index.html`

- [ ] Add Dashboard sections for Needs Attention, My Active Items, Blocked, and Missions.
- [ ] Add a Radio tab badge for current operator needs-attention count.
- [ ] Add blocked badge/reason to board cards.
- [ ] Run `node --check` against the extracted script.

### Task 6: End-To-End Verification

**Files:**
- No new source files.

- [ ] Run `python -m unittest discover -s tests`.
- [ ] Copy changes to `D:\The_Compound`.
- [ ] Run the full Windows test suite.
- [ ] Restart the Windows server.
- [ ] Browser-check `http://100.87.143.16:8765/` in Chrome with Trey plus a Joe websocket smoke client.
- [ ] Commit and push to GitHub.
