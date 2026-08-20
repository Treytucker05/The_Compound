# Give the first editor a visible lock on a shared source file

**Status:** Superseded - 2026-08-20

**Superseded by:** [ADR-0028](0028-live-shared-source-collaboration.md)

Real source files require a stronger protection against overwritten work than a shared Canvas note. Trey wants first-editor priority while preserving the other person's ability to follow along and communicate about the file.

## Decision

- The first Member who begins editing a source file in a shared project receives a visible Source Edit Lock.
- The lock holder may edit and explicitly save that source file.
- The other Member may read the file, add non-destructive annotations, and request an editor handoff, but cannot write the source file while the lock is held.
- The current lock holder releases the lock or accepts a handoff request before the other Member becomes the editor.
- The system does not use simultaneous live source editing or last-save-wins behavior for a locked shared source file.

## Consequences

- Real shared files avoid accidental overwrite and merge confusion.
- Both Members retain shared awareness and a clear collaboration path rather than a silent read-only failure.
- The interface needs clear lock ownership, handoff, unavailable-owner, and recovery states.
