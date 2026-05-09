# COMPOUND_APPROACH Companion Guide

## What This Is (in one breath)

**COMPOUND_APPROACH** is a private, buildable ecosystem that blends:
- a **text-MUD style world** (Python WebSocket server) 🗺️
- an **AI "witness / steward" layer** (truth-bound memory, consent, guardrails) 🧠
- an **operator workflow** (humans + tools + agents building without hallucinated facts) 🧰

This document is the **field manual**: where files are, what runs, what rules matter, what to change first.

---

## Core Non-Negotiables (Truth + Safety)

### Truth Hierarchy
All **memory writes** and **world facts** must follow:

1) **Canon** — curated and stable (highest)
2) **Observed** — logged, time-stamped, reproducible
3) **Hypothesis** — explicitly uncertain; expires or requires promotion

**Rule:** if something is uncertain, it must be labeled as Hypothesis (never smuggled into Canon).

### Consent & Privacy Boundaries (Ambient Witness)
Any "ambient" or "presence-aware" logging must remain **consent-first** and bounded to what's explicitly allowed.

> Rule of thumb: if a feature *could* become surveillance, it must be redesigned or gated.

---

## What Already Exists Right Now

### Active System
| Component | File | Status |
|-----------|------|--------|
| WebSocket MUD Server | `engine/server.py` | ✅ Running |
| Filesystem World Engine | `engine/world.py` | ✅ Active |
| Command Parser | `engine/commands.py` | ✅ Active |
| Kanban Board | `engine/board.py` | ✅ Active |
| Browser Client | `engine/static/index.html` | ✅ Active |
| AI Backend Seam | `engine/ai_stub.py` | ✅ Stub ready |
| Python Launcher | `launcher/app.py` | ✅ Active |
| Obsidian Vault | `vault/` | ✅ Ready |

### Two Tracks (avoid confusion)

**Track A — Web App (LifeOps/ThinkOps)**
- Purpose: personal OS + logging + synthesis + workflows
- Status: **Documented only**, not in this codebase
- Risk: agents mixing these assumptions into the MUD codebase

**Track B — WebSocket MUD (World Engine)**
- Purpose: deterministic world simulation + command loop + shared workspace
- Status: **Running now** in `engine/`
- Risk: agents inventing "API endpoints" or web stack components that do not exist

**Operator rule:** always state which track you're working on before making changes.

---

## Quick Start (Human Operator)

1) Double-click `start_portal.bat`
2) Click **Start Engine** in the launcher
3) Click **Open Client** to open the browser terminal
4) Type `board` to see the operational board
5) Type `look` to explore the filesystem
6) Type `help` for all commands

---

## Where AI Hooks In (Clean Seam)

### NPC "Brain" attachment
Design intent (keep this pure):
- **Engine = deterministic world rules**
- **AI = suggests actions** based on state
- **Truth policy = gates what becomes memory/lore**

### Recommended control policy
1) **Hard rules first** (safety + invariants)
2) **Scripted behaviors second** (fast, reliable)
3) **LLM last** (creative fill, strict constraints, *never writes Canon directly*)

---

## Persistence & State

### What gets saved
- Player: location, inventory
- World: flags, door states, quest states
- NPCs: state + relationships + key memory pointers (not raw lore injection)

### "Truth write" separation
- **World state updates:** OK (game simulation)
- **Lore / memory writes:** must obey Canon/Observed/Hypothesis policy

**Practical guardrail:** write game-state to save files freely; write lore to an auditable "memory gate" log that enforces the hierarchy.

---

## Operating Rules for Agents

### "No guessing" standard
Agents must not:
- invent files, paths, endpoints, keys, or credentials
- write "facts" into memory without evidence
- broaden scope without explicit instruction

### Preferred change style
- small commits / small diffs
- verify runtime after changes
- keep compatibility with the engine while refactoring

### Stop conditions (agent must pause and report)
- unclear source of truth
- contradictions between policy and code behavior
- uncertain file ownership / scope boundary

---

## Practical Build Roadmap (Short)

### Phase 1 — Stabilize the skeleton ✅
- Normalize imports and module layout (engine/launcher/vault)
- Add minimal test harness: "boot launcher → start engine → connect → look → quit"
- Confirm save/load cycle works

### Phase 2 — AI NPC v0 🤝
- Implement a **brain adapter interface**
- Add a single NPC with:
  - scripted baseline behavior
  - optional LLM-driven emotes/actions behind strict rules

### Phase 3 — Truth-bound memory 🧾
- Add a **memory write gate** that enforces policy tiers
- Add an **audit log**: what wrote, why, evidence pointer, timestamp

---

## Glossary

- **Canon:** curated truths; stable lore or rules
- **Observed:** logged facts from runtime, sensors, or explicit input
- **Hypothesis:** uncertain; must be marked and time-limited
- **Witness:** records what happened (not a storyteller)
- **Steward:** protects integrity + boundaries (not a hype engine)
- **Seam:** narrow interface where AI suggests actions

---

*End of field manual.*
