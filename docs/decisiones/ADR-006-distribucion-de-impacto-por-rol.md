# ADR-006 — Distribución de impacto por rol

**Estado:** aceptado · **Fecha:** 2026-08-11
**Reemplaza parcialmente:** [ADR-003](ADR-003-cargo-por-dimension.md) (lo extiende, no lo anula)
**Fuente:** `docs-fuente/Impacto en dimensiones por nivel (roles).xlsx`

---

## Contexto

AIEP reemplazó los 6 cargos —que eran una taxonomía de marcador de posición (S-30)—
por **3 roles** y, sobre ellos, entregó algo que antes no existía: una **distribución
porcentual** de las 5 dimensiones por rol, más una marca de **ruta crítica**.

La pregunta que había que resolver era si eso reemplazaba el modelo `cargo × dimensión`
de ADR-003 o cabía dentro de él.

## Decisión

**Cabe dentro.** La tabla de la matriz ya tenía exactamente el grano que el modelo
nuevo necesita —una fila por `(rol, dimensión)`—; le faltaban dos columnas.

### 1. El % es el único dato que se escribe a mano

El nivel de exigencia CNA y la criticidad **se derivan** de él, igual que el escalón se
deriva del XP. Lo derivable no se transcribe, porque transcribir es lo que se
desincroniza.

- **Corte %→nivel:** ≥25% → 3, 15–24% → 2, ≤10% → 1. Es una derivación del arquitecto
  y está marcada como tal (S-48): la fuente da el % y la 🔴, pero no el nivel.
- **Criticidad:** las 2 dimensiones de mayor peso del rol.

El hallazgo que hace todo esto coherente: **las 🔴 del Excel son exactamente las 2 de
mayor peso, en los tres roles, y con ese corte caen siempre en nivel 3**. Las tres
marcas son la misma casilla. Hay un test que contrasta la derivación contra las 🔴
transcritas una sola vez, para que si dejaran de coincidir se note.

Consecuencia práctica: la matriz derivada usa **9 de las 15 unidades ya generadas**.
No hubo que regenerar contenido por el cambio de modelo.

### 2. La estructura es la misma en las cinco dimensiones; la crítica SUMA

| | Estándar | Crítica |
|---|---|---|
| Módulos con quiz | 2 | 2 |
| Juego de la dimensión | 1 (fase 2) | 1 (fase 2) |
| Desafío aplicado | — | **1** |
| Umbral | 80% | **85%** |
| Medalla | silver | **gold** |
| Profundidad | según nivel | según nivel |

Lo que escala con el nivel de exigencia ya no es *cuántas piezas hay* sino *cuánto
trae cada una*: quices de 3/5/7 ítems y evaluaciones de 4/6/8 (S-50). Esto obligó a
revisar S-32, que fijaba 2/3/4 módulos por nivel.

**Ninguna dimensión se vuelve opcional.** La criticidad agrega exigencia; todos
recorren las cinco. La base lo verifica: un rol que no cubra las 5 dimensiones es
rechazado.

### 3. La criticidad vive en la RUTA, no en el contenido

El contenido se sigue generando una vez por `(dimensión, nivel)` y es **compartido
entre roles**. El mismo bloque es crítico para un rol y estándar para otro. Por eso
el umbral reforzado, el peso y la criticidad viven en `bloque_ruta`, y cada bloque de
contenido define **las dos medallas**; cuál se otorga lo decide la ruta de la persona.

Sin esto, reforzar el umbral habría sido imposible sin duplicar contenido, que es
justo lo que ADR-003 existe para evitar.

## Lo que NO cambia

El invariante de ADR-005, entero:

- La medalla —de cualquier rango— **solo nace de una evaluación aprobada**, verificado
  por `insignia.intento_evaluacion_id NOT NULL` + trigger.
- El **desafío aplicado no otorga completitud**: da XP lúdico y abre la puerta de la
  evaluación reforzada. Usa `origen_tipo='juego'`, que el CHECK de la migración 001 ya
  obliga a ser lúdico — la regla queda en la base, no en una convención.
- El XP sigue siendo dual, el escalón sigue derivándose solo del acreditable, y el
  tope de ranking sigue vigente.

## Candados nuevos (migración 006), todos verificados por el banco de mutación

1. La distribución de un rol **suma 1** y tiene **exactamente 2 críticas**, sobre las
   **5 dimensiones**. Va como constraint diferido: es una condición del conjunto de
   filas de un rol, no de una fila.
2. El veredicto del intento se verifica contra el **umbral efectivo** —el de la ruta si
   existe—. Sin esto, un 80% en la dimensión crítica habría pasado como aprobado y el
   refuerzo habría sido decorativo.
3. Una dimensión crítica **no puede quedar con umbral estándar**, ni al revés.
4. La **gold no se otorga** donde la dimensión no es crítica en esa ruta, y una crítica
   **no entrega un rango menor**.
5. Una persona no acumula dos insignias del mismo bloque de contenido.
6. El desafío **solo se resuelve sobre un bloque crítico de la ruta propia**.

## Alternativas descartadas

- **Que el % controlara cuántos módulos recibe cada dimensión.** Contradice la
  estructura idéntica que AIEP fijó, y con 5 dimensiones el redondeo dejaba bloques
  de 0 piezas.
- **Que la ruta crítica volviera opcionales las demás dimensiones.** Rompe «la
  acreditación es de todos», que viene de la fuente de AIEP, y dejaría a casi todos
  con 3 medallas de 5.
- **Bajar el umbral en las dimensiones estándar.** Debilita el relato de la medalla,
  que hoy es nítido. El refuerzo se aplica solo hacia arriba.
- **Eliminar `nivel_estandar` y dejar una unidad por dimensión.** Simplificaba a 5
  unidades pero botaba contenido ya validado y el fundamento de ADR-003.

## Pendientes con AIEP

- **S-48** — confirmar el corte %→nivel, o reemplazarlo por el suyo.
- **S-49** — en qué rol caen los docentes de aula. Provisional: N2.
