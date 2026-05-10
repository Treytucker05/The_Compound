import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "engine"
sys.path.insert(0, str(ENGINE))

import commands
import server
from board import load_board
from commands import handle
from sparks import add_spark, load_sparks, open_sparks, promote_spark, render_sparks
from world import Player


class DummyWorld:
    def __init__(
        self,
        root: Path,
        board_path: Path | None = None,
        sparks_path: Path | None = None,
    ):
        self.root = root
        self.board_path = board_path
        self.sparks_path = sparks_path
        self.radio_path = root / "radio.json"
        self.players = {}
        self.board_events = []

    def log_board_event(self, event_type: str, player_name: str, data: dict):
        self.board_events.append((event_type, player_name, data))


class SparkInboxTests(unittest.TestCase):
    def test_add_spark_persists_outside_the_board(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sparks_path = root / "sparks.json"
            board_path = root / "board.json"

            sparks, item = add_spark(sparks_path, "Maybe the map should show active rooms", "Joe")

            self.assertEqual(item["text"], "Maybe the map should show active rooms")
            self.assertEqual(item["status"], "open")
            self.assertEqual(open_sparks(sparks)[0]["id"], item["id"])
            self.assertEqual(load_board(board_path)["columns"]["raw"], [])
            self.assertIn("Spark Inbox", render_sparks(sparks))

    def test_promote_command_moves_a_spark_to_board_ideas(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            board_path = root / "board.json"
            sparks_path = root / "sparks.json"
            _sparks, item = add_spark(sparks_path, "Add shared calendar view", "Trey")
            world = DummyWorld(root, board_path=board_path, sparks_path=sparks_path)
            player = Player("Trey")
            original_vault_sync = commands.vault_sync
            commands.vault_sync = lambda *args, **kwargs: None
            try:
                output = handle(player, world, f"promote {item['id']} to idea")
            finally:
                commands.vault_sync = original_vault_sync

            sparks = load_sparks(sparks_path)
            board = load_board(board_path)
            self.assertEqual(open_sparks(sparks), [])
            self.assertEqual(sparks["items"][0]["status"], "promoted")
            self.assertEqual(board["columns"]["raw"][0]["title"], "Add shared calendar view")
            self.assertIn("Promoted to Ideas", output)
            self.assertEqual([event[0] for event in world.board_events], ["spark_promoted"])

    def test_spark_api_add_promote_and_delete(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            original_board = server.BOARD_PATH
            original_sparks = server.SPARKS_PATH
            original_build_pulse = server.build_pulse_payload
            original_log_board_event = server.log_board_event
            original_sync_board_vault = server.sync_board_vault
            server.BOARD_PATH = root / "board.json"
            server.SPARKS_PATH = root / "sparks.json"
            server.build_pulse_payload = lambda: {}
            server.log_board_event = lambda *args, **kwargs: None
            server.sync_board_vault = lambda: None
            try:
                status, payload = server.api_add_spark({"actor": ["Joe"], "text": ["Maybe add tiny quests"]})
                self.assertEqual(status, 200)
                spark_id = payload["sparks"]["items"][0]["id"]

                status, payload = server.api_promote_spark({"actor": ["Joe"], "id": [spark_id]})
                self.assertEqual(status, 200)
                self.assertEqual(payload["sparks"]["items"][0]["status"], "promoted")
                self.assertEqual(payload["board_payload"]["board"]["columns"]["raw"][0]["title"], "Maybe add tiny quests")

                status, payload = server.api_delete_spark({"id": [spark_id]})
                self.assertEqual(status, 200)
                self.assertEqual(payload["sparks"]["items"], [])
            finally:
                server.BOARD_PATH = original_board
                server.SPARKS_PATH = original_sparks
                server.build_pulse_payload = original_build_pulse
                server.log_board_event = original_log_board_event
                server.sync_board_vault = original_sync_board_vault

    def test_pulse_payload_counts_open_sparks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "vault" / "03_SHARED").mkdir(parents=True)
            add_spark(root / "data" / "sparks.json", "Raw thought one", "Trey")
            add_spark(root / "data" / "sparks.json", "Raw thought two", "Joe")

            original_root = server.ROOT_DIR
            original_board = server.BOARD_PATH
            original_radio = server.RADIO_PATH
            original_sparks = server.SPARKS_PATH
            original_event = server.EVENT_LOG
            server.ROOT_DIR = root
            server.BOARD_PATH = root / "data" / "board.json"
            server.RADIO_PATH = root / "data" / "radio.json"
            server.SPARKS_PATH = root / "data" / "sparks.json"
            server.EVENT_LOG = root / "data" / "logs" / "events.jsonl"
            try:
                pulse = server.build_pulse_payload()
            finally:
                server.ROOT_DIR = original_root
                server.BOARD_PATH = original_board
                server.RADIO_PATH = original_radio
                server.SPARKS_PATH = original_sparks
                server.EVENT_LOG = original_event

            self.assertEqual(pulse["spark_count"], 2)


if __name__ == "__main__":
    unittest.main()
