# Let either Member save shared files and retain file revisions

**Status:** Accepted - 2026-08-20

A live shared source buffer needs a clear save action, and Trey wants the ability to undo a bad change later. File-level revision history provides a practical reversible record without copying every entire project folder on every save.

## Decision

- Either Member may invoke an Explicit Save for the current merged live source buffer.
- The shared file visibly records the most recent saver and save time.
- Every Shared Save creates a retained Revision Snapshot of that individual source file.
- Restoring a Revision Snapshot loads it into the live shared buffer; a later Explicit Save is still required before the real source file changes.
- Revision Snapshots have no automatic expiration or deletion policy in version 1; Trey and Joe will decide retention and removal later.
- Revision history is file-level only. It does not imply an automatic full-project backup or capture unregistered files.

## Consequences

- Both Members can save a merged collaborative file without waiting for an owner.
- Bad saved changes are reversible through visible history instead of fragile manual copies.
- Storage growth, history browsing, and deliberate revision removal need dedicated follow-up design decisions.
