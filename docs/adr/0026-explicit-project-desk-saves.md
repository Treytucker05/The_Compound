# Require explicit saves for Project Desk source edits

**Status:** Accepted - 2026-08-20

Project Desk editing writes to real source folders. Autosave could persist an unfinished or accidental change before a Member intends it, while a normal explicit save matches how source editing is expected to work.

## Decision

- A Project Desk Editor writes a source file only after the Member explicitly saves, including through the normal keyboard shortcut.
- Unsaved changes show a clear dirty indicator.
- Unsaved editor content is kept in a recoverable local buffer after interruption or restart but is not written to the source file until a later explicit save.
- Closing, switching, or leaving with unsaved work presents a clear save, discard, or stay choice.

## Consequences

- Members retain deliberate control over real project writes.
- Recovery protects work from interruptions without turning into silent autosave.
- Save failures must preserve the editor buffer and offer an understandable retry path.
