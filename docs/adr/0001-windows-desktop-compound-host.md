# Use the Windows Desktop as the Compound coordination host

**Status:** Accepted - 2026-08-19

The Compound needs a persistent coordination service plus access to Member-owned programming environments. Version 1 uses the always-on Windows Desktop as its Compound coordination host, while Trey and Joe can attach their own Execution Hosts. This preserves one shared Compound without making the Windows Desktop the default workload machine.

## Considered options

- Use the Mac as the Compound Host.
- Treat the Windows Desktop and Mac as equal workspace hosts.
- Use the Windows Desktop as the Compound Host and connect other machines explicitly.

## Decision

- The Windows Desktop runs the Compound Hub: membership, shared state, signaling, and persistent Compound metadata.
- Member programs, development servers, terminals, and local LLM workloads run on their originating Execution Host by default.
- Each Execution Host connects through an approved Compound Connector and exposes only deliberate project roots or sessions.

## Consequences

- The ordinary Workstation remains scoped to Registered Project Roots.
- A browser session cannot itself become arbitrary full-host control; that remains a deliberate Computer Session.
- Model availability is represented through explicit LLM Connections rather than assuming all model compute runs on the Windows Desktop.
- Every Projected App Session declares its source Execution Host; the Windows Desktop does not start that Member workload.
- The Compound Hub coordinates live-app control and state but avoids relaying high-bandwidth session data whenever a direct authenticated route is available.
- If an Execution Host is offline, its projects and live sessions are unavailable without affecting the Compound Hub or the other Member's Execution Host.
