# Compare revisions before manually restoring changes

**Status:** Accepted - 2026-08-20

Trey wants to be able to recover from a bad saved change without accidentally replacing good current work. A visible comparison gives both Members confidence and lets them bring back only the parts they actually want.

## Decision

- Selecting a Revision Snapshot opens a Revision Compare rather than immediately restoring it.
- Revision Compare shows the snapshot and current live shared file side by side with changed lines highlighted.
- Members manually copy the desired prior changes into the live shared buffer.
- Opening or viewing a revision never changes the live buffer or the real source file.
- Any resulting restored work still follows normal live collaboration and Explicit Save rules.

## Consequences

- Revision recovery is deliberate, inspectable, and reversible.
- Members can preserve current good work while bringing back only selected older changes.
- The comparison surface needs a clear current-versus-revision label and safe copy interactions.
