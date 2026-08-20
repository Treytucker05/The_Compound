# Let either Member end a project share

**Status:** Accepted - 2026-08-20

Trey wants a collaboration boundary either Member can leave, while keeping the Project Owner in control of their own project and retaining saved work safely.

## Decision

- A Project Owner may revoke Collaborator Access at any time.
- A collaborator may leave a Shared Project at any time.
- Either action causes a Project Access End immediately for future file browsing, live editing, and source-file saves by that collaborator.
- After the access end, the project is again a Personal Project unless the Project Owner shares it again through a new accepted invitation.
- A Project Access End never deletes the Project Home Host's source files, Revision Snapshots, or existing saved history.
- An open Project Desk transitions to a clear access-ended state; handling an unsaved shared buffer is decided separately.

## Consequences

- Neither Member is trapped in a collaboration relationship they no longer want.
- The interface needs a clear revoke action for the owner and leave action for the collaborator.
- The next safety decision is how an unsaved live shared buffer behaves when access ends.
