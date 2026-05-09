"""
sync_board_to_vault.py — Bridge operational data into readable markdown.

Converts data/board.json into vault/03_SHARED/OPERATIONAL_BOARD.md
so the kanban can be viewed in Obsidian without opening the terminal.

Run manually:
    python scripts/sync_board_to_vault.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from engine.vault_sync import sync

if __name__ == "__main__":
    ok = sync()
    if ok:
        print("[SYNC] Board synced.")
    else:
        print("[SYNC] Board sync failed.")
