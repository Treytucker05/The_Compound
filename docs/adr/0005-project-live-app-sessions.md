# Project live app sessions instead of replacing them with chat

**Status:** Accepted - 2026-08-19

For the Compound to feel like a real shared workstation, a Member must be able to put an actual terminal, browser, or LLM application into a Projector Window and work in that same running application together. A copied chat abstraction is not the default collaboration surface.

## Decision

- Dragging an app card or window into the Canvas Board creates a **Projected App Session** in a Projector Window.
- The Projector presents the live application and passes the active Driver's clicks and keystrokes to that actual application.
- A Projected App Session is always a Controlled Session: it has one Driver at a time, a visible Co-Pilot Cursor, Annotations, and Driver Handoff requests.
- A terminal, Codex-style CLI, browser-based LLM, or other tool keeps its native interface; the Projector does not replace it with separate prompt boxes.
- A private LLM conversation remains private until its owner deliberately projects it; the detailed history-selection flow remains a separate decision.

## Consequences

- Two Members can see and take turns operating the exact same running program.
- Canvas Boards retain true concurrent interaction for native canvas objects; this exception is necessary because terminal and application input are single live streams.
- Version 1 must choose whether to prioritize Compound-owned terminal/browser sessions or capture and control of arbitrary already-running desktop windows.
- A specialized Shared AI Session can be reconsidered later as an optional renderer, but it is not the primary workstation collaboration model.
