-- =============================================================================
-- 002 — Catálogo institucional y la matriz Cargo × Dimensión
--
-- Todo lo de acá sale de la ruta oficial de AIEP (docs/DOMINIO-RUTA-AIEP.md):
-- los 13 hitos 2026–2027, la gobernanza por comités, y la matriz de ADR-003 que
-- convierte 6 cargos y 5 dimensiones en rutas distintas SIN duplicar contenido.
-- =============================================================================

-- Los 13 hitos de la ruta real. Es la columna vertebral temporal del sistema.
CREATE TABLE hito (
  id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  codigo         text NOT NULL UNIQUE,
  ruta           text NOT NULL CHECK (ruta IN ('autoevaluacion','acreditacion')),
  anio           smallint NOT NULL,
  periodo_texto  text NOT NULL,
  titulo         text NOT NULL,
  -- Nullable a propósito: la visita de pares (H13) está "por definir" en la
  -- fuente. El sistema no inventa la fecha.
  fecha_inicio   date,
  fecha_fin      date,
  orden          smallint NOT NULL UNIQUE
);

CREATE TABLE unidad (
  id               uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tipo             text NOT NULL CHECK (tipo IN ('sede','escuela','direccion_nacional')),
  nombre           text NOT NULL UNIQUE,
  unidad_padre_id  uuid REFERENCES unidad(id)
);

-- Gobernanza de la fuente: junta directiva, aseguramiento, central, por
-- dimensión, sedes y escuelas. De acá salen los permisos institucionales (S-35),
-- no de un cargo inventado.
CREATE TABLE comite (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tipo          text NOT NULL CHECK (tipo IN ('junta_directiva','aseguramiento_calidad',
                                              'central_autoevaluacion','por_dimension',
                                              'sede','escuela')),
  nombre        text NOT NULL UNIQUE,
  dimension_id  uuid REFERENCES dimension(id),
  unidad_id     uuid REFERENCES unidad(id),
  CHECK (tipo <> 'por_dimension' OR dimension_id IS NOT NULL),
  CHECK (tipo NOT IN ('sede','escuela') OR unidad_id IS NOT NULL)
);

CREATE TABLE membresia_comite (
  colaborador_id  uuid NOT NULL REFERENCES colaborador(id),
  comite_id       uuid NOT NULL REFERENCES comite(id),
  rol_en_comite   text NOT NULL DEFAULT 'integrante',
  PRIMARY KEY (colaborador_id, comite_id)
);

-- LA MATRIZ (ADR-003). 6 cargos × 5 dimensiones = 30 filas.
-- Cada cargo toca las 5 dimensiones con nivel >= 1 —la acreditación es de todos—
-- y se diferencia por dónde se le exige profundidad.
CREATE TABLE exigencia_cargo_dimension (
  cargo_id        uuid NOT NULL REFERENCES cargo(id),
  dimension_id    uuid NOT NULL REFERENCES dimension(id),
  nivel_estandar  smallint NOT NULL CHECK (nivel_estandar BETWEEN 1 AND 3),
  orden_en_ruta   smallint NOT NULL,
  hito_id         uuid REFERENCES hito(id),
  PRIMARY KEY (cargo_id, dimension_id),
  UNIQUE (cargo_id, orden_en_ruta)
);

-- Módulos del bloque. La cantidad escala con el nivel (S-32): N1→2, N2→3, N3→4,
-- porque el contenido CNA está anidado (el nivel 3 incluye al 2 y el 2 al 1).
-- El Generador (C5) los llena; acá quedan como estructura.
CREATE TABLE modulo (
  id                     uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  bloque_contenido_id    uuid NOT NULL REFERENCES bloque_contenido(id),
  orden                  smallint NOT NULL,
  titulo                 text NOT NULL,
  cuerpo                 text NOT NULL DEFAULT '',
  duracion_min           smallint NOT NULL DEFAULT 12,
  xp                     integer NOT NULL CHECK (xp >= 0),
  -- En qué tramo se generó. Un bloque N3 incluye módulos con origen 1, 2 y 3.
  nivel_estandar_origen  smallint NOT NULL CHECK (nivel_estandar_origen BETWEEN 1 AND 3),
  UNIQUE (bloque_contenido_id, orden)
);

ALTER TABLE cargo       ADD COLUMN descripcion text;
ALTER TABLE colaborador ADD COLUMN unidad_id uuid REFERENCES unidad(id);
ALTER TABLE bloque_ruta ADD COLUMN hito_id  uuid REFERENCES hito(id);

CREATE INDEX ix_comite_unidad ON comite (unidad_id);
CREATE INDEX ix_colab_unidad  ON colaborador (unidad_id);

-- ¿Quién ve el panel institucional? Quien está en el Comité de Aseguramiento de
-- la Calidad, en el Comité Central, o en la Dirección Nacional (S-35).
CREATE VIEW permiso_institucional AS
SELECT DISTINCT c.id AS colaborador_id
  FROM colaborador c
  LEFT JOIN membresia_comite mc ON mc.colaborador_id = c.id
  LEFT JOIN comite co ON co.id = mc.comite_id
  LEFT JOIN unidad u  ON u.id = c.unidad_id
 WHERE co.tipo IN ('aseguramiento_calidad','central_autoevaluacion','junta_directiva')
    OR u.tipo = 'direccion_nacional';

-- Ranking con el desempate de S-15: XP total, luego constancia (el último evento
-- acreditable más antiguo gana), luego alfabético.
CREATE VIEW ranking AS
SELECT
  ec.colaborador_id,
  ec.nombre,
  u.nombre AS unidad,
  ec.xp_total,
  ec.xp_acreditable,
  ec.escalon,
  ec.insignias,
  RANK() OVER (
    ORDER BY ec.xp_total DESC,
             (SELECT MAX(e.ocurrido_en) FROM evento_gamificacion e
               WHERE e.colaborador_id = ec.colaborador_id AND e.clase_xp = 'acreditable')
             ASC NULLS LAST,
             ec.nombre ASC
  ) AS posicion
FROM estado_colaborador ec
JOIN colaborador c ON c.id = ec.colaborador_id
LEFT JOIN unidad u ON u.id = c.unidad_id;
