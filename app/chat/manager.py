"""Registro de usuarios y enrutamiento de mensajes entre clientes.

El `ConnectionManager` es el corazón del servidor:
  * registra a cada usuario que se conecta (poli01, poli02, ...),
  * lleva el log de usuarios conectados / que abandonaron el chat,
  * empareja a un usuario con el interlocutor que elige,
  * reenvía los mensajes de un cliente a su interlocutor.

Por ahora el estado vive en memoria. En la Entrega 2/3 se puede reemplazar
por un repositorio respaldado en base de datos sin cambiar la interfaz.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Protocol

from .protocol import (
    InfoEvent,
    PartnerSelectedEvent,
    ServerEvent,
    UsersEvent,
    WelcomeEvent,
    now_utc,
)

logger = logging.getLogger("duplex.chat")


class Connection(Protocol):
    """Lo mínimo que el manager necesita de un socket (permite usar fakes en pruebas)."""

    async def send_json(self, data: Any, mode: str = "text") -> None: ...


class UserStatus(str, Enum):
    CONECTADO = "conectado"
    ABANDONO = "abandonó"


class ChatError(Exception):
    """Error de negocio que se reporta al cliente como evento `error`."""


@dataclass
class ChatUser:
    username: str
    connection: Connection | None
    status: UserStatus = UserStatus.CONECTADO
    partner: str | None = None
    connected_at: datetime = field(default_factory=now_utc)
    left_at: datetime | None = None

    @property
    def is_connected(self) -> bool:
        return self.status is UserStatus.CONECTADO


class ConnectionManager:
    def __init__(self) -> None:
        self._users: dict[str, ChatUser] = {}
        self._lock = asyncio.Lock()

    # ------------------------------------------------------------------ consultas
    def get(self, username: str) -> ChatUser | None:
        return self._users.get(username)

    def all_users(self) -> list[ChatUser]:
        return list(self._users.values())

    def connected_usernames(self, exclude: str | None = None) -> list[str]:
        return sorted(
            u.username for u in self._users.values() if u.is_connected and u.username != exclude
        )

    # ------------------------------------------------------------------ ciclo de vida
    async def register(self, username: str, connection: Connection) -> ChatUser:
        """Registra (o reconecta) un usuario. Falla si ya hay una sesión activa con ese nombre."""
        async with self._lock:
            existing = self._users.get(username)
            if existing and existing.is_connected:
                raise ChatError(f"El usuario '{username}' ya está conectado.")
            user = ChatUser(username=username, connection=connection)
            self._users[username] = user
        self.log_connected()
        # Al nuevo usuario se le devuelve el log de conectados; a los demás se les avisa.
        await self.send_to(
            username, WelcomeEvent(username=username, users=self.connected_usernames(exclude=username))
        )
        await self.broadcast(InfoEvent(detail=f"{username} se unió al chat."), exclude=username)
        await self.broadcast_user_list(exclude=username)
        return user

    async def disconnect(self, username: str, reason: str = "abandonó el chat") -> None:
        """Marca al usuario como 'abandonó' y avisa a quienes chateaban con él."""
        async with self._lock:
            user = self._users.get(username)
            if user is None or not user.is_connected:
                return
            user.status = UserStatus.ABANDONO
            user.left_at = now_utc()
            user.connection = None
            user.partner = None
            orphans = [u for u in self._users.values() if u.partner == username]
            for other in orphans:
                other.partner = None
        logger.info("%s %s", username, reason)
        self.log_connected()
        for other in orphans:
            await self.send_to(
                other.username,
                InfoEvent(detail=f"{username} abandonó el chat. Elige otro usuario."),
            )
        await self.broadcast(InfoEvent(detail=f"{username} {reason}."), exclude=username)
        await self.broadcast_user_list()

    # ------------------------------------------------------------------ chat
    async def select_partner(self, username: str, partner: str) -> None:
        """El usuario elige con quién chatear. Si el otro está libre, quedan emparejados."""
        if partner == username:
            raise ChatError("No puedes chatear contigo mismo.")
        async with self._lock:
            me = self._require_connected(username)
            other = self._users.get(partner)
            if other is None or not other.is_connected:
                raise ChatError(f"El usuario '{partner}' no está conectado.")
            me.partner = partner
            auto_paired = other.partner is None
            if auto_paired:
                other.partner = username
        logger.info("%s eligió chatear con %s", username, partner)
        await self.send_to(username, PartnerSelectedEvent(username=partner))
        if auto_paired:
            await self.send_to(partner, PartnerSelectedEvent(username=username))
            await self.send_to(partner, InfoEvent(detail=f"{username} quiere chatear contigo."))
        else:
            await self.send_to(
                partner,
                InfoEvent(detail=f"{username} quiere chatear contigo (usa 'select' para responder)."),
            )

    async def relay(self, sender: str, event: ServerEvent) -> str:
        """Reenvía un evento al interlocutor del remitente. Devuelve el destinatario."""
        me = self._require_connected(sender)
        if me.partner is None:
            raise ChatError("Primero elige un usuario con quien chatear.")
        target = self._users.get(me.partner)
        if target is None or not target.is_connected:
            raise ChatError(f"El usuario '{me.partner}' ya no está conectado.")
        logger.info("[%s -> %s] %s", sender, target.username, getattr(event, "text", ""))
        await self.send_to(target.username, event)
        return target.username

    # ------------------------------------------------------------------ envío
    async def send_to(self, username: str, event: ServerEvent) -> None:
        user = self._users.get(username)
        if user is None or user.connection is None:
            return
        try:
            await user.connection.send_json(event.to_json())
        except Exception:  # socket roto: se limpia en el handler del WebSocket
            logger.warning("No se pudo enviar a %s", username, exc_info=True)

    async def broadcast(self, event: ServerEvent, exclude: str | None = None) -> None:
        for name in self.connected_usernames(exclude=exclude):
            await self.send_to(name, event)

    async def broadcast_user_list(self, exclude: str | None = None) -> None:
        for name in self.connected_usernames(exclude=exclude):
            await self.send_to(name, UsersEvent(users=self.connected_usernames(exclude=name)))

    # ------------------------------------------------------------------ util
    def log_connected(self) -> None:
        """Log del servidor con la lista de clientes conectados (Figura 4 de la guía)."""
        conectados = self.connected_usernames()
        logger.info("Usuarios conectados (%d): %s", len(conectados), ", ".join(conectados) or "-")

    def _require_connected(self, username: str) -> ChatUser:
        user = self._users.get(username)
        if user is None or not user.is_connected:
            raise ChatError("Debes iniciar sesión primero.")
        return user
