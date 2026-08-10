# Verificación en tu máquina — C1 · C2 · C5

```bash
cd ~/Documents/acreditacion
cp .env.example .env
docker compose up
```

Un solo comando. Espera la base → migra → siembra → sirve. Sin pasos manuales.

**Puertos:** 8010 (API), 5442 (base), 2567 (Plaza). Elegidos para **no chocar con
`portal-inclusion`**, que tiene tomados el 5432 y el 8000. Los dos proyectos corren a la vez.

En el log de arranque debes ver exactamente esto:

```
  migrando · 001_integridad.sql
  migrando · 002_catalogo.sql
  seed · 5 dimensiones · 13 hitos · 6 cargos · 30 filas de matriz · 3 colaboradores
  contenido generado y validado · 15 unidades · 45 módulos · 360 ítems de banco
```

Y los tres servicios sanos: `docker compose ps` → `api`, `db`, `realtime` en **healthy**.

---

## Las URLs, y qué debes ver en cada una

Todo se puede hacer desde **http://localhost:8010/docs** (botón *Try it out*).

### 1. El catálogo real

| URL | Qué debes ver |
|---|---|
| http://localhost:8010/catalogo/dimensiones | **5** dimensiones con sus nombres oficiales. `ICI` es la única con `obligatoria: false` — es voluntaria pero necesaria para el período máximo de vigencia. |
| http://localhost:8010/catalogo/hitos | **13** hitos. H01–H09 son ruta `autoevaluacion` 2026; H10–H13 son `acreditacion` 2027. **H13 (visita de pares) tiene `fecha_inicio` y `fecha_fin` en `null`** — la fuente dice "por definir" y el sistema no inventa la fecha. |
| http://localhost:8010/catalogo/cargos | **6** cargos, con cuántas personas ocupa cada uno (3 ocupados, 3 en cero). |
| http://localhost:8010/catalogo/comites | La gobernanza real: Junta Directiva, Aseguramiento, Central, **5** por dimensión, y los de sede y escuela. |

### 2. La matriz — el corazón del modelo

**http://localhost:8010/catalogo/matriz** → **30 filas**. Puestas en tabla:

```
                         GESTION  DOCENCIA  CALIDAD   VCM   ICI
  Rector                       3         2        3     2     2
  Vicerrector Académico        2         3        3     1     1
  Director de Carrera          1         3        2     3     1
  Docente                      1         3        1     1     1
  Coordinador de Calidad       3         2        3     1     1
  Administrativo               2         1        2     1     1
```

Debe coincidir exactamente con la tabla de `docs/decisiones/ADR-003`. Fíjate en que el
**Rector no tiene ningún 1** (amplitud) y el **Docente tiene un solo 3** (profundidad
puntual).

### 3. Que el contenido se genera una vez y se comparte

**http://localhost:8010/catalogo/contenido** → **15 unidades** (5 dimensiones × 3 niveles),
no 30, con **45 módulos y 360 ítems** generados y validados. La columna `cargos_que_la_usan` suma **30**: los 30 pares cargo×dimensión se sirven
con 15 unidades. Ahí está el ahorro de ADR-003.

Verás también que los módulos escalan con el nivel: N1 → 2, N2 → 3, N3 → 4 (S-32).

> `ICI N3` aparece con **0 cargos**: ningún cargo del slice exige Investigación al nivel 3.
> Existe para completar la grilla y para cargos futuros. No es un error.

### 4. Que las rutas son distintas por cargo

**http://localhost:8010/colaboradores** → los 3, con su escalón derivado y si ven el panel
institucional. **Copia el `id`** de dos de ellos.

Después **http://localhost:8010/colaboradores/{id}/ruta** y compara:

```
Pablo · Docente                        Rectoría · Rector
1. DOCENCIA N3  4 mód  400 XP          1. GESTION  N3  4 mód  400 XP
2. GESTION  N1  2 mód  200 XP          2. CALIDAD  N3  4 mód  400 XP
3. CALIDAD  N1  2 mód  200 XP          3. DOCENCIA N2  3 mód  300 XP
4. VCM      N1  2 mód  200 XP          4. VCM      N2  3 mód  300 XP
5. ICI      N1  2 mód  200 XP          5. ICI      N2  3 mód  300 XP
```

Cada bloque anclado a un hito real (H01, H04, H05, H07, H08) para que se vea *por qué ahora*
le toca esa dimensión.

**Permisos (S-35):** `ve_panel_institucional` es `true` para Rectoría y Coordinación de
Calidad —están en Junta Directiva / Central / Aseguramiento— y `false` para Pablo. El
permiso sale de la **membresía de comité**, no del cargo.

### 5. El canario, en el sistema corriendo

Desde `/docs`, con el `id` de Pablo y el `bloque_ruta_id` de su bloque 1:

1. `GET /bloques-ruta/{bloque_ruta_id}/clave-de-respuestas` → las respuestas correctas.
   *(Solo funciona con `MODO_DEV=true` **y** contenido de prueba. Sobre contenido real
   responde 403 aunque el modo dev esté encendido.)*
2. `POST /intentos` con `colaborador_id` y `bloque_ruta_id` → te devuelve 5 `items_servidos`.
3. `POST /intentos/{id}/respuestas` por cada ítem — **contesta mal a propósito**.
4. `POST /intentos/{id}/cerrar` → debes ver:

```json
{ "aprobado": false, "puntaje": 0.4, "insignia_id": null, "xp_otorgado": 0 }
```

5. `GET /colaboradores/{id}/estado` → `insignias: 0`, `xp_acreditable: 0`, `escalon: "Explorador"`.

**Eso es el canario cantando dentro del sistema desplegado.**

Ahora repite contestando bien: `aprobado: true`, `xp_otorgado: 400`, y en
`GET /colaboradores/{id}/insignias` la medalla aparece **con el intento que la respalda**
(número de intento y puntaje). Auditable por diseño.

Aprieta `cerrar` **dos veces**: el XP no se duplica y la insignia sigue siendo una (S-13).

### 6. Ranking y Plaza

| URL | Qué debes ver |
|---|---|
| http://localhost:8010/ranking | Posiciones con desempate de S-15. El escalón usa XP acreditable; la posición, el total. |
| http://localhost:2567/ | La Plaza. Sigue funcionando igual que en el Hito 1. |
| http://localhost:2567/salud | `{"ok":true,"servicio":"realtime"}` |

---

## Empezar de cero

```bash
docker compose down -v && docker compose up
```

Borra la base y vuelve a sembrar. Útil para repetir el canario desde limpio.

## Lo que todavía NO está

- **Frontend.** No hay `web` en el compose: la UI es D1–D7. Por ahora la interfaz es `/docs`.
- **Contenido oficial.** Las 15 unidades ya tienen microlearning y banco de ítems reales,
  pero marcados `es_contenido_prueba: true`: sirven para validar la máquina. El material CNA
  lo aporta AIEP y entra por el mismo generador cambiando `fuente_de_contenido`.
- **Login.** Los endpoints no piden identidad todavía: el adapter va en C4. Por eso puedes
  consultar cualquier colaborador — el aislamiento por cargo (I-10) se implementa y se
  prueba en la Tanda 4.
- **`clave-de-respuestas`** se elimina antes de producción (tarea D8).
