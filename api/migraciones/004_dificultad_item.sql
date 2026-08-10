-- =============================================================================
-- 004 — Dificultad del ítem
--
-- El Generador la produce desde siempre (1 reconocer, 2 distinguir, 3 aplicar)
-- pero la migración 001 nunca creó la columna, así que se perdía al integrar.
--
-- La necesita M2 «Ascenso» para armar sus tramos: la escalera del juego ES la
-- escalera cognitiva del contenido, y sin este dato habría que adivinarla.
-- =============================================================================

ALTER TABLE item_evaluacion
  ADD COLUMN dificultad smallint CHECK (dificultad BETWEEN 1 AND 3);

ALTER TABLE item_quiz_formativo
  ADD COLUMN dificultad smallint CHECK (dificultad BETWEEN 1 AND 3);

-- Los juegos piden ítems por dificultad dentro de una evaluación.
CREATE INDEX ix_item_dificultad ON item_evaluacion (evaluacion_id, dificultad);
