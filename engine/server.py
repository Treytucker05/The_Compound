"""
server.py -- COMPOUND_APPROACH WebSocket MUD server.

Binds 0.0.0.0:8765. Serves static/index.html on / and WebSocket on /ws.
Also serves small JSON endpoints for the portal HUD.
"""

from __future__ import annotations

import asyncio
import copy
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

import websockets
from websockets.asyncio.server import serve

sys.path.insert(0, str(Path(__file__).parent))

from agent_briefing import briefing_for_actor
from board import COLUMNS, active_items_for_actor, add_item, blocked_items, load_board, save_board, utc_now
from commands import handle
from missions import load_missions
from quickstart import ensure_quickstart
from radio import ask_question, load_radio, needs_attention_threads, reply_to_thread, resolve_thread, summarize_radio
from vault_sync import sync as vault_sync
from world import ROOT_PATH, Player, World

ROOT_DIR = Path(__file__).parent.parent
HOST = os.environ.get("MUD_HOST", "0.0.0.0")
PORT = int(os.environ.get("MUD_PORT", "8765"))
NOTES_PATH = Path(os.environ.get("NOTES_PATH", str(ROOT_DIR / "data" / "notes.json")))
BOARD_PATH = Path(os.environ.get("BOARD_PATH", str(ROOT_DIR / "data" / "board.json")))
RADIO_PATH = Path(os.environ.get("RADIO_PATH", str(ROOT_DIR / "data" / "radio.json")))
LOG_DIR = Path(os.environ.get("LOG_DIR", str(ROOT_DIR / "data" / "logs")))
VAULT_DIR = ROOT_DIR / "vault"

EVENT_LOG = LOG_DIR / "events.jsonl"

QUICKSTART_STATUS: dict = {}
world: World | None = None
connected_players: dict = {}

STAGE_LABELS = {
    "raw": "Ideas",
    "refined": "Plan",
    "planned": "Ready",
    "in_progress": "Doing",
    "done": "Done",
}

STAGE_RULES = {
    "raw": {
        "label": "Ideas",
        "next": "Plan",
        "missing": ("why",),
        "message": "Add why/use before moving into Plan.",
    },
    "refined": {
        "label": "Plan",
        "next": "Ready",
        "missing": ("why", "steps", "acceptance"),
        "message": "Add why/use, steps, and a done check before Ready.",
    },
    "planned": {
        "label": "Ready",
        "next": "Doing",
        "missing": ("why", "steps", "acceptance"),
        "message": "Ready to start once the plan basics are filled in.",
    },
    "in_progress": {
        "label": "Doing",
        "next": "Done",
        "missing": (),
        "message": "Actively owned work.",
    },
    "done": {
        "label": "Done",
        "next": "",
        "missing": (),
        "message": "Completed work.",
    },
}

GUIDE_TEMPLATES = {
    "why": {
        "label": "Why / use",
        "summary": "Explain why the idea matters before it becomes a plan.",
        "questions": [
            "What is the idea in one sentence?",
            "Who is this for: Trey, Joe, or both?",
            "What problem does it solve, or what useful/fun thing does it add?",
            "What is the smallest useful version?",
            "Where does it belong: HUD, vault, MUD/world, launcher, or server?",
        ],
    },
    "steps": {
        "label": "Steps",
        "summary": "Turn the idea into a short build path.",
        "questions": [
            "What has to change first?",
            "What files, screens, or commands are likely involved?",
            "What can be tested in the browser before moving on?",
            "What should be saved to the shared vault or board?",
        ],
    },
    "acceptance": {
        "label": "Done check",
        "summary": "Describe the proof that this is ready to use.",
        "questions": [
            "What should Trey and Joe both be able to see or do?",
            "What browser check proves it works?",
            "What server or data check proves it persisted?",
            "What should be cut for v1?",
        ],
    },
}

GUIDE_PROMPT_TEMPLATE = """Help turn this Compound board card into a buildable plan.

Answer the guide questions, keep the scope small, and separate must-have v1 work from later ideas.

Required output:
1. Why / use
2. Steps
3. Done check
4. Browser verification
5. Cut for v1
"""

PINNED_VAULT_NOTES = (
    "03_SHARED/OPERATIONAL_BOARD.md",
    "03_SHARED/PROJECT_MAP.md",
    "03_SHARED/PORTAL_MISSIONS.md",
)

