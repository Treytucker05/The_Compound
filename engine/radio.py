"""
radio.py - Persistent Radio Inbox for shared questions and handoffs.

The Radio Inbox is deliberately small: one shared JSON file, open/resolved
threads, and plain text rendering for the terminal HUD.
"""

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_RADIO_PATH = Path(__file__).parent.parent / "data" / "radio.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def default_radio() -> dict:
    now = utc_now()
    return {
        "version": 1,
        "created_at": now,
        "updated_at": now,
        "threads": [],
    }


def load_radio(path: Path | str | None = None) -> dict:
    path = resolve_radio_path(path)
    if not path.exists():
        radio = default_radio()
        save_radio(path, radio)
        return radio

    try:
        with open(path, "r", encoding="utf-8") as f:
            radio = json.load(f)
    except json.JSONDecodeError:
        radio = default_radio()

    radio.setdefault("version", 1)
    radio.setdefault("created_at", utc_now())
    radio.setdefault("updated_at", utc_now())
    radio.setdefault("threads", [])
    return radio


def save_radio(path: Path | str | None, radio: dict):
    path = resolve_radio_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    radio["updated_at"] = utc_now()
    tmp_path = path.with_suffix(".json.tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(radio, f, indent=2)
    os.replace(tmp_path, path)


def ask_question(path: Path | str | None, sender: str, target: str, text: str) -> tuple[dict, dict]:
    radio = load_radio(path)
    now = utc_now()
    thread = {
        "id": uuid.uuid4().hex[:8],
        "from": sender.strip(),
        "to": target.strip(),
        "status": "open",
        "created_at": now,
        "updated_at": now,
        "messages": [
            {
                "from": sender.strip(),
                "text": text.strip(),
                "timestamp": now,
            }
        ],
    }
    radio["threads"].append(thread)
    save_radio(path, radio)
    return radio, thread


def reply_to_thread(path: Path | str | None, query: str, sender: str, text: str) -> tuple[dict, dict | None]:
    radio = load_radio(path)
    thread = find_thread(radio, query)
    if not thread:
        return radio, None

    now = utc_now()
    thread.setdefault("messages", []).append(
        {
            "from": sender.strip(),
            "text": text.strip(),
            "timestamp": now,
        }
    )
    thread["updated_at"] = now
    save_radio(path, radio)
    return radio, thread


def resolve_thread(path: Path | str | None, query: str, actor: str, note: str = "") -> tuple[dict, dict | None]:
    radio = load_radio(path)
    thread = find_thread(radio, query)
    if not thread:
        return radio, None

    now = utc_now()
    thread["status"] = "resolved"
    thread["resolved_by"] = actor.strip()
    thread["resolved_at"] = now
    if note.strip():
        thread.setdefault("messages", []).append(
            {
                "from": actor.strip(),
                "text": note.strip(),
                "timestamp": now,
                "kind": "resolution",
            }
        )
    thread["updated_at"] = now
    save_radio(path, radio)
    return radio, thread


def find_thread(radio: dict, query: str) -> dict | None:
    needle = query.strip().lower()
    if not needle:
        return None

    for thread in radio.get("threads", []):
        thread_id = str(thread.get("id", "")).lower()
        if needle == thread_id or thread_id.startswith(needle):
            return thread
    return None


def render_inbox(radio: dict, viewer: str, include_resolved: bool = False) -> str:
    viewer_lower = viewer.lower()
    threads = [
        thread for thread in radio.get("threads", [])
        if include_resolved or thread.get("status") == "open"
    ]
    relevant = [
        thread for thread in threads
        if thread.get("to", "").lower() == viewer_lower or thread.get("from", "").lower() == viewer_lower
    ]

    lines = ["Radio Inbox", ""]
    if not relevant:
        lines.append("No open radio threads.")
        lines.append("")
        lines.append("Use: ask <Trey|Joe> <question>")
        return "\n".join(lines)

    open_count = sum(1 for thread in relevant if thread.get("status") == "open")
    lines.append(f"Open for you or from you: {open_count}")
    lines.append("")
    for thread in relevant[-8:]:
        messages = thread.get("messages", [])
        first = messages[0] if messages else {}
        latest = messages[-1] if messages else {}
        status = thread.get("status", "open").upper()
        lines.append(
            f"#{thread.get('id')} [{status}] {thread.get('from')} -> {thread.get('to')}: "
            f"{first.get('text', '')}"
        )
        if latest is not first and latest.get("text"):
            lines.append(f"  latest from {latest.get('from')}: {latest.get('text')}")
    lines.append("")
    lines.append("Use: reply <id> <message> | resolve <id> <note>")
    return "\n".join(lines)


def summarize_radio(radio: dict) -> dict:
    open_threads = [
        _thread_summary(thread)
        for thread in radio.get("threads", [])
        if thread.get("status") == "open"
    ]
    resolved_count = sum(1 for thread in radio.get("threads", []) if thread.get("status") == "resolved")
    return {
        "open_count": len(open_threads),
        "resolved_count": resolved_count,
        "open_threads": open_threads[-8:],
    }


def needs_attention_threads(radio: dict, actor: str) -> list[dict]:
    return [
        _thread_summary(thread)
        for thread in radio.get("threads", [])
        if thread_needs_attention(thread, actor)
    ]


def thread_needs_attention(thread: dict, actor: str) -> bool:
    actor_lower = actor.strip().lower()
    if not actor_lower or thread.get("status") != "open":
        return False
    participants = {str(thread.get("from", "")).lower(), str(thread.get("to", "")).lower()}
    if actor_lower not in participants:
        return False
    messages = thread.get("messages", [])
    if not messages:
        return False
    latest_from = str(messages[-1].get("from", "")).lower()
    return latest_from != actor_lower


def resolve_radio_path(path: Path | str | None) -> Path:
    if path is None:
        return DEFAULT_RADIO_PATH
    return Path(path)


def _thread_summary(thread: dict) -> dict:
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
    }
