import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "engine"
sys.path.insert(0, str(ENGINE))


class AgentBriefingTests(unittest.TestCase):
    def test_profile_briefings_name_the_correct_worktree_branch_and_port(self):
        from agent_briefing import briefing_for_actor

        trey = briefing_for_actor("Trey")
        joe = briefing_for_actor("Joe")

        self.assertEqual(trey["actor"], "Trey")
        self.assertEqual(trey["worktree_path"], r"D:\The_Compound_Worktrees\Trey")
        self.assertEqual(trey["branch"], "trey/workspace")
        self.assertEqual(trey["dev_port"], 8766)
        self.assertEqual(trey["live_port"], 8765)
        self.assertIn("git push", trey["agent_prompt"])
        self.assertIn("merge conflicts", trey["agent_prompt"].lower())

        self.assertEqual(joe["actor"], "Joe")
        self.assertEqual(joe["worktree_path"], r"D:\The_Compound_Worktrees\Joe")
        self.assertEqual(joe["branch"], "joe/workspace")
        self.assertEqual(joe["dev_port"], 8767)
        self.assertEqual(joe["live_port"], 8765)

    def test_server_payload_exposes_agent_briefing(self):
        import server

        payload = server.agent_briefing_payload("Joe")

        self.assertEqual(payload["briefing"]["actor"], "Joe")
        self.assertEqual(payload["briefing"]["branch"], "joe/workspace")
        self.assertIn("D:\\The_Compound", payload["briefing"]["live_path"])

    def test_hud_contains_agent_briefing_hooks(self):
        html = (ROOT / "engine" / "static" / "index.html").read_text(encoding="utf-8")

        self.assertIn('data-testid="agent-brief-button"', html)
        self.assertIn('data-testid="agent-brief-overlay"', html)
        self.assertIn("/api/agent-briefing", html)
        self.assertIn("showAgentBriefing", html)

    def test_docs_and_dev_scripts_are_easy_to_find_and_port_safe(self):
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        vault = (ROOT / "vault" / "03_SHARED" / "AGENT_BRIEFING.md").read_text(encoding="utf-8")
        trey_cmd = (ROOT / "Start_Trey_Dev_Compound.cmd").read_text(encoding="utf-8")
        joe_cmd = (ROOT / "Start_Joe_Dev_Compound.cmd").read_text(encoding="utf-8")
        ps1 = (ROOT / "scripts" / "Start-WorktreeDev.ps1").read_text(encoding="utf-8")

        for text in (agents, vault):
            self.assertIn(r"D:\The_Compound_Worktrees\Trey", text)
            self.assertIn(r"D:\The_Compound_Worktrees\Joe", text)
            self.assertIn("trey/workspace", text)
            self.assertIn("joe/workspace", text)
            self.assertIn("conflict", text.lower())

        self.assertIn("8766", trey_cmd)
        self.assertIn("8767", joe_cmd)
        self.assertIn("MUD_PORT", ps1)
        self.assertNotIn("MUD_PORT=8765", ps1)


if __name__ == "__main__":
    unittest.main()
