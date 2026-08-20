# Keep a project unavailable while its home host is offline

**Status:** Accepted - 2026-08-20

Trey wants project state to stay truthful when its real source folder and apps are unreachable, rather than offering stale files or creating a later sync conflict.

## Decision

- When a Project Home Host Connector cannot be reached, its Project Desk enters the Project Home Host Offline State.
- The offline Project Desk shows no cached project file contents and permits no project browsing or editing.
- It cannot start Live Source Collaboration, make a Shared Save, or open that project's native app, terminal, or local-model surface.
- Version 1 does not create an offline clone or queue source-file changes for later synchronization.
- Existing Access-End Recovery Drafts remain local recovery material and never make the former project appear available.

## Consequences

- Members never mistake a stale cache or offline draft for the current project source.
- Reconnection restores normal project access only after the Project Home Host Connector is available again.
- A later explicitly designed offline-copy feature can be added without changing source-file authority.
