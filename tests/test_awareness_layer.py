import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "engine"
sys.path.insert(0, str(ENGINE))

import server
import commands
from board import (
    active_items_for_actor,
    add_item,
    block_item,
    blocked_items,
    load_board,
    render_board,
    unblock_item,
)
from commands import handle
from missions import load_missions, render_missions
from radio import ask_question, load_radio, needs_attention_threads, reply_to_thread
from world import Player


class DummyWorld:
    def __init__(self, root: Path, board_path: Path | None = None, radio_path: Path | None = None):
        self.root = root
        self.board_path = board_path
        self.radio_path = radio_path
        self.players = {}
        self.board_events = []

    def log_board_event(self, event_type: str, player_name: str, data: dict):
        self.board_events.append((event_type, player_name, data))


class AwarenessLayerTests(unittest.TestCase):
    def test_radio_needs_attention_tracks_latest_sender(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "radio.json"

            radio, thread = ask_question(path, sender="Trey", target="Joe", text="Can you check the board?")

            self.assertEqual([item["id"] for item in needs_attention_threads(radio, "Joe")], [thread["id"]])
            self.assertEqual(needs_attention_threads(radio, "Trey"), [])

            radio, _updated = reply_to_thread(path, query=thread["id"], sender="Joe", text="Yes, checking now.")

            self.assertEqual([item["id"] for item in needs_attention_threads(radio, "Trey")], [thread["id"]])
            self.assertEqual(needs_attention_threads(radio, "Joe"), [])

    def test_blocked_and_unblocked_board_items_are_persisted_and_rendered(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "board.json"
            _board, item = add_item(path, "Review launch checklist", "Trey")

            board, blocked = block_item(path, item["title"], "needs Joe review", "Trey")

            self.assertIsNotNone(blocked)
            self.assertTrue(blocked["blocked"])
            self.assertEqual(blocked["blocked_reason"], "needs Joe review")
            self.assertEqual(blocked["blocked_by"], "Trey")
            self.assertIn(blocked["id"], [entry["id"] for entry in blocked_items(board)])
            self.assertIn("[BLOCKED: needs Joe review]", render_board(board, "Trey"))

            board, unblocked = unblock_item(path, item["title"], "Joe cleared it", "Joe")

            self.assertIsNotNone(unblocked)
            self.assertFalse(unblocked.get("blocked", False))
            self.assertEqual(unblocked["unblocked_note"], "Joe cleared it")
            self.assertEqual(blocked_items(board), [])

    def test_active_items_for_actor_includes_owned_and_shared_planned_or_in_progress(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "board.json"
            board, trey_owned = add_item(path, "Trey implementation", "Trey")
            board["columns"]["raw"].remove(trey_owned)
            trey_owned["owner"] = "Trey"
            board["columns"]["planned"].append(trey_owned)

            shared = {
                **trey_owned,
                "id": "shared-card",
                "title": "Shared ready card",
                "owner": None,
                "mode": "SHARED",
            }
            board["columns"]["planned"].append(shared)

            joe_owned = {
                **trey_owned,
                "id": "joe-card",
                "title": "Joe implementation",
                "owner": "Joe",
                "mode": "SOLO",
            }
            board["columns"]["in_progress"].append(joe_owned)

            titles = [item["title"] for item in active_items_for_actor(board, "Trey")]

            self.assertEqual(titles, ["Trey implementation", "Shared ready card"])

    def test_plan_and_ready_commands_move_cards_through_board_pipeline(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "board.json"
            _board, item = add_item(path, "Bridge board actions to chat", "Trey")
            world = DummyWorld(Path(tmp), board_path=path)
            player = Player("Trey")
            original_vault_sync = commands.vault_sync
            commands.vault_sync = lambda *args, **kwargs: None
            try:
                plan_output = handle(player, world, f"plan {item['title']}")
                ready_output = handle(player, world, f"ready {item['title']}")
            finally:
                commands.vault_sync = original_vault_sync

            board = load_board(path)
            self.assertEqual(board["columns"]["raw"], [])
            self.assertEqual(board["columns"]["refined"], [])
            self.assertEqual(board["columns"]["planned"][0]["id"], item["id"])
            self.assertIn("Moved to PLAN", plan_output)
            self.assertIn("Moved to READY", ready_output)
            self.assertEqual([event[0] for event in world.board_events], ["task_planned", "task_readied"])

    def test_missions_parse_current_stack_and_command_renders_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mission_path = root / "vault" / "03_SHARED" / "PORTAL_MISSIONS.md"
            mission_path.parent.mkdir(parents=True)
            mission_path.write_text(
                "# Portal Missions\n\n"
                "## Current Mission Stack\n"
                "1. Keep shared board current.\n"
                "2. End each session with next-best-action set.\n\n"
                "## Command Cheatsheet\n"
                "- `board`\n",
                encoding="utf-8",
            )
            world = DummyWorld(root)
            player = Player("Trey")

            missions = load_missions(root)
            rendered = render_missions(missions)
            command_output = handle(player, world, "missions")

            self.assertEqual([mission["title"] for mission in missions], [
                "Keep shared board current.",
                "End each session with next-best-action set.",
            ])
            self.assertIn("Current Missions", rendered)
            self.assertIn("Keep shared board current.", command_output)

    def test_pulse_payload_exposes_awareness_lists(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            board_path = root / "data" / "board.json"
            radio_path = root / "data" / "radio.json"
            mission_path = root / "vault" / "03_SHARED" / "PORTAL_MISSIONS.md"
            mission_path.parent.mkdir(parents=True)
            mission_path.write_text("# Portal Missions\n\n## Current Mission Stack\n1. Keep board current.\n", encoding="utf-8")

            board, item = add_item(board_path, "Ready shared card", "Trey")
            board["columns"]["raw"].remove(item)
            item["mode"] = "SHARED"
            board["columns"]["planned"].append(item)
            from board import save_board
            save_board(board_path, board)
            block_item(board_path, item["title"], "waiting for answer", "Trey")
            ask_question(radio_path, sender="Joe", target="Trey", text="Need your eyes on this.")

            original_root = server.ROOT_DIR
            original_board = server.BOARD_PATH
            original_radio = server.RADIO_PATH
            original_sparks = server.SPARKS_PATH
            original_event = server.EVENT_LOG
            server.ROOT_DIR = root
            server.BOARD_PATH = board_path
            server.RADIO_PATH = radio_path
            server.SPARKS_PATH = root / "data" / "sparks.json"
            server.EVENT_LOG = root / "data" / "logs" / "events.jsonl"
            try:
                pulse = server.build_pulse_payload()
                radio_payload = server.radio_payload("Trey")
            finally:
                server.ROOT_DIR = original_root
                server.BOARD_PATH = original_board
                server.RADIO_PATH = original_radio
                server.SPARKS_PATH = original_sparks
                server.EVENT_LOG = original_event

            self.assertEqual(pulse["active_items"][0]["title"], "Ready shared card")
            self.assertEqual(pulse["blocked_items"][0]["blocked_reason"], "waiting for answer")
            self.assertEqual(pulse["missions"][0]["title"], "Keep board current.")
            self.assertEqual(radio_payload["needs_attention_count"], 1)


if __name__ == "__main__":
    unittest.main()
