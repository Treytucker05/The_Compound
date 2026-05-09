import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "engine"
sys.path.insert(0, str(ENGINE))

import server
from world import Directory, Player


class PresencePayloadTests(unittest.TestCase):
    def test_presence_state_includes_room_path_status_and_last_action(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            room_path = root / "vault" / "03_SHARED"
            room_path.mkdir(parents=True)
            room = Directory("03_SHARED", room_path, "03_SHARED")
            player = Player("Joe")
            player.room = room
            player.status = "coding"

            server.record_presence_action(player, "status coding")

            payload = server.presence_entry(player, root / "vault")

        self.assertEqual(payload["name"], "Joe")
        self.assertEqual(payload["room"], "03_SHARED")
        self.assertEqual(payload["room_id"], "03_SHARED")
        self.assertEqual(payload["room_path"], "03_SHARED")
        self.assertEqual(payload["status"], "coding")
        self.assertEqual(payload["last_action"], "status: coding")
        self.assertTrue(payload["last_action_at"])

    def test_presence_action_summary_does_not_expose_message_text_for_chat_commands(self):
        player = Player("Trey")

        server.record_presence_action(player, "tell Joe private note")

        self.assertEqual(player.last_action, "sent a tell")

    def test_failed_navigation_is_not_reported_as_a_move(self):
        with tempfile.TemporaryDirectory() as tmp:
            room = Directory("", Path(tmp), None)
            player = Player("Joe")
            player.room = room

            server.record_presence_action(player, "cd 03_SHARED", previous_room_id="")

        self.assertEqual(player.last_action, "tried to move")


if __name__ == "__main__":
    unittest.main()
