# Grant collaboration access when a project share is accepted

**Status:** Accepted - 2026-08-20

Trey wants an accepted project share to be immediately useful for real work, without silently granting control of another Member's programs or computer.

## Decision

- Accepting a Project Share Invitation grants the recipient Collaborator Access immediately.
- Collaborator Access lets both Members browse the shared Registered Project Root and use Live Source Collaboration for its source files.
- No second approval is needed for ordinary live source editing inside that Shared Project.
- Shared Saves remain explicit and write only to the Project Home Host.
- A terminal, browser, local-model surface, or running app is not shared merely by accepting the project; it requires a deliberate Projected App Session or Computer Session.
- Full-machine control remains separate from Collaborator Access.

## Consequences

- Project sharing is quick enough for normal pair work while keeping machine control intentional.
- The Project Desk must distinguish Collaborator Access from a Projected App Session and from a Computer Session.
- A future read-only collaborator role can be added without changing this default editing workflow.
