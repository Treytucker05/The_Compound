# Make shared AI sessions Canvas objects, not screen casts

**Status:** Accepted - 2026-08-19

The Compound needs both Members to work together with an LLM without giving either person remote control of the other's computer or exposing a private conversation by accident.

## Decision

- A Member can use **Share to Canvas** to place an LLM conversation in a Projector Window; the interaction can feel like dragging an AI card from a Workstation onto the Canvas Board.
- The result is a **Shared AI Session**, a synchronized conversation object rather than a projected desktop window.
- Both Members can immediately submit prompts. Prompts and responses are visibly attributed, so concurrent turns remain understandable.
- The LLM Connection used by the Shared AI Session is explicit and visible; no credential is exposed to the other Member.
- A private conversation's existing history and attachments are never silently included in a Shared AI Session.

## Consequences

- Shared AI collaboration works without a single Driver and without screen-share latency or pointer contention.
- The initial-history choice for sharing an existing private conversation needs an explicit follow-on decision.
