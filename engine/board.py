"""
board.py - Persistent Operational Board for COMPOUND_APPROACH.

The board is the human-facing work surface. The MUD/filesystem remains the
witness layer underneath it.
"""

import json
import os
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path


COLUMNS = ("raw", "refined", "planned", "in_progress", "done")
DEFAULT_MODE = "SHARED"
DEFAULT_BOARD_PATH = Path(__file__).parent.parent / "data" / "board.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def default_board() -> dict:
    now = utc_now()
    return {
        "version": 1,
        "created_at": now,
        "updated_at": now,
        "columns": {column: [] for column in COLUMNS},
        "new": [],
    }


def load_board(path: Path) -> dict:
    path = resolve_board_path(path)
    if not path.exists():
        board = default_board()
        save_board(path, board)
        return board

    try:
        with open(path, "r", encoding="utf-8") as f:
            board = json.load(f)
    except json.JSONDecodeError:
        board = default_board()

    board.setdefault("version", 1)
    board.setdefault("created_at", utc_now())
    board.setdefault("updated_at", utc_now())
    board.setdefault("columns", {})
    board.setdefault("new", [])
    for column in COLUMNS:
        board["columns"].setdefault(column, [])
    return board


def save_board(path: Path, board: dict):
    path = resolve_board_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    board["updated_at"] = utc_now()
    tmp_path = path.with_suffix(".json.tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(board, f, indent=2)
    os.replace(tmp_path, path)


def add_item(path: Path, title: str, actor: str) -> tuple[dict, dict]:
    path = resolve_board_path(path)
    board = load_board(path)
    item = _new_item(title.strip(), actor)
    board["columns"]["raw"].append(item)
    _record_new(board, f"{actor} added: {item['title']}")
    save_board(path, board)
    return board, item


def mark_priority(path: Path, query: str, actor: str) -> tuple[dict, dict | None]:
    path = resolve_board_path(path)
    board = load_board(path)
    found = find_item(board, query)
    if not found:
        return board, None

    column, item = found
    item["priority"] = True
    item["updated_at"] = utc_now()
    _record_new(board, f"{actor} marked priority: {item['title']}")
    save_board(path, board)
    return board, item


def set_mode(path: Path, query: str, mode: str, actor: str) -> tuple[dict, dict | None]:
    path = resolve_board_path(path)
    board = load_board(path)
    found = find_item(board, query)
    if not found:
        return board, None

    column, item = found
    item["mode"] = mode
    item["updated_at"] = utc_now()
    _record_new(board, f"{actor} marked {mode}: {item['title']}")
    save_board(path, board)
    return board, item


def start_work(path: Path, query: str, actor: str) -> tuple[dict, dict]:
    path = resolve_board_path(path)
    board = load_board(path)
    found = find_item(board, query)
    if found:
        column, item = found
        board["columns"][column].remove(item)
    else:
        item = _new_item(query.strip(), actor)

    item["owner"] = actor
    item["started_at"] = item.get("started_at") or utc_now()
    item["updated_at"] = utc_now()
    board["columns"]["in_progress"].append(item)
    _record_new(board, f"{actor} started: {item['title']}")
    save_board(path, board)
    return board, item


def complete_work(path: Path, query: str, note: str, actor: str) -> tuple[dict, dict | None]:
    path = resolve_board_path(path)
    board = load_board(path)
    found = find_item(board, query, preferred_columns=("in_progress", "planned", "refined", "raw"))
    if not found:
        return board, None

    column, item = found
    board["columns"][column].remove(item)
    item["completed_at"] = utc_now()
    item["completed_by"] = actor
    item["completion_note"] = note.strip()
    item["updated_at"] = utc_now()
    board["columns"]["done"].append(item)
    _record_new(board, f"{actor} completed: {item['title']}")
    save_board(path, board)
    return board, item


def complete_current_work(path: Path, note: str, actor: str) -> tuple[dict, dict | None]:
    path = resolve_board_path(path)
    board = load_board(path)
    for item in board["columns"]["in_progress"]:
        if item.get("owner", "").lower() == actor.lower():
            return complete_work(path, item["title"], note, actor)
    return board, None


def find_item(board: dict, query: str, preferred_columns: tuple[str, ...] = COLUMNS) -> tuple[str, dict] | None:
    needle = _normalize(query)
    if not needle:
        return None

    candidates = []
    for column in preferred_columns:
        for item in board["columns"].get(column, []):
            title = item.get("title", "")
            norm_title = _normalize(title)
            if needle == norm_title:
                return column, item
            if needle in norm_title:
                candidates.append((column, item))

    return candidates[0] if candidates else None


def resolve_board_path(path: Path | str | None) -> Path:
    if path is None:
        return DEFAULT_BOARD_PATH
    return Path(path)


def next_best_item(board: dict, actor: str | None = None) -> dict | None:
    active_for_actor = []
    if actor:
        active_for_actor = [
            item for item in board["columns"]["in_progress"]
            if item.get("owner", "").lower() == actor.lower()
        ]
    if active_for_actor:
        return active_for_actor[0]

    ready_columns = ("planned", "refined", "raw")
    ready = [item for column in ready_columns for item in board["columns"][column]]
    priority = [item for item in ready if item.get("priority")]
    if priority:
        return priority[0]
    return ready[0] if ready else None


def render_board(board: dict, actor: str | None = None, online_players: list[str] | None = None) -> str:
    online_players = online_players or []
    next_item = next_best_item(board, actor)
    lines = [
        "================= The Compound =================",
        "",
        "IN PROGRESS",
    ]
    lines.extend(_render_items(board["columns"]["in_progress"], show_owner=True))

    lines.extend(["", "NEXT BEST ACTION"])
    if next_item:
        lines.append(f"- {_format_item(next_item, show_owner=True)}")
    else:
        lines.append("(none)")

    lines.extend(["", "NEW"])
    recent = board.get("new", [])[-5:]
    if recent:
        for entry in recent:
            lines.append(f"+ {entry.get('text', '')}")
    else:
        lines.append("(none)")

    lines.extend(["", "PIPELINE", "RAW"])
    lines.extend(_render_items(board["columns"]["raw"]))
    lines.append("")
    lines.append("REFINED")
    lines.extend(_render_items(board["columns"]["refined"]))
    lines.append("")
    lines.append("PLANNED")
    lines.extend(_render_items(board["columns"]["planned"]))
    lines.append("")
    lines.append("DONE")
    lines.extend(_render_items(board["columns"]["done"][-5:], show_done_note=True))

    lines.extend(["", "SYSTEM"])
    if online_players:
        lines.append("online: " + ", ".join(online_players))
    else:
        lines.append("online: none")
    lines.append(f"last update: {board.get('updated_at', '')[:19].replace('T', ' ')}")
    lines.append("mode: BUILD")
    lines.append("=====================================================")
    return "\n".join(lines)


def _new_item(title: str, actor: str) -> dict:
    now = utc_now()
    return {
        "id": uuid.uuid4().hex[:12],
        "title": title,
        "owner": None,
        "mode": DEFAULT_MODE,
        "priority": False,
        "created_by": actor,
        "created_at": now,
        "updated_at": now,
    }


def _record_new(board: dict, text: str):
    board.setdefault("new", []).append({"timestamp": utc_now(), "text": text})
    board["new"] = board["new"][-25:]


def _render_items(items: list[dict], show_owner: bool = False, show_done_note: bool = False) -> list[str]:
    if not items:
        return ["(empty)"]
    return [f"- {_format_item(item, show_owner=show_owner, show_done_note=show_done_note)}" for item in items]


def _format_item(item: dict, show_owner: bool = False, show_done_note: bool = False) -> str:
    parts = [item.get("title", "untitled")]
    if show_owner and item.get("owner"):
        parts.append(f"({item['owner']})")
    if item.get("mode"):
        parts.append(f"[{item['mode']}]")
    if item.get("priority"):
        parts.append("[PRIORITY]")
    if show_done_note and item.get("completion_note"):
        parts.append(f"- {item['completion_note']}")
    return " ".join(parts)


def _normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())
