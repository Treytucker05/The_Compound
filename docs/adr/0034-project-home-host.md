# Give each project one home computer

**Status:** Accepted - 2026-08-20

Trey wants real collaborative editing without continuously copying whole project folders between computers or moving the work onto the Windows Desktop.

## Decision

- Every project has one named Project Home Host: Trey’s or Joe’s approved Execution Host.
- The Project Home Host contains the project's Registered Project Root and receives its real source-file saves.
- Both Members can open a Shared Project and work in its Live Source Collaboration buffer at the same time.
- A Shared Save from either Member writes the merged buffer to the Project Home Host only.
- That project's native apps, terminal sessions, development servers, and local models run on its Project Home Host.
- The Compound Hub coordinates the collaboration but holds neither a central working folder nor a second authoritative copy of the project.
- Version 1 does not continuously mirror a project folder to the other Member's computer.

## Consequences

- A project's owner computer is explicit, while both Members still see and edit the same live document.
- The Project Desk must label the Project Home Host so Members know where a save and a running app occur.
- If the Project Home Host Connector is unavailable, the Desk must clearly show that source-file saves and native app sessions are unavailable.
- A future deliberate clone or sync feature can be added without changing which source copy is authoritative.
