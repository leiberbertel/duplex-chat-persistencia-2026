# Reparto de tareas — Entrega 1 (semana 3)

Cada integrante trabaja en **su propia rama** y abre un Pull Request hacia `main` (ver README → Flujo de trabajo).

## Integrante 1 — Servidor de sockets y base del proyecto ✅
- [x] Scaffold del repo, `venv`, `requirements*.txt`, `.gitignore`, configuración por variables de entorno.
- [x] Protocolo de mensajes JSON (`app/chat/protocol.py`, `docs/protocolo.md`).
- [x] Socket servidor `/ws` con FastAPI: login, lista de conectados, elegir interlocutor, reenviar mensajes, "chao".
- [x] Log del servidor con los usuarios conectados y registro de estados (`conectado` / `abandonó`).
- [x] API REST de monitoreo (`/api/usuarios`, `/api/usuarios/conectados`, `/health`).
- [x] Pruebas automáticas del servidor (`tests/test_manager.py`, `tests/test_chat_socket.py`).
- [x] Documento de arquitectura (`docs/arquitectura.md`).
- [ ] Para el documento final: explicar el código del servidor (sección "Explicación del código – Servidor") y grabar su parte del video.

## Integrante 2 — Cliente de consola ⬜
Rama sugerida: `feature/cliente-consola` · Archivo: `client/cli.py`
- [ ] Pedir IP, puerto y usuario (por argumentos o `input()`, ver Figura 3 de la guía).
- [ ] Conectarse a `ws://IP:PUERTO/ws` y enviar `login`.
- [ ] Mostrar la lista de usuarios recibida y permitir elegir uno (`/con <usuario>`).
- [ ] Recibir y enviar **al mismo tiempo** (`asyncio.gather` con un loop de recepción y otro de envío).
- [ ] Mostrar los mensajes con formato `[usuario] texto` y los avisos `info` y `error`.
- [ ] Al escribir `chao`: enviarlo, esperar `bye` y cerrar limpio.
- [ ] Manejar errores: servidor apagado, usuario duplicado, Ctrl+C.
- [ ] Quitar el `skip` de `tests/test_client.py` y hacer que pase.
- [ ] *(Opcional)* Interfaz gráfica con `tkinter`, parecida a la Figura 3.
- [ ] Para el documento: explicar el código del cliente y grabar su parte del video.

## Integrante 3 — Documentación, red y pruebas ⬜
Rama sugerida: `docs/entrega-1`
- [ ] `docs/marco-teorico.md`: marco teórico y estado del arte de los sockets (APA).
- [ ] `docs/diseno-red.md`: IP y puerto, escenarios local y LAN, diagrama de red, firewall.
- [ ] `docs/pruebas.md`: ejecutar las pruebas manuales, llenar la matriz de trazabilidad y pegar las evidencias.
- [ ] Coordinar el video (explicación del código y demo funcionando), subirlo a YouTube y verificar el enlace.
- [ ] Armar el **documento maestro** en APA: portada, introducción, marco teórico, diseño de red, explicación del código (aportes de los Integrantes 1 y 2), pruebas, enlace del video (antes de las conclusiones), conclusiones y bibliografía.
- [ ] Adjuntar el código fuente (zip del repo o enlace) y subir la entrega a la plataforma.

## Entregables según la guía
- [ ] Estado del arte de los sockets → Integrante 3
- [ ] Explicación de las líneas de código de los sockets → Integrantes 1 y 2
- [ ] Diseño de red y trazabilidad con las pruebas → Integrante 3
- [ ] Enlace del video → Integrante 3 (todos graban)
- [ ] Código fuente, conclusiones y bibliografía → todos
