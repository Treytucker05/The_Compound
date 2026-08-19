# Use a dedicated Canvas Board with Projector Windows

**Status:** Accepted - 2026-08-19

The Compound needs a place for freeform co-creation and for talking through project material. Making every Preview into an editor would blur the boundary between a shared presentation and a canvas.

## Decision

- Version 1 includes a **Canvas Board**: a dedicated shared whiteboard in Collaborative Canvas mode with text, sticky notes, shapes, arrows, and images.
- The Canvas Board hosts movable, resizable **Projector Windows**.
- A Projector Window deliberately loads one Attachment or Preview. It chooses a compatible renderer: reading or editing for supported file types, playback for media such as video, and a clear non-editable fallback for unsupported types.
- The Projector Window is extensible for additional useful renderers, but it does not silently expose a project folder or the Compound Host.

## Consequences

- A Projector Window is a canvas object, not a replacement for the underlying Workstation Files view, Stage, or Controlled Session.
- The file's initial write behavior, permission checks, and supported first file types need an explicit follow-on decision before implementation.
- Underlying application input remains governed by the active surface's Collaboration Mode.
