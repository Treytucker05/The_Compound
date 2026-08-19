# Treat an occupied Radio Floor as busy, not queued

**Status:** Accepted - 2026-08-19

The Compound's Radio is meant to feel like a shared push-to-talk channel. When one Member is already speaking, automatically queueing or interrupting the other person's voice would create accidental audio and make the floor harder to understand.

## Decision

- The first Member holding push-to-talk receives the Radio Floor.
- If the other Member presses push-to-talk while that floor is occupied, the interface displays that the current speaker is talking and sends no audio.
- The attempted transmission is not queued and cannot interrupt the active speaker.
- After the speaker releases push-to-talk, the other Member must press again to transmit.

## Consequences

- Radio behavior is predictable and matches a real two-way radio.
- There is no delayed or accidentally transmitted speech.
- The interface needs a clear busy indicator for both Members.
