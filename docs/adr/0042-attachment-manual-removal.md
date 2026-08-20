# Retain attachments until manually removed

**Status:** Accepted - 2026-08-20

Trey wants shared files to remain available for the work they support instead of disappearing on an automatic timer.

## Decision

- Attachments have no automatic expiration or time-based deletion in version 1.
- The Member who added an Attachment may remove that Attachment at any time.
- A Project Owner may remove any Attachment scoped to their project, including one added by the collaborator.
- An Attachment scoped only to a Canvas Board can be removed only by the Member who added it.
- Attachment Removal ends shared availability and never moves, changes, or deletes the original source file.

## Consequences

- Both Members can rely on attachments staying present until a person deliberately cleans them up.
- The interface must show an Attachment's uploader and scope before offering removal.
- Storage cleanup follows an explicit removal action rather than a silent retention timer.
