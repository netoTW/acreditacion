-- =============================================================================
-- 006 — Tres roles, distribución de impacto y estructura escalonada
-- =============================================================================
--
-- AIEP reemplaza los 6 cargos por 3 roles y entrega, por rol, una DISTRIBUCIÓN %
-- sobre las 5 dimensiones. De ese % se derivan dos cosas —el nivel de exigencia
-- CNA y la criticidad— en vez de guardarse a mano, que es el mismo principio que
-- ya rige para el XP y el escalón: lo derivable no se edita.
--
-- Lo que NO cambia, y por eso esta migración es aditiva y no una reescritura:
--
--   · El contenido se sigue generando una vez por (dimensión, nivel) — ADR-003.
--   · La medalla sigue naciendo SOLO de una evaluación aprobada, verificado por
--     la base — ADR-005. El desafío aplicado NO otorga medalla ni XP acreditable;
--     usa origen_tipo 'juego', que el CHECK de 001 ya obliga a ser lúdico.
--   · Todos recorren las 5 dimensiones. La criticidad SUMA exigencia; nunca
--     vuelve opcional una dimensión.

-- -----------------------------------------------------------------------------
-- 1. LA MATRIZ gana el dato de AIEP
-- -----------------------------------------------------------------------------
-- La tabla ya tenía exactamente el grano que el modelo nuevo necesita: una fila
-- por (rol, dimensión). Solo le faltaban estas dos columnas.
ALTER TABLE exigencia_cargo_dimension
  ADD COLUMN distribucion_pct numeric(4,3) NOT NULL DEFAULT 0
    CHECK (distribucion_pct >= 0 AND distribucion_pct <= 1),
  ADD COLUMN es_critica       boolean      NOT NULL DEFAULT false;

COMMENT ON COLUMN exigencia_cargo_dimension.distribucion_pct IS
  'Peso de la dimensión para este rol, del Excel de AIEP. Suma 1 por rol.';
COMMENT ON COLUMN exigencia_cargo_dimension.es_critica IS
  'Derivado: las 2 dimensiones de mayor % del rol. Coincide con las marcas del Excel.';

-- La suma por rol tiene que dar 1 y las críticas tienen que ser exactamente 2.
-- Va como CONSTRAINT TRIGGER diferido porque la condición es sobre el conjunto de
-- filas de un rol, no sobre una fila: durante la carga la suma está incompleta y
-- solo tiene sentido evaluarla al cerrar la transacción.
CREATE FUNCTION fn_distribucion_coherente() RETURNS trigger AS $$
DECLARE
  v_cargo uuid := COALESCE(NEW.cargo_id, OLD.cargo_id);
  v_suma  numeric;
  v_crit  integer;
  v_filas integer;
BEGIN
  SELECT COALESCE(SUM(distribucion_pct), 0),
         COUNT(*) FILTER (WHERE es_critica),
         COUNT(*)
    INTO v_suma, v_crit, v_filas
    FROM exigencia_cargo_dimension WHERE cargo_id = v_cargo;

  IF v_filas = 0 THEN
    RETURN NULL;                       -- rol sin matriz: nada que verificar
  END IF;

  IF round(v_suma, 3) <> 1.000 THEN
    RAISE EXCEPTION
      'INTEGRIDAD: la distribución del rol suma %, y tiene que sumar 1', round(v_suma, 3)
      USING ERRCODE = 'check_violation';
  END IF;

  IF v_crit <> 2 THEN
    RAISE EXCEPTION
      'INTEGRIDAD: el rol tiene % dimensiones críticas y el modelo de AIEP define 2', v_crit
      USING ERRCODE = 'check_violation';
  END IF;

  -- "La acreditación es de todos": ninguna dimensión desaparece de ninguna ruta.
  IF v_filas <> (SELECT count(*) FROM dimension) THEN
    RAISE EXCEPTION
      'INTEGRIDAD: el rol cubre % dimensiones y tienen que ser las %',
      v_filas, (SELECT count(*) FROM dimension)
      USING ERRCODE = 'check_violation';
  END IF;

  RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE CONSTRAINT TRIGGER tg_distribucion_coherente
  AFTER INSERT OR UPDATE OR DELETE ON exigencia_cargo_dimension
  DEFERRABLE INITIALLY DEFERRED
  FOR EACH ROW EXECUTE FUNCTION fn_distribucion_coherente();

