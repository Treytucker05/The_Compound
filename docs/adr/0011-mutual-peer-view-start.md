# Require mutual start for a Peer View Session

**Status:** Accepted - 2026-08-19

Reciprocal Peer View exposes live program output to another Member. Trey and Joe want that sharing to be intentional without adding a disruptive approval prompt every time either Member switches which app they are sharing.

## Decision

- A Reciprocal Peer View begins only after both Members explicitly select **Start Peer View**.
- Once the Peer View Session is active, either Member may use Drag to Project to place an eligible local app in the other Member's Peer Pane.
- A new app share begins only when its source owner deliberately drags that app; activating the session does not automatically expose any program.
- No separate recipient approval is required for each app while the mutually started Peer View Session remains active.

## Consequences

- Both Members retain an explicit, shared consent boundary before any peer stream begins.
- Changing the app being shared stays quick during an active work session.
- The interface must make the session's active state and a clear end control visible to both Members.
