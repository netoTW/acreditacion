-- =============================================================================
-- 011 — Panel institucional: agregados con anonimato garantizado
-- =============================================================================
--
-- El panel es la vista de la dirección: participación, avance, aprendizaje,
-- riesgo y cultura de calidad. Y es donde el sistema deja de mirar a una persona
-- para mirar a la institución.
--
-- LA REGLA DE PRIVACIDAD VIVE ACÁ, NO EN LA PANTALLA (Ley 21.719 · E-03).
-- Un grupo de menos de 5 personas no se muestra desglosado: con n=1, decir
-- «Sede X: 100% completado» es publicar el dato de una persona identificable.
-- Ponerlo en el frontend sería confiar en que ninguna consulta futura se saltee
-- el filtro; ponerlo en la vista significa que **no existe forma de pedir el
-- desglose pequeño**, igual que I-10 para el contenido de otro rol.
--
-- Los grupos pequeños NO se borran: se pliegan en una fila «reservados». Así el
-- total institucional sigue cuadrando y nadie desaparece del denominador — que
-- es la otra forma de mentir con privacidad.
--
-- Escala: todas las métricas por persona se calculan con agregados por lote
-- (GROUP BY + LEFT JOIN), no con subconsultas correlacionadas. Con 1.600
-- funcionarios da lo mismo; con 85.000 es la diferencia entre un panel y un
-- tiempo de espera.

-- Marca para poder distinguir —y purgar— la población sintética del slice.
ALTER TABLE colaborador ADD COLUMN es_de_prueba boolean NOT NULL DEFAULT false;

CREATE INDEX ix_colab_cargo ON colaborador (cargo_id);
CREATE INDEX ix_insignia_colab ON insignia (colaborador_id);

-- El umbral de k-anonimato en un solo lugar.
CREATE FUNCTION fn_umbral_anonimato() RETURNS integer AS $$
  SELECT 5;
$$ LANGUAGE sql IMMUTABLE;

COMMENT ON FUNCTION fn_umbral_anonimato IS
  'Ley 21.719: tamaño mínimo de un grupo para poder mostrarlo desglosado. '
  'Cambiarlo acá lo cambia en todo el panel.';

-- -----------------------------------------------------------------------------
-- Métrica por persona. NO se expone: es el insumo de los agregados.
-- -----------------------------------------------------------------------------
CREATE VIEW metrica_colaborador AS
SELECT
  c.id            AS colaborador_id,
  c.unidad_id,
  c.cargo_id,
  c.es_de_prueba,
  COALESCE(b.bloques, 0)          AS bloques,
  COALESCE(b.completos, 0)        AS bloques_completos,
  COALESCE(b.en_riesgo, 0)        AS bloques_en_riesgo,
  COALESCE(b.criticos, 0)         AS bloques_criticos,
  COALESCE(b.criticos_completos, 0) AS criticos_completos,
  COALESCE(i.insignias, 0)        AS insignias,
  COALESCE(e.eventos, 0)          AS eventos,
  e.ultima_actividad,
  COALESCE(e.eventos_juego, 0)    AS eventos_juego,
  COALESCE(e.xp_acreditable, 0)   AS xp_acreditable,
  COALESCE(t.intentos, 0)         AS intentos,
  COALESCE(t.aprobados, 0)        AS intentos_aprobados,
  t.puntaje_promedio
