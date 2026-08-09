# ADR-005 — La integridad de completitud se impone en el esquema, no en la lógica

**Estado:** aceptado · **Fecha:** 2026-08-09 · **Decide:** arquitecto · **Implementa:** CLAUDE.md §4

## Contexto

El invariante máximo del proyecto es que cuando el sistema dice "cumplió", sea verdad,
porque eso es evidencia ante la CNA. La fuente institucional usa exactamente el mismo
estándar para la evidencia de acreditación: información **válida, confiable y verificable**.

La forma habitual de implementar esto —validar en la capa de servicio antes de otorgar la
medalla— **no alcanza**. Deja la puerta abierta a que un constructor futuro, un script de
seed, una migración o una corrección manual creen una insignia sin respaldo. En un sistema
que va a ser tocado por varios agentes en paralelo, una convención de código no es una
garantía.

## Decisión

**Los invariantes se expresan como restricciones de la base de datos.** Violarlos tiene que
ser un error del motor, no un test que alguien recuerde correr.

### 1. Ninguna insignia sin su intento aprobado

```sql
insignia.intento_evaluacion_id  NOT NULL  REFERENCES intento_evaluacion(id)
```

Más un trigger que verifica que el intento referenciado tenga `aprobado = true`. **Una
insignia sin respaldo no es un bug: es imposible de insertar.** Esto realiza CLAUDE.md §4.1
y §4.4 al mismo tiempo, y hace que la auditoría "¿qué respalda esta medalla?" sea un JOIN,
no una investigación.

También: `UNIQUE (colaborador_id, definicion_medalla_id)` — la misma medalla no se otorga
dos veces.

### 2. El XP nunca es negativo y siempre tiene origen

```sql
evento_gamificacion.xp             CHECK (xp >= 0)
evento_gamificacion.origen_tipo    NOT NULL
evento_gamificacion.origen_id      NOT NULL
evento_gamificacion.clave_idempotencia  UNIQUE
```

La tabla es **append-only**: sin `UPDATE`, sin `DELETE`, revocado por permisos del rol de
aplicación. Corregir es emitir un evento compensatorio, nunca editar la historia. Realiza
§4.2 y, de paso, S-13: el doble envío de una evaluación choca contra el índice único de
`clave_idempotencia` y devuelve el resultado del primer envío.

### 3. El nivel no existe como dato

No hay columna `nivel` en `colaborador`. El nivel se calcula en una vista:

```sql
CREATE VIEW estado_colaborador AS
  SELECT colaborador_id,
         SUM(xp) FILTER (WHERE clase_xp = 'acreditable') AS xp_acreditable,
         SUM(xp)                                          AS xp_total,
         ...
  FROM evento_gamificacion GROUP BY colaborador_id;
```

**No se puede desincronizar porque no se guarda.** Realiza §4.3. El ranking usa
`xp_total`; el nivel y toda decisión de completitud usan `xp_acreditable`.

### 4. El XP lúdico no puede producir completitud

Ratificado por el director como decisión nivel 2 (S-04). La trivia de la cáscara entrega
`20 + racha×10` XP con "jugar de nuevo" ilimitado: sin esta separación, alguien llega a
Maestro de Acreditación sin aprobar una evaluación.

`clase_xp` es `NOT NULL` y solo `'acreditable'` proviene de módulos y evaluaciones
aprobadas. Los juegos solo pueden emitir `'ludico'`, con tope diario (S-05). El cálculo de
nivel filtra por clase; el ranking no.

### 5. Un intento reprobado no deja residuo

El intento es la única fuente de verdad de la evaluación. Reprobar cierra el intento con
`aprobado = false` y **no emite ningún evento de XP acreditable**. No hay crédito parcial,
no hay XP por preguntas correctas dentro de un intento reprobado. Realiza §4.5.

## El canario

Caso congelado en la suite, corriendo en CI **antes de que exista la primera medalla del
sistema** (gate C3 del orden de trabajo):

> Un colaborador rinde una evaluación y la reprueba deliberadamente. Al terminar:
> cero insignias, cero XP acreditable, nivel sin cambio, y el bloque no queda completo.

Si el canario produce insignia, **el build se bloquea**. No es un test más: es la condición
de existencia del sistema.

Se acompaña de un **canario de esquema**: un test que intenta insertar directamente una
insignia con `intento_evaluacion_id` nulo y otro con un intento reprobado, y **exige que la
base de datos los rechace**. Eso verifica que la garantía sigue siendo estructural y que
nadie la aflojó en una migración.

## Tests espejo

Cada módulo que toque XP, nivel, medallas o completitud lleva su propia verificación del
mismo invariante desde su lado: generador, integrador, motor, evaluación, juegos, API y
dashboard. Ningún constructor puede romperlo sin que el test de otro lo delate.

## Alternativas descartadas

**Validar solo en la capa de servicio.** Es la práctica común y es insuficiente acá: no
protege contra seeds, migraciones, correcciones manuales ni contra un constructor que
agregue una ruta de código nueva.

**Guardar `nivel` y `xp` desnormalizados por rendimiento.** Descartada: crea la posibilidad
de desincronización, que es exactamente lo prohibido por §4.3. Si el cálculo pesa, se
resuelve con vista materializada refrescada por evento — derivada, nunca editable.

## Cómo se revierte

No se revierte. Es el invariante máximo del proyecto. Si alguna restricción resulta
inviable técnicamente, se escala a nivel 3 antes de aflojarla, nunca después.
