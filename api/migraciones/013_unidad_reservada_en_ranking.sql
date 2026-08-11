-- =============================================================================
-- 013 — La unidad chica tampoco se nombra en el ranking institucional
-- =============================================================================
--
-- Detectado revisando el ranking en pantalla: la vista `ranking_en_unidad` no
-- deja desglosar una unidad bajo el umbral, pero el ranking INSTITUCIONAL no
-- agrupa por unidad y aun así **publicaba el nombre de la unidad** junto al de
-- la persona. Con una unidad de tres, ver «Nombre Apellido · Escuela X» en una
-- tabla pública identifica a un miembro de un grupo bajo el umbral y expone su
-- posición: la misma filtración que el umbral existe para impedir, entrando por
-- otra puerta.
--
-- El arreglo va donde va todo lo demás: en la vista. La persona sigue en la
-- tabla —su posición es suya y no la esconde nadie—; lo que se reserva es la
-- etiqueta que la vuelve ubicable dentro de un grupo diminuto.

CREATE OR REPLACE VIEW ranking_institucional AS
WITH ultima AS (
  SELECT colaborador_id, MAX(ocurrido_en) AS ultimo_avance
    FROM evento_gamificacion
   WHERE clase_xp = 'acreditable'
   GROUP BY colaborador_id
),
grandes AS (
  SELECT unidad_id
    FROM colaborador
   WHERE unidad_id IS NOT NULL
   GROUP BY unidad_id
  HAVING count(*) >= fn_umbral_anonimato()
)
SELECT
  ec.colaborador_id,
  ec.nombre,
  -- Solo se nombra la unidad si pasa el umbral. Si no, la fila queda sin etiqueta.
  CASE WHEN g.unidad_id IS NOT NULL THEN u.nombre END AS unidad,
  ec.xp_ranking,
  ec.xp_acreditable,
  ec.xp_ludico,
  ec.escalon,
  ec.insignias,
  RANK() OVER (ORDER BY ec.xp_ranking DESC, ul.ultimo_avance ASC NULLS LAST,
                        ec.nombre ASC) AS posicion,
  count(*) OVER ()                     AS personas
FROM estado_colaborador ec
JOIN colaborador c ON c.id = ec.colaborador_id
LEFT JOIN unidad u  ON u.id = c.unidad_id
LEFT JOIN grandes g ON g.unidad_id = c.unidad_id
LEFT JOIN ultima ul ON ul.colaborador_id = ec.colaborador_id;
