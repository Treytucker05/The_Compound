"""
commands.py — Filesystem Command Parser
Track B — COMPOUND_APPROACH World Engine
"""

from datetime import datetime, timezone
from pathlib import Path

from board import (
    add_item,
    block_item,
    complete_current_work,
    complete_work,
    load_board,
    mark_priority,
    move_item,
    render_board,
    set_mode,
    start_work,
    unblock_item,
)
from missions import load_missions, render_missions
from radio import ask_question, load_radio, render_inbox, reply_to_thread, resolve_thread
from sparks import add_spark, load_sparks, promote_spark, render_sparks
from vault_sync import sync as vault_sync
from world import Player, World


def handle(player: Player, world: World, raw: str) -> str:
    raw = raw.strip()
    if not raw:
        return ""

    parts = raw.split(None, 1)
    cmd = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""

    board_path = getattr(world, "board_path", None)
    radio_path = getattr(world, "radio_path", None)
    sparks_path = getattr(world, "sparks_path", None)

    # Operational board
    if cmd == "spark":
        if not args:
            return "Use: spark <raw thought>"
        sparks, item = add_spark(sparks_path, args, player.name)
        _log_board_event(world, "spark_added", player, {"spark": item})
        return f"Spark captured: {item['text']}\n\n{render_sparks(sparks)}"

    if cmd == "sparks":
        return render_sparks(load_sparks(sparks_path))

    if cmd == "promote":
        query = _parse_promote_args(args)
        if not query:
            return "Use: promote <spark id or text> to idea"
        sparks, spark_item = promote_spark(sparks_path, query, player.name)
        if not spark_item:
            return f"No open spark matching: {query}"
        board, board_item = add_item(board_path, spark_item["text"], player.name)
        _log_board_event(world, "spark_promoted", player, {"spark": spark_item, "item": board_item})
        _trigger_sync()
        return (
            f"Promoted to Ideas: {board_item['title']}\n\n"
            f"{render_board(board, player.name, _online_players(world))}\n\n"
            f"{render_sparks(sparks)}"
        )

    if cmd == "board":
        return _render_operational_board(player, world)

    if cmd == "next":
        return _render_operational_board(player, world)

    if cmd == "add":
        if not args:
            return "Add what?"
        board, item = add_item(board_path, args, player.name)
        _log_board_event(world, "task_added", player, {"item": item})
        _trigger_sync()
        return f"Added to RAW: {item['title']}\n\n{render_board(board, player.name, _online_players(world))}"

    if cmd == "working":
        if not args.lower().startswith("on "):
            return "Use: working on <item>"
        title = args[3:].strip()
        if not title:
            return "Working on what?"
        board, item = start_work(board_path, title, player.name)
        player.status = f"working on {item['title']}"[:60]
        _log_board_event(world, "task_started", player, {"item": item})
        _trigger_sync()
        return f"Moved to IN PROGRESS: {item['title']} ({player.name})\n\n{render_board(board, player.name, _online_players(world))}"

    if cmd == "priority":
        if not args:
            return "Mark what as priority?"
        board, item = mark_priority(board_path, args, player.name)
        if not item:
            return f"No board item matching: {args}"
        _log_board_event(world, "task_prioritized", player, {"item": item})
        _trigger_sync()
        return f"Marked PRIORITY: {item['title']}\n\n{render_board(board, player.name, _online_players(world))}"

    if cmd in ("plan", "planned"):
        if not args:
            return "Plan what?"
        board, item = move_item(board_path, args, "refined", player.name)
        if not item:
            return f"No board item matching: {args}"
        _log_board_event(world, "task_planned", player, {"item": item})
        _trigger_sync()
        return f"Moved to PLAN: {item['title']}\n\n{render_board(board, player.name, _online_players(world))}"

    if cmd == "ready":
        if not args:
            return "Mark what ready?"
        board, item = move_item(board_path, args, "planned", player.name)
        if not item:
            return f"No board item matching: {args}"
        _log_board_event(world, "task_readied", player, {"item": item})
        _trigger_sync()
        return f"Moved to READY: {item['title']}\n\n{render_board(board, player.name, _online_players(world))}"

    if cmd in ("solo", "shared", "share"):
        if not args:
            return f"Mark what as {cmd.upper()}?"
        mode = "SHARED" if cmd in ("shared", "share") else "SOLO"
        board, item = set_mode(board_path, args, mode, player.name)
        if not item:
            return f"No board item matching: {args}"
        _log_board_event(world, "task_mode_changed", player, {"item": item, "mode": mode})
        _trigger_sync()
        return f"Marked {mode}: {item['title']}\n\n{render_board(board, player.name, _online_players(world))}"

    if cmd == "blocked":
        title, reason = _parse_blocked_args(args)
        if not title or not reason:
            return "Use: blocked <item> -- <reason>"
        board, item = block_item(board_path, title, reason, player.name)
        if not item:
            return f"No board item matching: {title}"
        _log_board_event(world, "task_blocked", player, {"item": item, "reason": reason})
        _trigger_sync()
        return f"Blocked: {item['title']} -- {item.get('blocked_reason', '')}\n\n{render_board(board, player.name, _online_players(world))}"

    if cmd in ("unblocked", "unblock"):
        title, note = _parse_optional_note(args)
        if not title:
            return "Use: unblocked <item> -- <note optional>"
        board, item = unblock_item(board_path, title, note, player.name)
        if not item:
            return f"No board item matching: {title}"
        _log_board_event(world, "task_unblocked", player, {"item": item, "note": note})
        _trigger_sync()
        return f"Unblocked: {item['title']}\n\n{render_board(board, player.name, _online_players(world))}"

    if cmd == "done":
        if not args:
            return "Use: done <item> -- <what happened>, or done <what happened> for your current task."
        title, note = _parse_done_args(args)
        if title:
            board, item = complete_work(board_path, title, note, player.name)
        else:
            board, item = complete_current_work(board_path, note, player.name)
        if not item:
            return "No matching in-progress board item found."
        player.status = "observing"
        _log_board_event(world, "task_done", player, {"item": item, "note": note})
        _trigger_sync()
        return f"Moved to DONE: {item['title']}\nLogged: {note}\n\n{render_board(board, player.name, _online_players(world))}"

    # Radio Inbox
    if cmd == "ask":
        target, text = _parse_target_message(args)
        if not target or not text:
            return "Use: ask <Trey|Joe> <question>"
        radio, thread = ask_question(radio_path, player.name, target, text)
        _log_radio_event(world, "question_sent", player, {"thread": thread})
        _notify_radio(world, player, target, f"[RADIO #{thread['id']}] {player.name}: {text}")
        return f"Radio sent to {thread['to']} as #{thread['id']}.\n\n{render_inbox(radio, player.name)}"

    if cmd in ("inbox", "radio"):
        radio = load_radio(radio_path)
        return render_inbox(radio, player.name)

    if cmd == "reply":
        thread_id, text = _parse_target_message(args)
        if not thread_id or not text:
            return "Use: reply <id> <message>"
        radio, thread = reply_to_thread(radio_path, thread_id, player.name, text)
        if not thread:
            return f"No radio thread matching: {thread_id}"
        target = _other_radio_person(thread, player.name)
        _log_radio_event(world, "reply_sent", player, {"thread": thread, "reply": text})
        _notify_radio(world, player, target, f"[RADIO #{thread['id']}] {player.name}: {text}")
        return f"Radio reply logged on #{thread['id']}.\n\n{render_inbox(radio, player.name)}"

    if cmd == "resolve":
        thread_id, note = _parse_target_message(args)
        if not thread_id:
            return "Use: resolve <id> <note>"
        radio, thread = resolve_thread(radio_path, thread_id, player.name, note)
        if not thread:
            return f"No radio thread matching: {thread_id}"
        target = _other_radio_person(thread, player.name)
        _log_radio_event(world, "thread_resolved", player, {"thread": thread, "note": note})
        _notify_radio(world, player, target, f"[RADIO #{thread['id']}] resolved by {player.name}: {note or 'resolved'}")
        return f"Radio resolved #{thread['id']}.\n\n{render_inbox(radio, player.name)}"

    # Navigation by cardinal direction
    if cmd in ("n", "north"):
        return world.move_player(player, "north")
    if cmd in ("s", "south"):
        return world.move_player(player, "south")
    if cmd in ("e", "east"):
        return world.move_player(player, "east")
    if cmd in ("w", "west"):
        return world.move_player(player, "west")
    if cmd in ("ne", "northeast"):
        return world.move_player(player, "northeast")
    if cmd in ("nw", "northwest"):
        return world.move_player(player, "northwest")
    if cmd in ("se", "southeast"):
        return world.move_player(player, "southeast")
    if cmd in ("sw", "southwest"):
        return world.move_player(player, "southwest")
    if cmd in ("u", "up"):
        return world.move_player(player, "up")
    if cmd in ("d", "down"):
        return world.move_player(player, "down")

    # Filesystem navigation
    if cmd == "cd" or cmd == "go":
        if not args:
            return "Go where?"
        return _cd(player, world, args)

    if cmd == "ls" or cmd == "dir" or cmd == "l" or cmd == "look":
        if not player.room:
            return "You are nowhere."
        return player.room.look()

    if cmd == "cat" or cmd == "read" or cmd == "less":
        if not args:
            return "Read what?"
        return _cat(player, args)

    if cmd == "pwd":
        if not player.room:
            return "Nowhere."
        rel = str(player.room.path.relative_to(world.root.parent)) if player.room.path != world.root else "The Compound"
        return f"Current directory: {rel}"

    if cmd == "find":
        if not args:
            return "Find what?"
        return _find(world, args)

    # Communication
    if cmd == "say":
        if not args:
            return "Say what?"
        world.broadcast(player, f"{player.name} says, '{args}'")
        return f"You say, '{args}'"

    if cmd == "tell":
        if not args:
            return "Tell who what?"
        target_parts = args.split(None, 1)
        if len(target_parts) < 2:
            return "Tell them what?"
        return world.tell(player, target_parts[0], target_parts[1])

    if cmd == "who":
        return world.who()

    if cmd == "examine" or cmd == "ex":
        if not args:
            return "Examine what?"
        return _examine(player, args)

    if cmd == "status":
        if not args:
            return f"Your current status: {player.status}"
        player.status = args.strip()[:60]
        return f"Status set: {player.status}"

    if cmd == "projects":
        return world.projects()

    if cmd in ("mission", "missions", "quests"):
        return render_missions(load_missions(_world_root(world)))

    if cmd == "warp":
        if not args:
            return "Warp where? Type 'projects' to see active directories."
        return world.warp_player(player, args.strip())

    if cmd == "note":
        if not args:
            return "Note what?"
        if not player.room:
            return "You are nowhere."
        note = {
            "author": player.name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "text": args.strip(),
        }
        player.room.notes.append(note)
        world.save_notes()
        return f"You pin a note to the board: '{note['text']}'"

    if cmd == "notes":
        if not player.room:
            return "You are nowhere."
        if not player.room.notes:
            return "The board is empty."
        lines = ["Notes on the board:", ""]
        for i, note in enumerate(player.room.notes[-10:], 1):
            ts = note["timestamp"][:19].replace("T", " ") if "timestamp" in note else ""
            lines.append(f"  {i}. [{ts}] {note['author']}: {note['text']}")
        return "\n".join(lines)

    if cmd == "clear":
        return "__CLEAR__"

    if cmd == "help" or cmd == "?":
        return _help()

    if cmd == "quit":
        return "__QUIT__"

    return f"Unknown command: {cmd}. Type 'help' for a list."


