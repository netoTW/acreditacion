# ADR-001 — Stack

**Estado:** aceptado · **Fecha:** 2026-08-09 · **Decide:** arquitecto

## Decisión

| Capa | Elección | Versión |
|---|---|---|
| API | Python + FastAPI + Pydantic v2 | 3.12 / FastAPI 0.115 |
| Persistencia | PostgreSQL + SQLAlchemy 2 + Alembic | PG 16 |
| Tiempo real | Node + Colyseus + `@colyseus/schema` | Node 22 / Colyseus 0.15 |
| Frontend | ver [ADR-002](ADR-002-frontend.md) | — |
| Orquestación | Docker Compose | — |
| Tests | pytest + testcontainers · Vitest · Playwright | — |

Verificado en la máquina del director: Node 26.7.0, npm 11.19.0, Docker 29.6.2, git 2.50.1.
Python del sistema es 3.9, por eso el intérprete de la API va **dentro del contenedor** y no
se depende del local.

## FastAPI y no Django

CLAUDE.md §11 deja la puerta abierta a Django+DRF si el panel de administración lo
justifica. No lo justifica:

- El corazón del sistema es un **motor derivado de eventos con invariantes en el esquema**
  ([ADR-005](ADR-005-integridad-de-completitud.md)). El admin autogenerado de Django es
  justamente lo que **no** queremos cerca de `evento_gamificacion` e `insignia`: ofrece
  editar a mano lo que por diseño no se edita.
- La administración que este sistema necesita no es CRUD genérico: es *generar contenido de
  una dimensión, validarlo, revisarlo y aprobarlo*. Es una pantalla de dominio que hay que
  diseñar igual, con o sin Django.
- CLAUDE.md §11 pide `/docs` interactiva con seed desde el día 1 como primera interfaz de
  prueba del director. En FastAPI eso es gratis y fiel al esquema real.
- Menos superficie que endurecer para que la base de datos, y no el framework, sea la que
  garantiza la verdad.

**Costo asumido:** hay que construir a mano el CRUD de catálogos (cargos, unidades,
comités). Son tablas de seed que casi no cambian, así que el costo es bajo y acotado.

## Node solo para el tiempo real

El track de realtime queda aislado en su propio servicio y su propio lenguaje. Colyseus
resuelve sala, esquema de estado, sincronización delta y reconexión, que es exactamente el
riesgo del proyecto. No se mezcla con la API: se comunican por HTTP con un token firmado
por la API para que la sala sepa **quién** entra sin duplicar la lógica de identidad.

## Compose

Servicios: `db` · `api` · `realtime` · `web`. Reglas de CLAUDE.md §11, sin pasos manuales:

- `healthcheck` en `db`, `api` y `realtime`.
- `depends_on: {condition: service_healthy}`.
- Arranque autosuficiente: espera dependencias → migra → carga seed (5 dimensiones, 13
  hitos, 6 cargos, matriz de 30 filas, comités, y los 3 colaboradores del slice) → sirve.
- `.env.example` versionado. El arranque **corta con mensaje claro** si falta una variable,
  en vez de arrancar a medias.
- Sin nube: todo local. El túnel del spike es lo único que sale a internet (§8).

## Consecuencias

- Dos ecosistemas de dependencias (pip y npm). Aceptado: la frontera es nítida.
- El seed es parte del arranque, no un script aparte: si el seed se rompe, el sistema no
  levanta, y eso es lo correcto.
- Los tests de invariantes corren contra **PostgreSQL real** vía testcontainers, no SQLite:
  los `CHECK`, los triggers y los índices únicos de ADR-005 no existen en SQLite, y probar
  contra otro motor daría una garantía falsa.

## Cómo se revierte

La API se toca detrás de contratos OpenAPI versionados; cambiar de framework es reescribir
la capa HTTP, no el dominio. El motor y sus invariantes viven en la base de datos y en
módulos de dominio sin dependencia del framework, justamente para que esto sea posible.
