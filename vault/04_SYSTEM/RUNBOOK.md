# COMPOUND_APPROACH Runbook

## Daily Operations

### Start the Portal
1. Open `C:\COMPOUND_APPROACH`
2. Double-click `start_portal.bat`
3. In the launcher, select your profile
4. Click **Start Engine**
5. Click **Open Vault** or **Open Client** as needed

### Stop the Portal
1. In the launcher, click **Stop Engine**
2. Close the launcher window

### Add Work to the Board
**Via MUD Client:**
```
add Fix the sync script
working on Fix the sync script
done Fix the sync script -- Script now runs every 60s
```

**Via Obsidian:**
Edit `03_SHARED/OPERATIONAL_BOARD.md` directly (sync is one-way from engine to vault, so manual edits will be overwritten).

---

## Profile Switching

| Profile | Vault Folder | Use When |
|---------|--------------|----------|
| Joseph | `01_JOSEPH/` | Joseph is driving |
| Trey | `02_TREY/` | Trey is driving |
| Shared | `03_SHARED/` | Both collaborating, or neither specific |

The profile changes the accent color and status message in the launcher. It does not enforce file permissions — that is up to mutual respect.

---

## Troubleshooting

### Engine won't start
- Check if port 8765 is already in use: `netstat -ano | findstr 8765`
- Check the log in the launcher for Python errors
- Ensure `websockets` is installed: `pip install websockets`

### Vault won't open in Obsidian
- The launcher falls back to Explorer if Obsidian is not found
- Install Obsidian and the launcher will auto-detect it

### Board sync not working
- The sync script runs manually or on a timer
- Run `python scripts/sync_board_to_vault.py` to force a sync

---

## File Locations

| Purpose | Path |
|---------|------|
| Engine code | `engine/` |
| Launcher code | `launcher/` |
| Vault / notes | `vault/` |
| Runtime data | `data/` |
| Config / env | `config/` |
| Utility scripts | `scripts/` |
| Event logs | `data/logs/events.jsonl` |
| Board state | `data/board.json` |

---

*Keep this document updated as the system evolves.*
