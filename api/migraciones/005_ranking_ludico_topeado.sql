-- =============================================================================
-- 005 — El XP lúdico cuenta para el ranking hasta el tope del acreditable
--
-- Regla ratificada por el director:
--
--   «Jugar puede como mucho duplicar tu posición, nunca reemplazar el recorrido.»
--
-- Sin esto, con tres motores pagando, el XP de juego termina superando al
-- acreditable y el ranking pasa a medir cuánto juegas y no cuánto avanzas.
-- Quien no avanza en su ruta no escala jugando; quien avanza es premiado.
--
-- El invariante no cambia en nada: el escalón y la completitud siguen derivando
-- SOLO del XP acreditable, y la medalla solo nace de la evaluación aprobada.
-- Esto toca el orden del ranking, nada más.
-- =============================================================================

-- Se recrean las dos, en orden de dependencia: `CREATE OR REPLACE VIEW` solo deja
-- agregar columnas AL FINAL, y acá `xp_ludico` entra en medio.
DROP VIEW IF EXISTS ranking;
DROP VIEW IF EXISTS estado_colaborador;

CREATE VIEW estado_colaborador AS
SELECT
  c.id AS colaborador_id,
  c.nombre,
  COALESCE(SUM(e.xp) FILTER (WHERE e.clase_xp = 'acreditable'), 0)::bigint AS xp_acreditable,
  COALESCE(SUM(e.xp) FILTER (WHERE e.clase_xp = 'ludico'), 0)::bigint      AS xp_ludico,
  COALESCE(SUM(e.xp), 0)::bigint                                           AS xp_total,
  -- Lo que ordena el ranking: todo lo acreditable, más lo lúdico hasta igualarlo.
  (COALESCE(SUM(e.xp) FILTER (WHERE e.clase_xp = 'acreditable'), 0)
   + LEAST(
       COALESCE(SUM(e.xp) FILTER (WHERE e.clase_xp = 'ludico'), 0),
       COALESCE(SUM(e.xp) FILTER (WHERE e.clase_xp = 'acreditable'), 0)
     ))::bigint AS xp_ranking,
  fn_escalon(COALESCE(SUM(e.xp) FILTER (WHERE e.clase_xp = 'acreditable'), 0)::bigint) AS escalon,
  (SELECT count(*) FROM insignia i WHERE i.colaborador_id = c.id) AS insignias
FROM colaborador c
LEFT JOIN evento_gamificacion e ON e.colaborador_id = c.id
GROUP BY c.id, c.nombre;

CREATE VIEW ranking AS
SELECT
  ec.colaborador_id,
  ec.nombre,
  u.nombre AS unidad,
  ec.xp_ranking,
  ec.xp_acreditable,
  ec.xp_ludico,
  ec.xp_total,
  ec.escalon,
  ec.insignias,
  RANK() OVER (
    ORDER BY ec.xp_ranking DESC,
             (SELECT MAX(e.ocurrido_en) FROM evento_gamificacion e
               WHERE e.colaborador_id = ec.colaborador_id AND e.clase_xp = 'acreditable')
             ASC NULLS LAST,
             ec.nombre ASC
  ) AS posicion
FROM estado_colaborador ec
JOIN colaborador c ON c.id = ec.colaborador_id
LEFT JOIN unidad u ON u.id = c.unidad_id;
