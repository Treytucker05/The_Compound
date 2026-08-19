# Run member workloads on their own Execution Hosts

**Status:** Accepted - 2026-08-19

Trey and Joe need to project and control programs that run on their own computers, while the always-on Windows Desktop remains responsive as the Compound coordination host. Running every program on the Windows Desktop would make one machine a performance and reliability bottleneck.

## Decision

- Each Member can attach one or more approved **Execution Hosts** to the Compound.
- An Execution Host runs that Member's program, development server, terminal, browser session, or local model where it already belongs.
- A **Compound Connector** on the Execution Host makes an outbound, authenticated connection to the Compound Hub and shares only the projects and sessions the Member explicitly chooses.
- The Compound Hub owns access decisions, collaboration state, and session signaling; it does not execute the projected program.
- A Projected App Session sends its live display and driver input between the Projector and its Execution Host over a direct authenticated route when available, avoiding the Windows Desktop as the data path for heavy session traffic.
- The Connector never grants implicit filesystem browsing or unattended arbitrary process execution.

## Consequences

- Trey can run a larger program on his laptop and project it without competing with the Windows Desktop server.
- Joe receives the same ability from his own Execution Host.
- A source Execution Host being unavailable ends only its own projected session; it does not bring down the Compound Hub.
- The initial Connector implementation must choose and validate the terminal/browser transport and the capture/control approach for existing desktop windows.
