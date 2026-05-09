"""
vault_sync.py — Bridge operational board data into readable markdown.

Auto-called after board mutations. Can also be run manually via:
    python scripts/sync_board_to_vault.py
"""

import json
from datetime import datetime, timezone
from pathlib import Path


def sync(root: Path = None) -> bool:
    """Convert data/board.json into vault/03_SHARED/OPERATIONAL_BOARD.md."""
    if root is None:
        root = Path(__file__).parent.parent

    board_path = root / "data" / "board.json"
    vault_path = root / "vault" / "03_SHARED" / "OPERATIONAL_BOARD.md"

    if not board_path.exists():
        return False

    try:
        with open(board_path, "r", encoding="utf-8") as f:
            board = json.load(f)
    except (json.JSONDecodeError, IOError):
        return False

    now = datetime.now(timezone.utc).isoformat()

    def items_list(column: str) -> list[str]:
        items = board.get("columns", {}).get(column, [])
        if not items:
            return ["*(empty)*"]
        lines = []
        for item in items:
            parts = [item.get("title", "untitled")]
            if item.get("owner"):
                parts.append(f"({item['owner']})")
            if item.get("mode"):
                parts.append(f"[{item['mode']}]")
            if item.get("priority"):
                parts.append("[PRIORITY]")
            lines.append("- " + " ".join(parts))
        return lines

    def done_items() -> list[str]:
        items = board.get("columns", {}).get("done", [])
        if not items:
            return ["*(empty)*"]
        lines = []
        for item in items[-5:]:
            parts = [item.get("title", "untitled")]
            if item.get("completed_by"):
                parts.append(f"(by {item['completed_by']})")
            if item.get("completion_note"):
                parts.append(f"— {item['completion_note']}")
            lines.append("- " + " ".join(parts))
        return lines

    def next_best() -> str:
        in_prog = board.get("columns", {}).get("in_progress", [])
        if in_prog:
            item = in_prog[0]
            return f"- {item.get('title', 'untitled')} ({item.get('owner', 'unowned')})"
        ready = (
            board.get("columns", {}).get("planned", []) +
            board.get("columns", {}).get("refined", []) +
            board.get("columns", {}).get("raw", [])
        )
        priority = [i for i in ready if i.get("priority")]
        if priority:
            return f"- {priority[0].get('title', 'untitled')} [PRIORITY]"
        if ready:
            return f"- {ready[0].get('title', 'untitled')}"
        return "*(none)*"

    def recent_news() -> list[str]:
        news = board.get("new", [])
        if not news:
            return ["*(none)*"]
        return [f"- {n.get('text', '')}" for n in news[-5:]]

    lines = [
        "# Operational Board",
        "",
        "> Auto-synced from `data/board.json`.  ",
        f"> Last sync: {now[:19].replace('T', ' ')}",
        "",
        "## IN PROGRESS",
    ]
    lines.extend(items_list("in_progress"))
    lines.extend(["", "## NEXT BEST ACTION", next_best()])
    lines.extend(["", "## NEW"])
    lines.extend(recent_news())
    lines.extend(["", "## PIPELINE", "", "### RAW"])
    lines.extend(items_list("raw"))
    lines.extend(["", "### REFINED"])
    lines.extend(items_list("refined"))
    lines.extend(["", "### PLANNED"])
    lines.extend(items_list("planned"))
    lines.extend(["", "### DONE (last 5)"])
    lines.extend(done_items())
    lines.extend(["", "---", "", "*To modify the board, use the MUD client (`add`, `working on`, `done`).*"])

    vault_path.parent.mkdir(parents=True, exist_ok=True)
    with open(vault_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return True
