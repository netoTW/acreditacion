# Cola de tareas — Somos Calidad (orden por dependencias)
# El runner procesa las líneas "- [ ]" de arriba a abajo.
# [x] hecho · [ ] pendiente · [!] bloqueado

## Track A — Realtime (riesgo; define el plazo)
- [x] A1 Fijar estrategia de render: servidor agnóstico, decisión 2D/3D después del gate (ADR-004)
- [x] A2 Servidor Colyseus mínimo: sala, esquema de estado en tiles, join/leave
- [x] A3 Cliente sobre el canvas isométrico portado de la cáscara + autoridad de posición en servidor
- [x] A3.1 Corregir el bundle del cliente: se servía el UMD de Node (Buffer is not defined) — ahora esbuild sobre la condición browser + verificador en prestart
- [x] A4 GATE DEL DIRECTOR: túnel ngrok + dispositivos reales fuera de localhost — APROBADO (Hito 1)
- [x] A5 Chat sincronizado con rate limit y truncado + presencia real
- [x] A6 Reconexión: cliente que se cae vuelve con su sessionId y posición — 11/11 en verde
- [x] A7 GATE DEL DIRECTOR: 3 personas en redes distintas a la vez — APROBADO (Hito 1)
- [ ] A8 Identidad por token firmado por la API (reemplaza el nombre por opciones)
- [ ] A9 Persistencia del chat en mensaje_plaza (S-24)
- [ ] A10 Actividad social: trivia grupal reusando el motor de la cáscara (S-42)

## Track B — Fase 0, especificación
- [x] B1 Tanda 1: dominio real extraído de la ruta oficial AIEP (5 dimensiones, 13 hitos, gobernanza)
- [x] B1 Tanda 1: ADR-001 stack · ADR-002 frontend · ADR-003 cargo×dimensión · ADR-004 realtime · ADR-005 integridad
- [x] B1 Tanda 1: glosario, modelo de datos, design-system, JSON Schema de contenido, reglas del validador
- [x] B1 Tanda 1: SUPUESTOS.md (S-01…S-42) y DECISIONES-AUTONOMAS.md
- [x] B2 Tanda 2 — Motor de integridad: candados en el esquema, canario, canario de esquema, banco de mutación, CI
- [ ] B3 Tanda 3 — Contenido y evaluación: contrato del generador, quiz vs evaluación, autosave, reintentos, casos borde
- [ ] B4 Tanda 4 — Superficie: adapters (identidad, correo, Open Badges), permisos por comité, specs de las 16 pantallas
- [ ] B5 Compuerta de Fase 0: reporte de consistencia (numeración, links, terminología, invariantes espejo)

## Track C — Cimientos supervisados (secuencial; el director verifica entre cada uno)
- [x] C1 Scaffold: docker compose autosuficiente (db, api, realtime) con /docs viva y 3 servicios healthy
- [x] C2 Modelo + migraciones + seed (5 dimensiones, 13 hitos, 6 cargos, matriz 30 filas, comités, 3 colaboradores)
- [x] C3 Motor de gamificación + CANARIO EN CI (verde antes de que exista la primera medalla del sistema)
- [x] C4 Adapter de identidad conmutable (dev ↔ Entra) + login "actuar como" + sesión firmada
- [x] C5 Generador de contenido: 15 unidades validadas · 45 módulos · 360 ítems · integrado en el arranque
- [x] C6 Integrador: contenido validado → rutas por cargo (rechaza lo inválido; no pisa contenido con intentos)

## Track D — Modo fábrica (worktrees en paralelo, con cimientos verdes)
- [x] D1a Pantalla de Ingreso ("actuar como") y Mi Ruta con mapa generado desde datos
- [ ] D1b Pantalla de bloque y visor de módulo (no existe en la cáscara)
- [ ] D2 Quiz formativo y evaluación final con autosave e idempotencia
- [ ] D3 Insignias y Open Badges + pantalla de medalla obtenida
- [ ] D4 Ranking desde eventos con desempate S-15
- [ ] D5 Dashboard desde eventos + rezagados agregados + registro de acceso (E-03)
- [ ] D6 Juegos recableados al banco real, con tope de XP lúdico
- [ ] D7 Navegación móvil (S-28) y accesibilidad en todas las pantallas
- [ ] D8 Eliminar /clave-de-respuestas y MODO_DEV antes de producción
- [x] D9 Servicio web en el compose: `docker compose up` levanta db, api, realtime y web

## Gate final
- [ ] Los 5 puntos de CLAUDE.md §13 verdes de punta a punta
