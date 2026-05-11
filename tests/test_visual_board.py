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

    def test_board_payload_includes_guide_questions_and_prompt_template(self):
        payload = server.board_payload(load_board(self.board_path))

        self.assertIn("guide_templates", payload)
        self.assertIn("guide_prompt_template", payload)
        self.assertIn("why", payload["guide_templates"])
        self.assertIn("steps", payload["guide_templates"])
        self.assertIn("acceptance", payload["guide_templates"])
        self.assertIn(
            "Who is this for: Trey, Joe, or both?",
            payload["guide_templates"]["why"]["questions"],
        )
        self.assertIn("Cut for v1", payload["guide_prompt_template"])

    def test_board_overlay_runs_primary_actions_through_command_chat(self):
        html = (ROOT / "engine" / "static" / "index.html").read_text(encoding="utf-8")

        self.assertIn("function runBoardCommand", html)
        self.assertIn("runCommand(command)", html)
        self.assertIn("function boardCommandForForward", html)
        self.assertIn('data-board-action="command"', html)
        self.assertIn("runBoardCommand(`add ${title}`)", html)
        self.assertIn("return `plan ${title}`", html)
        self.assertIn("return `ready ${title}`", html)
        self.assertIn("return `working on ${title}`", html)
        self.assertIn("return `done ${title} -- completed from board`", html)

    def test_board_overlay_contains_spark_inbox_tab(self):
        html = (ROOT / "engine" / "static" / "index.html").read_text(encoding="utf-8")

        self.assertIn('data-board-panel="sparks"', html)
        self.assertIn('data-board-panel="work"', html)
        self.assertIn('data-testid="spark-list"', html)
        self.assertIn("function fetchSparks", html)
        self.assertIn("function promoteSpark", html)
        self.assertIn("Spark Inbox", html)

    def test_board_panel_hidden_rule_prevents_tab_bleed(self):
        html = (ROOT / "engine" / "static" / "index.html").read_text(encoding="utf-8")

        self.assertIn("#spark-panel[hidden]", html)
        self.assertIn("#board-work-panel[hidden]", html)

    def test_persistent_chat_button_and_dropdown_shell_exist(self):
        html = (ROOT / "engine" / "static" / "index.html").read_text(encoding="utf-8")

        self.assertIn('id="chat-alert"', html)
        self.assertIn('data-testid="chat-alert-button"', html)
        self.assertIn('id="chat-alert-badge"', html)
        self.assertIn('data-testid="chat-alert-badge"', html)
        self.assertIn('id="chat-panel"', html)
        self.assertIn('data-testid="chat-panel"', html)
        self.assertIn('data-testid="chat-thread-list"', html)
        self.assertIn('data-testid="chat-message-input"', html)
        self.assertIn('data-testid="chat-send-button"', html)
        self.assertIn("function toggleChatPanel", html)
        self.assertIn("function closeChatPanel", html)

    def test_chat_dropdown_reads_and_updates_radio_threads(self):
        html = (ROOT / "engine" / "static" / "index.html").read_text(encoding="utf-8")

        self.assertIn("function chatThreadsForActor", html)
        self.assertIn("function renderChatThreads", html)
        self.assertIn("function fetchChatThreads", html)
        self.assertIn("function sendChatMessage", html)
        self.assertIn("function replyChatThread", html)
        self.assertIn("function resolveChatThreadFromChat", html)
        self.assertIn('data-chat-action="reply"', html)
        self.assertIn('data-chat-action="resolve"', html)
        self.assertIn('class="chat-reply-input"', html)
        self.assertIn('radioRequest("/api/radio/ask"', html)
        self.assertIn('radioRequest("/api/radio/reply"', html)
        self.assertIn('radioRequest("/api/radio/resolve"', html)
        self.assertIn('data-chat-action="resolve" data-id="${escapeHtml(thread.id || "")}">Resolve</button>', html)
        self.assertNotIn('data-chat-action="resolve" data-id="${escapeHtml(thread.id || "")}">Ack</button>', html)
        self.assertIn('chatStatusEl.textContent = "Thread resolved."', html)
        self.assertNotIn('chatStatusEl.textContent = "Thread acknowledged."', html)

    def test_chat_button_has_attention_badge_and_reduced_motion_alert(self):
        html = (ROOT / "engine" / "static" / "index.html").read_text(encoding="utf-8")

        self.assertIn("function chatAttentionThreads", html)
        self.assertIn("function chatAttentionKey", html)
        self.assertIn("function updateChatAlert", html)
        self.assertIn("state.chatSeenAttentionKey", html)
        self.assertIn('classList.toggle("is-alerting"', html)
        self.assertIn("#chat-alert-button.is-alerting", html)
        self.assertIn("@keyframes chat-alert-wiggle", html)
        self.assertIn("@keyframes chat-alert-flash", html)
        self.assertIn("@media (prefers-reduced-motion: reduce)", html)

    def test_chat_stays_above_board_and_enter_sends_messages(self):
        html = (ROOT / "engine" / "static" / "index.html").read_text(encoding="utf-8")

        self.assertIn("#chat-alert {\n    position: fixed;\n    top: 18px;\n    right: 18px;\n    z-index: 135;", html)
        self.assertIn("function handleChatComposeKeydown", html)
        self.assertIn("function handleChatThreadKeydown", html)
        self.assertIn('chatMessageInputEl.addEventListener("keydown", handleChatComposeKeydown)', html)
        self.assertIn('chatThreadListEl.addEventListener("keydown", handleChatThreadKeydown)', html)
        self.assertIn('event.key !== "Enter"', html)
        self.assertIn("event.shiftKey", html)
        self.assertIn("await sendChatMessage()", html)
        self.assertIn("await runChatThreadAction(button)", html)

    def test_urgent_chat_button_auto_opens_fullscreen_chat(self):
        html = (ROOT / "engine" / "static" / "index.html").read_text(encoding="utf-8")

        self.assertIn('data-testid="chat-urgent-button"', html)
        self.assertIn('id="chat-urgent-button"', html)
        self.assertIn("#chat-alert.is-urgent-fullscreen", html)
        self.assertIn("const URGENT_PREFIX = \"[URGENT]\";", html)
        self.assertIn("function threadIsUrgent", html)
        self.assertIn("function chatUrgentAttentionKey", html)
        self.assertIn("function setChatFullscreen", html)
        self.assertIn("function openUrgentChatPanel", html)
        self.assertIn("async function sendUrgentChatMessage", html)
        self.assertIn("state.chatSeenUrgentKey", html)
        self.assertIn("sendChatMessage(true)", html)
        self.assertIn("chatUrgentButtonEl.addEventListener", html)
        self.assertIn("openUrgentChatPanel(urgentKey)", html)
        self.assertIn("chatAlertEl.classList.toggle(\"is-urgent-fullscreen\"", html)


if __name__ == "__main__":
    unittest.main()
