"""Cliente de consola del chat — RESPONSABLE: INTEGRANTE 2.

Uso esperado:
    python -m client --host 127.0.0.1 --port 8000 --usuario poli02

Requisitos de la guía (pasos 11 a 13):
  * El cliente arranca e inicia la conversación dando sus credenciales:
    IP del servidor, puerto y nombre de usuario.
  * Recibe del servidor la lista de usuarios conectados y elige uno.
  * Chatea con él (enviar y recibir AL MISMO TIEMPO => bidireccional).
  * Al escribir "chao" el servidor lo marca como que abandonó y termina.

El protocolo (qué JSON enviar y qué eventos llegan) está en docs/protocolo.md.
Las pruebas del servidor (tests/test_chat_socket.py) sirven de ejemplo de uso.

Sugerencia de diseño (asyncio + librería `websockets`, ya instalada):

    async with websockets.connect(url) as ws:
        await ws.send(json.dumps({"type": "login", "username": usuario}))
        await asyncio.gather(recibir(ws), enviar(ws))

`input()` bloquea el event loop: léalo con `await asyncio.to_thread(input, "> ")`.
"""

from __future__ import annotations

import argparse
import asyncio
import json  # noqa: F401  (se usará al implementar)

import websockets  # noqa: F401  (se usará al implementar)

QUIT_WORD = "chao"


def build_url(host: str, port: int) -> str:
    return f"ws://{host}:{port}/ws"


def render_event(event: dict) -> str:
    """Convierte un evento del servidor en el texto que se muestra en consola.

    TODO (Integrante 2): manejar cada tipo -> welcome, users, partner_selected,
    message, info, error, bye. Ej.: message => "[poli01] hola".
    """
    raise NotImplementedError


def parse_input(line: str) -> dict | None:
    """Convierte lo que escribe el usuario en un mensaje del protocolo.

    TODO (Integrante 2). Propuesta de comandos:
        /usuarios        -> {"type": "list_users"}
        /con poli01      -> {"type": "select", "username": "poli01"}
        chao             -> {"type": "message", "text": "chao"}
        cualquier texto  -> {"type": "message", "text": <texto>}
    Devuelve None si la línea está vacía.
    """
    raise NotImplementedError


async def receive_loop(ws) -> None:
    """TODO (Integrante 2): leer eventos del socket e imprimir `render_event`.
    Terminar cuando llegue `bye` o se cierre la conexión."""
    raise NotImplementedError


async def send_loop(ws) -> None:
    """TODO (Integrante 2): leer la consola sin bloquear, enviar `parse_input`
    y terminar después de enviar "chao"."""
    raise NotImplementedError


async def run(host: str, port: int, usuario: str) -> None:
    """TODO (Integrante 2): conectar, enviar login y correr ambos loops a la vez."""
    raise NotImplementedError


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Cliente del chat Duplex")
    parser.add_argument("--host", default="127.0.0.1", help="IP del servidor")
    parser.add_argument("--port", type=int, default=8000, help="Puerto del servidor")
    parser.add_argument("--usuario", help="Nombre de usuario (ej. poli01)")
    args = parser.parse_args(argv)
    # TODO (Integrante 2): si falta --usuario/--host, pedirlos con input() (Figura 3).
    asyncio.run(run(args.host, args.port, args.usuario))


if __name__ == "__main__":
    main()
