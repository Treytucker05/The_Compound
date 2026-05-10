# Awareness Layer Design

## Goal
Make the shared Trey/Joe workspace answer four questions immediately: who needs me, what am I doing, what is blocked, and what mission are we on?

## Scope
Build one awareness layer across the existing board, radio, dashboard, and terminal commands. Keep the server, JSON files, and single-file HUD architecture intact for this pass.

## Features
- Radio Needs Attention: open radio threads are highlighted when the latest message is from the other operator.
- My Active Items: dashboard shows planned and in-progress cards owned by the logged-in operator, plus shared planned/in-progress cards.
- Blocked State: board cards can be marked blocked or unblocked from terminal commands, with reason, actor, and timestamp.
- Missions: terminal and dashboard surface the current mission stack from `vault/03_SHARED/PORTAL_MISSIONS.md`.

## Data
Board cards may include `blocked`, `blocked_reason`, `blocked_by`, `blocked_at`, and `unblocked_note`. Radio data keeps its existing schema; attention is derived from latest message sender. Missions are parsed from markdown and not copied into a new source of truth.

## Interface
The dashboard adds sections for Needs Attention, My Active Items, Blocked, and Missions. The Radio tab displays an attention badge. Board cards display a blocked badge/reason when relevant. Terminal adds `blocked`, `unblocked`, and `missions` commands.

## Out Of Scope
No AI summaries, XP/scoring, cron, notifications, read receipts, authentication, or `index.html` split in this pass.
