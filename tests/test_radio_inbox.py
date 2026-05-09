import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "engine"
sys.path.insert(0, str(ENGINE))

from commands import handle
from radio import ask_question, load_radio, render_inbox, reply_to_thread, resolve_thread
from world import Player
import server


class DummyWorld:
    def __init__(self, radio_path: Path):
        self.radio_path = radio_path
        self.players = {}
        self.events = []

    def log_radio_event(self, event_type: str, player_name: str, data: dict):
        self.events.append((event_type, player_name, data))


class RadioInboxTests(unittest.TestCase):
    def test_ask_question_persists_open_thread_for_recipient(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "radio.json"

            radio, thread = ask_question(path, sender="Trey", target="Joe", text="Can you review the board?")

            self.assertEqual(thread["from"], "Trey")
            self.assertEqual(thread["to"], "Joe")
            self.assertEqual(thread["status"], "open")
            self.assertEqual(thread["messages"][0]["text"], "Can you review the board?")
            reloaded = load_radio(path)
            self.assertEqual(reloaded["threads"][0]["id"], thread["id"])
            self.assertIn("Can you review the board?", render_inbox(reloaded, "Joe"))

    def test_reply_appends_message_and_keeps_thread_open(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "radio.json"
            _, thread = ask_question(path, sender="Trey", target="Joe", text="Need a call?")

            radio, updated = reply_to_thread(path, query=thread["id"], sender="Joe", text="Yes after lunch.")

            self.assertIsNotNone(updated)
            self.assertEqual(updated["status"], "open")
            self.assertEqual(updated["messages"][-1]["from"], "Joe")
            self.assertIn("Yes after lunch.", render_inbox(radio, "Trey"))

    def test_resolve_thread_closes_it_with_note(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "radio.json"
            _, thread = ask_question(path, sender="Joe", target="Trey", text="Where is the launcher?")

            radio, updated = resolve_thread(path, query=thread["id"], actor="Trey", note="Handled in HUD.")

            self.assertIsNotNone(updated)
            self.assertEqual(updated["status"], "resolved")
            self.assertEqual(updated["resolved_by"], "Trey")
            self.assertIn("Handled in HUD.", render_inbox(radio, "Joe", include_resolved=True))

    def test_command_handler_wires_radio_commands_to_world_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "radio.json"
            world = DummyWorld(path)
            trey = Player("Trey")
            joe = Player("Joe")
            world.players = {"trey": trey, "joe": joe}

            ask_result = handle(trey, world, "ask Joe Can you check the vault?")
            self.assertIn("Radio sent to Joe", ask_result)
            thread_id = load_radio(path)["threads"][0]["id"]

            inbox_result = handle(joe, world, "inbox")
            self.assertIn("Can you check the vault?", inbox_result)

            reply_result = handle(joe, world, f"reply {thread_id} Yes, checking now.")
            self.assertIn("Radio reply logged", reply_result)

            resolve_result = handle(trey, world, f"resolve {thread_id} Thanks.")
            self.assertIn("Radio resolved", resolve_result)
            self.assertEqual([event[0] for event in world.events], ["question_sent", "reply_sent", "thread_resolved"])

    def test_radio_api_ask_reply_and_resolve_for_hud(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "radio.json"
            original_radio_path = server.RADIO_PATH
            original_build_pulse_payload = server.build_pulse_payload
            original_log_radio_event = server.log_radio_event
            server.RADIO_PATH = path
            server.build_pulse_payload = lambda: {}
            server.log_radio_event = lambda *args, **kwargs: None
            try:
                status, payload = server.api_ask_radio(
                    {"actor": ["Trey"], "to": ["Joe"], "text": ["Can you check the vault?"]}
                )
                self.assertEqual(status, 200)
                self.assertEqual(payload["radio"]["open_count"], 1)
                self.assertEqual(payload["threads"][0]["from"], "Trey")
                self.assertEqual(payload["threads"][0]["to"], "Joe")
                thread_id = payload["threads"][0]["id"]

                status, payload = server.api_reply_radio(
                    {"actor": ["Joe"], "id": [thread_id], "text": ["Yes, checking now."]}
                )
                self.assertEqual(status, 200)
                self.assertEqual(payload["threads"][0]["latest_from"], "Joe")
                self.assertEqual(payload["threads"][0]["latest_text"], "Yes, checking now.")

                status, payload = server.api_resolve_radio(
                    {"actor": ["Trey"], "id": [thread_id], "note": ["Handled."]}
                )
                self.assertEqual(status, 200)
                self.assertEqual(payload["radio"]["open_count"], 0)
                self.assertEqual(payload["radio"]["resolved_count"], 1)
            finally:
                server.RADIO_PATH = original_radio_path
                server.build_pulse_payload = original_build_pulse_payload
                server.log_radio_event = original_log_radio_event


if __name__ == "__main__":
    unittest.main()
