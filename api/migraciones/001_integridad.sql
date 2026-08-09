-- =============================================================================
-- 001 — Núcleo de integridad de completitud
--
-- Realiza ADR-005: los invariantes de CLAUDE.md §4 se imponen en el ESQUEMA,
-- no en la capa de servicio. Una medalla sin respaldo no es un bug que haya que
-- cazar: es un INSERT que la base rechaza.
--
-- La cadena que hay que romper para falsificar una completitud es:
--   insignia -> intento_evaluacion -> bloque_ruta -> bloque_contenido
-- y cada eslabón tiene su candado. Ver el bloque de triggers al final.
-- =============================================================================

CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ----------------------------------------------------------------- catálogo
CREATE TABLE dimension (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  codigo          text NOT NULL UNIQUE
                    CHECK (codigo IN ('GESTION','DOCENCIA','CALIDAD','VCM','ICI')),
  nombre_oficial  text NOT NULL,
  obligatoria     boolean NOT NULL DEFAULT true,
  orden           smallint NOT NULL
);

CREATE TABLE cargo (
  id      uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  codigo  text NOT NULL UNIQUE,
  nombre  text NOT NULL
);

-- ----------------------------------------------------------------- contenido
-- Unidad de generación: el par (dimensión, nivel). Ver ADR-003.
CREATE TABLE bloque_contenido (
  id                   uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  dimension_id         uuid NOT NULL REFERENCES dimension(id),
  nivel_estandar       smallint NOT NULL CHECK (nivel_estandar BETWEEN 1 AND 3),
  titulo               text NOT NULL,
  es_contenido_prueba  boolean NOT NULL DEFAULT true,
  estado               text NOT NULL DEFAULT 'generado'
                         CHECK (estado IN ('generado','validado','rechazado')),
  UNIQUE (dimension_id, nivel_estandar)
);

CREATE TABLE evaluacion (
  id                   uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  bloque_contenido_id  uuid NOT NULL UNIQUE REFERENCES bloque_contenido(id),
  umbral_aprobacion    numeric(3,2) NOT NULL DEFAULT 0.80
                         CHECK (umbral_aprobacion > 0 AND umbral_aprobacion <= 1),
  n_items_por_intento  smallint NOT NULL DEFAULT 5,
  max_reintentos       smallint NOT NULL DEFAULT 3 CHECK (max_reintentos >= 1),
  minutos_expiracion   integer  NOT NULL DEFAULT 1440
);

CREATE TABLE item_evaluacion (
  id               uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  evaluacion_id    uuid NOT NULL REFERENCES evaluacion(id),
  enunciado        text NOT NULL,
  alternativas     jsonb NOT NULL,
  indice_correcta  smallint NOT NULL CHECK (indice_correcta BETWEEN 0 AND 3),
  explicaciones    jsonb NOT NULL,
  hash_enunciado   text NOT NULL,
  UNIQUE (evaluacion_id, hash_enunciado),           -- sin ítems duplicados en el banco
  CHECK (jsonb_array_length(alternativas) = 4),
  CHECK (jsonb_array_length(explicaciones) = 4)     -- una explicación por alternativa
);

CREATE TABLE definicion_medalla (
  id                   uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  bloque_contenido_id  uuid NOT NULL REFERENCES bloque_contenido(id),
  tipo                 text NOT NULL CHECK (tipo IN ('mini','silver','gold','master')),
  nombre               text NOT NULL,
  xp                   integer NOT NULL CHECK (xp >= 0)
);

