"""Pruebas del cliente — RESPONSABLE: INTEGRANTE 2.

Se omiten mientras el cliente no esté implementado. Al terminarlo, quite el
`skip` y complete los casos.
"""

import pytest

from client.cli import build_url, parse_input, render_event


def test_build_url():
    assert build_url("127.0.0.1", 8000) == "ws://127.0.0.1:8000/ws"


def test_parse_input_comandos():
    assert parse_input("/usuarios") == {"type": "list_users"}
    assert parse_input("/con poli01") == {"type": "select", "username": "poli01"}
    assert parse_input("hola") == {"type": "message", "text": "hola"}
    assert parse_input("   ") is None


def test_render_message():
    event = {"type": "message", "from": "poli01", "text": "hola", "timestamp": "..."}
    assert "poli01" in render_event(event) and "hola" in render_event(event)