def _cd(player: Player, world: World, target: str) -> str:
    """Change directory by name or direction."""
    target_lower = target.lower().strip()

    # Try exact direction match first
    if target_lower in player.room.exits:
        return world.move_player(player, target_lower)

    # Try match on directory name (last path component) or exact dir_id
    for direction, dir_id in player.room.exits.items():
        if target_lower == dir_id.lower():
            return world.move_player(player, direction)
        dir_name = dir_id.split("/")[-1].lower() if "/" in dir_id else dir_id.lower()
        if target_lower == dir_name:
            return world.move_player(player, direction)
        if target_lower == direction:
            return world.move_player(player, direction)

    # Try warp (absolute path)
    if target_lower in world.dirs:
        return world.warp_player(player, target_lower)

    return f"Cannot find: {target}"


def _cat(player: Player, target: str) -> str:
    """Preview a file's contents."""
    target_lower = target.lower()
    if not player.room:
        return "You are nowhere."

    for f in player.room.files:
        if target_lower in f.name.lower():
            return f.preview()

    return f"No file matching '{target}' here."


def _examine(player: Player, target: str) -> str:
    """Examine a file or player in the room."""
    target_lower = target.lower()

    if player.room:
        for f in player.room.files:
            if target_lower in f.name.lower():
                size = f.format_size()
                mtime = f.mtime.strftime("%Y-%m-%d %H:%M:%S")
                text_flag = "text" if f.is_text else "binary"
                return f"{f.name}\n  Size: {size}\n  Modified: {mtime}\n  Type: {text_flag}"
        for p in player.room.players:
            if target_lower in p.name.lower() and p is not player:
                status = f"\nThey appear to be: {p.status}" if p.status else ""
                return f"{p.name} is here.{status}"

    return "You don't see that here."


