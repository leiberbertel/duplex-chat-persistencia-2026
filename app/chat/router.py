"""Endpoints del chat: el socket (WebSocket) y una API REST de consulta."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect, status
from pydantic import ValidationError

from .manager import ChatError, ConnectionManager
from .protocol import (
    ByeEvent,
    ChatMessageEvent,
    ChatMessageRequest,
    ErrorEvent,
    ListUsersRequest,
    LoginRequest,
    SelectPartnerRequest,
    UsersEvent,
    parse_client_message,
)

logger = logging.getLogger("duplex.chat")

router = APIRouter()


def _manager(app) -> ConnectionManager:
    return app.state.manager


def _validation_detail(exc: ValidationError) -> str:
    first = exc.errors()[0]
    loc = ".".join(str(p) for p in first.get("loc", ()))
    return f"Mensaje inválido ({loc}): {first.get('msg')}" if loc else f"Mensaje inválido: {first.get('msg')}"


# ---------------------------------------------------------------------------
# Socket del chat
# ---------------------------------------------------------------------------
@router.websocket("/ws")
async def chat_socket(websocket: WebSocket) -> None:
    """Socket servidor. Flujo:

    1. El cliente se conecta y envía `login` con su nombre de usuario.
    2. El servidor lo registra y le devuelve la lista de usuarios conectados.
    3. El cliente elige un interlocutor (`select`) y envía mensajes (`message`).
    4. Al enviar "chao", el servidor lo marca como que abandonó y cierra el socket.
    """
    manager = _manager(websocket.app)
    await websocket.accept()
    client = f"{websocket.client.host}:{websocket.client.port}" if websocket.client else "?"
    logger.info("Nueva conexión desde %s", client)

    # --- 1. Autenticación (primer mensaje obligatorio) ---
    username: str | None = None
    try:
        login = parse_client_message(await websocket.receive_text())
        if not isinstance(login, LoginRequest):
            raise ChatError("El primer mensaje debe ser de tipo 'login'.")
        await manager.register(login.username, websocket)
        username = login.username
    except WebSocketDisconnect:
        return
    except (ValidationError, ChatError) as exc:
        detail = _validation_detail(exc) if isinstance(exc, ValidationError) else str(exc)
        await websocket.send_json(ErrorEvent(detail=detail).to_json())
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        logger.info("Conexión %s rechazada: %s", client, detail)
        return

    logger.info("%s inició sesión desde %s", username, client)

    # --- 2. Bucle de conversación ---
    try:
        while True:
            raw = await websocket.receive_text()
            try:
                msg = parse_client_message(raw)
                if isinstance(msg, ListUsersRequest):
                    await websocket.send_json(
                        UsersEvent(users=manager.connected_usernames(exclude=username)).to_json()
                    )
                elif isinstance(msg, SelectPartnerRequest):
                    await manager.select_partner(username, msg.username)
                elif isinstance(msg, ChatMessageRequest):
                    if msg.is_quit:
                        # Se entrega el "chao" al interlocutor (si hay) antes de salir.
                        try:
                            await manager.relay(username, ChatMessageEvent(sender=username, text=msg.text))
                        except ChatError:
                            pass
                        await websocket.send_json(ByeEvent().to_json())
                        await manager.disconnect(username)
                        await websocket.close()
                        return
                    await manager.relay(username, ChatMessageEvent(sender=username, text=msg.text))
                elif isinstance(msg, LoginRequest):
                    raise ChatError("Ya iniciaste sesión.")
            except ValidationError as exc:
                await websocket.send_json(ErrorEvent(detail=_validation_detail(exc)).to_json())
            except ChatError as exc:
                await websocket.send_json(ErrorEvent(detail=str(exc)).to_json())
    except WebSocketDisconnect:
        await manager.disconnect(username, reason="se desconectó")


# ---------------------------------------------------------------------------
# API REST (consulta / monitoreo)
# ---------------------------------------------------------------------------
@router.get("/api/usuarios", tags=["chat"])
async def listar_usuarios(request: Request) -> list[dict]:
    """Log de usuarios: todos los que han entrado, con su estado actual."""
    return [
        {
            "username": u.username,
            "estado": u.status.value,
            "chateando_con": u.partner,
            "conectado_en": u.connected_at.isoformat(),
            "salio_en": u.left_at.isoformat() if u.left_at else None,
        }
        for u in _manager(request.app).all_users()
    ]


@router.get("/api/usuarios/conectados", tags=["chat"])
async def listar_conectados(request: Request) -> list[str]:
    return _manager(request.app).connected_usernames()
