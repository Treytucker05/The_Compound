"""
services.py — Engine lifecycle management for the COMPOUND_APPROACH Portal.

Handles starting, stopping, and monitoring the WebSocket MUD engine process.
"""

import os
import socket
import subprocess
import sys
import threading
from pathlib import Path


class EngineService:
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.engine_dir = root_dir / "engine"
        self.data_dir = root_dir / "data"
        self.config_dir = root_dir / "config"
        self.process: subprocess.Popen | None = None
        self._stdout_thread: threading.Thread | None = None
        self._stderr_thread: threading.Thread | None = None
        self._on_output: callable = None
        self._running = False

    def _python_can_import(self, python_exe: str | Path, module_name: str) -> bool:
        try:
            result = subprocess.run(
                [str(python_exe), "-c", f"import {module_name}"],
                cwd=str(self.root_dir),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=8,
            )
            return result.returncode == 0
        except Exception:
            return False

    def _engine_python(self) -> str | None:
        """Return a Python runtime that can run the WebSocket engine."""
        candidates: list[str | Path] = [
            self.root_dir / ".python" / "python.exe",
            self.root_dir / ".venv" / "Scripts" / "python.exe",
            Path(sys.executable),
            "python",
        ]

        seen: set[str] = set()
        for candidate in candidates:
            key = str(candidate).lower()
            if key in seen:
                continue
            seen.add(key)
            if isinstance(candidate, Path) and not candidate.exists():
                continue
            if self._python_can_import(candidate, "websockets"):
                return str(candidate)
        return None

    def on_output(self, callback: callable):
        """Register a callback(lines: list[str]) for new stdout/stderr lines."""
        self._on_output = callback

    def is_running(self) -> bool:
        if self.process is None:
            return False
        return self.process.poll() is None

    def preflight(self) -> list[str]:
        """Run startup checks. Returns list of error messages (empty if all clear)."""
        errors = []

        # Check the engine runtime, not just the launcher runtime.
        if self._engine_python() is None:
            errors.append("No Python runtime with 'websockets' is available. Run scripts/setup.bat")

        # Check required files/directories
        required = [
            (self.engine_dir / "server.py", "Engine server.py"),
            (self.engine_dir / "world.py", "Engine world.py"),
            (self.data_dir, "Data directory"),
            (self.root_dir / "vault", "Vault directory"),
        ]
        for path, name in required:
            if not path.exists():
                errors.append(f"{name} missing: {path}")

        # Check write permissions
        for test_dir in [self.data_dir, self.data_dir / "logs"]:
            try:
                test_dir.mkdir(parents=True, exist_ok=True)
                test_file = test_dir / ".write_test"
                test_file.write_text("ok")
                test_file.unlink()
            except Exception as e:
                errors.append(f"Cannot write to {test_dir}: {e}")

        # Check port availability
        port = int(os.environ.get("MUD_PORT", "8765"))
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex(("127.0.0.1", port))
                if result == 0:
                    errors.append(f"Port {port} is already in use. Stop the existing engine first.")
        except Exception as e:
            errors.append(f"Could not check port {port}: {e}")

        return errors

    def start(self) -> bool:
        if self.is_running():
            return True

        env = os.environ.copy()
        env["PYTHONNOUSERSITE"] = "1"
        env["MUD_HOST"] = "0.0.0.0"
        env["MUD_PORT"] = "8765"
        env["NOTES_PATH"] = str(self.data_dir / "notes.json")
        env["BOARD_PATH"] = str(self.data_dir / "board.json")
        env["LOG_DIR"] = str(self.data_dir / "logs")

        # Load .env if present; resolve relative paths against root_dir
        env_path = self.config_dir / ".env"
        if env_path.exists():
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        key, value = line.split("=", 1)
                        val = value.strip()
                        # Resolve relative paths to absolute
                        if key.strip().endswith("_PATH") or key.strip().endswith("_DIR"):
                            p = Path(val)
                            if not p.is_absolute():
                                val = str((self.root_dir / p).resolve())
                        env[key.strip()] = val

        python_exe = self._engine_python()
        if python_exe is None:
            if self._on_output:
                self._on_output(["[LAUNCHER ERROR] No Python runtime with 'websockets' is available."])
            return False

        server_script = self.engine_dir / "server.py"

        try:
            self.process = subprocess.Popen(
                [python_exe, str(server_script)],
                cwd=str(self.root_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=env,
            )
        except Exception as e:
            if self._on_output:
                self._on_output([f"[LAUNCHER ERROR] Failed to start engine: {e}"])
            return False

        self._running = True

        def _reader():
            try:
                for line in self.process.stdout:
                    if not self._running:
                        break
                    if self._on_output:
                        self._on_output([line.rstrip()])
            except Exception as e:
                if self._on_output:
                    self._on_output([f"[LAUNCHER ERROR] Engine output reader failed: {e}"])

        self._stdout_thread = threading.Thread(target=_reader, daemon=True)
        self._stdout_thread.start()
        return True

    def bootstrap_quickstart(self) -> list[str]:
        """Seed first-run board/vault content if needed."""
        if str(self.root_dir) not in sys.path:
            sys.path.insert(0, str(self.root_dir))

        try:
            from engine.quickstart import ensure_quickstart
        except Exception as e:
            return [f"Quickstart bootstrap unavailable: {e}"]

        try:
            result = ensure_quickstart(self.root_dir)
        except Exception as e:
            return [f"Quickstart bootstrap failed: {e}"]

        messages = result.get("messages", []) if isinstance(result, dict) else []
        if not messages:
            messages = ["Quickstart bootstrap finished."]
        if result.get("seeded"):
            messages.insert(0, "Quickstart content seeded.")
        else:
            messages.insert(0, "Quickstart already prepared.")
        return messages

    def stop(self) -> bool:
        if not self.is_running():
            return True
        self._running = False
        try:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=2)
        except Exception as e:
            if self._on_output:
                self._on_output([f"[LAUNCHER ERROR] Failed to stop engine: {e}"])
            return False
        finally:
            self.process = None
        return True

    def open_vault(self):
        """Open the Obsidian vault or the vault folder."""
        vault_dir = self.root_dir / "vault"
        # Try Obsidian first
        obsidian_paths = [
            Path(os.environ.get("LOCALAPPDATA", "")) / "Obsidian" / "Obsidian.exe",
            Path("C:/Program Files/Obsidian/Obsidian.exe"),
            Path("C:/Program Files (x86)/Obsidian/Obsidian.exe"),
        ]
        obsidian_exe = None
        for p in obsidian_paths:
            if p.exists():
                obsidian_exe = p
                break

        if obsidian_exe:
            try:
                subprocess.Popen(
                    [str(obsidian_exe), "--vault", str(vault_dir)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                return "obsidian"
            except Exception as e:
                print(f"[LAUNCHER] Could not open Obsidian: {e}")

        # Fallback to Explorer
        try:
            os.startfile(str(vault_dir))
            return "explorer"
        except Exception as e:
            print(f"[LAUNCHER] Could not open vault folder: {e}")

        return None

    def open_client(self):
        """Open the browser client."""
        import webbrowser
        webbrowser.open("http://localhost:8765")