def _find(world: World, target: str) -> str:
    """Search for files across all directories."""
    target_lower = target.lower()
    matches = []
    for d in world.dirs.values():
        for f in d.files:
            if target_lower in f.name.lower():
                rel = str(d.path.relative_to(world.root)) if d.path != world.root else "."
                matches.append(f"  {rel}/{f.name}")
    if not matches:
        return f"No files matching '{target}' found."
    if len(matches) > 20:
        return f"Found {len(matches)} matches (showing first 20):\n" + "\n".join(matches[:20])
    return f"Found {len(matches)} match(es):\n" + "\n".join(matches)


def _help() -> str:
    return (
        "Commands:\n"
        "  board                — Show the Operational Board\n"
        "  spark <thought>      — Capture a raw pre-board thought\n"
        "  sparks               — Show open Spark Inbox thoughts\n"
        "  promote <spark> to idea — Move a spark into board Ideas\n"
        "  add <item>           — Add an item to RAW\n"
        "  plan <item>          — Move an idea into PLAN\n"
        "  ready <item>         — Move a plan into READY\n"
        "  working on <item>    — Move item to IN PROGRESS and claim it\n"
        "  priority <item>      — Mark an item as priority\n"
        "  solo <item>          — Mark item as owner-only\n"
        "  shared <item>        — Mark item as handoff-friendly\n"
        "  blocked <item> -- <reason> — Mark a board item blocked\n"
        "  unblocked <item> -- <note> — Clear a board item block\n"
        "  done <item> -- <note> — Move item to DONE and log what happened\n"
        "  next                 — Show the board with next best action\n"
        "  missions             — Show the current shared mission stack\n"
        "  ask <who> <question> — Send a Radio Inbox question\n"
        "  inbox / radio        — Show your Radio Inbox\n"
        "  reply <id> <message> — Reply to a radio thread\n"
        "  resolve <id> <note>  — Close a radio thread\n"
        "  n, s, e, w, ne, nw, se, sw, u, d\n"
        "                       — Move by cardinal direction\n"
        "  cd / go <dir>        — Go to a subdirectory by name\n"
        "  ls / look / dir      — List files and subdirectories\n"
        "  cat / read <file>    — Preview file contents\n"
        "  pwd                  — Show current directory path\n"
        "  find <name>          — Search for files across The Compound\n"
        "  say <message>        — Speak to everyone in the room\n"
        "  tell <who> <msg>     — Send a private message\n"
        "  who                  — List connected players + locations\n"
        "  status <text>        — Set what you're working on\n"
        "  projects             — See active directories + occupancy\n"
        "  warp <dir_id>        — Jump to any directory instantly\n"
        "  note <message>       — Pin a note to the room board\n"
        "  notes                — Read the room's note board\n"
        "  examine <target>     — Inspect a file or player\n"
        "  clear                — Clear your screen\n"
        "  help (?)             — Show this help\n"
        "  quit                 — Leave the workspace"
    )


