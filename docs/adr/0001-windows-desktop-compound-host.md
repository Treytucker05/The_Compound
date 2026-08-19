# Use the Windows Desktop as the Compound Host

**Status:** Accepted - 2026-08-19

The Compound needs persistent Workstations, project access, terminals, previews, and a deliberately available Computer Session. Version 1 will use the always-on Windows Desktop as its single Compound Host, while connecting to external model hosts through explicit LLM Connections. This gives Trey and Joe the same live work environment without turning each browser or laptop into a competing workspace host.

## Considered options

- Use the Mac as the Compound Host.
- Treat the Windows Desktop and Mac as equal workspace hosts.
- Use the Windows Desktop as the Compound Host and connect other machines explicitly.

## Consequences

- The ordinary Workstation remains scoped to Registered Project Roots.
- A browser session cannot itself become arbitrary full-host control; that remains a deliberate Computer Session.
- Model availability is represented through explicit LLM Connections rather than assuming all model compute runs on the Windows Desktop.
