# Restore each Member's last Project Desk

**Status:** Accepted - 2026-08-20

A Project Desk should feel like a personal workstation instead of making a Member repeatedly navigate back to the same project. Restoration must not cross the boundary into silently launching work or reconnecting a computer without an intentional approved connection.

## Decision

- On return, a Workstation restores that Member's most recently selected Registered Project Root and Project Desk arrangement.
- Project selection and layout restore independently for Trey and Joe.
- Restore never starts a program, terminal, local model, development server, or Connector connection.
- If the prior project or Execution Host is unavailable, the Desk shows a clear unavailable state and a path to choose another project or reconnect intentionally.

## Consequences

- Members resume focused work with less navigation.
- Restoration is safe for local resource usage and remains honest about unavailable tools.
- The project picker remains directly available instead of trapping a Member in the last project.
