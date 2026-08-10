-- =============================================================================
-- 003 — Ítems del quiz formativo
--
-- El Generador ya los producía dentro de cada módulo, pero no existía dónde
-- guardarlos y el Integrador los descartaba. Van en tabla propia y NO en
-- `item_evaluacion`, por una razón de fondo:
--
--   el quiz formativo entrega la respuesta correcta al cliente para dar feedback
--   inmediato (S-07). El banco de la evaluación no la entrega jamás. Si vivieran
--   en la misma tabla, una consulta distraída filtraría el banco.
--
-- Separarlos hace que ese error sea imposible de cometer.
-- =============================================================================

CREATE TABLE item_quiz_formativo (
  id               uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  modulo_id        uuid NOT NULL REFERENCES modulo(id) ON DELETE CASCADE,
  orden            smallint NOT NULL,
  enunciado        text NOT NULL,
  alternativas     jsonb NOT NULL,
  indice_correcta  smallint NOT NULL CHECK (indice_correcta BETWEEN 0 AND 3),
  explicaciones    jsonb NOT NULL,
  hash_enunciado   text NOT NULL,
  UNIQUE (modulo_id, hash_enunciado),
  UNIQUE (modulo_id, orden),
  CHECK (jsonb_array_length(alternativas) = 4),
  CHECK (jsonb_array_length(explicaciones) = 4)
);

CREATE INDEX ix_quiz_modulo ON item_quiz_formativo (modulo_id, orden);
