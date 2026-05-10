# Agent Briefing Worktrees Design

## Goal
Give Trey and Joe an obvious, copyable agent briefing inside The Compound so coding agents know which worktree to use, how to push, how to merge, and how to keep the live shared server running separately.

## Design
The repo gets a root `AGENTS.md` for coding agents and a vault mirror at `vault/03_SHARED/AGENT_BRIEFING.md` for humans inside the HUD. The backend exposes one profile-aware briefing payload at `/api/agent-briefing?actor=Trey|Joe`. The HUD shows an Agent Briefing overlay after login and keeps an `Agent Brief` button available in the top bar.

The live app remains `D:\The_Compound` on port `8765`. Trey development runs from `D:\The_Compound_Worktrees\Trey` on port `8766`; Joe development runs from `D:\The_Compound_Worktrees\Joe` on port `8767`. Worktree dev scripts set `MUD_PORT` before running `engine/server.py`, so a side HUD can run while the real shared Compound stays open.

## Acceptance
- Trey briefing names `D:\The_Compound_Worktrees\Trey`, `trey/workspace`, and port `8766`.
- Joe briefing names `D:\The_Compound_Worktrees\Joe`, `joe/workspace`, and port `8767`.
- HUD contains an Agent Brief button and overlay with copyable prompt text.
- Scripts exist for starting Trey/Joe dev servers without touching port `8765`.
- Tests prove the payload, docs, scripts, and HUD hooks exist.
