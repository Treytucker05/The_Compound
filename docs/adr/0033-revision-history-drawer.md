# Keep shared revision history beside project files

**Status:** Accepted - 2026-08-20

Trey wants saved versions readily available while working on a file, rather than requiring either Member to leave the Project Desk or hunt for a separate history screen.

## Decision

- Each Project Desk has one shared Revision History Drawer beside its Files view.
- The drawer lists Revision Snapshots for the currently selected shared source file, including saver, save time, Diff Summary, and Revision Fingerprint.
- Either Member can open a listed snapshot in Revision Compare from the drawer.
- The drawer is shared: it reflects the same file-level snapshots and metadata to both Members.
- Version 1 needs no separate project-wide history screen; the drawer does not change revision retention or deletion policy.

## Consequences

- Revision recovery and verification stay close to the file Members are actively editing.
- The Files view needs a clear selected-file state so the drawer never suggests snapshots belong to a different file.
- A later retention policy can change which snapshots appear without moving the history workflow.
