# Cola de tareas — Somos Calidad (orden por dependencias)
# El runner procesa las líneas "- [ ]" de arriba a abajo.
# [x] hecho · [ ] pendiente · [!] bloqueado

## Track A — Realtime (riesgo; define el plazo)
- [x] A1 Fijar estrategia de render: servidor agnóstico, decisión 2D/3D después del gate (ADR-004)
- [x] A2 Servidor Colyseus mínimo: sala, esquema de estado en tiles, join/leave
- [x] A3 Cliente sobre el canvas isométrico portado de la cáscara + autoridad de posición en servidor
- [ ] A4 GATE DEL DIRECTOR: túnel ngrok + 2 dispositivos reales fuera de localhost
- [x] A5 Chat sincronizado con rate limit y truncado + presencia real
- [ ] A6 GATE DEL DIRECTOR: un cliente refresca y vuelve sin romper la sala
- [ ] A7 GATE DEL DIRECTOR: los 3 dispositivos a la vez (punto 4 de LISTO)
- [ ] A8 Identidad por token firmado por la API (reemplaza el nombre por opciones)
- [ ] A9 Persistencia del chat en mensaje_plaza (S-24)
- [ ] A10 Actividad social: trivia grupal reusando el motor de la cáscara (S-42)

## Track B — Fase 0, especificación
- [x] B1 Tanda 1: dominio real extraído de la ruta oficial AIEP (5 dimensiones, 13 hitos, gobernanza)
- [x] B1 Tanda 1: ADR-001 stack · ADR-002 frontend · ADR-003 cargo×dimensión · ADR-004 realtime · ADR-005 integridad
- [x] B1 Tanda 1: glosario, modelo de datos, design-system, JSON Schema de contenido, reglas del validador
- [x] B1 Tanda 1: SUPUESTOS.md (S-01…S-42) y DECISIONES-AUTONOMAS.md
- [ ] B2 Tanda 2 — Motor de integridad: eventos, XP dual, nivel derivado, medallas, invariantes espejo, canario
- [ ] B3 Tanda 3 — Contenido y evaluación: contrato del generador, quiz vs evaluación, autosave, reintentos, casos borde
- [ ] B4 Tanda 4 — Superficie: adapters (identidad, correo, Open Badges), permisos por comité, specs de las 16 pantallas
- [ ] B5 Compuerta de Fase 0: reporte de consistencia (numeración, links, terminología, invariantes espejo)

## Track C — Cimientos supervisados (secuencial; el director verifica entre cada uno)
- [ ] C1 Scaffold: docker compose autosuficiente (db, api, realtime, web) con /docs viva
- [ ] C2 Modelo + migraciones + seed (5 dimensiones, 13 hitos, 6 cargos, matriz 30 filas, comités, 3 colaboradores)
- [ ] C3 Motor de gamificación + Validador de Integridad + CANARIO EN CI (antes de la primera medalla)
- [ ] C4 Adapter de identidad + login dev "actuar como"
- [ ] C5 Generador de contenido: 15 unidades (5 dimensiones × 3 niveles) validadas
- [ ] C6 Integrador: contenido validado → rutas por cargo en base de datos

## Track D — Modo fábrica (worktrees en paralelo, con cimientos verdes)
- [ ] D1 UI de ruta + bloque + módulo (la pantalla de módulo no existe en la cáscara)
- [ ] D2 Quiz formativo y evaluación final con autosave e idempotencia
- [ ] D3 Insignias y Open Badges + pantalla de medalla obtenida
- [ ] D4 Ranking desde eventos con desempate S-15
- [ ] D5 Dashboard desde eventos + rezagados agregados + registro de acceso (E-03)
- [ ] D6 Juegos recableados al banco real, con tope de XP lúdico
- [ ] D7 Navegación móvil (S-28) y accesibilidad en todas las pantallas

## Gate final
- [ ] Los 5 puntos de CLAUDE.md §13 verdes de punta a punta
