import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "engine"
sys.path.insert(0, str(ENGINE))

import server
from board import add_item, load_board


class VisualBoardTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.board_path = Path(self.tmp.name) / "board.json"
        self.original_board_path = server.BOARD_PATH
        self.original_log_board_event = server.log_board_event
        self.original_sync_board_vault = server.sync_board_vault
        self.original_build_pulse_payload = server.build_pulse_payload
        server.BOARD_PATH = self.board_path
        server.log_board_event = lambda *args, **kwargs: None
        server.sync_board_vault = lambda: None
        server.build_pulse_payload = lambda: {}

    def tearDown(self):
        server.BOARD_PATH = self.original_board_path
        server.log_board_event = self.original_log_board_event
        server.sync_board_vault = self.original_sync_board_vault
        server.build_pulse_payload = self.original_build_pulse_payload
        self.tmp.cleanup()

    def test_update_board_item_persists_planning_fields(self):
        _board, item = add_item(self.board_path, "Build shared room viewer", "Trey")

        status, _payload = server.api_update_board_item(
            {
                "id": [item["id"]],
                "actor": ["Trey"],
                "why": ["So Joe and Trey can see the same workspace."],
                "steps": ["Sketch, build, browser verify."],
                "acceptance": ["Both users can open the same viewer."],
            }
        )

        self.assertEqual(status, 200)
        reloaded = load_board(self.board_path)
        updated = reloaded["columns"]["raw"][0]
        self.assertEqual(updated["why"], "So Joe and Trey can see the same workspace.")
        self.assertEqual(updated["steps"], "Sketch, build, browser verify.")
        self.assertEqual(updated["acceptance"], "Both users can open the same viewer.")

    def test_soft_gate_warns_but_allows_idea_to_move_to_plans(self):
        _board, item = add_item(self.board_path, "Rough idea without details", "Joe")

        status, payload = server.api_move_board_item(
            {"id": [item["id"]], "actor": ["Joe"], "column": ["refined"]}
        )

        self.assertEqual(status, 200)
        planned_item = payload["board"]["columns"]["refined"][0]
        self.assertEqual(planned_item["id"], item["id"])
        self.assertEqual(planned_item["gate_status"]["state"], "needs_info")
        self.assertIn("why", planned_item["gate_status"]["missing"])

    def test_delete_board_item_removes_card_and_records_news(self):
        _board, item = add_item(self.board_path, "Delete me", "Trey")

        status, payload = server.api_delete_board_item({"id": [item["id"]], "actor": ["Trey"]})

        self.assertEqual(status, 200)
        self.assertEqual(payload["board"]["columns"]["raw"], [])
        self.assertIn("deleted", payload["board"]["new"][-1]["text"].lower())


if __name__ == "__main__":
    unittest.main()
