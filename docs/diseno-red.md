# Diseño del modelo de comunicaciones y de la red

**Responsable:** Integrante 3 · **Estado:** pendiente

> Paso 8 de la guía: definir las IP y el puerto del servidor. Incluir un diagrama de la red.

## Valores por defecto del proyecto

| Elemento | Valor | Dónde se cambia |
|---|---|---|
| Interfaz del servidor | `0.0.0.0` (todas las interfaces) | `CHAT_HOST` |
| Puerto del servidor | `8000/TCP` | `CHAT_PORT` |
| URL del socket | `ws://<IP_SERVIDOR>:8000/ws` | — |
| Prueba local | `127.0.0.1` (localhost) | — |

## TODO
- [ ] Escenario 1 — **local**: servidor y clientes en el mismo equipo (`127.0.0.1`).
- [ ] Escenario 2 — **LAN**: servidor en el PC de un integrante y clientes en los PCs de los demás. Registrar la IP real de cada equipo (`ipconfig` / `ip a`).
  | Equipo | Rol | IP | SO |
  |---|---|---|---|
  | PC Integrante 1 | Servidor | 192.168.x.x | |
  | PC Integrante 2 | Cliente poli01 | | |
  | PC Integrante 3 | Cliente poli02 | | |
- [ ] Regla de firewall de Windows para permitir el puerto 8000 entrante (documentar con capturas).
- [ ] Diagrama de red (draw.io o similar): router/switch, equipos, IP, puerto.
- [ ] Diagrama de secuencia de la conversación (se puede partir del de `protocolo.md`).