VAULT_GROUP_ORDER = {
    "Shared": 0,
    "Daily": 1,
    "Projects": 2,
    "Personal": 3,
    "System": 4,
    "Logs": 5,
    "Archive": 6,
    "Other": 7,
}


def require_world() -> World:
    if world is None:
        raise RuntimeError("World is not initialized. Start the server via main().")
    return world


def log_event(event_type: str, player_name: str, data: dict):
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        "player": player_name,
        "data": data,
    }
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        with open(EVENT_LOG, "a", encoding="utf-8") as handle_out:
            handle_out.write(json.dumps(entry) + "\n")
    except Exception as exc:
        print(f"[LOG ERROR] {exc}")


def log_board_event(event_type: str, player_name: str, data: dict):
    log_event(f"board_{event_type}", player_name, data)


def log_radio_event(event_type: str, player_name: str, data: dict):
    log_event(f"radio_{event_type}", player_name, data)


def load_board_snapshot() -> dict:
    if not BOARD_PATH.exists():
        return {}
    try:
        return json.loads(BOARD_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def query_value(query: dict, key: str, default: str = "") -> str:
    return unquote(query.get(key, [default])[0] or default).strip()


def query_bool(query: dict, key: str, default: bool = False) -> bool:
    raw = query_value(query, key, "1" if default else "0").lower()
    return raw in ("1", "true", "yes", "on")


def board_column_label(column: str) -> str:
    return STAGE_LABELS.get(column, column.replace("_", " "))


def gate_status_for_item(item: dict, column: str) -> dict:
    rule = STAGE_RULES.get(column, {})
    required = rule.get("missing", ())
    missing = [field for field in required if not str(item.get(field, "")).strip()]
    return {
        "state": "needs_info" if missing else "ready",
        "missing": missing,
        "message": rule.get("message", ""),
        "next": rule.get("next", ""),
    }


def board_payload(board: dict | None = None) -> dict:
    board = copy.deepcopy(board or load_board(BOARD_PATH))
    for column in COLUMNS:
        for item in board.get("columns", {}).get(column, []):
            item["gate_status"] = gate_status_for_item(item, column)
    return {
        "board": board,
        "pulse": build_pulse_payload(),
        "stage_rules": STAGE_RULES,
        "guide_templates": GUIDE_TEMPLATES,
        "guide_prompt_template": GUIDE_PROMPT_TEMPLATE,
    }


def board_actor(query: dict) -> str:
    return query_value(query, "actor", "portal")[:32] or "portal"


def radio_actor(query: dict) -> str:
    return query_value(query, "actor", "portal")[:32] or "portal"


def radio_payload(actor: str = "", include_resolved: bool = False) -> dict:
    radio = load_radio(RADIO_PATH)
    actor_lower = actor.strip().lower()
    threads = []
    for thread in radio.get("threads", []):
        if not include_resolved and thread.get("status") != "open":
            continue
        if actor_lower in ("trey", "joe"):
            participants = {thread.get("from", "").lower(), thread.get("to", "").lower()}
            if actor_lower not in participants:
                continue
        threads.append(radio_thread_summary(thread))
    attention = needs_attention_threads(radio, actor)
    return {
        "actor": actor or "portal",
        "radio": summarize_radio(radio),
        "threads": threads[-12:],
        "needs_attention_count": len(attention),
        "needs_attention_threads": attention[-8:],
        "pulse": build_pulse_payload(),
    }


def agent_briefing_payload(actor: str = "Trey") -> dict:
    return {"briefing": briefing_for_actor(actor)}


def radio_thread_summary(thread: dict) -> dict:
    messages = thread.get("messages", [])
    first = messages[0] if messages else {}
    latest = messages[-1] if messages else {}
    return {
        "id": thread.get("id", ""),
        "from": thread.get("from", ""),
        "to": thread.get("to", ""),
        "status": thread.get("status", "open"),
        "text": first.get("text", ""),
        "latest_from": latest.get("from", ""),
        "latest_text": latest.get("text", ""),
        "updated_at": thread.get("updated_at", ""),
        "messages": messages[-6:],
    }


def api_ask_radio(query: dict) -> tuple[int, dict]:
    actor = radio_actor(query)
    target = query_value(query, "to")[:32]
    text = query_value(query, "text")[:800]
    if not target or not text:
        return 400, {"error": "Missing recipient or message."}

    radio, thread = ask_question(RADIO_PATH, actor, target, text)
    log_radio_event("question_sent_ui", actor, {"thread": thread})
    return 200, radio_payload(actor)


def api_reply_radio(query: dict) -> tuple[int, dict]:
    actor = radio_actor(query)
    thread_id = query_value(query, "id")
    text = query_value(query, "text")[:800]
    if not thread_id or not text:
        return 400, {"error": "Missing thread id or message."}

    _radio, thread = reply_to_thread(RADIO_PATH, thread_id, actor, text)
    if not thread:
        return 404, {"error": "Radio thread not found."}
    log_radio_event("reply_sent_ui", actor, {"thread": thread, "reply": text})
    return 200, radio_payload(actor)


def api_resolve_radio(query: dict) -> tuple[int, dict]:
    actor = radio_actor(query)
    thread_id = query_value(query, "id")
    note = query_value(query, "note")[:800]
    if not thread_id:
        return 400, {"error": "Missing thread id."}

    _radio, thread = resolve_thread(RADIO_PATH, thread_id, actor, note)
    if not thread:
        return 404, {"error": "Radio thread not found."}
    log_radio_event("thread_resolved_ui", actor, {"thread": thread, "note": note})
    return 200, radio_payload(actor)


def find_board_item(board: dict, item_id: str) -> tuple[str, int, dict] | None:
    for column in COLUMNS:
        for index, item in enumerate(board.get("columns", {}).get(column, [])):
            if item.get("id") == item_id:
                return column, index, item
    return None


def record_board_news(board: dict, text: str):
    board.setdefault("new", []).append({"timestamp": utc_now(), "text": text})
    board["new"] = board["new"][-25:]


def sync_board_vault():
    try:
        vault_sync(ROOT_DIR)
    except TypeError:
        try:
            vault_sync()
        except Exception:
            pass
    except Exception:
        pass


def api_add_board_item(query: dict) -> tuple[int, dict]:
    title = query_value(query, "title")
    if not title:
        return 400, {"error": "Missing title."}

    actor = board_actor(query)
    board, item = add_item(BOARD_PATH, title[:180], actor)
    target_column = query_value(query, "column", "raw")
    if target_column in COLUMNS and target_column != "raw":
        board["columns"]["raw"].remove(item)
        board["columns"][target_column].append(item)
        record_board_news(board, f"{actor} moved: {item['title']} -> {board_column_label(target_column)}")
        save_board(BOARD_PATH, board)

    log_board_event("task_added_ui", actor, {"item": item})
    sync_board_vault()
    return 200, board_payload(board)


def api_update_board_item(query: dict) -> tuple[int, dict]:
    item_id = query_value(query, "id")
    if not item_id:
        return 400, {"error": "Missing id."}

    board = load_board(BOARD_PATH)
    found = find_board_item(board, item_id)
    if not found:
        return 404, {"error": "Board item not found."}

    column, _index, item = found
    actor = board_actor(query)
    title = query_value(query, "title")
    owner = query_value(query, "owner")
    mode = query_value(query, "mode")
    completion_note = query_value(query, "completion_note")
    why = query_value(query, "why")
    steps = query_value(query, "steps")
    acceptance = query_value(query, "acceptance")
    blocked_reason = query_value(query, "blocked_reason")
    unblocked_note = query_value(query, "unblocked_note")

    changed = []
    if title and title != item.get("title"):
        item["title"] = title[:180]
        changed.append("title")
    if "owner" in query:
        item["owner"] = owner or None
        changed.append("owner")
    if mode in ("SOLO", "SHARED"):
        item["mode"] = mode
        changed.append("mode")
    if "priority" in query:
        item["priority"] = query_bool(query, "priority")
        changed.append("priority")
    if "completion_note" in query:
        item["completion_note"] = completion_note
        changed.append("completion_note")
    if "why" in query:
        item["why"] = why[:500]
        changed.append("why")
    if "steps" in query:
        item["steps"] = steps[:900]
        changed.append("steps")
    if "acceptance" in query:
        item["acceptance"] = acceptance[:500]
        changed.append("acceptance")
    if "blocked" in query:
        blocked = query_bool(query, "blocked")
        item["blocked"] = blocked
        if blocked:
            item["blocked_reason"] = blocked_reason[:500]
            item["blocked_by"] = actor
            item["blocked_at"] = utc_now()
        else:
            item.pop("blocked_reason", None)
            item.pop("blocked_by", None)
            item.pop("blocked_at", None)
            item["unblocked_by"] = actor
            item["unblocked_at"] = utc_now()
            item["unblocked_note"] = unblocked_note[:500]
        changed.append("blocked")

    if changed:
        item["updated_at"] = utc_now()
        record_board_news(board, f"{actor} updated: {item.get('title', 'untitled')}")
        save_board(BOARD_PATH, board)
        log_board_event("task_updated_ui", actor, {"item": item, "column": column, "changed": changed})
        sync_board_vault()

    return 200, board_payload(board)


def api_move_board_item(query: dict) -> tuple[int, dict]:
    item_id = query_value(query, "id")
    target_column = query_value(query, "column")
    if not item_id or target_column not in COLUMNS:
        return 400, {"error": "Missing id or invalid column."}

    board = load_board(BOARD_PATH)
    found = find_board_item(board, item_id)
    if not found:
        return 404, {"error": "Board item not found."}

    source_column, _old_index, item = found
    actor = board_actor(query)
    raw_index = query_value(query, "index", "")
    try:
        target_index = int(raw_index)
    except ValueError:
        target_index = len(board["columns"].get(target_column, []))

    board["columns"][source_column].remove(item)
    target_items = board["columns"][target_column]
    target_index = max(0, min(target_index, len(target_items)))

    item["updated_at"] = utc_now()
    if target_column == "in_progress":
        item["owner"] = actor
        item["started_at"] = item.get("started_at") or utc_now()
        item.pop("completed_at", None)
        item.pop("completed_by", None)
        item.pop("completion_note", None)
    elif target_column == "done":
        item["completed_at"] = item.get("completed_at") or utc_now()
        item["completed_by"] = actor
        note = query_value(query, "completion_note")
        if note:
            item["completion_note"] = note[:240]
    else:
        item.pop("completed_at", None)
        item.pop("completed_by", None)
        item.pop("completion_note", None)

    target_items.insert(target_index, item)
    record_board_news(board, f"{actor} moved: {item.get('title', 'untitled')} -> {board_column_label(target_column)}")
    save_board(BOARD_PATH, board)
    log_board_event("task_moved_ui", actor, {"item": item, "from": source_column, "to": target_column})
    sync_board_vault()
    return 200, board_payload(board)


def api_delete_board_item(query: dict) -> tuple[int, dict]:
    item_id = query_value(query, "id")
    if not item_id:
        return 400, {"error": "Missing id."}

    board = load_board(BOARD_PATH)
    found = find_board_item(board, item_id)
    if not found:
        return 404, {"error": "Board item not found."}

    column, _index, item = found
    actor = board_actor(query)
    board["columns"][column].remove(item)
    record_board_news(board, f"{actor} deleted: {item.get('title', 'untitled')}")
    save_board(BOARD_PATH, board)
    log_board_event("task_deleted_ui", actor, {"item": item, "from": column})
    sync_board_vault()
    return 200, board_payload(board)


def read_event_tail(limit: int = 30) -> list[dict]:
    if not EVENT_LOG.exists():
        return []
    try:
        lines = EVENT_LOG.read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception:
        return []

    events: list[dict] = []
    for line in lines[-limit:]:
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return events


def compute_done_streak(done_items: list[dict]) -> int:
    done_dates = set()
    for item in done_items:
        stamp = item.get("completed_at")
        if not stamp:
            continue
        try:
            day = datetime.fromisoformat(stamp.replace("Z", "+00:00")).astimezone(timezone.utc).date()
            done_dates.add(day)
        except Exception:
            continue

    streak = 0
    cursor = datetime.now(timezone.utc).date()
    while cursor in done_dates:
        streak += 1
        cursor -= timedelta(days=1)
    return streak


def next_action_from_board(board: dict) -> str:
    columns = board.get("columns", {})
    in_progress = columns.get("in_progress", [])
    if in_progress:
        item = in_progress[0]
        owner = item.get("owner") or "unowned"
        return f"{item.get('title', 'untitled')} ({owner})"

    ready = columns.get("planned", []) + columns.get("refined", []) + columns.get("raw", [])
    for item in ready:
        if item.get("priority"):
            return f"{item.get('title', 'untitled')} [PRIORITY]"
    if ready:
        return ready[0].get("title", "untitled")
    return "No active tasks."


def build_pulse_payload() -> dict:
    board = load_board_snapshot()
    radio = summarize_radio(load_radio(RADIO_PATH))
    columns = board.get("columns", {})
    counts = {
        "raw": len(columns.get("raw", [])),
        "refined": len(columns.get("refined", [])),
        "planned": len(columns.get("planned", [])),
        "in_progress": len(columns.get("in_progress", [])),
        "done": len(columns.get("done", [])),
    }
    total_items = sum(counts.values())
    streak = compute_done_streak(columns.get("done", []))
    recent_news = board.get("new", [])[-8:]

    done_count = counts["done"]
    active_count = counts["in_progress"]
    quests = [
        {"id": "first_add", "title": "Add first task", "done": total_items > 0},
        {"id": "start_focus", "title": "Start one task", "done": active_count > 0 or done_count > 0},
        {"id": "ship_result", "title": "Complete one task", "done": done_count > 0},
    ]

    return {
        "counts": counts,
        "total_items": total_items,
        "done_streak_days": streak,
        "next_action": next_action_from_board(board),
        "recent_news": recent_news,
        "recent_events": read_event_tail(14),
        "quests": quests,
        "radio": radio,
        "active_items": _pulse_active_items(board),
        "blocked_items": blocked_items(board),
        "missions": load_missions(ROOT_DIR),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def _pulse_active_items(board: dict) -> list[dict]:
    merged = {}
    for actor in ("Trey", "Joe"):
        for item in active_items_for_actor(board, actor):
            merged[item["id"]] = item
    return list(merged.values())


def format_file_size(size: int) -> str:
    if size < 1024:
        return f"{size} B"
    if size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    return f"{size / (1024 * 1024):.1f} MB"


def vault_note_title(relative_path: str) -> str:
    stem = Path(relative_path).stem
    words = stem.replace("_", " ").replace("-", " ").split()
    return " ".join(word.capitalize() for word in words) or relative_path


def vault_note_group(relative_path: str) -> str:
    parts = relative_path.split("/")
    first = parts[0].upper() if parts else ""
    rel_upper = relative_path.upper()
    if first == "03_SHARED":
        return "Shared"
    if first in ("00_DAILY", "DAILY"):
        return "Daily"
    if first in ("01_PROJECTS", "PROJECTS") or "PROJECT" in rel_upper:
        return "Projects"
    if first in ("01_JOSEPH", "02_TREY", "PERSONAL", "PEOPLE"):
        return "Personal"
    if first in ("04_SYSTEM", "SYSTEM"):
        return "System"
    if first in ("06_LOGS", "LOGS") or "LOG" in rel_upper:
        return "Logs"
    if first in ("99_ARCHIVE", "ARCHIVE"):
        return "Archive"
    return "Other"


def vault_pin_rank(relative_path: str) -> int:
    try:
        return PINNED_VAULT_NOTES.index(relative_path)
    except ValueError:
        return len(PINNED_VAULT_NOTES)


def vault_file_metadata(path: Path) -> dict:
    rel = path.relative_to(VAULT_DIR).as_posix()
    folder = rel.rsplit("/", 1)[0] if "/" in rel else ""
    try:
        stat = path.stat()
        updated = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat()
        size = stat.st_size
    except OSError:
        updated = ""
        size = 0
    group = vault_note_group(rel)
    return {
        "path": rel,
        "title": vault_note_title(rel),
        "folder": folder,
        "group": group,
        "pinned": rel in PINNED_VAULT_NOTES,
        "size": size,
        "size_label": format_file_size(size),
        "updated_at": updated,
    }


def vault_index_sort_key(item: dict) -> tuple:
    return (
        0 if item.get("pinned") else 1,
        vault_pin_rank(item.get("path", "")),
        VAULT_GROUP_ORDER.get(item.get("group", "Other"), 99),
        item.get("path", "").lower(),
    )


def build_vault_index() -> list[dict]:
    if not VAULT_DIR.exists():
        return []

    files: list[dict] = []
    for path in sorted(VAULT_DIR.rglob("*.md"), key=lambda item: str(item).lower()):
        if ".obsidian" in path.parts:
            continue
        files.append(vault_file_metadata(path))

    files.sort(key=vault_index_sort_key)
    return files[:400]


def read_vault_markdown(relative_path: str) -> tuple[int, dict]:
    if not relative_path:
        return 400, {"error": "Missing path parameter."}

    normalized = relative_path.strip().replace("\\", "/")
    candidate = (VAULT_DIR / normalized).resolve()
    vault_root = VAULT_DIR.resolve()

    try:
        candidate.relative_to(vault_root)
    except ValueError:
        return 403, {"error": "Path is outside vault."}

    if not candidate.exists() or not candidate.is_file():
        return 404, {"error": "File not found."}
    if candidate.suffix.lower() != ".md":
        return 400, {"error": "Only markdown files are supported."}

    try:
        content = candidate.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:
        return 500, {"error": f"Could not read file: {exc}"}

    payload = vault_file_metadata(candidate)
    payload["content"] = content
    return 200, payload


def json_response(connection, status: int, payload: dict):
    response = connection.respond(status, json.dumps(payload))
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    response.headers["Cache-Control"] = "no-store"
    return response


async def send_prompt(ws, player: Player):
    await ws.send(f"PROMPT:{player.prompt()}")


def room_path_label(player: Player, vault_root: Path | None = None) -> str:
    if not player.room:
        return "unknown"
    root = vault_root or VAULT_DIR
    try:
        rel = player.room.path.relative_to(root)
    except ValueError:
        return player.room.name or "unknown"
    return rel.as_posix() or "The Compound"


def summarize_presence_action(raw: str, player: Player, previous_room_id: str | None = None) -> str:
    parts = raw.strip().split(None, 1)
    cmd = parts[0].lower() if parts else ""
    args = parts[1].strip() if len(parts) > 1 else ""

    if cmd == "login":
        return "entered the Compound"
    if cmd == "status":
        return f"status: {player.status}"
    if cmd in ("n", "s", "e", "w", "u", "d", "ne", "nw", "se", "sw", "north", "south", "east", "west", "up", "down", "northeast", "northwest", "southeast", "southwest", "cd", "go", "warp"):
        current_room_id = player.room.id if player.room else ""
        if previous_room_id is not None and current_room_id == previous_room_id:
            return "tried to move"
        return f"moved to {room_path_label(player)}"
    if cmd == "working":
        return f"working on {args[3:].strip() or 'a task'}"[:80]
    if cmd == "done":
        return "logged a completion"
    if cmd == "add":
        return "added a board card"
    if cmd in ("board", "next"):
        return "checked the board"
    if cmd in ("ask", "reply", "resolve", "inbox", "radio"):
        return "used radio"
    if cmd in ("blocked", "unblocked", "unblock"):
        return "updated a block"
    if cmd in ("mission", "missions", "quests"):
        return "checked missions"
    if cmd == "say":
        return "spoke in room"
    if cmd == "tell":
        return "sent a tell"
    if cmd in ("look", "ls", "dir", "l"):
        return f"looked at {room_path_label(player)}"
    if cmd in ("cat", "read", "less"):
        return "read a vault note"
    if cmd == "note":
        return "pinned a room note"
    return f"ran {cmd}" if cmd else "active"


def record_presence_action(player: Player, raw: str, previous_room_id: str | None = None):
    player.last_action = summarize_presence_action(raw, player, previous_room_id)
    player.last_action_at = datetime.now(timezone.utc).isoformat()


def presence_entry(player: Player, vault_root: Path | None = None) -> dict:
    return {
        "name": player.name,
        "room": player.room.name if player.room else "unknown",
        "room_id": player.room.id if player.room else "",
        "room_path": room_path_label(player, vault_root),
        "status": player.status,
        "last_action": getattr(player, "last_action", "active"),
        "last_action_at": getattr(player, "last_action_at", ""),
    }


async def broadcast_state():
    """Send a lightweight state snapshot to connected clients."""
    runtime_world = require_world()
    state = []
    for player in list(runtime_world.players.values()):
        state.append(presence_entry(player))

    payload = f"STATE:{json.dumps(state)}"
    for ws_conn in list(connected_players.keys()):
        try:
            await ws_conn.send(payload)
        except Exception as exc:
            log_event("error", "system", {"context": "broadcast_state", "error": str(exc)})


async def broadcast_pulse():
    payload = f"PULSE:{json.dumps(build_pulse_payload())}"
    for ws_conn in list(connected_players.keys()):
        try:
            await ws_conn.send(payload)
        except Exception as exc:
            log_event("error", "system", {"context": "broadcast_pulse", "error": str(exc)})


async def send_dir_state(ws, room):
    """Send current directory state for the HUD sidebar."""
    runtime_world = require_world()
    dirs = []
    for direction, dir_id in room.exits.items():
        if dir_id in runtime_world.dirs:
            dirs.append({"name": runtime_world.dirs[dir_id].name, "direction": direction, "id": dir_id})
    files = [{"name": file_item.name, "size": file_item.format_size(), "ext": file_item.ext} for file_item in room.files]
    path_label = str(room.path.relative_to(runtime_world.root)) if room.path != runtime_world.root else "The Compound"
    payload = f"DIR:{json.dumps({'path': path_label, 'dirs': dirs, 'files': files})}"
    try:
        await ws.send(payload)
    except Exception as exc:
        log_event("error", "system", {"context": "send_dir_state", "error": str(exc)})


async def mud_handler(websocket):
    runtime_world = require_world()

    await websocket.send("Welcome to The Compound - The Portal")
    await websocket.send("Enter your character name:")

    try:
        name_msg = await websocket.recv()
    except websockets.exceptions.ConnectionClosed:
        return

    name = str(name_msg).strip()[:32] or "Wanderer"

    if name.lower() in runtime_world.players:
        await websocket.send(f"The name '{name}' is already in use. Disconnecting.")
        await websocket.close()
        return

    player = Player(name=name, ws=websocket)
    runtime_world.add_player(player)
    connected_players[websocket] = player

    record_presence_action(player, "login")
    log_event("login", player.name, {"ip": websocket.remote_address[0] if websocket.remote_address else None})
    board_view = handle(player, runtime_world, "board")
    await websocket.send(
        "Connected to The Compound.\n"
        "Operational board is your home screen. Type 'look' to explore the witness layer.\n\n"
        f"{board_view}"
    )
    await send_prompt(websocket, player)
    await broadcast_state()
    await send_dir_state(websocket, player.room)
    await broadcast_pulse()

    for occupant in list(player.room.players):
        if occupant is not player and occupant.ws:
            try:
                await occupant.ws.send(f"{player.name} arrives in a shimmer of light.")
            except Exception as exc:
                log_event("error", "system", {"context": "login_broadcast", "error": str(exc)})

    try:
        async for message in websocket:
            raw = str(message).strip()
            if not raw:
                await send_prompt(websocket, player)
                continue

            log_event("command", player.name, {"raw": raw, "room": player.room.id if player.room else None})
            previous_room_id = player.room.id if player.room else ""
            result = handle(player, runtime_world, raw)
            record_presence_action(player, raw, previous_room_id)

            if result == "__QUIT__":
                await websocket.send("Disconnected from The Compound.")
                await websocket.close()
                break

            if result == "__CLEAR__":
                await websocket.send("CLEAR:")
                await send_prompt(websocket, player)
                continue

            if result:
                await websocket.send(result)

            await send_prompt(websocket, player)

            lowered = raw.lower()
            if lowered.startswith(
                (
                    "n ",
                    "s ",
                    "e ",
                    "w ",
                    "u ",
                    "d ",
                    "ne ",
                    "nw ",
                    "se ",
                    "sw ",
                    "n",
                    "s",
                    "e",
                    "w",
                    "u",
                    "d",
                    "ne",
                    "nw",
                    "se",
                    "sw",
                    "warp",
                    "status",
                    "cd",
                    "go",
                    "working",
                    "add",
                    "done",
                    "ask",
                    "inbox",
                    "radio",
                    "reply",
                    "resolve",
                    "priority",
                    "solo",
                    "shared",
                    "share",
                    "board",
                    "blocked",
                    "unblocked",
                    "unblock",
                    "mission",
                    "missions",
                    "quests",
                )
            ):
                await broadcast_state()
                await send_dir_state(websocket, player.room)
                await broadcast_pulse()

    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        if player.room:
            for occupant in list(player.room.players):
                if occupant is not player and occupant.ws:
                    try:
                        await occupant.ws.send(f"{player.name} fades into the mist.")
                    except Exception as exc:
                        log_event("error", "system", {"context": "logout_broadcast", "error": str(exc)})
        runtime_world.remove_player(player)
        connected_players.pop(websocket, None)
        log_event("logout", player.name, {"room": player.room.id if player.room else None})
        await broadcast_state()
        await broadcast_pulse()


async def process_request(connection, request):
    """Serve static client and lightweight JSON API routes."""
    parsed = urlparse(request.path or "/")
    path = parsed.path
    query = parse_qs(parsed.query, keep_blank_values=True)

    if path == "/":
        html_path = Path(__file__).parent / "static" / "index.html"
        if html_path.exists():
            body = html_path.read_text(encoding="utf-8")
            response = connection.respond(200, body)
            response.headers["Content-Type"] = "text/html; charset=utf-8"
            return response

    if path == "/favicon.ico":
        response = connection.respond(204, "")
        response.headers["Content-Type"] = "image/x-icon"
        return response

    if path == "/api/pulse":
        return json_response(connection, 200, build_pulse_payload())

    if path == "/api/agent-briefing":
        actor = board_actor(query)
        return json_response(connection, 200, agent_briefing_payload(actor))

    if path == "/api/board":
        return json_response(connection, 200, board_payload())

    if path == "/api/board/add":
        status, payload = api_add_board_item(query)
        if status == 200:
            await broadcast_pulse()
        return json_response(connection, status, payload)

    if path == "/api/board/update":
        status, payload = api_update_board_item(query)
        if status == 200:
            await broadcast_pulse()
        return json_response(connection, status, payload)

    if path == "/api/board/move":
        status, payload = api_move_board_item(query)
        if status == 200:
            await broadcast_pulse()
        return json_response(connection, status, payload)

    if path == "/api/board/delete":
        status, payload = api_delete_board_item(query)
        if status == 200:
            await broadcast_pulse()
        return json_response(connection, status, payload)

    if path == "/api/radio":
        actor = radio_actor(query)
        include_resolved = query_bool(query, "include_resolved", False)
        return json_response(connection, 200, radio_payload(actor, include_resolved))

    if path == "/api/radio/ask":
        status, payload = api_ask_radio(query)
        if status == 200:
            await broadcast_pulse()
        return json_response(connection, status, payload)

    if path == "/api/radio/reply":
        status, payload = api_reply_radio(query)
        if status == 200:
            await broadcast_pulse()
        return json_response(connection, status, payload)

    if path == "/api/radio/resolve":
        status, payload = api_resolve_radio(query)
        if status == 200:
            await broadcast_pulse()
        return json_response(connection, status, payload)

    if path == "/api/vault/index":
        return json_response(connection, 200, {"files": build_vault_index()})

    if path == "/api/vault/read":
        value = query.get("path", [""])[0]
        rel_path = unquote(value)
        status, payload = read_vault_markdown(rel_path)
        return json_response(connection, status, payload)

    if path == "/api/health":
        return json_response(connection, 200, {"ok": True, "time": datetime.now(timezone.utc).isoformat()})

    return None


async def main():
    global world
    global QUICKSTART_STATUS

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    QUICKSTART_STATUS = ensure_quickstart(ROOT_DIR)
    world = World(root=ROOT_PATH, notes_path=NOTES_PATH)
    world.board_path = BOARD_PATH
    world.radio_path = RADIO_PATH
    world.log_board_event = log_board_event
    world.log_radio_event = log_radio_event
    connected_players.clear()

    print(f"[PORTAL] Scanning filesystem: {ROOT_PATH} ...")
    print(f"[PORTAL] Loaded {len(world.dirs)} directories")
    print(f"[PORTAL] Starting WebSocket server on ws://{HOST}:{PORT}/ws")
    print(f"[PORTAL] Browser client: http://{HOST}:{PORT}/")
    print(f"[PORTAL] Event log: {EVENT_LOG}")
    print(f"[PORTAL] Notes: {NOTES_PATH}")
    print(f"[PORTAL] Board: {BOARD_PATH}")
    print(f"[PORTAL] Radio: {RADIO_PATH}")
    if QUICKSTART_STATUS.get("messages"):
        for message in QUICKSTART_STATUS["messages"]:
            print(f"[PORTAL] {message}")

    async with serve(
        mud_handler,
        HOST,
        PORT,
        process_request=process_request,
    ):
        await asyncio.Future()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[PORTAL] Server shut down gracefully.")
