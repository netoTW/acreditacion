# Modelo de datos

> Contrato entre módulos. Ningún constructor inventa tablas ni campos fuera de acá.
> Terminología según [GLOSARIO.md](GLOSARIO.md). Invariantes según
> [ADR-005](decisiones/ADR-005-integridad-de-completitud.md).

## Mapa

```
CATÁLOGO (seed, viene de la ruta oficial AIEP)
  Dimension(5) ── Criterio(16)
  Hito(13)
  Cargo(6) ──┐
  Unidad ────┤
  Comite ────┘
             └── ExigenciaCargoDimension(30)   ← la matriz de ADR-003

CONTENIDO (generado una vez por par dimensión×nivel = 15 unidades)
  BloqueContenido ── Modulo ── ItemQuizFormativo
                  ├─ Evaluacion ── ItemEvaluacion
                  └─ DefinicionMedalla

PERSONAS Y RUTAS
  Colaborador ── MembresiaComite
              ├─ RespuestaDiagnostico
              └─ Ruta ── BloqueRuta ─→ BloqueContenido
                                    └─→ Hito

VERDAD (append-only, de acá se deriva todo)
  IntentoEvaluacion ── RespuestaIntento
  EventoGamificacion
  Insignia ─→ IntentoEvaluacion   (NOT NULL: el invariante en el esquema)
```

---

## Catálogo institucional

**`dimension`** — 5 filas fijas.
`id` · `codigo` (`GESTION|DOCENCIA|CALIDAD|VCM|ICI`) · `nombre_oficial` · `obligatoria` bool ·
`orden`

**`criterio`** — 16 en total. La distribución oficial no está en la fuente.
`id` · `dimension_id` FK · `codigo` · `nombre` · `es_contenido_prueba` bool

**`hito`** — 13 filas fijas de la ruta 2026–2027.
`id` · `codigo` (`H01`…`H13`) · `ruta` (`autoevaluacion|acreditacion`) · `anio` ·
`periodo_texto` · `fecha_inicio` date? · `fecha_fin` date? · `titulo` · `descripcion` · `orden`

> `fecha_*` es nullable a propósito: H13 (visita de pares) está "por definir" en la fuente.
> El sistema no inventa la fecha.

**`cargo`** — 6 filas en el slice.
`id` · `codigo` · `nombre` · `descripcion`

**`unidad`**
`id` · `tipo` (`sede|escuela|direccion_nacional`) · `nombre` · `unidad_padre_id` FK?

**`comite`**
`id` · `tipo` (`junta_directiva|aseguramiento_calidad|central_autoevaluacion|por_dimension|sede|escuela`) ·
`dimension_id` FK? · `unidad_id` FK? · `nombre`

**`membresia_comite`**
`colaborador_id` FK · `comite_id` FK · `rol_en_comite` · PK compuesta

> `CHECK`: un comité de tipo `por_dimension` exige `dimension_id NOT NULL`; uno de tipo
> `sede` o `escuela` exige `unidad_id NOT NULL`.

**`exigencia_cargo_dimension`** — **la matriz de ADR-003.** 30 filas.
`cargo_id` FK · `dimension_id` FK · `nivel_estandar` smallint `CHECK BETWEEN 1 AND 3` ·
`orden_en_ruta` · `hito_id` FK? · PK `(cargo_id, dimension_id)`

---

## Contenido generado

**`bloque_contenido`** — unidad de generación: un par (dimensión, nivel).
`id` · `dimension_id` FK · `nivel_estandar` smallint · `titulo` · `resumen` ·
`es_contenido_prueba` bool `NOT NULL DEFAULT true` · `fuente_contenido` jsonb ·
`generador_version` · `generado_en` · `validado_en`? · `estado` (`generado|validado|rechazado`)
· `UNIQUE (dimension_id, nivel_estandar)`

> Solo un bloque de contenido `validado` puede entrar en una ruta. Contenido que no pasa el
> Validador **no se integra** (CLAUDE.md §9.3).

**`modulo`**
`id` · `bloque_contenido_id` FK · `orden` · `titulo` · `cuerpo` text (microlearning) ·
`duracion_min` · `xp` int `CHECK >= 0` · `nivel_estandar_origen` smallint

> `nivel_estandar_origen` marca en qué tramo se generó el módulo. Como el nivel 3 contiene
> al 2 y el 2 al 1, un bloque de nivel 3 incluye módulos con origen 1, 2 y 3. Así el
> anidamiento es explícito y no se duplica texto.

**`item_quiz_formativo`**
`id` · `modulo_id` FK · `enunciado` · `alternativas` jsonb[] · `indice_correcta` ·
`explicaciones` jsonb[] (una por alternativa)

**`evaluacion`**
`id` · `bloque_contenido_id` FK UNIQUE · `umbral_aprobacion` numeric `DEFAULT 0.80` ·
`n_items_por_intento` · `max_reintentos` `DEFAULT 3` · `minutos_expiracion` `DEFAULT 1440`

**`item_evaluacion`** — banco de la evaluación.
`id` · `evaluacion_id` FK · `criterio_id` FK? · `enunciado` · `alternativas` jsonb[] ·
`indice_correcta` · `explicaciones` jsonb[] · `dificultad` smallint · `hash_enunciado`
`UNIQUE (evaluacion_id, hash_enunciado)` ← impide ítems duplicados en el banco

