# Allow a bounded Reciprocal Peer View for parallel work

**Status:** Accepted - 2026-08-19

Trey and Joe need to work in parallel on their own computers while still seeing and annotating each other's active program. A single shared projection cannot provide that reciprocal view, but unrestricted live streams would undermine responsiveness.

## Decision

- Version 1 supports two mutually exclusive shared-projection modes: one Shared Projection, or one **Reciprocal Peer View**.
- A Shared Projection shows one program to both Members and remains a one-Driver Controlled Session.
- A Reciprocal Peer View consists of exactly two one-way **Peer Projections**: one from Trey to Joe and one from Joe to Trey. Each source program remains local to its owner and is not streamed back to that owner.
- A Peer Projection is observation and annotation only. Any direct input to the source program requires an explicit switch to a Shared Projection and its Controlled Session rules.
- Annotations and Co-Pilot Cursors synchronize to both the remote Projector view and the source Member's local overlay through the Connector.
- No additional high-bandwidth Projected App Session or live media stream may run while either mode is active. Radio, static Canvas objects, and ordinary file previews remain available.

## Consequences

- Both Members can keep working locally while seeing the other person's selected app and their annotations.
- Each Member receives one remote stream rather than both streams, avoiding unnecessary loopback and duplicate rendering.
- The interface must clearly show whether the Compound is in Shared Projection or Reciprocal Peer View mode and which app each Member is sharing.
- The two-stream Peer View budget is a version 1 performance limit and can be revisited only with measured evidence.
