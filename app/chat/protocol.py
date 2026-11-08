"""Protocolo de mensajes del chat (JSON sobre WebSocket).

Todos los mensajes son objetos JSON con un campo `type` que indica su tipo.
La especificación completa, con ejemplos, está en `docs/protocolo.md`.

Cliente -> Servidor:
    login       {"type": "login", "username": "poli01"}
    list_users  {"type": "list_users"}
    select      {"type": "select", "username": "poli02"}
    message     {"type": "message", "text": "hola"}   ("chao" termina la sesión)

Servidor -> Cliente:
    welcome, users, partner_selected, message, info, error, bye
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field, TypeAdapter

# Palabra que el cliente envía para abandonar el chat (requisito de la entrega).
QUIT_WORD = "chao"

USERNAME_PATTERN = r"^[A-Za-z0-9_]{3,20}$"


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


# --------------------------------------------------------------------------
# Mensajes Cliente -> Servidor
# --------------------------------------------------------------------------
class LoginRequest(BaseModel):
    type: Literal["login"]
    username: str = Field(pattern=USERNAME_PATTERN)


class ListUsersRequest(BaseModel):
    type: Literal["list_users"]


class SelectPartnerRequest(BaseModel):
    type: Literal["select"]
    username: str = Field(pattern=USERNAME_PATTERN)


class ChatMessageRequest(BaseModel):
    type: Literal["message"]
    text: str = Field(min_length=1, max_length=1000)

    @property
    def is_quit(self) -> bool:
        return self.text.strip().lower() == QUIT_WORD


ClientMessage = Annotated[
    Union[LoginRequest, ListUsersRequest, SelectPartnerRequest, ChatMessageRequest],
    Field(discriminator="type"),
]
client_message_adapter: TypeAdapter[ClientMessage] = TypeAdapter(ClientMessage)


def parse_client_message(raw: str) -> ClientMessage:
    """Valida un texto JSON recibido del cliente. Lanza `pydantic.ValidationError`."""
    return client_message_adapter.validate_json(raw)


# --------------------------------------------------------------------------
# Eventos Servidor -> Cliente
# --------------------------------------------------------------------------
class ServerEvent(BaseModel):
    timestamp: datetime = Field(default_factory=now_utc)

    def to_json(self) -> dict:
        return self.model_dump(mode="json")


class WelcomeEvent(ServerEvent):
    type: Literal["welcome"] = "welcome"
    username: str
    users: list[str]


class UsersEvent(ServerEvent):
    type: Literal["users"] = "users"
    users: list[str]


class PartnerSelectedEvent(ServerEvent):
    type: Literal["partner_selected"] = "partner_selected"
    username: str


class ChatMessageEvent(ServerEvent):
    type: Literal["message"] = "message"
    sender: str = Field(serialization_alias="from")
    text: str

    def to_json(self) -> dict:
        return self.model_dump(mode="json", by_alias=True)


class InfoEvent(ServerEvent):
    type: Literal["info"] = "info"
    detail: str


class ErrorEvent(ServerEvent):
    type: Literal["error"] = "error"
    detail: str


class ByeEvent(ServerEvent):
    type: Literal["bye"] = "bye"
    detail: str = "Has abandonado el chat. ¡Hasta pronto!"
