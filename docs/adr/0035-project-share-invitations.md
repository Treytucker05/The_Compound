# Require accepted invitations before sharing a project

**Status:** Accepted - 2026-08-20

Trey wants collaboration to feel easy without making every registered project or the rest of either Member's computer visible by default.

## Decision

- A Registered Project Root is private to its Project Owner by default.
- The Project Owner starts sharing by deliberately sending a Project Share Invitation to the other Member.
- The invitation identifies the named project and its Project Home Host before the recipient decides.
- The recipient must explicitly accept before the project becomes a Shared Project.
- Acceptance grants access only to that Registered Project Root through the Compound; it never exposes adjacent folders, other projects, or the whole host.
- Sharing a project never automatically starts an app, terminal, local model, or full-machine-control session.

## Consequences

- Each Member can understand and consent to a project-level collaboration boundary.
- The Project Desk needs clear pending, accepted, and declined invitation states.
- Later access-removal controls can be added without weakening the default private-project boundary.
