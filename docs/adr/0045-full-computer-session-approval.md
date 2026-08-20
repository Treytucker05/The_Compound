# Require owner approval for every full-computer session

**Status:** Accepted - 2026-08-20

Trey wants the convenience of whole-computer collaboration without making a project share, trusted network, or prior session into an always-on computer-control permission.

## Decision

- A Member requests a Computer Session by naming the target approved Execution Host.
- The target computer’s owner must explicitly approve every new Computer Session before any view or input begins.
- Approval applies only to that session; it creates no persistent control grant or automatic reconnect.
- An approved Computer Session follows Controlled Session rules: one Driver at a time, visible co-pilot presence, and explicit Driver Handoff.
- Private-Network Admission, Member selection, project sharing, and prior Computer Sessions never bypass the owner-approval requirement.

## Consequences

- Whole-computer access remains clear and consent-based even between Trey and Joe.
- The interface needs a prominent request and approval state that identifies the target computer.
- Project collaboration can stay lightweight without becoming remote desktop control by accident.
