# Automate Presence Status with an Away override

**Status:** Accepted - 2026-08-19

Manual status changes would make Clubhouse presence stale or burdensome. Fully automatic status without a way to step away would misrepresent a Member who is temporarily unavailable.

## Decision

- The Compound derives each connected Member's high-level Presence Status from their current Compound activity.
- A Member can set an explicit Away override; it temporarily replaces the automatic activity label until that Member clears it.
- Offline and unavailable status remains system-controlled when a connection is no longer active.
- Automatic and Away statuses remain coarse and never expose project, file, application, prompt, or screen details.

## Consequences

- Clubhouse presence remains useful without routine manual upkeep.
- Members retain a simple, clear way to indicate that they should not be expected to respond.
- Status changes need accessible text announcements and must not rely on animation or color alone.
