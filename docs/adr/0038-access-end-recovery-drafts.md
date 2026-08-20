# Preserve unsaved buffers as local recovery drafts after access ends

**Status:** Accepted - 2026-08-20

Trey wants ending a collaboration to cut access immediately without losing unsaved work or silently turning that work into a source-file change.

## Decision

- A Project Access End takes effect immediately, even when a Shared Save State is dirty.
- Each Member who had the live buffer open keeps an Access-End Recovery Draft locally.
- A recovery draft is separate from the Project Home Host's project, source files, and Revision Snapshots.
- It cannot save, sync, or rejoin the former Shared Project after access ends.
- If the Project Owner later grants new Collaborator Access, a Member may manually copy recovery-draft content into a new live buffer; no automatic merge or source write occurs.

## Consequences

- Ending access remains immediate while unsaved work is not silently lost.
- A recovery draft cannot be mistaken for a saved revision or a route around revoked access.
- The interface needs an explicit local-recovery label and a clear unavailable Project Desk state.
- Retention and deletion rules for recovery drafts remain a later decision.
