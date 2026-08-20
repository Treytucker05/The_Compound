# Require explicit saves for live shared source collaboration

**Status:** Accepted - 2026-08-20

Google-Docs-style live editing makes collaboration immediate, but Trey wants deliberate control over when the merged work changes a real source file in a Registered Project Root.

## Decision

- Both Members see and edit one live merged source buffer in real time.
- Live typing and merge operations never automatically write the underlying source file.
- The file's shared dirty state is visible to both Members.
- A deliberate Explicit Save is required before the merged buffer persists to the registered source file.

## Consequences

- Collaboration feels live without silently changing a real project folder.
- Save, write failure, reconnect, and recovery states need to be visible to both Members.
- Save authority for a live shared file remains a separate product decision.
