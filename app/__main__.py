"""Arranca el servidor: `python -m app`."""

import uvicorn

from .config import settings

if __name__ == "__main__":
    print(f"Servidor de chat escuchando en ws://{settings.host}:{settings.port}/ws")
    uvicorn.run("app.main:app", host=settings.host, port=settings.port, log_level=settings.log_level.lower())