-- -----------------------------------------------------------------------------
-- 2. La ruta materializada lleva su exigencia encima
-- -----------------------------------------------------------------------------
-- La criticidad es del par (rol, dimensión), pero el bloque de contenido es
-- compartido entre roles: por eso el umbral reforzado y el peso NO pueden vivir
-- en `evaluacion`. Viven acá, en la ruta de cada persona.
ALTER TABLE bloque_ruta
  ADD COLUMN es_critica         boolean      NOT NULL DEFAULT false,
  ADD COLUMN peso_ranking       numeric(4,3) NOT NULL DEFAULT 0
    CHECK (peso_ranking >= 0 AND peso_ranking <= 1),
  ADD COLUMN umbral_aprobacion  numeric(3,2)
    CHECK (umbral_aprobacion IS NULL
           OR (umbral_aprobacion > 0 AND umbral_aprobacion <= 1));

COMMENT ON COLUMN bloque_ruta.umbral_aprobacion IS
  'Umbral reforzado de la dimensión crítica. NULL = usa el de evaluacion (80%).';
COMMENT ON COLUMN bloque_ruta.peso_ranking IS
  'El % del rol para esta dimensión. Listo en el dato; lo consume la pantalla de ranking.';

-- Una dimensión crítica no puede quedar con umbral estándar: sería una crítica de
-- nombre. Y una estándar no puede llevar umbral reforzado por descuido.
ALTER TABLE bloque_ruta
  ADD CONSTRAINT ck_critica_refuerza_umbral
    CHECK ((es_critica AND umbral_aprobacion IS NOT NULL)
           OR (NOT es_critica AND umbral_aprobacion IS NULL));

-- -----------------------------------------------------------------------------
-- 3. El candado del veredicto pasa a usar el umbral EFECTIVO
-- -----------------------------------------------------------------------------
-- Antes leía `evaluacion.umbral_aprobacion` y punto. Si se hubiera quedado así,
-- una crítica al 85% se habría aprobado con 80% sin que la base dijera nada: el
-- refuerzo habría sido decorativo. El umbral efectivo es el de la ruta si existe.
CREATE OR REPLACE FUNCTION fn_intento_coherente() RETURNS trigger AS $$
DECLARE
  v_umbral numeric(3,2);
BEGIN
  IF NEW.puntaje IS NULL OR NEW.aprobado IS NULL THEN
    RETURN NEW;
  END IF;

  SELECT COALESCE(br.umbral_aprobacion, e.umbral_aprobacion)
    INTO v_umbral
    FROM evaluacion e
    JOIN bloque_ruta br ON br.id = NEW.bloque_ruta_id
   WHERE e.id = NEW.evaluacion_id;

  IF v_umbral IS NULL THEN
    RAISE EXCEPTION 'INTEGRIDAD: el intento no tiene umbral que verificar'
      USING ERRCODE = 'check_violation';
  END IF;

  IF NEW.aprobado <> (NEW.puntaje >= v_umbral) THEN
    RAISE EXCEPTION
      'INTEGRIDAD: el veredicto no corresponde al puntaje (puntaje=%, umbral=%, aprobado=%)',
      NEW.puntaje, v_umbral, NEW.aprobado
      USING ERRCODE = 'check_violation';
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- -----------------------------------------------------------------------------
-- 4. Rangos de medalla: la gold se GANA, no se regala por el rol
-- -----------------------------------------------------------------------------
-- Cada bloque de contenido define ahora dos medallas —silver y gold— y cuál se
-- otorga depende de si la dimensión es crítica EN LA RUTA de esa persona.
ALTER TABLE definicion_medalla
  ADD CONSTRAINT uq_medalla_bloque_tipo UNIQUE (bloque_contenido_id, tipo);

CREATE OR REPLACE FUNCTION fn_insignia_respaldada() RETURNS trigger AS $$
DECLARE
  i RECORD;
  m RECORD;
