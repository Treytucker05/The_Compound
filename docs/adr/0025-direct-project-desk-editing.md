# Save Project Desk file edits directly to registered projects

**Status:** Accepted - 2026-08-20

A Member's personal Project Desk should be a usable workstation, not a read-only file browser. Trey wants text and code changes made there to become real project changes, while shared Projector edits retain their separate draft boundary.

## Decision

- The Project Desk provides direct editing for supported text and code files.
- When a Member explicitly saves, the Connector writes that file to the Member's Registered Project Root on the appropriate Execution Host.
- The editor cannot use this ability to write outside the selected Registered Project Root.
- Direct Project Desk saves are distinct from Projector Drafts; a shared Projector Draft never writes back to a source project merely because someone edited it.
- Unsupported file types continue through their appropriate viewer or approved native application path.

## Consequences

- Members can make real code and text changes without leaving their Workstation.
- Save state, write errors, host unavailability, and conflicts need clear visible recovery paths.
- Projector sharing keeps its safe separate-draft model even while personal Workstations edit source files directly.
