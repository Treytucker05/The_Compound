r"""
world.py — COMPOUND_APPROACH Filesystem World Engine
Track B — MUD World Engine
The world mirrors C:\COMPOUND_APPROACH. Directories are rooms, files are artifacts.
"""

import json
import mimetypes
import os
from datetime import datetime, timezone
from pathlib import Path


# Filesystem config
ROOT_PATH = Path(__file__).parent.parent
EXCLUDED_NAMES = {"__pycache__", ".git", ".venv", "venv", "node_modules", ".pytest_cache", ".kimi", ".python"}
EXCLUDED_EXTS = {".pyc", ".pyo", ".log", ".tmp"}
SENSITIVE_NAME_MARKERS = (
    ".env",
    "api key",
    "apikey",
    "credential",
    "password",
    "private key",
    "secret",
    "token",
)
MAX_FILE_PREVIEW = 80  # lines


def is_excluded_entry(path: Path) -> bool:
    name = path.name.lower()
    if path.name in EXCLUDED_NAMES:
        return True
    if path.is_file() and path.suffix.lower() in EXCLUDED_EXTS:
        return True
    return any(marker in name for marker in SENSITIVE_NAME_MARKERS)


class FileItem:
    def __init__(self, path: Path):
        self.path = path
        self.name = path.name
        self._size = path.stat().st_size
        self.mtime = datetime.fromtimestamp(path.stat().st_mtime)
        self.ext = path.suffix.lower()
        self.is_text = self._guess_text()

    def _guess_text(self) -> bool:
        text_exts = {".py", ".md", ".txt", ".json", ".yaml", ".yml", ".html", ".css", ".js", ".ts", ".csv", ".bat", ".ps1", ".cypher"}
        if self.ext in text_exts:
            return True
        mime, _ = mimetypes.guess_type(str(self.path))
        if mime and mime.startswith("text/"):
            return True
        return False

    def format_size(self) -> str:
        size = self._size
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024:
                return f"{size:.1f} {unit}" if isinstance(size, float) else f"{size} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    def preview(self) -> str:
        if not self.is_text:
            return f"[{self.ext or 'bin'}] Binary file — {self.format_size()}"
        try:
            with open(self.path, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
            total = len(lines)
            shown = lines[:MAX_FILE_PREVIEW]
            header = f"[{self.ext or 'txt'}] {self.format_size()} — {total} lines"
            if total > MAX_FILE_PREVIEW:
                header += f" (showing first {MAX_FILE_PREVIEW})"
            body = "".join(shown)
            return f"{header}\n{'='*60}\n{body}\n{'='*60}" if body else header
        except Exception as e:
            return f"Cannot read file: {e}"

    def __repr__(self):
        return f"File({self.name})"


class Directory:
    def __init__(self, dir_id: str, path: Path, parent_id: str = None):
        self.id = dir_id
        self.path = path
        self.name = "The Compound" if path == ROOT_PATH else path.name
        self.parent_id = parent_id
        self.exits = {}  # direction -> dir_id
        self.files = []  # FileItem objects
        self.players = []
        self.notes = []

    def scan(self):
        """Populate exits and files from filesystem."""
        self.exits = {}
        self.files = []

        if self.parent_id is not None:
            self.exits["up"] = self.parent_id

        try:
            entries = sorted(self.path.iterdir(), key=lambda e: (e.is_file(), e.name.lower()))
        except PermissionError:
            return

        for entry in entries:
            if is_excluded_entry(entry):
                continue
            if entry.is_dir():
                dir_id = str(entry.relative_to(ROOT_PATH)).replace("\\", "/")
                # Pick a direction for the subdir
                direction = self._assign_direction(dir_id)
                self.exits[direction] = dir_id
            elif entry.is_file():
                self.files.append(FileItem(entry))

    def _assign_direction(self, dir_id: str) -> str:
        """Assign a direction to a subdirectory deterministically."""
        dirs = ["north", "south", "east", "west", "northeast", "northwest", "southeast", "southwest",
                "in", "out", "left", "right", "forward", "back"]
        h = sum(ord(c) for c in dir_id.lower()) % len(dirs)
        direction = dirs[h]
        while direction in self.exits:
            h = (h + 1) % len(dirs)
            direction = dirs[h]
        return direction

    def look(self) -> str:
        rel = str(self.path.relative_to(ROOT_PATH.parent)) if self.path != ROOT_PATH else "The Compound"
        lines = [f"[ {rel} ]", f"Directory — {len(self.files)} files, {len([e for e in self.exits if e != 'up'])} subdirs", ""]

        if self.exits:
            exits_sorted = sorted(self.exits.items(), key=lambda x: x[0])
            exit_str = ", ".join(f"{d} ({rid})" for d, rid in exits_sorted)
            lines.append(f"Exits: {exit_str}")
        else:
            lines.append("Exits: none")

        if self.files:
            lines.append("")
            lines.append("Files:")
            for f in self.files:
                tag = f.ext.upper()[1:] if f.ext else "???"
                size = f.format_size()
                mtime = f.mtime.strftime("%m/%d %H:%M")
                lines.append(f"  [{tag:4}] {f.name:40} {size:>10}  {mtime}")

        if self.notes:
            lines.append("")
            lines.append(f"  [ {len(self.notes)} note(s) — type 'notes' to read ]")

        if self.players:
            lines.append("")
            for p in self.players:
                status = f" ({p.status})" if p.status else ""
                lines.append(f"  {p.name} is here.{status}")

        return "\n".join(lines)

    def __repr__(self):
        return f"Dir({self.name})"


class Player:
    def __init__(self, name: str, ws=None):
        self.name = name
        self.room = None
        self.ws = ws
        self.status = "observing"

    def prompt(self) -> str:
        return f"{self.name}@compound> "

    def send(self, message: str):
        if self.ws and hasattr(self.ws, "send"):
            try:
                import asyncio
                asyncio.create_task(self.ws.send(message))
            except Exception:
                pass

    def __repr__(self):
        return f"Player({self.name})"


class NPC:
    """Placeholder NPC class for future AI integration (ai_stub.py compatibility)."""
    def __init__(self, name: str, greeting: str = "", dialogue_lines: list = None):
        self.name = name
        self.greeting = greeting
        self.dialogue_lines = dialogue_lines or []
        self._line_index = 0

    def get_next_line(self) -> str:
        if not self.dialogue_lines:
            return f"{self.name} says nothing."
        line = self.dialogue_lines[self._line_index % len(self.dialogue_lines)]
        self._line_index += 1
        return line


class World:
    def __init__(self, root: Path = None, notes_path: Path = None):
        self.root = root or ROOT_PATH
        self.notes_path = notes_path
        self.dirs = {}
        self.players = {}
        self.scan()
        if notes_path:
            self.load_notes()

    def scan(self):
        """Recursively scan ROOT_PATH and build directory rooms."""
        self.dirs = {}
        for dirpath in sorted(self.root.rglob("*")):
            if not dirpath.is_dir():
                continue
            rel = dirpath.relative_to(self.root)
            dir_id = str(rel).replace("\\", "/") if str(rel) != "." else ""
            if any(part in EXCLUDED_NAMES for part in dir_id.split("/")):
                continue
            if dir_id == "":
                parent_id = None
            else:
                parent_id = "/".join(dir_id.split("/")[:-1])
            d = Directory(dir_id, dirpath, parent_id)
            d.scan()
            self.dirs[dir_id] = d

        # Root directory
        root_dir = Directory("", self.root, None)
        root_dir.scan()
        self.dirs[""] = root_dir

        # Resolve exit links (subdirs may not have been scanned yet during first pass)
        for d in self.dirs.values():
            resolved = {}
            for direction, target_id in d.exits.items():
                if target_id in self.dirs:
                    resolved[direction] = target_id
                else:
                    resolved[direction] = None
            d.exits = resolved

    def load_notes(self):
        if not self.notes_path or not self.notes_path.exists():
            return
        try:
            with open(self.notes_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for dir_id, notes in data.items():
                if dir_id in self.dirs:
                    self.dirs[dir_id].notes = notes
        except Exception as e:
            print(f"[WARN] Could not load notes: {e}")

    def save_notes(self):
        if not self.notes_path:
            return
        data = {dir_id: d.notes for dir_id, d in self.dirs.items() if d.notes}
        try:
            tmp_path = self.notes_path.with_suffix(".json.tmp")
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            os.replace(tmp_path, self.notes_path)
        except Exception as e:
            print(f"[WARN] Could not save notes: {e}")

    def get_starting_dir(self) -> Directory:
        return self.dirs.get("", list(self.dirs.values())[0])

    def move_player(self, player: Player, direction: str) -> str:
        if not player.room:
            return "You are nowhere."
        room = player.room
        target_id = room.exits.get(direction)
        if target_id is None or target_id not in self.dirs:
            return "You can't go that way."
        target = self.dirs[target_id]
        room.players.remove(player)
        player.room = target
        target.players.append(player)
        for p in room.players:
            p.send(f"{player.name} leaves {direction}.")
        for p in target.players:
            if p is not player:
                p.send(f"{player.name} arrives from the {self._opposite(direction)}.")
        return target.look()

    def warp_player(self, player: Player, dir_id: str) -> str:
        if dir_id not in self.dirs:
            return f"No such directory: {dir_id}"
        target = self.dirs[dir_id]
        if player.room:
            if player in player.room.players:
                player.room.players.remove(player)
            for p in player.room.players:
                p.send(f"{player.name} vanishes in a swirl of light.")
        player.room = target
        target.players.append(player)
        for p in target.players:
            if p is not player:
                p.send(f"{player.name} materializes in a swirl of light.")
        return target.look()

    @staticmethod
    def _opposite(direction: str) -> str:
        opposites = {
            "north": "south", "south": "north",
            "east": "west", "west": "east",
            "northeast": "southwest", "southwest": "northeast",
            "northwest": "southeast", "southeast": "northwest",
            "up": "down", "down": "up",
        }
        return opposites.get(direction, "unknown")

    def add_player(self, player: Player):
        self.players[player.name.lower()] = player
        starting = self.get_starting_dir()
        player.room = starting
        starting.players.append(player)

    def remove_player(self, player: Player):
        if player.room and player in player.room.players:
            player.room.players.remove(player)
        if player.name.lower() in self.players:
            del self.players[player.name.lower()]

    def broadcast(self, sender: Player, message: str):
        if sender.room:
            for p in sender.room.players:
                if p is not sender:
                    p.send(message)

    def tell(self, sender: Player, target_name: str, message: str) -> str:
        target = self.players.get(target_name.lower())
        if not target:
            return "They're not here."
        target.send(f"{sender.name} tells you, '{message}'")
        return f"You tell {target.name}, '{message}'"

    def who(self) -> str:
        if not self.players:
            return "No one is connected."
        lines = ["Connected players:"]
        for p in self.players.values():
            room_name = p.room.name if p.room else "unknown"
            status = f" ({p.status})" if p.status else ""
            lines.append(f"  {p.name} — {room_name}{status}")
        return "\n".join(lines)

    def projects(self) -> str:
        lines = ["Active directories:"]
        active = [(d.name, d.id, d.players) for d in self.dirs.values() if d.players]
        if not active:
            return "No active directories."
        for name, did, players in active:
            status_list = ", ".join(f"{p.name} ({p.status})" for p in players)
            lines.append(f"  [{did or 'ROOT'}] {name}: {status_list}")
        return "\n".join(lines)
