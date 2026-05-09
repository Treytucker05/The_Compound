import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "engine"
sys.path.insert(0, str(ENGINE))

import server


class VaultViewerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.vault_dir = Path(self.tmp.name) / "vault"
        self.original_vault_dir = server.VAULT_DIR
        server.VAULT_DIR = self.vault_dir
        self.write_note("03_SHARED/PORTAL_MISSIONS.md", "# Portal Missions\n\n- [ ] Open the room\n")
        self.write_note("03_SHARED/OPERATIONAL_BOARD.md", "# Operational Board\n")
        self.write_note("03_SHARED/PROJECT_MAP.md", "# Project Map\n")
        self.write_note("00_DAILY/QUICKSTART_TODAY.md", "# Quickstart Today\n")
        self.write_note("01_PROJECTS/HUD.md", "# HUD\n")
        self.write_note("02_TREY/README.md", "# Trey\n")
        self.write_note("04_SYSTEM/RUNBOOK.md", "# Runbook\n")
        self.write_note("06_LOGS/events.md", "# Events\n")
        self.write_note("99_ARCHIVE/README.md", "# Archive\n")
        self.write_note("scratch/random.md", "# Random\n")

    def tearDown(self):
        server.VAULT_DIR = self.original_vault_dir
        self.tmp.cleanup()

    def write_note(self, rel_path, content):
        path = self.vault_dir / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def test_vault_index_groups_and_pins_shared_notes(self):
        files = server.build_vault_index()
        paths = [item["path"] for item in files]
        self.assertEqual(paths[:3], [
            "03_SHARED/OPERATIONAL_BOARD.md",
            "03_SHARED/PROJECT_MAP.md",
            "03_SHARED/PORTAL_MISSIONS.md",
        ])
        by_path = {item["path"]: item for item in files}
        self.assertTrue(by_path["03_SHARED/OPERATIONAL_BOARD.md"]["pinned"])
        self.assertEqual(by_path["03_SHARED/OPERATIONAL_BOARD.md"]["group"], "Shared")
        self.assertEqual(by_path["00_DAILY/QUICKSTART_TODAY.md"]["group"], "Daily")
        self.assertEqual(by_path["01_PROJECTS/HUD.md"]["group"], "Projects")
        self.assertEqual(by_path["02_TREY/README.md"]["group"], "Personal")
        self.assertEqual(by_path["04_SYSTEM/RUNBOOK.md"]["group"], "System")
        self.assertEqual(by_path["06_LOGS/events.md"]["group"], "Logs")
        self.assertEqual(by_path["99_ARCHIVE/README.md"]["group"], "Archive")
        self.assertEqual(by_path["scratch/random.md"]["group"], "Other")
        self.assertEqual(by_path["03_SHARED/PORTAL_MISSIONS.md"]["title"], "Portal Missions")
        self.assertIn("B", by_path["03_SHARED/PORTAL_MISSIONS.md"]["size_label"])

    def test_read_vault_markdown_returns_preview_metadata(self):
        status, payload = server.read_vault_markdown("03_SHARED/PORTAL_MISSIONS.md")
        self.assertEqual(status, 200)
        self.assertEqual(payload["title"], "Portal Missions")
        self.assertEqual(payload["folder"], "03_SHARED")
        self.assertEqual(payload["group"], "Shared")
        self.assertIn("- [ ] Open the room", payload["content"])
        self.assertGreater(payload["size"], 0)
        self.assertIn("B", payload["size_label"])


if __name__ == "__main__":
    unittest.main()
