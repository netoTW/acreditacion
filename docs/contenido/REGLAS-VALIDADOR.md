# Reglas del Validador de Integridad

> CLAUDE.md §9. El Validador es **código, no criterio de agente**: un agente nunca es juez
> cuando existe un test. Lo que no pasa acá **no se integra**.

## Bloque 1 — Regresión de integridad de completitud

Set congelado que verifica los cinco invariantes de CLAUDE.md §4 contra
[ADR-005](../decisiones/ADR-005-integridad-de-completitud.md).

| # | Caso | Debe ocurrir |
|---|---|---|
| I-1 | Aprobar la evaluación al 80% o más | Se otorga la insignia, con `intento_evaluacion_id` apuntando al intento aprobado |
| I-2 | Reprobar bajo el umbral | Cero insignias · cero XP acreditable · nivel sin cambio · bloque no completo |
| I-3 | Sumar XP sin evento de origen | Imposible: `origen_tipo`/`origen_id` son NOT NULL |
| I-4 | Intentar XP negativo | Rechazado por `CHECK (xp >= 0)` |
| I-5 | Editar el nivel de un colaborador | Imposible: no existe la columna, el nivel es derivado |
| I-6 | Reenviar la misma evaluación dos veces | Segundo envío devuelve el resultado del primero · un solo evento de XP (S-13) |
| I-7 | Agotar los 3 reintentos | Bloque en `requiere_acompanamiento` · sin insignia (S-11) |
| I-8 | Intento expirado a las 24 h | Cerrado como no aprobado · consume reintento · no otorga nada (S-12) |
| I-9 | Jugar trivia hasta superar el umbral de un nivel | El nivel **no** sube: el XP lúdico no cuenta para nivel ni completitud (S-04) |
| I-10 | Pedir un bloque de contenido que no está en la ruta propia | 404 — nunca contenido de otro cargo (CLAUDE.md §3) |

## Bloque 2 — El canario

**Corre en CI antes de que exista la primera medalla del sistema** (gate C3).

> Un colaborador rinde una evaluación y la reprueba deliberadamente.
> Al terminar: **cero insignias**. Si aparece una, el build se bloquea.

**Canario de esquema**, que verifica que la garantía siga siendo estructural:

- `INSERT` de insignia con `intento_evaluacion_id = NULL` → la base **debe** rechazarlo.
- `INSERT` de insignia apuntando a un intento con `aprobado = false` → la base **debe**
  rechazarlo.
- `UPDATE` o `DELETE` sobre `evento_gamificacion` → **debe** fallar por permisos.

Si alguno de estos pasa, alguien aflojó el esquema en una migración y hay que detenerse.

## Bloque 3 — Validación del contenido generado

Todo lo que produce el Generador pasa por acá antes de integrarse.

**Estructurales** (contra [`schema-bloque-contenido.json`](schema-bloque-contenido.json)):

1. Valida el schema completo. Si no valida, se rechaza sin más análisis.
2. `es_contenido_prueba` es `true`. Sin excepción en esta etapa.
3. Cantidad de módulos coherente con el nivel: N1→2, N2→3, N3→4.
4. En un bloque de nivel N, existe al menos un módulo de cada `nivel_estandar_origen` de 1
   a N. Si falta un tramo, el anidamiento está roto.

**De ítems:**

5. Cada ítem tiene exactamente 4 alternativas y 4 explicaciones, una por alternativa.
6. `indice_correcta` está en rango. Por construcción del schema no puede haber dos correctas
   ni ninguna.
7. Ninguna explicación está vacía ni es un placeholder (`lorem`, `TODO`, `...`, texto
   repetido entre alternativas).
8. **Sin ítems duplicados**: hash normalizado del enunciado, único dentro de la evaluación.
   Normalización: minúsculas, sin tildes, sin puntuación, espacios colapsados.
9. **Sin alternativas duplicadas** dentro de un mismo ítem.
10. El banco tiene al menos **3 × `n_items_por_intento`** ítems. Con menos, barajar no
    produce pruebas distintas y el reintento sería la misma prueba (S-06).

**De coherencia con el dominio:**

11. `dimension` es uno de los 5 códigos oficiales.
12. Si el ítem declara `criterio_codigo`, ese criterio existe en el bloque.
13. El XP de la medalla y de los módulos es coherente con la tabla de XP por nivel (S-37).

**Anti-degeneración** — atrapa contenido que valida pero no sirve:

14. Ningún par de ítems del banco tiene similitud de enunciado mayor a 0,9.
15. La alternativa correcta no es sistemáticamente la más larga: se compara el largo medio
    de correctas contra incorrectas en todo el banco y se exige que no haya sesgo marcado.
16. La posición de la correcta está razonablemente repartida entre las 4 posiciones del
    banco: si más del 50% cae en la misma posición, se rechaza.

> Las reglas 14 a 16 existen porque un generador basado en modelo de lenguaje tiende a
> producir bancos donde la respuesta correcta se adivina sin saber la materia. Un banco así
> pasa el schema y arruina la evidencia: alguien aprobaría sin saber, y la insignia sería
> técnicamente válida pero institucionalmente falsa.

## Bloque 4 — Tests espejo

Cada módulo que toca XP, nivel, medallas o completitud verifica el mismo invariante desde su
lado: generador · integrador · motor de gamificación · evaluación · juegos · API · dashboard.
Ningún constructor puede romper el invariante sin que el test de otro lo delate.

## Qué pasa cuando algo falla

- **Contenido rechazado** → no se integra, queda en estado `rechazado` con el detalle, y se
  regenera. Nunca se integra "arreglándolo a mano".
- **Invariante o canario en rojo** → build bloqueado. No es un resultado: es una detención.
- **Tres fallos de gate seguidos** → `LIMITE-ENCONTRADO.md` y plan de destrabe en
  `BITACORA.md`, según CLAUDE.md §14.