**`definicion_medalla`**
`id` · `bloque_contenido_id` FK? · `tipo` (`mini|silver|gold|master`) · `nombre` ·
`descripcion` · `xp` int `CHECK >= 0` · `dimension_id` FK? · `nivel_estandar` smallint?

> La medalla se define por (dimensión, nivel), no por cargo: "Docencia · N3" y
> "Docencia · N1" son insignias distintas. Es lo que hace que dos cargos con contenido
> compartido tengan vitrinas distintas.

---

## Personas y rutas

**`colaborador`**
`id` · `email` UNIQUE · `nombre` · `cargo_id` FK · `unidad_id` FK ·
`proveedor_identidad` (`dev|entra`) · `subject_id` · `creado_en`
**Sin columna `xp`. Sin columna `nivel`.** (ADR-005 §3)

**`respuesta_diagnostico`**
`id` · `colaborador_id` FK · `respuestas` jsonb · `nivel_dificultad_sugerido` ·
`respondido_en` · `UNIQUE (colaborador_id)` ← se responde una vez (S-02)

**`ruta`**
`id` · `colaborador_id` FK UNIQUE · `cargo_id` FK · `generada_en`

**`bloque_ruta`** — instancia: una dimensión, a un nivel, para una persona.
`id` · `ruta_id` FK · `bloque_contenido_id` FK · `hito_id` FK? · `orden` ·
`estado` (`bloqueado|disponible|en_curso|completo|requiere_acompanamiento`) ·
`UNIQUE (ruta_id, orden)`

> `requiere_acompanamiento` es el estado de S-11: se agotaron los 3 reintentos. El bloque
> **no** se cierra solo y **nunca** otorga la medalla; solo alguien con permiso institucional
> puede reabrirlo.

---

## La verdad

**`intento_evaluacion`**
`id` · `colaborador_id` FK · `bloque_ruta_id` FK · `evaluacion_id` FK · `numero_intento` ·
`estado` (`abierto|enviado|expirado`) · `items_servidos` jsonb[] (orden barajado del intento) ·
`iniciado_en` · `expira_en` · `enviado_en`? · `puntaje` numeric? · `aprobado` bool? ·
`UNIQUE (bloque_ruta_id, numero_intento)`

**`respuesta_intento`** — autosave por respuesta (§7).
`intento_id` FK · `item_id` FK · `indice_elegido` · `respondido_en` · PK `(intento_id, item_id)`

> El autosave escribe acá en cada respuesta. Por eso una caída al enviar no pierde nada:
> "enviar" solo cierra el intento (S-14).

**`evento_gamificacion`** — **append-only.** De acá se deriva todo.
`id` · `colaborador_id` FK · `tipo` · `origen_tipo` NOT NULL · `origen_id` NOT NULL ·
`xp` int `CHECK (xp >= 0)` · `clase_xp` (`acreditable|ludico`) NOT NULL ·
`clave_idempotencia` UNIQUE NOT NULL · `ocurrido_en`

> Sin `UPDATE` ni `DELETE`: revocado por permisos del rol de aplicación. Corregir es emitir
> un evento compensatorio.

**`insignia`**
`id` · `colaborador_id` FK · `definicion_medalla_id` FK ·
**`intento_evaluacion_id` FK NOT NULL** · `otorgada_en` · `open_badge_assertion_id`? ·
`UNIQUE (colaborador_id, definicion_medalla_id)`

> El `NOT NULL` más el trigger que exige `intento.aprobado = true` **es** el invariante
> máximo. Una insignia sin respaldo no es un bug: no se puede insertar.

**`mensaje_plaza`** — el chat es espacio institucional (S-24).
`id` · `colaborador_id` FK · `sala` · `texto` `CHECK (length <= 80)` · `enviado_en` ·
`reportado` bool

**`acceso_dato_personal`** — registro de auditoría de E-03.
`id` · `colaborador_id` (quien consulta) · `recurso` · `objetivo_id` · `consultado_en`

---

## Vistas derivadas

**`estado_colaborador`** — la única fuente de XP y nivel.

```sql
SELECT colaborador_id,
       COALESCE(SUM(xp) FILTER (WHERE clase_xp = 'acreditable'), 0) AS xp_acreditable,
       COALESCE(SUM(xp), 0)                                          AS xp_total
FROM evento_gamificacion
GROUP BY colaborador_id;
```

- **Nivel y completitud** ← `xp_acreditable`
- **Ranking** ← `xp_total` (S-04)

**`ranking`** — desempate por S-15: `xp_total` desc, luego fecha más antigua del último
evento acreditable, luego alfabético. Posiciones empatadas comparten número.

---

## Índices y reglas transversales

- `evento_gamificacion (colaborador_id, ocurrido_en)` — cálculo de estado y dashboard.
- `evento_gamificacion (clase_xp, ocurrido_en)` — tope diario de XP lúdico (S-05).
- `intento_evaluacion (colaborador_id, estado)` — retomar intento abierto.
- `bloque_ruta (ruta_id, estado)` — mapa de ruta.
- Todo `id` es UUID. Toda marca de tiempo es `timestamptz` en UTC.
- **Aislamiento por cargo (CLAUDE.md §3):** toda consulta de contenido pasa por
  `bloque_ruta` del colaborador. No existe endpoint que devuelva un `bloque_contenido` por
  id sin verificar que esté en la ruta de quien pregunta. Test espejo obligatorio en API.
