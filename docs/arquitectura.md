# Arquitectura

**Responsable:** Integrante 1 · **Estado:** listo

## Decisión: FastAPI + WebSocket

La guía permite Java, C++ o Python. Usamos **Python 3.13 + FastAPI**. El socket servidor es un endpoint **WebSocket** (`/ws`) servido por Uvicorn:

- WebSocket va sobre **un socket TCP** y es *full-duplex*: los dos extremos pueden escribir a la vez, que es lo que pide un chat bidireccional.
- FastAPI valida los mensajes con Pydantic y genera documentación (`/docs`).
- El mismo servidor expone una API REST con el log de usuarios. En las entregas 2 y 3 se reutiliza para las operaciones contra la base de datos.

## Componentes

```text
+-------------------+        ws://IP:8000/ws         +--------------------------------+
| client/cli.py     | <----------------------------> | app/chat/router.py  (socket)   |
| (Integrante 2)    |       JSON (protocolo.md)      |   - login / bucle de mensajes  |
+-------------------+                                |   - API REST /api/usuarios     |
                                                     +---------------+----------------+
+-------------------+                                                |
| client/cli.py     | <---------------------------->  +--------------v-----------------+
| (otro usuario)    |                                 | app/chat/manager.py            |
+-------------------+                                 |   ConnectionManager            |
                                                      |   - registro de usuarios       |
                                                      |   - log de conectados          |
                                                      |   - emparejar y reenviar       |
                                                      +--------------------------------+
```

| Archivo | Responsabilidad |
|---|---|
| `app/config.py` | Host, puerto y nivel de log (variables `CHAT_*`). |
| `app/main.py` | Crea la app FastAPI (`create_app`), configura el logging y monta las rutas. |
| `app/chat/protocol.py` | Modelos Pydantic de cada mensaje y evento. Valida lo que llega por el socket. |
| `app/chat/manager.py` | Estado del chat: usuarios, estados, parejas. Envía y reenvía eventos. |
| `app/chat/router.py` | Ciclo de vida del socket de cada cliente y endpoints REST. |
| `client/cli.py` | Cliente de consola (Integrante 2). |

## Concurrencia

Uvicorn corre un *event loop* de `asyncio`. Cada cliente conectado es una corrutina `chat_socket` que espera mensajes con `await websocket.receive_text()`. Esa espera no bloquea a los demás clientes, así que el servidor atiende a muchos usuarios a la vez sin crear un hilo por cliente. El `ConnectionManager` protege los cambios de estado con un `asyncio.Lock`.

## Estado y persistencia

En esta entrega el registro de usuarios vive **en memoria**. Si el servidor se reinicia, el registro se pierde. `ConnectionManager` aísla ese estado, así que en las entregas 2 y 3 se puede cambiar por un repositorio en base de datos (MySQL o PostgreSQL) sin tocar el router.
