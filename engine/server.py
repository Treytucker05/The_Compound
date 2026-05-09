"""
server.py -- COMPOUND_APPROACH WebSocket MUD server.

Binds 0.0.0.0:8765. Serves static/index.html on / and WebSocket on /ws.
Also serves small JSON endpoints for the portal HUD.
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

import websockets
from websockets.asyncio.server import serve

sys.path.insert(0, str(Path(__file__).parent))

from commands import handle
from quickstart import ensure_quickstart
from world import ROOT_PATH, Player, World

ROOT_DIR = Path(__file__).parent.parent
HOST = os.environ.get("MUD_HOST", "0.0.0.0")
PORT = int(os.environ.get("MUD_PORT", "8765"))
NOTES_PATH = Path(os.environ.get("NOTES_PATH", str(ROOT_DIR / "data" / "notes.json")))
BOARD_PATH = Path(os.environ.get("BOARD_PATH", str(ROOT_DIR / "data" / "board.json")))
LOG_DIR = Path(os.environ.get("LOG_DIR", str(ROOT_DIR / "data" / "logs")))
VAULT_DIR = ROOT_DIR / "vault"

EVENT_LOG = LOG_DIR / "events.jsonl"

QUICKSTART_STATUS: dict = {}
world: World | None = None
connected_players: dict = {}


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


def load_board_snapshot() -> dict:
    if not BOARD_PATH.exists():
        return {}
    try:
        return json.loads(BOARD_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


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
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def build_vault_index() -> list[dict]:
    if not VAULT_DIR.exists():
        return []

    files: list[dict] = []
    for path in sorted(VAULT_DIR.rglob("*.md"), key=lambda item: str(item).lower()):
        if ".obsidian" in path.parts:
            continue
        rel = path.relative_to(VAULT_DIR).as_posix()
        try:
            stat = path.stat()
            updated = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat()
            size = stat.st_size
        except OSError:
            updated = ""
            size = 0
        files.append({"path": rel, "size": size, "updated_at": updated})

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

    return 200, {
        "path": str(candidate.relative_to(vault_root).as_posix()),
        "content": content,
    }


def json_response(connection, status: int, payload: dict):
    response = connection.respond(status, json.dumps(payload))
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    response.headers["Cache-Control"] = "no-store"
    return response


async def send_prompt(ws, player: Player):
    await ws.send(f"PROMPT:{player.prompt()}")


async def broadcast_state():
    """Send a lightweight state snapshot to connected clients."""
    runtime_world = require_world()
    state = []
    for player in list(runtime_world.players.values()):
        state.append(
            {
                "name": player.name,
                "room": player.room.name if player.room else "unknown",
                "room_id": player.room.id if player.room else "",
                "status": player.status,
            }
        )

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
            result = handle(player, runtime_world, raw)

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
                    "priority",
                    "solo",
                    "shared",
                    "share",
                    "board",
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
    query = parse_qs(parsed.query)

    if path == "/":
        html_path = Path(__file__).parent / "static" / "index.html"
        if html_path.exists():
            body = html_path.read_text(encoding="utf-8")
            response = connection.respond(200, body)
            response.headers["Content-Type"] = "text/html; charset=utf-8"
            return response

    if path == "/api/pulse":
        return json_response(connection, 200, build_pulse_payload())

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
    world.log_board_event = log_board_event
    connected_players.clear()

    print(f"[PORTAL] Scanning filesystem: {ROOT_PATH} ...")
    print(f"[PORTAL] Loaded {len(world.dirs)} directories")
    print(f"[PORTAL] Starting WebSocket server on ws://{HOST}:{PORT}/ws")
    print(f"[PORTAL] Browser client: http://{HOST}:{PORT}/")
    print(f"[PORTAL] Event log: {EVENT_LOG}")
    print(f"[PORTAL] Notes: {NOTES_PATH}")
    print(f"[PORTAL] Board: {BOARD_PATH}")
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
