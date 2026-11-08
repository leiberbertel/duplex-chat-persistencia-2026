"""Configuración del servidor leída de variables de entorno.

Variables soportadas (ver `.env.example`):
    CHAT_HOST       Interfaz donde escucha el servidor (por defecto 0.0.0.0).
    CHAT_PORT       Puerto TCP del servidor (por defecto 8000).
    CHAT_LOG_LEVEL  Nivel de log (DEBUG, INFO, WARNING...).
"""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            host=os.getenv("CHAT_HOST", cls.host),
            port=int(os.getenv("CHAT_PORT", cls.port)),
            log_level=os.getenv("CHAT_LOG_LEVEL", cls.log_level).upper(),
        )


settings = Settings.from_env()
