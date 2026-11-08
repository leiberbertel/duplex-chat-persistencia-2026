# Plan de pruebas y trazabilidad

**Responsable:** Integrante 3 (pruebas manuales) · Integrante 1 (pruebas automáticas del servidor)

> La guía pide "la trazabilidad con las pruebas del proceso descrito". Cada requisito debe tener al menos una prueba con su evidencia (captura o minuto del video).

## Pruebas automáticas

```bash
.venv\Scripts\python -m pytest -v
```

## Matriz de trazabilidad

| Req. (paso de la guía) | Descripción | Prueba automática | Prueba manual / evidencia | Estado |
|---|---|---|---|---|
| R10 | El servidor arranca y espera clientes | `test_health` | TODO captura de consola | Auto ✅ / Manual ⬜ |
| R11 | El cliente se conecta con IP, puerto y usuario | `test_login_devuelve_lista_de_conectados` | TODO (requiere cliente del Integrante 2) | Auto ✅ / Manual ⬜ |
| R12 | El servidor muestra la lista de conectados | `test_registro_y_log_de_conectados` | TODO captura del log del servidor | Auto ✅ / Manual ⬜ |
| R12 | El servidor devuelve la lista y el usuario elige uno | `test_chat_bidireccional_y_chao` | TODO | Auto ✅ / Manual ⬜ |
| R13 | Chat en ambos sentidos | `test_chat_bidireccional_y_chao` | TODO | Auto ✅ / Manual ⬜ |
| R13 | "chao" marca al usuario como que abandonó | `test_chat_bidireccional_y_chao`, `test_reconexion_tras_chao` | TODO captura de `/api/usuarios` | Auto ✅ / Manual ⬜ |
| — | Usuario duplicado rechazado | `test_usuario_duplicado_rechazado` | — | Auto ✅ |
| — | Mensajes inválidos no cierran la sesión | `test_json_invalido_no_tumba_la_sesion` | — | Auto ✅ |
| — | Cliente: comandos y formato | `tests/test_client.py` | — | ⬜ Integrante 2 |

## TODO (Integrante 3)
- [ ] Ejecutar cada prueba manual en escenario local y LAN, y pegar las evidencias.
- [ ] Prueba con 3 o más clientes a la vez (poli01, poli02, poli03).
- [ ] Prueba de desconexión abrupta (cerrar la consola del cliente sin escribir "chao").
