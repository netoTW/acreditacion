-- =============================================================================
-- 008 — D4 Vinculación con el Medio · «El mapa de contrapartes»
-- =============================================================================
--
-- Dos catálogos y un vínculo entre ellos. `accion_clave` NULL no es un dato que
-- falte: significa que ese actor **no es una contraparte de vinculación**, y es
-- la respuesta correcta para él. Por eso la columna admite nulos y la razón no.
--
-- El contenido es de prueba. En la fase de contenido real AIEP entrega sus
-- convenios y contrapartes efectivas (DUDAS.md).

CREATE TABLE accion_institucional (
  id                   uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  clave                text NOT NULL UNIQUE,
  nombre               text NOT NULL,
  descripcion          text NOT NULL,
  es_contenido_prueba  boolean NOT NULL DEFAULT true
);

CREATE TABLE actor_externo (
  id                   uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  codigo               text NOT NULL UNIQUE,
  nombre               text NOT NULL,
  tipo                 text NOT NULL,
  descripcion          text NOT NULL,
  -- NULL = no se sostiene como vinculación. Es una respuesta, no un vacío.
  accion_clave         text REFERENCES accion_institucional(clave),
  razon                text NOT NULL,
  es_contenido_prueba  boolean NOT NULL DEFAULT true
);

CREATE INDEX ix_actor_accion ON actor_externo (accion_clave);

COMMENT ON COLUMN actor_externo.accion_clave IS
  'La acción institucional que sostiene el vínculo. NULL significa que el actor NO '
  'es contraparte de vinculación —proveedor, servicio contratado, difusión—, que es '
  'la discriminación que el juego enseña.';
