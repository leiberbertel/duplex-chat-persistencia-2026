"""Pruebas de integración del socket del chat (Integrante 1).

Usan el TestClient de FastAPI: abre WebSockets reales contra la app en memoria.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client():
    with TestClient(create_app()) as c:  # `with` => un solo event loop compartido
        yield c


def login(ws, username: str) -> dict:
    ws.send_json({"type": "login", "username": username})
    return ws.receive_json()


def receive_until(ws, type_: str, max_events: int = 10) -> dict:
    """Lee eventos hasta encontrar uno del tipo indicado (ignora info/users intermedios)."""
    for _ in range(max_events):
        event = ws.receive_json()
        if event["type"] == type_:
            return event
    raise AssertionError(f"No llegó un evento '{type_}'")


def test_health(client):
    assert client.get("/health").json()["status"] == "ok"


def test_login_devuelve_lista_de_conectados(client):
    with client.websocket_connect("/ws") as a:
        welcome = login(a, "poli01")
        assert welcome == {**welcome, "type": "welcome", "username": "poli01", "users": []}

        with client.websocket_connect("/ws") as b:
            welcome_b = login(b, "poli02")
            assert welcome_b["users"] == ["poli01"]
            # poli01 recibe aviso y lista actualizada
            assert receive_until(a, "users")["users"] == ["poli02"]


def test_primer_mensaje_debe_ser_login(client):
    with client.websocket_connect("/ws") as ws:
        ws.send_json({"type": "list_users"})
        assert ws.receive_json()["type"] == "error"


def test_usuario_duplicado_rechazado(client):
    with client.websocket_connect("/ws") as a:
        login(a, "poli01")
        with client.websocket_connect("/ws") as dup:
            event = login(dup, "poli01")
            assert event["type"] == "error"
            assert "ya está conectado" in event["detail"]


def test_nombre_invalido(client):
    with client.websocket_connect("/ws") as ws:
        assert login(ws, "a b")["type"] == "error"


def test_chat_bidireccional_y_chao(client):
    with client.websocket_connect("/ws") as a, client.websocket_connect("/ws") as b:
        login(a, "poli01")
        login(b, "poli02")

        a.send_json({"type": "select", "username": "poli02"})
        assert receive_until(a, "partner_selected")["username"] == "poli02"
        # poli02 queda emparejado automáticamente con poli01
        assert receive_until(b, "partner_selected")["username"] == "poli01"

        a.send_json({"type": "message", "text": "hola poli02"})
        msg = receive_until(b, "message")
        assert msg["from"] == "poli01" and msg["text"] == "hola poli02"

        b.send_json({"type": "message", "text": "hola poli01"})
        msg = receive_until(a, "message")
        assert msg["from"] == "poli02" and msg["text"] == "hola poli01"

        a.send_json({"type": "message", "text": "chao"})
        assert receive_until(b, "message")["text"] == "chao"
        assert receive_until(a, "bye")["type"] == "bye"

        estados = {u["username"]: u["estado"] for u in client.get("/api/usuarios").json()}
        assert estados == {"poli01": "abandonó", "poli02": "conectado"}
        assert client.get("/api/usuarios/conectados").json() == ["poli02"]

        # poli02 ya no tiene interlocutor
        b.send_json({"type": "message", "text": "¿sigues ahí?"})
        assert receive_until(b, "error")["detail"].startswith("Primero elige")


def test_mensaje_sin_interlocutor(client):
    with client.websocket_connect("/ws") as a:
        login(a, "poli01")
        a.send_json({"type": "message", "text": "hola"})
        assert a.receive_json()["type"] == "error"


def test_seleccionar_usuario_inexistente(client):
    with client.websocket_connect("/ws") as a:
        login(a, "poli01")
        a.send_json({"type": "select", "username": "fantasma"})
        assert "no está conectado" in a.receive_json()["detail"]


def test_json_invalido_no_tumba_la_sesion(client):
    with client.websocket_connect("/ws") as a:
        login(a, "poli01")
        a.send_text("esto no es json")
        assert a.receive_json()["type"] == "error"
        a.send_json({"type": "list_users"})
        event = a.receive_json()
        assert event["type"] == "users" and event["users"] == []


def test_reconexion_tras_chao(client):
    with client.websocket_connect("/ws") as a:
        login(a, "poli01")
        a.send_json({"type": "message", "text": "CHAO"})
        assert a.receive_json()["type"] == "bye"
    with client.websocket_connect("/ws") as a2:
        assert login(a2, "poli01")["type"] == "welcome"
