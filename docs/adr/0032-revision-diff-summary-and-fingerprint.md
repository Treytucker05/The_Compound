# Show both a diff summary and exact fingerprint for revisions

**Status:** Accepted - 2026-08-20

Trey wants revision comparison to be quick for a person to understand while also allowing precise verification of the exact version being reviewed. Either signal alone would leave out a useful part of that confidence.

## Decision

- Revision Compare displays a human-readable Diff Summary of added, removed, and changed content.
- Every Revision Snapshot has a SHA-256 Revision Fingerprint calculated from its exact saved file bytes.
- The comparison and history views display the revision identity, save metadata, Diff Summary, and Revision Fingerprint together.
- The fingerprint remains associated with the snapshot even when a Member later opens it for comparison.
- A Revision Fingerprint verifies version identity only; it does not grant access, encrypt a file, or replace normal permissions.

## Consequences

- Members can quickly understand the scope of a change and verify the exact revision they selected.
- Revision history remains useful for both casual recovery and careful technical review.
- The interface needs clear labels so a fingerprint is not mistaken for a save command or a permission indicator.
