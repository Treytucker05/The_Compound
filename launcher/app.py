"""
app.py — Main launcher window for the COMPOUND_APPROACH Portal.

A dark-themed tkinter GUI that acts as air traffic control:
- Switch profiles (Joseph / Trey / Shared)
- Start/Stop the MUD engine
- Open Obsidian vault or browser client
- View live engine logs
"""

import os
import sys
from pathlib import Path
from tkinter import messagebox

import tkinter as tk

# Ensure root is on path so we can import sibling modules
ROOT = Path(__file__).parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from launcher.profiles import get_profile, list_profile_keys, load_profiles
from launcher.services import EngineService
from launcher.widgets import COLORS, FONTS, ActionButton, DarkFrame, LogViewer, StatusCard


class PortalApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root_dir = Path(__file__).parent.parent
        self.service = EngineService(self.root_dir)
        self.service.on_output(self._on_engine_output)
        self.auto_launch_enabled = os.environ.get("PORTAL_AUTO_LAUNCH", "1").strip() not in {"0", "false", "False", "no", "NO"}
        self._auto_launch_fired = False

        self.profiles = load_profiles(self.root_dir / "data")
        self.current_profile_key = "shared"
        self.profile = get_profile(self.root_dir / "data", self.current_profile_key)

        self.root.title("COMPOUND_APPROACH — Portal")
        self.root.geometry("900x700")
        self.root.configure(bg=COLORS["bg"])
        self.root.minsize(700, 500)

        # Try to set window icon
        icon_path = Path(__file__).parent / "assets" / "portal.ico"
        if icon_path.exists():
            try:
                self.root.iconbitmap(str(icon_path))
            except Exception:
                pass

        self._build_ui()
        self._update_status_loop()
        self.root.after(600, self._maybe_auto_launch)

    def _build_ui(self):
        # Main container with padding
        container = tk.Frame(self.root, bg=COLORS["bg"])
        container.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)

        # ===== Header =====
        header = tk.Frame(container, bg=COLORS["bg"])
        header.pack(fill=tk.X, pady=(0, 12))

        tk.Label(header, text="COMPOUND_APPROACH", bg=COLORS["bg"], fg=COLORS["text"],
                 font=("Courier New", 16, "bold")).pack(side=tk.LEFT)

        tk.Label(header, text="Portal", bg=COLORS["bg"], fg=COLORS["accent_default"],
                 font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=(8, 0))

        # ===== Profile Selector =====
        profile_frame = DarkFrame(container)
        profile_frame.pack(fill=tk.X, pady=(0, 12))

        tk.Label(profile_frame, text="ACTIVE PROFILE", bg=COLORS["bg_card"], fg=COLORS["text_dim"],
                 font=FONTS["status"]).pack(anchor="w", padx=10, pady=(8, 4))

        btn_row = tk.Frame(profile_frame, bg=COLORS["bg_card"])
        btn_row.pack(fill=tk.X, padx=10, pady=(0, 8))

        self.profile_buttons = {}
        for key in list_profile_keys(self.root_dir / "data"):
            prof = get_profile(self.root_dir / "data", key)
            accent = prof.get("accent", COLORS["accent_default"]) if prof else COLORS["accent_default"]
            btn = ActionButton(btn_row, text=prof["name"] if prof else key, accent=accent,
                               command=lambda k=key: self._set_profile(k))
            btn.pack(side=tk.LEFT, padx=(0, 8))
            self.profile_buttons[key] = btn

        # ===== Status Cards =====
        cards_frame = tk.Frame(container, bg=COLORS["bg"])
        cards_frame.pack(fill=tk.X, pady=(0, 12))
        cards_frame.columnconfigure(0, weight=1)
        cards_frame.columnconfigure(1, weight=1)
        cards_frame.columnconfigure(2, weight=1)

        self.card_engine = StatusCard(cards_frame, "Engine Status", "STOPPED", COLORS["error"])
        self.card_engine.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        self.card_profile = StatusCard(cards_frame, "Profile", self.profile["name"] if self.profile else "—",
                                       self.profile.get("accent", COLORS["accent_default"]) if self.profile else COLORS["accent_default"])
        self.card_profile.grid(row=0, column=1, sticky="nsew", padx=(0, 8))

        self.card_activity = StatusCard(cards_frame, "Recent Activity", "—")
        self.card_activity.grid(row=0, column=2, sticky="nsew")

        # ===== Action Buttons =====
        actions_frame = tk.Frame(container, bg=COLORS["bg"])
        actions_frame.pack(fill=tk.X, pady=(0, 12))

        self.btn_start = ActionButton(actions_frame, "▶  Start Engine", self._start_engine, COLORS["success"])
        self.btn_start.pack(side=tk.LEFT, padx=(0, 8))

        self.btn_stop = ActionButton(actions_frame, "■  Stop Engine", self._stop_engine, COLORS["error"])
        self.btn_stop.pack(side=tk.LEFT, padx=(0, 8))
        self.btn_stop.config(state=tk.DISABLED)

        self.btn_portal = ActionButton(actions_frame, "⎈  Launch Portal", self._launch_portal, COLORS["accent_default"])
        self.btn_portal.pack(side=tk.LEFT, padx=(0, 8))

        self.btn_vault = ActionButton(actions_frame, "📂  Open Vault", self._open_vault, COLORS["accent_default"])
        self.btn_vault.pack(side=tk.LEFT, padx=(0, 8))

        self.btn_client = ActionButton(actions_frame, "🌐  Open Client", self._open_client, COLORS["accent_default"])
        self.btn_client.pack(side=tk.LEFT, padx=(0, 8))

        # ===== Log Viewer =====
        log_frame = DarkFrame(container)
        log_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(log_frame, text="ENGINE LOG", bg=COLORS["bg_card"], fg=COLORS["text_dim"],
                 font=FONTS["status"]).pack(anchor="w", padx=10, pady=(8, 4))

        self.log = LogViewer(log_frame, height=20)
        self.log.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 8))

        # ===== Footer =====
        footer = tk.Frame(container, bg=COLORS["bg"])
        footer.pack(fill=tk.X, pady=(8, 0))

        self.footer_label = tk.Label(footer, text="Ready.", bg=COLORS["bg"], fg=COLORS["text_dim"],
                                     font=FONTS["status"])
        self.footer_label.pack(side=tk.LEFT)

        # Highlight current profile button
        self._highlight_profile_button()

    def _set_profile(self, key: str):
        self.current_profile_key = key
        self.profile = get_profile(self.root_dir / "data", key)
        self._highlight_profile_button()
        if self.profile:
            self.card_profile.set_value(self.profile["name"], self.profile.get("accent", COLORS["accent_default"]))
            self.footer_label.config(text=f"Profile switched to {self.profile['name']}. {self.profile.get('status', '')}")
        self.log.append(f"[PROFILE] Switched to {key}", "system")

    def _highlight_profile_button(self):
        for key, btn in self.profile_buttons.items():
            prof = get_profile(self.root_dir / "data", key)
            accent = prof.get("accent", COLORS["accent_default"]) if prof else COLORS["accent_default"]
            if key == self.current_profile_key:
                btn.config(bg=COLORS["border"], fg=accent)
            else:
                btn.config(bg=COLORS["bg_input"], fg=accent)

    def _start_engine(self):
        self.log.append("[LAUNCHER] Running preflight checks...", "system")
        preflight_errors = self.service.preflight()
        if preflight_errors:
            for err in preflight_errors:
                self.log.append(f"[PREFLIGHT] {err}", "error")
            self.footer_label.config(text="Preflight failed — see log for details.")
            return

        self.log.append("[LAUNCHER] Preparing quickstart workspace...", "system")
        for message in self.service.bootstrap_quickstart():
            self.log.append(f"[BOOTSTRAP] {message}", "info")

        self.log.append("[LAUNCHER] Preflight passed. Starting engine...", "system")
        ok = self.service.start()
        if ok:
            self.log.append("[LAUNCHER] Engine started.", "success")
            self.footer_label.config(text="Engine running on ws://0.0.0.0:8765")
            self.btn_start.config(state=tk.DISABLED)
            self.btn_stop.config(state=tk.NORMAL)
            self.card_engine.set_value("RUNNING", COLORS["success"])
        else:
            self.log.append("[LAUNCHER] Engine failed to start.", "error")
            self.footer_label.config(text="Engine failed to start.")

    def _launch_portal(self):
        """One-click launch: ensure engine, open client HUD, then open vault."""
        if not self.service.is_running():
            self._start_engine()
        if self.service.is_running():
            self.log.append("[LAUNCHER] Launching portal surfaces...", "system")
            self.root.after(300, self._open_client)
            self.root.after(700, self._open_vault)
            self.footer_label.config(text="Portal launched: HUD + Vault + Engine.")

    def _maybe_auto_launch(self):
        """Auto-launch onboarding flow so running the launcher is enough for first-time users."""
        if self._auto_launch_fired:
            return
        self._auto_launch_fired = True
        if not self.auto_launch_enabled:
            return
        self.log.append("[LAUNCHER] Auto-launching portal onboarding flow...", "system")
        self._launch_portal()

    def _stop_engine(self):
        self.log.append("[LAUNCHER] Stopping engine...", "system")
        ok = self.service.stop()
        if ok:
            self.log.append("[LAUNCHER] Engine stopped.", "warn")
            self.footer_label.config(text="Engine stopped.")
            self.btn_start.config(state=tk.NORMAL)
            self.btn_stop.config(state=tk.DISABLED)
            self.card_engine.set_value("STOPPED", COLORS["error"])
        else:
            self.log.append("[LAUNCHER] Engine stop failed.", "error")

    def _open_vault(self):
        result = self.service.open_vault()
        if result == "obsidian":
            self.log.append("[LAUNCHER] Opened vault in Obsidian.", "success")
            self.footer_label.config(text="Vault opened in Obsidian.")
        elif result == "explorer":
            self.log.append("[LAUNCHER] Opened vault folder (Obsidian not found).", "warn")
            self.footer_label.config(text="Vault folder opened (Obsidian not found).")
        else:
            self.log.append("[LAUNCHER] Could not open vault.", "error")
            self.footer_label.config(text="Could not open vault.")

    def _open_client(self):
        self.service.open_client()
        self.log.append("[LAUNCHER] Opened browser client.", "info")
        self.footer_label.config(text="Browser client opened at http://localhost:8765")

    def _on_engine_output(self, lines: list[str]):
        # Called from background thread — schedule on main thread
        for line in lines:
            tag = "info"
            if "error" in line.lower() or "fail" in line.lower():
                tag = "error"
            elif "started" in line.lower() or "running" in line.lower():
                tag = "success"
            elif "warn" in line.lower():
                tag = "warn"
            # Use after() to safely update UI from background thread
            self.root.after(0, lambda l=line, t=tag: self.log.append(l, t))

    def _update_status_loop(self):
        """Periodic UI refresh for engine status and activity."""
        running = self.service.is_running()
        if running:
            self.card_engine.set_value("RUNNING", COLORS["success"])
            self.btn_start.config(state=tk.DISABLED)
            self.btn_stop.config(state=tk.NORMAL)
        else:
            self.card_engine.set_value("STOPPED", COLORS["error"])
            self.btn_start.config(state=tk.NORMAL)
            self.btn_stop.config(state=tk.DISABLED)

        # Try to read recent board activity
        try:
            import json
            board_path = self.root_dir / "data" / "board.json"
            if board_path.exists():
                with open(board_path, "r", encoding="utf-8") as f:
                    board = json.load(f)
                recent = board.get("new", [])
                if recent:
                    last = recent[-1]
                    text = last.get("text", "—")
                    self.card_activity.set_value(text[:40] + ("..." if len(text) > 40 else ""))
                else:
                    self.card_activity.set_value("No recent activity")
        except Exception:
            pass

        self.root.after(2000, self._update_status_loop)

    def on_close(self):
        if self.service.is_running():
            if messagebox.askyesno("Engine Running", "The engine is still running. Stop it and exit?"):
                self.service.stop()
            else:
                return
        self.root.destroy()


def main():
    root = tk.Tk()
    app = PortalApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()


if __name__ == "__main__":
    main()
