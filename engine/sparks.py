"""
sparks.py - Pre-board Spark Inbox for raw Compound thoughts.

Sparks stay separate from the operational board until someone promotes them
into Ideas.
"""

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_SPARKS_PATH = Path(__file__).parent.parent / "data" / "sparks.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def default_sparks() -> dict:
    now = utc_now()
    return {
        "version": 1,
        "created_at": now,
        "updated_at": now,
        "items": [],
    }


def resolve_sparks_path(path: Path | str | None) -> Path:
    return Path(path) if path else DEFAULT_SPARKS_PATH


def load_sparks(path: Path | str | None = None) -> dict:
    path = resolve_sparks_path(path)
    if not path.exists():
        sparks = default_sparks()
        save_sparks(path, sparks)
        return sparks

    try:
        sparks = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        sparks = default_sparks()

    sparks.setdefault("version", 1)
    sparks.setdefault("created_at", utc_now())
    sparks.setdefault("updated_at", utc_now())
    sparks.setdefault("items", [])
    return sparks


def save_sparks(path: Path | str | None, sparks: dict):
    path = resolve_sparks_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    sparks["updated_at"] = utc_now()
    tmp_path = path.with_suffix(".json.tmp")
    tmp_path.write_text(json.dumps(sparks, indent=2), encoding="utf-8")
    os.replace(tmp_path, path)


def add_spark(path: Path | str | None, text: str, actor: str) -> tuple[dict, dict]:
    sparks = load_sparks(path)
    item = {
        "id": uuid.uuid4().hex[:8],
        "text": text.strip()[:500],
        "created_by": actor,
        "created_at": utc_now(),
        "updated_at": utc_now(),
        "status": "open",
    }
    sparks["items"].append(item)
    save_sparks(path, sparks)
    return sparks, item


def open_sparks(sparks: dict) -> list[dict]:
    return [item for item in sparks.get("items", []) if item.get("status", "open") == "open"]


def find_spark(sparks: dict, query: str) -> dict | None:
    needle = query.strip().lower()
    if not needle:
        return None

    items = open_sparks(sparks)
    for item in items:
        if item.get("id", "").lower().startswith(needle):
            return item
    for item in items:
        if needle in item.get("text", "").lower():
            return item
    return None


def promote_spark(path: Path | str | None, query: str, actor: str) -> tuple[dict, dict | None]:
    sparks = load_sparks(path)
    item = find_spark(sparks, query)
    if not item:
        return sparks, None

    item["status"] = "promoted"
    item["promoted_by"] = actor
    item["promoted_at"] = utc_now()
    item["updated_at"] = utc_now()
    save_sparks(path, sparks)
    return sparks, item


def delete_spark(path: Path | str | None, query: str) -> tuple[dict, dict | None]:
    sparks = load_sparks(path)
    needle = query.strip().lower()
    item = None
    for candidate in sparks.get("items", []):
        if candidate.get("id", "").lower().startswith(needle):
            item = candidate
            break
    if not item:
        item = find_spark(sparks, query)
    if not item:
        return sparks, None

    sparks["items"].remove(item)
    save_sparks(path, sparks)
    return sparks, item


def render_sparks(sparks: dict) -> str:
    lines = ["Spark Inbox"]
    items = open_sparks(sparks)
    if not items:
        lines.append("No open sparks. Use: spark <raw thought>")
        return "\n".join(lines)

    for index, item in enumerate(items, 1):
        actor = item.get("created_by") or "unknown"
        lines.append(f"{index}. [{item.get('id', '')}] {item.get('text', '')} ({actor})")
    lines.append("")
    lines.append("Promote with: promote <spark id or text> to idea")
    return "\n".join(lines)