-- ----------------------------------------------------------------- personas
-- OJO: sin columna xp. Sin columna nivel. Son DERIVADOS (ADR-005 §3).
CREATE TABLE colaborador (
  id         uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  email      text NOT NULL UNIQUE,
  nombre     text NOT NULL,
  cargo_id   uuid NOT NULL REFERENCES cargo(id),
  creado_en  timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE ruta (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  colaborador_id  uuid NOT NULL UNIQUE REFERENCES colaborador(id),
  cargo_id        uuid NOT NULL REFERENCES cargo(id),
  generada_en     timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE bloque_ruta (
  id                   uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  ruta_id              uuid NOT NULL REFERENCES ruta(id),
  bloque_contenido_id  uuid NOT NULL REFERENCES bloque_contenido(id),
  orden                smallint NOT NULL,
  estado               text NOT NULL DEFAULT 'bloqueado'
                         CHECK (estado IN ('bloqueado','disponible','en_curso',
                                           'completo','requiere_acompanamiento')),
  UNIQUE (ruta_id, orden),
  UNIQUE (ruta_id, bloque_contenido_id)
);

-- ----------------------------------------------------------------- la verdad
CREATE TABLE intento_evaluacion (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  colaborador_id  uuid NOT NULL REFERENCES colaborador(id),
  bloque_ruta_id  uuid NOT NULL REFERENCES bloque_ruta(id),
  evaluacion_id   uuid NOT NULL REFERENCES evaluacion(id),
  numero_intento  smallint NOT NULL CHECK (numero_intento >= 1),
  estado          text NOT NULL DEFAULT 'abierto'
                    CHECK (estado IN ('abierto','enviado','expirado')),
  items_servidos  jsonb NOT NULL DEFAULT '[]'::jsonb,
  iniciado_en     timestamptz NOT NULL DEFAULT now(),
  expira_en       timestamptz NOT NULL,
  enviado_en      timestamptz,
  puntaje         numeric(4,3) CHECK (puntaje >= 0 AND puntaje <= 1),
  aprobado        boolean,
  UNIQUE (bloque_ruta_id, numero_intento),
  -- Un intento cerrado tiene que tener puntaje y veredicto; uno abierto, ninguno.
  CHECK (
    (estado = 'abierto'  AND enviado_en IS NULL AND puntaje IS NULL AND aprobado IS NULL)
    OR
    (estado = 'enviado'  AND enviado_en IS NOT NULL AND puntaje IS NOT NULL AND aprobado IS NOT NULL)
    OR
    (estado = 'expirado' AND aprobado = false)
  )
);

CREATE TABLE respuesta_intento (
  intento_id      uuid NOT NULL REFERENCES intento_evaluacion(id),
  item_id         uuid NOT NULL REFERENCES item_evaluacion(id),
  indice_elegido  smallint NOT NULL CHECK (indice_elegido BETWEEN 0 AND 3),
  respondido_en   timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (intento_id, item_id)
);

-- Append-only. De acá se deriva TODO el estado de gamificación.
CREATE TABLE evento_gamificacion (
  id                   uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  colaborador_id       uuid NOT NULL REFERENCES colaborador(id),
  tipo                 text NOT NULL,
  origen_tipo          text NOT NULL
                         CHECK (origen_tipo IN ('modulo','evaluacion','medalla','juego')),
  origen_id            uuid NOT NULL,
  xp                   integer NOT NULL CHECK (xp >= 0),          -- §4.2: nunca negativo
  clase_xp             text NOT NULL CHECK (clase_xp IN ('acreditable','ludico')),
  clave_idempotencia   text NOT NULL UNIQUE,                      -- S-13: doble envío
  ocurrido_en          timestamptz NOT NULL DEFAULT now(),
  -- S-04: un juego JAMÁS puede producir XP acreditable. Si pudiera, alguien llegaría
  -- a Maestro de Acreditación jugando trivia sin aprobar nada.
  CHECK (NOT (clase_xp = 'acreditable' AND origen_tipo = 'juego'))
);

CREATE TABLE insignia (
  id                     uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  colaborador_id         uuid NOT NULL REFERENCES colaborador(id),
  definicion_medalla_id  uuid NOT NULL REFERENCES definicion_medalla(id),
  -- EL INVARIANTE MÁXIMO, en una línea: sin intento que la respalde, no hay medalla.
  intento_evaluacion_id  uuid NOT NULL REFERENCES intento_evaluacion(id),
  otorgada_en            timestamptz NOT NULL DEFAULT now(),
  open_badge_assertion_id text,
  UNIQUE (colaborador_id, definicion_medalla_id)    -- no se otorga dos veces
);

CREATE INDEX ix_evento_colaborador ON evento_gamificacion (colaborador_id, ocurrido_en);
CREATE INDEX ix_evento_clase       ON evento_gamificacion (clase_xp, ocurrido_en);
CREATE INDEX ix_intento_colab      ON intento_evaluacion (colaborador_id, estado);
CREATE INDEX ix_bloque_ruta_estado ON bloque_ruta (ruta_id, estado);

-- =============================================================================
-- CANDADOS
-- =============================================================================

-- 1. Un intento no puede declararse aprobado si el puntaje no llega al umbral.
--    Sin esto, falsificar la medalla es tan fácil como marcar aprobado=true.
CREATE FUNCTION fn_intento_coherente() RETURNS trigger AS $$
DECLARE
  v_umbral numeric(3,2);
BEGIN
  IF NEW.puntaje IS NULL OR NEW.aprobado IS NULL THEN
    RETURN NEW;
  END IF;

  SELECT umbral_aprobacion INTO v_umbral FROM evaluacion WHERE id = NEW.evaluacion_id;

  IF NEW.aprobado <> (NEW.puntaje >= v_umbral) THEN
    RAISE EXCEPTION
      'INTEGRIDAD: el veredicto no corresponde al puntaje (puntaje=%, umbral=%, aprobado=%)',
      NEW.puntaje, v_umbral, NEW.aprobado
      USING ERRCODE = 'check_violation';
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tg_intento_coherente
  BEFORE INSERT OR UPDATE ON intento_evaluacion
  FOR EACH ROW EXECUTE FUNCTION fn_intento_coherente();

-- 2. Toda insignia tiene que estar respaldada de verdad. No basta con que exista
--    un intento: tiene que ser aprobado, de la MISMA persona, y del MISMO bloque
--    de contenido que define la medalla.
CREATE FUNCTION fn_insignia_respaldada() RETURNS trigger AS $$
DECLARE
  i RECORD;
  v_bloque_medalla uuid;
BEGIN
  SELECT ie.aprobado, ie.estado, ie.colaborador_id, br.bloque_contenido_id
    INTO i
    FROM intento_evaluacion ie
    JOIN bloque_ruta br ON br.id = ie.bloque_ruta_id
   WHERE ie.id = NEW.intento_evaluacion_id;

  IF NOT FOUND THEN
    RAISE EXCEPTION 'INTEGRIDAD: la insignia apunta a un intento inexistente'
      USING ERRCODE = 'foreign_key_violation';
  END IF;

  IF i.aprobado IS NOT TRUE THEN
    RAISE EXCEPTION 'INTEGRIDAD: no se otorga insignia sobre un intento no aprobado'
      USING ERRCODE = 'check_violation';
  END IF;

  IF i.estado <> 'enviado' THEN
    RAISE EXCEPTION 'INTEGRIDAD: el intento que respalda la insignia no está cerrado (estado=%)', i.estado
      USING ERRCODE = 'check_violation';
  END IF;

  IF i.colaborador_id <> NEW.colaborador_id THEN
    RAISE EXCEPTION 'INTEGRIDAD: el intento que respalda la insignia es de otro colaborador'
      USING ERRCODE = 'check_violation';
  END IF;

  SELECT bloque_contenido_id INTO v_bloque_medalla
    FROM definicion_medalla WHERE id = NEW.definicion_medalla_id;

  IF v_bloque_medalla <> i.bloque_contenido_id THEN
    RAISE EXCEPTION
      'INTEGRIDAD: el intento respalda otro bloque de contenido que el de la medalla'
      USING ERRCODE = 'check_violation';
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tg_insignia_respaldada
  BEFORE INSERT OR UPDATE ON insignia
  FOR EACH ROW EXECUTE FUNCTION fn_insignia_respaldada();

-- 3. evento_gamificacion es append-only. Corregir es emitir un evento
--    compensatorio, nunca reescribir la historia.
CREATE FUNCTION fn_solo_append() RETURNS trigger AS $$
BEGIN
  RAISE EXCEPTION 'INTEGRIDAD: % sobre % está prohibido; la tabla es append-only',
    TG_OP, TG_TABLE_NAME
    USING ERRCODE = 'insufficient_privilege';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tg_evento_append_only
  BEFORE UPDATE OR DELETE ON evento_gamificacion
  FOR EACH ROW EXECUTE FUNCTION fn_solo_append();

-- Una insignia otorgada tampoco se borra ni se reescribe: es evidencia.
CREATE TRIGGER tg_insignia_append_only
  BEFORE DELETE ON insignia
  FOR EACH ROW EXECUTE FUNCTION fn_solo_append();

-- =============================================================================
-- DERIVADOS — el nivel no se guarda, se calcula
-- =============================================================================

-- Escalera de S-10. Se nombra el escalón: "nivel" ya significa nivel_estandar
-- en el dominio CNA, así que la escalera no se numera (glosario).
CREATE FUNCTION fn_escalon(p_xp bigint) RETURNS text AS $$
  SELECT CASE
    WHEN p_xp >= 10000 THEN 'Maestro de Acreditación'
    WHEN p_xp >=  7000 THEN 'Líder de Calidad'
    WHEN p_xp >=  4500 THEN 'Embajador'
    WHEN p_xp >=  2500 THEN 'Facilitador'
    WHEN p_xp >=  1000 THEN 'Colaborador'
    ELSE                    'Explorador'
  END;
$$ LANGUAGE sql IMMUTABLE;

-- La ÚNICA fuente de XP y escalón.
--   escalón y completitud  <- xp_acreditable
--   ranking                <- xp_total
CREATE VIEW estado_colaborador AS
SELECT
  c.id AS colaborador_id,
  c.nombre,
  COALESCE(SUM(e.xp) FILTER (WHERE e.clase_xp = 'acreditable'), 0)::bigint AS xp_acreditable,
  COALESCE(SUM(e.xp), 0)::bigint                                           AS xp_total,
  fn_escalon(COALESCE(SUM(e.xp) FILTER (WHERE e.clase_xp = 'acreditable'), 0)::bigint) AS escalon,
  (SELECT count(*) FROM insignia i WHERE i.colaborador_id = c.id)          AS insignias
FROM colaborador c
LEFT JOIN evento_gamificacion e ON e.colaborador_id = c.id
GROUP BY c.id, c.nombre;
