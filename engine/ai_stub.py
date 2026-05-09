"""
ai_stub.py — Pluggable AI Interface
Track B — COMPOUND_APPROACH World Engine
Policy: Hard rules first, scripted second, LLM last (Companion Guide §5.2)
Tonight: static scripted responses only.
Future: RemoteLLMBackend via MCP/Tailscale.
"""

from world import NPC, Player


class AIBackend:
    """Base class for NPC AI backends."""

    def respond(self, npc: NPC, player: Player, message: str) -> str:
        raise NotImplementedError

    def greet(self, npc: NPC, player: Player) -> str:
        raise NotImplementedError


class ScriptedBackend(AIBackend):
    """Static dialogue backend — no external dependencies."""

    def respond(self, npc: NPC, player: Player, message: str) -> str:
        return npc.get_next_line()

    def greet(self, npc: NPC, player: Player) -> str:
        return npc.greeting


class RemoteLLMBackend(AIBackend):
    """
    Future backend for remote LLM integration.
    Wires to cousin's laptop via existing MCP/Tailscale path.
    Stub only — not active tonight.
    """

    def __init__(self, endpoint: str = None, api_key: str = None):
        self.endpoint = endpoint
        self.api_key = api_key

    def respond(self, npc: NPC, player: Player, message: str) -> str:
        # TODO: Implement MCP/API call for Phase 2
        return f"[{npc.name} pauses, considering your words...] (LLM not yet wired)"

    def greet(self, npc: NPC, player: Player) -> str:
        return npc.greeting


# Global backend registry — swap this for Phase 2
_current_backend: AIBackend = ScriptedBackend()


def set_backend(backend: AIBackend):
    global _current_backend
    _current_backend = backend


def get_backend() -> AIBackend:
    return _current_backend


def npc_respond(npc: NPC, player: Player, message: str = "") -> str:
    backend = get_backend()
    if message:
        return backend.respond(npc, player, message)
    return backend.greet(npc, player)
