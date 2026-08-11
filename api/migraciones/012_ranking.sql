-- =============================================================================
-- 012 — Ranking: la tabla competitiva, con sus dos límites
-- =============================================================================
--
-- Dos reglas que no dependen de la pantalla:
--
-- 1. **El tope.** El orden lo da `xp_ranking`, que ya trae el XP lúdico contado
--    solo hasta donde llega el acreditable (migración 005). Quien no avanza en su
--    ruta no escala jugando; quien avanza es premiado por jugar. El ranking usa
--    ese valor y nunca el lúdico crudo.
--
-- 2. **El umbral de anonimato.** Un ranking nominal dentro de una unidad de 3
--    personas publica la posición de alguien identificable. `ranking_en_unidad`
--    simplemente NO TIENE FILAS para esas unidades: no es que la pantalla las
--    esconda, es que no existen. Mismo umbral que el panel.
--
-- El desempate se calcula con un JOIN y no con una subconsulta por persona, que
-- es lo que hacía la vista original: con 85.000 personas eso son 85.000
-- subconsultas cada vez que alguien abre la pantalla.

-- -----------------------------------------------------------------------------
-- Institucional. Se sirve SIEMPRE acotado a la cabeza; la vista tiene el orden.
-- -----------------------------------------------------------------------------
CREATE VIEW ranking_institucional AS
WITH ultima AS (
  SELECT colaborador_id, MAX(ocurrido_en) AS ultimo_avance
    FROM evento_gamificacion
   WHERE clase_xp = 'acreditable'
   GROUP BY colaborador_id
)
SELECT
  ec.colaborador_id,
  ec.nombre,
  u.nombre AS unidad,
  ec.xp_ranking,
  ec.xp_acreditable,
  ec.xp_ludico,
  ec.escalon,
  ec.insignias,
  -- S-15: primero el XP topeado; a igualdad, quien llegó antes; luego alfabético.
  RANK() OVER (ORDER BY ec.xp_ranking DESC, ul.ultimo_avance ASC NULLS LAST,
                        ec.nombre ASC) AS posicion,
  count(*) OVER ()                     AS personas
FROM estado_colaborador ec
JOIN colaborador c ON c.id = ec.colaborador_id
LEFT JOIN unidad u ON u.id = c.unidad_id
LEFT JOIN ultima ul ON ul.colaborador_id = ec.colaborador_id;

-- -----------------------------------------------------------------------------
-- Dentro de la propia unidad. Acá vive el candado de privacidad.
-- -----------------------------------------------------------------------------
-- Es el ranking sano: se compite con los pares, el grupo es chico y la posición
-- significa algo. Pero por lo mismo, en un grupo bajo el umbral cada fila es una
-- persona señalada — por eso esas unidades no producen filas.
CREATE VIEW ranking_en_unidad AS
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
  c.unidad_id,
  u.nombre AS unidad,
  ec.nombre,
  ec.xp_ranking,
  ec.escalon,
  ec.insignias,
  RANK() OVER (PARTITION BY c.unidad_id
               ORDER BY ec.xp_ranking DESC, ul.ultimo_avance ASC NULLS LAST,
                        ec.nombre ASC)  AS posicion,
  count(*) OVER (PARTITION BY c.unidad_id) AS personas
FROM estado_colaborador ec
JOIN colaborador c   ON c.id = ec.colaborador_id
JOIN unidad u        ON u.id = c.unidad_id
JOIN grandes g       ON g.unidad_id = c.unidad_id
LEFT JOIN ultima ul  ON ul.colaborador_id = ec.colaborador_id;

COMMENT ON VIEW ranking_en_unidad IS
  'Ranking nominal dentro de la unidad. Las unidades con menos personas que '
  'fn_umbral_anonimato() no aparecen: en un grupo chico, una posición nominal '
  'identifica a una persona (Ley 21.719).';

-- -----------------------------------------------------------------------------
-- Entre unidades. Agregado, con el mismo plegado del panel.
-- -----------------------------------------------------------------------------
-- Compara promedios, no personas: una sede grande no gana por ser grande.
CREATE VIEW ranking_unidades AS
WITH agg AS (
  SELECT COALESCE(u.nombre, 'Sin unidad asignada') AS unidad,
         COALESCE(u.tipo, 'sin_unidad')            AS tipo,
         count(*)                                  AS personas,
         AVG(ec.xp_ranking)::numeric(10,1)         AS xp_promedio,
         SUM(ec.insignias)                         AS insignias,
         AVG(m.bloques_completos::numeric / NULLIF(m.bloques, 0))::numeric(5,4) AS avance,
         count(*) FILTER (WHERE ec.xp_acreditable > 0)::numeric / count(*)      AS con_avance
    FROM estado_colaborador ec
    JOIN colaborador c        ON c.id = ec.colaborador_id
    JOIN metrica_colaborador m ON m.colaborador_id = ec.colaborador_id
    LEFT JOIN unidad u        ON u.id = c.unidad_id
   GROUP BY 1, 2
)
SELECT unidad, tipo, false AS es_reservado, personas, xp_promedio, insignias,
       avance, con_avance,
       RANK() OVER (ORDER BY xp_promedio DESC) AS posicion
  FROM agg WHERE personas >= fn_umbral_anonimato()
UNION ALL
SELECT 'Unidades con menos de ' || fn_umbral_anonimato() || ' personas', 'reservado',
       true, SUM(personas), AVG(xp_promedio)::numeric(10,1), SUM(insignias),
       AVG(avance)::numeric(5,4), AVG(con_avance), NULL
  FROM agg WHERE personas < fn_umbral_anonimato()
 HAVING SUM(personas) >= fn_umbral_anonimato();
