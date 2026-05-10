"""Profile-specific agent briefing for Compound worktree development."""

from __future__ import annotations

from copy import deepcopy


LIVE_PATH = r"D:\The_Compound"
LIVE_PORT = 8765
REMOTE_URL = "http://100.87.143.16:8765"

PROFILE_BRIEFINGS = {
    "Trey": {
        "actor": "Trey",
        "worktree_path": r"D:\The_Compound_Worktrees\Trey",
        "branch": "trey/workspace",
        "dev_port": 8766,
    },
    "Joe": {
        "actor": "Joe",
        "worktree_path": r"D:\The_Compound_Worktrees\Joe",
        "branch": "joe/workspace",
        "dev_port": 8767,
    },
}


def normalize_actor(actor: str | None) -> str:
    return "Joe" if str(actor or "").strip().lower() == "joe" else "Trey"


def briefing_for_actor(actor: str | None) -> dict:
    profile = normalize_actor(actor)
    briefing = deepcopy(PROFILE_BRIEFINGS[profile])
    briefing["live_path"] = LIVE_PATH
    briefing["live_port"] = LIVE_PORT
    briefing["remote_url"] = REMOTE_URL
    briefing["dev_url"] = f"http://127.0.0.1:{briefing['dev_port']}"
    briefing["agent_prompt"] = render_agent_prompt(briefing)
    briefing["merge_steps"] = merge_steps(briefing)
    briefing["conflict_rules"] = conflict_rules()
    return briefing


def merge_steps(briefing: dict) -> list[str]:
    branch = briefing["branch"]
    return [
        "Commit only intentional source/docs/test changes from your worktree.",
        f"Run `git push origin {branch}` from the worktree.",
        "Open or request a PR from your workspace branch into `master`.",
        "Before merging, update from `master` and rerun the relevant tests.",
        "After merge, pull `master` into `D:\\The_Compound` and restart the live server if needed.",
    ]


def conflict_rules() -> list[str]:
    return [
        "Do not edit from `D:\\The_Compound` unless the task is a live hotfix.",
        "If a conflict happens, stop and inspect both sides before choosing.",
        "Never overwrite the other operator's branch to make a conflict disappear.",
        "Resolve conflicts in the worktree, rerun tests, then commit the resolution.",
        "Keep generated runtime state out of commits unless Trey explicitly asks for it.",
    ]


def render_agent_prompt(briefing: dict) -> str:
    return "\n".join(
        [
            f"You are working on The Compound as {briefing['actor']}.",
            "",
            "Use this worktree and branch:",
            f"- Worktree: `{briefing['worktree_path']}`",
            f"- Branch: `{briefing['branch']}`",
            f"- Dev HUD: `http://127.0.0.1:{briefing['dev_port']}`",
            "",
            "Keep the live shared Compound running separately:",
            f"- Live app: `{LIVE_PATH}`",
            f"- Live HUD: `http://127.0.0.1:{LIVE_PORT}` or `{REMOTE_URL}`",
            "",
            "Daily coding loop:",
            f"1. `cd {briefing['worktree_path']}`",
            "2. `git fetch origin`",
            "3. `git merge --ff-only origin/master` before starting new work",
            "4. Run tests before and after changes",
            "5. Commit focused changes",
            f"6. `git push origin {briefing['branch']}`",
            "7. Merge to `master` only after review/checks",
            "",
            "Conflict handling:",
            "- Treat merge conflicts as shared decisions, not speed bumps.",
            "- Read both versions, keep intentional work from both sides, rerun tests.",
            "- If the right resolution is not obvious, ask Trey/Joe before committing.",
        ]
    )


def render_markdown() -> str:
    sections = ["# Compound Agent Briefing", ""]
    for actor in ("Trey", "Joe"):
        briefing = briefing_for_actor(actor)
        sections.extend(
            [
                f"## {actor}",
                "",
                f"- Worktree: `{briefing['worktree_path']}`",
                f"- Branch: `{briefing['branch']}`",
                f"- Dev HUD: `{briefing['dev_url']}`",
                f"- Live HUD stays on: `http://127.0.0.1:{LIVE_PORT}` / `{REMOTE_URL}`",
                "",
            ]
        )
    sections.extend(
        [
            "## Merge And Conflict Rules",
            "",
            *[f"- {step}" for step in merge_steps(briefing_for_actor("Trey"))],
            "",
            "## Conflict Rules",
            "",
            *[f"- {rule}" for rule in conflict_rules()],
            "",
        ]
    )
    return "\n".join(sections)
