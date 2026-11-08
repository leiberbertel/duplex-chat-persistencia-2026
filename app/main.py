"""Punto de entrada de la aplicación FastAPI."""

from __future__ import annotations

import logging

from fastapi import FastAPI

from . import __version__
from .chat.manager import ConnectionManager
from .chat.router import router as chat_router
from .config import settings


def configure_logging(level: str = settings.log_level) -> None:
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def create_app() -> FastAPI:
    """Crea la app con un `ConnectionManager` propio (útil para aislar pruebas)."""
    app = FastAPI(
        title="Duplex — Chat bidireccional con sockets",
        version=__version__,
        description="Entrega 1 (semana 3) — Persistencia de Datos y Transaccionalidad.",
    )
    app.state.manager = ConnectionManager()
    app.include_router(chat_router)

    @app.get("/health", tags=["sistema"])
    async def health() -> dict:
        return {"status": "ok", "version": __version__}

    return app


configure_logging()
app = create_app()