def _render_operational_board(player: Player, world: World) -> str:
    board = load_board(getattr(world, "board_path", None))
    return render_board(board, player.name, _online_players(world))


def _online_players(world: World) -> list[str]:
    return [p.name for p in getattr(world, "players", {}).values()]


def _parse_done_args(args: str) -> tuple[str | None, str]:
    if " -- " in args:
        title, note = args.split(" -- ", 1)
        return title.strip(), note.strip()
    if " - " in args:
        title, note = args.split(" - ", 1)
        return title.strip(), note.strip()
    return None, args.strip()


def _parse_blocked_args(args: str) -> tuple[str, str]:
    text = args.strip()
    if text.lower().startswith("on "):
        text = text[3:].strip()
    title, reason = _parse_optional_note(text)
    return title, reason


def _parse_optional_note(args: str) -> tuple[str, str]:
    if " -- " in args:
        title, note = args.split(" -- ", 1)
        return title.strip(), note.strip()
    if " - " in args:
        title, note = args.split(" - ", 1)
        return title.strip(), note.strip()
    return args.strip(), ""


def _parse_promote_args(args: str) -> str:
    text = args.strip()
    lowered = text.lower()
    for suffix in (" to idea", " to ideas"):
        if lowered.endswith(suffix):
            return text[: -len(suffix)].strip()
    return text


def _parse_target_message(args: str) -> tuple[str, str]:
    parts = args.strip().split(None, 1)
    if len(parts) < 2:
        return args.strip(), ""
    return parts[0].strip(), parts[1].strip()


def _other_radio_person(thread: dict, actor: str) -> str:
    sender = thread.get("from", "")
    target = thread.get("to", "")
    if sender.lower() == actor.lower():
        return target
    return sender


def _notify_radio(world: World, sender: Player, target_name: str, message: str):
    if not target_name:
        return
    target = getattr(world, "players", {}).get(target_name.lower())
    if target and target is not sender:
        target.send(message)


def _trigger_sync():
    try:
        vault_sync()
    except Exception:
        pass


def _world_root(world: World) -> Path:
    return Path(getattr(world, "root", Path(__file__).parent.parent))


def _log_board_event(world: World, event_type: str, player: Player, data: dict):
    logger = getattr(world, "log_board_event", None)
    if callable(logger):
        logger(event_type, player.name, data)


def _log_radio_event(world: World, event_type: str, player: Player, data: dict):
    logger = getattr(world, "log_radio_event", None)
    if callable(logger):
        logger(event_type, player.name, data)
