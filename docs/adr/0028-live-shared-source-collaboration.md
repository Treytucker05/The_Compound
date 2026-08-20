# Use live collaboration for shared source files

**Status:** Accepted - 2026-08-20

Trey wants a shared source file to feel like Google Docs: both Members can work in the same file at the same time and immediately see what the other person is doing. A first-editor lock would block that style of collaboration.

## Decision

- Shared source files use character-level live collaboration with one merged document buffer.
- Both Members can type at the same time and see each other's labelled caret and selection.
- The system does not impose a writer lock, handoff requirement, or last-save-wins overwrite rule for a live shared file.
- Concurrent edits merge in the shared buffer before any source-file persistence happens.
- The current Explicit Save policy remains in force for writing that merged buffer to a real Registered Project Root; autosave is a separate decision.

## Consequences

- Trey and Joe can truly work together in one source file without waiting for a lock.
- The collaboration layer needs resilient real-time merge, reconnect, offline, and recovery behavior.
- The save interaction must make it clear whose action writes the currently merged buffer to the real project file.