BEGIN
  SELECT ie.aprobado, ie.estado, ie.colaborador_id,
         br.bloque_contenido_id, br.es_critica
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

  SELECT bloque_contenido_id, tipo INTO m
    FROM definicion_medalla WHERE id = NEW.definicion_medalla_id;

  IF m.bloque_contenido_id <> i.bloque_contenido_id THEN
    RAISE EXCEPTION
      'INTEGRIDAD: el intento respalda otro bloque de contenido que el de la medalla'
      USING ERRCODE = 'check_violation';
  END IF;

  -- La gold es la medalla de la mayor exigencia. Si la dimensión no es crítica en
  -- esta ruta, la persona no rindió al 85% ni pasó por el desafío: no hay gold.
  IF m.tipo = 'gold' AND i.es_critica IS NOT TRUE THEN
    RAISE EXCEPTION
      'INTEGRIDAD: no se otorga medalla gold sobre una dimensión que no es crítica en esta ruta'
      USING ERRCODE = 'check_violation';
  END IF;

  IF m.tipo <> 'gold' AND i.es_critica IS TRUE THEN
    RAISE EXCEPTION
      'INTEGRIDAD: una dimensión crítica otorga gold, no una medalla de rango %', m.tipo
      USING ERRCODE = 'check_violation';
  END IF;

  -- Con dos definiciones por bloque, hay que impedir que alguien acumule las dos
  -- por el mismo recorrido. Una persona, un bloque, una insignia.
  IF EXISTS (
    SELECT 1 FROM insignia ins
      JOIN definicion_medalla dm ON dm.id = ins.definicion_medalla_id
     WHERE ins.colaborador_id = NEW.colaborador_id
       AND dm.bloque_contenido_id = m.bloque_contenido_id
       AND ins.id <> NEW.id
  ) THEN
    RAISE EXCEPTION
      'INTEGRIDAD: ya existe una insignia de este colaborador para este bloque de contenido'
      USING ERRCODE = 'unique_violation';
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- -----------------------------------------------------------------------------
-- 5. Desafío aplicado — solo en dimensiones críticas
-- -----------------------------------------------------------------------------
-- Un caso realista: te pone en un rol, te da una situación con datos y te pide
-- DECIDIR entre opciones definidas. Lo corrige el servidor; el cliente nunca
-- recibe la respuesta correcta antes de resolver.
--
-- Su lugar en la mecánica: es REQUISITO para abrir la evaluación reforzada, no
-- una vía alternativa a ella. Da XP lúdico y nada más. La medalla sigue naciendo
-- únicamente del intento aprobado.
CREATE TABLE desafio_aplicado (
  id                   uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  bloque_contenido_id  uuid NOT NULL UNIQUE REFERENCES bloque_contenido(id) ON DELETE CASCADE,
  titulo               text NOT NULL,
  rol_ficticio         text NOT NULL,
  situacion            text NOT NULL,
  datos                jsonb NOT NULL DEFAULT '[]'::jsonb,
  es_contenido_prueba  boolean NOT NULL DEFAULT true
);

CREATE TABLE decision_desafio (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  desafio_id      uuid NOT NULL REFERENCES desafio_aplicado(id) ON DELETE CASCADE,
  orden           smallint NOT NULL,
  tipo            text NOT NULL
                    CHECK (tipo IN ('eleccion_unica','seleccion_multiple','clasificacion')),
  enunciado       text NOT NULL,
  -- [{clave, texto}]; en 'clasificacion' cada opción se ubica en un grupo.
  opciones        jsonb NOT NULL,
  grupos          jsonb NOT NULL DEFAULT '[]'::jsonb,
  -- Forma según tipo: "b" | ["a","c"] | {"e1":"g2", ...}. Nunca sale al cliente
  -- antes de que la decisión esté tomada.
  clave_correcta  jsonb NOT NULL,
  explicacion     text NOT NULL,
  UNIQUE (desafio_id, orden)
);

CREATE TABLE resolucion_desafio (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  colaborador_id  uuid NOT NULL REFERENCES colaborador(id),
  bloque_ruta_id  uuid NOT NULL REFERENCES bloque_ruta(id),
  desafio_id      uuid NOT NULL REFERENCES desafio_aplicado(id),
  respuestas      jsonb NOT NULL,
  aciertos        smallint NOT NULL CHECK (aciertos >= 0),
  total           smallint NOT NULL CHECK (total > 0),
  resuelto_en     timestamptz NOT NULL DEFAULT now(),
  UNIQUE (colaborador_id, bloque_ruta_id)
);

CREATE INDEX ix_decision_desafio ON decision_desafio (desafio_id, orden);
CREATE INDEX ix_resolucion_colab ON resolucion_desafio (colaborador_id);

-- El desafío se resuelve en la ruta propia. Un desafío resuelto contra el bloque
-- de otra persona no tendría sentido y abriría una vía para saltarse el requisito.
CREATE FUNCTION fn_resolucion_propia() RETURNS trigger AS $$
DECLARE
  v_ok boolean;
BEGIN
  SELECT r.colaborador_id = NEW.colaborador_id AND br.es_critica
    INTO v_ok
    FROM bloque_ruta br JOIN ruta r ON r.id = br.ruta_id
   WHERE br.id = NEW.bloque_ruta_id;

  IF v_ok IS NOT TRUE THEN
    RAISE EXCEPTION
      'INTEGRIDAD: el desafío solo se resuelve sobre un bloque crítico de la ruta propia'
      USING ERRCODE = 'check_violation';
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tg_resolucion_propia
  BEFORE INSERT OR UPDATE ON resolucion_desafio
  FOR EACH ROW EXECUTE FUNCTION fn_resolucion_propia();
