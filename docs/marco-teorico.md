# Marco teórico: programación con sockets

**Responsable:** Integrante 3 · **Estado:** pendiente

> Pasos 7 y "estado del arte" de la guía. Redactar en normas APA (citas en el texto y referencias al final).

## TODO
- [ ] ¿Qué es un socket? Definición, historia (Berkeley sockets, BSD 4.2).
- [ ] Modelo cliente-servidor.
- [ ] Tipos de socket: de flujo (TCP, `SOCK_STREAM`) y de datagrama (UDP, `SOCK_DGRAM`). Comparación.
- [ ] Ciclo de vida: `socket` → `bind` → `listen` → `accept` / `connect` → `send`/`recv` → `close`.
- [ ] Puertos e IP: puertos bien conocidos, registrados y dinámicos; `localhost` y `0.0.0.0`.
- [ ] Comunicación *half-duplex* y *full-duplex*.
- [ ] WebSocket (RFC 6455): handshake HTTP *Upgrade*, *frames*, relación con TCP. Por qué lo usamos (ver `arquitectura.md`).
- [ ] Concurrencia en servidores: hilos y E/S asíncrona (`asyncio`).
- [ ] Sockets en Python: módulo `socket`, `asyncio`, librería `websockets`, FastAPI/Starlette.

## Referencias (APA 7)
- Fette, I., & Melnikov, A. (2011). *The WebSocket Protocol* (RFC 6455). IETF. https://www.rfc-editor.org/rfc/rfc6455
- TODO: agregar como mínimo 4 fuentes más (libros de redes, documentación oficial de Python y FastAPI).
