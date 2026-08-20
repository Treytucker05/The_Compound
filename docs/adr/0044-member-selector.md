# Let trusted devices select a Member at entry

**Status:** Accepted - 2026-08-20

Trey wants the least-friction identity experience on the already approved private network, accepting that those devices are trusted by both Members.

## Decision

- Each new Compound entry on an admitted device presents a Member Selector with Trey and Joe.
- The selected Member determines that session's presence, Project Desk restore state, and action attribution.
- Version 1 uses no device pairing, passkey, password, or additional identity challenge after network admission.
- Selecting a Member does not override existing project-sharing, Controlled Session, or Computer Session boundaries.
- The Member Selector is shown again on the next entry rather than remembered as a device identity.

## Consequences

- Entry stays quick for Trey and Joe on their trusted private-network devices.
- Any approved device can select either Member, so the selection is an asserted identity rather than strong audit proof.
- A later paired-device or passkey upgrade can strengthen identity without changing project collaboration rules.