FROM colaborador c
LEFT JOIN (
  SELECT r.colaborador_id,
         count(*)                                                    AS bloques,
         count(*) FILTER (WHERE br.estado = 'completo')              AS completos,
         count(*) FILTER (WHERE br.estado = 'requiere_acompanamiento') AS en_riesgo,
         count(*) FILTER (WHERE br.es_critica)                       AS criticos,
         count(*) FILTER (WHERE br.es_critica AND br.estado = 'completo') AS criticos_completos
    FROM bloque_ruta br JOIN ruta r ON r.id = br.ruta_id
   GROUP BY r.colaborador_id
) b ON b.colaborador_id = c.id
LEFT JOIN (
  SELECT colaborador_id, count(*) AS insignias FROM insignia GROUP BY colaborador_id
) i ON i.colaborador_id = c.id
LEFT JOIN (
  SELECT colaborador_id,
         count(*)                                             AS eventos,
         max(ocurrido_en)                                     AS ultima_actividad,
         count(*) FILTER (WHERE origen_tipo = 'juego')        AS eventos_juego,
         COALESCE(SUM(xp) FILTER (WHERE clase_xp = 'acreditable'), 0) AS xp_acreditable
    FROM evento_gamificacion GROUP BY colaborador_id
) e ON e.colaborador_id = c.id
LEFT JOIN (
  SELECT colaborador_id,
         count(*) FILTER (WHERE estado = 'enviado')  AS intentos,
         count(*) FILTER (WHERE aprobado)            AS aprobados,
         avg(puntaje) FILTER (WHERE estado = 'enviado') AS puntaje_promedio
    FROM intento_evaluacion GROUP BY colaborador_id
) t ON t.colaborador_id = c.id;

COMMENT ON VIEW metrica_colaborador IS
  'Insumo interno del panel. NO se sirve por la API: el panel expone solo '
  'agregados que pasan por el umbral de anonimato.';

-- -----------------------------------------------------------------------------
-- El resumen institucional. Sin desglose, así que no necesita umbral.
-- -----------------------------------------------------------------------------
CREATE VIEW panel_resumen AS
SELECT
  count(*)                                                          AS personas,
  count(*) FILTER (WHERE eventos > 0)                               AS con_actividad,
  count(*) FILTER (WHERE ultima_actividad > now() - interval '30 days') AS activos_30d,
  count(*) FILTER (WHERE bloques > 0 AND bloques_completos = bloques) AS rutas_completas,
  COALESCE(SUM(bloques), 0)                                         AS bloques,
  COALESCE(SUM(bloques_completos), 0)                               AS bloques_completos,
  COALESCE(SUM(bloques_criticos), 0)                                AS bloques_criticos,
  COALESCE(SUM(criticos_completos), 0)                              AS criticos_completos,
  COALESCE(SUM(insignias), 0)                                       AS insignias,
  COALESCE(SUM(intentos), 0)                                        AS intentos,
  COALESCE(SUM(intentos_aprobados), 0)                              AS intentos_aprobados,
  avg(puntaje_promedio) FILTER (WHERE intentos > 0)                 AS puntaje_promedio,
  count(*) FILTER (WHERE bloques_en_riesgo > 0)                     AS personas_en_riesgo,
  count(*) FILTER (WHERE eventos_juego > 0)                         AS personas_que_juegan,
  count(*) FILTER (WHERE es_de_prueba)                              AS personas_de_prueba
FROM metrica_colaborador;

-- -----------------------------------------------------------------------------
-- Desgloses. Acá SÍ manda el umbral.
-- -----------------------------------------------------------------------------
-- Un grupo bajo el umbral no se muestra con su nombre: se suma a «reservados».
-- Y si los reservados juntos tampoco llegan al umbral, esa fila desaparece
-- también — de otro modo, dos sedes de 2 personas se volverían una de 4 y el
-- desglose seguiría siendo demasiado fino.
CREATE VIEW panel_por_unidad AS
WITH agg AS (
  SELECT COALESCE(u.nombre, 'Sin unidad asignada') AS grupo,
         COALESCE(u.tipo, 'sin_unidad')            AS tipo,
         count(*)                                  AS personas,
         COALESCE(SUM(m.bloques), 0)               AS bloques,
         COALESCE(SUM(m.bloques_completos), 0)     AS bloques_completos,
         count(*) FILTER (WHERE m.eventos > 0)     AS con_actividad,
         count(*) FILTER (WHERE m.bloques > 0 AND m.bloques_completos = m.bloques) AS rutas_completas,
         count(*) FILTER (WHERE m.bloques_en_riesgo > 0) AS en_riesgo,
         count(*) FILTER (WHERE m.eventos_juego > 0)     AS juegan,
         COALESCE(SUM(m.intentos), 0)              AS intentos,
         COALESCE(SUM(m.intentos_aprobados), 0)    AS intentos_aprobados
    FROM metrica_colaborador m
    LEFT JOIN unidad u ON u.id = m.unidad_id
   GROUP BY 1, 2
)
SELECT grupo, tipo, false AS es_reservado, personas, bloques, bloques_completos,
       con_actividad, rutas_completas, en_riesgo, juegan, intentos, intentos_aprobados
  FROM agg WHERE personas >= fn_umbral_anonimato()
