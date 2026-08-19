# Let collaboration mode follow the active surface

**Status:** Accepted - 2026-08-19

The Compound must support natural co-creation on canvas-like surfaces and reliable control when driving an existing program. A single global control rule would make one of those experiences unnecessarily frustrating.

## Decision

Every shared surface declares one explicit Collaboration Mode.

- **Collaborative Canvas** allows both Members to move, click, and type concurrently on independent canvas objects.
- **Controlled Session** gives exactly one Driver actual host input while the other Member retains a Co-Pilot Cursor and can create Annotations.

## Consequences

- A mode switch is visible to both Members and records who is Driver when applicable.
- Canvas text-edit collisions require a separately defined merge rule; this ADR does not silently pick one.
- Annotations never become underlying host input unless the active surface is explicitly switched to Collaborative Canvas.
