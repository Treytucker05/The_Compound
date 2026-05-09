# COMPOUND_APPROACH — The Portal

A profile-aware collaboration portal for Joseph Harris and Trey. This laptop becomes a dedicated bridge: your accounts stay yours, the space between is where you build.

## Quick Start

1. **First time only:** Run `scripts\setup.bat` to install dependencies
2. **Every time:** Double-click `start_portal.bat`
3. Select a profile (Joseph / Trey / Shared)
4. Click **Start Engine**
5. Click **Open Vault** or **Open Client**

## Architecture

```
COMPOUND_APPROACH/
├── launcher/     # Python GUI control panel
├── engine/       # WebSocket MUD world engine
├── vault/        # Obsidian vault (shared knowledge)
├── data/         # Runtime state (board, notes, logs)
├── config/       # Environment configuration
└── scripts/      # Utilities
```

## Layers

| Layer | Tool | Purpose |
|-------|------|---------|
| **Control** | Python Launcher | Start/stop services, switch profiles |
| **Knowledge** | Obsidian Vault | Long-form notes, decisions, docs |
| **Operations** | MUD Engine | Live kanban, filesystem nav, chat |

## Truth Hierarchy

1. **Canon** — Curated and stable (highest)
2. **Observed** — Logged, time-stamped, reproducible
3. **Hypothesis** — Explicitly uncertain; expires

## Key Documents

- [Portal Manifesto](vault/04_SYSTEM/PORTAL_MANIFESTO.md) — The vision
- [Companion Guide](vault/04_SYSTEM/COMPANION_GUIDE.md) — Field manual for agents
- [Build Roadmap](vault/04_SYSTEM/BUILD_ROADMAP.md) — Future phases
- [Runbook](vault/04_SYSTEM/RUNBOOK.md) — Daily operations

## License

Private. For Joseph Harris and Trey only.
