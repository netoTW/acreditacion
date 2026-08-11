-- =============================================================================
-- 007 — D2 Docencia · «El caso del estudiante que se pierde»
-- =============================================================================
--
-- Cada dimensión lleva su propio juego (fase 2), y cada juego trae su contenido.
-- Se le da tabla propia en vez de meterlo en el bloque de contenido porque las
-- cinco mecánicas son distintas: forzarlas a un solo schema haría un formato que
-- no le sirve bien a ninguna. El registro `motor/juegos.py` las une.
--
-- El invariante no cambia: esto no otorga completitud. El puntaje sale de acá,
-- el XP es lúdico por `origen_tipo='juego'`, y la medalla sigue naciendo solo de
-- una evaluación aprobada.

CREATE TABLE caso_cohorte (
  id                     uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  codigo                 text NOT NULL UNIQUE,
  titulo                 text NOT NULL,
  contexto               text NOT NULL,
  -- [{nombre, valor}] — cuántos estudiantes quedan en cada etapa.
  etapas                 jsonb NOT NULL,
  -- [{desde, hasta, referencia_pct}] — cuánto se conservaría normalmente.
  -- La referencia SÍ viaja al cliente: una caída no significa nada sin ella.
  tramos                 jsonb NOT NULL,
  -- Índice del tramo donde se rompe. Nunca sale al cliente antes de responder.
  tramo_quiebre          smallint NOT NULL CHECK (tramo_quiebre >= 0),
  explicacion_quiebre    text NOT NULL,
  -- [{clave, nombre, valor}] — los cuatro desviados; solo uno pertenece a la etapa.
  indicadores            jsonb NOT NULL,
  indicador_correcto     text NOT NULL,
  explicacion_indicador  text NOT NULL,
  es_contenido_prueba    boolean NOT NULL DEFAULT true
);

COMMENT ON TABLE caso_cohorte IS
  'Contenido de prueba de D2. Las cifras son sintéticas y no describen ninguna '
  'carrera real; en producción las reemplaza el corte que aporte AIEP.';
