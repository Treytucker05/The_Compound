# Offer three Basketball Shootout modes, led by HORSE

**Status:** Accepted - 2026-08-19

Basketball Shootout should feel like a game Trey and Joe can casually play together, not merely a score counter. Trey specifically wants a shared on-screen court where one person can choose a shot location and challenge the other person to match it, while retaining the simultaneous and cooperative ideas as additional ways to play.

## Decision

- Basketball Shootout offers three selectable modes: **HORSE**, **Timed Shootout**, and **Cooperative Target**.
- HORSE is the default mode. The active caller selects a visible shot position on the shared court and takes the shot; after a made shot, the other Member must attempt the same marked position under normal HORSE progression.
- Timed Shootout lets both Members score simultaneously during the same timed round; the higher score wins.
- Cooperative Target lets both Members contribute to one shared score before the round ends.
- HORSE alternates turns, while Timed Shootout and Cooperative Target permit both Members to interact at the same time.

## Consequences

- The Game Table needs a simple mode selector and a clear short explanation of each mode.
- HORSE needs shared, durable visual shot markers so both Members know exactly which position must be matched.
- The first game validates both turn-based and concurrent multiplayer patterns for later Lobby games.
