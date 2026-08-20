# Admit only approved private-network devices

**Status:** Accepted - 2026-08-20

Trey wants frictionless entry from the computers he and Joe already trust without turning ordinary Wi-Fi or a public address into a way into The Compound.

## Decision

- The Compound Hub accepts network connections only from devices approved on the private network.
- An approved private-network device may reach the Compound without a separate per-device Compound invitation.
- Presence on an ordinary local Wi-Fi or Ethernet network alone is not enough for entry.
- The Compound exposes no public-network entry path in version 1.
- Private-Network Admission is a transport boundary only; it does not identify a Member or grant project, application, or full-machine access.

## Consequences

- Trey and Joe can use their already trusted private-network devices with little friction.
- Removing a device from the private network removes its ability to reach the Compound.
- The next identity decision determines how an admitted device is associated with Trey or Joe.
