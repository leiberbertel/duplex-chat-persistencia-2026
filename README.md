# duplex-chat-persistencia-2026

**Duplex** es un chat bidireccional con sockets. Proyecto de Persistencia de Datos y Transaccionalidad, 2026-2.

Entrega 1 (semana 3): un **socket servidor** y un **socket cliente** para chatear entre usuarios, hecho con **Python 3.13 + FastAPI (WebSocket)**.

| Integrante | Rol | Estado |
|---|---|---|
| Integrante 1 | Servidor de sockets, protocolo, scaffold, pruebas del servidor | ✅ |
| Integrante 2 | Cliente de consola (`client/cli.py`) | ⬜ |
| Integrante 3 | Marco teórico, diseño de red, pruebas y trazabilidad, video, documento APA | ⬜ |

El detalle de las tareas está en [docs/TAREAS.md](docs/TAREAS.md).

## Requisitos
- Python 3.11 o superior (probado con 3.13)
- Git

## Instalación

```bash
git clone <url-del-repo>
cd duplex-chat-persistencia-2026
python -m venv .venv
```

Activar el entorno:

```bash
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
# Linux / macOS
source .venv/bin/activate
```

Instalar dependencias:

```bash
pip install -r requirements-dev.txt
```

## Ejecutar el servidor

```bash
python -m app
```

El servidor escucha en `ws://0.0.0.0:8000/ws`. Para cambiar la IP o el puerto, use las variables `CHAT_HOST` y `CHAT_PORT` (ver `.env.example`):

```powershell
$env:CHAT_PORT = "9000"; python -m app
```

- Documentación interactiva: http://127.0.0.1:8000/docs
- Log de usuarios: http://127.0.0.1:8000/api/usuarios

La consola del servidor muestra la lista de usuarios conectados cada vez que alguien entra o sale:

```text
18:00:01 [INFO] duplex.chat: Usuarios conectados (2): poli01, poli02
18:00:09 [INFO] duplex.chat: [poli01 -> poli02] hola
18:00:15 [INFO] duplex.chat: poli01 abandonó el chat
```

## Ejecutar el cliente *(Integrante 2, en construcción)*

```bash
python -m client --host 127.0.0.1 --port 8000 --usuario poli01
```

Mientras el cliente no esté listo, el servidor se puede probar con las pruebas automáticas o con cualquier cliente WebSocket (por ejemplo Postman), enviando los JSON de [docs/protocolo.md](docs/protocolo.md).

## Pruebas

```bash
python -m pytest -v
```

## Estructura

```text
app/
  __main__.py        # python -m app -> arranca Uvicorn
  main.py            # create_app(): FastAPI, logging, rutas
  config.py          # CHAT_HOST, CHAT_PORT, CHAT_LOG_LEVEL
  chat/
    protocol.py      # modelos de mensajes (Pydantic)
    manager.py       # registro de usuarios, parejas, reenvío
    router.py        # socket /ws + API REST
client/
  cli.py             # cliente de consola (Integrante 2)
tests/               # pytest
docs/
  TAREAS.md          # reparto de trabajo
  arquitectura.md    # decisiones y componentes
  protocolo.md       # especificación de mensajes
  marco-teorico.md   # Integrante 3
  diseno-red.md      # Integrante 3
  pruebas.md         # matriz de trazabilidad
```

## Flujo de trabajo en equipo
1. Actualice `main`: `git pull origin main`.
2. Cree su rama: `git checkout -b feature/cliente-consola` (o `docs/entrega-1`).
3. Haga commits pequeños y descriptivos.
4. Antes de subir, ejecute `python -m pytest`.
5. Haga `git push -u origin <rama>` y abra un Pull Request hacia `main`. Otro integrante lo revisa.

Si cambia el protocolo, actualice `docs/protocolo.md` y avise al equipo, porque el cliente y el servidor dependen de él.
