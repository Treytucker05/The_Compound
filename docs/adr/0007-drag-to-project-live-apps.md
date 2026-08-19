# Make Drag to Project the primary live-app sharing gesture

**Status:** Accepted - 2026-08-19

Members should be able to share a running program naturally from their own computer without selecting hosts, copying URLs, or moving the workload onto the Windows Desktop.

## Decision

- The Compound Connector presents explicitly permitted running applications as draggable live app cards or thumbnails in a local Share Tray or overlay.
- Dropping one onto a Canvas Board or Projector Window creates a Projected App Session. The original program continues running on its originating Execution Host.
- The drop itself is the Member's deliberate opt-in to project that application; the Connector does not enumerate or project unsurfaced desktop windows.
- The browser receives an authenticated projection capability from the Connector rather than attempting to access arbitrary operating-system windows itself.

## Consequences

- Sharing a terminal, Codex-style CLI, browser, or other app feels like dragging it into the shared room.
- The Connector needs native desktop integration for the Share Tray, capture permission, and session capability handoff.
- A Projected App Session still obeys the existing single-Driver, annotation, and Driver Handoff rules.
