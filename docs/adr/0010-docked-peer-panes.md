# Dock Reciprocal Peer Views beside each Workstation

**Status:** Accepted - 2026-08-19

Reciprocal Peer View should let Trey and Joe remain focused on their own local work while keeping the other person's selected program immediately visible. Sending both people back to a central Canvas or requiring a window-search step would make the parallel-work mode feel less natural.

## Decision

- When Reciprocal Peer View is active, each Workstation shows one dedicated, labelled Peer Pane beside its local work surface.
- Trey's Peer Pane shows Joe's selected program; Joe's Peer Pane shows Trey's selected program.
- The Peer Pane is an observation-and-annotation surface. It does not give direct input to the other Member's underlying program.
- A request to operate the remote program must explicitly switch that program into Shared Projection and its one-Driver Controlled Session.
- The Peer Pane closes when its Peer Projection ends; no loopback view of a source Member's own app is created.

## Consequences

- Both Members can work locally and still see the other person's progress without navigating away from their Workstation.
- The shared Canvas stays available for intentional planning, file, and game activity instead of becoming a required monitoring screen.
- Size, placement, and expand/collapse behavior remain interface details to validate during design work.
