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
"""

from __future__ import annotations

import argparse
import asyncio
import json
import websockets

QUIT_WORD = "chao"

HELP_TEXT = (
    "Comandos disponibles:\n"
    "  /con <usuario>  — Emparejarte con un usuario\n"
    "  /usuarios       — Listar usuarios conectados\n"
    "  /ayuda          — Mostrar esta ayuda\n"
    f"  {QUIT_WORD}            — Salir del chat"
)


def build_url(host: str, port: int) -> str:
    """Construye la URL WebSocket del servidor."""
    return f"ws://{host}:{port}/ws"


def render_event(event: dict) -> str:
    """Convierte un evento del servidor en el texto que se muestra en consola."""
    msg_type = event.get("type")

    if msg_type == "welcome":
        users = event.get("users", [])
        lista = ", ".join(users) if users else "ninguno"
        return (
            f"[SISTEMA] ¡Bienvenido, {event.get('username')}!\n"
            f"[SISTEMA] Usuarios conectados: {lista}\n"
            f"[INSTRUCCIONES] Usa '/con <usuario>' para emparejarte, '/usuarios' para listar o '{QUIT_WORD}' para salir."
        )

    elif msg_type == "users":
        users = event.get("users", [])
        lista = ", ".join(users) if users else "ninguno"
        return f"[SISTEMA] Usuarios conectados: {lista}"

    elif msg_type == "partner_selected":
        return f"[SISTEMA] Quedaste emparejado exitosamente con: [{event.get('username')}]"

    elif msg_type == "message":
        sender = event.get("from", "Desconocido")
        return f"[{sender}] {event.get('text', '')}"

    elif msg_type == "info":
        return f"[INFO] {event.get('detail', '')}"

    elif msg_type == "error":
        return f"[ERROR] {event.get('detail', '')}"

    elif msg_type == "bye":
        return f"[SISTEMA] {event.get('detail', 'Desconexión confirmada.')}"

    return f"[EVENTO] {event}"


def parse_input(line: str) -> dict | None:
    """Convierte lo que escribe el usuario en un mensaje del protocolo JSON.

    Devuelve None si la línea está vacía o es un comando local (p. ej. /ayuda).
    Devuelve un dict con 'type' == '__local_error__' para avisos que no se envían
    al servidor (uso incorrecto de comandos o comandos desconocidos).
    """
    texto = line.strip()
    if not texto:
        return None

    if texto == "/ayuda":
        print(f"\n{HELP_TEXT}")
        return None

    if texto == "/con":
        return {"type": "__local_error__", "detail": "Uso: /con <usuario>"}

    if texto.startswith("/con "):
        partes = texto.split(" ", 1)
        target = partes[1].strip() if len(partes) > 1 else ""
        if not target:
            return {"type": "__local_error__", "detail": "Uso: /con <usuario>"}
        return {"type": "select", "username": target}

    if texto in ("/usuarios", "/list"):
        return {"type": "list_users"}

    if texto.lower() == QUIT_WORD:
        return {"type": "message", "text": QUIT_WORD}

    if texto.startswith("/"):
        return {"type": "__local_error__", "detail": f"Comando desconocido: '{texto}'. Escribe /ayuda para ver los disponibles."}

    return {"type": "message", "text": texto}


async def receive_loop(ws) -> None:
    """Lee eventos del socket e imprime render_event."""
    try:
        async for raw_msg in ws:
            try:
                event = json.loads(raw_msg)
            except json.JSONDecodeError:
                print("\n[ERROR] Formato JSON inválido recibido del servidor.")
                continue

            output = render_event(event)
            if output:
                print(f"\n{output}")

            if event.get("type") == "bye":
                break
    except websockets.exceptions.ConnectionClosed:
        print("\n[INFO] Conexión cerrada por el servidor.")


async def send_loop(ws) -> None:
    """Lee la consola sin bloquear y envía parse_input."""
    while True:
        try:
            line = await asyncio.to_thread(input, "> ")
            payload = parse_input(line)
            if payload is None:
                continue

            # Avisos locales: no se envían al servidor
            if payload.get("type") == "__local_error__":
                print(f"\n[ERROR] {payload['detail']}")
                continue

            try:
                await ws.send(json.dumps(payload))
            except websockets.exceptions.ConnectionClosed:
                break

            if payload.get("type") == "message" and payload.get("text") == QUIT_WORD:
                break
        except (EOFError, KeyboardInterrupt):
            try:
                await ws.send(json.dumps({"type": "message", "text": QUIT_WORD}))
            except websockets.exceptions.ConnectionClosed:
                pass
            break


async def run(host: str, port: int, usuario: str) -> None:
    """Conecta al socket, envía el login y corre ambos loops a la vez.

    Termina en cuanto cualquiera de los dos loops finalice (p. ej. el servidor
    cierra la conexión) sin quedarse bloqueado esperando un Enter extra.
    """
    url = build_url(host, port)
    print(f"[CONEXIÓN] Conectando a {url} como '{usuario}'...")

    try:
        async with websockets.connect(url) as ws:
            await ws.send(json.dumps({"type": "login", "username": usuario}))

            recv = asyncio.create_task(receive_loop(ws))
            send = asyncio.create_task(send_loop(ws))
            done, _ = await asyncio.wait({recv, send}, return_when=asyncio.FIRST_COMPLETED)
            if recv in done and not send.done():
                print("[INFO] La conexión terminó. Presiona Enter para salir.")
            await asyncio.gather(recv, send, return_exceptions=True)
    except (OSError, websockets.exceptions.WebSocketException) as e:
        print(f"\n[ERROR DE CONEXIÓN] No se pudo conectar a {url}. Detalle: {e}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Cliente del chat Duplex")
    parser.add_argument("--host", default=None, help="IP del servidor")
    parser.add_argument("--port", type=int, default=None, help="Puerto del servidor")
    parser.add_argument("--usuario", default=None, help="Nombre de usuario (ej. poli01)")
    args = parser.parse_args(argv)

    host = args.host or input("IP del servidor [127.0.0.1]: ").strip() or "127.0.0.1"
    port = args.port or int(input("Puerto [8000]: ").strip() or 8000)
    usuario = args.usuario or input("Nombre de usuario: ").strip()

    try:
        asyncio.run(run(host, port, usuario))
    except KeyboardInterrupt:
        print("\n[INFO] Cliente cerrado.")


if __name__ == "__main__":
    main()
