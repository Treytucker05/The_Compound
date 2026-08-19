# Use a dedicated Canvas Board with Projector Windows

**Status:** Accepted - 2026-08-19

The Compound needs a place for freeform co-creation and for talking through project material. Making every Preview into an editor would blur the boundary between a shared presentation and a canvas.

## Decision

- Version 1 includes a **Canvas Board**: a dedicated shared whiteboard in Collaborative Canvas mode with text, sticky notes, shapes, arrows, and images.
- The Canvas Board hosts movable, resizable **Projector Windows**.
- A Projector Window deliberately loads one Attachment or Preview. It chooses a compatible renderer: reading or editing for supported file types, playback for media such as video, and a clear non-editable fallback for unsupported types.
- Editing a loaded file always creates a separate shared **Projector Draft**; it never writes into the source file automatically.
- The Projector Window is extensible for additional useful renderers, but it does not silently expose a project folder or the Compound Host.

## Consequences

- A Projector Window is a canvas object, not a replacement for the underlying Workstation Files view, Stage, or Controlled Session.
- Projector Draft storage, retention, supported first file types, and any explicit publish or merge action need follow-on decisions before implementation.
- Underlying application input remains governed by the active surface's Collaboration Mode.
