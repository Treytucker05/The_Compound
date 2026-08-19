# Let collaboration mode follow the active surface

**Status:** Accepted - 2026-08-19

The Compound must support natural co-creation on canvas-like surfaces and reliable control when driving an existing program. A single global control rule would make one of those experiences unnecessarily frustrating.

## Decision

Every shared surface declares one explicit Collaboration Mode.

- **Collaborative Canvas** allows both Members to move, click, and type concurrently on independent canvas objects.
- **Controlled Session** gives exactly one Driver actual host input while the other Member retains a Co-Pilot Cursor and can create Annotations.
- A non-Driver requests a Driver Handoff. The current Driver approves or releases that request before host input changes hands.
- When both Members edit the same canvas text object, their input is merged so both Members' text remains present. The first Member to focus that object becomes the Primary Editor and receives deterministic ordering priority for a collision.

## Consequences

- A mode switch is visible to both Members and records who is Driver when applicable.
- The active Driver, a pending handoff request, and a completed transfer remain visible to both Members.
- Text editing needs a real-time merge mechanism with visible Member carets; it must preserve both inputs and apply the Primary Editor rule only when concurrent edits conflict.
- Annotations never become underlying host input unless the active surface is explicitly switched to Collaborative Canvas.
