# Limit version 1 to one Active Projection

**Status:** Superseded - 2026-08-19

**Superseded by:** [ADR-0009](0009-reciprocal-peer-view.md)

The Compound must feel responsive while the Windows Desktop remains a lightweight coordination host. Simultaneously streaming several live applications or media sources creates avoidable bandwidth, encoding, and interaction lag.

## Decision

- Version 1 allows exactly one **Active Projection** in The Compound at a time.
- An Active Projection is a high-bandwidth Projected App Session or live audio/video media playback. Radio is separate and remains available.
- Starting a second heavy projection requires explicitly switching, parking, or closing the current Active Projection.
- Programs not currently projected stay on their originating Execution Host and continue to be used there locally.
- Static Canvas objects, annotations, and ordinary file previews do not consume the Active Projection slot.

## Consequences

- The Projector protects low-latency collaboration instead of attempting to show every running program at once.
- Each Member can keep multiple tools open on their own computer without loading the Compound Hub or the shared Canvas.
- The user interface must make the active slot and any switch action obvious to both Members.
- The single-projection limit is a version 1 capacity decision and can be revisited with measured performance evidence.
