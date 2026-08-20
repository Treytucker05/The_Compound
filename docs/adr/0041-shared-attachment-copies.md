# Retain deliberate attachment copies for Canvas and project work

**Status:** Accepted - 2026-08-20

Trey wants a PDF, image, video, or other standalone file added to a Projector to stay useful to both Members even when the computer it came from is no longer connected.

## Decision

- Adding a standalone file to a Canvas Board or project creates a deliberate stored Attachment copy scoped to that surface.
- The Attachment remains available to Members permitted on that Canvas Board or Shared Project when the originating Execution Host is offline.
- The copy exposes only that file; it never grants browsing access to the original folder, adjacent files, or source computer.
- Changing the original file later does not silently change the Attachment; adding a newer version is another deliberate action.
- Creating an Attachment never moves the original file or writes it into a Registered Project Root.

## Consequences

- Projector file viewing is reliable without making all collaboration depend on the source laptop staying online.
- The Compound needs durable attachment storage with the same Canvas or project membership boundary.
- Attachment retention and deletion controls remain a separate decision.
