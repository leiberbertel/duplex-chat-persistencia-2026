"""Pruebas unitarias del ConnectionManager con un socket falso (Integrante 1)."""

from __future__ import annotations

import asyncio

import pytest

from app.chat.manager import ChatError, ConnectionManager, UserStatus
from app.chat.protocol import ChatMessageEvent


class FakeConnection:
    def __init__(self) -> None:
        self.sent: list[dict] = []

    async def send_json(self, data, mode: str = "text") -> None:
        self.sent.append(data)

    def types(self) -> list[str]:
        return [e["type"] for e in self.sent]


def run(coro):
    return asyncio.run(coro)


def test_registro_y_log_de_conectados():
    async def scenario():
        m = ConnectionManager()
        a, b = FakeConnection(), FakeConnection()
        await m.register("poli01", a)
        await m.register("poli02", b)
        assert m.connected_usernames() == ["poli01", "poli02"]
        assert a.types()[0] == "welcome" and b.sent[0]["users"] == ["poli01"]
        assert "users" in a.types()

    run(scenario())


def test_no_se_puede_chatear_consigo_mismo():
    async def scenario():
        m = ConnectionManager()
        await m.register("poli01", FakeConnection())
        with pytest.raises(ChatError):
            await m.select_partner("poli01", "poli01")

    run(scenario())


def test_relay_y_desconexion():
    async def scenario():
        m = ConnectionManager()
        a, b = FakeConnection(), FakeConnection()
        await m.register("poli01", a)
        await m.register("poli02", b)
        await m.select_partner("poli01", "poli02")
        assert m.get("poli02").partner == "poli01"

        target = await m.relay("poli01", ChatMessageEvent(sender="poli01", text="hola"))
        assert target == "poli02" and b.sent[-1]["text"] == "hola"

        await m.disconnect("poli01")
        assert m.get("poli01").status is UserStatus.ABANDONO
        assert m.get("poli02").partner is None
        with pytest.raises(ChatError):
            await m.relay("poli02", ChatMessageEvent(sender="poli02", text="?"))

    run(scenario())


def test_no_empareja_si_el_otro_ya_esta_ocupado():
    async def scenario():
        m = ConnectionManager()
        for name in ("poli01", "poli02", "poli03"):
            await m.register(name, FakeConnection())
        await m.select_partner("poli01", "poli02")
        await m.select_partner("poli03", "poli02")
        assert m.get("poli02").partner == "poli01"
        assert m.get("poli03").partner == "poli02"

    run(scenario())
