# Stage Lobby games after Basketball Shootout

**Status:** Accepted - 2026-08-19

Trey wants air hockey, pool, and soccer in the Compound, but requiring every game before the Lobby can be used would delay the social experience. Basketball Shootout already provides a meaningful first shared activity and a place to validate the multiplayer patterns.

## Decision

- Basketball Shootout is the only Game Table required for the initial Lobby release.
- Air hockey, pool, and soccer are sequenced after Basketball Shootout is working and validated.
- Each later game remains a separate, lightweight native Game Table and must preserve the same social and access boundaries.
- The order among air hockey, pool, and soccer is a later product-priority decision.

## Consequences

- The Lobby can become useful and fun sooner.
- Basketball validates reusable multiplayer and presence patterns before additional game work.
- Future game additions do not change the scope of the initial Lobby release.
