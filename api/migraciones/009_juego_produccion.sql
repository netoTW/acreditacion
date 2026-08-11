-- =============================================================================
-- 009 — D5 Investigación, Creación e Innovación · «El cuadrante de la producción»
-- =============================================================================
--
-- Dos juicios INDEPENDIENTES sobre cada pieza: si es producción ICI y si la
-- institución puede reclamarla. Son dos columnas booleanas y no un solo campo
-- «cuenta / no cuenta» a propósito: el juego enseña justamente que se pueden
-- acertar por separado, y el puntaje lo cobra por eje.
--
-- Contenido de prueba. AIEP entrega sus líneas declaradas y su criterio de
-- adscripción en la fase de contenido real (DUDAS.md).

CREATE TABLE linea_ici (
  id                   uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  clave                text NOT NULL UNIQUE,
  nombre               text NOT NULL,
  descripcion          text NOT NULL,
  es_contenido_prueba  boolean NOT NULL DEFAULT true
);

CREATE TABLE produccion_ici (
  id                     uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  codigo                 text NOT NULL UNIQUE,
  titulo                 text NOT NULL,
  tipo                   text NOT NULL,
  -- La única pista: dónde se publicó, con qué afiliación, en qué condición estaba
  -- el autor. Sin leerlo el tablero no se resuelve.
  detalle                text NOT NULL,
  es_ici                 boolean NOT NULL,
  es_adscrita            boolean NOT NULL,
  linea_clave            text REFERENCES linea_ici(clave),
  razon_ici              text NOT NULL,
  razon_adscripcion      text NOT NULL,
  es_contenido_prueba    boolean NOT NULL DEFAULT true,
  -- Lo que no es producción ICI no puede colgar de una línea de investigación.
  CONSTRAINT ck_linea_solo_si_es_ici
    CHECK (linea_clave IS NULL OR es_ici)
);

CREATE INDEX ix_produccion_cuadrante ON produccion_ici (es_ici, es_adscrita);

COMMENT ON TABLE produccion_ici IS
  'Contenido de prueba de D5. Producciones plausibles pero inventadas: no describen '
  'la actividad real de ninguna institución.';
