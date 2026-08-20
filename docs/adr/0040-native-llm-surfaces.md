# Keep native LLM tools at the center of a Project Desk

**Status:** Accepted - 2026-08-20

Trey wants the Compound to work with the real AI tools each Member already uses, rather than duplicate them with a simplified shared prompt interface.

## Decision

- A Project Desk uses a selected Native LLM Surface from the Member's approved Execution Host.
- Native LLM Surfaces include real Codex, terminal, local-model, and browser-based AI tools.
- The Compound does not create a separate universal chat panel or prompt-only model wrapper.
- A Member intentionally shares an LLM surface through a Projected App Session, with existing Controlled Session and annotation rules.
- LLM credentials, provider settings, token use, and private conversation context remain with the source tool and its Execution Host.
- Returning to a Project Desk never starts a model or reconnects a Native LLM Surface automatically.

## Consequences

- Each Member keeps their established tool setup while the Compound provides a consistent collaboration surface.
- The Connector needs to expose selected native surfaces without collecting their credentials.
- Projected AI interaction follows the same one-Driver control boundary as other live applications.
