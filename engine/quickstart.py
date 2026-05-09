"""
quickstart.py -- Idempotent first-run bootstrap for COMPOUND_APPROACH.

This seeds a usable board + vault experience for new or reset environments
without overwriting existing work.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

try:
    from .board import load_board, save_board
    from .vault_sync import sync as sync_board_to_vault
except ImportError:
    from board import load_board, save_board
    from vault_sync import sync as sync_board_to_vault


MARKER_NAME = ".quickstart_seeded_v1.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_quickstart(root: Path | None = None) -> dict:
    root = root or Path(__file__).parent.parent
    data_dir = root / "data"
    vault_dir = root / "vault"
    logs_dir = data_dir / "logs"
    marker_path = data_dir / MARKER_NAME

    data_dir.mkdir(parents=True, exist_ok=True)
    vault_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    result = {"seeded": False, "messages": []}

    if marker_path.exists():
        result["messages"].append("Quickstart already initialized.")
        _write_workspace_map(root)
        return result

    board_seeded = _seed_board_if_empty(root)
    notes_seeded = _seed_notes_if_empty(root)
    vault_seeded = _seed_vault_files(root)
    _write_workspace_map(root)

    try:
        sync_board_to_vault(root)
    except Exception:
        pass

    marker = {
        "seeded_at": utc_now(),
        "version": 1,
        "board_seeded": board_seeded,
        "notes_seeded": notes_seeded,
        "vault_seeded_files": vault_seeded,
    }
    marker_path.write_text(json.dumps(marker, indent=2), encoding="utf-8")

    result["seeded"] = bool(board_seeded or notes_seeded or vault_seeded)
    if board_seeded:
        result["messages"].append(f"Seeded board with {board_seeded} starter items.")
    if notes_seeded:
        result["messages"].append("Seeded starter room notes.")
    if vault_seeded:
        result["messages"].append(f"Created {vault_seeded} quickstart vault file(s).")
    result["messages"].append("Generated workspace map.")

    return result


def _seed_board_if_empty(root: Path) -> int:
    board_path = root / "data" / "board.json"
    board = load_board(board_path)
    total_items = sum(len(board.get("columns", {}).get(column, [])) for column in ("raw", "refined", "planned", "in_progress", "done"))
    if total_items > 0:
        return 0

    now = utc_now()
    starter = [
        _new_item("Run `help` in the portal terminal and explore available commands.", "system", now, "planned", priority=True),
        _new_item("Capture one daily note in `vault/00_DAILY/QUICKSTART_TODAY.md`.", "system", now, "planned"),
        _new_item("Add your first real task with: add <task title>.", "system", now, "refined", priority=True),
        _new_item("Define one shared objective for this week in `03_SHARED/PORTAL_MISSIONS.md`.", "system", now, "raw"),
    ]

    for item in starter:
        board["columns"][item.pop("_column")].append(item)
        board.setdefault("new", []).append({"timestamp": now, "text": f"system seeded: {item['title']}"})

    board["new"] = board["new"][-25:]
    save_board(board_path, board)
    return len(starter)


def _seed_notes_if_empty(root: Path) -> bool:
    notes_path = root / "data" / "notes.json"
    payload = {}
    if notes_path.exists():
        try:
            payload = json.loads(notes_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            payload = {}

    if payload:
        return False

    now = utc_now()
    payload = {
        "": [
            {
                "author": "system",
                "timestamp": now,
                "text": "Welcome to the portal. Type `board` for active work, then `help` for command list.",
            }
        ],
        "vault/03_SHARED": [
            {
                "author": "system",
                "timestamp": now,
                "text": "Shared zone online. Keep decisions in DECISION_LOG.md and ship from board.",
            }
        ],
    }
    notes_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return True


def _seed_vault_files(root: Path) -> int:
    files = {
        root / "vault" / "00_DAILY" / "QUICKSTART_TODAY.md": _daily_quickstart(),
        root / "vault" / "03_SHARED" / "PORTAL_MISSIONS.md": _portal_missions(),
        root / "vault" / "03_SHARED" / "SESSION_RITUAL.md": _session_ritual(),
    }

    created = 0
    for path, content in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists() or not path.read_text(encoding="utf-8", errors="replace").strip():
            path.write_text(content, encoding="utf-8")
            created += 1
    return created


def _write_workspace_map(root: Path):
    map_path = root / "vault" / "03_SHARED" / "WORKSPACE_MAP.md"
    sections = []
    for child in sorted(root.iterdir(), key=lambda p: p.name.lower()):
        if child.name.startswith(".") or child.name in {"__pycache__", ".venv", "venv", "node_modules"}:
            continue
        if child.is_dir():
            file_count = _count_files(child)
            sections.append(f"- **{child.name}/** ({file_count} files)")
        else:
            sections.append(f"- `{child.name}`")

    lines = [
        "# Workspace Map",
        "",
        f"> Auto-generated: {utc_now()[:19].replace('T', ' ')} UTC",
        "",
        "## Top-Level",
    ]
    lines.extend(sections if sections else ["- (empty)"])
    lines.extend(
        [
            "",
            "## Fast Paths",
            "- `engine/` runtime world + websocket server",
            "- `launcher/` control panel",
            "- `vault/` knowledge layer (Obsidian)",
            "- `data/` board state + logs",
        ]
    )
    map_path.parent.mkdir(parents=True, exist_ok=True)
    map_path.write_text("\n".join(lines), encoding="utf-8")


def _count_files(path: Path) -> int:
    count = 0
    for _ in path.rglob("*"):
        count += 1
    return count


def _new_item(title: str, actor: str, now: str, column: str, priority: bool = False) -> dict:
    return {
        "_column": column,
        "id": uuid.uuid4().hex[:12],
        "title": title,
        "owner": None,
        "mode": "SHARED",
        "priority": priority,
        "created_by": actor,
        "created_at": now,
        "updated_at": now,
    }


def _daily_quickstart() -> str:
    return (
        "# QUICKSTART TODAY\n\n"
        "## Minimum Viable Session\n"
        "- [ ] Open portal client and run `board`\n"
        "- [ ] Add one task with `add`\n"
        "- [ ] Claim it with `working on`\n"
        "- [ ] Log one result with `done`\n\n"
        "## Capture\n"
        "- Win:\n"
        "- Blocker:\n"
        "- Next move:\n"
    )


def _portal_missions() -> str:
    return (
        "# Portal Missions\n\n"
        "## Current Mission Stack\n"
        "1. Keep shared board current from command terminal.\n"
        "2. Distill decisions into `DECISION_LOG.md`.\n"
        "3. End each session with next-best-action set.\n\n"
        "## Command Cheatsheet\n"
        "- `board`\n"
        "- `add <task>`\n"
        "- `working on <task>`\n"
        "- `done <task> -- <result>`\n"
        "- `projects`, `warp`, `find`\n"
    )


def _session_ritual() -> str:
    return (
        "# Session Ritual\n\n"
        "## Start (2 min)\n"
        "- Open board and pick one outcome.\n"
        "- Set status to that outcome.\n\n"
        "## Build (25 min)\n"
        "- Ship one meaningful change.\n"
        "- Log notes on evidence, not vibes.\n\n"
        "## Close (3 min)\n"
        "- Move finished work to DONE.\n"
        "- Write next-best-action for next login.\n"
    )