UNION ALL
SELECT 'Unidades con menos de ' || fn_umbral_anonimato() || ' personas', 'reservado',
       true, SUM(personas), SUM(bloques), SUM(bloques_completos), SUM(con_actividad),
       SUM(rutas_completas), SUM(en_riesgo), SUM(juegan), SUM(intentos),
       SUM(intentos_aprobados)
  FROM agg WHERE personas < fn_umbral_anonimato()
 HAVING SUM(personas) >= fn_umbral_anonimato();

CREATE VIEW panel_por_rol AS
WITH agg AS (
  SELECT ca.nombre                              AS grupo,
         ca.codigo                              AS tipo,
         count(*)                               AS personas,
         COALESCE(SUM(m.bloques), 0)            AS bloques,
         COALESCE(SUM(m.bloques_completos), 0)  AS bloques_completos,
         count(*) FILTER (WHERE m.eventos > 0)  AS con_actividad,
         count(*) FILTER (WHERE m.bloques > 0 AND m.bloques_completos = m.bloques) AS rutas_completas,
         count(*) FILTER (WHERE m.bloques_en_riesgo > 0) AS en_riesgo,
         count(*) FILTER (WHERE m.eventos_juego > 0)     AS juegan,
         COALESCE(SUM(m.intentos), 0)           AS intentos,
         COALESCE(SUM(m.intentos_aprobados), 0) AS intentos_aprobados
    FROM metrica_colaborador m
    JOIN cargo ca ON ca.id = m.cargo_id
   GROUP BY 1, 2
)
SELECT grupo, tipo, false AS es_reservado, personas, bloques, bloques_completos,
       con_actividad, rutas_completas, en_riesgo, juegan, intentos, intentos_aprobados
  FROM agg WHERE personas >= fn_umbral_anonimato()
UNION ALL
SELECT 'Roles con menos de ' || fn_umbral_anonimato() || ' personas', 'reservado',
       true, SUM(personas), SUM(bloques), SUM(bloques_completos), SUM(con_actividad),
       SUM(rutas_completas), SUM(en_riesgo), SUM(juegan), SUM(intentos),
       SUM(intentos_aprobados)
  FROM agg WHERE personas < fn_umbral_anonimato()
 HAVING SUM(personas) >= fn_umbral_anonimato();

-- -----------------------------------------------------------------------------
-- Aprendizaje: dónde se atora la institución, por dimensión.
-- -----------------------------------------------------------------------------
-- No lleva umbral porque no agrupa personas: agrupa contenido. Una dimensión no
-- identifica a nadie.
CREATE VIEW panel_por_dimension AS
SELECT
  d.codigo                                        AS dimension,
  d.nombre_oficial                                AS nombre,
  count(DISTINCT br.id)                           AS bloques,
  count(DISTINCT br.id) FILTER (WHERE br.estado = 'completo')  AS bloques_completos,
  count(DISTINCT br.id) FILTER (WHERE br.es_critica)           AS bloques_criticos,
  count(DISTINCT br.id) FILTER (WHERE br.estado = 'requiere_acompanamiento') AS en_riesgo,
  count(ie.id) FILTER (WHERE ie.estado = 'enviado')            AS intentos,
  count(ie.id) FILTER (WHERE ie.aprobado)                      AS intentos_aprobados,
  avg(ie.puntaje) FILTER (WHERE ie.estado = 'enviado')         AS puntaje_promedio
FROM dimension d
JOIN bloque_contenido bc ON bc.dimension_id = d.id
JOIN bloque_ruta br      ON br.bloque_contenido_id = bc.id
LEFT JOIN intento_evaluacion ie ON ie.bloque_ruta_id = br.id
GROUP BY d.codigo, d.nombre_oficial, d.orden
ORDER BY d.orden;
