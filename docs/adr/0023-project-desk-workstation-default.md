# Open each Workstation as a ready Project Desk

**Status:** Accepted - 2026-08-20

Trey wants each Workstation to feel as immediately useful as Codex: project files, the real tool in use, and a way to preview or share work should be together without turning the experience into a new, disconnected chat box.

## Decision

- A Workstation opens as a ready Project Desk rather than a blank desktop or chat-first screen.
- The left side provides a clear Registered Project Root and file navigation surface.
- The center is the primary working surface for the selected real terminal, browser, or LLM tool running through the appropriate Execution Host and Connector path.
- Preview and sharing controls sit alongside the active work so a Member can intentionally show a file, demo, or Projected App Session without leaving the desk.
- The Project Desk does not invent a separate prompt-only AI UI when the Member is using an existing native LLM tool.

## Consequences

- Each Member has a consistent place to begin focused project work.
- The interface must make no-project, unavailable-host, loading, and error states clear rather than rendering only a populated desk.
- Freeform desktop arrangements can remain a later optional mode, not the default starting experience.
