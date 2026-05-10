"""
missions.py - Parse the shared mission stack from the vault.
"""

import re
from pathlib import Path


MISSION_RELATIVE_PATH = Path("vault") / "03_SHARED" / "PORTAL_MISSIONS.md"


def load_missions(root: Path | str | None = None) -> list[dict]:
    base = Path(root) if root else Path(__file__).parent.parent
    path = base / MISSION_RELATIVE_PATH
    if not path.exists():
        return []

    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    in_stack = False
    missions = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## "):
            in_stack = stripped.lower() == "## current mission stack"
            continue
        if not in_stack or not stripped:
            continue
        if stripped.startswith("#"):
            break

        title, done = _parse_mission_line(stripped)
        if title:
            missions.append(
                {
                    "id": f"mission-{len(missions) + 1}",
                    "title": title,
                    "done": done,
                    "source": "03_SHARED/PORTAL_MISSIONS.md",
                }
            )
    return missions


def render_missions(missions: list[dict]) -> str:
    lines = ["Current Missions", ""]
    if not missions:
        lines.append("No current missions found in 03_SHARED/PORTAL_MISSIONS.md.")
        return "\n".join(lines)
    for index, mission in enumerate(missions, 1):
        marker = "[x]" if mission.get("done") else "[ ]"
        lines.append(f"{index}. {marker} {mission.get('title', 'Untitled mission')}")
    return "\n".join(lines)


def _parse_mission_line(line: str) -> tuple[str, bool]:
    done = False
    text = line

    task_match = re.match(r"^[-*]\s+\[([ xX])\]\s+(.+)$", text)
    if task_match:
        done = task_match.group(1).lower() == "x"
        text = task_match.group(2)
    else:
        text = re.sub(r"^\d+[.)]\s+", "", text)
        text = re.sub(r"^[-*]\s+", "", text)

    return text.strip(), done
