# Protocolo de mensajes

**Responsable:** Integrante 1 · **Estado:** listo

La comunicación es **JSON sobre WebSocket**. WebSocket es un protocolo full-duplex (RFC 6455) que va sobre un socket TCP: después de un *handshake* HTTP, cliente y servidor pueden enviar datos en cualquier momento por la misma conexión.

- **URL del socket servidor:** `ws://<IP_SERVIDOR>:<PUERTO>/ws` (por defecto `ws://127.0.0.1:8000/ws`)
- Cada mensaje es un objeto JSON con un campo `type`.
- Todo evento del servidor trae `timestamp` (ISO-8601, UTC).

## Flujo

```text
Cliente                                   Servidor
  | --- conexión TCP + handshake WS --->     |
  | --- login {username} --------------->    |  registra usuario, log de conectados
  | <-- welcome {users:[...]} -----------    |
  | --- select {username: poli02} ------>    |  empareja
  | <-- partner_selected ---------------     |
  | --- message {text} ----------------->    |  reenvía al interlocutor
  | <-- message {from, text} ------------    |  (mensajes del interlocutor)
  | --- message {text: "chao"} --------->    |  marca "abandonó"
  | <-- bye -----------------------------    |  cierra el socket
```

## Cliente → Servidor

| type | Campos | Descripción |
|---|---|---|
| `login` | `username` (3–20 caracteres: letras, números, `_`) | **Obligatorio como primer mensaje.** Si no, el servidor responde `error` y cierra (código 1008). |
| `list_users` | — | Pide la lista de usuarios conectados. |
| `select` | `username` | Elige con quién chatear. Si el otro no tiene interlocutor, también queda emparejado contigo. |
| `message` | `text` (1–1000 caracteres) | Mensaje para el interlocutor. Si `text` es `chao` (sin importar mayúsculas), el servidor lo reenvía, responde `bye`, marca al usuario como *abandonó* y cierra. |

## Servidor → Cliente

| type | Campos | Cuándo |
|---|---|---|
| `welcome` | `username`, `users` | Login correcto. `users` = los demás conectados. |
| `users` | `users` | Respuesta a `list_users` o cuando alguien entra o sale. |
| `partner_selected` | `username` | Quedaste emparejado con `username`. |
| `message` | `from`, `text` | Mensaje de tu interlocutor. |
| `info` | `detail` | Avisos: alguien se unió, salió o quiere chatear contigo. |
| `error` | `detail` | Petición inválida. La sesión **sigue abierta** (salvo en el login). |
| `bye` | `detail` | Confirmación de salida después de enviar `chao`. |

## Ejemplos

```json
{"type": "login", "username": "poli01"}
{"type": "welcome", "username": "poli01", "users": ["poli02"], "timestamp": "2026-11-08T18:00:00Z"}
{"type": "select", "username": "poli02"}
{"type": "message", "text": "hola poli02"}
{"type": "message", "from": "poli02", "text": "hola poli01", "timestamp": "2026-11-08T18:00:05Z"}
{"type": "error", "detail": "Primero elige un usuario con quien chatear.", "timestamp": "..."}
```

## API REST de monitoreo

| Método | Ruta | Respuesta |
|---|---|---|
| GET | `/health` | `{"status": "ok"}` |
| GET | `/api/usuarios` | Log de todos los usuarios que han entrado, con su estado (`conectado` / `abandonó`), con quién chatean y fechas. |
| GET | `/api/usuarios/conectados` | Lista de nombres conectados. |

Documentación interactiva: `http://127.0.0.1:8000/docs`.
