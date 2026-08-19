# Use a dedicated Canvas Board with Projector Windows

**Status:** Accepted - 2026-08-19

The Compound needs a place for freeform co-creation and for talking through project material. Making every Preview into an editor would blur the boundary between a shared presentation and a canvas.

## Decision

- Version 1 includes a **Canvas Board**: a dedicated shared whiteboard in Collaborative Canvas mode with text, sticky notes, shapes, arrows, and images.
- The Canvas Board hosts movable, resizable **Projector Windows**.
- A Projector Window deliberately loads one Attachment or Preview. It chooses a compatible renderer: reading or editing for supported file types, playback for media such as video, and a clear non-editable fallback for unsupported types.
- Editing a loaded file always creates a separate shared **Projector Draft**; it never writes into the source file automatically.
- Projector Drafts are persistent shared artifacts in a **Projector Drafts Shelf** linked to their Canvas Board and source context.
- The version 1 Projector Renderer set edits code, text, and Markdown; views PDFs and images; plays audio and video; presents live local web demos; and supports Projected App Sessions.
- The Projector Window is extensible for additional useful renderers, but it does not silently expose a project folder or the Compound Host.

## Consequences

- A Projector Window is a canvas object, not a replacement for the underlying Workstation Files view, Stage, or Controlled Session.
- Projector Draft lifecycle, including any explicit publish, merge, archive, or removal workflow, needs a follow-on decision before implementation.
- Native editing of Word, Excel, and PowerPoint files is out of version 1 scope; future Projector Renderers can add it deliberately.
- Underlying application input remains governed by the active surface's Collaboration Mode.
