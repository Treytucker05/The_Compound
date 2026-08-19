# Make Radio available across Compound surfaces

**Status:** Accepted - 2026-08-19

Trey and Joe need to coordinate while they are naturally working in different Compound surfaces. Requiring a return to the Lobby before speaking would make the radio less useful than the real push-to-talk interaction it is meant to resemble.

## Decision

- The Compound provides one shared Radio channel across the Lobby, Canvas, Workstations, and Projector views.
- A Member may hold push-to-talk from any of those surfaces without navigating away from current work.
- Radio Floor ownership remains global: the same one-speaker rule applies everywhere.
- Radio does not automatically mute or change behavior merely because a Member is driving a shared app or viewing a Projector.

## Consequences

- Members can coordinate naturally while working separately.
- The Radio control and current-speaker state must remain consistently visible across Compound surfaces.
- Room location does not divide the voice channel in version 1.
